# Architecture Overview

```mermaid
flowchart LR
    n8n[n8n Scheduler] -->|triggers| ingestion[Ingestion Workers]
    ingestion -->|raw JSONL| data[(Object Storage)]
    ingestion --> metadata[(Metadata Store)]
    data --> processing[Processing Pipelines]
    processing -->|embeddings| qdrant[(Qdrant Vector DB)]
    processing -->|sections| postgres[(PostgreSQL)]
    qdrant --> matcher[Relationship Matcher]
    postgres --> matcher
    matcher -->|candidate matches| postgres
    postgres --> api[FastAPI]
    api --> frontend[React Admin UI]
```

The system is organized into modular services that can scale independently. Ingestion,
processing, and relationship discovery can run as asynchronous workers or scheduled jobs.
