#!/bin/bash

# CodePulse - GitHub Repository Analyzer
# Start Script for Linux/Mac

echo "🚀 Starting CodePulse - GitHub Repository Analyzer"
echo "=================================="

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

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
    
    # Verify that veracode-api-py is installed in the virtual environment
    if ! python -c "import veracode_api_py" 2>/dev/null; then
        echo "⚠️  Veracode API library not found in virtual environment"
        echo "📋 Installing dependencies including Veracode API..."
        pip install -r requirements.txt
    fi
else
    echo "❌ Error: Virtual environment not found!"
    echo "Please create a virtual environment first:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Install dependencies if requirements.txt exists and virtual environment is active
if [ -f "requirements.txt" ] && [ -n "$VIRTUAL_ENV" ]; then
    echo "📋 Verifying dependencies in virtual environment..."
    pip install -r requirements.txt --quiet
elif [ -f "requirements.txt" ]; then
    echo "⚠️  Warning: Not using virtual environment. Dependencies may conflict."
    echo "📋 Installing dependencies..."
    pip install -r requirements.txt
fi

# Create PID file directory if it doesn't exist
mkdir -p .pid

# Kill any existing instances
echo "🔄 Stopping any existing instances..."
pkill -f "python.*app.py" 2>/dev/null || true

# Start the application
echo "🎯 Starting CodePulse on http://localhost:5050"
echo "💡 Press Ctrl+C to stop the server"
echo "💡 Or run './stop_app.sh' from another terminal"
echo "=================================="

# Start the app and save PID
python3 app.py &
echo $! > .pid/codepulse.pid

# Wait for the process
wait