from pathlib import Path

import pandas as pd

from ingestion.config import IngestionConfig
from ingestion.pipeline import IngestionPipeline


def test_persist_creates_jsonl(tmp_path: Path, monkeypatch):
    source_path = tmp_path / "doc.txt"
    source_path.write_text("hello world\nsecond line", encoding="utf-8")

    def fake_download_all(urls, output_dir):
        return [source_path]

    def fake_batch_extract(paths):
        return {source_path: "hello world\nsecond line"}

    monkeypatch.setattr("ingestion.pipeline.download_all", fake_download_all)
    monkeypatch.setattr("ingestion.pipeline.batch_extract", fake_batch_extract)

    config = IngestionConfig(sources=["http://example.com/doc.txt"], output_dir=tmp_path, metadata_dir=tmp_path)
    pipeline = IngestionPipeline(config)
    files = pipeline.run()

    assert len(files) == 1
    df = pd.read_json(files[0], lines=True)
    assert len(df) == 2
    assert set(df.columns) == {"text", "source"}
