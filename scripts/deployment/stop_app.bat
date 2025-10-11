@echo off
REM CodePulse - GitHub Repository Analyzer
REM Stop Script for Windows

echo 🛑 Stopping CodePulse - GitHub Repository Analyzer
echo ==================================

REM Kill Python processes that might be running the app
echo 🔄 Stopping CodePulse processes...
taskkill /f /im python.exe >nul 2>&1

REM Also try to kill specifically by window title if available
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo csv ^| find "python.exe"') do (
    echo Found Python process: %%i
    taskkill /f /pid %%i >nul 2>&1
)

REM Wait a moment
timeout /t 2 /nobreak >nul

REM Check if any Python processes are still running
tasklist /fi "imagename eq python.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️  Some Python processes may still be running
    echo You can check with: tasklist /fi "imagename eq python.exe"
    echo Force stop with: taskkill /f /im python.exe
) else (
    echo ✅ CodePulse stopped successfully
)

echo ==================================
pause