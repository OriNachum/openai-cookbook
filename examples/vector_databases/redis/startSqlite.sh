#!/bin/bash

echo "Starting uvicorn"
/home/ec2-user/.local/bin/uvicorn sqlite:app --reload --host 0.0.0.0 --port 8003
