#!/bin/bash
./setup.sh

echo "Starting uvicorn"
uvicorn app:app --reload --host 0.0.0.0 --port 3000
