---
description: Stage changes and create a conventional commit with a well-crafted message
mode: agent
---

# Smart Commit

Analyze staged/unstaged changes and create a commit following **Conventional Commits** and project conventions.

## Instructions

1. **Check the current state** of the working directory:

   ```bash
   git status
   ```

2. **If nothing is staged**, show the unstaged changes and ask the user what to stage. Options:
   - Stage everything: `git add -A`
   - Stage specific files: `git add <files>`
   - The user may have already staged changes — respect that.

3. **Analyze the diff** of staged changes:

   ```bash
   git diff --cached --stat
   git diff --cached
   ```

4. **Determine the commit type** from the changes:
   - `feat` — new feature for the user
   - `fix` — bug fix for the user
   - `docs` — documentation only
   - `style` — formatting, no logic changes
   - `refactor` — code restructuring, no behavior change
   - `test` — adding or updating tests
   - `chore` — build process, deps, tooling
   - If multiple types apply, prefer the **dominant** one.

5. **Determine the scope** from the changed files:
   - Use the feature/module/area name (e.g., `claims`, `auth`, `ci`, `lambda`, `db`)
   - If changes span many areas, scope is optional.

6. **Craft the commit message** following these rules:
   - **Subject line**: `<type>(<scope>): <subject>`
     - Max 50 characters
     - Imperative mood ("add" not "added")
     - Capitalize first word after colon
     - No period at end
   - **Body** (if the change is non-trivial):
     - Blank line after subject
     - Wrap at 72 characters
     - Explain **what** and **why**, not how

7. **Present the proposed commit** to the user:

   ```bash
   type(scope): subject line here

   Optional body explaining what changed and why.
   ```

   Ask for confirmation before committing.

8. **Create the commit**:

   ```bash
   git commit -m "type(scope): subject" -m "body"
   ```

9. **Do NOT push** automatically. Remind the user if they want to push.

## Rules

- Never amend or force-push without explicit user request.
- Never commit untracked files without asking.
- If there are merge conflicts, stop and inform the user.
- If the diff is empty (nothing staged), do not commit.

