"""ParseDoc AI Prompts (PRD #18, #43)"""

# Versioned prompt used to ask the model for structured document output.
# Bump when the structure/rules change so the response cache is invalidated.
PROMPT_VERSION = "v2"

DOCUMENT_STRUCTURE_PROMPT = """You are a document structure analyzer. Convert the extracted
document text into a structured JSON representation.

Rules:
1. Preserve factual content and wording EXACTLY. Do not invent, rephrase, or summarize.
2. Detect headings and assign a "level" (1-6).
3. Reconstruct paragraphs verbatim from the source text.
4. Identify tables with "headers" and "rows".
5. Preserve lists as type "list" with "items".
6. Remove obvious repeated headers/footers.
7. Preserve document order.
8. Do NOT add information not present in the source.
9. IMPORTANT - preserve INLINE formatting inside every text field using Markdown:
   - Bold runs → wrap the exact words in **double asterisks**
   - Italic runs → wrap in *single asterisks*
   - Underlined runs → wrap in <u>...</u>
   - Hyperlinks → use [label](https://url) with the real destination URL
   Keep these markers tightly around the original words so the rendered
   Markdown matches the source document's appearance.

Return ONLY valid JSON matching this schema:
{
  "title": string,
  "blocks": [
    {"type": "heading", "level": int, "text": string},
    {"type": "paragraph", "text": string},
    {"type": "list", "ordered": bool, "items": [string]},
    {"type": "table", "headers": [string], "rows": [[string]]}
  ]
}
"""

OCR_CLEANUP_PROMPT = """You are an OCR cleanup assistant. The provided text was produced by
optical character recognition and may contain errors. Fix obvious OCR errors
(letters confused with similar shapes, broken words) while preserving the
original meaning and factual content. Return the cleaned text only."""

TABLE_REPAIR_PROMPT = """You are a table repair assistant. The provided table may have broken
structure. Repair column alignment and return ONLY valid JSON:
{"headers": [string], "rows": [[string]]}. Do not change any values."""


def get_prompt(name: str = "document_structure") -> str:
    """Return a versioned prompt by name."""
    prompts = {
        "document_structure": DOCUMENT_STRUCTURE_PROMPT,
        "ocr_cleanup": OCR_CLEANUP_PROMPT,
        "table_repair": TABLE_REPAIR_PROMPT,
    }
    return prompts.get(name, DOCUMENT_STRUCTURE_PROMPT)
