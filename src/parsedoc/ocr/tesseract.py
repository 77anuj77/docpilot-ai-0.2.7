"""ParseDoc Tesseract OCR provider (PRD #23)"""

from typing import List, Optional

from .base import OCRProvider


class TesseractProvider(OCRProvider):
    name = "tesseract"

    def __init__(self, language: str = "eng", dpi: int = 300):
        self.language = language
        self.dpi = dpi

    def ocr(self, image_path: str) -> str:
        try:
            from PIL import Image
            import pytesseract
        except ImportError as e:
            raise RuntimeError(
                "Tesseract OCR requires 'pillow' and 'pytesseract'. "
                "Install with: pip install pillow pytesseract"
            ) from e

        with Image.open(image_path) as img:
            return pytesseract.image_to_string(img, lang=self.language).strip()

    def ocr_pdf_page(self, image_bytes: bytes) -> str:
        """Convenience OCR for a rendered PDF page (bytes)."""
        from PIL import Image
        import io

        img = Image.open(io.BytesIO(image_bytes))
        import pytesseract

        return pytesseract.image_to_string(img, lang=self.language).strip()

    def is_available(self) -> bool:
        try:
            import pytesseract  # noqa: F401

            return True
        except ImportError:
            return False
