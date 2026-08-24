"""ParseDoc OpenAI-compatible AI provider (PRD #13, P0)"""

from typing import Optional

from .base import AIProvider


class OpenAICompatibleProvider(AIProvider):
    """Provider that talks to any OpenAI-compatible chat completions API.

    Works with OpenAI, Ollama, LM Studio, vLLM, etc. by pointing ``base_url``
    at the server's ``/v1`` endpoint.
    """

    name = "openai-compatible"

    def __init__(
        self,
        base_url: Optional[str] = "http://localhost:11434/v1",
        model: Optional[str] = "qwen3",
        api_key: Optional[str] = "local",
    ):
        self.base_url = base_url or "http://localhost:11434/v1"
        self.model = model or "qwen3"
        self.api_key = api_key or "local"

    def generate(self, prompt: str, content: str) -> str:
        try:
            from openai import OpenAI
        except ImportError as e:
            raise RuntimeError(
                "The 'openai' package is required for OpenAI-compatible providers. "
                "Install with: pip install openai"
            ) from e

        client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            timeout=120,
            max_retries=1,
        )
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": content},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content or ""

    def is_available(self) -> bool:
        try:
            import openai  # noqa: F401

            return True
        except ImportError:
            return False
