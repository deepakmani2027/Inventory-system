#!/bin/bash

# Change to backend directory
cd "$(dirname "$0")/backend" || exit

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run setup.sh first:"
    echo "   cd .. && bash setup.sh"
    exit 1
fi

source venv/bin/activate

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "❌ Please edit .env and set OPENROUTER_API_KEY"
    exit 1
fi

# Check if OPENROUTER_API_KEY is set
if grep -q "OPENROUTER_API_KEY=sk-or-v1-" .env; then
    echo "✅ OPENROUTER_API_KEY is configured"
else
    echo "⚠️  WARNING: OPENROUTER_API_KEY may not be set correctly"
    echo "Get your key from: https://openrouter.ai/settings/keys"
fi

echo ""
echo "🚀 Starting InventoryPro Backend on http://0.0.0.0:8001"
echo "Press Ctrl+C to stop"
echo ""

# Start the server
python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload

