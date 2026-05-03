"""Career role matcher: 3 role recommendations with match scores and skill gaps."""

from __future__ import annotations

import logging
from typing import Any

from core.llm_client import llm_call
from core.prompts import career_prompt

logger = logging.getLogger(__name__)

_FALLBACK_ROLES = [
    {
        "role_title": "Software Developer",
        "match_score": 65,
        "match_reasons": [
            "Technical background aligns with software development requirements",
            "Problem-solving skills transferable to engineering contexts",
            "Programming experience relevant to application development",
        ],
        "skill_gaps": [
            "System design and scalability fundamentals",
            "CI/CD pipeline setup and DevOps practices",
            "Cloud platform experience (AWS/GCP/Azure)",
        ],
        "time_to_ready": "2-3 months with focused upskilling",
        "recommended_project": "Build and deploy a full-stack web application with authentication, database, and REST API on a free cloud tier",
        "seniority_target": "Junior",
    },
    {
        "role_title": "Data Analyst",
        "match_score": 58,
        "match_reasons": [
            "Analytical mindset applicable to data interpretation",
            "Attention to detail supports accurate data reporting",
            "Communication skills valuable for presenting insights to stakeholders",
        ],
        "skill_gaps": [
            "SQL proficiency for complex data queries",
            "Python (pandas, numpy) for data manipulation",
            "Tableau or Power BI for business intelligence dashboards",
        ],
        "time_to_ready": "3-4 months with focused upskilling",
        "recommended_project": "Analyse a public dataset (e.g. Kaggle), produce a report with visualisations, and publish findings on GitHub",
        "seniority_target": "Junior",
    },
    {
        "role_title": "Product Manager",
        "match_score": 52,
        "match_reasons": [
            "Cross-functional experience aligns with PM coordination requirements",
            "Customer-facing background applicable to user research",
            "Organisational skills relevant to roadmap management",
        ],
        "skill_gaps": [
            "Agile/Scrum ceremonies and sprint planning",
            "Product analytics tools (Mixpanel, Amplitude)",
            "Stakeholder prioritisation frameworks (RICE, MoSCoW)",
        ],
        "time_to_ready": "4-6 months with networking and certification",
        "recommended_project": "Write and publicly share a product requirements document (PRD) for a real-world problem with user stories and success metrics",
        "seniority_target": "Junior",
    },
]


def _normalize_result_to_list(result: Any) -> list:
    """Normalize LLM output to a list of role dicts regardless of shape returned."""
    if isinstance(result, list):
        return result

    if isinstance(result, dict):
        # Single role object returned directly
        if "role_title" in result:
            return [result]

        # Wrapped in a key like {"roles": [...]} or {"career_matches": [...]}
        for key in ("roles", "career_matches", "careers", "results", "matches"):
            if key in result and isinstance(result[key], list):
                return result[key]

        # Try any list value in the dict
        for v in result.values():
            if isinstance(v, list) and len(v) > 0:
                return v

    raise ValueError(f"Cannot normalize LLM career result of type {type(result)}: {str(result)[:200]}")


async def run_career_matcher(
    resume_text: str, target_role: str = ""
) -> list[dict[str, Any]]:
    """
    Generate 3 career role recommendations via LLM.
    Falls back to generic roles if LLM fails.
    """
    prompt = career_prompt(resume_text, target_role)
    try:
        raw = await llm_call(prompt, prompt_type="career")
        result = _normalize_result_to_list(raw)

        roles = [_normalize_role(r) for r in result[:3]]

        # Pad to 3 if LLM returned fewer
        if len(roles) < 3:
            roles.extend(_FALLBACK_ROLES[len(roles):3])

        return roles

    except Exception as exc:
        logger.error("LLM career matcher failed, using fallback: %s", exc)
        if target_role.strip():
            fallback = list(_FALLBACK_ROLES)
            fallback[0] = {**fallback[0], "role_title": target_role, "match_score": 60}
            return fallback
        return _FALLBACK_ROLES


def _normalize_role(raw: dict[str, Any]) -> dict[str, Any]:
    score = int(raw.get("match_score", 50))
    score = max(0, min(100, score))

    reasons = raw.get("match_reasons", [])
    if not isinstance(reasons, list):
        reasons = []

    gaps = raw.get("skill_gaps", [])
    if not isinstance(gaps, list):
        gaps = []

    return {
        "role_title": str(raw.get("role_title", "Unknown Role")),
        "match_score": score,
        "match_reasons": reasons[:3],
        "skill_gaps": gaps[:3],
        "time_to_ready": str(raw.get("time_to_ready", "3-6 months")),
        "recommended_project": str(raw.get("recommended_project", "")),
        "seniority_target": str(raw.get("seniority_target", "Mid")),
    }