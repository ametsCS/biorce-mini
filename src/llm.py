# src/llm.py
import os
from dotenv import load_dotenv
from google import genai

MODEL = "gemini-2.5-flash-lite"


def get_client() -> genai.Client:
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY in .env")
    return genai.Client(api_key=api_key)


def generate_text(
    prompt: str, temperature: float = 0.0, max_output_tokens: int = 2000
) -> str:
    client = get_client()
    resp = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config={
            "temperature": temperature,
            "max_output_tokens": max_output_tokens,
            "thinking_config": {"thinking_budget": 0},
        },
    )
    if resp.text:
        return resp.text.strip()
    # Fallback for thinking models: extract non-thought text parts manually
    try:
        parts = resp.candidates[0].content.parts
        text = "".join(
            p.text
            for p in parts
            if hasattr(p, "text") and p.text and not getattr(p, "thought", False)
        )
        return text.strip()
    except Exception:
        return ""
