"""Command line interface for ingestion."""
from __future__ import annotations

import argparse
from pathlib import Path

from .config import IngestionConfig
from .pipeline import IngestionPipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the EchoGraph ingestion pipeline")
    parser.add_argument("sources", nargs="+", help="Source URLs to ingest")
    parser.add_argument("--output-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--metadata-dir", type=Path, default=Path("data/metadata"))
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    config = IngestionConfig(
        sources=args.sources,
        output_dir=args.output_dir,
        metadata_dir=args.metadata_dir,
    )
    pipeline = IngestionPipeline(config)
    files = pipeline.run()
    parquet = pipeline.to_parquet(files)
    print(f"Wrote {len(files)} JSONL files and parquet at {parquet}")


if __name__ == "__main__":
    main()
