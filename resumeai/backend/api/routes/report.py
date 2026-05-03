"""GET /report/{id} — generate and stream the PDF report."""

from __future__ import annotations

import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import get_db
from models.orm_models import AnalysisRecord
from modules.report_builder import generate_pdf_report

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/report/{analysis_id}")
async def download_report(
    analysis_id: str,
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """
    Generate and stream a multi-page PDF report for a completed analysis.
    """
    result = await db.execute(
        select(AnalysisRecord).where(AnalysisRecord.id == analysis_id)
    )
    record: AnalysisRecord | None = result.scalar_one_or_none()

    if record is None:
        raise HTTPException(status_code=404, detail=f"Analysis {analysis_id!r} not found.")

    try:
        ats_result = json.loads(record.ats_result_json)
        resume_fixes = json.loads(record.resume_fixes_json)
        career_matches = json.loads(record.career_matches_json)
        roadmap = json.loads(record.roadmap_json)
    except (json.JSONDecodeError, TypeError) as exc:
        logger.error("Failed to deserialize analysis data for id=%s: %s", analysis_id, exc)
        raise HTTPException(status_code=500, detail="Stored analysis data is corrupted.")

    try:
        pdf_bytes = generate_pdf_report(
            candidate_name=record.candidate_name or "Candidate",
            ats_result=ats_result,
            resume_fixes=resume_fixes,
            career_matches=career_matches,
            roadmap=roadmap,
        )
    except Exception as exc:
        logger.exception("PDF generation failed for id=%s: %s", analysis_id, exc)
        raise HTTPException(status_code=500, detail="Failed to generate PDF report.")

    safe_name = (record.candidate_name or "resume").replace(" ", "_")
    filename = f"ResumeAI_{safe_name}_Report.pdf"

    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
