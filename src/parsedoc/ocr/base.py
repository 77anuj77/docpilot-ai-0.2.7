"""ParseDoc OCR Provider abstraction (PRD #23)"""

import abc
from typing import Optional


class OCRProvider(abc.ABC):
    """Abstract base for OCR providers."""

    name: str = "base"

    @abc.abstractmethod
    def ocr(self, image_path: str) -> str:
        """Run OCR on an image file and return extracted text."""
        raise NotImplementedError

    def is_available(self) -> bool:
        return True


def build_ocr_provider(name: Optional[str] = "tesseract") -> OCRProvider:
    name = (name or "tesseract").lower()
    if name == "tesseract":
        from .tesseract import TesseractProvider

        return TesseractProvider()
    raise ValueError(f"Unknown OCR provider: {name}")
