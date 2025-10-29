"""Helpers for handling interactive document uploads."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import re

import numpy as np
from sentence_transformers import SentenceTransformer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ingestion.extract import extract_text
from processing.cleanup import normalize_text
from processing.matching import RelationshipMatcher

from .models import CloudGuidelineSection, Match, RegulationSection


_embedding_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _embedding_model


@dataclass(slots=True)
class Segment:
    text: str
    start: int
    end: int


@dataclass(slots=True)
class UploadSummary:
    sections_created: int
    matches_created: int


async def ingest_uploaded_document(
    session: AsyncSession,
    *,
    file_path: Path,
    category: str,
    title: str,
    language: str,
    max_segment_length: int = 800,
    similarity_threshold: float = 0.55,
    top_k: int = 5,
) -> UploadSummary:
    """Extract text, persist sections, and create similarity matches."""

    raw_text = await asyncio.to_thread(extract_text, file_path)
    normalized = normalize_text(raw_text)
    if not normalized:
        return UploadSummary(sections_created=0, matches_created=0)

    segments = list(_segment_text(normalized, max_segment_length=max_segment_length))
    if not segments:
        return UploadSummary(sections_created=0, matches_created=0)

    if category not in {"guideline", "regulation"}:
        raise ValueError(f"Unsupported category: {category}")

    matches_created = 0
    if category == "guideline":
        created_sections: list[tuple[CloudGuidelineSection, Segment]] = []
        for index, segment in enumerate(segments, start=1):
            external_id = f"{file_path.stem}-{index}"
            section = CloudGuidelineSection(
                external_id=external_id,
                title=f"{title} (Section {index})",
                body=segment.text,
                language=language,
            )
            session.add(section)
            await session.flush()
            created_sections.append((section, segment))

        matches_created = await _match_new_guidelines(
            session,
            created_sections,
            similarity_threshold=similarity_threshold,
            top_k=top_k,
        )
        sections_created = len(created_sections)
    else:
        created_sections: list[tuple[RegulationSection, Segment]] = []
        for index, segment in enumerate(segments, start=1):
            external_id = f"{file_path.stem}-{index}"
            section = RegulationSection(
                external_id=external_id,
                title=f"{title} (Section {index})",
                body=segment.text,
                region="uploaded",
                regulation_type="custom",
                language=language,
            )
            session.add(section)
            await session.flush()
            created_sections.append((section, segment))

        matches_created = await _match_new_regulations(
            session,
            created_sections,
            similarity_threshold=similarity_threshold,
            top_k=top_k,
        )
        sections_created = len(created_sections)

    await session.commit()
    return UploadSummary(sections_created=sections_created, matches_created=matches_created)


PARAGRAPH_PATTERN = re.compile(r"(.+?)(\n\n+|$)", re.DOTALL)


def _segment_text(text: str, *, max_segment_length: int) -> Iterable[Segment]:
    for match in PARAGRAPH_PATTERN.finditer(text):
        paragraph = match.group(1)
        stripped = paragraph.strip()
        if not stripped:
            continue

        leading = len(paragraph) - len(paragraph.lstrip())
        trailing = len(paragraph) - len(paragraph.rstrip())
        actual_start = match.start(1) + leading
        actual_end = match.end(1) - trailing
        if actual_start >= actual_end:
            continue

        yield from _slice_segment(
            stripped,
            base_start=actual_start,
            max_segment_length=max_segment_length,
        )


def _slice_segment(text: str, *, base_start: int, max_segment_length: int) -> Iterable[Segment]:
    cursor = 0
    length = len(text)
    while cursor < length:
        end = min(length, cursor + max_segment_length)
        if end < length:
            split = text.rfind(" ", cursor + int(max_segment_length * 0.4), end)
            if split > cursor:
                end = split
        chunk = text[cursor:end]
        stripped = chunk.strip()
        if stripped:
            leading = len(chunk) - len(chunk.lstrip())
            trailing = len(chunk) - len(chunk.rstrip())
            start = base_start + cursor + leading
            finish = base_start + end - trailing
            yield Segment(text=stripped, start=start, end=finish)
        next_cursor = end if end > cursor else cursor + max(1, max_segment_length)
        cursor = next_cursor


async def _match_new_guidelines(
    session: AsyncSession,
    sections: Sequence[tuple[CloudGuidelineSection, Segment]],
    *,
    similarity_threshold: float,
    top_k: int,
) -> int:
    regulations = (await session.scalars(select(RegulationSection))).all()
    if not regulations:
        return 0

    guideline_texts = [segment.text for _, segment in sections]
    regulation_texts = [reg.body for reg in regulations]
    guideline_vectors, regulation_vectors = await _encode_pair(guideline_texts, regulation_texts)
    similarity_matrix = _cosine_similarity(guideline_vectors, regulation_vectors)

    created = 0
    for row, (section, segment) in enumerate(sections):
        scores = similarity_matrix[row]
        top_indices = np.argsort(scores)[::-1][:top_k]
        for index in top_indices:
            score = float(scores[index])
            if score < similarity_threshold:
                continue
            regulation = regulations[index]
            match = Match(
                guideline_id=section.id,
                regulation_id=regulation.id,
                score=score,
                confidence=RelationshipMatcher.confidence_from_score(score),
                rationale=RelationshipMatcher.summarize_rationale(
                    {"id": section.external_id, "title": section.title},
                    {"id": regulation.external_id, "title": regulation.title},
                ),
                guideline_excerpt=_clip_excerpt(segment.text),
                regulation_excerpt=_clip_excerpt(regulation.body),
                guideline_span_start=segment.start,
                guideline_span_end=segment.end,
                regulation_span_start=0,
                regulation_span_end=len(regulation.body),
            )
            session.add(match)
            created += 1
    return created


async def _match_new_regulations(
    session: AsyncSession,
    sections: Sequence[tuple[RegulationSection, Segment]],
    *,
    similarity_threshold: float,
    top_k: int,
) -> int:
    guidelines = (await session.scalars(select(CloudGuidelineSection))).all()
    if not guidelines:
        return 0

    guideline_texts = [guideline.body for guideline in guidelines]
    regulation_texts = [segment.text for _, segment in sections]
    guideline_vectors, regulation_vectors = await _encode_pair(guideline_texts, regulation_texts)
    similarity_matrix = _cosine_similarity(guideline_vectors, regulation_vectors)

    created = 0
    for col, (section, segment) in enumerate(sections):
        scores = similarity_matrix[:, col]
        top_indices = np.argsort(scores)[::-1][:top_k]
        for index in top_indices:
            score = float(scores[index])
            if score < similarity_threshold:
                continue
            guideline = guidelines[index]
            match = Match(
                guideline_id=guideline.id,
                regulation_id=section.id,
                score=score,
                confidence=RelationshipMatcher.confidence_from_score(score),
                rationale=RelationshipMatcher.summarize_rationale(
                    {"id": guideline.external_id, "title": guideline.title},
                    {"id": section.external_id, "title": section.title},
                ),
                guideline_excerpt=_clip_excerpt(guideline.body),
                regulation_excerpt=_clip_excerpt(segment.text),
                guideline_span_start=0,
                guideline_span_end=len(guideline.body),
                regulation_span_start=segment.start,
                regulation_span_end=segment.end,
            )
            session.add(match)
            created += 1
    return created


async def _encode_pair(
    left: Sequence[str],
    right: Sequence[str],
) -> tuple[np.ndarray, np.ndarray]:
    model = _get_model()
    left_vectors = await asyncio.to_thread(
        model.encode,
        list(left),
        show_progress_bar=False,
        convert_to_numpy=True,
    )
    right_vectors = await asyncio.to_thread(
        model.encode,
        list(right),
        show_progress_bar=False,
        convert_to_numpy=True,
    )
    return np.asarray(left_vectors), np.asarray(right_vectors)


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    a_norm = np.linalg.norm(a, axis=1, keepdims=True)
    b_norm = np.linalg.norm(b, axis=1, keepdims=True)
    a_safe = np.maximum(a_norm, 1e-9)
    b_safe = np.maximum(b_norm, 1e-9)
    denominator = a_safe * b_safe.T
    similarity = a @ b.T
    return similarity / denominator


def _clip_excerpt(text: str, limit: int = 480) -> str:
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "…"
