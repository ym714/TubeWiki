#!/bin/bash
set -e

# Use PORT from environment, default to 8080 if not set
PORT=${PORT:-8080}

echo "Starting worker service on port $PORT"
exec uvicorn worker.main:app --host 0.0.0.0 --port "$PORT"
