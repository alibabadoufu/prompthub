#!/bin/bash

# PromptFlow Studio Installation Script

echo "🚀 PromptFlow Studio Installation"
echo "================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment."
    echo "   On Ubuntu/Debian, you may need to run: sudo apt install python3-venv"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies."
    exit 1
fi

echo "✅ Installation complete!"
echo ""
echo "🧪 Running system tests..."
python test_system.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Installation successful!"
    echo ""
    echo "Next steps:"
    echo "1. Activate the virtual environment: source venv/bin/activate"
    echo "2. (Optional) Set up demo data: python demo_setup.py"
    echo "3. Start the application: python app.py"
    echo "4. Open your browser to: http://localhost:7860"
else
    echo ""
    echo "⚠️  Some tests failed, but the core functionality should work."
    echo "You can still try running the application with: python app.py"
fi