"""Abstract base class for LLM providers."""

from abc import ABC, abstractmethod
from evalforge.models import PromptRun, ProviderResponse

class Provider(ABC):
    """All providers conform to this interface."""

    name: str # e.g. "openai", "anthropic"
    
    @abstractmethod
    def complete(
        self, 
        user_prompt: str,
        system_prompt: str | None = None,
        model: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 1.0,
        ) -> ProviderResponse:
        """Synchronous completion. Returs normalized ProviderResponse."""
        ...