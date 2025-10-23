"""Configuration for document ingestion pipelines."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence


@dataclass(slots=True)
class IngestionConfig:
    """Runtime configuration for an ingestion job."""

    sources: Sequence[str]
    output_dir: Path = Path("data/raw")
    metadata_dir: Path = Path("data/metadata")
    tika_server_url: str | None = None
    schedule: str | None = None
    allowed_mime_types: Sequence[str] = field(
        default_factory=lambda: (
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    )

    def ensure_directories(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
