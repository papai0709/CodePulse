# CodePulse - AI-Enhanced GitHub Repository Analyzer �

A comprehensive, intelligent tool that analyzes GitHub repositories for test coverage, code quality, security, and performance. **Now featuring AI-powered insights for deeper analysis and intelligent recommendations!**

## ✨ Features

### 📊 Standard Analysis
- **Repository Analysis**: Deep analysis of both public and private GitHub repositories
- **Test Coverage**: Automated test case coverage analysis with multiple language support
- **Issue Detection**: Identifies main issues and suggests corrective actions
- **Interactive Dashboard**: Web-based interface with public/private repository selection
- **Improvement Suggestions**: Detailed recommendations for code quality enhancement
- **No Token Required**: Analyze public repositories without authentication

### 🧠 AI-Enhanced Analysis
- **Intelligent Code Review**: Context-aware analysis beyond simple pattern matching
- **Smart Security Analysis**: Advanced vulnerability detection using AI reasoning
- **Architecture Assessment**: AI-powered evaluation of code structure and complexity
- **Performance Optimization**: Intelligent suggestions for algorithmic improvements
- **Automated Documentation**: Missing docs detection with AI-generated suggestions
- **Strategic Roadmap**: AI-generated implementation timeline with priority matrix
- **Confidence Scoring**: AI provides reliability scores for all recommendations

## 🚀 Quick Start

### Easy Setup with Scripts

#### Linux/Mac
```bash
# Start the application
./start_app.sh

# Stop the application  
./stop_app.sh
```

#### Windows
```cmd
# Start the application
start_app.bat

# Stop the application
stop_app.bat
```

### 🐳 Docker Deployment (Recommended)

#### Quick Docker Start
```bash
# Production mode
./docker/docker-manage.sh run

# Development mode  
./docker/docker-manage.sh dev

# Check status
./docker/docker-manage.sh status
```

#### Docker Requirements
- Docker Engine 20.10+
- Docker Compose 2.0+
- 2GB RAM minimum

#### Docker Features
- ✅ **Production Ready**: Optimized containers with health checks
- ✅ **Development Mode**: Live code reloading for development
- ✅ **Security**: Non-root execution, isolated networks
- ✅ **Monitoring**: Built-in logging and health monitoring
- ✅ **Scalability**: Easy horizontal scaling with compose

📖 **Full Docker Documentation**: [docker/README.md](docker/README.md)

### Manual Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   python app.py
   ```

3. **Access Dashboard**:
   Open http://localhost:5050 in your browser

### Enable AI Features (Optional)

1. **Set Up GitHub Token** (Required for AI features):
   ```bash
   cp .env.example .env
   # Edit .env and add your GitHub token
   GITHUB_TOKEN=your_github_token_here
   ```

2. **Restart Application**:
   ```bash
   python app.py
   ```

3. **Enable AI Analysis**:
   - Check "Enable AI-Enhanced Analysis" in the web interface
   - Experience intelligent insights and recommendations!
   ```bash
   python app_enhanced.py
   ```

3. **Enable AI Analysis**:
   - Visit http://localhost:5050
   - Check "Enable AI-Enhanced Analysis" option
   - Experience intelligent insights!

## 📊 Usage

### Standard Analysis
1. Enter a GitHub repository URL in the dashboard
2. Check "This is a public repository" for public repos (no token needed)
3. Uncheck for private repositories (requires GitHub token in .env)
4. Click "Analyze Repository"
5. View comprehensive test coverage analysis and basic recommendations

### AI-Enhanced Analysis  
1. Ensure you have a GitHub token configured in `.env`
2. Enter a repository URL
3. **Enable "AI-Enhanced Analysis"** checkbox
4. Click "AI-Enhanced Analysis" button
5. Get intelligent insights including:
   - Context-aware code quality assessment
   - AI-powered security vulnerability analysis
   - Performance optimization suggestions
   - Strategic improvement roadmap
   - ROI projections for improvements

## 🏗️ Project Structure

```
├── app.py                           # Unified Flask application with AI features
├── config.py                       # Configuration settings
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables (create this)
├── analyzer/                      # Core analysis modules
│   ├── __init__.py
│   ├── github_client.py           # GitHub API client
│   ├── test_analyzer.py           # Test coverage analysis
│   ├── issue_detector.py          # Issue detection logic
│   ├── report_generator.py        # Standard report generation
│   ├── ai_analyzer.py             # 🧠 AI analysis engine
│   └── enhanced_report_generator.py # 🚀 AI-enhanced reporting
├── templates/                     # HTML templates
│   ├── base.html
│   ├── index.html                 # Main dashboard with AI toggle
│   ├── results.html              # Standard analysis results
│   ├── results_enhanced.html     # 🎨 AI-enhanced results page
│   └── ...
├── static/                       # Static assets
│   ├── css/
│   │   └── style.css            # Enhanced styling
│   └── js/
│       └── main.js              # Interactive features
├── scripts/                      # Utility scripts
│   ├── test_ai_compatibility.py  # AI feature testing
│   └── test_app.py               # Application testing
├── tests/                        # Test suite
└── docs/                         # Documentation
    ├── AI_ENHANCEMENT_SUMMARY.md
    └── PROJECT_STRUCTURE.md
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file from the example:
```bash
cp .env.example .env
```

Required for AI features:
```bash
# GitHub Personal Access Token
GITHUB_TOKEN=your_github_token_here

# Optional settings
DEBUG=True
SECRET_KEY=your-secret-key
```

### GitHub Token Setup

1. **Go to GitHub Settings**: https://github.com/settings/tokens
2. **Generate new token** with these scopes:
   - `repo` (for private repositories)
   - `public_repo` (for public repositories)
3. **Copy token** to your `.env` file

## 🤖 AI Models Supported

| Model | Use Case | Cost | Quality |
|-------|----------|------|---------|
| `gpt-4.1-mini` | General analysis (default) | Low | High |
| `gpt-4.1` | Comprehensive analysis | Medium | Very High |
| `codestral-2501` | Code-specific tasks | Low | High |
| `o1-mini` | Complex reasoning | High | Very High |

## 📈 Analysis Comparison

| Feature | Standard | AI-Enhanced |
|---------|----------|-------------|
| **Speed** | Fast | Moderate |
| **Depth** | Basic patterns | Deep understanding |
| **Accuracy** | Good | Excellent |
| **Recommendations** | Generic | Tailored |
| **Roadmap** | Basic | Strategic |
| **Cost** | Free | $0.10-10.00/analysis |

## 🎯 Examples

### Standard Output
```bash
✅ Test Coverage: 75%
⚠️  Security Issues: 3 found
📝 Documentation: Missing in 12 files
```

### AI-Enhanced Output
```bash
🧠 AI Quality Score: 82/100
🚨 Critical: SQL injection in auth/login.py (2-4 hours fix)
⚡ Performance: Implement Redis caching (15% speed improvement)
📋 Roadmap: 4-phase improvement plan (6 months)
💰 ROI: 25% development velocity increase
```

## 📚 Documentation

- **[AI Improvements Guide](AI_IMPROVEMENTS.md)**: Comprehensive AI enhancement documentation
- **[API Documentation](#)**: REST API reference
- **[Contributing Guidelines](#)**: How to contribute to the project
│   └── results.html
├── static/               # CSS, JS, and assets
│   ├── css/
│   ├── js/
│   └── images/
└── tests/                # Unit tests
    ├── __init__.py
    ├── test_github_client.py
    ├── test_analyzer.py
    └── test_issue_detector.py
```

## Usage

1. Enter a GitHub repository URL in the dashboard
2. View comprehensive test coverage analysis
3. Review identified issues and improvement areas
4. Follow suggested corrective actions

## Development

To run tests:
```bash
pytest tests/ --cov=analyzer
```

To run in development mode:
```bash
export FLASK_ENV=development
python app.py
```

## License

MIT License# CodePulse
