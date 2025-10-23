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

## Bare-metal Ubuntu 22.04 (Contabo VM) Setup

The project can run on a fresh Contabo virtual machine that ships only with
Ubuntu 22.04. The following checklist prepares the host, deploys the stack, and
opens access from your local laptop.

### 1. Prepare the VM

1. SSH into the instance: `ssh ubuntu@<vm-ip>`
2. Update the base system and install build tools:

   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y git build-essential curl ca-certificates gnupg lsb-release
   ```

### 2. Install Runtime Prerequisites

EchoGraph expects Docker, Python 3.10+, Node.js 18+, and pnpm for the frontend.

1. **Docker Engine and Compose plugin**

   ```bash
   curl -fsSL https://get.docker.com | sh
   sudo usermod -aG docker "$USER"
   newgrp docker
   ```

   Verify with `docker --version` and `docker compose version`.

2. **Python tooling**

   ```bash
   sudo apt install -y python3-pip python3-venv
   ```

3. **Node.js 18 and pnpm**

   ```bash
   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
   sudo apt install -y nodejs
   sudo npm install -g pnpm
   ```

### 3. Clone the Repository and Bootstrap

```bash
git clone https://github.com/<your-org>/EchoGraph.git
cd EchoGraph
make bootstrap
```

The bootstrap target configures Python environments, installs backend/frontend
dependencies, and downloads demo documents.

### 4. Configure Environment Variables (Optional)

Create a `.env` file with overrides such as `DATABASE_URL`, `QDRANT_URL`, or
`N8N_WEBHOOK_SECRET` if you are not using the default docker-compose settings.

### 5. Launch the Stack

```bash
docker compose up --build -d
```

Check container status with `docker compose ps` and stream logs via
`docker compose logs -f <service>`.

### 6. Open Firewall Ports

If UFW is enabled, allow inbound traffic for the exposed services:

```bash
sudo ufw allow 5173/tcp   # frontend
sudo ufw allow 8000/tcp   # FastAPI API
sudo ufw reload
```

Expose any additional ports you require (e.g., 5678 for n8n webhooks).

### 7. Access from Your Laptop

Visit `http://<vm-ip>:5173` for the reviewer UI and
`http://<vm-ip>:8000` for the REST API. For hardened access, place a reverse
proxy such as Nginx or Caddy in front of the stack with TLS and authentication.

### 8. Enable HTTPS with Caddy (Optional)

Browsers will warn when you access the stack over HTTPS by IP address because
public certificate authorities cannot issue valid TLS certificates for raw IPs.
To eliminate the warning you must serve the site via a domain name that you
control and terminate TLS in front of the containers. The repository ships with
an optional [Caddy](https://caddyserver.com/) reverse proxy profile that
automates certificate management once a DNS record points to your VM.

1. Purchase or configure a domain/subdomain and create an `A` record that
   resolves to your VM's public IP.
2. Create or update a `.env` file in the repository root:

   ```env
   CADDY_DOMAIN=guidelines.example.com
   CADDY_ACME_EMAIL=ops@example.com
   ```

   Caddy accepts multiple hostnames separated by spaces (e.g.,
   `CADDY_DOMAIN="guidelines.example.com www.guidelines.example.com"`).
3. Open ports 80 and 443 on the VM firewall:

   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw reload
   ```

4. Start the reverse proxy alongside the stack:

   ```bash
   docker compose --profile tls up -d caddy
   ```

   The `tls` profile leaves the existing HTTP port mappings in place so you can
   verify the stack before cutting over DNS.
5. Browse to `https://guidelines.example.com`. Caddy will obtain and renew
   Let's Encrypt certificates automatically.

If you cannot use a domain name, your only options are to continue with HTTP or
install a self-signed certificate locally. Browsers will still display a
warning in the self-signed case, but you can trust the certificate manually for
your machine.
