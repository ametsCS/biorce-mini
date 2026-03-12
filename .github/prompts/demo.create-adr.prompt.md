---
description: Create an Architecture Decision Record (ADR) with auto-numbering
mode: agent
---

# Create ADR

Generate a new Architecture Decision Record following the Nygard format with automatic numbering.

## Shell Compatibility

Detect the user's shell from the terminal context and adapt file counting:

- **PowerShell**: `(Get-ChildItem -Path "docs/adr/{subdir}" -Filter "*.md").Count`
- **Bash / Zsh**: `ls docs/adr/{subdir}/*.md 2>/dev/null | wc -l`

All other commands (`git`, `gh`) work identically across shells.

## Instructions

1. **Gather inputs** — ask the user if not provided:
   - **Title**: short descriptive title (e.g., "Use PostgreSQL for persistence")
   - **Subdirectory**: where the ADR belongs. Auto-detect from context:
     - `docs/adr/backend/` — .NET backend decisions
     - `docs/adr/python/` — Python Lambda decisions
     - `docs/adr/` — general/cross-cutting decisions
   - **Context**: why this decision is needed
   - **Decision**: what was decided
   - **Consequences**: what follows from this decision

2. **Auto-number** the ADR:

   ```bash
   # Count existing ADRs in the target directory
   Get-ChildItem -Path "docs/adr/{subdir}" -Filter "*.md" | Measure-Object
   ```

   Next number = count + 1, zero-padded to 4 digits (e.g., `0003`).

3. **Generate the filename**: `{number}-{kebab-case-title}.md`
   - Example: `0003-use-postgresql-for-persistence.md`

4. **Write the ADR** using this template:

   ```markdown
   <!-- markdownlint-disable MD013 -->
   # {number}. {Title}

   {YYYY-MM-DD}

   ## Status

   Accepted

   ## Context

   {Context paragraph explaining the problem or need}

   ## Decision

   {Decision paragraph explaining what was decided and why}

   ## Consequences

   {Consequences paragraph explaining trade-offs and impacts}
   <!-- markdownlint-enable MD013 -->
   ```

5. **Present the ADR** to the user for review before saving.

6. **Save the file** to the correct directory.

## Rules

- Use `markdownlint-disable MD013` / `markdownlint-enable MD013` wrapper (matches existing ADRs).
- Date format: `YYYY-MM-DD`.
- Status is always `Accepted` unless the user specifies otherwise (other options: `Proposed`, `Deprecated`, `Superseded by [ADR-XXXX]`).
- Keep paragraphs concise — 2-5 sentences each.
- Do not add sections beyond Status, Context, Decision, Consequences (matches Nygard format used in this repo).

