# BI Copilot: Business Intelligence through Model Context Protocol (MCP)

Developed by **Rudolfo Blake**

> Portuguese documentation: [README.md](README.md)

## Overview

This project is a production-oriented MVP of a Business Intelligence copilot for e-commerce. It uses the Model Context Protocol (MCP) to let a large language model answer business questions through controlled, auditable tools instead of giving the model direct database access.

The application combines:

- a Python MCP server responsible for business rules, SQL execution, validation, caching, and telemetry;
- a Node.js and TypeScript MCP client responsible for the interactive CLI, LLM orchestration, tool selection, retry behavior, and circuit breaking;
- PostgreSQL as the transactional data source;
- Redis for caching repeated analytical queries;
- Google Gemini for natural-language interpretation and response generation;
- Docker Compose for a reproducible local environment.

The system was originally created for an engineering challenge that required a polyglot MCP architecture and accurate answers to executive e-commerce questions such as GMV comparison, cancellation analysis, Year-over-Year average ticket, top products, business overview, and inventory health.

## Core Design Principle

The model never receives unrestricted SQL access.

All calculations are performed by specialized server-side tools. The LLM receives compact, validated business results and is responsible only for deciding which tool to call and explaining the returned facts.

This design reduces:

- hallucinated calculations;
- token usage;
- accidental exposure of raw transactional data;
- inconsistent business rules;
- duplicated analytical logic across clients.

## Architecture

```text
User
  -> Interactive CLI
  -> Gemini
  -> MCP Client (Node.js + TypeScript)
  -> Streamable HTTP transport
  -> MCP Server (Python + FastMCP)
  -> Specialized business tools
  -> Service layer
  -> SQLAlchemy repositories
  -> PostgreSQL

Repeated analytical calls
  -> Redis cache

Every tool execution
  -> Structured telemetry on stdout
```

### MCP Server

The Python server owns the authoritative analytical behavior:

- database access through SQLAlchemy;
- period resolution;
- revenue and cancellation rules;
- financial aggregation;
- response validation through Pydantic;
- Redis caching;
- structured tool telemetry;
- MCP tool registration.

### MCP Client

The TypeScript client owns interaction and orchestration:

- interactive command-line experience;
- connection to the MCP server through Streamable HTTP;
- discovery and execution of MCP tools;
- Gemini integration;
- retry behavior for model calls;
- a circuit breaker for repeated MCP failures;
- graceful transport shutdown.

## Available MCP Tools

### Sales tools

| Tool | Purpose |
|---|---|
| `get_gmv` | Returns GMV for a supported period. |
| `get_gmv_comparison` | Compares one period with another or with the previous equivalent period. |
| `get_average_ticket` | Returns the average ticket for a period. |
| `get_average_ticket_yoy` | Compares current Year-to-Date average ticket with the equivalent previous-year period. |

### Analytics tools

| Tool | Purpose |
|---|---|
| `get_top_products` | Returns the highest-selling products for a period. |
| `get_cancellation_analysis` | Returns cancellation totals, category rates, affected products, and cancelled revenue. |
| `get_business_overview` | Returns an executive summary with GMV, average ticket, valid orders, cancellations, and category signals. |
| `get_stock_health` | Returns stock indicators when a compatible inventory column exists. |

## Supported Periods

The service supports relative periods such as:

- `today`
- `yesterday`
- `current_month`
- `last_month`
- `current_quarter`
- `last_quarter`
- `current_year`
- `last_year`
- `last_12_months`

It also supports explicit dates and historical periods, including formats such as:

- `2025-01`
- `2025-06-02`
- `2025-Q1`

## Business Rules

Financial metrics are calculated on the server using centralized status rules.

Revenue-valid statuses:

- `processing`
- `shipped`
- `delivered`

Excluded from revenue:

- `cancelled`
- `pending`

The LLM does not infer these rules. It receives values that have already been filtered and calculated consistently by the backend.

## Reliability and Operational Controls

### Redis cache

Analytical tools use a five-minute cache by default. This reduces repeated database work and avoids paying the model and database cost again for identical questions.

### Circuit breaker

The MCP client tracks consecutive failures. After three failures, the circuit opens and temporarily blocks additional calls. After 30 seconds, it transitions to a half-open state and allows a recovery attempt.

### Structured telemetry

Each MCP tool execution records structured information such as:

- timestamp;
- tool name;
- arguments;
- execution time;
- success or failure;
- error message;
- cache-hit information when available.

Logs are written to stdout and can be consumed by Docker or an external observability platform.

## Repository Structure

```text
magazord-mvp/
├── database/                  # Database migrations and SQL scripts
├── init/                      # PostgreSQL initialization and restore scripts
├── mcp-client/                # Node.js + TypeScript MCP client
│   ├── src/                   # CLI, Gemini integration, MCP transport and resilience
│   └── Dockerfile
├── mcp-server/                # Python FastMCP server
│   ├── src/
│   │   ├── business_rules/    # Revenue and order-status rules
│   │   ├── database/          # SQLAlchemy connection configuration
│   │   ├── models/            # Validated response schemas
│   │   ├── repositories/      # Data-access layer
│   │   ├── services/          # Periods, analytics, caching and business processing
│   │   └── tools/             # MCP tool definitions
│   ├── tests/                 # Unit and integration tests
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
├── README.md                  # Portuguese documentation
├── README_EN.md               # English documentation
├── ARCHITECTURE_EN.md         # Architecture and decision record
└── IMPROVEMENTS_EN.md         # Evolution roadmap
```

## Running Locally

### Requirements

- Docker
- Docker Compose
- a Google Gemini API key

### 1. Create the environment file

```bash
cp .env.example .env
```

Configure at least:

- `GEMINI_API_KEY`
- `TZ`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `DATABASE_URL`
- `REDIS_URL`
- `MCP_SERVER_URL`

### 2. Start the infrastructure and MCP server

```bash
docker compose up --build -d
```

The initial database restore may take several minutes. The PostgreSQL health check waits for both database readiness and the restore-completion marker.

### 3. Start the interactive client

```bash
docker compose --profile client run --rm mcp-client
```

### 4. Run the server test suite

```bash
docker compose exec mcp-server pytest
```

## Engineering Decisions

### Why Python for the server?

Python provides a mature ecosystem for data access, analytics, validation, and MCP development. FastMCP, SQLAlchemy, and Pydantic make it practical to express business rules clearly while keeping data access and tool contracts separated.

### Why TypeScript for the client?

TypeScript provides a strong fit for an interactive CLI and the JavaScript MCP and Gemini SDKs. It also makes transport lifecycle, tool invocation, and resilience behavior explicit and type-safe.

### Why specialized tools instead of a generic SQL tool?

A generic SQL tool would move business correctness and security responsibilities into the model. Specialized tools keep metrics deterministic, limit returned data, and make every available operation reviewable and testable.

### Why return aggregates instead of raw rows?

Executive questions usually require validated metrics, comparisons, and rankings. Returning aggregates minimizes context size and prevents the model from performing fragile financial calculations over large raw datasets.

## AI-Assisted Development

AI tools were used as engineering accelerators during research, prototyping, SQL drafting, MCP tool implementation, documentation, and technical review.

The project followed a Human-in-the-Loop workflow. The human responsibilities included:

- defining the architecture;
- designing the MCP tool boundaries;
- reviewing and correcting generated code;
- validating SQL queries and financial rules;
- debugging integration problems;
- running local tests;
- checking returned metrics;
- approving the final implementation.

AI-generated output was never treated as automatically correct or merged without review.

## Current Scope and Limitations

This repository is an MVP and intentionally does not yet include:

- authentication and role-based access control;
- tenant isolation;
- a browser-based dashboard;
- distributed tracing;
- provider-agnostic LLM orchestration;
- forecasting models;
- production secrets management;
- materialized analytical views;
- read replicas;
- horizontally scalable workers.

The architecture separates these concerns well enough for incremental evolution without replacing the MCP tool model.

## Additional Documentation

- [Architecture and decisions](ARCHITECTURE_EN.md)
- [Improvement roadmap](IMPROVEMENTS_EN.md)
- [Original challenge specification in Portuguese](instrucoes_desafio.md)
- [Original improvement report in Portuguese](relatorio_de_melhorias.md)

## License and Usage

This repository is provided as a technical portfolio and educational project. Review the repository licensing terms before reusing it in commercial environments.
