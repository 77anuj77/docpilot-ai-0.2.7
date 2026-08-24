"""ParseDoc Parsers package"""

from .base import BaseParser
from .pdf import PDFParser
from .docx import DOCXParser
from .pptx import PPTXParser
from .html import HTMLParser
from .image import ImageParser
from .text import TextParser

PARSER_REGISTRY = {
    "pdf": PDFParser,
    "docx": DOCXParser,
    "pptx": PPTXParser,
    "html": HTMLParser,
    "image": ImageParser,
    "txt": TextParser,
    "md": TextParser,
}


def get_parser(format_name: str, config):
    """Return a parser instance for the given format name."""
    parser_cls = PARSER_REGISTRY.get(format_name)
    if parser_cls is None:
        raise ValueError(f"No parser registered for format: {format_name}")
    return parser_cls(config)


__all__ = [
    "BaseParser",
    "PDFParser",
    "DOCXParser",
    "PPTXParser",
    "HTMLParser",
    "ImageParser",
    "TextParser",
    "PARSER_REGISTRY",
    "get_parser",
]
