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
else
    echo "⚠️  No virtual environment found. Using system Python."
fi

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "📋 Installing/updating dependencies..."
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