@echo off
REM CodePulse - GitHub Repository Analyzer
REM Start Script for Windows

echo 🚀 Starting CodePulse - GitHub Repository Analyzer
echo ==================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if we're in the correct directory
if not exist "app.py" (
    echo ❌ Error: app.py not found in current directory
    echo Please run this script from the CodePulse project directory
    pause
    exit /b 1
)

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo 📦 Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo ⚠️  No virtual environment found. Using system Python.
)

REM Install dependencies if requirements.txt exists
if exist "requirements.txt" (
    echo 📋 Installing/updating dependencies...
    pip install -r requirements.txt
)

REM Create PID directory if it doesn't exist
if not exist ".pid" mkdir .pid

REM Kill any existing instances
echo 🔄 Stopping any existing instances...
taskkill /f /im python.exe >nul 2>&1

REM Start the application
echo 🎯 Starting CodePulse on http://localhost:5050
echo 💡 Press Ctrl+C to stop the server
echo 💡 Or run 'stop_app.bat' from another terminal
echo ==================================

python app.py