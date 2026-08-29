"""ParseDoc PDF Parser (PyMuPDF)"""

from typing import Dict

from ..core.config import Config
from ..extraction import assess_text_quality, extract_pdf_images, extract_pdf_text
from ..schema.document import Document
from .base import BaseParser


class PDFParser(BaseParser):
    format_name = "pdf"

    def detect_format(self, input_path: str) -> str:
        try:
            try:
                import pymupdf as fitz
            except ImportError:
                import fitz  # PyMuPDF

            with fitz.open(input_path):
                return "pdf"
        except Exception:
            return "unknown"

    def extract(self, input_path: str) -> Dict:
        self.logger.info("Extracting PDF content with PyMuPDF")
        try:
            data = extract_pdf_text(input_path)
        except Exception as e:
            self.logger.error(f"PDF extraction failed: {e}")
            return {"text": "", "layout": "", "tables": [], "images": [], "page_count": 0}
        data["tables"] = data.get("tables") or []
        data["images"] = extract_pdf_images(input_path)
        data["quality"] = assess_text_quality(data.get("text", ""))
        return data

    def to_document(self, extracted: Dict, input_path: str = "") -> Document:
        text = extracted.get("text", "")
        blocks = self._paragraph_blocks(text)
        blocks += self._table_blocks(extracted.get("tables"))
        return Document(
            title="Document",
            blocks=blocks,
            metadata={
                "source": input_path,
                "format": "pdf",
                "page_count": extracted.get("page_count", 0),
                "quality": extracted.get("quality", {}),
            },
        )
