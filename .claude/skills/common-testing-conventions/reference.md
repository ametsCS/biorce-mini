# Testing Conventions Reference

## Test Naming Rules

### Pattern

```txt
Should_{ExpectedBehavior}_When_{Condition}
```

### Rules

- Use **PascalCase** for both parts
- Do **NOT** use natural language sentences
- Be **specific** about behavior and condition

### Good Examples

| Test Name | Description |
| --------- | ----------- |
| `Should_LoginSuccessfully_When_CredentialsAreValid` | Clear behavior and condition |
| `Should_ThrowNotFound_When_UserDoesNotExist` | Exception testing |
| `Should_ReturnEmptyList_When_NoRecordsFound` | Edge case |
| `Should_CreateGroupSuccessfully_When_AllDataIsValid` | Success path |
| `Should_ThrowArgumentException_When_RequestIsNull` | Input validation |

### Bad Examples

| Test Name | Problem |
| --------- | ------- |
| `"should successfully login with valid credentials"` | Natural language |
| `TestLogin` | Not descriptive |
| `Test_1` | Meaningless |
| `LoginTest` | Doesn't describe behavior |
| `Should_Work` | Too vague |
| `CreateGroup_Success` | Wrong format |

## Variable Naming

| Purpose | Name | Description |
| ------- | ---- | ----------- |
| Subject under test | `sut` | The main object being tested |
| Expected value | `expected` | Value to compare against |
| Actual result | `actual` | Value returned from Act phase |

## Anti-Patterns

### ✗ Missing AAA Comments

```csharp
// BAD
[Fact]
public async Task TestCreateGroup()
{
    var request = new CreateGroupRequest { Name = "Test" };
    var command = new CreateGroupCommand(request);
    var actual = await _sut.Handle(command, CancellationToken.None);
    actual.Should().NotBeNull();
}

// GOOD
[Fact]
public async Task Should_CreateGroup_When_RequestIsValid()
{
    // Arrange
    var request = new CreateGroupRequest { Name = "Test" };
    var command = new CreateGroupCommand(request);

    // Act
    var actual = await _sut.Handle(command, CancellationToken.None);

    // Assert
    actual.Should().NotBeNull();
}
```

### ✗ Missing Mock Verification

```csharp
// BAD - Repository call not verified
[Fact]
public async Task Should_CreateGroup_When_RequestIsValid()
{
    // Arrange
    var command = new CreateGroupCommand(new CreateGroupRequest { Name = "Test" });

    // Act
    var actual = await _sut.Handle(command, CancellationToken.None);

    // Assert
    actual.Should().NotBeNull();
    // Missing: Verify repository was called!
}

// GOOD
[Fact]
public async Task Should_CreateGroup_When_RequestIsValid()
{
    // Arrange
    var command = new CreateGroupCommand(new CreateGroupRequest { Name = "Test" });

    // Act
    var actual = await _sut.Handle(command, CancellationToken.None);

    // Assert
    actual.Should().NotBeNull();
    _repository.Received(1).AddGroup(Arg.Any<Group>());
    await _repository.Received(1).SaveChangesAsync(Arg.Any<CancellationToken>());
}
```

### ✗ Multiple Assertions Without Clear Purpose

```csharp
// BAD - Too many unrelated assertions
actual.Name.Should().Be("Test");
actual.Id.Should().NotBeEmpty();
actual.Status.Should().Be(Status.Active);
otherThing.Should().BeTrue();
unrelatedValue.Should().NotBeNull();

// GOOD - Focused assertions with one concept
actual.Should().NotBeNull();
actual.Id.Should().NotBeEmpty();
actual.Name.Should().Be("Test Group");
```

### ✗ Control Flow in AAA Blocks

```csharp
// BAD - if inside Assert
// Assert
if (result is null)
{
    actual.Should().BeNull();
}
else
{
    actual.Should().NotBeNull();
}

// BAD - try/catch inside Act
// Act
try
{
    await _sut.Handle(command, CancellationToken.None);
}
catch (Exception ex)
{
    actual = ex;
}

// GOOD - Use AwesomeAssertions for exceptions
// Act
var act = () => _sut.Handle(command, CancellationToken.None);

// Assert
await act.Should().ThrowAsync<NotFoundException>();

// GOOD - Split into separate tests for different scenarios
[Fact]
public async Task Should_ReturnNull_When_RecordNotFound() { ... }

[Fact]
public async Task Should_ReturnRecord_When_RecordExists() { ... }
```

```typescript
// BAD - if inside Assert (Playwright / Jest)
if (responseStatus !== null && responseStatus >= 400) {
    expect(responseStatus).toBeGreaterThanOrEqual(400);
    return;
}
await expect(button).toBeVisible();

// GOOD - One clear assertion path per test
await expect(googleButton).toBeVisible({ timeout: 10000 });
```

## Test Checklist

1. ✓ AAA pattern with comments
2. ✓ `Should_When_` naming convention
3. ✓ Use `sut`, `actual`, `expected` variables
4. ✓ Verify all mock interactions
5. ✓ Use Mother pattern for complex test data
6. ✓ One assertion concept per test
7. ✓ Tests are independent and isolated
8. ✓ No shared mutable state between tests
9. ✓ **No `if`, `switch`, `try/catch`** inside Arrange, Act, or Assert blocks
10. ✓ One scenario per test — if branching is needed, create separate tests
