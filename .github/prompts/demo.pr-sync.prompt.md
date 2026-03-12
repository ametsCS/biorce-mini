---
description: Create or update a pull request with auto-generated title and description
mode: agent
---

# PR Sync

Create a new PR or update an existing one. Auto-generates the title and description from the branch diff against `main`.

## Shell Compatibility

All `git` and `gh` commands work identically across shells.
Use `--body-file` with a temporary file for the PR body (see **Body File Strategy** below).
Always wrap `gh` flag values in **single quotes** to avoid shell parsing issues.

## Instructions

1. **Ensure the branch is pushed**:

   ```bash
   git push -u origin $(git branch --show-current)
   ```

2. **Check if a PR already exists** for the current branch:

   ```bash
   gh pr view --json number,title,body,url 2>&1
   ```

   - If a PR exists, proceed to **step 5** (update).
   - If no PR exists, proceed to **step 3** (create).

3. **Analyze the branch diff** against `main`:

   ```bash
   git log main..HEAD --oneline
   git diff main..HEAD --stat
   ```

4. **Create the PR**:
   - Generate the **title** following conventional commits: `type(scope): subject` (max 72 chars, imperative mood, no period).
   - Generate the **body** by filling in the PR template at `.github/pull_request_template.md`:
     - **Description**: 2-3 sentences summarizing what and why.
     - **Type of Change**: check the matching type (`[x]`).
     - **Changes Made**: bullet list of concrete changes from the diff.
     - **How to Test**: infer verification steps.
     - **Checklist**: check items that are verifiable from the diff (tests added, etc.).
   - **Choose labels** from the repo's available labels:

     ```bash
     gh label list --limit 100
     ```

     Only pick labels that **clearly and directly match** the changes (e.g., `enhancement` for `feat`, `bug` for `fix`,
     `documentation` for `docs`, `dotnet` for C# changes, `python` for Python changes).
     **If no label is a good fit, do not add any labels.** Never force a label that doesn't accurately describe the changes.

   - Present the title, body, and labels (if any) to the user for confirmation.
   - After confirmation, **push the branch** first:

     ```bash
     git push
     ```

   - Write the body to a **temporary file** and create the PR in separate steps:

     ```bash
     # Step 1: Write body to temp file (use create_file tool)
     # File: .pr-body.md (at repo root, already in .gitignore)

     # Step 2: Create the PR with title, body file, and assignee
     gh pr create --title '<title>' --body-file '.pr-body.md' --assignee '@me'

     # Step 3: Add labels (only if there are matching labels)
     gh pr edit <number> --add-label '<label1>,<label2>'

     # Step 4: Mark as ready for review
     gh pr ready <number>

     # Step 5: Delete the temp file (ALWAYS — even if previous steps fail)
     # PowerShell: Remove-Item '.pr-body.md'
     # Bash: rm -f .pr-body.md
     ```

   - Done. Show the PR URL.

5. **Update an existing PR**:
   - Read the current PR title and body from step 2.
   - Re-analyze the diff:

     ```bash
     git log main..HEAD --oneline
     git diff main..HEAD --stat
     ```

   - Regenerate the **title** and **body** based on the current diff (same rules as step 4).
   - Re-evaluate **labels** — only add labels that clearly match. Remove this step if none fit.
   - Present the updated title, body, and labels (if any) to the user, highlighting what changed.
   - After confirmation, **push the branch** first:

     ```bash
     git push
     ```

   - Write the body to a **temporary file** and update in separate steps:

     ```bash
     # Step 1: Write body to temp file (use create_file tool)
     # File: .pr-body.md (at repo root, already in .gitignore)

     # Step 2: Update title and body
     gh pr edit <number> --title '<title>' --body-file '.pr-body.md'

     # Step 3: Add assignee
     gh pr edit <number> --add-assignee '@me'

     # Step 4: Add labels (only if there are matching labels)
     gh pr edit <number> --add-label '<label1>,<label2>'

     # Step 5: Delete the temp file (ALWAYS — even if previous steps fail)
     # PowerShell: Remove-Item '.pr-body.md'
     # Bash: rm -f .pr-body.md
     ```

   - Done. Show the PR URL.

## Rules

- Always ask for confirmation before creating or updating.
- After confirmation, **push changes and create/update the PR automatically** — do not ask again.
- Never force-push or modify commits — this prompt only touches PR metadata.
- Title must follow conventional commits format.
- Body must follow the `.github/pull_request_template.md` structure.
- Write the PR body to a **temporary file** (`.pr-body.md` at repo root) and pass it with `--body-file '.pr-body.md'`.
- **ALWAYS delete `.pr-body.md` after the PR is created/updated**,
  even if a previous step fails.
  This prevents the temp file from being accidentally committed.
- Always wrap `gh` flag values in **single quotes** to avoid shell parsing issues (e.g., `--add-label 'my-label'`).
- Execute `gh` commands in **separate steps** (create/edit, then label, then reviewer,
then ready). Do not combine all flags in a single command.
- Always assign the PR to `@me`.
- Do NOT attempt to add Copilot as a reviewer via `gh` CLI — it is not supported.
  Copilot code review is configured at the repository level and triggers automatically.
- Only add labels that **clearly match** the changes. If no label fits, skip labels entirely.
- Always mark PRs as ready for review.
- If `gh` CLI is not authenticated, stop and tell the user to run `gh auth login`.
- If the branch has no commits ahead of `main`, stop and inform the user.

