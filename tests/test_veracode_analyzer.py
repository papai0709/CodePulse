"""
Comprehensive Test Suite for Veracode Analyzer
Tests Veracode API integration, mock responses, error handling, and fallback mechanisms
"""

import pytest
import asyncio
import tempfile
import shutil
import os
import json
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime, timedelta

# Test imports
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analyzer.veracode_analyzer import VeracodeAnalyzer


class TestVeracodeAnalyzer:
    """Test cases for Veracode Analyzer functionality"""
    
    def setup_method(self):
        """Set up test fixtures before each test method"""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_path = self.temp_dir
        self.repo_name = "test-repo"
        
        # Create sample repository structure
        os.makedirs(os.path.join(self.temp_dir, "src"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "tests"), exist_ok=True)
        
        # Create sample Python files
        with open(os.path.join(self.temp_dir, "src", "main.py"), "w") as f:
            f.write("""
def main():
    # Sample code with potential security issue
    import os
    password = os.environ.get('PASSWORD', 'default123')  # Hardcoded default password
    return password

if __name__ == "__main__":
    main()
""")
        
        with open(os.path.join(self.temp_dir, "requirements.txt"), "w") as f:
            f.write("flask==2.3.0\nrequests==2.31.0\n")
    
    def teardown_method(self):
        """Clean up test fixtures after each test method"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_veracode_analyzer_initialization_without_credentials(self):
        """Test VeracodeAnalyzer initialization when credentials are not available"""
        with patch('analyzer.veracode_analyzer.Config.VERACODE_API_ID', None):
            with patch('analyzer.veracode_analyzer.Config.VERACODE_API_KEY', None):
                analyzer = VeracodeAnalyzer()
                assert not analyzer.is_available
                assert analyzer.veracode_api is None
    
    def test_veracode_analyzer_initialization_with_credentials(self):
        """Test VeracodeAnalyzer initialization when credentials are available"""
        with patch('analyzer.veracode_analyzer.Config.VERACODE_API_ID', 'test_id'):
            with patch('analyzer.veracode_analyzer.Config.VERACODE_API_KEY', 'test_key'):
                with patch('analyzer.veracode_analyzer.VERACODE_AVAILABLE', True):
                    with patch('analyzer.veracode_analyzer.VeracodeAPI') as mock_api:
                        mock_api.return_value = Mock()
                        analyzer = VeracodeAnalyzer()
                        assert analyzer.is_available
                        assert analyzer.veracode_api is not None
    
    def test_veracode_analyzer_initialization_import_error(self):
        """Test VeracodeAnalyzer initialization when veracode-api-py is not available"""
        with patch('analyzer.veracode_analyzer.VERACODE_AVAILABLE', False):
            analyzer = VeracodeAnalyzer()
            assert not analyzer.is_available
            assert analyzer.veracode_api is None
    
    @pytest.mark.asyncio
    async def test_analyze_repository_not_available(self):
        """Test repository analysis when Veracode is not available"""
        with patch('analyzer.veracode_analyzer.Config.VERACODE_API_ID', None):
            analyzer = VeracodeAnalyzer()
            result = await analyzer.analyze_repository(self.repo_path, self.repo_name)
            
            assert result is not None
            assert result['analysis_type'] == 'veracode_static_analysis'
            assert 'security_score' in result
            assert isinstance(result['security_score'], int)
            assert 0 <= result['security_score'] <= 100
            assert 'vulnerability_categories' in result
            assert 'security_issues' in result
            assert 'recommendations' in result
    
    @pytest.mark.asyncio
    async def test_analyze_repository_success(self):
        """Test successful repository analysis with mocked Veracode API"""
        mock_scan_results = {
            'security_score': 85,
            'total_findings': 5,
            'critical_flaws': 1,
            'high_severity': 2,
            'vulnerabilities': [
                {
                    'category': 'SQL Injection',
                    'severity': 'High',
                    'count': 1,
                    'description': 'Potential SQL injection vulnerability'
                },
                {
                    'category': 'Cross-Site Scripting',
                    'severity': 'Medium',
                    'count': 2,
                    'description': 'XSS vulnerability detected'
                }
            ],
            'compliance': {
                'owasp': True,
                'pci_dss': False,
                'hipaa': True
            }
        }
        
        with patch('analyzer.veracode_analyzer.Config.VERACODE_API_ID', 'test_id'):
            with patch('analyzer.veracode_analyzer.Config.VERACODE_API_KEY', 'test_key'):
                with patch('analyzer.veracode_analyzer.VERACODE_AVAILABLE', True):
                    with patch('analyzer.veracode_analyzer.VeracodeAPI') as mock_api:
                        mock_client = Mock()
                        mock_api.return_value = mock_client
                        
                        analyzer = VeracodeAnalyzer()
                        
                        # Mock the scanning process
                        with patch.object(analyzer, '_upload_for_scanning', return_value='scan_123'):
                            with patch.object(analyzer, '_monitor_scan_progress', return_value=True):
                                with patch.object(analyzer, '_parse_veracode_results', return_value=mock_scan_results):
                                    
                                    result = await analyzer.analyze_repository(self.repo_path, self.repo_name)
                                    
                                    assert result is not None
                                    assert result['status'] == 'completed'
                                    assert result['security_score'] == 85
                                    assert result['summary']['total_findings'] == 5
                                    assert result['summary']['critical_flaws'] == 1
                                    assert len(result['vulnerability_categories']) == 2
                                    assert result['compliance']['owasp'] is True
    
    @pytest.mark.asyncio
    async def test_analyze_repository_scan_failure(self):
        """Test repository analysis when scan fails"""
        with patch('analyzer.veracode_analyzer.Config.VERACODE_API_ID', 'test_id'):
            with patch('analyzer.veracode_analyzer.Config.VERACODE_API_KEY', 'test_key'):
                with patch('analyzer.veracode_analyzer.VERACODE_AVAILABLE', True):
                    with patch('analyzer.veracode_analyzer.VeracodeAPI') as mock_api:
                        mock_client = Mock()
                        mock_api.return_value = mock_client
                        
                        analyzer = VeracodeAnalyzer()
                        
                        # Mock scanning failure
                        with patch.object(analyzer, '_upload_for_scanning', side_effect=Exception("Upload failed")):
                            result = await analyzer.analyze_repository(self.repo_path, self.repo_name)
                            
                            assert result is not None
                            assert result['status'] == 'error'
                            assert 'error' in result
                            assert result['security_score'] == 50  # Default score on error
    
    def test_prepare_scan_package(self):
        """Test scan package preparation"""
        with patch('analyzer.veracode_analyzer.Config.VERACODE_API_ID', 'test_id'):
            with patch('analyzer.veracode_analyzer.Config.VERACODE_API_KEY', 'test_key'):
                with patch('analyzer.veracode_analyzer.VERACODE_AVAILABLE', True):
                    with patch('analyzer.veracode_analyzer.VeracodeAPI') as mock_api:
                        mock_api.return_value = Mock()
                        analyzer = VeracodeAnalyzer()
                        
                        package_path = analyzer._prepare_scan_package(self.repo_path, self.repo_name)
                        
                        assert package_path is not None
                        assert package_path.endswith('.zip')
                        assert os.path.exists(package_path)
                        
                        # Clean up created file
                        if os.path.exists(package_path):
                            os.remove(package_path)
    
    def test_prepare_scan_package_empty_directory(self):
        """Test scan package preparation with empty directory"""
        empty_dir = tempfile.mkdtemp()
        try:
            with patch('analyzer.veracode_analyzer.Config.VERACODE_API_ID', 'test_id'):
                with patch('analyzer.veracode_analyzer.Config.VERACODE_API_KEY', 'test_key'):
                    with patch('analyzer.veracode_analyzer.VERACODE_AVAILABLE', True):
                        with patch('analyzer.veracode_analyzer.VeracodeAPI') as mock_api:
                            mock_api.return_value = Mock()
                            analyzer = VeracodeAnalyzer()
                            
                            package_path = analyzer._prepare_scan_package(empty_dir, "empty-repo")
                            
                            assert package_path is not None
                            assert package_path.endswith('.zip')
                            assert os.path.exists(package_path)
                            
                            # Clean up
                            if os.path.exists(package_path):
                                os.remove(package_path)
        finally:
            shutil.rmtree(empty_dir)
    
    def test_generate_mock_scan_results(self):
        """Test mock scan results generation"""
        with patch('analyzer.veracode_analyzer.Config.VERACODE_API_ID', None):
            analyzer = VeracodeAnalyzer()
            
            mock_results = analyzer._generate_mock_scan_results(self.repo_name)
            
            assert mock_results is not None
            assert 'scan_id' in mock_results
            assert 'findings' in mock_results
            assert 'scan_date' in mock_results
            assert isinstance(mock_results['findings'], list)
    
    def test_generate_error_scan_results(self):
        """Test error scan results generation"""
        with patch('analyzer.veracode_analyzer.Config.VERACODE_API_ID', 'test_id'):
            with patch('analyzer.veracode_analyzer.Config.VERACODE_API_KEY', 'test_key'):
                with patch('analyzer.veracode_analyzer.VERACODE_AVAILABLE', True):
                    with patch('analyzer.veracode_analyzer.VeracodeAPI') as mock_api:
                        mock_api.return_value = Mock()
                        analyzer = VeracodeAnalyzer()
                        
                        error_results = analyzer._fallback_veracode_analysis("Test error message", self.repo_name)
                        
                        assert error_results is not None
                        assert error_results['analysis_type'] == 'fallback_analysis'
                        assert error_results['error_message'] == "Test error message"
                        assert error_results['security_score'] == 75
                        assert 'scan_summary' in error_results


class TestVeracodeAnalyzerIntegration:
    """Integration tests for Veracode Analyzer with real-world scenarios"""
    
    def setup_method(self):
        """Set up integration test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.create_sample_project()
    
    def teardown_method(self):
        """Clean up integration test fixtures"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def create_sample_project(self):
        """Create a more realistic sample project for integration testing"""
        # Create directory structure
        dirs = ['src', 'tests', 'config', 'static', 'templates']
        for directory in dirs:
            os.makedirs(os.path.join(self.temp_dir, directory), exist_ok=True)
        
        # Create Python files with various security patterns
        files_content = {
            'src/main.py': '''
import os
import hashlib
import sqlite3
from flask import Flask, request, render_template

app = Flask(__name__)

# Security issue: hardcoded secret
SECRET_KEY = "hardcoded-secret-key-123"

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    # Security issue: SQL injection vulnerability
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    
    # Security issue: weak password hashing
    password_hash = hashlib.md5(password.encode()).hexdigest()
    
    return "Login successful"

@app.route('/file')
def serve_file():
    filename = request.args.get('filename')
    # Security issue: path traversal vulnerability
    return open(f"/uploads/{filename}").read()

if __name__ == '__main__':
    app.run(debug=True)  # Security issue: debug mode in production
''',
            'src/database.py': '''
import sqlite3
import os

class Database:
    def __init__(self):
        # Security issue: database file permissions
        self.db_path = "/tmp/database.db"
        os.chmod(self.db_path, 0o777)
    
    def execute_query(self, query, params=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            # Security issue: allowing direct query execution
            cursor.execute(query)
        
        return cursor.fetchall()
''',
            'config/settings.py': '''
import os

class Config:
    # Security issue: sensitive data in configuration
    DATABASE_URL = "postgresql://admin:password123@localhost/mydb"
    API_KEY = "sk-1234567890abcdef"
    
    # Security issue: allowing all hosts
    ALLOWED_HOSTS = ['*']
    
    # Good practice
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
''',
            'requirements.txt': '''
flask==1.1.1
sqlite3
requests==2.25.1
jinja2==2.11.3
''',
            'setup.py': '''
from setuptools import setup, find_packages

setup(
    name="vulnerable-app",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "flask==1.1.1",
        "requests==2.25.1"
    ]
)
'''
        }
        
        for filepath, content in files_content.items():
            full_path = os.path.join(self.temp_dir, filepath)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)
    
    @pytest.mark.asyncio
    async def test_comprehensive_analysis_mock_mode(self):
        """Test comprehensive analysis in mock mode with realistic project"""
        with patch('analyzer.veracode_analyzer.Config.VERACODE_API_ID', None):
            analyzer = VeracodeAnalyzer()
            result = await analyzer.analyze_repository(self.temp_dir, "vulnerable-app")
            
            # Verify mock analysis structure
            assert result is not None
            assert result['analysis_type'] == 'veracode_static_analysis'
            assert isinstance(result['security_score'], int)
            assert 0 <= result['security_score'] <= 100
            
            # Verify all required sections are present
            required_sections = ['vulnerability_categories', 'security_issues', 'compliance_status', 'recommendations']
            for section in required_sections:
                assert section in result
                assert result[section] is not None
            
            # Verify scan summary structure
            scan_summary = result['scan_summary']
            assert 'status' in scan_summary
            assert 'duration_minutes' in scan_summary
            assert 'files_scanned' in scan_summary
            
            # Verify vulnerability categories
            assert isinstance(result['vulnerability_categories'], list)
            
            # Verify compliance status
            compliance_status = result['compliance_status']
            assert isinstance(compliance_status, dict)
            assert 'status' in compliance_status
            
            # Verify recommendations
            recommendations = result['recommendations']
            assert isinstance(recommendations, list)


# Test utilities and fixtures
@pytest.fixture
def sample_veracode_response():
    """Fixture providing sample Veracode API response"""
    return {
        'scan_id': 'scan_12345',
        'findings': [
            {
                'category': 'SQL Injection',
                'severity': 'High',
                'description': 'SQL injection vulnerability detected in login function',
                'file': 'src/main.py',
                'line': 15,
                'cwe_id': 89
            },
            {
                'category': 'Hardcoded Credentials',
                'severity': 'Critical',
                'description': 'Hardcoded secret key found in source code',
                'file': 'src/main.py',
                'line': 8,
                'cwe_id': 798
            },
            {
                'category': 'Path Traversal',
                'severity': 'High',
                'description': 'Path traversal vulnerability in file serving endpoint',
                'file': 'src/main.py',
                'line': 28,
                'cwe_id': 22
            }
        ],
        'summary': {
            'total_findings': 3,
            'critical_flaws': 1,
            'high_severity': 2,
            'medium_severity': 0,
            'low_severity': 0
        },
        'compliance': {
            'owasp_top_10': False,
            'pci_dss': False,
            'hipaa': False,
            'sox': False
        },
        'scan_info': {
            'scan_date': '2024-01-15T14:30:00Z',
            'duration': '12m 45s',
            'files_scanned': 8,
            'lines_of_code': 150
        }
    }


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])