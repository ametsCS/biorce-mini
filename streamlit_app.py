import streamlit as st
from src.llm import generate_text
from src.rag import ingest_if_empty, retrieve

import re
from pathlib import Path

st.set_page_config(page_title="Biorce Mini Demo", layout="wide")
st.title("Mini Clinical Trial Assistant (RAG MVP)")

# Asegura que hay índice
ingest_if_empty()

condition = st.text_input("Condition", "severe asthma")
intervention = st.text_input("Intervention", "anti-IL5 biologic")
population = st.text_input("Population", "adults")

k = st.slider("Top-K chunks (retrieval)", 3, 8, 5)


def extract_doc_ids(text: str):
    return sorted(set(re.findall(r"\[DOC:([A-Za-z0-9_\-]+)\]", text)))


if st.button("Generate draft (with RAG)"):
    query = f"{condition} {intervention} {population}"
    chunks = retrieve(query, k=k)

    best = min(chunks, key=lambda c: c.distance)
    st.info(
        f"Best match = {best.chunk_id} | chunk_index={best.chunk_index} | "
        f"Source Document: {best.doc_title} (doc_id={best.doc_id}) | distance={best.distance:.3f}"
    )

    # Tabla para que se vea clarísimo chunk vs doc
    st.subheader("Retrieved chunks (what the vector DB actually returns)")
    st.dataframe(
        [
            {
                "chunk_id": c.chunk_id,
                "chunk_index": c.chunk_index,
                "distance": round(c.distance, 4),
                "source_document": c.doc_title,
                "doc_id": c.doc_id,
            }
            for c in chunks
        ]
    )

    sources_block = "\n\n".join(
        [
            f"{c.chunk_id} | doc_id={c.doc_id} | Source Document: {c.doc_title} | chunk_index={c.chunk_index}\nTEXT:\n{c.text}"
            for c in chunks
        ]
    )

    prompt = f"""
        You are drafting a clinical trial protocol draft (VERY concise).

        TOPIC:
        - Condition: {condition}
        - Intervention: {intervention}
        - Population: {population}

        SOURCES (chunks retrieved from a vector DB):
        {sources_block}

        STRICT GROUNDING RULES:
        - Use ONLY the provided SOURCES.
        - Every bullet MUST include at least one citation in this exact format: [DOC:doc_id]
        Example: [DOC:S1]
        - Cite the DOCUMENT (doc_id), not the chunk_id.
        - If a claim cannot be supported by SOURCES, OMIT it.
        - Do NOT invent numbers or facts.

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

    out = generate_text(prompt, temperature=0.0)
    print("LLM Output:\n", out)

    # ---- UI: Draft + Retrieved chunks ----
    col1, col2 = st.columns(2)

    # =========================
    # LEFT COLUMN → DRAFT
    # =========================
    with col1:
        st.subheader("Draft")
        st.info(out)

        # =========================
        # DOCUMENTOS CITADOS
        # =========================
        doc_ids = extract_doc_ids(out)

        st.subheader("Source documents cited in the draft")
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

    # =========================
    # RIGHT COLUMN → CHUNKS
    # =========================
    with col2:
        st.subheader("Retrieved chunks (what the vector DB returns)")

        for c in chunks:
            st.markdown(
                f"**{c.chunk_id}** | chunk_index={c.chunk_index} | "
                f"distance={c.distance:.3f} | Source Document: {c.doc_title}"
            )
            st.code(c.text[:800])
