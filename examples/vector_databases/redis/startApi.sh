#!/bin/bash
./setup.sh

echo "Starting uvicorn"
/home/ec2-user/.local/bin/uvicorn app:app --reload --host 0.0.0.0 --port 8000
