#!/bin/bash

docker-compose up -d

python3 -m venv /workspaces/openai-cookbook/examples/vector_databases/redis/.venv
pip3 install -r requirements.txt
