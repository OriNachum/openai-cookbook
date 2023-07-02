#!/bin/bash

docker-compose up -d

python -m venv /workspaces/openai-cookbook/examples/vector_databases/redis/.venv
pip install -r requirements.txt
