import streamlit as st
from src.llm import generate_text
from src.rag import ingest_if_empty, retrieve

st.set_page_config(page_title="Biorce Mini Demo", layout="wide")
st.title("Mini Clinical Trial Assistant (RAG MVP)")

# Asegura que hay índice
ingest_if_empty()

condition = st.text_input("Condition", "severe asthma")
intervention = st.text_input("Intervention", "anti-IL5 biologic")
population = st.text_input("Population", "adults")

k = st.slider("Top-K sources", 3, 8, 5)

if st.button("Generate draft (with RAG)"):
    query = f"{condition} {intervention} {population}"
    chunks = retrieve(query, k=k)

    sources_block = "\n\n".join([f"{c.sid} ({c.source}):\n{c.text}" for c in chunks])

    prompt = f"""
You are drafting a clinical trial protocol.
Write:
1) Background (6-10 lines)
2) Objective (2-3 lines)
3) Methodology (8-12 lines, high-level)

TOPIC:
- Condition: {condition}
- Intervention: {intervention}
- Population: {population}

SOURCES (use ONLY these):
{sources_block}

STRICT RULES:
- Every factual sentence MUST include at least one citation like [S1] or [S2].
- If a sentence cannot be supported by SOURCES, REMOVE it.
- Do not invent numbers or claims not in SOURCES.
- Output only the draft text.
"""

    out = generate_text(prompt, temperature=0.2)
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Draft")
        st.write(out)

    with col2:
        st.subheader("Retrieved sources")
        for c in chunks:
            st.markdown(f"**{c.sid}** — {c.source} (distance={c.distance:.3f})")
            st.code(c.text[:800])
