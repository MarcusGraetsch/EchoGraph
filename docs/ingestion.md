# Ingestion Playbook

## Sources

Configure remote sources in the n8n workflow or pass URLs to the CLI:

```bash
python -m ingestion.cli https://example.com/doc1.pdf https://example.com/doc2.docx
```

## Extraction

* `pdfplumber` parses PDF page text
* `python-docx` parses DOCX paragraphs
* Apache Tika is used as a fallback for legacy formats

## Outputs

* Raw JSONL files: `data/raw/*.jsonl`
* Metadata: `data/metadata/*.json`
* Aggregated parquet: `data/raw/ingestion.parquet`

## Scheduling

The `ingestion/workflows/cloud_guideline_ingestion.json` flow demonstrates how to trigger the
CLI from n8n on a cron schedule or on-demand via webhook.
