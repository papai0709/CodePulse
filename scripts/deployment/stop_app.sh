#!/bin/bash

# CodePulse - GitHub Repository Analyzer
# Stop Script for Linux/Mac

echo "🛑 Stopping CodePulse - GitHub Repository Analyzer"
echo "=================================="

# Function to kill process by PID file
kill_by_pid() {
    if [ -f ".pid/codepulse.pid" ]; then
        PID=$(cat .pid/codepulse.pid)
        if ps -p $PID > /dev/null 2>&1; then
            echo "🔄 Stopping CodePulse (PID: $PID)..."
            kill $PID
            sleep 2
            
            # Force kill if still running
            if ps -p $PID > /dev/null 2>&1; then
                echo "⚡ Force stopping CodePulse..."
                kill -9 $PID
            fi
        fi
        rm -f .pid/codepulse.pid
    fi
}

# Kill by PID file first
kill_by_pid

# Kill any remaining Python processes running app.py
echo "🧹 Cleaning up any remaining processes..."
pkill -f "python.*app.py" 2>/dev/null || true

# Wait a moment and check if any processes are still running
sleep 1
REMAINING=$(pgrep -f "python.*app.py" | wc -l)

if [ $REMAINING -eq 0 ]; then
    echo "✅ CodePulse stopped successfully"
else
    echo "⚠️  Some processes may still be running. You can force stop with:"
    echo "   pkill -9 -f 'python.*app.py'"
fi

echo "=================================="