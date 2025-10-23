"""Pydantic models for API payloads."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class GuidelineSection(BaseModel):
    id: int
    external_id: str
    title: str
    body: str
    language: str

    class Config:
        orm_mode = True


class RegulationSection(BaseModel):
    id: int
    external_id: str
    title: str
    body: str
    region: str
    regulation_type: str
    language: str

    class Config:
        orm_mode = True


class Match(BaseModel):
    id: int
    guideline_id: int
    regulation_id: int
    score: float
    confidence: float
    rationale: str
    status: str
    reviewer: Optional[str]
    reviewer_notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class MatchUpdate(BaseModel):
    status: Optional[str] = None
    reviewer: Optional[str] = None
    reviewer_notes: Optional[str] = None
