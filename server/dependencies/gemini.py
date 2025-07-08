import os
from functools import lru_cache

from ..llm.gemini_llm_provider import GeminiLLMProvider


@lru_cache()
def get_gemini_provider() -> GeminiLLMProvider:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is required")

    return GeminiLLMProvider(api_key=api_key)
