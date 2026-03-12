# Description

> 💡 **TIP:** Use the **pr-sync** prompt to auto-fill this template:
>
> | IDE | How to run |
> | --- | --------- |
> | **VS Code (Copilot)** | Chat → `/demo.pr-sync` |
> | **Claude Code** | `/demo.pr-sync` |
> | **Cursor** | Chat → `@file .github/prompts/demo.pr-sync.prompt.md` |

Brief description of what this PR does and why.

## Type of Change

- [ ] `feat` — New feature
- [ ] `fix` — Bug fix
- [ ] `refactor` — Code restructuring (no behavior change)
- [ ] `test` — Adding or updating tests
- [ ] `docs` — Documentation update
- [ ] `chore` — Build process, deps, tooling
- [ ] `BREAKING CHANGE` — Introduces breaking changes

## Scope

- [ ] LangGraph pipeline (`src/graph.py`)
- [ ] RAG layer (`src/rag.py`)
- [ ] LLM client (`src/llm.py`)
- [ ] Streamlit UI (`streamlit_app.py`)
- [ ] Ingestion (`ingest.py`)
- [ ] Tests
- [ ] CI/CD

## Changes Made

- Changed X to do Y
- Added Z component
- Removed W because ...

## Related Issues

Closes #<!-- issue number -->

## How to Test

1. Step to reproduce or verify
2. Expected result

## Checklist

- [ ] Code follows project conventions
- [ ] Tests added/updated
- [ ] Formatting verified (`uv run ruff format`)
- [ ] Tests pass locally (`uv run pytest`)
- [ ] No breaking changes (or documented above)
