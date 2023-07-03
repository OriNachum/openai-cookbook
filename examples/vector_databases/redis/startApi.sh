#!/bin/bash
./setup.sh

source /workspaces/openai-cookbook/examples/vector_databases/redis/.venv/bin/activate

echo "Starting uvicorn"
uvicorn app:app --reload --host 0.0.0.0 --port 8000
