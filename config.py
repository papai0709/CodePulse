import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Analysis configuration
    MAX_REPO_SIZE_MB = 100
    ANALYSIS_TIMEOUT = 300  # 5 minutes
    
    # Test coverage thresholds
    COVERAGE_EXCELLENT = 90
    COVERAGE_GOOD = 75
    COVERAGE_FAIR = 50
    
    # AI Configuration
    AI_MODEL = os.environ.get('AI_MODEL', 'gpt-4o-mini')
    AI_ENDPOINT = os.environ.get('AI_ENDPOINT', 'https://models.github.ai/inference')
    AI_MAX_TOKENS = int(os.environ.get('AI_MAX_TOKENS', '4000'))
    AI_TEMPERATURE = float(os.environ.get('AI_TEMPERATURE', '0.3'))
    AI_TIMEOUT = int(os.environ.get('AI_TIMEOUT', '30'))
    
    # GitHub Models Configuration
    GITHUB_MODELS_ENDPOINT = "https://models.github.ai/inference"
    AVAILABLE_MODELS = [
        "gpt-4o-mini",
        "gpt-4o", 
        "o1-mini",
        "o1-preview",
        "Mistral-large",
        "Mistral-large-2407",
        "Mistral-Nemo"
    ]
    
    # Feature Flags
    ENABLE_AI_FEATURES = os.environ.get('ENABLE_AI_FEATURES', 'True').lower() == 'true'
    ENABLE_CACHING = os.environ.get('ENABLE_CACHING', 'True').lower() == 'true'
    ENABLE_RATE_LIMITING = os.environ.get('ENABLE_RATE_LIMITING', 'True').lower() == 'true'
    
    # Veracode Configuration
    VERACODE_API_ID = os.environ.get('VERACODE_API_ID')
    VERACODE_API_KEY = os.environ.get('VERACODE_API_KEY')
    VERACODE_ENABLED = os.environ.get('VERACODE_ENABLED', 'false').lower() == 'true'
    VERACODE_SCAN_TIMEOUT = int(os.environ.get('VERACODE_SCAN_TIMEOUT', '1800'))
    VERACODE_APPLICATION_PROFILE = os.environ.get('VERACODE_APPLICATION_PROFILE', 'CodePulse_Analysis')
    
    @staticmethod
    def validate():
        """Validate required configuration"""
        # GitHub token is now optional for public repositories
        # But required for AI features
        if Config.ENABLE_AI_FEATURES and not Config.GITHUB_TOKEN:
            print("Warning: AI features are enabled but GITHUB_TOKEN is not set")
            print("AI features will be disabled for this session")
            Config.ENABLE_AI_FEATURES = False
        
        # Veracode validation
        if Config.VERACODE_ENABLED:
            if not Config.VERACODE_API_ID or not Config.VERACODE_API_KEY:
                print("Warning: Veracode is enabled but API credentials are not set")
                print("Veracode scanning will be disabled for this session")
                Config.VERACODE_ENABLED = False