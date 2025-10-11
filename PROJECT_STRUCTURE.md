# CodePulse Project Structure

```
CodePulse/
├── 📁 analyzer/                    # Core analysis modules
│   ├── __init__.py
│   ├── github_client.py           # GitHub API integration
│   ├── test_analyzer.py           # Test coverage analysis
│   ├── issue_detector.py          # Issue detection logic
│   ├── report_generator.py        # Standard report generation
│   ├── ai_analyzer.py            # AI-powered analysis
│   └── enhanced_report_generator.py # AI-enhanced reports
│
├── 📁 docker/                      # 🐳 Docker configuration
│   ├── Dockerfile                 # Production container
│   ├── Dockerfile.dev            # Development container
│   ├── docker-compose.yml        # Production orchestration
│   ├── docker-compose.dev.yml    # Development orchestration
│   ├── docker-manage.sh          # Management script (Linux/Mac)
│   ├── docker-run.sh             # Simple runner (Linux/Mac)
│   ├── docker-run.bat            # Simple runner (Windows)
│   ├── .dockerignore             # Docker ignore patterns
│   ├── .env.docker               # Environment template
│   └── README.md                 # Docker documentation
│
├── 📁 scripts/                     # Utility scripts and automation
│   ├── deployment/               # Deployment automation
│   │   ├── start_app.sh          # Start script (Linux/Mac)
│   │   ├── start_app.bat         # Start script (Windows)
│   │   ├── stop_app.sh           # Stop script (Linux/Mac)
│   │   ├── stop_app.bat          # Stop script (Windows)
│   │   └── monitor_logs.sh       # Log monitoring
│   └── testing/                  # Testing utilities
│       ├── test_ai_compatibility.py # AI features test
│       └── test_app.py           # Application testing
│
├── 📁 static/                      # Web assets
│   ├── css/
│   │   └── style.css             # Application styling
│   └── js/
│       └── main.js               # Frontend JavaScript
│
├── 📁 templates/                   # HTML templates
│   ├── base.html                 # Base template
│   ├── index.html                # Main dashboard
│   ├── loading.html              # Loading page
│   ├── results.html              # Standard results display
│   ├── results_enhanced.html     # AI-enhanced results display
│   ├── results_overview.html     # Overview tab
│   ├── results_coverage.html     # Coverage tab
│   ├── results_issues.html       # Issues tab
│   ├── results_recommendations.html # Recommendations tab
│   └── results_action_plan.html  # Action plan tab
│
├── 📁 tests/                       # Test suite
│   ├── __init__.py
│   ├── test_analyzer.py          # Analyzer tests
│   └── test_github_client.py     # GitHub client tests
│
├── 📁 docs/                        # Documentation
│   ├── AI_ENHANCEMENT_SUMMARY.md  # AI features overview
│   └── PROJECT_STRUCTURE.md       # This file
│
├── 📁 .github/                     # GitHub configuration
│   └── copilot-instructions.md    # GitHub Copilot instructions
│
├── 📄 app.py                       # 🚀 Main Flask application
├── 📄 config.py                   # Configuration management
├── 📄 requirements.txt            # Python dependencies
├── 📄 codepulse.log               # Application logs (created at runtime)
│
├── 📄 .dockerignore              # Docker ignore patterns
├── 📄 .env                        # Environment variables (create from .env.example)
├── 📄 .env.example               # Environment template
├── 📄 .gitignore                 # Git ignore patterns
│
├── 📄 README.md                   # 📖 Main documentation
├── 📄 SCRIPTS_README.md          # Scripts documentation
└── 📄 PROJECT_STRUCTURE.md       # This file

```

## 🔧 Key Components

### Core Application
- **`app.py`**: Unified Flask application supporting both standard and AI-enhanced analysis
- **`config.py`**: Centralized configuration with environment variable support
- **`analyzer/`**: Modular analysis components with AI capabilities

### 🐳 Docker Infrastructure
- **Production**: Optimized containers with security and performance features
- **Development**: Live-reload containers for rapid development
- **Management**: Comprehensive scripts for easy deployment and maintenance

### 🌐 Web Interface
- **Responsive Design**: Bootstrap-based UI with dark mode support
- **Interactive Dashboard**: Real-time analysis with progress indicators
- **Export Functionality**: JSON, Markdown, and AI Summary export formats
- **Tabbed Results**: Organized presentation of analysis outcomes

### 🧪 Testing & Scripts
- **Automated Testing**: Comprehensive test suite for reliability
- **Deployment Scripts**: Cross-platform scripts for production deployment
- **Testing Utilities**: AI compatibility tests and application validation
- **Management Tools**: Log monitoring and application lifecycle management

## 🚀 Deployment Options

1. **🐳 Docker (Recommended)**
   - Production-ready containers
   - Easy scaling and management
   - Isolated and secure environment

2. **📜 Deployment Scripts**
   - Quick local development
   - Cross-platform compatibility (Windows/Linux/Mac)
   - Automatic dependency management
   - Located in `scripts/deployment/`

3. **🔧 Manual Setup**
   - Direct Python execution
   - Full control over environment
   - Development and testing
   - Development and debugging

## 📊 Features by Directory

| Directory | Purpose | Key Features |
|-----------|---------|--------------|
| `analyzer/` | Core Logic | AI integration, GitHub API, analysis algorithms |
| `docker/` | Containerization | Production deployment, development environment |
| `static/` | Frontend Assets | Responsive design, dark mode, animations |
| `templates/` | Web Interface | Tabbed results, interactive dashboard |
| `tests/` | Quality Assurance | Automated testing, reliability validation |
| `scripts/` | Automation | Management tools, utility functions |

---

**CodePulse: Where Code Analysis Meets Intelligence 🚀📊🧠**