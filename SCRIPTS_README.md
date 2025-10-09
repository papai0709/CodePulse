# CodePulse - Application Management Scripts

This directory contains convenient scripts to start and stop the CodePulse application on different operating systems.

## 📁 Available Scripts

### Linux/Mac (Shell Scripts)
- `start_app.sh` - Start the CodePulse application
- `stop_app.sh` - Stop the CodePulse application

### Windows (Batch Files)
- `start_app.bat` - Start the CodePulse application
- `stop_app.bat` - Stop the CodePulse application

## 🚀 Usage Instructions

### Linux/Mac
```bash
# Start the application
./start_app.sh

# Stop the application
./stop_app.sh
```

### Windows
```cmd
# Start the application
start_app.bat

# Stop the application
stop_app.bat
```

## ✨ Features

### Start Scripts (`start_app.sh` / `start_app.bat`)
- ✅ **Environment Check**: Verifies Python installation
- ✅ **Directory Validation**: Ensures script runs from correct location
- ✅ **Virtual Environment**: Activates venv if available
- ✅ **Dependency Management**: Installs/updates requirements automatically
- ✅ **Clean Start**: Stops any existing instances before starting
- ✅ **Process Tracking**: Creates PID files for proper management
- ✅ **User Feedback**: Clear status messages and instructions

### Stop Scripts (`stop_app.sh` / `stop_app.bat`)
- ✅ **Graceful Shutdown**: Attempts clean process termination first
- ✅ **Force Stop**: Uses force termination if needed
- ✅ **Process Cleanup**: Removes PID files and temp resources
- ✅ **Verification**: Confirms successful shutdown
- ✅ **Error Handling**: Provides troubleshooting guidance

## 🔧 Technical Details

### Process Management
- **Linux/Mac**: Uses `pkill` and process IDs for clean management
- **Windows**: Uses `taskkill` with process name and PID matching
- **PID Files**: Stored in `.pid/codepulse.pid` for tracking

### Error Handling
- Python installation verification
- Directory structure validation
- Process conflict resolution
- Graceful fallback mechanisms

## 🛠️ Troubleshooting

### If the app won't start:
1. Check Python installation: `python --version` (Windows) or `python3 --version` (Linux/Mac)
2. Ensure you're in the CodePulse project directory
3. Verify `app.py` exists in the current directory
4. Check if port 5050 is already in use

### If the app won't stop:
1. Try the stop script first
2. Manual process termination:
   - **Linux/Mac**: `pkill -9 -f 'python.*app.py'`
   - **Windows**: `taskkill /f /im python.exe`

### Permission Issues (Linux/Mac):
```bash
# Make scripts executable
chmod +x start_app.sh stop_app.sh
```

## 🌐 Access Points

Once started, CodePulse will be available at:
- **Local**: http://localhost:5050
- **Network**: http://[your-ip]:5050

## 💡 Tips

1. **Virtual Environment**: Create a `venv` folder for isolated dependencies
2. **Background Mode**: On Linux/Mac, add `&` to run in background
3. **Logs**: Check terminal output for debugging information
4. **Port Conflicts**: Change port in `config.py` if 5050 is unavailable

---

**Happy Analyzing! 🚀📊**