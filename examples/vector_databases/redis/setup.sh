#!/bin/bash

echo "Setting up vector db"
docker-compose up -d

echo "Setting up python e"
python3 -m venv /workspaces/openai-cookbook/examples/vector_databases/redis/.venv
pip3 install -r requirements.txt

echo "Preparing data"
python3 gettingStartedSetup.py