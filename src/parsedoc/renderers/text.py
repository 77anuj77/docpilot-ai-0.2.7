"""ParseDoc Plain-text renderer"""

from ..schema.document import Block, Document


def render_text(doc: Document) -> str:
    """Render a Document model to plain text (headings and paragraphs only)."""
    lines = []
    if doc.title and doc.title != "Untitled Document":
        lines.append(doc.title)
        lines.append("=" * len(doc.title))
        lines.append("")
    for block in doc.blocks:
        if block.type in ("heading", "paragraph", "quote"):
            lines.append(block.text or "")
            lines.append("")
        elif block.type == "list":
            for item in block.items or []:
                lines.append(f"- {item}")
            lines.append("")
    return "\n".join(lines).strip() + "\n"
