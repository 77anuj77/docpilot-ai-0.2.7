"""ParseDoc Format Detection"""

from pathlib import Path
from typing import Dict, List

# Extension -> canonical format name
EXTENSION_MAP: Dict[str, str] = {
    ".pdf": "pdf",
    ".docx": "docx",
    ".pptx": "pptx",
    ".html": "html",
    ".htm": "html",
    ".txt": "txt",
    ".md": "md",
    ".markdown": "md",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
}

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}
TEXT_EXTENSIONS = {".txt", ".md", ".markdown"}
MARKUP_EXTENSIONS = {".html", ".htm"}


def detect_format(input_path: str) -> str:
    """Detect the document format from its file extension.

    Args:
        input_path: Path to the input file.

    Returns:
        A canonical format string (pdf, docx, pptx, html, txt, md, image) or
        "unknown" if it cannot be determined.
    """
    suffix = Path(input_path).suffix.lower()
    return EXTENSION_MAP.get(suffix, "unknown")


def supported_formats() -> List[str]:
    """Return the list of supported canonical format names."""
    return sorted(set(EXTENSION_MAP.values()))


def is_supported(input_path: str) -> bool:
    """Return True if the file extension is supported."""
    return detect_format(input_path) != "unknown"
