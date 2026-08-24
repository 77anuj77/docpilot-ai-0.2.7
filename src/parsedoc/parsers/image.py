"""ParseDoc Image Parser (OCR via Tesseract)"""

from typing import Dict

from ..core.config import Config
from ..schema.document import Document
from .base import BaseParser


class ImageParser(BaseParser):
    format_name = "image"

    def detect_format(self, input_path: str) -> str:
        try:
            from PIL import Image

            with Image.open(input_path) as img:
                img.verify()
            return "image"
        except Exception:
            return "unknown"

    def extract(self, input_path: str) -> Dict:
        self.logger.info("Extracting image content via OCR")
        try:
            from PIL import Image
            import pytesseract

            with Image.open(input_path) as img:
                text = pytesseract.image_to_string(img)
                size = img.size
            return {"text": text.strip(), "layout": f"Image dimensions: {size}"}
        except Exception as e:
            self.logger.error(f"OCR failed: {e}")
            return {"text": "", "layout": ""}

    def to_document(self, extracted: Dict, input_path: str = "") -> Document:
        text = extracted.get("text", "")
        blocks = self._paragraph_blocks(text)
        return Document(
            title="Image Content",
            blocks=blocks,
            metadata={"source": input_path, "format": "image"},
        )
