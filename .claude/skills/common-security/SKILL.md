---
name: common-security
description: Security guardrails covering OWASP Top 10 adapted to this Python/LangGraph/Streamlit project. Use when reviewing code for security, handling API keys and secrets, validating user inputs, guarding against prompt injection, or configuring Streamlit safely.
---

# Security Skill

Security guardrails for biorce-mini. Covers OWASP Top 10 risks adapted to the
Python + LangGraph + Streamlit stack.

## When to Use

- Reviewing code for security vulnerabilities
- Handling API keys or `.env` secrets
- Validating user input from the Streamlit UI
- Guarding against prompt injection in LLM calls
- Reviewing LLM output before displaying or persisting it

## OWASP Top 10 — Stack-Specific Guidance

### 1. Broken Access Control

This project has no authentication layer (local demo). If deployed publicly:

- Use Streamlit's built-in secrets (`st.secrets`) — never `os.environ` directly in app code
- Restrict access at the infrastructure level (network rules, reverse proxy auth)
- Never expose raw LLM prompts or retrieved chunks to untrusted users without review

### 2. Cryptographic Failures

**Rules:**

- API keys go in `.env` — never hardcoded, never committed to git
- `.env` is in `.gitignore` — verify before every commit
- Use `.env.example` (already present) to document required variables without values
- Never log API keys, even partially (`sk-...` is enough for abuse)
- `python-dotenv` loads `.env` at startup — check the call is in `llm.py`, not scattered

### 3. Injection

**Prompt Injection (critical for LLM apps):**

Prompt injection is the LLM equivalent of SQL injection — a user crafts input that
alters the model's behavior by overriding instructions.

```python
# RISKY — raw user input embedded directly in system/user prompt
prompt = f"You are a clinical assistant. Answer this: {user_input}"

# SAFER — separate user content from system instructions clearly
system_prompt = "You are a clinical assistant. Use only the provided context."
user_message = f"Context: {context}\n\nQuestion: {user_input}"
```

**Rules:**

- Never embed raw `st.text_input()` values directly into system prompts
- Always place user content in a clearly delimited `user` message role
- Validate that user input does not contain instruction-override patterns before sending to LLM
- LLM responses are untrusted — never `eval()` or `exec()` them

**Command Injection:**

- Never use `os.system()` or `subprocess.run(shell=True)` with any user-derived input
- `ingest.py` should only read files from the known `data/docs/` folder — no dynamic paths from user input

### 4. Insecure Design

**Rules:**

- The LangGraph pipeline has a bounded loop (`iteration < 1`) — always keep this limit;
  removing it enables infinite LLM calls and cost abuse
- Never pass retrieved document content directly as a system prompt — always constrain
  the model's role in the system prompt separately from retrieved context
- Validate Pydantic models at LangGraph node boundaries — never assume state fields
  are present without defaults

### 5. Security Misconfiguration

**Streamlit:**

- Use `.streamlit/secrets.toml` for secrets in deployment (already in `.gitignore`)
- Never call `st.write()` with raw LLM output that contains unsanitized HTML/Markdown
  from untrusted sources
- Disable CORS in Streamlit config only if running behind a trusted reverse proxy

**Environment:**

- `.env` must never be committed —  verify `.gitignore` contains it
- Use `.env.example` to document variables without values

### 6. Vulnerable and Outdated Components

**Rules:**

- `uv.lock` is the source of truth for pinned versions — keep it committed
- Run `uv lock --upgrade` periodically and review changes
- Check `google-genai`, `langgraph`, and `chromadb` for security advisories (they
  change frequently as they are actively developed)

### 7. Identification and Authentication Failures

Not applicable in local demo mode. If adding authentication:

- Do not implement custom auth — use an established provider
- API key for Gemini: compare with constant-time comparison if verifying externally

### 8. Software and Data Integrity Failures

**Rules:**

- Lock file (`uv.lock`) must be committed — prevents supply chain attacks
- Do not `pip install` packages outside `pyproject.toml` without adding them formally
- Source documents in `data/docs/` are treated as trusted — do not ingest user-uploaded
  files without validation if the app is ever deployed publicly

### 9. Security Logging and Monitoring Failures

**Rules:**

- Log when the LLM is called (model, token count if available) — not the full prompt
- Log retrieval failures and empty results — these can indicate data ingestion problems
- Never log: API keys, full prompts if they contain PII, document contents
- Streamlit does not have built-in logging — use Python `logging` module explicitly

### 10. Server-Side Request Forgery (SSRF)

**Rules:**

- The LLM client calls the Google Gemini API — never allow user input to control the
  target URL or model name
- If adding web search or external URL fetching as a tool, validate all URLs against
  an allowlist before making requests

## Quick Security Checklist

Before merging any PR, verify:

- [ ] No API keys hardcoded in any `.py` file
- [ ] `.env` is listed in `.gitignore` and not staged
- [ ] User input from Streamlit is not embedded raw in system prompts
- [ ] LLM output is not passed to `eval()`, `exec()`, or `os.system()`
- [ ] The LangGraph loop iteration limit is still in place
- [ ] No `subprocess.run(shell=True)` with dynamic input
- [ ] Sensitive values are not logged


### 3. Injection

**SQL Injection:**

- EF Core parametrizes all LINQ queries automatically — never use `FromSqlRaw()` with concatenation
- If raw SQL is needed, use `FromSqlInterpolated()` (parametrized) — never string concat

```csharp
// GOOD
context.Processes.FromSqlInterpolated($"SELECT * FROM Process WHERE Id = {id}");

// BAD — never do this
context.Processes.FromSqlRaw($"SELECT * FROM Process WHERE Id = '{id}'");
```

**XSS:**

- React escapes output by default — never use `dangerouslySetInnerHTML`
- Sanitize any user-provided HTML before rendering
- API responses should set `Content-Type: application/json` — never return raw HTML from APIs

**Command Injection:**

- Python: never use `os.system()` or `subprocess.run(shell=True)` with user input
- .NET: never use `Process.Start()` with unsanitized arguments

### 4. Insecure Design

**Rules:**

- Clean Architecture enforces security boundaries by design:
  - Domain layer has zero external dependencies (no I/O, no HTTP, no SDK)
  - Infrastructure layer implements ports — security validation happens at boundaries
  - Presentation layer validates input before dispatching to Application
- FluentValidation on every request DTO — never trust input from external sources
- Rate limiting on public endpoints (configure in CDK or middleware)

### 5. Security Misconfiguration

**CORS:**

- **WithCredentials** policy: specific origins from config, credentials allowed
- **AnyOrigin** policy: public endpoints only (no credentials)
- Never use `AllowAnyOrigin()` + `AllowCredentials()` together — browsers reject this
- Origins loaded from `appsettings.json` `Cors:AllowedOrigins` — configure per environment

**HTTP Headers:**

- Use HSTS in production
- Set `X-Content-Type-Options: nosniff`
- Set `X-Frame-Options: DENY` for API endpoints

**Error Responses:**

- `UnhandledExceptionMiddleware` returns structured errors without stack traces in production
- Never expose internal exception details to the client

### 6. Vulnerable and Outdated Components

**Rules:**

- Dependabot configured for automatic dependency updates
- Review NuGet, pip, and npm advisories on every PR
- Pin exact versions in `Directory.Packages.props` (.NET), `pyproject.toml` (Python)
- CDK: keep `aws-cdk-lib` up to date — security patches affect deployed infrastructure

### 7. Identification and Authentication Failures

**Rules:**

- JWT tokens must be validated (issuer, audience, expiry, signature)
- API keys: compare with constant-time comparison (`CryptographicOperations.FixedTimeEquals`)
- Session timeout: configure token expiry in Cognito (not infinite)
- Never implement custom password hashing — delegate to Cognito

### 8. Software and Data Integrity Failures

**Rules:**

- GitHub Actions: use OIDC federation for AWS (no stored credentials)
- Lock files committed: `pnpm-lock.yaml`, `Directory.Packages.props`
- Verify checksums for external downloads in Dockerfiles
- CDK: use CDK Nag or similar for best-practice validation

### 9. Security Logging and Monitoring Failures

**Rules:**

- Log authentication failures (failed logins, invalid tokens, rejected API keys)
- Log authorization failures (access denied to resources)
- Include correlation context: `ClaimId`, `ProcessId`, `UserId` where applicable
- Never log sensitive data (passwords, tokens, full credit card numbers)
- Serilog enrichers: `FromLogContext()`, `WithExceptionDetails()`, `WithMachineName()`

See `common-observability` skill for the Structured Log Key Contract, PascalCase key naming
rules, and the full list of mandatory/contextual log properties.

### 10. Server-Side Request Forgery (SSRF)

**Rules:**

- Never pass user-supplied URLs directly to `HttpClient` or `httpx`
- Validate URLs against an allowlist of known hosts/domains
- Lambda functions: restrict outbound with VPC security groups
- S3 pre-signed URLs: set short expiry, validate bucket/key patterns

## Quick Security Checklist

Before merging any PR, verify:

- [ ] All endpoints have `.RequireAuthorization()` with appropriate policy
- [ ] All request DTOs have FluentValidation validators
- [ ] No secrets hardcoded in code or config files
- [ ] No `FromSqlRaw()` with string concatenation
- [ ] No `dangerouslySetInnerHTML` without sanitization
- [ ] CORS configured with specific origins (not `*` with credentials)
- [ ] Error responses don't leak stack traces or internal details
- [ ] Sensitive operations are logged (auth events, data access)
