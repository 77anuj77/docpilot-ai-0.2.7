"""ParseDoc Pipeline orchestration (PRD #4, #11, #55)."""

import glob
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Dict, List, Optional

from ..ai import build_provider
from ..ai.base import AIProvider
from ..ai.prompts import PROMPT_VERSION, get_prompt
from ..ai import cache as ai_cache
from ..core.chunking import chunk_text
from ..core.config import Config
from ..core.detection import detect_format
from ..ocr import build_ocr_provider
from ..parsers import get_parser
from ..renderers import render
from ..schema.document import Document, SUPPORTED_BLOCK_TYPES
from ..schema.validation import validate_document
from ..utils.filesystem import validate_input_path
from ..utils.logging import setup_logging


def _parse_ai_document(text: str) -> Dict:
    """Extract a {title, blocks} dict from a (possibly fenced) AI response."""
    if not text:
        return {"title": "", "blocks": []}
    cleaned = text.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", cleaned, re.DOTALL)
    if fence:
        cleaned = fence.group(1).strip()
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start != -1 and end != -1:
            try:
                data = json.loads(cleaned[start : end + 1])
            except Exception:
                data = {}
        else:
            data = {}
    if not isinstance(data, dict):
        data = {}
    blocks = [
        b
        for b in data.get("blocks", [])
        if isinstance(b, dict) and b.get("type") in SUPPORTED_BLOCK_TYPES
    ]
    return {"title": data.get("title", "") or "", "blocks": blocks}


def _tables_context(tables: Optional[List]) -> str:
    if not tables:
        return ""
    parts: List[str] = []
    for i, tbl in enumerate(tables):
        rows = tbl if isinstance(tbl, list) else []
        parts.append(f"[Table {i + 1}]")
        for row in rows:
            parts.append(" | ".join(str(c) for c in row))
    return "\n".join(parts)


def _build_user_content(chunk: str, tables_ctx: str, idx: int, total: int) -> str:
    content = chunk
    if tables_ctx:
        content += (
            "\n\nThe following tables were extracted separately; preserve their "
            "values exactly:\n" + tables_ctx
        )
    if total > 1:
        content = f"[Part {idx}/{total}]\n" + content
    return content


class Pipeline:
    """Orchestrates the full ParseDoc conversion flow."""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.logger = setup_logging()

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def process(
        self,
        input_path: str,
        output_format: str = "markdown",
        mode: str = "hybrid",
        ai_provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
        ocr: bool = False,
        extract_images: bool = False,
        output_path: Optional[str] = None,
        tmpdir: Optional[str] = None,
    ) -> str:
        """Process a single document and return rendered output as a string."""
        doc = self.build(
            input_path,
            mode=mode,
            ai_provider=ai_provider,
            model=model,
            max_tokens=max_tokens,
            ocr=ocr,
            extract_images=extract_images,
            output_path=output_path,
        )
        return render(doc, output_format)

    def build(
        self,
        input_path: str,
        mode: str = "hybrid",
        ai_provider: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        ocr: bool = False,
        extract_images: bool = False,
        output_path: Optional[str] = None,
    ) -> Document:
        """Process a document and return the structured Document model."""
        if not validate_input_path(input_path):
            raise FileNotFoundError(f"Input file '{input_path}' not found")

        fmt = detect_format(input_path)
        if fmt == "unknown":
            raise ValueError(f"Unsupported format for '{input_path}'")

        parser = get_parser(fmt, self.config)
        extracted = parser.extract(input_path)

        quality = extracted.get("quality", {})
        needs_ocr = bool(ocr) or bool(quality.get("needs_ocr", False))
        if needs_ocr and self.config.ocr_enabled:
            extracted = self._apply_ocr(input_path, extracted, fmt)

        use_ai = self._should_use_ai(mode, ai_provider)
        if use_ai:
            try:
                doc = self._process_with_ai(extracted, ai_provider, model, max_tokens, fmt)
                if mode == "hybrid" and not doc.blocks:
                    self.logger.warning("AI returned no structured blocks; using local structure.")
                    doc = parser.to_document(extracted, input_path)
            except Exception as exc:  # noqa: BLE001 - fall back gracefully
                self.logger.warning("AI processing failed (%s); using local structure.", exc)
                doc = parser.to_document(extracted, input_path)
        else:
            doc = parser.to_document(extracted, input_path)

        if extract_images and fmt == "docx":
            doc = self._attach_docx_images(doc, input_path, output_path)
        return doc

    def _attach_docx_images(
        self, doc: Document, input_path: str, output_path: Optional[str]
    ) -> Document:
        from ..extraction.images import extract_docx_images

        base = Path(output_path) if output_path else Path(input_path)
        assets_name = f"{base.stem}_assets"
        assets_dir = str(base.parent / assets_name)
        refs = extract_docx_images(input_path, assets_dir)
        if not refs:
            return doc
        image_blocks = [
            {
                "type": "image",
                "src": f"{assets_name}/{os.path.basename(r['src'])}",
                "alt": r.get("alt", ""),
            }
            for r in refs
        ]
        data = doc.model_dump()
        data["blocks"] = data["blocks"] + image_blocks
        return validate_document(data)

    def process_batch(self, directory: str, pattern: str = "*.*", **kwargs) -> Dict[str, str]:
        """Process all files in ``directory`` matching ``pattern``."""
        files = glob.glob(os.path.join(directory, pattern))
        results: Dict[str, str] = {}
        for file_path in files:
            try:
                results[file_path] = self.process(file_path, **kwargs)
            except Exception as e:
                self.logger.error(f"Failed to process {file_path}: {e}")
                results[file_path] = f"ERROR: {e}"
        return results

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    def _should_use_ai(self, mode: str, ai_provider: Optional[str]) -> bool:
        if mode == "local":
            return False
        if mode == "ai":
            return True
        if ai_provider:
            return True
        return bool(self.config.ai_enabled) and self.config.ai_provider not in (
            None,
            "none",
        )

    def _apply_ocr(self, input_path: str, extracted: Dict, fmt: str) -> Dict:
        try:
            provider = build_ocr_provider(self.config.ocr_provider)
        except Exception as exc:  # noqa: BLE001
            self.logger.warning("OCR provider unavailable (%s).", exc)
            return extracted

        existing = (extracted.get("text", "") or "").strip()
        try:
            if fmt == "pdf":
                ocr_text = self._ocr_pdf(input_path, provider)
                if ocr_text.strip() and len(ocr_text.strip()) > len(existing):
                    extracted["text"] = ocr_text
                    extracted["needs_ocr"] = False
                    if isinstance(extracted.get("quality"), dict):
                        extracted["quality"]["needs_ocr"] = False
            elif not existing:
                extracted["text"] = provider.ocr(input_path)
                extracted["needs_ocr"] = False
        except Exception as exc:  # noqa: BLE001
            self.logger.warning("OCR failed: %s", exc)
        return extracted

    def _ocr_pdf(self, input_path: str, provider) -> str:
        try:
            import pymupdf as fitz
        except ImportError:
            import fitz  # PyMuPDF

        pages: List[str] = []
        with fitz.open(input_path) as doc:
            for page in doc:
                pix = page.get_pixmap(dpi=self.config.ocr_dpi)
                tmp_name = None
                try:
                    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
                        pix.save(tf.name)
                        tmp_name = tf.name
                    pages.append(provider.ocr(tmp_name))
                finally:
                    if tmp_name and os.path.exists(tmp_name):
                        os.unlink(tmp_name)
        return "\n\n".join(pages)

    def _process_with_ai(
        self,
        extracted: Dict,
        ai_provider: Optional[str],
        model: Optional[str],
        max_tokens: Optional[int],
        fmt: str,
    ) -> Document:
        provider_name = ai_provider or self.config.ai_provider or "openai-compatible"
        provider: AIProvider = build_provider(
            provider=provider_name,
            base_url=self.config.base_url,
            model=model or self.config.model,
            api_key=self.config.api_key,
        )
        if provider is None or not provider.is_available():
            raise RuntimeError(f"AI provider '{provider_name}' is not available.")

        prompt = get_prompt("document_structure")
        text = extracted.get("text", "") or ""
        tables_ctx = _tables_context(extracted.get("tables"))
        title = extracted.get("title", "") or ""
        max_chars = max_tokens or self.config.max_tokens or 4096
        chunks = chunk_text(text, max_chars) if text.strip() else [""]

        blocks: List[Dict] = []
        for idx, chunk in enumerate(chunks):
            user = _build_user_content(chunk, tables_ctx, idx + 1, len(chunks))
            if self.config.cache_enabled:
                cache_cfg = self.config.to_dict()
                cached = ai_cache.lookup(user, provider.model, PROMPT_VERSION, cache_cfg)
                if cached is not None:
                    raw = cached
                else:
                    raw = provider.generate(prompt, user)
                    ai_cache.store(user, provider.model, PROMPT_VERSION, cache_cfg, raw)
            else:
                raw = provider.generate(prompt, user)
            data = _parse_ai_document(raw)
            if data["title"] and not title:
                title = data["title"]
            blocks.extend(data["blocks"])

        return validate_document(
            {
                "title": title,
                "blocks": blocks,
                "metadata": {
                    "source": extracted.get("source", ""),
                    "format": fmt,
                    "pages": extracted.get("page_count"),
                    "ai_provider": provider.name,
                    "ai_model": provider.model,
                },
            }
        )
