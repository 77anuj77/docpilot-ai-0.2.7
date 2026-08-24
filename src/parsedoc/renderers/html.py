"""ParseDoc HTML renderer"""

from typing import List

from ..schema.document import Block, Document


def _render_block(block: Block) -> str:
    btype = block.type
    if btype == "heading":
        level = max(1, min(6, block.level or 1))
        return f"<h{level}>{_esc(block.text or '')}</h{level}>"
    if btype == "paragraph":
        return f"<p>{_esc(block.text or '')}</p>"
    if btype == "list":
        items = "".join(f"<li>{_esc(i)}</li>" for i in (block.items or []))
        return f"<ul>{items}</ul>"
    if btype == "table":
        return _render_table(block.headers or [], block.rows or [])
    if btype == "code":
        return f"<pre><code>{_esc(block.text or '')}</code></pre>"
    if btype == "quote":
        return f"<blockquote>{_esc(block.text or '')}</blockquote>"
    if btype == "image":
        return f'<img src="{_esc(block.src or "")}" alt="{_esc(block.alt or "")}" />'
    if btype == "link":
        return f'<a href="{_esc(block.url or "")}">{_esc(block.text or "")}</a>'
    if btype == "pagebreak":
        return "<hr />"
    return f"<p>{_esc(block.text or '')}</p>"


def _render_table(headers: List[str], rows: List[List[str]]) -> str:
    def _c(v: str) -> str:
        return str(v).replace("\n", " ").replace("\r", " ").strip()

    thead = ""
    if headers:
        thead = (
            "<thead><tr>" + "".join(f"<th>{_esc(_c(h))}</th>" for h in headers) + "</tr></thead>"
        )
    tbody = (
        "<tbody>"
        + "".join(
            "<tr>" + "".join(f"<td>{_esc(_c(c))}</td>" for c in row) + "</tr>" for row in rows
        )
        + "</tbody>"
    )
    return f"<table>{thead}{tbody}</table>"


def _esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_html(doc: Document) -> str:
    title = _esc(doc.title) if doc.title != "Untitled Document" else "Document"
    body = "\n".join(_render_block(b) for b in doc.blocks)
    return f"<!DOCTYPE html>\n<html><head><title>{title}</title></head><body>\n{body}\n</body></html>\n"
