"""POST /analyze — runs all 4 AI analysis modules and returns unified response."""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Form, Request, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import limiter
from models.database import get_db
from models.orm_models import AnalysisRecord
from models.schemas import AnalysisData, AnalysisResponse, ErrorResponse
from modules.ats_scorer import run_ats_scoring
from modules.career_matcher import run_career_matcher
from modules.file_handler import cleanup_file, save_upload
from modules.resume_fixer import run_resume_fixer
from modules.roadmap_generator import run_roadmap_generator
from modules.text_cleaner import clean_text, extract_candidate_name
from modules.text_extractor import extract_text

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/analyze", response_model=AnalysisResponse)
@limiter.limit("10/minute")
async def analyze_resume(
    request: Request,
    file: UploadFile = File(..., description="Resume file (PDF or DOCX, max 5 MB)"),
    target_role: str = Form(default=""),
    job_description: str = Form(default=""),
    db: AsyncSession = Depends(get_db),
) -> AnalysisResponse:
    """
    Upload a resume and receive a full AI-powered analysis:
    - ATS score with keyword breakdown
    - Section-by-section BEFORE/AFTER fixes
    - 3 career role recommendations
    - Personalised 3-phase learning roadmap
    """
    temp_path = None
    try:
        # 1. Save and validate upload
        temp_path, file_type = await save_upload(file)

        # 2. Extract text
        raw_text = extract_text(temp_path, file_type)
        if not raw_text.strip():
            raise HTTPException(
                status_code=422,
                detail="Could not extract readable text from the uploaded file. "
                       "Ensure the file is not password-protected or fully image-based.",
            )

        # 3. Clean text
        cleaned_text = clean_text(raw_text)
        candidate_name = extract_candidate_name(cleaned_text)

        # 4. Run all 4 analysis modules concurrently
        import asyncio

        ats_task = asyncio.create_task(
            run_ats_scoring(cleaned_text, job_description)
        )
        fix_task = asyncio.create_task(
            run_resume_fixer(cleaned_text, job_description)
        )
        career_task = asyncio.create_task(
            run_career_matcher(cleaned_text, target_role)
        )

        ats_result, resume_fixes, career_matches = await asyncio.gather(
            ats_task, fix_task, career_task, return_exceptions=True
        )

        # Handle partial failures gracefully
        if isinstance(ats_result, Exception):
            logger.error("ATS scoring failed: %s", ats_result)
            ats_result = {
                "overall_score": 0, "grade": "F", "keyword_analysis": [],
                "section_scores": {"summary": 0, "experience": 0, "skills": 0, "education": 0, "projects": 0},
                "missing_sections": [], "top_issues": ["Analysis unavailable — please retry"],
            }

        if isinstance(resume_fixes, Exception):
            logger.error("Resume fixer failed: %s", resume_fixes)
            resume_fixes = []

        if isinstance(career_matches, Exception):
            logger.error("Career matcher failed: %s", career_matches)
            career_matches = []

        # 5. Extract skill gaps for roadmap (from first career match)
        skill_gaps: list[str] = []
        if career_matches and isinstance(career_matches, list) and len(career_matches) > 0:
            skill_gaps = career_matches[0].get("skill_gaps", [])

        effective_target_role = (
            target_role.strip()
            or (career_matches[0].get("role_title", "") if career_matches else "")
            or "Software Professional"
        )

        roadmap = await run_roadmap_generator(cleaned_text, effective_target_role, skill_gaps)

        # 6. Persist to database
        analysis_id = str(uuid.uuid4())
        record = AnalysisRecord(
            id=analysis_id,
            candidate_name=candidate_name,
            target_role=effective_target_role,
            ats_result_json=json.dumps(ats_result),
            resume_fixes_json=json.dumps(resume_fixes),
            career_matches_json=json.dumps(career_matches),
            roadmap_json=json.dumps(roadmap),
        )
        db.add(record)
        await db.commit()

        logger.info(
            "Analysis complete: id=%s candidate=%s score=%s",
            analysis_id,
            candidate_name,
            ats_result.get("overall_score"),
        )

        # 7. Build and validate response
        from pydantic import TypeAdapter
        from models.schemas import ATSResult, CareerRole, ResumeSectionFix, Roadmap

        def _parse_safely(model_class, data):
            try:
                if isinstance(data, list):
                    adapter = TypeAdapter(list[model_class])
                    return adapter.validate_python(data)
                return model_class.model_validate(data)
            except Exception as e:
                logger.warning("Schema validation warning for %s: %s", model_class.__name__, e)
                if isinstance(data, list):
                    return []
                return model_class.model_validate({})

        ats_validated = ATSResult.model_validate(ats_result)
        fixes_validated = [ResumeSectionFix.model_validate(f) for f in (resume_fixes or [])]
        careers_validated = [CareerRole.model_validate(c) for c in (career_matches or [])]
        roadmap_validated = Roadmap.model_validate(roadmap)

        return AnalysisResponse(
            success=True,
            data=AnalysisData(
                analysis_id=analysis_id,
                candidate_name=candidate_name,
                ats_result=ats_validated,
                resume_fixes=fixes_validated,
                career_matches=careers_validated,
                roadmap=roadmap_validated,
                created_at=datetime.utcnow(),
            ),
            error=None,
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unexpected error in /analyze: %s", exc)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(exc)}")
    finally:
        if temp_path:
            cleanup_file(temp_path)
