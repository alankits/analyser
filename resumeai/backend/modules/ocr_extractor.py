"""OCR fallback for scanned PDFs using pytesseract + Pillow."""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def extract_text_via_ocr(path: Path) -> str:
    """
    Convert each PDF page to an image and run Tesseract OCR.
    Requires: poppler-utils (pdf2image) and tesseract-ocr system packages.
    """
    try:
        from pdf2image import convert_from_path  # type: ignore
        import pytesseract  # type: ignore
    except ImportError as exc:
        logger.warning("OCR dependencies not available: %s", exc)
        return ""

    try:
        images = convert_from_path(str(path), dpi=300)
        logger.info("OCR: converted %d pages from PDF", len(images))
    except Exception as exc:
        logger.warning("pdf2image conversion failed: %s", exc)
        return ""

    texts: list[str] = []
    for i, image in enumerate(images):
        try:
            text = pytesseract.image_to_string(image, lang="eng")
            texts.append(text)
            logger.debug("OCR page %d: %d chars", i + 1, len(text))
        except Exception as exc:
            logger.warning("Tesseract failed on page %d: %s", i + 1, exc)

    result = "\n".join(texts)
    logger.info("OCR total extracted: %d chars", len(result))
    return result
