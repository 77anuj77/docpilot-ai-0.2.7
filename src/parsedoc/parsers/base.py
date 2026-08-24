"""ParseDoc Parser base class"""

import abc
from typing import Dict

from ..core.config import Config
from ..schema.document import Block, Document
from ..utils.logging import setup_logging


class BaseParser(abc.ABC):
    """Abstract base for format-specific parsers.

    A parser is responsible for:
      1. Detecting whether it can handle a given file (``detect_format``).
      2. Extracting raw content (``extract``).
      3. Structuring extracted content into a Document (``to_document``).
    """

    #: Canonical format name handled by this parser.
    format_name: str = "unknown"

    def __init__(self, config: Config):
        self.config = config
        self.logger = setup_logging()

    @abc.abstractmethod
    def detect_format(self, input_path: str) -> str:
        """Return the canonical format name if this parser handles the file."""

    @abc.abstractmethod
    def extract(self, input_path: str) -> Dict:
        """Extract raw content (text, tables, images, layout) from the file."""

    @abc.abstractmethod
    def to_document(self, extracted: Dict, input_path: str = "") -> Document:
        """Convert extracted content into a structured Document."""

    # ------------------------------------------------------------------ #
    # Shared helpers
    # ------------------------------------------------------------------ #
    def _paragraph_blocks(self, text: str) -> list:
        blocks = []
        for chunk in text.split("\n\n"):
            chunk = chunk.strip()
            if chunk:
                blocks.append(Block(type="paragraph", text=chunk))
        return blocks

    def _table_blocks(self, raw_tables) -> list:
        from ..extraction.tables import merge_tables

        blocks = []
        for table in merge_tables(raw_tables or []):
            blocks.append(Block(type="table", **table))
        return blocks
