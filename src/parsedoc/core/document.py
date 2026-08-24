"""ParseDoc Core Document model re-export.

The canonical document model lives in :mod:`parsedoc.schema.document`.
This module re-exports it so the PRD's ``core/document.py`` location remains
valid without duplicating the model.
"""

from ..schema.document import Block, Document, SUPPORTED_BLOCK_TYPES  # noqa: F401

__all__ = ["Block", "Document", "SUPPORTED_BLOCK_TYPES"]
