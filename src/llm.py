# src/llm.py
import os
from dotenv import load_dotenv
from google import genai

MODEL = "gemini-3-flash-preview"


def get_client() -> genai.Client:
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY in .env")
    return genai.Client(api_key=api_key)


def generate_text(
    prompt: str, temperature: float = 0.0, max_output_tokens: int = 1200
) -> str:
    client = get_client()
    resp = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config={
            "temperature": temperature,
            "max_output_tokens": max_output_tokens,
        },
    )
    return (resp.text or "").strip()
