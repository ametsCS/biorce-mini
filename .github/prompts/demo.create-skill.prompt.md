---
description: "Create a new Claude/Copilot skill in .claude/skills/ following the established structure and conventions."
mode: agent
---

# Create Skill

Generate a new Agent Skill following the conventions documented in `.claude/skills/README.md`.

## Instructions

1. **Gather inputs** — ask the user if not provided:
   - **Skill name** (e.g., `dotnet-caching`, `python-deployment`)
   - **Description** — one sentence explaining when the skill should be invoked
   - **Stack prefix** — infer from the name (see Naming Convention below)

2. **Validate the name** against existing skills in `.claude/skills/` to avoid duplicates.

3. **Create the skill directory and SKILL.md** following the structure below.

4. **Update `.claude/skills/README.md`** — add the new skill entry under the correct section.

5. **Optionally create supporting files** if the user provides content:
   - `examples.md` — real code examples from the codebase
   - `reference.md` — quick-reference tables and cheat sheets
   - `templates/` — code templates for scaffolding

## Naming Convention

| Prefix | Scope |
| ------ | ----- |
| `common-` | Cross-stack (all stacks) |
| `dotnet-` | .NET backend |
| `python-` | Python |
| `typescript-react-` | Next.js / React frontend |
| `typescript-cdk-` | AWS CDK infrastructure |

The directory name **must match** the `name` field in SKILL.md frontmatter.

## SKILL.md Structure

```markdown
---
name: {skill-name}
description: {description}
---

# {Title}

{Brief intro — what this skill covers and why it exists.}

## When to Use

- {Trigger condition 1}
- {Trigger condition 2}
- {Trigger condition 3}

## {Section 1 — Core Rules}

{Rules, patterns, or conventions. Use tables for concise reference.}

## {Section 2 — Examples}

{Code examples showing correct usage. Use fenced code blocks with language tags.}

## {Section N — Anti-Patterns (if applicable)}

{Common mistakes to avoid.}
```

## SKILL.md Rules

- **YAML frontmatter is mandatory** — `name` and `description` are required fields
- `name`: lowercase letters, numbers, hyphens only (max 64 chars)
- `description`: max 1024 chars, must explain **what** and **when**
- **No XML docs or inline comments** in code examples — only `// Arrange`, `// Act`, `// Assert`
- Code examples must follow the project's coding standards (see AGENTS.md)
- Include real codebase paths where possible
- Prefer tables over prose for reference material
- Keep sections focused — one concern per section

## README.md Update

Add the skill under the correct section header in `.claude/skills/README.md`:

```markdown
#### [{skill-name}](./{skill-name}/)

{Description sentence.}

**Use when:**

- {Trigger 1}
- {Trigger 2}

**Supporting files:** (only if created)

- `examples.md` - {brief description}
- `reference.md` - {brief description}
```

## Post-Creation Checklist

- [ ] Directory created: `.claude/skills/{skill-name}/`
- [ ] `SKILL.md` has valid YAML frontmatter with `name` and `description`
- [ ] `name` field matches directory name
- [ ] README.md updated with new entry
- [ ] No duplicate skill names
- [ ] Description explains both **what** and **when to use**

