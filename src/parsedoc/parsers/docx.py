"""ParseDoc DOCX Parser (python-docx)"""

import re
from typing import Dict, List, Optional

from docx.text.paragraph import Paragraph as _ParagraphType

from ..core.config import Config
from ..schema.document import Document
from ..schema.validation import validate_document
from ..utils.logging import get_logger
from .base import BaseParser


def _iter_block_items(parent):
    """Yield Paragraph and Table objects from a document in document order."""
    from docx.document import Document as _Doc
    from docx.oxml.table import CT_Tbl
    from docx.oxml.text.paragraph import CT_P
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    if isinstance(parent, _Doc):
        elem = parent.element.body
    else:
        elem = parent.element
    for child in elem.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)


class DOCXParser(BaseParser):
    format_name = "docx"

    def detect_format(self, input_path: str) -> str:
        try:
            from docx import Document as DocxDocument

            DocxDocument(input_path)
            return "docx"
        except Exception:
            return "unknown"

    @staticmethod
    def _inline_text(para) -> str:
        """Render a paragraph's runs, preserving bold/italic/underline."""
        parts = []
        for run in para.runs:
            t = run.text
            if not t:
                continue
            if run.bold and run.italic:
                t = f"***{t}***"
            elif run.bold:
                t = f"**{t}**"
            elif run.italic:
                t = f"*{t}*"
            if run.underline:
                t = f"<u>{t}</u>"
            parts.append(t)
        if parts:
            return "".join(parts).strip()
        return (para.text or "").strip()

    @staticmethod
    def _list_info(para):
        """Return (is_list, ordered) for a paragraph."""
        style = (para.style.name if para.style else "") or ""
        if style.startswith("List") or "Bullet" in style or "Number" in style:
            return True, ("Number" in style)
        pPr = para._p.pPr
        if pPr is not None and pPr.numPr is not None:
            return True, False
        return False, False

    def extract(self, input_path: str) -> Dict:
        self.logger.info("Extracting DOCX content with python-docx")
        try:
            from docx import Document as DocxDocument

            doc = DocxDocument(input_path)
            blocks: List[Dict] = []
            tables: List[List[List[str]]] = []
            title = ""
            text_lines: List[str] = []
            current_list = None  # dict being accumulated

            def flush_list():
                nonlocal current_list
                if current_list is not None:
                    blocks.append(current_list)
                    current_list = None

            for item in _iter_block_items(doc):
                # Tables: keep their in-document position.
                if not isinstance(item, _ParagraphType):
                    rows = [[cell.text for cell in row.cells] for row in item.rows]
                    if not rows:
                        continue
                    tables.append(rows)
                    blocks.append(
                        {
                            "type": "table",
                            "headers": rows[0] if rows else [],
                            "rows": rows[1:] if len(rows) > 1 else [],
                        }
                    )
                    text_lines.append("[table]")
                    continue

                para = item
                style = (para.style.name if para.style else "") or ""
                txt = self._inline_text(para)
                if not txt:
                    continue
                is_list, ordered = self._list_info(para)

                if is_list:
                    item_text = txt
                    if current_list and current_list.get("ordered") == ordered:
                        current_list["items"].append(item_text)
                    else:
                        flush_list()
                        current_list = {
                            "type": "list",
                            "ordered": ordered,
                            "items": [item_text],
                        }
                    text_lines.append(("1. " if ordered else "- ") + item_text)
                    continue

                flush_list()
                if style.startswith("Title"):
                    if not title:
                        title = txt
                    continue
                elif style.startswith("Heading"):
                    m = re.match(r"Heading\s*(\d+)", style)
                    level = int(m.group(1)) if m else 1
                    blocks.append({"type": "heading", "level": level, "text": txt})
                    text_lines.append("#" * level + " " + txt)
                else:
                    blocks.append({"type": "paragraph", "text": txt})
                    text_lines.append(txt)

            flush_list()

            # Fall back to the first heading (or first paragraph) as the title
            # when no explicit "Title" style was found.
            if not title:
                for b in blocks:
                    if b["type"] == "heading":
                        title = b["text"]
                        break
                if not title and blocks:
                    title = blocks[0].get("text", "")

            text = "\n".join(text_lines)
            return {"text": text, "tables": tables, "blocks": blocks, "title": title}
        except Exception as e:
            self.logger.error(f"DOCX extraction failed: {e}")
            return {"text": "", "tables": [], "blocks": []}

    def to_document(self, extracted: Dict, input_path: str = "") -> "Document":
        blocks = [b for b in extracted.get("blocks", []) if isinstance(b, dict) and "type" in b]
        if not blocks:
            blocks = self._paragraph_blocks(extracted.get("text", ""))
            blocks += self._table_blocks(extracted.get("tables"))
        return validate_document(
            {
                "title": extracted.get("title", "") or "Document",
                "blocks": blocks,
                "metadata": {"source": input_path, "format": "docx"},
            }
        )
