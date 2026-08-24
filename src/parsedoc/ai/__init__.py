"""ParseDoc AI package"""

from .base import AIProvider, build_provider
from .compatible import OpenAICompatibleProvider
from .openai import OpenAIProvider
from .gemini import GeminiProvider
from .ollama import OllamaProvider
from .prompts import PROMPT_VERSION, get_prompt
from . import cache

__all__ = [
    "AIProvider",
    "build_provider",
    "OpenAICompatibleProvider",
    "OpenAIProvider",
    "GeminiProvider",
    "OllamaProvider",
    "PROMPT_VERSION",
    "get_prompt",
    "cache",
]
