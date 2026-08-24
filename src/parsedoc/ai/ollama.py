"""ParseDoc Ollama provider (PRD #14, P1) - native Ollama API.

Uses the local Ollama REST API via the standard library so no extra SDK is
required. Ollama also exposes an OpenAI-compatible ``/v1`` endpoint, but this
implementation talks to ``/api/chat`` directly and requests JSON output.
"""

from typing import Optional

from .base import AIProvider


class OllamaProvider(AIProvider):
    name = "ollama"

    def __init__(
        self,
        base_url: Optional[str] = "http://localhost:11434",
        model: Optional[str] = "qwen3",
        api_key: Optional[str] = "ollama",
    ):
        self.base_url = (base_url or "http://localhost:11434").rstrip("/")
        self.model = model or "qwen3"
        self.api_key = api_key

    def generate(self, prompt: str, content: str) -> str:
        import json
        import urllib.request

        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": content},
            ],
            "stream": False,
            "format": "json",
        }
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=300) as response:
                data = json.loads(response.read().decode("utf-8"))
            return data["message"]["content"] or ""
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"Ollama request failed: {exc}") from exc

    def is_available(self) -> bool:
        import urllib.request

        try:
            urllib.request.urlopen(f"{self.base_url}/api/tags", timeout=3)
            return True
        except Exception:
            return False
