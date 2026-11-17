#!/usr/bin/env bash
# Cloud agent bootstrap (baked into the environment snapshot). Idempotent and non-interactive.
# Installs PostgreSQL + pgvector and Redis so integration tests can run without Docker,
# then installs backend and frontend dependencies.
set -euo pipefail

cd "$(dirname "$0")/.."

sudo apt-get update -q
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -q \
  python3.12-venv postgresql postgresql-16-pgvector redis-server

python3 -m venv backend/.venv
backend/.venv/bin/pip install --quiet --upgrade pip
backend/.venv/bin/pip install --quiet -r backend/requirements-dev.txt

(cd frontend && npm ci --no-audit --no-fund)

[ -f .env ] || cp .env.example .env
