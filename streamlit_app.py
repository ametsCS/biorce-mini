import streamlit as st
from src.llm import generate_text

st.set_page_config(page_title="Biorce Mini Demo", layout="wide")
st.title("Mini Clinical Trial Drafting Demo (MVP)")

condition = st.text_input("Condition", "severe asthma")
intervention = st.text_input("Intervention", "anti-IL5 biologic")
population = st.text_input("Population", "adults")

if st.button("Generate draft"):
    prompt = f"""
You are drafting a clinical trial protocol. Write:
1) Background (6-10 lines)
2) Objective (2-3 lines)
3) Methodology (8-12 lines, high-level)

Topic:
- Condition: {condition}
- Intervention: {intervention}
- Population: {population}

Constraints:
- Keep it generic. Do not claim specific numbers or study results.
- Not medical advice.
"""
    out = generate_text(prompt)
    st.subheader("Draft")
    st.write(out)
