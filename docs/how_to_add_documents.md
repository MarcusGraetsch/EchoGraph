# How to Add New Documents

1. Place source files in an accessible location (S3 bucket, HTTPS endpoint, or shared drive).
2. Update the n8n workflow `ingestion/workflows/cloud_guideline_ingestion.json` with the new
   source URLs or configure a webhook that sends the file location to the ingestion CLI.
3. Run `python -m ingestion.cli <url ...>` to validate extraction locally.
4. Commit metadata updates and ensure the ingestion pipeline writes new JSONL and parquet files.
5. Trigger the processing worker to normalize, chunk, and embed the new content.
