# 0001 - Use uv as Python Package Manager

**Date:** 2025-10-15

**Status:** Accepted

## Context

Python projects need a package manager to handle dependencies, virtual environments, and project builds.
Traditional options include pip, pip-tools, Poetry, and PDM.
We needed a fast, modern solution that handles both dependency resolution and virtual environment management automatically.

## Decision

We will use **uv** as our Python package manager for all Python projects in this repository.

## Rationale

**Why uv:**

- **Speed:** 10-100x faster than pip and pip-tools (written in Rust)
- **Automatic venv management:** No need to manually create/activate virtual environments
- **Simple workflow:** `uv sync` installs everything, `uv run` executes in the venv automatically
- **pip-compatible:** Works with existing `pyproject.toml` and requirements files
- **Modern standards:** Supports PEP 621 (project metadata) and PEP 631 (dependency groups)
- **All-in-one tool:** Replaces pip, pip-tools, virtualenv, and pipx

**Compared to alternatives:**

- **vs pip:** Much faster, handles venvs automatically, better dependency resolution
- **vs Poetry:** Faster, simpler, less opinionated, no separate lock file format
- **vs PDM:** Similar features but uv is faster and more widely adopted

## Consequences

**Positive:**

- Developers get faster dependency installation (especially on CI/CD)
- No need to remember `source venv/bin/activate` - just use `uv run`
- Consistent environment management across the team
- Modern Python packaging standards from the start

**Negative:**

- Developers need to install uv (simple: `pip install uv`)
- Relatively new tool (though backed by Astral, creators of Ruff)
- Team needs to learn `uv` commands (but they're intuitive)

## Implementation

Install uv:

```powershell
# Windows
pip install uv
```

Basic workflow:

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Run any Python command
uv run python app.py
```

## References

- [uv Documentation](https://github.com/astral-sh/uv)
- [Why uv is Fast](https://astral.sh/blog/uv)
- [PEP 621 - Project Metadata](https://peps.python.org/pep-0621/)
