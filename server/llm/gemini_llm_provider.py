from typing import Optional

from google import genai
from google.genai import types

from .llm_provider import LLMProvider


class GeminiLLMProvider(LLMProvider):
    """
    LLM provider implementation using Google's Gemini API via google-genai library.
    """

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def prompt(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Send a prompt to the Gemini API and return the response.

        Args:
            prompt: The user prompt to send to the LLM
            system_message: Optional system message to set context
            **kwargs: Additional provider-specific parameters

        Returns:
            The LLM's response as a string
        """
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_message,
                # thinking_config=types.ThinkingConfig(thinking_budget=0),  # Disables thinking if necessary ($$$)
            ),
        )
        return response.text or ""

    def get_provider_name(self) -> str:
        """
        Get the name of the LLM provider.

        Returns:
            The provider name as a string
        """
        return "Gemini"
