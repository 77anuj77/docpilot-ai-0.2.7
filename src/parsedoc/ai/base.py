"""ParseDoc AI Provider abstraction (PRD #12)"""

import abc
from typing import Optional


class AIProvider(abc.ABC):
    """Abstract interface for AI providers.

    Every provider must implement :meth:`generate`, which takes a prompt and
    content and returns the model's raw text response.
    """

    name: str = "base"
    model: str = ""

    @abc.abstractmethod
    def generate(self, prompt: str, content: str) -> str:
        """Generate a response from the model for the given prompt + content."""
        raise NotImplementedError

    def is_available(self) -> bool:
        """Return True if the provider can be used (dependencies/config present)."""
        return True


def build_provider(
    provider: Optional[str] = None,
    base_url: Optional[str] = None,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
) -> AIProvider:
    """Factory that returns an AIProvider instance by name.

    Supported names: openai-compatible, vllm, lm-studio, openai, gemini, ollama.
    """
    provider = (provider or "openai-compatible").lower()

    if provider in ("lm-studio", "lmstudio"):
        from .compatible import OpenAICompatibleProvider

        return OpenAICompatibleProvider(
            base_url=base_url or "http://localhost:1234/v1",
            model=model or "local-model",
            api_key=api_key or "lm-studio",
        )

    if provider in ("openai-compatible", "vllm"):
        from .compatible import OpenAICompatibleProvider

        return OpenAICompatibleProvider(base_url=base_url, model=model, api_key=api_key)

    if provider == "ollama":
        from .ollama import OllamaProvider

        return OllamaProvider(base_url=base_url, model=model, api_key=api_key)

    if provider == "openai":
        from .openai import OpenAIProvider

        return OpenAIProvider(base_url=base_url, model=model, api_key=api_key)

    if provider == "gemini":
        from .gemini import GeminiProvider

        return GeminiProvider(base_url=base_url, model=model, api_key=api_key)

    raise ValueError(f"Unknown AI provider: {provider}")
