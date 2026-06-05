#!/usr/bin/env bash
set -e
set -u

echo "[SYSTEM] Initializing Exy Agent Container..."

if [ -z "${OPENROUTER_API_KEY:-}" ]; then
  echo "[FATAL] OPENROUTER_API_KEY is not set. The LLM will fail."
  exit 1
fi

DATA_DIR="/app/data"
if [ ! -d "$DATA_DIR" ]; then
    echo "[SYSTEM] Creating data directory..."
    mkdir -p "$DATA_DIR"
fi

echo "[SYSTEM] Pre-flight checks passed. Handing over control to Uvicorn..."

exec uvicorn src.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips="*"