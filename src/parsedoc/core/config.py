"""ParseDoc Configuration module.

Holds parser, AI, OCR, output, and cache settings. Loads and saves TOML
configuration (PRD sections 36 and 46) with environment-variable overrides.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

try:  # Python 3.11+
    import tomllib  # type: ignore

    def _loads(data: bytes) -> dict:
        return tomllib.loads(data.decode("utf-8"))

except ModuleNotFoundError:  # pragma: no cover - py<3.11
    import tomli  # type: ignore

    def _loads(data: bytes) -> dict:
        return tomli.loads(data.decode("utf-8"))


from ..utils.filesystem import default_config_path


class Config:
    """In-memory configuration for ParseDoc, backed by an optional TOML file."""

    def __init__(self):
        self.provider: str = "hybrid"
        self.ai_enabled: bool = True
        self.ai_provider: Optional[str] = "openai-compatible"
        self.base_url: str = "http://localhost:11434/v1"
        self.model: str = "qwen3"
        self.api_key: str = "local"
        self.temperature: float = 0.2
        self.max_tokens: int = 4096
        self.ocr_enabled: bool = True
        self.ocr_provider: str = "tesseract"
        self.ocr_language: str = "eng"
        self.ocr_dpi: int = 300
        self.output_format: str = "markdown"
        self.extract_images: bool = False
        self.preserve_pages: bool = False
        self.cache_enabled: bool = True

    _SECTIONS = {
        "parser": {"provider"},
        "ai": {
            "enabled",
            "provider",
            "base_url",
            "model",
            "api_key",
            "temperature",
            "max_tokens",
        },
        "ocr": {"enabled", "provider", "language", "dpi"},
        "output": {"format", "extract_images", "preserve_pages"},
        "cache": {"enabled"},
    }

    def load_from_file(self, config_path: Optional[str] = None) -> "Config":
        path = os.path.expanduser(config_path or default_config_path())
        if not os.path.exists(path):
            return self._apply_env()
        try:
            with open(path, "rb") as fh:
                data = _loads(fh.read())
        except Exception as exc:  # pragma: no cover - defensive
            print(f"Warning: failed to load config from {path}: {exc}")
            return self._apply_env()
        self._apply_dict(data)
        return self._apply_env()

    def _apply_dict(self, data: dict) -> None:
        for section, fields in self._SECTIONS.items():
            values = data.get(section, {})
            if not isinstance(values, dict):
                continue
            for key in fields:
                if key in values:
                    setattr(self, self._attr(section, key), values[key])

    @staticmethod
    def _attr(section: str, key: str) -> str:
        mapping = {
            ("ai", "enabled"): "ai_enabled",
            ("ai", "provider"): "ai_provider",
            ("ocr", "enabled"): "ocr_enabled",
            ("ocr", "provider"): "ocr_provider",
            ("ocr", "language"): "ocr_language",
            ("ocr", "dpi"): "ocr_dpi",
            ("output", "format"): "output_format",
            ("output", "extract_images"): "extract_images",
            ("output", "preserve_pages"): "preserve_pages",
            ("cache", "enabled"): "cache_enabled",
        }
        return mapping.get((section, key), key)

    def _apply_env(self) -> "Config":
        overrides = {
            "PARSEDOC_AI_PROVIDER": "ai_provider",
            "PARSEDOC_BASE_URL": "base_url",
            "PARSEDOC_MODEL": "model",
            "PARSEDOC_API_KEY": "api_key",
            "PARSEDOC_OCR_LANGUAGE": "ocr_language",
        }
        for env, attr in overrides.items():
            value = os.environ.get(env)
            if value:
                setattr(self, attr, value)
        return self

    def save_to_file(self, config_path: Optional[str] = None) -> str:
        path = os.path.expanduser(config_path or default_config_path())
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        sections = {
            "parser": {"provider": self.provider},
            "ai": {
                "enabled": self.ai_enabled,
                "provider": self.ai_provider,
                "base_url": self.base_url,
                "model": self.model,
                "api_key": self.api_key,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            },
            "ocr": {
                "enabled": self.ocr_enabled,
                "provider": self.ocr_provider,
                "language": self.ocr_language,
                "dpi": self.ocr_dpi,
            },
            "output": {
                "format": self.output_format,
                "extract_images": self.extract_images,
                "preserve_pages": self.preserve_pages,
            },
            "cache": {"enabled": self.cache_enabled},
        }
        lines = ["# ParseDoc Configuration", ""]
        for name, values in sections.items():
            lines.append(f"[{name}]")
            for key, value in values.items():
                if isinstance(value, bool):
                    lines.append(f"{key} = {str(value).lower()}")
                elif isinstance(value, (int, float)):
                    lines.append(f"{key} = {value}")
                else:
                    lines.append(f'{key} = "{value}"')
            lines.append("")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))
        return path

    def to_dict(self) -> dict:
        return {
            "parser": {"provider": self.provider},
            "ai": {
                "enabled": self.ai_enabled,
                "provider": self.ai_provider,
                "base_url": self.base_url,
                "model": self.model,
                "api_key": self.api_key,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            },
            "ocr": {
                "enabled": self.ocr_enabled,
                "provider": self.ocr_provider,
                "language": self.ocr_language,
                "dpi": self.ocr_dpi,
            },
            "output": {
                "format": self.output_format,
                "extract_images": self.extract_images,
                "preserve_pages": self.preserve_pages,
            },
            "cache": {"enabled": self.cache_enabled},
        }

    @property
    def ai_active(self) -> bool:
        return bool(self.ai_enabled) and bool(self.ai_provider) and self.ai_provider != "none"
