# AI Agents, Skills & Customization Reference

A complete reference of every AI customization layer used in this project — agents,
skills, prompts, and instructions — so you can replicate the same setup in any VS Code workspace.

---

## How It All Fits Together

```txt
┌─────────────────────────────────────────────────────────────────┐
│                        VS Code / Copilot Chat                   │
├──────────────┬──────────────────┬───────────────────────────────┤
│  Agents      │  Prompts         │  Skills (model-invoked)       │
│  .github/    │  .github/        │  .claude/skills/              │
│  agents/     │  prompts/        │  (also loaded by Claude Code) │
├──────────────┴──────────────────┴───────────────────────────────┤
│  Instructions (.instructions.md — scoped to folder)             │
│  Global instructions (.github/copilot-instructions.md)          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. VS Code Settings Required

File: `.vscode/settings.json`

```json
{
    "github.copilot.chat.cli.customAgents.enabled": true
}
```

**Why this matters:**
- `github.copilot.chat.cli.customAgents.enabled` — experimental flag that enables
  the loading of custom `.agent.md` files. Defaults to `true` but must be explicit
  to guarantee activation.
- The agent discovery path `.github/agents/*.agent.md` is **hardcoded** in the
  Copilot Chat extension — it cannot be overridden via settings.
- The old `chat.agentFilesLocations` key is **not a real setting** and does nothing.

---

## 2. Agents (`.github/agents/`)

Agents are custom AI modes that appear in the Copilot Chat agent picker (`@agent-name`).
Each agent is a `.agent.md` file with YAML frontmatter and a system prompt body.

### YAML Frontmatter Fields

```yaml
---
name: my-agent              # Must match the filename prefix
description: >              # Shown in the agent picker
  What this agent does.
user-invocable: true        # false = only callable by other agents (not shown in picker)
tools: [read, search, edit, execute, agent]
agents: ['other-agent']     # Sub-agents this agent can delegate to
---
```

### Available Tool Values

| Tool | What It Enables |
|------|----------------|
| `read` | Read files in the workspace |
| `search` | Search the workspace and codebase |
| `edit` | Create/modify files |
| `execute` | Run terminal commands |
| `agent` | Delegate to other agents (required for orchestrators) |

---

### Agents in This Project

#### `demo.code-reviewer` — Code Review Agent
**File:** `.github/agents/demo.code-reviewer.agent.md`
**User-invocable:** yes
**Delegates to:** `demo.tdd-implement`

Reviews staged, unstaged, branch diff, or active PR. Classifies findings by severity
(Critical / High / Medium / Low / Nit) with strict anti-inflation rules. After presenting
findings, proactively offers to apply fixes via TDD one by one.

**Severity anti-inflation rules embedded in the agent:**
- Critical → must describe the exact production failure in one sentence
- High → must point to a concrete input path that produces wrong behavior
- Convention violations → Low/Nit, never Medium or above

---

#### `demo.pr-feedback` — PR Comment Processor
**File:** `.github/agents/demo.pr-feedback.agent.md`
**User-invocable:** yes
**Delegates to:** `demo.code-reviewer`, `demo.tdd-implement`

Reads all review comments from the active pull request. For each comment: presents it,
asks the user to apply or discard, applies fixes via TDD, and replies to comments that
don't apply on GitHub before dismissing them.

---

#### `demo.refactor` — Refactor Agent
**File:** `.github/agents/demo.refactor.agent.md`
**User-invocable:** yes

Analyzes code for smells and proposes SOLID-aligned refactors. Reads the code, presents
findings with suggested fixes, and applies changes after user approval.

---

#### `demo.tdd-coach` — TDD Coordinator
**File:** `.github/agents/demo.tdd-coach.agent.md`
**User-invocable:** yes
**Delegates to:** `demo.tdd-red`, `demo.tdd-green`, `demo.tdd-refactor`

Enforces the Red-Green-Refactor TDD cycle. Breaks down features into a list of behaviors
(one test per behavior), then delegates each phase to specialized workers. Never writes
code directly — the workers do that.

```txt
┌─────────────────────────────────────┐
│ demo.tdd-coach (coordinator)        │
├──────────┬──────────┬───────────────┤
│ Red      │ Green    │ Refactor      │
│ worker   │ worker   │ worker        │
└──────────┴──────────┴───────────────┘
```

---

#### `demo.tdd-red` — Write Failing Test
**File:** `.github/agents/demo.tdd-red.agent.md`
**User-invocable:** false (only called by `demo.tdd-coach`)

Writes a single failing test, runs it, and confirms it fails for the right reason.
Never writes production code.

---

#### `demo.tdd-green` — Make Test Pass
**File:** `.github/agents/demo.tdd-green.agent.md`
**User-invocable:** false (only called by `demo.tdd-coach`)

Writes the minimum production code to make the failing test pass, following the
module structure of this project (`src/rag.py`, `src/graph.py`, `src/llm.py`).
Returns the production file path and test result.

---

#### `demo.tdd-refactor` — Improve Structure
**File:** `.github/agents/demo.tdd-refactor.agent.md`
**User-invocable:** false (only called by `demo.tdd-coach`)

Improves code structure while keeping all tests green. Extracts functions, renames for
clarity, removes duplication, applies SOLID principles. Runs `pytest` and `ruff` after
every change.

---

#### `demo.tdd-implement` — Full TDD Cycle (Single Agent)
**File:** `.github/agents/demo.tdd-implement.agent.md`
**User-invocable:** false (only called by `demo.code-reviewer` / `demo.pr-feedback`)

Executes the full Red→Green→Refactor cycle for a single already-known fix. Used when
the calling agent knows exactly what needs to change and just needs it done with TDD.

---

## 3. Prompts (`.github/prompts/`)

Prompts are reusable slash commands in Copilot Chat. Their `mode: agent` frontmatter
means they run with full agentic capabilities (tools enabled).

### YAML Frontmatter Fields

```yaml
---
description: Human-readable description shown in the prompt picker
mode: agent      # or: ask (no tools), edit (file edits only)
---
```

### Prompts in This Project

| File | What It Does |
|------|-------------|
| `demo.scaffold-feature.prompt.md` | Generates the full file skeleton for a new Python module in this project (new LangGraph node, RAG component, or utility). Asks for module name and location. |
| `demo.smart-commit.prompt.md` | Analyzes staged/unstaged changes and creates a Conventional Commit with a well-crafted message. |
| `demo.pr-sync.prompt.md` | Creates or updates a pull request with auto-generated title and description from the branch diff. |
| `demo.create-adr.prompt.md` | Generates a new Architecture Decision Record with auto-numbering (Nygard format). |
| `demo.update-dependencies.prompt.md` | Analyzes open Dependabot PRs, assesses risk, and helps batch-update dependencies in `pyproject.toml`. |
| `demo.create-skill.prompt.md` | Generates a new `.claude/skills/` skill following project conventions. |
| `demo.create-weekly-tags.prompt.md` | Creates annotated semantic version git tags grouped by work week. |

---

## 4. Skills (`.claude/skills/`)

Skills are **model-invoked** — the AI decides when to use them based on the task
and each skill's description. They work in both Claude Code and VS Code (v1.107+).

### File Structure

```txt
.claude/skills/
├── README.md
└── {stack-prefix}-{topic}/
    └── SKILL.md          ← required
    └── reference.md      ← optional
    └── templates/        ← optional
```

### SKILL.md Frontmatter

```yaml
---
name: skill-name           # lowercase, hyphens, max 64 chars
description: >             # when to invoke this skill, max 1024 chars
  Brief description.
---
```

### Naming Convention

| Prefix | Scope |
|--------|-------|
| `common-` | Cross-stack (all technologies) |
| `python-` | Python modules in this project |

### Skills in This Project

#### Common (cross-stack)

| Skill | When to Use |
|-------|------------|
| `common-api-design` | REST endpoint naming, HTTP verbs, status codes, Problem Details (RFC 9457), pagination, error responses |
| `common-docker` | Docker Compose setup for local services |
| `common-e2e-testing` | End-to-end testing conventions — AAA, polling, locator best practices |
| `common-environments` | Environment model: Development / Test / Production config contract |
| `common-git` | Conventional Commits, PR workflow, branching strategy, semantic versioning |
| `common-observability` | Structured logging, tracing, health checks for Python services |
| `common-security` | OWASP Top 10 adapted to this stack — secrets, prompt injection, input validation |
| `common-testing-conventions` | Mandatory AAA pattern, naming (`test_should_x_when_y`), assertions |

#### Python

| Skill | When to Use |
|-------|------------|
| `python-architecture` | Module structure for `src/` — RAG pipeline, LangGraph nodes, LLM client separation |
| `python-testing` | pytest conventions — AAA, naming, mocks, fixtures, parametrize |

---

## 5. Instructions (`.instructions.md`)

Scoped instructions are automatically injected into the AI context when working on
files matching the `applyTo` glob. They reinforce layer-specific rules without repeating
them in every prompt.

### Frontmatter

```yaml
---
applyTo: "path/to/folder/**"   # glob pattern relative to workspace root
---
```

### Instructions in This Project

| File Location | `applyTo` | Purpose |
|--------------|-----------|---------|
| `Boehringer/src/Boehringer/Domain/.instructions.md` | `Boehringer/src/Boehringer/Domain/**` | Domain layer rules: aggregate roots, value objects, domain events, ports |
| `Boehringer/src/Boehringer/Application/.instructions.md` | `Boehringer/src/Boehringer/Application/**` | Application layer rules: CQRS structure, response DTOs, handler conventions |
| `Boehringer/src/Boehringer/Infrastructure/.instructions.md` | `Boehringer/src/Boehringer/Infrastructure/**` | Infrastructure layer: EF config, column types, enum conversions, indexes |
| `Boehringer/src/apps/.instructions.md` | `Boehringer/src/apps/**` | Presentation layer: thin API, no business logic, each app type rules (.NET/Python/TS) |
| `Boehringer/src/apps/Minimal.Api/.instructions.md` | `Boehringer/src/apps/Minimal.Api/**` | Minimal API specifics: endpoint structure, `TypedResults`, extension registration |
| `Boehringer/test/.instructions.md` | `Boehringer/test/**` | Test rules: AAA pattern, naming convention, test doubles, stack-specific conventions |
| `Boehringer/src/iac/.instructions.md` | `Boehringer/src/iac/**` | CDK rules: stack structure, config organization, buildspecs |
| `shared/src/Backend/.instructions.md` | `shared/src/Backend/**` | Shared library rules: base classes, port interfaces, AWS adapters, middleware |

---

## 6. Global Instructions (`.github/copilot-instructions.md`)

Applied to every conversation in the workspace. Contains the top-level architecture
and philosophy summary — the "always on" rules.

**Key sections in this project:**
- Architecture: LangGraph stateful pipeline, RAG (retrieve → research → write → review), Chroma vector store
- Testing: TDD Red-Green-Refactor with pytest, AAA pattern, naming (`test_should_x_when_y`)
- Python conventions (snake_case, Pydantic, type hints, explicit imports, no docstrings, `ruff` formatting)
- Git: trunk-based, Conventional Commits, squash merge

---

## 7. Replication Checklist for a New Project

To reproduce this full setup in any VS Code workspace:

### Minimum setup (agents only)

```
.vscode/
└── settings.json              ← { "github.copilot.chat.cli.customAgents.enabled": true }
.github/
├── copilot-instructions.md    ← global rules
└── agents/
    └── *.agent.md             ← one file per agent
```

### Full setup

```
.vscode/
└── settings.json
.github/
├── copilot-instructions.md
├── agents/
│   └── *.agent.md
└── prompts/
    └── *.prompt.md
.claude/
└── skills/
    └── {stack}-{topic}/
        └── SKILL.md
src/                           ← .instructions.md next to source modules
└── .instructions.md
data/docs/
└── .instructions.md
```

### Agent file template

```markdown
---
name: my-agent
description: >
  What this agent does and when to use it.
tools: [read, search, edit, execute]
---

# My Agent

You are a ...
```

### Prompt file template

```markdown
---
description: Short description shown in the prompt picker
mode: agent
---

# Prompt Title

## Instructions

1. Step one
2. Step two
```

### Skill file template

```markdown
---
name: my-skill
description: >
  Brief description of what this Skill does and when to invoke it.
---

# My Skill

## Instructions

Step-by-step guidance.

## Examples

Concrete examples.
```

---

## 8. How the AI Decides What to Use

| Mechanism | Triggered by |
|-----------|-------------|
| **Agents** | User explicitly selects the agent in the chat UI (`@demo.tdd-coach`) |
| **Sub-agents** | Parent agent delegates via `runSubagent` tool (invisible to user) |
| **Prompts** | User selects a prompt from the slash command picker |
| **Skills** | Model autonomously decides based on the task and skill descriptions |
| **`.instructions.md`** | Automatically injected when the active file matches `applyTo` glob |
| **`copilot-instructions.md`** | Always injected into every conversation in the workspace |
