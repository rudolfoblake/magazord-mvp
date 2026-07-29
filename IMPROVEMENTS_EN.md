# Improvement and Architecture Evolution Roadmap

## Overview

The current project satisfies the intended MVP scope: a polyglot MCP architecture that answers e-commerce business questions through controlled analytical tools.

The items below describe how the platform could evolve for larger datasets, more users, stricter security requirements, and production operations.

## Short-Term Priorities

### 1. Expand automated test coverage

Add focused tests for:

- SQLAlchemy repositories;
- cache behavior and invalidation;
- MCP tool contracts;
- unsupported period inputs;
- empty datasets;
- zero-value comparison periods;
- database and Redis failures;
- circuit-breaker transitions;
- Gemini retry and malformed tool-call scenarios.

### 2. Strengthen observability

Add:

- metrics per MCP tool;
- latency percentiles;
- cache-hit ratio;
- database-query duration;
- model-call duration and token usage;
- error-rate dashboards;
- request, session, and correlation identifiers.

### 3. Use data-aware cache policies

Apply different expiration rules according to volatility:

- current-day metrics: short TTL;
- current-month metrics: medium TTL;
- closed historical periods: long TTL;
- explicit invalidation after controlled data refreshes.

### 4. Improve multilingual behavior

Create tested prompt and response policies for English, Portuguese, and Spanish while keeping tool names and structured contracts language-neutral.

### 5. Add report export tools

Expose controlled MCP tools for generating:

- CSV extracts;
- XLSX executive reports;
- PDF summaries;
- scheduled report snapshots.

Exports should use the same server-side business rules as interactive answers.

## Security and Multi-User Access

### Authentication and authorization

Add OAuth2 or OIDC authentication and role-based access control.

Suggested roles:

- **Executive** — global strategic indicators;
- **Manager** — category or department scope;
- **Analyst** — detailed operational access.

### Tenant and data isolation

Introduce tenant identifiers across tool execution, cache keys, database access, and logs. Authorization must be enforced on the server rather than inferred by the language model.

### Tool-level permissions

Restrict sensitive operations and detailed datasets by tool, role, and business scope.

### Secret management

Move API keys and database credentials from local environment files to a managed secret store in production.

## Data Volume and Performance

### Purpose-built indexes

Review query plans and add indexes for frequently filtered fields such as:

- order creation date;
- order status;
- product and category identifiers;
- cancellation dimensions;
- customer identifiers when customer analytics are introduced.

### Materialized views

Pre-aggregate expensive historical metrics such as monthly GMV, cancellation rates, category performance, and Year-over-Year comparisons.

### Read replicas

Route analytical reads to replicas so BI workloads do not compete with transactional operations.

### Multi-layer cache

Combine:

- short-lived in-process caching;
- Redis distributed caching;
- precomputed analytical views.

Cache keys should include tenant, tool, normalized arguments, business-rule version, and dataset version.

## Observability Level 2

### Distributed tracing

Instrument the complete path:

```text
CLI -> Gemini -> MCP Client -> MCP Server -> Tool -> Service -> Repository -> PostgreSQL/Redis
```

Use OpenTelemetry and export traces to a platform such as Datadog, Grafana Tempo, or New Relic.

### Data-quality signals

Track:

- missing or invalid statuses;
- unexpected negative values;
- delayed data ingestion;
- discrepancies between aggregates;
- tools returning empty datasets;
- unusually large metric changes.

### Redaction policy

Define which arguments, errors, query details, and model outputs may be logged. Sensitive business and user data should be removed before telemetry export.

## AI Layer Evolution

### Provider-independent orchestration

Create an abstraction for multiple model providers with:

- ordered fallbacks;
- timeout and retry policies;
- cost controls;
- model capability checks;
- provider health metrics;
- response-quality evaluation.

### Evaluation suite

Build a repeatable set of business questions with expected tool calls and numeric results. Run it before merge to detect:

- incorrect tool selection;
- unsupported arguments;
- invented metrics;
- inconsistent explanations;
- regressions in financial calculations.

### Specialized agents

For more complex workflows, split responsibilities between agents such as:

- planner;
- business analyst;
- data-quality reviewer;
- report writer.

Agents should still use the same controlled MCP tools and must not receive unrestricted database access.

### Predictive analytics

Add forecasting services for:

- revenue;
- order volume;
- demand by category;
- cancellation risk;
- inventory depletion.

Predictions must be clearly separated from observed facts and include confidence intervals and model-version metadata.

## Product Evolution

### Web interface and dashboards

Add a browser-based interface with:

- interactive charts;
- dynamic filters;
- saved questions;
- role-specific dashboards;
- conversation history;
- export actions;
- links from generated explanations to source metrics.

### Scheduled insights

Allow users to subscribe to controlled reports and anomaly notifications, such as a sudden cancellation-rate increase or an unexpected GMV decline.

## Recommended Delivery Order

1. Test expansion and evaluation dataset.
2. Authentication, authorization, and tenant isolation.
3. Correlation IDs, metrics, and redaction.
4. Query-plan review and targeted indexes.
5. Dynamic cache strategy.
6. Provider-independent model orchestration.
7. Web dashboard and report exports.
8. Materialized views and read replicas.
9. Specialized agents and forecasting.

## Conclusion

The MVP already demonstrates the key architectural idea: language models should access business data through explicit, validated, and auditable tools. Scaling the system should strengthen that boundary rather than replace it with unrestricted model access.
