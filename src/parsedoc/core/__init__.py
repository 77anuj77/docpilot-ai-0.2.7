"""ParseDoc Core package"""

from .config import Config
from .detection import detect_format, is_supported, supported_formats
from .chunking import chunk_text

__all__ = [
    "Config",
    "detect_format",
    "is_supported",
    "supported_formats",
    "chunk_text",
]
