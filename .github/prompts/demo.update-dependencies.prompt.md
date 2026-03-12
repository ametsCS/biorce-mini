---
description: Analyze Dependabot PRs, review changelogs, and batch-update dependencies
mode: agent
---

# Update Dependencies

Analyze open dependency update PRs (Dependabot or manual), assess risk, and help
batch-update dependencies safely.

## Instructions

1. **List open dependency PRs**:

   ```bash
   gh pr list --label "dependencies" --state open --json number,title,url,labels
   ```

   If no label filter works, search by author:

   ```bash
   gh pr list --author "app/dependabot" --state open --json number,title,url
   ```

2. **Categorize updates** by risk level:

   | Risk | Criteria | Action |
   | --- | --- | --- |
   | **Low** | Patch version bump (x.y.Z) | Auto-merge candidate |
   | **Medium** | Minor version bump (x.Y.0) | Review changelog |
   | **High** | Major version bump (X.0.0) | Review changelog + breaking changes |

3. **For each PR**, gather context:
   - Read the PR description (Dependabot includes changelog links)
   - Check if the package has known vulnerabilities: `gh pr view {number} --json body`
   - Identify which stack is affected (.NET, Python, TypeScript)

4. **Present a summary table**:

   | # | PR | Package | From → To | Risk | Stack | Action |
   | --- | --- | --- | --- | --- | --- | --- |
   | 1 | #45 | Serilog | 4.2.0 → 4.3.0 | Low | .NET | Merge |
   | 2 | #46 | aws-cdk-lib | 2.170.0 → 2.180.0 | Medium | CDK | Review |
   | 3 | #47 | next | 14.x → 15.x | High | Frontend | Review breaking changes |

5. **For each update the user approves**, execute:

   ```bash
   # Merge the Dependabot PR
   gh pr merge {number} --squash --auto

   # Or if manual update is needed (e.g., lock file conflict):
   git fetch origin
   git checkout {branch}
   git merge main
   # Resolve conflicts, then push
   ```

6. **After merging**, verify the build:

   ```bash
   dotnet build
   pnpm build
   pnpm test
   dotnet test
   ```

7. **For major updates** that require code changes:
   - Read the migration guide / changelog
   - Identify breaking changes that affect the codebase
   - Propose code modifications and present them before applying
   - Run full test suite after changes

## Stack-Specific Update Commands

### .NET (Directory.Packages.props)

```bash
# Check outdated packages
dotnet list package --outdated

# Update specific package
# Edit Directory.Packages.props, then:
dotnet restore
dotnet build
dotnet test
```

### TypeScript (pnpm)

```bash
# Check outdated packages
pnpm outdated

# Update specific package
pnpm update {package}@{version}

# Update all within semver ranges
pnpm update

# Full test after update
pnpm build && pnpm test
```

### Python (uv)

```bash
# Check outdated
uv pip list --outdated

# Update in pyproject.toml, then:
uv sync
pytest
```

## Rules

- Never merge a PR without user confirmation
- Always check that CI passes before merging
- For major version bumps, always review the changelog for breaking changes
- Group related updates (e.g., all Serilog packages) into a single merge session
- If a merge causes test failures, revert and report the issue
- Never force-merge PRs with failing checks

