"""ParseDoc HTML Parser (BeautifulSoup)"""

from typing import Dict, List, Optional

from ..core.config import Config
from ..extraction.tables import normalize_table
from ..schema.validation import validate_document
from ..utils.logging import get_logger
from .base import BaseParser


class HTMLParser(BaseParser):
    format_name = "html"

    def detect_format(self, input_path: str) -> str:
        try:
            from bs4 import BeautifulSoup

            with open(input_path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f.read(), "html.parser")
            return "html" if soup.find() is not None else "unknown"
        except Exception:
            return "unknown"

    def extract(self, input_path: str) -> Dict:
        self.logger.info("Extracting HTML content with BeautifulSoup")
        try:
            from bs4 import BeautifulSoup

            with open(input_path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f.read(), "html.parser")
            blocks = self._structure(soup)
            text = "\n".join(
                (b.get("text") or b.get("code") or "")
                for b in blocks
                if b["type"] in ("heading", "paragraph", "quote")
            )
            tables: List[List[List[str]]] = []
            for b in blocks:
                if b["type"] == "table":
                    tbl = b["headers"] + b["rows"] if b.get("headers") else b["rows"]
                    tables.append(tbl)
            return {
                "text": text,
                "tables": tables,
                "blocks": blocks,
                "title": (soup.title.get_text(strip=True) if soup.title else ""),
            }
        except Exception as e:
            self.logger.error(f"HTML extraction failed: {e}")
            return {"text": "", "tables": [], "blocks": []}

    def _structure(self, soup) -> List[Dict]:
        blocks: List[Dict] = []
        for tag in soup.find_all(
            ["h1", "h2", "h3", "h4", "h5", "h6", "p", "ul", "ol", "table", "blockquote", "pre"]
        ):
            if tag.find_parent(["ul", "ol", "table", "blockquote", "pre"]):
                continue
            name = tag.name
            if name.startswith("h"):
                txt = tag.get_text(" ", strip=True)
                if txt:
                    blocks.append({"type": "heading", "level": int(name[1]), "text": txt})
            elif name == "p":
                txt = tag.get_text(" ", strip=True)
                if txt:
                    blocks.append({"type": "paragraph", "text": txt})
            elif name in ("ul", "ol"):
                items = [li.get_text(" ", strip=True) for li in tag.find_all("li")]
                if items:
                    blocks.append({"type": "list", "ordered": name == "ol", "items": items})
            elif name == "table":
                rows = [
                    [c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])]
                    for tr in tag.find_all("tr")
                ]
                rows = [r for r in rows if r]
                if rows:
                    norm = normalize_table(rows)
                    blocks.append(
                        {
                            "type": "table",
                            "headers": norm["headers"],
                            "rows": norm["rows"],
                        }
                    )
            elif name == "blockquote":
                blocks.append({"type": "quote", "text": tag.get_text(" ", strip=True)})
            elif name == "pre":
                blocks.append({"type": "code", "code": tag.get_text()})
        return blocks

    def to_document(self, extracted: Dict, input_path: str = "") -> "Document":
        blocks = [b for b in extracted.get("blocks", []) if isinstance(b, dict) and "type" in b]
        if not blocks:
            blocks = self._paragraph_blocks(extracted.get("text", ""))
        return validate_document(
            {
                "title": extracted.get("title", "") or "Web Page",
                "blocks": blocks,
                "metadata": {"source": input_path, "format": "html"},
            }
        )
