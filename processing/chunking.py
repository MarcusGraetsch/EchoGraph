"""Chunking strategies for long-form documents."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


def default_overlap(chunk_size: int) -> int:
    return max(0, chunk_size // 10)


@dataclass(slots=True)
class ChunkConfig:
    chunk_size: int = 512
    overlap: int | None = None


def chunk_text(text: str, config: ChunkConfig | None = None) -> list[str]:
    config = config or ChunkConfig()
    overlap = config.overlap if config.overlap is not None else default_overlap(config.chunk_size)

    tokens = text.split()
    chunks: list[str] = []
    start = 0
    while start < len(tokens):
        end = min(len(tokens), start + config.chunk_size)
        chunk = " ".join(tokens[start:end])
        if chunk:
            chunks.append(chunk)
        if end == len(tokens):
            break
        start = end - overlap
    return chunks


def chunk_many(texts: Iterable[str], config: ChunkConfig | None = None) -> list[list[str]]:
    return [chunk_text(text, config=config) for text in texts]
