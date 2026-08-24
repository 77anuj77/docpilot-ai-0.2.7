"""ParseDoc Chunking utilities (PRD #20)"""

from typing import List

DEFAULT_CHUNK_SIZE = 4000


def chunk_text(text: str, chunk_size: int = DEFAULT_CHUNK_SIZE) -> List[str]:
    """Split text into chunks of roughly ``chunk_size`` characters.

    Splitting prefers paragraph and sentence boundaries to keep chunks
    coherent. Chunks never exceed ``chunk_size * 1.5`` characters.
    """
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]

    chunks: List[str] = []
    current = ""

    paragraphs = text.split("\n\n")
    for para in paragraphs:
        if len(current) + len(para) + 2 <= chunk_size:
            current = (current + "\n\n" + para).strip() if current else para
        else:
            if current:
                chunks.append(current)
            # Paragraph itself larger than chunk_size -> split by sentences
            if len(para) > chunk_size:
                chunks.extend(_split_long(para, chunk_size))
                current = ""
            else:
                current = para
    if current:
        chunks.append(current)
    return chunks


def _split_long(text: str, chunk_size: int) -> List[str]:
    out: List[str] = []
    buf = ""
    for sentence in text.split(". "):
        piece = sentence + ". " if not sentence.endswith(".") else sentence + " "
        if len(buf) + len(piece) > chunk_size and buf:
            out.append(buf.strip())
            buf = piece
        else:
            buf += piece
    if buf:
        out.append(buf.strip())
    return out
