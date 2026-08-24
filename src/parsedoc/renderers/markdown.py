"""ParseDoc Markdown renderer (PRD #32)"""

from typing import List

from ..schema.document import Block, Document


def _render_block(block: Block) -> str:
    btype = block.type
    if btype == "heading":
        level = max(1, min(6, block.level or 1))
        return f"{'#' * level} {block.text or ''}"
    if btype == "paragraph":
        return block.text or ""
    if btype == "list":
        items = block.items or []
        if block.ordered:
            return "\n".join(f"{i + 1}. {item}" for i, item in enumerate(items))
        return "\n".join(f"- {item}" for item in items)
    if btype == "table":
        return _render_table(block.headers or [], block.rows or [])
    if btype == "code":
        lang = block.language or ""
        return f"```{lang}\n{block.text or ''}\n```"
    if btype == "quote":
        text = block.text or ""
        return "\n".join(f"> {line}" for line in text.splitlines())
    if btype == "image":
        alt = block.alt or "image"
        src = block.src or ""
        return f"![{alt}]({src})"
    if btype == "link":
        text = block.text or block.url or ""
        url = block.url or ""
        return f"[{text}]({url})"
    if btype == "pagebreak":
        return "\n---\n"
    return block.text or ""


def _cell(value) -> str:
    return str(value).replace("\n", " ").replace("\r", " ").strip()


def _render_table(headers: List[str], rows: List[List[str]]) -> str:
    if not headers and not rows:
        return ""
    lines = []
    if headers:
        lines.append("| " + " | ".join(_cell(h) for h in headers) + " |")
        lines.append("| " + " | ".join("---" for _ in headers) + " |")
    for row in rows:
        lines.append("| " + " | ".join(_cell(c) for c in row) + " |")
    return "\n".join(lines)


def render_markdown(doc: Document) -> str:
    """Render a Document model to deterministic Markdown."""
    parts: List[str] = []
    if doc.title and doc.title != "Untitled Document":
        # Avoid duplicating the title when the first block is already that heading.
        first = doc.blocks[0] if doc.blocks else None
        if not (
            first and first.type == "heading" and (first.text or "").strip() == doc.title.strip()
        ):
            parts.append(f"# {doc.title}")
    for block in doc.blocks:
        parts.append(_render_block(block))
    # Join with blank lines, collapsing excess whitespace.
    text = "\n\n".join(p for p in parts if p is not None)
    return text.strip() + "\n"
