"""GET /analysis/{id} — retrieve a stored analysis by ID."""

from __future__ import annotations

import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import get_db
from models.orm_models import AnalysisRecord
from models.schemas import AnalysisData, AnalysisResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/analysis/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: str,
    db: AsyncSession = Depends(get_db),
) -> AnalysisResponse:
    """Retrieve a previously completed analysis by its ID."""
    result = await db.execute(
        select(AnalysisRecord).where(AnalysisRecord.id == analysis_id)
    )
    record: AnalysisRecord | None = result.scalar_one_or_none()

    if record is None:
        raise HTTPException(
            status_code=404,
            detail=f"Analysis {analysis_id!r} not found.",
        )

    try:
        ats_result = json.loads(record.ats_result_json)
        resume_fixes = json.loads(record.resume_fixes_json)
        career_matches = json.loads(record.career_matches_json)
        roadmap_data = json.loads(record.roadmap_json)
    except (json.JSONDecodeError, TypeError) as exc:
        logger.error("Corrupt analysis data id=%s: %s", analysis_id, exc)
        raise HTTPException(status_code=500, detail="Stored analysis data is corrupted.")

    from models.schemas import ATSResult, CareerRole, ResumeSectionFix, Roadmap
    from datetime import datetime

    return AnalysisResponse(
        success=True,
        data=AnalysisData(
            analysis_id=record.id,
            candidate_name=record.candidate_name or "Candidate",
            ats_result=ATSResult.model_validate(ats_result),
            resume_fixes=[ResumeSectionFix.model_validate(f) for f in resume_fixes],
            career_matches=[CareerRole.model_validate(c) for c in career_matches],
            roadmap=Roadmap.model_validate(roadmap_data),
            created_at=record.created_at or datetime.utcnow(),
        ),
        error=None,
    )
