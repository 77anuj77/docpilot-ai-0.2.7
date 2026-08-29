"""Tests for renderer output across Markdown / JSON / HTML / Text formats."""

import json

from parsedoc.schema.document import Block, Document
from parsedoc.renderers.markdown import render_markdown
from parsedoc.renderers import json as rj
from parsedoc.renderers import html as rh
from parsedoc.renderers import text as rt


def _doc_with_table():
    blocks = [
        Block(type="heading", level=1, text="Sample"),
        Block(type="paragraph", text="Intro paragraph."),
        Block(type="table", headers=["A", "B"], rows=[["1", "2"], ["3", "4"]]),
    ]
    return Document(title="T", blocks=blocks, metadata={})


def test_markdown_renders_table():
    md = render_markdown(_doc_with_table())
    assert "| A | B |" in md
    assert "Sample" in md


def test_json_renders_table():
    data = json.loads(rj.render_json(_doc_with_table()))
    tables = [b for b in data["blocks"] if b["type"] == "table"]
    assert tables and tables[0]["headers"] == ["A", "B"]


def test_html_renders_table():
    html = rh.render_html(_doc_with_table())
    assert "<table>" in html
    assert "<th>A</th>" in html


def test_text_renders_content():
    txt = rt.render_text(_doc_with_table())
    assert "Sample" in txt
    assert "Intro paragraph." in txt
