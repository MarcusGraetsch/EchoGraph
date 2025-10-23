# Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | SQLAlchemy connection string for the API and workers | `postgresql+asyncpg://postgres:postgres@localhost:5432/echograph` |
| `QDRANT_URL` | Qdrant endpoint for embeddings | `http://localhost:6333` |
| `EMBEDDING_MODEL` | Sentence Transformers model name | `sentence-transformers/all-MiniLM-L6-v2` |
| `N8N_WEBHOOK_SECRET` | Optional shared secret for triggering ingestion flows | _unset_ |
