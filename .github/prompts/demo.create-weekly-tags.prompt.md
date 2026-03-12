---
description: Create semantic version tags grouped by work week (Mon-Fri)
mode: agent
---

# Create Weekly Semantic Version Tags

Create annotated git tags grouped by **work week (Monday to Friday)**, using semantic versioning with MINOR increments.

## Shell Compatibility

All `git` and `gh` commands in this prompt are cross-platform. Detect the user's
shell from the terminal context and adapt only where needed:

- **PowerShell**: `(git log --reverse --format="%ad" --date=short | Select-Object -First 1)`
- **Bash / Zsh**: `git log --reverse --format="%ad" --date=short | head -1`

Prefer cross-platform `git` commands over shell-specific file system utilities.

## Instructions

1. **Auto-detect parameters** (no user input needed):

   - **Start date**: get the date of the first commit in the repo:

     ```bash
     git log --reverse --format="%ad" --date=short | head -1
     ```

   - **End date**: today's date.
   - **Starting version**: list existing tags with `git tag -l --sort=version:refname "v*"`, find the highest
   `vMAJOR.MINOR.PATCH` tag, and start from the next MINOR. If no tags exist, start at `v0.1.0`.

2. **Get the full commit log** ordered chronologically:

   ```bash
   git log --oneline --format="%H %ad %s" --date=short --reverse
   ```

3. **Group commits by work week** (Monday through Friday):
   - Each week starts on Monday and ends on Friday.
   - Weekend commits (Saturday/Sunday) belong to the **following** Monday's week.
   - If a week has **zero commits**, skip it — do not create a tag.
   - Skip weeks that already have a tag on their last commit.

4. **For each week with commits**, create an annotated tag on the **last commit** of that week:

   ```bash
   git tag -a v<VERSION> <COMMIT_SHA> -m "v<VERSION> - Week <Mon date>-<Fri date>"
   ```

   - Increment the MINOR version for each subsequent week.
   - Example sequence: `v0.1.0`, `v0.2.0`, `v0.3.0`, ...

5. **Present a summary table** before creating tags, and **ask for confirmation**:

   | Tag     | Week          | Last Commit | Commit Message |
   | ------- | ------------- | ----------- | -------------- |
   | v0.1.0  | Dec 1-5, 2025 | `abc1234`   | feat: ...      |

6. **After creating tags**, verify with:

   ```bash
   git tag -l -n1 --sort=version:refname "v*"
   ```

7. **Do NOT push tags** automatically. Remind the user to push when ready:

   ```bash
   git push origin --tags
   ```

8. **After pushing tags**, ask if the user wants to **create GitHub Releases** for each tag.
   If confirmed, create a release per tag using the GitHub CLI with auto-generated release notes:

   ```bash
   # For all tags except the last one (not latest):
   gh release create v<VERSION> --title "v<VERSION>" --generate-notes --latest=false

   # For the last (most recent) tag, mark it as latest:
   gh release create v<VERSION> --title "v<VERSION>" --generate-notes
   ```

   - Skip tags that already have a release.
   - The `--generate-notes` flag produces the same output as GitHub's "Generate release notes" button.

## Rules

- Tags are **annotated** (`-a`), not lightweight.
- Tag message format: `v<VERSION> - Week <Mon> <day>-<Fri> <day>, <year>`
- Never overwrite existing tags.
- If `startVersion` conflicts with an existing tag, stop and ask the user.

