# Getting Started

1. Clone the repository and change directories to `EchoGraph`.
2. Run `make bootstrap` to install dependencies.
3. Execute `make download-demo` to populate sample documents. The task copies the bundled demo
   assets by default; rerun `python scripts/download_demo_documents.py --prefer-remote` if you
   need the latest upstream files once your network allows.
4. Use `docker compose up --build` to start local services.
5. Visit the frontend at http://localhost:5173 and log in with your SSO provider (stubbed during
   development) to review matches.
6. Deploying to a remote host? Follow the [bare-metal Ubuntu setup](deployment.md#bare-metal-ubuntu-2204-contabo-vm-setup).
