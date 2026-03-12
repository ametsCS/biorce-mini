# 0002 - Use Testcontainers for Acceptance Testing

**Date:** 2025-10-15

**Status:** Accepted

## Context

We need to test our Lambda functions running in Docker containers to ensure they work correctly in
a production-like environment. Initial approach used PowerShell scripts to manually manage Docker
containers, but this had limitations around cross-platform compatibility and test lifecycle management.

## Decision

We will use **testcontainers-python** for acceptance testing of containerized Lambda functions.

## Rationale

**Why testcontainers:**

- **Automatic lifecycle:** Containers start/stop automatically with pytest fixtures
- **Clean tests:** Each test suite gets fresh containers, no state leakage
- **Cross-platform:** Works on Windows, Linux, macOS (unlike PowerShell scripts)
- **Pythonic:** Integrates naturally with pytest and Python test code
- **Industry standard:** Widely used pattern in Java, now available for Python
- **No manual cleanup:** Containers are always removed, even if tests fail

**Problems with PowerShell scripts:**

- Platform-specific (Windows only)
- Manual container cleanup required
- Error-prone (forgot to stop containers)
- Not integrated with test framework
- Hard to run in CI/CD pipelines

## Consequences

**Positive:**

- Tests run consistently across all platforms
- No leftover containers after test failures
- Better integration with pytest
- Simpler test code (no subprocess calls)
- Works seamlessly in GitHub Actions

**Negative:**

- Requires Docker to be running (already needed for Lambda testing)
- Slightly slower first test run (but subsequent runs are fast)
- Additional Python dependency

## Implementation

Add to `pyproject.toml`:

```toml
[dependency-groups]
dev = [
    "pytest>=8.0.0",
    "testcontainers>=4.0.0",
    "requests>=2.31.0",
]
```

Test fixture example:

```python
@pytest.fixture(scope="module")
def lambda_container() -> Generator[DockerContainer, None, None]:
    container = DockerContainer("modulea-test:latest")
    container.with_exposed_ports(8080)
    container.with_bind_ports(8080, 9000)
    container.start()
    
    yield container
    
    container.stop()  # Automatic cleanup
```

## References

- [testcontainers-python](https://github.com/testcontainers/testcontainers-python)
- [testcontainers.org](https://testcontainers.org/)
