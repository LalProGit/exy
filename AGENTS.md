# Project Context: FastAPI Core

## 1. Stack & Architecture
- **Framework:** FastAPI + Pydantic
- **Runtime:** Python 3.11
- **Package Manager:** `uv` (Strictly use `uv` for dependency management, NOT `pip` or `poetry`)
- **Server:** Uvicorn (Host: 0.0.0.0, Port: 8000)
- **Deployment Target:** Single-node Ubuntu/Debian VPS via Docker Compose.
- **Reverse Proxy:** Caddy (handles SSL and proxies to localhost:8000).

## 2. Infrastructure & Deployment
- **Containerization:** Multi-stage `Dockerfile` using `ghcr.io/astral-sh/uv:latest` for builds.
- **Security:** The Docker container MUST run as a non-root user (`appuser`). 
- **CI/CD:** GitHub Actions (`workflow_dispatch` manual trigger).
- **Strategy:** Build -> Push to `ghcr.io` -> SSH to VPS -> `docker compose pull && docker compose up -d` (Standard Recreate, brief downtime acceptable).

## 3. Coding Guidelines
- **Typing:** Strict type hinting is mandatory. Leverage Pydantic V2 models for all data validation.
- **Environment Variables:** Handled via `.env` files locally and injected via Docker Compose in production. Never hardcode secrets.
- **Dependencies:** If adding a dependency, update `pyproject.toml` and generate a new `uv.lock`. Do not modify `requirements.txt` as we use `uv sync`.
- **Formatting:** Adhere strictly to PEP 8 standards (e.g., using `ruff` or `black`).

## 4. Operational Protocol
- Do not suggest complex orchestration (Kubernetes, Swarm) or strict zero-downtime Blue/Green deployments. Stick to the established single-node Docker Compose recreate architecture.
- When generating shell commands, favor modern, efficient CLI tools.