#!/usr/bin/env bash
# Runs on every cloud agent boot: brings up PostgreSQL and Redis and prepares the cheiro database.
# Safe to re-run. Output goes to /tmp/cursor/start-user/start-user.log.
set -euo pipefail

sudo service postgresql start
until sudo -u postgres pg_isready -q; do sleep 1; done

sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='cheiro'" | grep -q 1 \
  || sudo -u postgres psql -c "CREATE USER cheiro WITH PASSWORD 'cheiro' SUPERUSER"
sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='cheiro'" | grep -q 1 \
  || sudo -u postgres psql -c "CREATE DATABASE cheiro OWNER cheiro"

sudo service redis-server start
until redis-cli ping >/dev/null 2>&1; do sleep 1; done

echo "PostgreSQL and Redis are ready."
