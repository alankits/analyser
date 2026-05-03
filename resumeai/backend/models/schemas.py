"""Pydantic v2 request/response schemas for all API endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ─── ATS Result ───────────────────────────────────────────────────────────────


class KeywordItem(BaseModel):
    keyword: str
    present: bool
    importance: str  # "high" | "medium" | "low"


class SectionScores(BaseModel):
    summary: int = Field(ge=0, le=100)
    experience: int = Field(ge=0, le=100)
    skills: int = Field(ge=0, le=100)
    education: int = Field(ge=0, le=100)
    projects: int = Field(ge=0, le=100)


class ATSResult(BaseModel):
    overall_score: int = Field(ge=0, le=100)
    grade: str
    keyword_analysis: list[KeywordItem]
    section_scores: SectionScores
    missing_sections: list[str]
    top_issues: list[str]


# ─── Resume Fix ───────────────────────────────────────────────────────────────


class FixItem(BaseModel):
    original: str
    rewritten: str
    reason: str


class ResumeSectionFix(BaseModel):
    section_name: str
    issues: list[str]
    fixes: list[FixItem]
    missing_elements: list[str]


# ─── Career Match ─────────────────────────────────────────────────────────────


class CareerRole(BaseModel):
    role_title: str
    match_score: int = Field(ge=0, le=100)
    match_reasons: list[str]
    skill_gaps: list[str]
    time_to_ready: str
    recommended_project: str
    seniority_target: str


# ─── Roadmap ──────────────────────────────────────────────────────────────────


class SkillItem(BaseModel):
    skill_name: str
    why_it_matters: str
    resource_type: str
    estimated_hours: int


class RoadmapPhase(BaseModel):
    phase_number: int
    duration: str
    goal: str
    skills: list[SkillItem]
    milestone: str


class Roadmap(BaseModel):
    target_role: str
    current_level: str
    phases: list[RoadmapPhase]
    total_estimated_hours: int


# ─── Unified Analysis Response ────────────────────────────────────────────────


class AnalysisData(BaseModel):
    analysis_id: str
    candidate_name: str
    ats_result: ATSResult
    resume_fixes: list[ResumeSectionFix]
    career_matches: list[CareerRole]
    roadmap: Roadmap
    created_at: datetime


class AnalysisResponse(BaseModel):
    success: bool
    data: Optional[AnalysisData] = None
    error: Optional[str] = None


class ErrorResponse(BaseModel):
    success: bool = False
    data: None = None
    error: str


# ─── Health Check ─────────────────────────────────────────────────────────────


class HealthStatus(BaseModel):
    status: str  # "healthy" | "degraded" | "unhealthy"
    db: bool
    redis: bool
    hf_api: bool
