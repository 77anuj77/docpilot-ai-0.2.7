"""ParseDoc Quality assessment (PRD #24)"""

import re


def assess_text_quality(text: str) -> dict:
    """Assess whether extracted text is likely sufficient or needs OCR.

    Returns a dict with ``needs_ocr`` (bool) and a ``score`` between 0 and 1.
    """
    if not text or not text.strip():
        return {"needs_ocr": True, "score": 0.0, "reason": "empty"}

    length = len(text.strip())
    # Ratio of control/garbage characters
    garbage = len(re.findall(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", text))
    garbage_ratio = garbage / max(length, 1)

    # Very short text relative to a typical page often means a scanned doc
    short = length < 100

    score = 1.0 - min(garbage_ratio * 5, 1.0)
    needs_ocr = garbage_ratio > 0.05 or (short and length < 30)

    return {
        "needs_ocr": bool(needs_ocr),
        "score": round(score, 3),
        "reason": "garbage" if garbage_ratio > 0.05 else ("short" if short else "ok"),
    }
