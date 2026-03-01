import streamlit as st
import re
from pathlib import Path

from src.rag import ingest_if_empty
from src.graph import build_graph


st.set_page_config(page_title="Biorce Mini Demo", layout="wide")
st.title("Mini Clinical Trial Assistant (Agentic + RAG + Review)")

# Asegura que hay índice
ingest_if_empty()


@st.cache_resource
def get_app():
    return build_graph()


def extract_doc_ids(text: str):
    return sorted(set(re.findall(r"\[DOC:([A-Za-z0-9_\-]+)\]", text or "")))


# -------- UI Inputs --------
condition = st.text_input("Condition", "severe asthma")
intervention = st.text_input("Intervention", "anti-IL5 biologic")
population = st.text_input("Population", "adults")
k = st.slider("Top-K chunks (retrieval)", 3, 8, 5)

# -------- Show graph (nodes + edges) --------
st.subheader("Workflow graph (nodes + edges)")
dot = """
digraph G {
  rankdir=LR;
  retrieve -> research -> write -> review;
  review -> revise [label="if unsupported && iter<1"];
  revise -> write [label="loop once"];
  review -> end [label="else"];
}
"""
st.graphviz_chart(dot)

# -------- Run workflow --------
if st.button("Run Agentic Workflow"):
    app = get_app()

    init_state = {
        "condition": condition,
        "intervention": intervention,
        "population": population,
        "k": k,
        "query": "",
        "sources": [],
        "evidence": {},
        "draft": "",
        "review": {},
        "iteration": 0,
        "trace": [],
    }

    status = st.status("Running workflow...", expanded=True)

    final_state = None
    # Stream states as the graph progresses (so we can show step-by-step)
    for step_state in app.stream(init_state, stream_mode="values"):
        final_state = step_state
        trace = step_state.get("trace", [])
        if trace:
            last = trace[-1]
            status.write(f"✅ **{last['node']}** — {last.get('summary','')}")
        else:
            status.write("...")

    status.update(label="Workflow completed", state="complete", expanded=False)

    # -------- Expected outputs --------
    if not final_state:
        st.error("No output state received from the graph.")
        st.stop()

    # --- Retrieved chunks summary ---
    sources = final_state.get("sources", [])
    if sources:
        best = min(sources, key=lambda x: x["distance"])
        st.info(
            f"Best match = {best['chunk_id']} | chunk_index={best['chunk_index']} | "
            f"Source Document: {best.get('doc_title','')} (doc_id={best['doc_id']}) | distance={best['distance']:.3f}"
        )

    st.subheader("Execution trace (order of nodes)")
    st.dataframe(final_state.get("trace", []))

    # Layout
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Draft (final)")
        st.info(final_state.get("draft", ""))

        st.subheader("Evidence (Researcher output)")
        st.json(final_state.get("evidence", {}))

        st.subheader("Review (Reviewer output)")
        st.json(final_state.get("review", {}))

        st.subheader("Source documents cited in the draft")
        doc_ids = extract_doc_ids(final_state.get("draft", ""))
        if not doc_ids:
            st.warning("No [DOC:...] citations found in the draft.")
        else:
            for doc_id in doc_ids:
                p = Path("data/docs") / f"{doc_id}.txt"
                st.markdown(f"**DOC:{doc_id}** — file: `{p.name}`")
                if p.exists():
                    st.code(p.read_text(encoding="utf-8")[:2000])
                else:
                    st.write("⚠️ File not found for this doc_id (check naming).")

    with col2:
        st.subheader("Retrieved chunks (what the vector DB returns)")
        if not sources:
            st.warning("No chunks retrieved.")
        else:
            st.dataframe(
                [
                    {
                        "chunk_id": s["chunk_id"],
                        "chunk_index": s["chunk_index"],
                        "distance": round(s["distance"], 4),
                        "doc_id": s["doc_id"],
                        "source_document": s.get("doc_title", ""),
                    }
                    for s in sources
                ]
            )

            for s in sources:
                st.markdown(
                    f"**{s['chunk_id']}** | chunk_index={s['chunk_index']} | "
                    f"distance={s['distance']:.3f} | DOC:{s['doc_id']} | {s.get('doc_title','')}"
                )
                st.code((s.get("text") or "")[:800])
