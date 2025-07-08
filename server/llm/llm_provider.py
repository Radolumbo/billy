from abc import ABC, abstractmethod
from typing import Optional


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    """

    @abstractmethod
    def prompt(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Send a prompt to the LLM and return the response.

        Args:
            prompt: The user prompt to send to the LLM
            system_prompt: Optional system message to set context
            **kwargs: Additional provider-specific parameters

        Returns:
            The LLM's response as a string

        Raises:
            Exception: If the API call fails or returns an error
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Get the name of the LLM provider.

        Returns:
            The provider name as a string
        """
        pass
