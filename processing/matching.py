"""Relationship discovery between guideline and regulation sections."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, PointStruct


@dataclass(slots=True)
class MatchResult:
    guideline_id: str
    regulation_id: str
    score: float
    rationale: str
    confidence: float


class RelationshipMatcher:
    """Query Qdrant for similar sections and summarize the rationale."""

    def __init__(self, *, client: QdrantClient, collection_name: str) -> None:
        self.client = client
        self.collection_name = collection_name

    def search(
        self,
        vector: Sequence[float],
        *,
        limit: int = 5,
        filters: Filter | None = None,
    ) -> list[PointStruct]:
        return self.client.search(
            collection_name=self.collection_name,
            query_vector=list(vector),
            limit=limit,
            query_filter=filters,
        )

    def match(
        self,
        guideline_chunks: Iterable[dict[str, str]],
        *,
        embedding_lookup: callable[[str], Sequence[float]],
        rationale_fn: callable[[dict[str, str], dict[str, str]], str],
    ) -> list[MatchResult]:
        results: list[MatchResult] = []
        for chunk in guideline_chunks:
            vector = embedding_lookup(chunk["id"])
            matches = self.search(vector)
            for point in matches:
                payload = point.payload or {}
                rationale = rationale_fn(chunk, payload)
                results.append(
                    MatchResult(
                        guideline_id=chunk["id"],
                        regulation_id=str(payload.get("id")),
                        score=float(point.score or 0.0),
                        rationale=rationale,
                        confidence=float(payload.get("confidence", 0.5)),
                    )
                )
        return results

    @staticmethod
    def summarize_rationale(chunk: dict[str, str], candidate: dict[str, str]) -> str:
        guideline_label = chunk.get("title", chunk.get("id", "unknown"))
        regulation_label = candidate.get("title", candidate.get("id", "unknown"))
        return (
            f"Guideline '{guideline_label}' aligns with regulation '{regulation_label}' "
            "based on thematic overlap and shared control objectives."
        )

    @staticmethod
    def confidence_from_score(score: float) -> float:
        return float(np.clip(score, 0, 1))
