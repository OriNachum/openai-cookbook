#!/bin/bash

# Check if Milvus is running
if ! docker ps | grep -q "milvus-standalone"; then
    echo "Starting Milvus..."
    docker compose up -d 
    # Wait for Milvus to start

    echo "Waiting for Milvus to start..."
    sleep 30
fi



# Check if virtual environment exists, if not create one
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install Python requirements
echo "Installing Python requirements..."
pip install -r requirements.txt

# Run the Flask API
echo "Starting Flask API..."
python milvusApi.py
