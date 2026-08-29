"""Smoke test for end-to-end PDF text extraction using a generated PDF."""

import io
import os
import tempfile

import pymupdf as fitz

from parsedoc.extraction.text import extract_pdf_text


def test_extract_generated_pdf():
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Hello World")
    page.insert_text((50, 80), "Milk standards 63°C")
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as fh:
        fh.write(buf.getvalue())
        path = fh.name
    try:
        result = extract_pdf_text(path)
        assert result["page_count"] == 1
        assert "Hello World" in result["text"]
        assert "63°C" in result["text"]
    finally:
        os.unlink(path)
