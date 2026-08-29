"""Tests for PDF text-extraction artifact repair (no file I/O required)."""

from parsedoc.extraction.text import _fix_pdf_text_artifacts


def test_degree_sign_repair():
    assert _fix_pdf_text_artifacts("630 C") == "63°C"
    assert _fix_pdf_text_artifacts("71.50C") == "71.5°C"
    assert _fix_pdf_text_artifacts("1150 C") == "115°C"


def test_notmorethan_notlessthan():
    assert "Not more than" in _fix_pdf_text_artifacts("Notmorethan60.0")
    assert "Not less than" in _fix_pdf_text_artifacts("Notlessthan60.0percent")


def test_number_unit_spacing():
    assert _fix_pdf_text_artifacts("60.0percent") == "60.0 percent"


def test_ocr_typo_fixes():
    assert _fix_pdf_text_artifacts("hydorxide") == "hydroxide"
    assert _fix_pdf_text_artifacts("regulatiions") == "regulations"
    assert _fix_pdf_text_artifacts("Boudouins") == "Boudouin's"
    assert _fix_pdf_text_artifacts("rancidityand") == "rancidity and"
    assert _fix_pdf_text_artifacts("AssamBihar") == "Assam, Bihar"


def test_markup_artifact_cleanup():
    assert _fix_pdf_text_artifacts("$115^{0}C$") == "115°C"
    assert _fix_pdf_text_artifacts("$130^{0}c$ C") == "130°C"
    assert _fix_pdf_text_artifacts("N\\times6.25") == "N×6.25"
