"""ParseDoc Text Extraction helpers"""

from typing import Dict, List


def extract_pdf_text(pdf_path: str) -> Dict[str, object]:
    """Extract text and page layout from a PDF using PyMuPDF.

    Returns a dict with ``text``, ``layout``, and ``page_count`` keys.
    """
    import fitz  # PyMuPDF

    text_parts: List[str] = []
    layout_parts: List[str] = []
    with fitz.open(pdf_path) as doc:
        page_count = doc.page_count
        for i, page in enumerate(doc):
            text_parts.append(page.get_text("text"))
            layout_parts.append(f"Page {i + 1}")
    return {
        "text": "\n".join(text_parts).strip(),
        "layout": "\n".join(layout_parts),
        "page_count": page_count,
    }


def extract_docx_text(docx_path: str) -> Dict[str, object]:
    """Extract paragraphs and tables from a DOCX using python-docx."""
    from docx import Document

    doc = Document(docx_path)
    text_parts: List[str] = [p.text for p in doc.paragraphs]
    tables: List[List[List[str]]] = []
    for table in doc.tables:
        rows = [[cell.text for cell in row.cells] for row in table.rows]
        tables.append(rows)
    return {"text": "\n".join(text_parts).strip(), "tables": tables}


def _pptx_looks_like_list(shape) -> bool:
    """Heuristic: does this text frame contain a bullet/numbered list?"""
    paragraphs = shape.text_frame.paragraphs
    total = 0
    bullets = 0
    for p in paragraphs:
        t = (p.text or "").strip()
        if not t:
            continue
        total += 1
        if (p.level and p.level > 0) or t[0] in "•*-–◦·":
            bullets += 1
    return total > 0 and bullets >= max(1, total // 2)


def _pptx_clean_item(line: str) -> str:
    return line.strip("•*-–◦· \t")


def extract_pptx_text(pptx_path: str) -> Dict[str, object]:
    """Extract structured slide content (titles, lists, tables) from a PPTX."""
    from pptx import Presentation

    prs = Presentation(pptx_path)
    blocks: List[Dict] = []
    text_parts: List[str] = []
    tables: List[List[List[str]]] = []
    first_title: str = ""

    for i, slide in enumerate(prs.slides, 1):
        slide_title = None
        body = []
        for shape in slide.shapes:
            if shape.has_table:
                rows = [[cell.text for cell in row.cells] for row in shape.table.rows]
                tables.append(rows)
                blocks.append(
                    {
                        "type": "table",
                        "headers": rows[0] if rows else [],
                        "rows": rows[1:] if len(rows) > 1 else [],
                    }
                )
                continue
            if not shape.has_text_frame:
                continue
            txt = shape.text_frame.text.strip()
            if not txt:
                continue
            try:
                is_title = bool(
                    shape.is_placeholder and shape.placeholder_format.type == 1  # TITLE
                )
            except Exception:
                is_title = False
            if is_title and slide_title is None:
                slide_title = txt
                continue
            body.append((shape, txt))

        # Fall back to first text frame as the slide title.
        if slide_title is None and body:
            slide_title = body[0][1]
            body = body[1:]

        title = (slide_title or f"Slide {i}").strip()
        # Drop body items that merely repeat the slide title.
        body = [(s, t) for (s, t) in body if t.strip() != title]
        if not first_title:
            first_title = title
        blocks.append({"type": "heading", "level": 1, "text": title})
        text_parts.append(f"# {title}")

        for shape, txt in body:
            if _pptx_looks_like_list(shape):
                items = [_pptx_clean_item(ln) for ln in txt.splitlines() if ln.strip()]
                if items:
                    blocks.append({"type": "list", "ordered": False, "items": items})
                    text_parts.append("")
                    text_parts.extend(f"- {it}" for it in items)
            else:
                blocks.append({"type": "paragraph", "text": txt})
                text_parts.append(txt)
        text_parts.append("")  # slide separator

    return {
        "text": "\n".join(text_parts).strip(),
        "tables": tables,
        "blocks": blocks,
        "title": first_title,
    }


def extract_html_text(html_path: str) -> Dict[str, object]:
    """Extract headings, paragraphs, and tables from HTML using BeautifulSoup."""
    from bs4 import BeautifulSoup

    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    text_parts: List[str] = []
    for tag in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li"]):
        text_parts.append(tag.get_text(strip=True))
    tables: List[List[List[str]]] = []
    for table in soup.find_all("table"):
        rows = []
        for tr in table.find_all("tr"):
            cells = [c.get_text(strip=True) for c in tr.find_all(["td", "th"])]
            if cells:
                rows.append(cells)
        if rows:
            tables.append(rows)
    return {"text": "\n".join(text_parts).strip(), "tables": tables}


def extract_plain_text(text_path: str) -> Dict[str, object]:
    """Read a plain text or markdown file."""
    with open(text_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    return {"text": content.strip(), "tables": []}
