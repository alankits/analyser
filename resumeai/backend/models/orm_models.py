"""SQLAlchemy ORM model for persisted analysis records."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from models.database import Base


class AnalysisRecord(Base):
    __tablename__ = "analysis_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    candidate_name = Column(String(255), nullable=False, default="Candidate")
    target_role = Column(String(255), nullable=True)
    ats_result_json = Column(Text, nullable=False)
    resume_fixes_json = Column(Text, nullable=False)
    career_matches_json = Column(Text, nullable=False)
    roadmap_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
