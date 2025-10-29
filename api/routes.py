"""API routes exposing guideline and match data."""
from __future__ import annotations

import asyncio
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .database import get_session
from .models import CloudGuidelineSection, Match, RegulationSection
from .schemas import (
    GuidelineSection as GuidelineSchema,
    MatchDetail as MatchSchema,
    MatchUpdate,
    RegulationSection as RegulationSchema,
)
from .upload import ingest_uploaded_document

try:  # pragma: no cover - optional dependency for multipart parsing
    import multipart  # type: ignore  # noqa: F401

    MULTIPART_AVAILABLE = True
except ModuleNotFoundError:  # pragma: no cover - triggered in limited test envs
    MULTIPART_AVAILABLE = False

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
    stmt = (
        select(Match)
        .where(Match.guideline_id == guideline_id)
        .options(
            selectinload(Match.guideline),
            selectinload(Match.regulation),
        )
    )
    if status:
        stmt = stmt.filter(Match.status == status)
    result = await session.scalars(stmt)
    matches = result.all()
    return [MatchSchema.model_validate(row) for row in matches]


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


if MULTIPART_AVAILABLE:

    @router.post("/documents/upload")
    async def upload_document(
        file: UploadFile = File(...),
        category: str = Form(...),
        title: str = Form(...),
        language: str = Form("en"),
        session: AsyncSession = Depends(get_session),
    ) -> dict[str, int | str]:
        upload_dir = Path("data/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_id = uuid4().hex
        extension = Path(file.filename or "document").suffix or ".bin"
        target_path = upload_dir / f"{file_id}{extension}"
        contents = await file.read()
        target_path.write_bytes(contents)

        normalized_category = category.lower()
        if normalized_category not in {"guideline", "regulation"}:
            raise HTTPException(status_code=400, detail="category must be 'guideline' or 'regulation'")

        try:
            result = await ingest_uploaded_document(
                session,
                file_path=target_path,
                category=normalized_category,
                title=title,
                language=language,
            )
        finally:
            try:
                await asyncio.to_thread(target_path.unlink)
            except FileNotFoundError:
                pass

        return {
            "status": "processed",
            "sections_created": result.sections_created,
            "matches_created": result.matches_created,
        }

else:

    @router.post("/documents/upload")
    async def upload_document_unavailable() -> dict[str, str]:
        raise HTTPException(
            status_code=503,
            detail="File uploads require the 'python-multipart' package to be installed on the server.",
        )
