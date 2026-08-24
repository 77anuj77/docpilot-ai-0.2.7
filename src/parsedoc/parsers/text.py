"""ParseDoc Plain text / Markdown Parser (native)"""

from typing import Dict

from ..core.config import Config
from ..extraction import extract_plain_text
from ..schema.document import Block, Document
from .base import BaseParser


class TextParser(BaseParser):
    format_name = "txt"

    def detect_format(self, input_path: str) -> str:
        ext = input_path.lower().rsplit(".", 1)[-1] if "." in input_path else ""
        if ext in ("txt", "md", "markdown"):
            return ext
        return "unknown"

    def extract(self, input_path: str) -> Dict:
        self.logger.info("Reading plain text content")
        try:
            return extract_plain_text(input_path)
        except Exception as e:
            self.logger.error(f"Text extraction failed: {e}")
            return {"text": "", "tables": []}

    def to_document(self, extracted: Dict, input_path: str = "") -> Document:
        text = extracted.get("text", "")
        # For markdown, preserve headings; for plain txt, split into paragraphs.
        is_md = input_path.lower().endswith((".md", ".markdown"))
        blocks = []
        if is_md:
            blocks = self._markdown_blocks(text)
        else:
            blocks = self._paragraph_blocks(text)
        return Document(
            title="Text Document",
            blocks=blocks,
            metadata={"source": input_path, "format": "txt"},
        )

    def _markdown_blocks(self, text: str) -> list:
        blocks = []
        for line in text.splitlines():
            line = line.rstrip()
            if not line.strip():
                continue
            if line.startswith("#"):
                level = len(line.split(" ", 1)[0])
                blocks.append(Block(type="heading", level=level, text=line.lstrip("# ").strip()))
            else:
                blocks.append(Block(type="paragraph", text=line))
        return blocks
