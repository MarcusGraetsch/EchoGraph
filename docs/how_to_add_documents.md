# How to Add New Documents

## Option A — Upload through the reviewer UI

1. Open the reviewer UI (`http://<host>:5173`) and locate the **Upload document** panel.
2. Select the document category (cloud guideline vs. regulation), pick the source file, and
   provide a descriptive title. Supported formats include PDF, DOC, DOCX, and TXT.
3. Submit the form. The backend extracts text, segments the content, generates embeddings, and
   calculates matches against the opposite corpus automatically.
4. Once complete, new sections and matches appear in the sidebar lists and inline highlights so
   reviewers can validate the relationships immediately.

## Option B — Feed sources through the ingestion workflow

1. Place source files in an accessible location (S3 bucket, HTTPS endpoint, or shared drive).
2. Update the n8n workflow `ingestion/workflows/cloud_guideline_ingestion.json` with the new
   source URLs or configure a webhook that sends the file location to the ingestion CLI.
3. Run `python -m ingestion.cli <url ...>` to validate extraction locally.
4. Commit metadata updates and ensure the ingestion pipeline writes new JSONL and parquet files.
5. Trigger the processing worker to normalize, chunk, and embed the new content.
