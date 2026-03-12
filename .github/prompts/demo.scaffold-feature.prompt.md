---
description: Scaffold a new LangGraph node or src/ utility module for biorce-mini
mode: agent
---

# Scaffold Feature

Generate the file skeleton for a new feature in the **biorce-mini** project (Python / LangGraph / RAG / Streamlit).

## Instructions

1. **Gather inputs**  ask the user if not provided:
   - **Feature type**: `node` (new LangGraph pipeline node) or `module` (new utility in `src/`)
   - **Feature name** (e.g., `summarize`, `validate`, `format_output`)
   - **Brief description** of what it does

2. **Auto-detect type** from context if possible:
   - Mentions of "node", "pipeline step", "graph", or a processing stage  `node`
   - Mentions of "helper", "utility", "client", "service"  `module`

---

## Node Scaffold (`node`)

A node is a function that receives the pipeline state and returns updated state fields.

### Files to Generate

**Implementation** (`src/{feature_name}_node.py`):

```python
from src.graph import PipelineState


def {feature_name}(state: PipelineState) -> dict:
    # Arrange inputs from state
    # Process
    # Return updated state keys
    return {}
```

**Test** (`tests/test_{feature_name}_node.py`):

```python
import pytest
from src.{feature_name}_node import {feature_name}


def test_should_{expected_behavior}_when_{condition}():
    # Arrange
    state = {}

    # Act
    actual = {feature_name}(state)

    # Assert
    assert actual == {}
```

### Wire the node into the graph

In `src/graph.py`, add:

```python
from src.{feature_name}_node import {feature_name}

graph.add_node("{feature_name}", {feature_name})
graph.add_edge("previous_node", "{feature_name}")
graph.add_edge("{feature_name}", "next_node")
```

---

## Module Scaffold (`module`)

A utility module lives in `src/` and is imported by nodes or the graph.

### Files to Generate

**Implementation** (`src/{feature_name}.py`):

```python
class {FeatureName}:
    def __init__(self) -> None:
        pass
```

**Test** (`tests/test_{feature_name}.py`):

```python
import pytest
from src.{feature_name} import {FeatureName}


def test_should_{expected_behavior}_when_{condition}():
    # Arrange
    sut = {FeatureName}()

    # Act
    actual = sut.method()

    # Assert
    assert actual is not None
```

---

## Summary Table

After generating files, show:

| File | Action |
| --- | --- |
| `src/{feature_name}_node.py` / `src/{feature_name}.py` | Created |
| `tests/test_{feature_name}_node.py` / `tests/test_{feature_name}.py` | Created |
| `src/graph.py` | Updated (if node) |

## Post-Generation Steps

```bash
uv run pytest tests/test_{feature_name}*.py   # confirm Red (failing) test
uv run ruff format                             # format
```

## Rules

- Follow naming and structure of existing `src/` modules.
- NO docstrings  use descriptive names.
- NO inline comments unless logic is non-obvious.
- Empty `__init__.py`  never add exports there.
- `async/await` for all I/O operations.
- Pydantic `BaseModel` with `ConfigDict(validate_assignment=True)` for typed models.
- TDD: the test must fail first (Red), then implement (Green), then clean up (Refactor).
