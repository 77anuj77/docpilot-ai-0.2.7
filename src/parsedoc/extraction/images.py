"""ParseDoc Image Extraction helpers"""

import os


def extract_pdf_images(pdf_path: str) -> list:
    """Return a list of image references (page + xref) from a PDF."""
    import fitz  # PyMuPDF

    images = []
    with fitz.open(pdf_path) as doc:
        for page_num in range(doc.page_count):
            for img in doc[page_num].get_images(full=True):
                images.append({"page": page_num + 1, "xref": img[0]})
    return images


def save_pdf_image(pdf_path: str, xref: int, out_path: str) -> bool:
    """Save a single PDF image (by xref) to ``out_path``."""
    import fitz  # PyMuPDF

    try:
        with fitz.open(pdf_path) as doc:
            pix = fitz.Pixmap(doc, xref)
            if pix.n - pix.alpha >= 4:  # CMYK -> RGB
                pix = fitz.Pixmap(fitz.csRGB, pix)
            pix.save(out_path)
        return True
    except Exception:
        return False


def extract_docx_images(docx_path: str, assets_dir: str) -> list:
    """Save embedded DOCX images to ``assets_dir`` and return reference dicts.

    Each reference has ``src`` (absolute path on disk) and ``alt``. The caller
    is responsible for converting ``src`` to a path relative to the output
    document before rendering.
    """
    from docx import Document

    os.makedirs(assets_dir, exist_ok=True)
    doc = Document(docx_path)
    refs: list = []

    try:
        for i, shape in enumerate(doc.inline_shapes, 1):
            try:
                blip = shape._inline.graphic.graphicData.pic.blipFill.blip
                rId = blip.embed
                part = doc.part.related_parts[rId]
                ext = _image_ext(part)
                fname = f"image-{i:03d}.{ext}"
                with open(os.path.join(assets_dir, fname), "wb") as fh:
                    fh.write(part.blob)
                refs.append({"src": os.path.join(assets_dir, fname), "alt": f"Image {i}"})
            except Exception:
                continue
    except Exception:
        pass

    if refs:
        return refs

    # Fallback: pull every image relationship regardless of position.
    idx = 1
    for rel in doc.part.rels.values():
        if "image" in rel.reltype:
            try:
                part = rel.target_part
                ext = _image_ext(part)
                fname = f"image-{idx:03d}.{ext}"
                with open(os.path.join(assets_dir, fname), "wb") as fh:
                    fh.write(part.blob)
                refs.append({"src": os.path.join(assets_dir, fname), "alt": f"Image {idx}"})
                idx += 1
            except Exception:
                continue
    return refs


_CONTENT_TYPE_EXT = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/gif": "gif",
    "image/bmp": "bmp",
    "image/tiff": "tiff",
    "image/x-emf": "emf",
    "image/x-wmf": "wmf",
    "image/svg+xml": "svg",
}


def _image_ext(part) -> str:
    """Best-effort image extension from an OOXML part."""
    ext = getattr(part, "ext", None)
    if ext:
        return ext.lower().lstrip(".")
    ct = getattr(part, "content_type", "") or ""
    return _CONTENT_TYPE_EXT.get(ct, "png")
