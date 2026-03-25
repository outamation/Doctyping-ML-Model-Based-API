"""
Extracts per-page text from raw PDF bytes using PyMuPDF (fitz).
Not ML-specific — used by both the dev test endpoint and any future pipeline.
"""
import re

import fitz

MIN_TEXT_CHARS = 30


def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def extract_pages_from_bytes(pdf_bytes: bytes) -> list[dict]:
    """
    Returns list of {"page_number": int, "text": str}
    for pages with at least MIN_TEXT_CHARS of content.
    """
    pages = []
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    try:
        for i in range(len(doc)):
            txt = _clean(doc.load_page(i).get_text("text"))
            if len(txt) >= MIN_TEXT_CHARS:
                pages.append({"page_number": i + 1, "text": txt})
    finally:
        doc.close()
    return pages
