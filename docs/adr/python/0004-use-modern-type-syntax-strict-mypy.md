# 0004 - Use Modern Python Type Syntax and Strict mypy

**Date:** 2025-10-15

**Status:** Accepted

## Context

Python 3.10+ introduced modern type syntax improvements (PEP 604 union types). We needed to decide
on type checking approach and syntax standards for better code quality and maintainability.

## Decision

We will use **modern Python type syntax** with **strict mypy type checking**:

- Use `Type | None` instead of `Optional[Type]`
- Use `context` directly instead of `context as context_`
- Use `lambda_context` as parameter name (not `context`)
- Avoid `Any` type - use `object` or specific types
- Enable mypy strict mode in all projects

## Rationale

**Modern union syntax (`Type | None`):**

- Introduced in Python 3.10 (PEP 604)
- More readable: `str | None` vs `Optional[str]`
- Consistent with other languages
- Less imports needed
- Official Python direction

**Avoid `Optional` import:**

```python
# Old way
from typing import Optional
value: Optional[str] = None

# Modern way (Python 3.10+)
value: str | None = None
```

**Direct imports without aliases:**

```python
# Preferred
from aws_lambda_typing import context
def handler(event, lambda_context: context.Context):
    pass

# Avoid
from aws_lambda_typing import context as context_
def handler(event, context: context_.Context):  # Confusing!
    pass
```

**Use descriptive parameter names:**

- `lambda_context` instead of `context` (avoids confusion with context module)
- `sut` for subject under test
- `actual` for test results
- `expected` for comparison values

**Avoid `Any` type:**

```python
# Bad - no type safety
data: Dict[str, Any] = {}

# Good - specific types
data: Dict[str, object] = {}  # When type truly varies
data: Dict[str, str | int] = {}  # When specific types known
```

**Strict mypy configuration:**

```toml
[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
disallow_untyped_defs = true
```

## Consequences

**Positive:**

- Better code quality and IDE support
- Catch bugs at development time
- Self-documenting code
- Easier refactoring
- Modern Python idioms

**Negative:**

- Requires Python 3.10+ (we use 3.12, so no issue)
- More verbose code (type hints everywhere)
- Initial learning curve for team

## Implementation

**All Python files must:**

1. Use modern union syntax (`Type | None`)
2. Have full type hints on all functions
3. Pass `mypy` strict mode checks
4. Avoid `Any` type usage

**Example:**

```python
from typing import Dict
from aws_lambda_typing import context, responses

def lambda_handler(
    event: Dict[str, object], 
    lambda_context: context.Context | None
) -> responses.APIGatewayProxyResponseV2:
    return {"statusCode": 200, "body": "{}"}
```

**CI/CD enforcement:**

```yaml
- name: Type check
  run: uv run mypy app.py test_app.py
```

## References

- [PEP 604 - Union Operator](https://peps.python.org/pep-0604/)
- [mypy Documentation](https://mypy.readthedocs.io/)
- [Python Type Hints (PEP 484)](https://peps.python.org/pep-0484/)
