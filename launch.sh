#!/bin/bash

# PromptFlow Studio Launch Script

echo "🚀 Starting PromptFlow Studio..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found."
    echo "   Please run ./install.sh first to set up the environment."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if this is the first run (no database exists)
if [ ! -f "prompt_studio.db" ]; then
    echo "📊 First run detected. Setting up demo data..."
    python demo_setup.py
    echo ""
fi

echo "🌐 Launching PromptFlow Studio on http://localhost:7860"
echo "   Press Ctrl+C to stop the server"
echo ""

# Launch the application
python app.py