"""ParseDoc Document Schema - internal document model"""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class Block(BaseModel):
    """A single content block in a document"""

    type: str = Field(
        ...,
        description="Block type: heading, paragraph, list, table, image, code, quote, link, pagebreak",
    )
    level: Optional[int] = None
    text: Optional[str] = None
    items: Optional[List[str]] = None
    ordered: bool = False
    headers: Optional[List[str]] = None
    rows: Optional[List[List[str]]] = None
    src: Optional[str] = None
    alt: Optional[str] = None
    url: Optional[str] = None
    language: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Document(BaseModel):
    """Structured document representation"""

    title: str = "Untitled Document"
    blocks: List[Block] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


SUPPORTED_BLOCK_TYPES = [
    "heading",
    "paragraph",
    "list",
    "table",
    "image",
    "code",
    "quote",
    "link",
    "pagebreak",
]
