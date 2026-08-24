"""ParseDoc Renderers package"""

from ..schema.document import Document

from .markdown import render_markdown
from .html import render_html
from .json import render_json
from .text import render_text

RENDERERS = {
    "markdown": render_markdown,
    "html": render_html,
    "json": render_json,
    "text": render_text,
}


def render(doc: Document, fmt: str = "markdown") -> str:
    """Render a Document to the requested format."""
    fmt = (fmt or "markdown").lower()
    if fmt not in RENDERERS:
        raise ValueError(f"Unsupported output format: {fmt}")
    return RENDERERS[fmt](doc)


__all__ = [
    "render_markdown",
    "render_html",
    "render_json",
    "render_text",
    "render",
    "RENDERERS",
]
