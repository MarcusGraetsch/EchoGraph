# Deployment Guide

## Docker Compose

```bash
docker compose up --build
```

Services:

* `api`: FastAPI backend on port 8000
* `frontend`: React SPA on port 5173
* `postgres`: Application database
* `qdrant`: Vector database
* `ingestion-worker`: Runs ingestion CLI jobs
* `processing-worker`: Runs embedding and matching jobs
* `n8n`: Optional workflow orchestrator

## Kubernetes

The manifests under `infra/kubernetes` provide a starting point for deploying to a managed
cluster. Customize secrets and storage classes before applying:

```bash
kubectl apply -k infra/kubernetes/overlays/dev
```

## CI/CD

GitHub Actions workflows under `.github/workflows` lint, test, build, and publish container
images to a registry. Configure repository secrets `REGISTRY_USERNAME`, `REGISTRY_PASSWORD`, and
`REGISTRY_URL`.
