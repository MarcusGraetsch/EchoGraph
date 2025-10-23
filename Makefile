PYTHON?=python3
PIP?=pip
PNPM?=pnpm

.PHONY: bootstrap bootstrap-python bootstrap-frontend bootstrap-api test lint start

bootstrap: bootstrap-python bootstrap-api bootstrap-frontend download-demo

bootstrap-python:
$(PYTHON) -m venv .venv && \
. .venv/bin/activate && \
pip install -U pip && \
pip install -e ./ingestion -e ./processing -r api/requirements.txt

bootstrap-api:
$(PYTHON) -m venv .venv-api && \
. .venv-api/bin/activate && \
pip install -U pip && \
pip install -r api/requirements.txt

bootstrap-frontend:
npm install -g pnpm >/dev/null 2>&1 || true
cd frontend && $(PNPM) install

start:
docker compose up --build

lint:
. .venv/bin/activate && ruff check ingestion processing
cd frontend && $(PNPM) lint

format:
. .venv/bin/activate && ruff format ingestion processing
cd frontend && $(PNPM) format

unit-test:
. .venv/bin/activate && pytest tests -m "not integration"

integration-test:
. .venv/bin/activate && pytest tests -m integration

end-to-end-test:
cd frontend && $(PNPM) test:e2e

test: unit-test integration-test

clean:
rm -rf .venv .venv-api frontend/node_modules

.PHONY: download-demo

download-demo:
$(PYTHON) scripts/download_demo_documents.py --output data/demo_docs
