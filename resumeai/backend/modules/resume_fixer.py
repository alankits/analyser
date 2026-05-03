"""Resume fix generator: STAR rewrites, action verb checks, section analysis."""

from __future__ import annotations

import logging
from typing import Any

from core.llm_client import llm_call
from core.prompts import fix_prompt

logger = logging.getLogger(__name__)


async def run_resume_fixer(
    resume_text: str, job_description: str = ""
) -> list[dict[str, Any]]:
    """
    Generate section-by-section resume fixes via LLM.
    Falls back to heuristic fixes if LLM fails.
    """
    prompt = fix_prompt(resume_text, job_description)
    try:
        result = await llm_call(prompt, prompt_type="fix")

        # LLM sometimes returns a single dict instead of a list — normalize it
        if isinstance(result, dict):
            # Could be a wrapped response like {"sections": [...]} or a single section
            if "sections" in result and isinstance(result["sections"], list):
                result = result["sections"]
            elif "section_name" in result:
                # Single section object returned — wrap it in a list
                result = [result]
            elif "fixes" in result:
                result = [result]
            else:
                # Try to extract any list value from the dict
                for v in result.values():
                    if isinstance(v, list) and len(v) > 0:
                        result = v
                        break
                else:
                    raise ValueError(f"Unexpected dict structure from LLM: {list(result.keys())}")

        if not isinstance(result, list):
            raise ValueError(f"LLM returned unexpected type: {type(result)}")

        if len(result) == 0:
            raise ValueError("LLM returned empty list for resume fixes")

        return [_normalize_fix_section(section) for section in result]

    except Exception as exc:
        logger.error("LLM resume fixer failed: %s", exc)
        return _heuristic_fixes(resume_text)


def _normalize_fix_section(raw: dict[str, Any]) -> dict[str, Any]:
    """Ensure all required fields present with correct types."""
    fixes = raw.get("fixes", [])
    if not isinstance(fixes, list):
        fixes = []

    normalized_fixes = []
    for fix in fixes:
        if isinstance(fix, dict):
            normalized_fixes.append(
                {
                    "original": str(fix.get("original", "")),
                    "rewritten": str(fix.get("rewritten", "")),
                    "reason": str(fix.get("reason", "Improved clarity and impact")),
                }
            )

    return {
        "section_name": str(raw.get("section_name", "Unknown")),
        "issues": raw.get("issues", []) if isinstance(raw.get("issues"), list) else [],
        "fixes": normalized_fixes,
        "missing_elements": (
            raw.get("missing_elements", [])
            if isinstance(raw.get("missing_elements"), list)
            else []
        ),
    }


def _heuristic_fixes(resume_text: str) -> list[dict[str, Any]]:
    """Minimal fallback when LLM is unavailable."""
    import re

    sections: list[dict[str, Any]] = []
    issues: list[str] = []

    lines = resume_text.split("\n")
    weak_bullets = [
        line.strip()
        for line in lines
        if line.strip().startswith("-") and len(line.strip()) < 60
    ]
    if weak_bullets:
        issues.append("Several bullet points are too short and lack quantified outcomes")

    passive_pattern = re.compile(
        r"\b(responsible for|assisted with|helped|was involved in|worked on)\b",
        re.IGNORECASE,
    )
    passive_bullets = [line.strip() for line in lines if passive_pattern.search(line)]
    if passive_bullets:
        issues.append("Passive language detected - use strong action verbs instead")

    sections.append(
        {
            "section_name": "General",
            "issues": issues if issues else ["Resume analysis requires AI processing - please retry"],
            "fixes": [],
            "missing_elements": [],
        }
    )
    return sections