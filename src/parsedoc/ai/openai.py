"""ParseDoc OpenAI provider (PRD #14, P2)"""

from typing import Optional

from .base import AIProvider


class OpenAIProvider(AIProvider):
    name = "openai"

    def __init__(
        self,
        base_url: Optional[str] = "https://api.openai.com/v1",
        model: Optional[str] = "gpt-4o-mini",
        api_key: Optional[str] = None,
    ):
        self.base_url = base_url or "https://api.openai.com/v1"
        self.model = model or "gpt-4o-mini"
        self.api_key = api_key

    def generate(self, prompt: str, content: str) -> str:
        try:
            from openai import OpenAI
        except ImportError as e:
            raise RuntimeError(
                "The 'openai' package is required. Install with: pip install openai"
            ) from e

        client = OpenAI(base_url=self.base_url, api_key=self.api_key)
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
        return bool(self.api_key)
