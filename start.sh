#!/usr/bin/env bash
# Start ResumeAI application
set -e

PORT=${PORT:-8005}

echo "╔═══════════════════════════════════════╗"
echo "║  ResumeAI - AI Resume Parser          ║"
echo "║  http://localhost:$PORT               ║"
echo "╚═══════════════════════════════════════╝"

# Create virtual environment if needed
if [ ! -d "venv" ]; then
    echo "[*] Creating virtual environment..."
    python3 -m venv venv
fi

# Activate and install
source venv/bin/activate
echo "[*] Installing dependencies..."
pip install -q -r requirements.txt

# Create directories
mkdir -p instance uploads

# Run tests (optional)
if [ "${RUN_TESTS:-0}" = "1" ]; then
    echo "[*] Running tests..."
    python -m pytest tests/ -v --tb=short
fi

# Start application
echo "[*] Starting ResumeAI on port $PORT..."
export PORT=$PORT
python app.py
