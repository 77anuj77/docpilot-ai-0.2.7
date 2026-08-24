"""ParseDoc Gemini provider (PRD #14, P1)"""

from typing import Optional

from .base import AIProvider


class GeminiProvider(AIProvider):
    name = "gemini"

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = "gemini-1.5-flash",
        api_key: Optional[str] = None,
    ):
        self.model = model or "gemini-1.5-flash"
        self.api_key = api_key

    def generate(self, prompt: str, content: str) -> str:
        try:
            import google.generativeai as genai
        except ImportError as e:
            raise RuntimeError(
                "The 'google-generativeai' package is required. "
                "Install with: pip install google-generativeai"
            ) from e

        if not self.api_key:
            raise RuntimeError("Gemini requires an API key (GEMINI_API_KEY/GOOGLE_API_KEY).")

        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(self.model)
        response = model.generate_content(f"{prompt}\n\n{content}")
        return response.text or ""

    def is_available(self) -> bool:
        return bool(self.api_key)
