---
name: common-observability
description: Logging patterns for this Python/LangGraph/Streamlit project. Use when configuring structured logging, adding log statements to LangGraph nodes, debugging pipeline execution, or reviewing what should and should not be logged.
---

# Observability Skill

Structured logging patterns for biorce-mini: a Streamlit + LangGraph + Python app.

## When to Use

- Adding logging to a new LangGraph node
- Configuring log format or log level
- Reviewing log output for structured context
- Deciding what to log (and what NOT to log)
- Debugging pipeline execution issues

## Logging Setup

Use Python's standard `logging` module. Configure once at the entry point.

```python
# streamlit_app.py or at module top level
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
```

Each module gets its own logger:

```python
import logging
logger = logging.getLogger(__name__)
```

## Structured Log Key Contract

All log keys use **snake_case** (Python convention). Be consistent — the same
operation should always log the same keys.

### Mandatory Keys per Node

| Key | Type | Example |
|-----|------|---------|
| `node` | string | `"retrieve"`, `"research"`, `"write"`, `"review"` |
| `condition` | string | The input condition being processed |
| `iteration` | int | Loop iteration number |

### Contextual Keys

| Key | When | Example |
|-----|------|---------|
| `chunks_count` | After retrieval | Number of chunks returned |
| `duration_ms` | Long-running operations | Elapsed milliseconds |
| `has_unsupported` | After review node | Boolean from reviewer |
| `error` | On exception | Exception type (not full trace in logs) |

## Logging in LangGraph Nodes

```python
import logging
logger = logging.getLogger(__name__)

def retrieve(state: GraphState) -> dict:
    logger.info("node=retrieve condition=%s", state.condition)
    chunks = rag.retrieve(state.condition, state.intervention)
    logger.info("node=retrieve chunks_count=%d", len(chunks))
    return {"chunks": chunks}

def review(state: GraphState) -> dict:
    logger.info("node=review iteration=%d", state.iteration)
    result = llm.review(state.draft, state.chunks)
    logger.info("node=review has_unsupported=%s", result.get("has_unsupported"))
    return {"review": result}
```

## Log Level Guidance

| Level | When |
|-------|------|
| `DEBUG` | Internal state useful only during local dev (chunk contents, full prompts) |
| `INFO` | Normal pipeline milestones: node start/end, retrieval count, routing decisions |
| `WARNING` | Recoverable issues: empty retrieval, loop limit reached, fallback triggered |
| `ERROR` | Failed operations that need attention, with exception type |

## What NOT to Log

- Full LLM prompts (may contain PII from documents)
- Full LLM responses (unbounded size, potential PII)
- Raw document content from Chroma
- The Gemini API key — even partially
- Full stack traces at `INFO` level — use `logger.exception()` only in `except` blocks

```python
# GOOD
logger.error("LLM call failed node=research error=%s", type(e).__name__)

# BAD — leaks full prompt + response in logs
logger.error("LLM call failed prompt=%s response=%s", prompt, response)
```

## Debugging Pipeline Execution

The Streamlit UI already displays execution traces visually. For deeper debugging:

```python
# Temporarily enable DEBUG to see node transitions
logging.getLogger("src.graph").setLevel(logging.DEBUG)
```

Never commit `DEBUG` level as the default — it generates too much noise in normal runs.


## Structured Log Key Contract

Loggly is **case-sensitive**. All log keys across .NET and Python **must** use PascalCase to ensure consistent
querying, filtering, and dashboards.

### Mandatory Base Keys

Every log entry must include these keys:

| Key | Type | Source (.NET) | Source (Python) |
| --- | --- | --- | --- |
| `Timestamp` | ISO 8601 datetime | Serilog `@t` (override to PascalCase) | `asctime` formatted |
| `Level` | string | Serilog level | Python log level |
| `Message` | string | Serilog message template | Log message |
| `Application` | string | `Serilog.Properties.Application` | `extra={"Application": ...}` |
| `Environment` | string | `Serilog.Properties.Environment` | `extra={"Environment": ...}` |
| `SourceContext` | string | Serilog enricher (auto) | `logging.getLogger(__name__)` |

### Contextual Keys

Include these when the context applies:

| Key | When | Example |
| --- | --- | --- |
| `RequestId` | HTTP requests (API) | W3C trace ID from middleware |
| `RequestPath` | HTTP requests (API) | `/dashboard/agreements` |
| `ClaimId` | Domain operations on claims | `Guid` from command/query |
| `ProcessId` | Domain operations on processes | `Guid` from command/query |
| `Duration` | Long-running operations | Elapsed milliseconds |
| `MachineName` | Container identification | Serilog `WithMachineName()` |
| `ThreadId` | Concurrency debugging | Serilog `WithThreadId()` |
| `ExceptionDetail` | Error logs | Serilog `WithExceptionDetails()` |

### Key Naming Rules

- **ALL custom log keys MUST be PascalCase** — no exceptions
- Domain identifiers (`ClaimId`, `ProcessId`) must match entity property names exactly
- Never use `snake_case` or `camelCase` for log keys — Loggly queries will break
- Python `extra={}` keys must also be PascalCase: `extra={"ClaimId": claim_id}`
- Serilog structured parameters use PascalCase: `{ClaimId}` not `{claimId}`

### Sensitive Data — Never Log

- Passwords, tokens, API keys, secrets
- Connection strings, JWT payloads
- PII: email, phone, national ID numbers
- Full credit card or bank account numbers

See `common-security` skill (OWASP #9 — Security Logging Failures) for the full list.

## Logging

### .NET — Serilog

**Configuration** (via `appsettings.{Environment}.json`):

```json
{
    "Serilog": {
        "MinimumLevel": {
            "Default": "Information",
            "Override": {
                "System.Net.Http.HttpClient": "Warning",
                "Microsoft.EntityFrameworkCore": "Warning"
            }
        },
        "WriteTo": [
            { "Name": "Console" }
        ]
    }
}
```

**Enrichers** (configured in `ConfigureLoggerOptions.cs`):

- `FromLogContext()` — scoped context properties
- `WithExceptionDetails()` — structured exception info
- `WithMachineName()` — container/host identification
- `WithThreadId()` — concurrency debugging

**Sinks**:

| Environment | Sinks |
| --- | --- |
| Development | Console only |
| Production | Console + Loggly |

### Structured Logging Rules

```csharp
// GOOD — structured parameters with semantic names
_logger.LogInformation("Processing claim {ClaimId} for process {ProcessId}",
    command.ClaimId, process.Id);

// BAD — string interpolation (loses structured context)
_logger.LogInformation($"Processing claim {command.ClaimId}");
```

**Always include:**

- `ClaimId`, `ProcessId`, or relevant domain identifiers
- Operation name via `nameof()` at entry points
- Duration for long operations

**Log level guidance:**

| Level | When |
| --- | --- |
| `Debug` | Internal state useful during development |
| `Information` | Normal operation milestones (start, complete, significant decisions) |
| `Warning` | Recoverable issues (retries, fallbacks, degraded behavior) |
| `Error` | Failed operations that need attention (with exception details) |
| `Critical` | System-level failures (database down, queue inaccessible) |

**Override noisy namespaces** to `Warning`:

- `System.Net.Http.HttpClient`
- `Microsoft.EntityFrameworkCore`
- `Microsoft.AspNetCore`

### Python — Logging

```python
import logging

logger = logging.getLogger(__name__)

# GOOD — PascalCase keys for Loggly consistency
logger.info("Processing invoice", extra={"ClaimId": claim_id, "ProcessId": process_id})

# BAD — snake_case keys (Loggly queries won't match .NET logs)
logger.info("Processing invoice", extra={"claim_id": claim_id, "process_id": process_id})

# BAD — string concatenation (loses structured context)
logger.info(f"Processing invoice {claim_id}")
```

- Python Lambda logging: use `aws_lambda_powertools` or standard `logging`
- Langfuse `@observe()` decorator for LLM tracing in AI Lambda

### Worker Service Logging Patterns

- Entry: `"Consumer start at: {time}"`
- Processing: Include `ClaimId` and `ProcessId` in every message
- Success: `"Completed process successfully!"`
- Failure: Log error with full exception details
- Idle: Suppress until `LogAfterLoopCount` threshold to reduce noise

## Health Checks

### .NET — Built-in Health Checks

```csharp
builder.Services.AddHealthChecks()
    .AddCheck<DatabaseHealthCheck>("Database")
    .AddCheck<S3BucketHealthCheck>("S3 Bucket")
    .AddCheck<SqsQueueHealthCheck>("SQS Queue");
```

**Endpoint**: `ApiEndpoints.Health` — returns structured JSON per dependency.

**Status mapping**:

| Health Status | HTTP Code |
| --- | --- |
| Healthy | 200 OK |
| Degraded | 200 OK |
| Unhealthy | 503 Service Unavailable |

### Health Check Implementation Pattern

```csharp
public class DatabaseHealthCheck : IHealthCheck
{
    private readonly BoehringerDbContext _context;

    public async Task<HealthCheckResult> CheckHealthAsync(
        HealthCheckContext context,
        CancellationToken cancellationToken = default)
    {
        var canConnect = await _context.Database.CanConnectAsync(cancellationToken);
        return canConnect
            ? HealthCheckResult.Healthy()
            : HealthCheckResult.Unhealthy("Cannot connect to database");
    }
}
```

### When to Add a Health Check

- Every external dependency the service needs to function (DB, queue, storage)
- Use timeouts (e.g., 5 seconds for database) to prevent health check hangs
- Do not add health checks for optional dependencies (logging sinks, analytics)

## Error Handling & Observability

### UnhandledExceptionMiddleware

Centralized exception handling in Shared library:

| Exception | HTTP Code | Response |
| --- | --- | --- |
| `ValidationException` | 400 | `ValidationFailureResponse` with error array |
| `BadHttpRequestException` | 400 | `ValidationFailureResponse` |
| `NotFoundException` | 404 | Error message |
| Unknown | 500 | Generic error (no stack trace in production) |

**Never expose internal details** (stack traces, connection strings, internal paths)
to clients in production error responses.
