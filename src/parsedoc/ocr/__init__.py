"""ParseDoc OCR package"""

from .base import OCRProvider, build_ocr_provider
from .tesseract import TesseractProvider

__all__ = ["OCRProvider", "build_ocr_provider", "TesseractProvider"]
