"""Personalised 3-phase learning roadmap generator."""

from __future__ import annotations

import logging
from typing import Any

from core.llm_client import llm_call
from core.prompts import roadmap_prompt

logger = logging.getLogger(__name__)


async def run_roadmap_generator(
    resume_text: str,
    target_role: str,
    skill_gaps: list[str],
) -> dict[str, Any]:
    """
    Generate a 3-phase personalised learning roadmap via LLM.
    Falls back to a generic roadmap structure if LLM fails.
    """
    prompt = roadmap_prompt(resume_text, target_role, skill_gaps)
    try:
        result = await llm_call(prompt, prompt_type="roadmap")
        if not isinstance(result, dict):
            raise ValueError("LLM returned non-dict for roadmap")
        return _normalize_roadmap(result, target_role)
    except Exception as exc:
        logger.error("LLM roadmap generator failed: %s", exc)
        return _fallback_roadmap(target_role, skill_gaps)


def _normalize_roadmap(raw: dict[str, Any], target_role: str) -> dict[str, Any]:
    phases = raw.get("phases", [])
    if not isinstance(phases, list):
        phases = []

    normalized_phases = []
    for phase in phases[:3]:
        skills = phase.get("skills", [])
        if not isinstance(skills, list):
            skills = []

        normalized_skills = []
        for skill in skills:
            if isinstance(skill, dict):
                normalized_skills.append(
                    {
                        "skill_name": str(skill.get("skill_name", "")),
                        "why_it_matters": str(skill.get("why_it_matters", "")),
                        "resource_type": str(skill.get("resource_type", "online course")),
                        "estimated_hours": int(skill.get("estimated_hours", 10)),
                    }
                )

        normalized_phases.append(
            {
                "phase_number": int(phase.get("phase_number", len(normalized_phases) + 1)),
                "duration": str(phase.get("duration", "1 month")),
                "goal": str(phase.get("goal", "")),
                "skills": normalized_skills,
                "milestone": str(phase.get("milestone", "")),
            }
        )

    total_hours = sum(
        skill["estimated_hours"]
        for phase in normalized_phases
        for skill in phase["skills"]
    )

    return {
        "target_role": str(raw.get("target_role", target_role)),
        "current_level": str(raw.get("current_level", "Mid")),
        "phases": normalized_phases,
        "total_estimated_hours": int(raw.get("total_estimated_hours", total_hours)),
    }


def _fallback_roadmap(target_role: str, skill_gaps: list[str]) -> dict[str, Any]:
    """Generic 3-phase roadmap used when LLM is unavailable."""
    gap_skills = skill_gaps[:2] if skill_gaps else ["Core technical skills", "Domain knowledge"]

    return {
        "target_role": target_role or "Software Professional",
        "current_level": "Mid",
        "phases": [
            {
                "phase_number": 1,
                "duration": "0-30 days",
                "goal": f"Build foundational skills for the {target_role or 'target'} role with zero prerequisites",
                "skills": [
                    {
                        "skill_name": gap_skills[0] if gap_skills else "Core Fundamentals",
                        "why_it_matters": f"Essential baseline for success as a {target_role or 'professional'} in any team",
                        "resource_type": "official docs",
                        "estimated_hours": 20,
                    }
                ],
                "milestone": "Complete 3 hands-on exercises and publish to a public GitHub repository",
            },
            {
                "phase_number": 2,
                "duration": "1-3 months",
                "goal": f"Build on Phase 1 foundations with intermediate {target_role or 'domain'} skills",
                "skills": [
                    {
                        "skill_name": gap_skills[1] if len(gap_skills) > 1 else "Advanced Techniques",
                        "why_it_matters": f"Directly required for mid-level {target_role or 'role'} responsibilities",
                        "resource_type": "project-based course",
                        "estimated_hours": 40,
                    }
                ],
                "milestone": "Deploy a working project that demonstrates Phase 1 + Phase 2 skills end-to-end",
            },
            {
                "phase_number": 3,
                "duration": "3-6 months",
                "goal": "Assemble a portfolio and prepare for technical interviews",
                "skills": [
                    {
                        "skill_name": "Portfolio Project Development",
                        "why_it_matters": f"Interviewers for {target_role or 'technical'} roles expect a live demonstrable project",
                        "resource_type": "open source contribution",
                        "estimated_hours": 60,
                    }
                ],
                "milestone": "Publish a complete project with README, live demo, and architecture documentation",
            },
        ],
        "total_estimated_hours": 120,
    }
