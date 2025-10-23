# EchoGraph

EchoGraph is a mono-repository that orchestrates the ingestion, enrichment, matching, and
human validation of regulatory documents against a corpus of cloud provider guidelines.
It provides ready-to-run pipelines, APIs, and user interfaces to power governance and
compliance mapping workflows.

## Repository Layout

```
/ingestion      # Python ingestion workers and n8n workflow definitions
/processing     # Text cleanup, chunking, embeddings, and relationship discovery
/api            # FastAPI backend that exposes sections, matches, and metadata
/frontend       # React single-page application for reviewers and knowledge workers
/infra          # Docker, Kubernetes, and CI/CD automation
/docs           # Architecture, playbooks, and tutorials
/tests          # Unit and integration tests
/data           # Storage location for raw, cleaned, and demo datasets
```

## Quick Start

### Prerequisites

* Docker and Docker Compose for local orchestration
* Python 3.10+
* Node.js 18+
* Poetry (optional) for Python dependency management
* pnpm or npm/yarn for frontend dependency management

### Bootstrap the Environment

```bash
make bootstrap
```

The bootstrap script will:

1. Create Python virtual environments for ingestion and processing workers
2. Install FastAPI backend dependencies
3. Install frontend dependencies with pnpm
4. Download demo documents into `data/demo_docs`

### Run the Stack Locally

```bash
docker compose up --build
```

Services provided:

* `ingestion-worker`: Executes scheduled or on-demand document ingestion jobs
* `processing-worker`: Cleans, chunks, and embeds documents, and writes vectors to Qdrant
* `postgres`: Stores canonical document sections, matches, and reviewer annotations
* `qdrant`: Holds document embeddings for similarity search
* `api`: FastAPI server serving guideline data and matches
* `frontend`: React app for exploring guidelines and validating matches

The frontend is exposed on http://localhost:5173 by default, the API on http://localhost:8000.

## Data Lifecycle

1. **Ingestion**: Python workers, orchestrated by n8n, download documents, extract text
   using `pdfplumber`, `python-docx`, or Apache Tika, and write raw JSONL files to `data/raw`.
2. **Processing**: Cleanup and chunking pipelines normalize text and create embeddings using
   Sentence Transformers. Cleaned chunks and metadata are written to `data/processed` and
   mirrored into Qdrant or `pgvector`.
3. **Relationship Discovery**: Matching jobs look up related regulation sections for each
   cloud guideline chunk, summarize the rationale with an LLM, and produce candidate matches.
4. **Human Validation**: Reviewers validate or reject matches in the frontend UI; their
   decisions are persisted in PostgreSQL.

## Documentation

* [Architecture Overview](docs/architecture.md)
* [Ingestion Playbook](docs/ingestion.md)
* [Human Validation Guide](docs/validation.md)
* [Deployment](docs/deployment.md)

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for coding standards, pull request etiquette,
and how to participate in the community.

## License

EchoGraph is released under the GPL-3.0 license. See [LICENSE](LICENSE) for details.
