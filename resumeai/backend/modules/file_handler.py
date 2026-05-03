"""File upload handler: validation, temp storage, MIME detection."""

from __future__ import annotations

import logging
import mimetypes
import os
import tempfile
import uuid
from pathlib import Path

from fastapi import UploadFile, HTTPException

from core.config import settings

logger = logging.getLogger(__name__)

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
ALLOWED_EXTENSIONS = {".pdf", ".docx"}
TEMP_DIR = Path(tempfile.gettempdir()) / "resumeai_uploads"


def _ensure_temp_dir() -> None:
    TEMP_DIR.mkdir(parents=True, exist_ok=True)


def _detect_file_type(filename: str, content_type: str) -> str:
    """Return 'pdf' or 'docx', or raise HTTPException."""
    ext = Path(filename).suffix.lower()
    mime = content_type.lower() if content_type else ""

    if ext == ".pdf" or "pdf" in mime:
        return "pdf"
    if ext == ".docx" or "wordprocessingml" in mime or "openxmlformats" in mime:
        return "docx"

    # Fall back to mimetypes guess from filename
    guessed, _ = mimetypes.guess_type(filename)
    if guessed:
        if "pdf" in guessed:
            return "pdf"
        if "wordprocessingml" in guessed:
            return "docx"

    raise HTTPException(
        status_code=415,
        detail="Unsupported file type. Please upload a PDF or DOCX file.",
    )


async def save_upload(upload: UploadFile) -> tuple[Path, str]:
    """
    Validate and save an uploaded file to a temp path.

    Returns:
        (temp_path, file_type)  where file_type is 'pdf' or 'docx'

    Raises:
        HTTPException 413 if file exceeds size limit
        HTTPException 415 if file type is unsupported
    """
    _ensure_temp_dir()

    file_type = _detect_file_type(upload.filename or "", upload.content_type or "")

    content = await upload.read()
    if len(content) > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=413,
            detail=(
                f"File size exceeds the {settings.max_file_size_mb} MB limit. "
                f"Received {len(content) / (1024 * 1024):.1f} MB."
            ),
        )

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    unique_name = f"{uuid.uuid4().hex}.{file_type}"
    temp_path = TEMP_DIR / unique_name

    temp_path.write_bytes(content)
    logger.info(
        "Saved upload: filename=%s size=%d bytes path=%s",
        upload.filename,
        len(content),
        temp_path,
    )

    return temp_path, file_type


def cleanup_file(path: Path) -> None:
    """Remove a temp file, logging any errors without raising."""
    try:
        if path.exists():
            os.remove(path)
            logger.debug("Cleaned up temp file: %s", path)
    except Exception as exc:
        logger.warning("Failed to clean up temp file %s: %s", path, exc)
