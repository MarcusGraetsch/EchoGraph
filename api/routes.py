"""API routes exposing guideline and match data."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_session
from .models import CloudGuidelineSection, Match, RegulationSection
from .schemas import (
    GuidelineSection as GuidelineSchema,
    Match as MatchSchema,
    MatchUpdate,
    RegulationSection as RegulationSchema,
)

router = APIRouter()


@router.get("/guidelines", response_model=list[GuidelineSchema])
async def list_guidelines(
    language: str | None = Query(None),
    session: AsyncSession = Depends(get_session),
) -> list[GuidelineSchema]:
    stmt = select(CloudGuidelineSection)
    if language:
        stmt = stmt.filter(CloudGuidelineSection.language == language)
    result = await session.scalars(stmt)
    return [GuidelineSchema.model_validate(row) for row in result.all()]


@router.get("/regulations", response_model=list[RegulationSchema])
async def list_regulations(
    region: str | None = Query(None),
    regulation_type: str | None = Query(None),
    session: AsyncSession = Depends(get_session),
) -> list[RegulationSchema]:
    stmt = select(RegulationSection)
    if region:
        stmt = stmt.filter(RegulationSection.region == region)
    if regulation_type:
        stmt = stmt.filter(RegulationSection.regulation_type == regulation_type)
    result = await session.scalars(stmt)
    return [RegulationSchema.model_validate(row) for row in result.all()]


@router.get("/guidelines/{guideline_id}/matches", response_model=list[MatchSchema])
async def list_matches(
    guideline_id: int,
    status: str | None = Query(None),
    session: AsyncSession = Depends(get_session),
) -> list[MatchSchema]:
    stmt = select(Match).where(Match.guideline_id == guideline_id)
    if status:
        stmt = stmt.filter(Match.status == status)
    result = await session.scalars(stmt)
    return [MatchSchema.model_validate(row) for row in result.all()]


@router.patch("/matches/{match_id}", response_model=MatchSchema)
async def update_match(
    match_id: int,
    payload: MatchUpdate,
    session: AsyncSession = Depends(get_session),
) -> MatchSchema:
    match = await session.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(match, field, value)
    await session.commit()
    await session.refresh(match)
    return MatchSchema.model_validate(match)
