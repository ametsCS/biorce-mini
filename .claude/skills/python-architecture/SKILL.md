---
name: python-architecture
description: Module structure and architecture patterns for this Python RAG/LangGraph project. Use when adding new nodes to the LangGraph pipeline, extending the RAG retrieval layer, modifying the LLM client, or organizing new source modules under src/.
---

# Backend Architecture (Python — biorce-mini)

Architecture and module organization patterns for this project: a RAG-based clinical
trial assistant built with LangGraph, Chroma, SentenceTransformers, and Streamlit.

## When to Use

- Adding a new node to the LangGraph pipeline in `src/graph.py`
- Extending the RAG layer in `src/rag.py` (chunking, embedding, retrieval)
- Modifying the LLM client in `src/llm.py`
- Organizing a new utility module under `src/`
- Designing Pydantic models for state or node inputs/outputs

## Project Structure

```txt
biorce-mini/
├── src/
│   ├── rag.py          # Chunking, embeddings, Chroma indexing + retrieval
│   ├── llm.py          # LLM client wrapper (reads API key from .env)
│   └── graph.py        # LangGraph workflow: nodes, edges, conditional routing
├── data/
│   ├── docs/           # Source .txt documents
│   └── chroma/         # Local vector DB (auto-generated, git-ignored)
├── streamlit_app.py    # Streamlit UI + workflow runner
└── ingest.py           # One-time indexing script
```

## LangGraph Pipeline Architecture

The pipeline is a stateful graph. Each node is a pure function that receives the
current `GraphState` and returns a partial state update.

### Node Pattern

```python
# src/graph.py
from langgraph.graph import StateGraph
from pydantic import BaseModel

class GraphState(BaseModel):
    condition: str
    intervention: str
    population: str
    chunks: list[str] = []
    evidence: dict = {}
    draft: str = ""
    review: dict = {}
    iteration: int = 0

def retrieve(state: GraphState) -> dict:
    """← Only docstring allowed: one-line description of the node's role."""
    chunks = rag.retrieve(state.condition, state.intervention)
    return {"chunks": chunks}
```

**Key rules for nodes:**

- Each node receives `state: GraphState` and returns a `dict` of fields to update
- Node functions are pure: no side effects beyond returning state updates
- One responsibility per node — do not combine retrieval + writing in one function
- Use descriptive function names that match the edge names in the graph

### Conditional Routing Pattern

```python
def should_revise(state: GraphState) -> str:
    if state.review.get("has_unsupported") and state.iteration < 1:
        return "revise"
    return "end"

builder.add_conditional_edges("review", should_revise)
```

## RAG Layer (`src/rag.py`)

Responsible for document chunking, embedding generation, Chroma indexing, and query
retrieval.

**Key rules:**

- Chroma collection is initialized once at module level — do not re-initialize per query
- Embeddings use `SentenceTransformer` — keep model name configurable via a constant
- Retrieval returns a list of `(document_text, distance)` tuples or plain strings
- Chunking logic must be deterministic — same input always produces same chunks

## LLM Client (`src/llm.py`)

Thin wrapper around the Google Gemini SDK. Reads the API key from `.env` via
`python-dotenv`.

**Key rules:**

- The client is instantiated once and passed into nodes that need it
- No business logic in `llm.py` — only prompt construction and API call
- Always pass `temperature` explicitly — do not rely on SDK defaults
- Never log full prompts or responses (may contain PII from documents)

## Pydantic Models

Use Pydantic v2 for `GraphState` and any structured LLM output schemas.

```python
from pydantic import BaseModel, field_validator

class EvidenceItem(BaseModel):
    claim: str
    source: str
    confidence: float

    @field_validator("confidence")
    @classmethod
    def confidence_in_range(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        return v
```

## Import Conventions

- ✅ **Always use explicit imports** — import from specific module files
- ✅ `from src.rag import retrieve` — explicit and traceable
- ❌ `from src import *` — never use wildcard imports
- Keep `__init__.py` files **empty** — no re-exports

## Code Quality Rules

- ✅ Self-documenting code through clear naming
- ❌ **NO docstrings on internal functions** — use descriptive names instead
- ❌ Avoid comments that repeat what the code says
- ✅ One-line docstring on LangGraph nodes is the exception (describes node role)

## Related Skills

- For testing patterns, see [python-testing](../python-testing/)
- For security (API key handling, prompt injection), see [common-security](../common-security/)
- For logging, see [common-observability](../common-observability/)


## Domain Layer

### Entity Pattern

Entities have identity and business logic. Use Pydantic v2 with factory methods.

**Key rules:**

- Use `model_config = ConfigDict(validate_assignment=True)`
- Factory method `create()` for object creation with validation
- Business methods that enforce invariants
- Private setters via Pydantic

### Value Object Pattern

Immutable objects defined by their values.

**Key rules:**

- Use `model_config = ConfigDict(frozen=True)`
- No identity (compared by value)
- Validation in `field_validator`

### Repository Ports (Protocol Interfaces)

**Convention:** Use `I` prefix for Protocol interfaces. One interface per file in `domain/ports/`.

```python
# domain/ports/storage.py
from typing import Any, Protocol

class IStorage(Protocol):
    async def save(self, request_id: str, content: dict[str, Any]) -> str: ...
```

## Application Layer

Organized by use case (screaming architecture). Each use case has:

- `models/request.py` - Input validation with Pydantic
- `models/response.py` - Output structure
- `{use_case}_handler.py` - Orchestrates domain logic

**Handler pattern:**

```python
class VerifyClaimHandler:
    def __init__(self, claim_repository: IClaimRepository, logger: logging.Logger):
        self._claim_repository = claim_repository
        self._logger = logger
    
    async def handler(self, request: VerifyClaimRequest) -> VerifyClaimResponse:
        # 1. Load entity
        # 2. Execute domain logic
        # 3. Persist changes
        # 4. Return response
```

## Infrastructure Layer

Implements domain ports. Organized by type in subfolders.

**Key rules:**

- Support `endpoint_url` parameter for LocalStack testing
- Use async methods matching port signatures
- Handle external service errors with logging

## Presentation Layer

The `app/` folder contains Lambda entry point and DI setup.

**Key rules:**

- Configure DI at module load, not per request
- Use `asyncio.get_event_loop().run_until_complete()` for async handlers
- Structured logging with extra fields

## Key Principles

| Layer | Location | Rules |
| ----- | -------- | ----- |
| Domain | `domain/` | No external dependencies, Pydantic models, Protocol ports |
| Application | `application/` | Use case folders, request/response models, handlers |
| Infrastructure | `infrastructure/` | Implements ports, AWS SDK, endpoint_url support |
| Presentation | `app/` | Lambda handler, DI setup, logging config |

**Import Conventions:**

- ✅ **ALWAYS use explicit imports** - import from specific module files, not from `__init__.py`
- ✅ `from core.domain.models.user import User` - explicit, traceable, refactor-safe
- ❌ `from core.domain.models import User` - avoid re-exports via `__init__.py`
- ❌ `from core.domain import models` - too vague
- ✅ Keep `__init__.py` files **empty** - no `__all__`, no re-exports
- **Rationale:** Explicit imports eliminate indirection, enable better IDE support,
prevent circular imports, and improve maintainability

**Code Quality:**

- ✅ Self-documenting code through clear naming
- ❌ **NO docstrings** — use descriptive method and class names instead (same rule as C#)
- ❌ Avoid comments that repeat code — if a comment is needed, extract a method with a descriptive name

## Related Skills

- For testing patterns, see [python-testing](../python-testing/)
- For test doubles (Mother/Builder), see [python-testing](../python-testing/)

## Additional Resources

- For complete code examples, see [examples.md](examples.md)
- For DI configuration and advanced patterns, see [reference.md](reference.md)
- For code templates, see [templates/](templates/)
