"""Pydantic models for API payloads."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


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


class TextSpan(BaseModel):
    start: int
    end: int


class Match(BaseModel):
    id: int
    guideline_id: int
    regulation_id: int
    score: float
    confidence: float
    rationale: str
    guideline_excerpt: Optional[str]
    regulation_excerpt: Optional[str]
    guideline_span_start: Optional[int]
    guideline_span_end: Optional[int]
    regulation_span_start: Optional[int]
    regulation_span_end: Optional[int]
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


class MatchDetail(Match):
    guideline_section: Optional[GuidelineSection] = Field(default=None, alias="guideline")
    regulation_section: Optional[RegulationSection] = Field(default=None, alias="regulation")

    @property
    def guideline_span(self) -> Optional[TextSpan]:
        if self.guideline_span_start is None or self.guideline_span_end is None:
            return None
        return TextSpan(start=self.guideline_span_start, end=self.guideline_span_end)

    @property
    def regulation_span(self) -> Optional[TextSpan]:
        if self.regulation_span_start is None or self.regulation_span_end is None:
            return None
        return TextSpan(start=self.regulation_span_start, end=self.regulation_span_end)

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
