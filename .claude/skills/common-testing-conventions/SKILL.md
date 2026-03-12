---
name: common-testing-conventions
description: Mandatory testing conventions including AAA pattern, test naming, and assertions for Python with pytest. Use when writing unit tests, integration tests, or verifying mock interactions for any module in this project.
---

# Testing Conventions Skill

Mandatory testing conventions for biorce-mini. All tests are written in Python using
pytest.

## When to Use

- Writing unit tests for LangGraph nodes, RAG functions, or LLM client
- Writing integration tests against Chroma or the Gemini API
- Setting up test class structure or fixtures
- Verifying mock interactions

## Supporting Files

| File | Description |
|------|-------------|
| [python.md](./python.md) | Python testing stack (pytest, Mock/AsyncMock, pytest-snapshot, Pydantic) |
| [examples.md](./examples.md) | Full test examples |
| [reference.md](./reference.md) | Naming rules, anti-patterns, checklist |

## Core Principles

### 1. AAA Pattern (Mandatory)

All tests **MUST** follow Arrange-Act-Assert with clear comments:

```python
def test_should_return_chunks_when_query_matches_documents():
    # Arrange
    collection = build_test_collection(docs=["aspirin reduces inflammation"])
    sut = Retriever(collection)

    # Act
    actual = sut.retrieve(query="aspirin")

    # Assert
    assert len(actual) > 0
    assert "aspirin" in actual[0].lower()
```

**Rules:**

- Each section clearly separated by comments
- Never mix phases
- **No `if`, `switch`, or conditional logic** inside Arrange, Act, or Assert
- **No `try/catch`** inside the AAA blocks — use `pytest.raises()` instead
- Omit a comment only if that section is empty
- If a test needs branching, split into separate test functions (one per scenario)

### 2. Test Naming Convention

```txt
test_should_{expected_behavior}_when_{condition}
```

| ✓ Good | ✗ Bad |
|-------|-------|
| `test_should_return_chunks_when_query_matches` | `test_retrieve` |
| `test_should_raise_when_api_key_missing` | `test_error_case` |
| `test_should_return_empty_when_no_documents` | `test_should_work` |

### 3. Standard Variables

| Purpose | Name |
|---------|------|
| Subject under test | `sut` |
| Expected value | `expected` |
| Actual result | `actual` |

```python
expected = ["chunk about aspirin"]
actual = sut.retrieve(query="aspirin")
assert actual == expected
```

## Test Structure

```python
import pytest
from unittest.mock import MagicMock
from src.rag import Retriever

class TestRetriever:
    def setup_method(self):
        self.mock_collection = MagicMock()
        self.sut = Retriever(self.mock_collection)

    def test_should_return_chunks_when_query_matches(self):
        # Arrange
        self.mock_collection.query.return_value = {
            "documents": [["aspirin reduces fever"]],
            "distances": [[0.12]],
        }

        # Act
        actual = self.sut.retrieve(query="aspirin")

        # Assert
        assert actual == ["aspirin reduces fever"]
        self.mock_collection.query.assert_called_once()
```

## Related Skills

- **python-testing:** Python-specific AAA pattern, pytest configuration, mocks, builders

}
```

**Rules:**

- Each section clearly separated by comments
- Never mix phases
- **No `if`, `switch`, or conditional logic** inside Arrange, Act, or Assert blocks
- **No `try/catch`** inside Arrange, Act, or Assert blocks
- For exceptions, use `AwesomeAssertions` `.Should().ThrowAsync<T>()` or Jest `expect(...).rejects.toThrow()`
- Omit comment if section is empty
- If a test needs branching, split it into separate test methods (one per scenario)

### 2. Test Naming Convention

```txt
Should_{ExpectedBehavior}_When_{Condition}
```

| ✓ Good                                       | ✗ Bad             |
| -------------------------------------------- | ----------------- |
| `Should_CreateGroup_When_RequestIsValid`     | `TestCreateGroup` |
| `Should_ThrowNotFound_When_UserDoesNotExist` | `"should login"`  |
| `Should_ReturnEmptyList_When_NoRecordsFound` | `Should_Work`     |

### 3. Standard Variables

| Purpose | Name |
| ------- | ---- |
| Subject under test | `sut` |
| Expected value | `expected` |
| Actual result | `actual` |

```csharp
var expected = GroupMother.Create(id: groupId);
var actual = await _sut.Handle(query, CancellationToken.None);
actual.Id.Should().Be(expected.Id);
```

## Test Class Structure (C#)

```csharp
public class CreateGroupCommandHandlerTests
{
    private readonly Fixture _fixture;
    private readonly CreateGroupCommandHandler _sut;
    private readonly IBoehringerRepository _repository;

    public CreateGroupCommandHandlerTests()
    {
        _fixture = new();
        _repository = Substitute.For<IBoehringerRepository>();
        _sut = new(_repository);
    }

    [Fact]
    public async Task Should_CreateGroup_When_RequestIsValid()
    {
        // Test implementation
    }
}
```

## Libraries by Stack

See the dedicated supporting file for each stack:

- **.NET Backend:** [dotnet.md](./dotnet.md) — xUnit, AwesomeAssertions, NSubstitute,
  AutoFixture, Bogus, Verify.Xunit, WireMock.Net, Testcontainers (PostgreSQL,
  LocalStack)
- **Frontend & IaC (TypeScript):** [frontend.md](./frontend.md) — Jest,
  @testing-library/react, Playwright, Biome
- **Python:** [python.md](./python.md) — pytest, pytest-asyncio, pytest-snapshot,
  unittest.mock, black, mypy, Pydantic

## Related Skills

- **dotnet-test-doubles:** Bogus, AutoFixture, NSubstitute, WireMock patterns
- **dotnet-integration-testing:** Testcontainers, LocalStack, WebApplicationFactory
- **python-testing:** Python-specific AAA pattern, pytest configuration
