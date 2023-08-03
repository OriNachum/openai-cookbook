# PowerShell

# Check if Milvus is running
if ((docker ps | Select-String "milvus-standalone") -eq $null) {
    Write-Output "Starting Milvus..."
    docker compose up -d
    # Wait for Milvus to start

    Write-Output "Waiting for Milvus to start..."
    Start-Sleep -s 30
}

# Check if virtual environment exists, if not create one
if (!(Test-Path .venv)) {
    Write-Output "Creating virtual environment..."
    python3 -m venv .venv
}

# Activate the virtual environment
Write-Output "Activating virtual environment..."
. .venv/Scripts/activate

# Install Python requirements
Write-Output "Installing Python requirements..."
pip install -r requirements.txt

# Run the Flask API
Write-Output "Starting Flask API..."
python milvusApi.py
