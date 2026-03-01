# src/graph.py
from __future__ import annotations

from typing import TypedDict, List, Dict, Any
import json
import re

from langgraph.graph import StateGraph, END

from src.rag import retrieve
from src.llm import generate_text


def _safe_json_loads(s: str) -> Dict[str, Any]:
    """Parsea JSON aunque el modelo meta texto alrededor."""
    try:
        return json.loads(s)
    except Exception:
        start = s.find("{")
        end = s.rfind("}")
        if start >= 0 and end > start:
            return json.loads(s[start : end + 1])
        raise


def hard_validate_citations(draft: str, allowed_docs: list[str]) -> list[dict]:
    issues = []
    for line in (draft or "").splitlines():
        line = line.strip()
        if line.startswith("-"):
            cites = re.findall(r"\[DOC:([A-Za-z0-9_\-]+)\]", line)
            if not cites:
                issues.append(
                    {"sentence": line, "reason": "Missing [DOC:...] citation"}
                )
            else:
                for c in cites:
                    if c not in allowed_docs:
                        issues.append(
                            {
                                "sentence": line,
                                "reason": f"Invalid doc_id citation: {c}",
                            }
                        )
    return issues


def _add_trace(
    state: Dict[str, Any], node: str, summary: str, extra: Dict[str, Any] | None = None
):
    trace = list(state.get("trace", []))
    item = {"node": node, "summary": summary}
    if extra:
        item.update(extra)
    trace.append(item)
    return trace


def _extract_doc_ids(text: str) -> List[str]:
    return sorted(set(re.findall(r"\[DOC:([A-Za-z0-9_\-]+)\]", text or "")))


class State(TypedDict):
    # inputs
    condition: str
    intervention: str
    population: str
    k: int

    # workflow
    query: str
    sources: List[Dict[str, Any]]  # chunks retrieved (serializable)
    evidence: Dict[str, Any]  # JSON from Researcher
    draft: str  # Markdown from Writer
    review: Dict[str, Any]  # JSON from Reviewer
    iteration: int  # loop control
    trace: List[Dict[str, Any]]  # timeline for UI


def retrieve_node(state: State) -> State:
    query = f"{state['condition']} {state['intervention']} {state['population']}"
    chunks = retrieve(query, k=state["k"])

    sources = []
    for c in chunks:
        sources.append(
            {
                "chunk_id": c.chunk_id,
                "doc_id": c.doc_id,
                "doc_title": c.doc_title,
                "chunk_index": c.chunk_index,
                "text": c.text,
                "distance": c.distance,
            }
        )

    best = min(sources, key=lambda x: x["distance"]) if sources else None
    summary = f"Retrieved {len(sources)} chunks for query='{query}'."
    extra = (
        {"best_chunk_id": best["chunk_id"], "best_distance": best["distance"]}
        if best
        else {}
    )

    return {
        **state,
        "query": query,
        "sources": sources,
        "trace": _add_trace(state, "retrieve", summary, extra),
    }


def researcher_node(state: State) -> State:
    sources_block = "\n\n".join(
        [
            f"{s['chunk_id']} | DOC:{s['doc_id']} | {s.get('doc_title','')} | chunk_index={s['chunk_index']}\nTEXT:\n{s['text']}"
            for s in state["sources"]
        ]
    )
    allowed_docs = ", ".join(sorted(set([s["doc_id"] for s in state["sources"]])))

    prompt = f"""
You are a clinical research assistant.
You MUST only use the provided SOURCES. Do not add external facts.

Return JSON ONLY with this schema:
{{
  "key_findings": [{{"claim": "...", "sources": ["S1"]}}],
  "risk_notes": [{{"note": "...", "sources": ["S2"]}}],
  "open_questions": ["..."]
}}

IMPORTANT:
- In "sources", use ONLY doc_ids from this allowed list: {allowed_docs}
- "sources" must reference DOCUMENT IDs (doc_id), not chunk_id.

QUESTION: {state["query"]}

SOURCES:
{sources_block}
"""
    out = generate_text(prompt, temperature=0.1)
    evidence = _safe_json_loads(out)

    kf = len(evidence.get("key_findings", []))
    rn = len(evidence.get("risk_notes", []))
    summary = f"Extracted evidence JSON: key_findings={kf}, risk_notes={rn}."

    return {
        **state,
        "evidence": evidence,
        "trace": _add_trace(state, "research", summary),
    }


def writer_node(state: State) -> State:
    sources_block = "\n\n".join(
        [
            f"{s['chunk_id']} | DOC:{s['doc_id']} | {s.get('doc_title','')} | chunk_index={s['chunk_index']}\nTEXT:\n{s['text']}"
            for s in state["sources"]
        ]
    )

    evidence_lines = []
    for item in state.get("evidence", {}).get("key_findings", []):
        srcs = ", ".join(item.get("sources", []))
        evidence_lines.append(f"- {item.get('claim','')} [DOC:{srcs}]")
    evidence_brief = (
        "\n".join(evidence_lines) if evidence_lines else "- No strong findings."
    )

    # Si vienes de una revisión, pasa instrucciones al writer
    review_fix = ""
    if state.get("review", {}).get("fix_instructions"):
        review_fix = "\nREVIEW FIX INSTRUCTIONS:\n" + "\n".join(
            state["review"]["fix_instructions"]
        )

    prompt = f"""
You are drafting a clinical trial protocol draft (VERY concise).

TOPIC:
- Condition: {state["condition"]}
- Intervention: {state["intervention"]}
- Population: {state["population"]}

EVIDENCE (from Researcher):
{evidence_brief}

SOURCES (chunks retrieved from a vector DB):
{sources_block}

STRICT GROUNDING RULES:
- Use ONLY the provided SOURCES.
- Every bullet MUST include at least one citation in this exact format: [DOC:doc_id]
Example: [DOC:S1]
- Cite the DOCUMENT (doc_id), not the chunk_id.
- If a claim cannot be supported by SOURCES, OMIT it.
- Do NOT invent numbers or facts.
{review_fix}

OUTPUT FORMAT (STRICT MARKDOWN — NO DEVIATIONS):
- Use EXACTLY these headings (on their own line):
**Background**
**Objective**
**Methodology**
- Use "*" ONLY for the required bold headings.
- Use "-" for all bullet points.
- No paragraphs. Only bullet points.
- Do NOT put text on the same line as a heading.
- No extra sections.
- No explanations.

STRUCTURE TO FOLLOW EXACTLY:

**Background**
- <bullet, max 18 words> [DOC:SX]
- <bullet, max 18 words> [DOC:SX]

**Objective**
- <bullet, max 18 words> [DOC:SX]

**Methodology**
- <bullet, max 18 words> [DOC:SX]
- <bullet, max 18 words> [DOC:SX]
- <bullet, max 18 words> [DOC:SX]

HARD LIMITS:
- Maximum 120 total words.
- Only output valid Markdown.
"""
    draft = generate_text(prompt, temperature=0.0)

    cited = _extract_doc_ids(draft)
    summary = f"Wrote draft. cited_docs={len(cited)}."
    return {
        **state,
        "draft": draft,
        "trace": _add_trace(state, "write", summary, {"cited_docs": cited}),
    }


def reviewer_node(state: State) -> State:
    sources_block = "\n\n".join(
        [
            f"{s['chunk_id']} | DOC:{s['doc_id']} | {s.get('doc_title','')} | chunk_index={s['chunk_index']}\nTEXT:\n{s['text']}"
            for s in state["sources"]
        ]
    )
    allowed_docs = sorted(set([s["doc_id"] for s in state["sources"]]))
    hard_issues = hard_validate_citations(state["draft"], allowed_docs)
    if hard_issues:
        review = {
            "unsupported_sentences": hard_issues,
            "fix_instructions": [
                "Add a valid [DOC:...] citation to every bullet or remove the bullet."
            ],
            "revised_draft": "",
        }
        return {
            **state,
            "review": review,
            "trace": _add_trace(
                state,
                "review",
                f"Hard-review failed. unsupported={len(hard_issues)}.",
                {"unsupported_count": len(hard_issues)},
            ),
        }

    prompt = f"""
You are a strict reviewer for grounding.

TASK:
- Check the DRAFT against the SOURCES.
- Flag any bullet that lacks [DOC:...] citation.
- Flag any bullet whose claim is not supported by the cited DOC.
- If citations exist but point to a doc_id not in allowed list -> flag.

Allowed doc_ids: {", ".join(allowed_docs)}

Return JSON ONLY with this schema:
{{
  "unsupported_sentences": [{{"sentence": "...", "reason": "..."}}],
  "fix_instructions": ["..."],
  "revised_draft": "..."
}}

SOURCES:
{sources_block}

DRAFT:
{state["draft"]}
"""
    out = generate_text(prompt, temperature=0.1)
    review = _safe_json_loads(out)

    unsupported = review.get("unsupported_sentences", [])
    summary = f"Reviewed draft. unsupported={len(unsupported)}."

    return {
        **state,
        "review": review,
        "trace": _add_trace(
            state, "review", summary, {"unsupported_count": len(unsupported)}
        ),
    }


def route_after_review(state: State) -> str:
    unsupported = state.get("review", {}).get("unsupported_sentences", [])
    if unsupported and state["iteration"] < 1:
        return "revise"
    return "end"


def revise_node(state: State) -> State:
    # 1 loop máximo
    revised = state.get("review", {}).get("revised_draft", "")
    new_state = {**state, "iteration": state["iteration"] + 1}

    if isinstance(revised, str) and len(revised) > 50:
        summary = "Applied reviewer revised_draft and looping once."
        new_state["draft"] = revised
    else:
        summary = "No revised_draft provided; looping once with fix_instructions."

    new_state["trace"] = _add_trace(state, "revise", summary)
    return new_state


def build_graph():
    g = StateGraph(State)

    g.add_node("retrieve", retrieve_node)
    g.add_node("research", researcher_node)
    g.add_node("write", writer_node)
    g.add_node("review", reviewer_node)
    g.add_node("revise", revise_node)

    g.set_entry_point("retrieve")
    g.add_edge("retrieve", "research")
    g.add_edge("research", "write")
    g.add_edge("write", "review")

    g.add_conditional_edges(
        "review", route_after_review, {"revise": "revise", "end": END}
    )

    g.add_edge("revise", "write")  # loop 1 vez
    return g.compile()
