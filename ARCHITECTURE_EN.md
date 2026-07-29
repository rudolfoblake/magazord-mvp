# Architecture and Technical Decisions

## 1. Context

The system provides natural-language access to e-commerce business indicators through the Model Context Protocol (MCP). Its primary constraint is correctness: the language model must not calculate financial metrics from raw records or execute arbitrary SQL.

The architecture therefore treats the LLM as an orchestrator and explanation layer, not as the source of truth for business calculations.

## 2. System Boundaries

```text
Interactive user
  -> TypeScript CLI
  -> Gemini
  -> MCP Client
  -> Streamable HTTP
  -> Python MCP Server
  -> Tool layer
  -> Service layer
  -> Repository layer
  -> PostgreSQL

Tool result cache
  -> Redis

Tool execution events
  -> Structured stdout logs
```

### Client boundary

The client is responsible for:

- accepting natural-language questions;
- presenting available tools to the model;
- executing the selected MCP tool;
- passing validated tool output back to the model;
- retrying transient model failures;
- preventing repeated MCP calls through a circuit breaker;
- formatting the final response for the terminal.

The client does not own metric definitions or database rules.

### Server boundary

The server is responsible for:

- exposing a small set of explicit MCP tools;
- validating tool arguments;
- resolving relative and explicit periods;
- applying revenue and cancellation rules;
- executing parameterized data-access operations;
- aggregating results;
- validating response contracts;
- caching repeatable analytical results;
- emitting execution telemetry.

The server does not allow the model to submit arbitrary SQL.

## 3. Layered Backend Design

### Tool layer

The tool layer defines the public MCP contract. Functions are intentionally small and business-oriented, such as `get_gmv_comparison` and `get_cancellation_analysis`.

Responsibilities:

- argument validation;
- MCP registration;
- cache and telemetry decorators;
- database-session lifecycle;
- delegation to services.

### Service layer

The service layer combines business rules and repository results into validated response objects.

Responsibilities:

- period coordination;
- metric composition;
- percentage variation;
- cancellation-rate calculation;
- data normalization;
- Pydantic response construction.

### Repository layer

The repository layer isolates SQLAlchemy queries from orchestration and presentation.

Responsibilities:

- filtered database reads;
- financial aggregation;
- product rankings;
- cancellation groupings;
- inventory-column detection;
- conversion of database rows into application structures.

### Business-rule layer

Revenue-valid and excluded order statuses are centralized instead of duplicated across tools. This prevents different metrics from applying incompatible definitions of revenue.

## 4. Tool Design Decision

### Decision

Expose specialized analytical tools instead of one generic SQL execution tool.

### Reasons

1. **Deterministic calculations** — financial metrics are computed by reviewed server code.
2. **Reduced hallucination risk** — the model explains results instead of recreating calculations.
3. **Smaller prompts** — aggregated responses are much smaller than transactional rows.
4. **Clear authorization path** — future permissions can be applied per tool and domain.
5. **Testability** — each business operation has a stable input and output contract.
6. **Auditability** — tool calls can be logged by name and arguments.

### Trade-off

Adding a new analytical capability requires implementing or extending a server tool. This is deliberate: business metrics should evolve through reviewed code, not through unconstrained model-generated SQL.

## 5. Transport Decision

The client communicates with the MCP server through Streamable HTTP.

Benefits:

- language-independent process separation;
- compatibility with containerized execution;
- simpler deployment than tightly coupling Python and Node.js processes;
- explicit connection lifecycle;
- clear place for resilience controls.

## 6. Cache Decision

Redis caches deterministic analytical tool results for five minutes.

The cache is placed around tools because tool inputs represent stable business requests. Repeated questions therefore avoid unnecessary database aggregation while preserving the same validated response contract.

Future improvements should assign different TTLs by data volatility. Historical periods can tolerate longer caching than current-day operational metrics.

## 7. Resilience Decision

The client implements a three-state circuit breaker:

- `CLOSED`: requests flow normally;
- `OPEN`: calls are blocked after three consecutive failures;
- `HALF_OPEN`: one recovery attempt is allowed after 30 seconds.

This protects the interactive client from repeatedly calling an unhealthy MCP service and gives the dependency time to recover.

## 8. Observability Decision

A telemetry decorator wraps tool execution and emits structured JSON to stdout.

Recorded fields include:

- timestamp;
- tool name;
- provided arguments;
- execution time;
- success state;
- error information;
- cache-hit state when propagated by the cache layer.

This keeps infrastructure concerns outside business methods and makes logs compatible with Docker log collection.

The current implementation is intentionally lightweight. A production evolution should add correlation IDs, metrics, traces, redaction policies, and centralized log ingestion.

## 9. Data and Financial Correctness

Revenue metrics include orders in the following states:

- `processing`
- `shipped`
- `delivered`

They exclude:

- `cancelled`
- `pending`

The server returns both the metric and relevant context, such as analyzed periods and included or excluded statuses. This makes responses easier to verify and explain.

Year-over-Year average-ticket comparison uses equivalent Year-to-Date ranges rather than comparing a partial current year with a complete previous year.

## 10. Security Model

Current safeguards:

- no arbitrary SQL tool;
- database logic remains on the server;
- compact tool outputs instead of raw tables;
- explicit tool arguments;
- container-network separation;
- environment-based configuration.

Current limitations:

- no end-user authentication;
- no RBAC;
- no tenant isolation;
- no per-tool authorization;
- no managed secret store;
- tool arguments may appear in telemetry and require a formal redaction policy before handling sensitive inputs.

## 11. AI Development Workflow

AI agents assisted with research, initial implementations, SQL drafts, documentation, and technical review.

The accepted workflow was:

1. define the requirement and architectural boundary;
2. provide the agent with explicit constraints;
3. generate or refine an implementation;
4. inspect the diff and integration impact;
5. verify business rules and SQL behavior;
6. execute local tests and representative questions;
7. correct failures and edge cases;
8. approve the final result manually.

The human engineer retained ownership of architecture, security constraints, metric definitions, validation, and release decisions.

## 12. Known Evolution Path

The current architecture can evolve without changing its core principle. Likely next steps include:

- stronger automated testing;
- RBAC and multi-tenant boundaries;
- dynamic cache policies;
- OpenTelemetry tracing;
- provider-independent LLM orchestration;
- web dashboards;
- materialized views and read replicas;
- forecasting and specialized analytical agents.
