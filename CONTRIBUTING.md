# Contributing to EchoGraph

We welcome contributions that improve document ingestion, processing, relationship
discovery, backend services, and user experiences.

## Code of Conduct

All contributors must follow the [Contributor Covenant](https://www.contributor-covenant.org/).

## Development Workflow

1. Fork the repository and clone your fork locally.
2. Create a topic branch based on `main`.
3. Install dependencies using `make bootstrap`.
4. Run unit tests with `make test` and ensure lint checks pass before submitting a PR.
5. Submit a pull request and tag relevant maintainers for review.

## Coding Standards

* **Python**: Use type hints, docstrings, and follow PEP8. Run `ruff` and `mypy` locally.
* **JavaScript/TypeScript**: Follow the ESLint and Prettier rules configured in the repo.
* **Infrastructure**: Validate Kubernetes manifests with `kubectl kustomize` and `kubeconform`.

## Commit Messages

Use conventional commit prefixes such as `feat:`, `fix:`, `docs:`, `test:`, `refactor:` to help
with changelog generation.

## Pull Requests

* Link to related issues.
* Provide a summary of changes, testing evidence, and screenshots for UI updates.
* Ensure new functionality is covered by tests and documentation.

Thank you for helping build EchoGraph!
