# Custom Agents — Beginner's Guide

A plain-language explanation of all the custom AI agents in this project: what they
are, how to use them, how they work internally, and what to expect from them.

---

## What Are These Custom Agents?

Think of them as **specialized AI coworkers**, each with a specific job title and a
set of rules they always follow. Instead of chatting with a generic AI that tries to
do everything, you pick the right coworker for the task.

---

## The Big Picture — Two Types

There are only **two kinds** of agents:

```
┌──────────────────────────┬─────────────────────────────────┐
│  User-facing (YOU pick)  │  Internal workers (hidden)      │
├──────────────────────────┼─────────────────────────────────┤
│  demo.tdd-coach          │  demo.tdd-red    (write test)   │
│  demo.code-reviewer      │  demo.tdd-green  (make it pass) │
│  demo.pr-feedback        │  demo.tdd-refactor (clean up)   │
│  demo.refactor           │  demo.tdd-implement (quick TDD) │
└──────────────────────────┴─────────────────────────────────┘
```

You only ever talk to the left column. The right column is invoked **automatically**
behind the scenes when a boss agent decides it needs their help — you never call them
directly.

---

## How to Actually Use Them

In the Copilot Chat panel, you'll see an **agent picker** (a dropdown or `@` menu).
Select the agent, then type your request normally:

```
@demo.tdd-coach      implement the summarize node
@demo.code-reviewer  review staged changes
@demo.refactor       this file has too much going on
@demo.pr-feedback    process PR comments
```

That's it. The agent takes over from there.

---

## What Each Agent Actually Does

### `demo.tdd-coach` — The Strict TDD Teacher

The most complex agent. When you ask it to implement something, it **refuses to write
code directly**. Instead it:

1. **Asks you questions** if the requirement is unclear
2. **Makes a plan** — breaks the feature into a list of small behaviors, one test per
   behavior, with a table showing which kind of test each one needs (unit, integration, E2E)
3. **Calls the Red worker** → writes a failing test, runs it, confirms it fails
4. **Calls the Green worker** → writes the minimum code to make that test pass
5. **Calls the Refactor worker** → cleans up the code without changing behavior
6. **Repeats** for each behavior in the plan

> The key thing: it will push back if you try to skip the TDD steps.
> It is intentionally stubborn about that.

---

### `demo.code-reviewer` — The Code Reviewer

When you run it against your changes it:

1. **Detects what to review** (staged files, unstaged files, PR, or branch diff)
   — if it's obvious it picks automatically; if ambiguous it asks you
2. **Launches 4 mini-agents in parallel**, each looking at the code from a different angle:

   | Mini-agent Focus | What It Checks |
   |---|---|
   | Correctness & Logic | Does the code do what it claims? Edge cases? Test coverage? |
   | Architecture & SOLID | LangGraph node responsibilities, RAG pipeline separation, SRP, DRY/YAGNI |
   | Security & Performance | Injection, secrets, SSRF, prompt injection, hardcoded API keys |
   | Convention Compliance | snake_case, type hints, Pydantic models, explicit imports, `ruff` formatting |

3. **Merges their findings** into a single report sorted by severity (Critical → Nit)
4. **Offers to fix** each Critical, High, and Medium finding — one by one, always asking
   your confirmation before touching a file, always via TDD

**Important design choice:** it has strict anti-inflation rules. Most healthy PRs should
have zero Critical or High findings — it will not cry wolf.

| Severity | Meaning |
|---|---|
| **Critical** | Will cause data loss, security breach, or outage — provable, not hypothetical |
| **High** | Wrong behavior that manifests in normal usage — concrete buggy path exists |
| **Medium** | Maintainability issue — works today but makes future changes error-prone |
| **Low** | Minor quality improvement — code is correct but could be slightly cleaner |
| **Nit** | Stylistic preference — no functional or maintainability impact |

---

### `demo.pr-feedback` — The PR Comment Processor

When a pull request has review comments from teammates:

1. **Reads all comments** from the active PR via the `gh` CLI
2. **Shows you each comment**, one at a time
3. **Asks you: apply or discard?**
4. If apply → delegates to `demo.tdd-implement` to fix it with TDD
5. If discard → replies to the comment on GitHub with a reason and dismisses it
6. **Asks for confirmation before committing** anything

It is your assistant for clearing a PR review backlog without losing track of what
you have already handled.

---

### `demo.refactor` — The Code Quality Agent

Point it at a file or piece of code. It:

1. **Reads the file** and all related files (tests, interfaces, callers)
2. **Looks for code smells** in priority order:

   | Priority | Smell |
   |---|---|
   | High | God Class, Long Method, Feature Envy, Shotgun Surgery |
   | Medium | Duplicate Code, Primitive Obsession, Data Clump, Middle Man |
   | Low | Dead Code, Speculative Generality, Comments explaining what |

3. **Presents findings** with severity and concrete fix suggestions
4. **Applies changes** only after you approve each one — runs tests after every
   change to ensure nothing broke

---

## Are They Running in the Background?

**No.** These agents are 100% interactive — they only run when you explicitly invoke
them and they stop to ask you questions throughout. They never do anything autonomously.

Specifically:
- They **always ask before writing files** if there is any ambiguity
- They **always ask before committing**
- `demo.pr-feedback` asks "apply or discard?" for each comment
- `demo.code-reviewer` asks "want me to fix this finding?" before each fix
- `demo.tdd-coach` asks for your approval of the plan before writing a single line

The internal workers (`tdd-red`, `tdd-green`, etc.) run **silently relative to you** —
meaning the coach tells you what they are doing ("Delegating to Red phase...") but you
do not interact with them directly. Each one runs in its own isolated context so they
do not interfere with each other.

---

## The Agent Delegation Chain

```
YOU
 │
 ▼
demo.tdd-coach ──────────── you see this conversation
     │
     ├─► demo.tdd-red       ← runs silently, returns result to coach
     ├─► demo.tdd-green      ← runs silently, returns result to coach
     └─► demo.tdd-refactor   ← runs silently, returns result to coach

demo.code-reviewer ──────── you see this conversation
     │
     ├─► [4 parallel review subagents]  ← run silently
     └─► demo.tdd-implement  ← runs silently when fixing a finding

demo.pr-feedback ─────────── you see this conversation
     ├─► demo.code-reviewer  ← if it needs impact analysis
     └─► demo.tdd-implement  ← for each fix applied
```

---

## Quick Reference

| Question | Answer |
|---|---|
| Do they run automatically? | No — you always invoke them explicitly |
| Can they commit/push without asking? | No — always ask for confirmation first |
| Can I call `tdd-red` directly? | No — marked `user-invocable: false`, won't appear in the picker |
| Do sub-agents share context with each other? | No — each gets a fresh isolated context |
| What tools can they use? | `read` (files), `search` (codebase), `edit` (write files), `execute` (terminal) |
| Where do they find the codebase rules? | They load the relevant Skills from `.claude/skills/` automatically |
| What if I disagree with a finding or suggestion? | Just say no — everything requires your confirmation before being applied |

---

## A Real Day-to-Day Workflow Example

```
1.  You want to add a new node to the LangGraph pipeline
2.  Open Copilot Chat → pick @demo.tdd-coach
3.  Type: "implement the summarize node in graph.py"
4.  Coach makes a plan, shows a table of behaviors → you approve
5.  Coach delegates Red → a failing pytest test appears in your editor
6.  Coach delegates Green → production code appears, test goes green
7.  Coach delegates Refactor → code gets cleaned up
8.  Repeat for each behavior in the plan

9.  When done → pick @demo.code-reviewer → "review branch changes"
10. Reviewer runs 4 parallel perspectives → finds 2 medium issues
11. For each finding: asks "fix it?" → you say yes → TDD cycle applies the fix

12. You push → PR is created → teammates leave review comments
13. Pick @demo.pr-feedback → it processes each comment one by one
14. For each: apply via TDD or reply with a reason and dismiss
```

Each agent hands off naturally to the next in the workflow — you just steer.

---

## Where the Files Live

```
.github/
└── agents/
    ├── demo.code-reviewer.agent.md    ← user-facing
    ├── demo.pr-feedback.agent.md      ← user-facing
    ├── demo.refactor.agent.md         ← user-facing
    ├── demo.tdd-coach.agent.md        ← user-facing (coordinator)
    ├── demo.tdd-red.agent.md          ← internal worker
    ├── demo.tdd-green.agent.md        ← internal worker
    ├── demo.tdd-refactor.agent.md     ← internal worker
    └── demo.tdd-implement.agent.md    ← internal worker
```

The discovery path `.github/agents/*.agent.md` is **hardcoded** in the Copilot Chat
extension. It cannot be changed via settings — the files must be in that exact location.
