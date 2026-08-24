"""ParseDoc PPTX Parser (python-pptx)"""

from typing import Dict

from ..core.config import Config
from ..extraction import extract_pptx_text
from ..schema.document import Document
from .base import BaseParser


class PPTXParser(BaseParser):
    format_name = "pptx"

    def detect_format(self, input_path: str) -> str:
        try:
            from pptx import Presentation

            Presentation(input_path)
            return "pptx"
        except Exception:
            return "unknown"

    def extract(self, input_path: str) -> Dict:
        self.logger.info("Extracting PPTX content with python-pptx")
        try:
            return extract_pptx_text(input_path)
        except Exception as e:
            self.logger.error(f"PPTX extraction failed: {e}")
            return {"text": "", "tables": [], "blocks": []}

    def to_document(self, extracted: Dict, input_path: str = "") -> Document:
        blocks = [b for b in extracted.get("blocks", []) if isinstance(b, dict) and "type" in b]
        if not blocks:
            blocks = self._paragraph_blocks(extracted.get("text", ""))
        blocks += self._table_blocks(extracted.get("tables"))
        return Document(
            title=extracted.get("title") or "Presentation",
            blocks=blocks,
            metadata={"source": input_path, "format": "pptx"},
        )
