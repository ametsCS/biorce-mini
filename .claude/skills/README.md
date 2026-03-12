# Claude Code Skills

This directory contains Agent Skills for Claude Code following the official structure defined in the [Claude Code documentation](https://code.claude.com/docs/en/skills).

**Note:** These skills are also compatible with Visual Studio Code (version 1.107+) as documented in the
[VS Code release notes](https://code.visualstudio.com/updates/v1_107#_reuse-your-claude-skills-experimental).

## What are Agent Skills?

Agent Skills package expertise into discoverable capabilities. Each Skill consists of a `SKILL.md` file with instructions
that Claude reads when relevant, plus optional supporting files like scripts and templates.

Skills are **model-invoked** Claude autonomously decides when to use them based on your request and the Skill's description.

## Skill Structure

Each skill follows this standard structure:

```txt
my-skill/
├── SKILL.md (required)
├── reference.md (optional documentation)
├── examples.md (optional examples)
├── scripts/
│   ├── helper.py (optional utility)
├── templates/
    ├── template.txt (optional template)
```

### SKILL.md Format

Every `SKILL.md` file must include YAML frontmatter:

```markdown
---
name: skill-name
description: Brief description of what this Skill does and when to use it
---

# Skill Name

## Instructions
Provide clear, step-by-step guidance for Claude.

## Examples
Show concrete examples of using this Skill.
```

**Field requirements:**

- `name`: Must use lowercase letters, numbers, and hyphens only (max 64 characters)
- `description`: Brief description of what the Skill does and when to use it (max 1024 characters)

## Naming Convention

Skill directories use a **stack prefix** to group related skills alphabetically:

| Prefix | Scope | Examples |
| ------ | ----- | -------- |
| `common-` | Cross-stack (applies to all) | `common-git`, `common-security`, `common-testing-conventions` |
| `python-` | Python | `python-architecture`, `python-testing` |

The `name` field in SKILL.md frontmatter **must match** the directory name.

## Available Skills

### Common (Cross-Stack)

#### [common-git](./common-git/)

Conventional Commits, PR workflow, branching strategy, and semantic versioning.

#### [common-observability](./common-observability/)

Python structured logging patterns for LangGraph nodes and Streamlit.

#### [common-security](./common-security/)

OWASP Top 10 adapted to this Python/LangGraph/Streamlit stack — prompt injection, API key safety, input validation.

#### [common-testing-conventions](./common-testing-conventions/)

Mandatory AAA pattern, `test_should_x_when_y` naming, and assertion conventions for Python/pytest.

**Supporting files:**

- `python.md` - pytest stack details
- `examples.md` - Full test examples
- `reference.md` - Naming rules, anti-patterns, checklist

### Python (python-*)

#### [python-architecture](./python-architecture/)

Module structure and patterns for this project: LangGraph nodes, RAG pipeline, LLM client, `src/` organization.

**Use when:**

- Adding a new LangGraph node
- Extending `src/rag.py`, `src/llm.py`, or `src/graph.py`
- Designing Pydantic models for state or node I/O
- Organizing a new utility module

**Supporting files:**

- `examples.md` - Code examples for nodes and RAG patterns
- `reference.md` - Advanced patterns
- `templates/entity.py` - Pydantic model template
- `templates/handler.py` - Node handler template
- `templates/port.py` - Protocol interface template

#### [python-testing](./python-testing/)

Python testing conventions including AAA pattern and pytest best practices.

**Use when:**

- Writing unit tests for LangGraph nodes, RAG, or LLM client
- Setting up pytest fixtures and mocks
- Implementing test builders

**Supporting files:**

- `examples.md` - Real test examples
- `reference.md` - pytest config, mock verification patterns

## How Claude Uses Skills

Claude automatically discovers Skills from `.claude/skills/` in this directory.
Skills activate automatically based on the context of your request — you don't need to explicitly invoke them.

To see available skills, ask Claude: `What Skills are available?`


#### [common-environments](./common-environments/)

Environment configuration contract for Development, LocalDevelopment, Test, and Production.

**Use when:**

- Configuring environment-specific settings
- Understanding DNS and configuration resolution
- Avoiding breaking environment parity

**Supporting files:**

- `reference.md` - Environment matrix, config file hierarchy, connection strings
- `examples.md` - Full JSON config per environment, Docker DNS, Testcontainers, WireMock

#### [common-git](./common-git/)

Commit messages, PR workflow, and branching strategy.

**Use when:**

- Creating commits
- Opening pull requests
- Managing branches
- Tagging releases

**Supporting files:**

- `reference.md` - Commit types, branch naming, CI workflow triggers

#### [common-observability](./common-observability/)

Structured logging, health checks, and monitoring patterns.

**Use when:**

- Configuring Serilog or Python logging
- Adding health checks for external dependencies
- Reviewing log output for structured context
- Debugging observability issues

#### [common-security](./common-security/)

Security guardrails covering OWASP Top 10 adapted to this stack.

**Use when:**

- Reviewing code for security vulnerabilities
- Implementing authentication or authorization
- Handling secrets or sensitive configuration
- Validating user input or configuring CORS

#### [common-testing-conventions](./common-testing-conventions/)

Mandatory AAA pattern, test naming conventions, and per-stack library references.

**Use when:**

- Writing unit tests with xUnit, Jest, or pytest
- Writing integration tests
- Writing E2E tests with Playwright
- Implementing test patterns

**Supporting files:**

- `dotnet.md` - .NET stack (xUnit, AwesomeAssertions, NSubstitute, Bogus, Verify.Xunit, WireMock, Testcontainers)
- `typescript.md` - TypeScript stack — Frontend & IaC (Jest, @testing-library, Playwright, Biome)
- `python.md` - Python stack (pytest, Mock/AsyncMock, pytest-snapshot, black, mypy, Pydantic)
- `examples.md` - Full test examples for C# and TypeScript
- `reference.md` - Naming rules, anti-patterns, checklist

### .NET Backend (dotnet-*)

#### [dotnet-architecture](./dotnet-architecture/)

Core architectural patterns including DDD and Clean Architecture.

**Use when:**

- Building a new .NET backend application
- Implementing complex business logic
- Organizing code into clean, testable layers
- Working with Entity Framework Core

**Supporting files:**

- `examples.md` - Full code examples for DDD patterns
- `reference.md` - Layer rules, dependency diagrams
- `templates/aggregate-root.cs` - Aggregate root template
- `templates/domain-event.cs` - Domain event templates

#### [dotnet-cqrs](./dotnet-cqrs/)

Command Query Responsibility Segregation patterns for .NET.

**Use when:**

- Implementing commands (write operations)
- Implementing queries (read operations)
- Creating request/response DTOs
- Setting up pipeline behaviors
- Handling domain events

**Supporting files:**

- `examples.md` - Full CQRS code examples
- `templates/command.cs` - Command with handler template
- `templates/query.cs` - Query with handler template

#### [dotnet-dependency-injection](./dotnet-dependency-injection/)

Proper DI usage and anti-patterns to avoid.

**Use when:**

- Setting up DI
- Registering services
- Configuring application dependencies
- Working with Options pattern
- Using HttpClient Factory

**Supporting files:**

- `examples.md` - Full DI code examples
- `reference.md` - Anti-patterns, lifetime decision tree
- `templates/service-extension.cs` - Service registration template

#### [dotnet-ef-migrations](./dotnet-ef-migrations/)

Creating and managing Entity Framework Core migrations.

**Use when:**

- Creating database migrations
- Applying schema changes
- Managing EF Core migration workflow

**Supporting files:**

- `reference.md` - Advanced scenarios and troubleshooting

#### [dotnet-integration-testing](./dotnet-integration-testing/)

Testcontainers, LocalStack, and WireMock for integration tests.

**Use when:**

- Writing integration tests
- Testing with real databases (PostgreSQL)
- Testing with AWS services (LocalStack)
- Mocking HTTP services

**Supporting files:**

- `examples.md` - Real examples (ApiServicesFactory, acceptance tests, Mother objects, CI workflow)

#### [dotnet-libraries](./dotnet-libraries/)

How to use FluentValidation, Mediator, and Entity Framework Core.

**Use when:**

- Working with validation
- Implementing commands and queries
- Performing database operations
- Setting up configuration validation

**Supporting files:**

- `examples.md` - Full code examples for all libraries
- `reference.md` - Options extension, testing, interceptors

#### [dotnet-test-doubles](./dotnet-test-doubles/)

Using Fakes, Dummies, Stubs, Spies, and Mocks.

**Use when:**

- Creating test data with Bogus
- Generating dummy objects with AutoFixture
- Mocking dependencies with NSubstitute
- Setting up HTTP mocks with WireMock.Net

**Supporting files:**

- `reference.md` - Advanced patterns for AutoFixture, Bogus, NSubstitute, WireMock

### Python (python-*)

#### [python-architecture](./python-architecture/)

Domain-Driven Design and Clean Architecture for Python AWS Lambda functions.

**Use when:**

- Building AWS Lambda functions with Python
- Implementing serverless backend features
- Organizing Python code with DDD patterns
- Using python-dependency-injector for DI
- Working with Pydantic and Protocol interfaces

**Supporting files:**

- `examples.md` - Full Python DDD code examples
- `reference.md` - DI configuration, AWS patterns
- `templates/entity.py` - Entity template
- `templates/handler.py` - Handler template
- `templates/port.py` - Protocol interface template

#### [python-testing](./python-testing/)

Python testing conventions including AAA pattern and pytest best practices.

**Use when:**

- Writing Python unit tests with pytest
- Writing Python integration tests
- Writing E2E tests with Playwright for Python
- Implementing test patterns in Python projects

**Supporting files:**

- `examples.md` - Real test examples (builders, fixtures, async tests, acceptance tests)
- `reference.md` - pytest config, commands, Builder cheat sheet, mock verification patterns

### TypeScript CDK (typescript-cdk-*)

#### [typescript-cdk-infrastructure](./typescript-cdk-infrastructure/)

AWS CDK patterns for infrastructure-as-code.

**Use when:**

- Creating or modifying CDK stacks
- Adding new AWS resources (Lambda, SQS, S3, RDS)
- Configuring deployment pipelines
- Setting up networking (VPC, subnets, security groups)
- Managing environment-specific infrastructure config

**Supporting files:**

- `reference.md` - Directory structure, config types, cross-resource references, SSM convention, commands

#### [typescript-cdk-testing](./typescript-cdk-testing/)

CDK testing patterns: snapshot tests, fine-grained assertions, normalization strategies.

**Use when:**

- Writing tests for new CDK stacks or constructs
- Adding assertions for specific resource properties
- Updating snapshots after intentional infrastructure changes
- Reviewing CDK test coverage

### TypeScript React (typescript-react-*)

#### [typescript-react-architecture](./typescript-react-architecture/)

Next.js App Router architecture with static export, service layer, and routing conventions.

**Use when:**

- Setting up frontend project structure
- Creating new pages and routes
- Adding API services (real and mock)
- Organizing types by domain
- Defining routing constants and navigation

**Supporting files:**

- `examples.md` - Full code examples for pages, services, and types
- `reference.md` - Project structure tree, layer rules, naming conventions
- `templates/page.tsx.template` - Protected page template with data fetching
- `templates/service.ts.template` - Domain service template with real + mock

#### [typescript-react-components](./typescript-react-components/)

Chakra UI v3 compound components, theme system, layout components, and UI patterns.

**Use when:**

- Building UI components with Chakra UI v3
- Working with the theme system (colors, tokens, dark mode)
- Creating layout components (page bodies, split layouts)
- Implementing tables with filtering and pagination
- Building forms with validation

**Supporting files:**

- `examples.md` - Full code examples for all component patterns
- `reference.md` - Chakra v3 migration table, theme tokens, layout specs

#### [typescript-react-hooks](./typescript-react-hooks/)

Domain-specific React hooks for data fetching, API access, and auth.

**Use when:**

- Creating domain-specific data hooks (CRUD operations)
- Accessing API services from components
- Encapsulating data fetching with loading/error state
- Managing authentication tokens

**Supporting files:**

- `examples.md` - Full hook examples for all patterns
- `templates/hook.tsx.template` - Domain hook template with data fetching

#### [typescript-react-pdf](./typescript-react-pdf/)

PDF rendering with react-pdf, worker configuration, Next.js integration, and component testing.

**Use when:**

- Displaying PDF documents from base64, URL, or Uint8Array sources
- Building custom PDF viewers with pagination and zoom
- Configuring PDF.js worker for Next.js
- Testing components that render PDFs

**Supporting files:**

- `examples.md` - Full code examples for PDF viewer, dynamic import, and tests

#### [typescript-react-state](./typescript-react-state/)

Zustand stores with devtools, persist middleware, and two-phase search pattern.

**Use when:**

- Creating new Zustand stores
- Managing global application state (auth, settings)
- Implementing search and filter logic
- Persisting state to localStorage

**Supporting files:**

- `examples.md` - Full store examples with middleware and selectors
- `templates/store.ts.template` - Store template with devtools and selector hook

#### [typescript-react-testing](./typescript-react-testing/)

Frontend testing with Jest, React Testing Library, and test data builders.

**Use when:**

- Writing unit tests for React components
- Creating test data builders
- Setting up mock data for development and testing
- Testing hooks, services, and Zustand stores

**Supporting files:**

- `examples.md` - Full test examples for components, hooks, and stores
- `reference.md` - Builder base class, test organization, naming rules
- `templates/builder.ts.template` - Test data builder template
- `templates/component.test.tsx.template` - Component test template

## How Claude Uses Skills

Claude automatically discovers Skills from:

- Project Skills: `.claude/skills/` (this directory)
- Personal Skills: `~/.claude/skills/`
- Plugin Skills: bundled with installed plugins

To view all available Skills, ask Claude:

```txt
What Skills are available?
```

Skills activate automatically based on the context of your request—you don't need to explicitly invoke them.

## Relationship with GitHub Copilot Skills

This repository also contains skills for GitHub Copilot in `.github/copilot-skills/`.

**Key differences:**

| Aspect | Claude Skills | GitHub Copilot Skills |
| ------ | ------------- | --------------------- |
| Location | `.claude/skills/` | `.github/copilot-skills/` |
| File naming | `SKILL.md` with YAML frontmatter | `.md` files with custom frontmatter |
| Invocation | Model-invoked (automatic) | Context-based |
| Structure | Official Claude structure | GitHub-specific format |
| Compatibility | Claude Code + VS Code 1.107+ | GitHub Copilot (VS Code) |

Both skill systems can coexist in the same project and complement each other.

**Note:** With VS Code 1.107+, you can use Claude Skills directly in VS Code, making `.claude/skills/` the preferred
location for new skills as they work across both Claude Code and VS Code.

## Best Practices

### Keep Skills Focused

One Skill should address one capability:

- Focused: "PDF form filling", "Excel data analysis", "Git commit messages"
- Too broad: "Document processing", "Data tools"

### Write Clear Descriptions

Help Claude discover when to use Skills by including specific triggers in your description:

**Clear:**

```yaml
description: Analyze Excel spreadsheets, create pivot tables, and generate charts. Use when working with Excel files, spreadsheets, or analyzing tabular data in .xlsx format.
```

**Vague:**

```yaml
description: For files
```

### Test with Your Team

Have teammates use Skills and provide feedback:

- Does the Skill activate when expected?
- Are the instructions clear?
- Are there missing examples or edge cases?

## Contributing to Skills

When updating or creating skills:

1. Follow the **naming convention** (stack prefix + context)
2. Keep them **concise and actionable**
3. Include **code examples**
4. Show both **good and bad** patterns
5. Reference **related skills** using relative links
6. Update the YAML frontmatter if changing behavior
7. Test that Claude discovers the Skill correctly

## Learn More

- [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills)
- [Agent Skills Best Practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)
- [Agent Skills Overview](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)

---

**Last Updated:** 2026-02-09
**Maintained by:** Development Team
