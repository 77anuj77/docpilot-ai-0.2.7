"""ParseDoc Layout Extraction helpers"""


def estimate_reading_order(layout_text: str) -> list:
    """Return a simple ordered list of page markers from layout text."""
    return [line for line in layout_text.splitlines() if line.strip()]


def summarize_layout(layout_text: str) -> dict:
    """Summarize a layout string into a small descriptor dict."""
    pages = [l for l in layout_text.splitlines() if l.lower().startswith("page")]
    return {"page_count": len(pages), "raw": layout_text}
