#!/bin/bash

# CodePulse - Setup Script
# This script ensures the virtual environment is properly configured with all dependencies

echo "🔧 CodePulse Setup Script"
echo "========================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3 and try again"
    exit 1
fi

# Check if we're in the correct directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found in current directory"
    echo "Please run this script from the CodePulse project directory"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
if [ -f "requirements.txt" ]; then
    echo "📋 Installing dependencies..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to install dependencies"
        exit 1
    fi
else
    echo "❌ Error: requirements.txt not found"
    exit 1
fi

# Verify critical dependencies
echo "🔍 Verifying critical dependencies..."

# Check Flask
if ! python -c "import flask" 2>/dev/null; then
    echo "❌ Error: Flask not installed properly"
    exit 1
fi

# Check Veracode API
if ! python -c "import veracode_api_py" 2>/dev/null; then
    echo "⚠️  Warning: Veracode API library not available"
    echo "Real Veracode analysis will not be available"
else
    echo "✅ Veracode API library installed"
fi

# Check AI dependencies
if ! python -c "import openai" 2>/dev/null; then
    echo "⚠️  Warning: OpenAI library not available"
    echo "AI-enhanced analysis will not be available"
else
    echo "✅ AI dependencies installed"
fi

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "🚀 To start the application:"
echo "   ./scripts/deployment/start_app.sh"
echo "   or"
echo "   source venv/bin/activate && python app.py"
echo ""
echo "🧪 To run tests:"
echo "   source venv/bin/activate && python -m pytest tests/ -v"
echo ""
echo "🔧 To use VS Code tasks:"
echo "   Ctrl+Shift+P -> Tasks: Run Task -> Run GitHub Repository Analyzer"
echo ""