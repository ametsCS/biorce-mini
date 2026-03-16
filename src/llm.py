# src/llm.py
import os
from dotenv import load_dotenv
from google import genai

from src.observability import get_langfuse, observe

MODEL = "gemini-2.5-flash-lite"


def get_client() -> genai.Client:
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY in .env")
    return genai.Client(api_key=api_key)


@observe(as_type="generation")
def generate_text(
    prompt: str, temperature: float = 0.0, max_output_tokens: int = 2000
) -> str:
    client = get_client()
    get_langfuse().update_current_generation(
        input=prompt,
        model=MODEL,
        model_parameters={
            "temperature": temperature,
            "max_output_tokens": max_output_tokens,
        },
    )
    resp = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config={
            "temperature": temperature,
            "max_output_tokens": max_output_tokens,
            "thinking_config": {"thinking_budget": 0},
        },
    )
    output_text = ""
    if resp.text:
        output_text = resp.text.strip()
    else:
        # Fallback for thinking models: extract non-thought text parts manually
        try:
            parts = resp.candidates[0].content.parts
            output_text = "".join(
                p.text
                for p in parts
                if hasattr(p, "text") and p.text and not getattr(p, "thought", False)
            ).strip()
        except Exception:
            output_text = ""

    usage_meta = getattr(resp, "usage_metadata", None)
    get_langfuse().update_current_generation(
        output=output_text,
        usage_details={
            "input": getattr(usage_meta, "prompt_token_count", 0) or 0,
            "output": getattr(usage_meta, "candidates_token_count", 0) or 0,
        }
        if usage_meta
        else {},
    )
    return output_text
