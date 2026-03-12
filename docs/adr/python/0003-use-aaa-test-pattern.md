# 0003 - Use AAA Test Pattern with Explicit Comments

**Date:** 2025-10-15

**Status:** Accepted

## Context

Tests need to be readable and maintainable. Without a consistent structure, tests become hard to
understand, especially for new team members or when debugging failures. We needed a standard pattern
that makes test intent clear.

## Decision

All tests must follow the **AAA (Arrange-Act-Assert) pattern** with explicit section comments:

```python
def test_Should_ReturnSuccess_When_ValidInput(self) -> None:
    """Test description"""
    # Arrange
    input_data = {"key": "value"}
    expected_result = "success"
    
    # Act
    actual = process(input_data)
    
    # Assert
    assert actual == expected_result
```

## Rationale

**Why AAA with comments:**

- **Readability:** Anyone can understand test structure immediately
- **Consistency:** All tests follow same pattern
- **Debugging:** Easy to identify which phase failed
- **Review:** Code reviews focus on test logic, not structure
- **Self-documenting:** Test phases are explicit

**Test naming convention:**

Format: `test_Should_{ExpectedBehavior}_When_{Condition}`

Examples:

- `test_Should_Return200StatusCode_When_InvokedWithEmptyEvent`
- `test_Should_ReturnHelloWorldMessage_When_InvokedSuccessfully`

**Variable naming in tests:**

- `sut` - Subject Under Test (the thing being tested)
- `actual` - Output from the Act phase
- `expected` - Expected values for comparison

## Consequences

**Positive:**

- Tests are immediately understandable
- New developers can write tests correctly from examples
- Test failures are easier to debug
- Code reviews are faster
- Test reports are more descriptive

**Negative:**

- Slightly more verbose (extra comment lines)
- Requires team discipline to follow pattern

## Implementation

**Template for unit tests:**

```python
def test_Should_ExpectedBehavior_When_Condition(self) -> None:
    """Description of what this test verifies"""
    # Arrange
    # Set up test data and preconditions
    event: Dict[str, object] = {}
    expected_status: int = 200
    
    # Act
    # Execute the code being tested
    actual = lambda_handler(event, None)
    
    # Assert
    # Verify expected outcomes
    assert actual["statusCode"] == expected_status
```

**Enforcement:**

- All tests must have `# Arrange`, `# Act`, `# Assert` comments
- Test names must follow `test_Should_*_When_*` convention
- Code reviews check for pattern compliance

## References

- [Arrange-Act-Assert Pattern](https://automationpanda.com/2020/07/07/arrange-act-assert-a-pattern-for-writing-good-tests/)
- [Roy Osherove - Naming Standards](http://osherove.com/blog/2005/4/3/naming-standards-for-unit-tests.html)
