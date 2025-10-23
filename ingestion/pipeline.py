"""High-level ingestion pipeline."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Iterable

import pandas as pd

from .config import IngestionConfig
from .download import download_all
from .extract import batch_extract


class IngestionPipeline:
    """Coordinates downloads, extraction, and persistence."""

    def __init__(self, config: IngestionConfig) -> None:
        self.config = config
        self.config.ensure_directories()

    def run(self) -> list[Path]:
        """Execute the pipeline and return created JSONL files."""
        downloaded = download_all(self.config.sources, self.config.output_dir)
        extracted = batch_extract(downloaded)
        return [self._persist(path, text) for path, text in extracted.items()]

    def _persist(self, original_path: Path, text: str) -> Path:
        metadata = {
            "source_path": str(original_path),
            "ingested_at": datetime.utcnow().isoformat(),
            "num_characters": len(text),
        }
        metadata_path = self.config.metadata_dir / f"{original_path.stem}.json"
        metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

        jsonl_path = self.config.output_dir / f"{original_path.stem}.jsonl"
        records = [{"text": line, "source": metadata["source_path"]} for line in text.splitlines() if line]
        df = pd.DataFrame.from_records(records)
        df.to_json(jsonl_path, orient="records", lines=True, force_ascii=False)
        return jsonl_path

    def to_parquet(self, files: Iterable[Path]) -> Path:
        """Persist combined text to a Parquet file for downstream use."""
        all_records: list[dict[str, str]] = []
        for file in files:
            for line in file.read_text(encoding="utf-8").splitlines():
                all_records.append(json.loads(line))
        df = pd.DataFrame.from_records(all_records)
        parquet_path = self.config.output_dir / "ingestion.parquet"
        df.to_parquet(parquet_path)
        return parquet_path
