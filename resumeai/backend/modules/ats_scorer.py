"""ATS scoring: keyword extraction, section detection, and composite scoring."""

from __future__ import annotations

import logging
import re
from typing import Any

from core.llm_client import llm_call
from core.prompts import ats_prompt

logger = logging.getLogger(__name__)


async def run_ats_scoring(
    resume_text: str, job_description: str = ""
) -> dict[str, Any]:
    """
    Run ATS analysis via LLM and return the structured result.
    Falls back to a rule-based score if LLM call fails.
    """
    prompt = ats_prompt(resume_text, job_description)
    try:
        result = await llm_call(prompt, prompt_type="ats")
        if not isinstance(result, dict):
            raise ValueError("LLM returned non-dict for ATS")
        return _normalize_ats_result(result)
    except Exception as exc:
        logger.error("LLM ATS scoring failed, using heuristic fallback: %s", exc)
        return _heuristic_ats_score(resume_text, job_description)


def _normalize_ats_result(raw: dict[str, Any]) -> dict[str, Any]:
    """Ensure all required fields are present with correct types."""
    score = int(raw.get("overall_score", 50))
    score = max(0, min(100, score))
    keyword_analysis = raw.get("keyword_analysis", [])
    if not isinstance(keyword_analysis, list):
        keyword_analysis = []

    section_scores = raw.get("section_scores", {})
    if not isinstance(section_scores, dict):
        section_scores = {}

    for section in ["summary", "experience", "skills", "education", "projects"]:
        if section not in section_scores:
            section_scores[section] = 0

    return {
        "overall_score": score,
        "grade": _score_to_grade(score),
        "keyword_analysis": keyword_analysis[:30],  # cap at 30 keywords
        "section_scores": section_scores,
        "missing_sections": raw.get("missing_sections", []),
        "top_issues": raw.get("top_issues", [])[:5],
    }


def _score_to_grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    if score >= 45:
        return "D"
    return "F"


def _heuristic_ats_score(resume_text: str, job_description: str) -> dict[str, Any]:
    """Rule-based fallback scoring when LLM is unavailable."""
    text_lower = resume_text.lower()
    sections = {
        "summary": bool(re.search(r"\b(summary|profile|objective|about)\b", text_lower)),
        "experience": bool(re.search(r"\b(experience|work|employment|career)\b", text_lower)),
        "skills": bool(re.search(r"\b(skills|technologies|technical)\b", text_lower)),
        "education": bool(re.search(r"\b(education|degree|university|college|bachelor|master)\b", text_lower)),
        "projects": bool(re.search(r"\b(projects|portfolio|github)\b", text_lower)),
    }

    section_completeness = sum(sections.values()) / len(sections)
    quantified = len(re.findall(r"\b\d+[\%\$]|\b\d+\s*(percent|million|thousand|users|customers)\b", text_lower))
    quant_score = min(quantified / 5, 1.0)

    keyword_coverage = 0.5  # neutral without JD
    if job_description:
        jd_words = set(re.findall(r"\b[a-z]{3,}\b", job_description.lower()))
        resume_words = set(re.findall(r"\b[a-z]{3,}\b", text_lower))
        common = jd_words & resume_words
        keyword_coverage = len(common) / max(len(jd_words), 1)
        keyword_coverage = min(keyword_coverage, 1.0)

    composite = (
        keyword_coverage * 40
        + section_completeness * 30
        + quant_score * 20
        + 0.5 * 10  # neutral formatting
    )
    score = int(composite)

    missing = [s.capitalize() for s, present in sections.items() if not present]
    issues = []
    if not sections["summary"]:
        issues.append("Missing a professional summary section")
    if quantified < 2:
        issues.append("Very few quantified achievements — add metrics and numbers")
    if not sections["projects"]:
        issues.append("No projects section found — add relevant work samples")

    return {
        "overall_score": score,
        "grade": _score_to_grade(score),
        "keyword_analysis": [],
        "section_scores": {
            s: (80 if present else 20) for s, present in sections.items()
        },
        "missing_sections": missing,
        "top_issues": issues[:5],
    }
