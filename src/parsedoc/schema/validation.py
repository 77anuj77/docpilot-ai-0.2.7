"""ParseDoc Schema Validation"""

from typing import Any, Dict, Union

from pydantic import ValidationError

from .document import Document, Block


def validate_document(data: Union[Dict[str, Any], Document]) -> Document:
    """Validate and coerce input into a Document model.

    Args:
        data: A dict or already-built Document.

    Returns:
        A validated Document instance.

    Raises:
        ValueError: If the data cannot be coerced into a valid Document.
    """
    if isinstance(data, Document):
        return data
    try:
        return Document(**data)
    except ValidationError as e:
        raise ValueError(f"Invalid document structure: {e}") from e


def validate_block(data: Dict[str, Any]) -> Block:
    """Validate a single block."""
    try:
        return Block(**data)
    except ValidationError as e:
        raise ValueError(f"Invalid block: {e}") from e
