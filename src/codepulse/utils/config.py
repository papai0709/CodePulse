"""
Configuration settings for CodePulse
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration class"""
    
    # Basic Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Analysis configuration
    MAX_REPO_SIZE_MB = int(os.environ.get('MAX_REPO_SIZE_MB', '100'))
    ANALYSIS_TIMEOUT = int(os.environ.get('ANALYSIS_TIMEOUT', '300'))  # 5 minutes
    
    # Test coverage thresholds
    COVERAGE_EXCELLENT = int(os.environ.get('COVERAGE_EXCELLENT', '90'))
    COVERAGE_GOOD = int(os.environ.get('COVERAGE_GOOD', '75'))
    COVERAGE_FAIR = int(os.environ.get('COVERAGE_FAIR', '50'))
    
    # AI Configuration
    AI_MODEL = os.environ.get('AI_MODEL', 'gpt-4o-mini')
    AI_ENDPOINT = os.environ.get('AI_ENDPOINT', 'https://models.inference.ai.azure.com')
    AI_MAX_TOKENS = int(os.environ.get('AI_MAX_TOKENS', '4000'))
    AI_TEMPERATURE = float(os.environ.get('AI_TEMPERATURE', '0.3'))
    AI_TIMEOUT = int(os.environ.get('AI_TIMEOUT', '30'))
    
    # GitHub Models Configuration
    GITHUB_MODELS_ENDPOINT = "https://models.inference.ai.azure.com"
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
    
    # Web server configuration
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', '5050'))
    
    @staticmethod
    def validate():
        """Validate required configuration"""
        # GitHub token is now optional for public repositories
        # But required for AI features
        if Config.ENABLE_AI_FEATURES and not Config.GITHUB_TOKEN:
            print("Warning: AI features are enabled but GITHUB_TOKEN is not set")
            print("AI features will be disabled for this session")
            Config.ENABLE_AI_FEATURES = False
    
    @classmethod
    def get_ai_config(cls) -> dict:
        """Get AI-specific configuration"""
        return {
            'model': cls.AI_MODEL,
            'endpoint': cls.AI_ENDPOINT,
            'max_tokens': cls.AI_MAX_TOKENS,
            'temperature': cls.AI_TEMPERATURE,
            'timeout': cls.AI_TIMEOUT,
            'enabled': cls.ENABLE_AI_FEATURES and bool(cls.GITHUB_TOKEN)
        }