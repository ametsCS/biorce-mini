# Copilot Instructions

This is **biorce-mini** — a Python RAG pipeline and Streamlit demo assistant for clinical
trial document analysis, powered by LangGraph, Chroma, SentenceTransformers, and Gemini.

## Architecture

- **LangGraph pipeline**: `src/graph.py` defines nodes wired into a `StateGraph`
  - Nodes: `retrieve` → `research` → `write` → `review`
  - State is a typed `TypedDict` passed through each node
- **RAG layer**: `src/rag.py` — Chroma vector DB + SentenceTransformer embeddings
- **LLM client**: `src/llm.py` — wraps `google-genai` (Gemini)
- **Ingestion**: `ingest.py` — loads `data/docs/` into `data/chroma/`
- **UI**: `streamlit_app.py` — Streamlit frontend invoking the graph

## Testing

- **TDD**: Red-Green-Refactor — always write a failing test first
- **Naming**: `test_should_{expected_behavior}_when_{condition}`
- **AAA**: Mandatory `# Arrange`, `# Act`, `# Assert` comments
- **Test doubles**: Builder/factory pattern for Arrange — never inline magic values
  - Builders: Polyfactory `ModelFactory` with seeded `FACTORY_SEED=42`
  - Mocks: `unittest.mock` (`MagicMock`, `AsyncMock`, `patch`)
- Use `sut` for subject under test, `expected`/`actual` for assertion values
- Run tests: `uv run pytest`

## Python

- snake_case files/folders/functions, PascalCase classes, `I` prefix for Protocol interfaces
- NO docstrings (`"""`) — use descriptive class, method, and variable names instead
- Pydantic `BaseModel` with `ConfigDict(validate_assignment=True)` for typed models
- `async/await` for all I/O operations
- Explicit imports from defining modules — empty `__init__.py`
- Formatter: `uv run ruff format` — run after every modification
- Type checking: `uv run mypy src/`
- Package manager: `uv` — use `uv sync` to install, `uv run <cmd>` to execute

## Git

- Trunk-based development, short-lived feature branches
- Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
- PRs: squash and merge, title ≤72 chars

## Key References

- Agent guidelines and demo agents: see `.github/agents/`
- Skills with domain-specific patterns: see `.claude/skills/`
- Prompts / slash commands: see `.github/prompts/`
