import os
import subprocess
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

class TestAnalyzer:
    """Analyzes test coverage and test quality in repositories"""
    
    def __init__(self):
        self.supported_languages = {
            'python': {
                'test_patterns': ['test_*.py', '*_test.py', 'test*.py'],
                'test_directories': ['tests', 'test', 'testing'],
                'coverage_tools': ['coverage', 'pytest-cov'],
                'extensions': ['.py']
            },
            'javascript': {
                'test_patterns': ['*.test.js', '*.spec.js', '*.test.ts', '*.spec.ts'],
                'test_directories': ['test', 'tests', '__tests__', 'spec'],
                'coverage_tools': ['jest', 'nyc', 'c8'],
                'extensions': ['.js', '.ts', '.jsx', '.tsx']
            },
            'java': {
                'test_patterns': ['*Test.java', '*Tests.java'],
                'test_directories': ['src/test', 'test'],
                'coverage_tools': ['jacoco', 'cobertura'],
                'extensions': ['.java']
            },
            'csharp': {
                'test_patterns': ['*Test.cs', '*Tests.cs'],
                'test_directories': ['Tests', 'Test'],
                'coverage_tools': ['coverlet', 'dotcover'],
                'extensions': ['.cs']
            }
        }
    
    def analyze_coverage(self, repo_path: str) -> Dict[str, Any]:
        """Analyze test coverage for the repository"""
        try:
            # Detect primary language
            primary_language = self._detect_primary_language(repo_path)
            
            # Find test files
            test_files = self._find_test_files(repo_path, primary_language)
            
            # Analyze test structure
            test_structure = self._analyze_test_structure(repo_path, test_files)
            
            # Calculate coverage metrics
            coverage_metrics = self._calculate_coverage_metrics(repo_path, primary_language)
            
            # Identify uncovered areas
            uncovered_areas = self._identify_uncovered_areas(repo_path, primary_language)
            
            return {
                'primary_language': primary_language,
                'test_files_count': len(test_files),
                'test_files': test_files,
                'test_structure': test_structure,
                'coverage_metrics': coverage_metrics,
                'uncovered_areas': uncovered_areas,
                'recommendations': self._generate_test_recommendations(test_structure, coverage_metrics)
            }
            
        except Exception as e:
            return {
                'error': f"Coverage analysis failed: {str(e)}",
                'primary_language': 'unknown',
                'test_files_count': 0,
                'coverage_metrics': {'overall': 0}
            }
    
    def _detect_primary_language(self, repo_path: str) -> str:
        """Detect the primary programming language of the repository"""
        language_counts = {}
        
        for root, dirs, files in os.walk(repo_path):
            # Skip hidden directories and common non-source directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv', 'env']]
            
            for file in files:
                file_path = Path(file)
                extension = file_path.suffix.lower()
                
                # Map extensions to languages
                extension_map = {
                    '.py': 'python',
                    '.js': 'javascript',
                    '.ts': 'javascript',
                    '.jsx': 'javascript',
                    '.tsx': 'javascript',
                    '.java': 'java',
                    '.cs': 'csharp',
                    '.cpp': 'cpp',
                    '.c': 'c',
                    '.go': 'go',
                    '.rs': 'rust'
                }
                
                if extension in extension_map:
                    lang = extension_map[extension]
                    language_counts[lang] = language_counts.get(lang, 0) + 1
        
        if not language_counts:
            return 'unknown'
        
        return max(language_counts, key=language_counts.get)
    
    def _find_test_files(self, repo_path: str, language: str) -> List[str]:
        """Find test files in the repository"""
        test_files = []
        
        if language not in self.supported_languages:
            return test_files
        
        config = self.supported_languages[language]
        
        for root, dirs, files in os.walk(repo_path):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            # Check if we're in a test directory
            current_dir = Path(root).name.lower()
            is_test_dir = any(test_dir in current_dir for test_dir in config['test_directories'])
            
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, repo_path)
                
                # Skip __init__.py files
                if file == '__init__.py':
                    continue
                
                # Check if file matches test patterns
                is_test_file = any(self._matches_pattern(file, pattern) for pattern in config['test_patterns'])
                
                if is_test_file or (is_test_dir and file.endswith(tuple(config['extensions']))):
                    test_files.append(relative_path)
        
        return test_files
    
    def _matches_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches the given pattern"""
        import fnmatch
        return fnmatch.fnmatch(filename.lower(), pattern.lower())
    
    def _analyze_test_structure(self, repo_path: str, test_files: List[str]) -> Dict[str, Any]:
        """Analyze the structure and quality of test files with enhanced categorization"""
        structure = {
            'total_test_files': len(test_files),
            'test_directories': set(),
            'test_types': {'unit': 0, 'integration': 0, 'e2e': 0, 'performance': 0, 'unknown': 0},
            'test_frameworks': set(),
            'test_file_sizes': [],
            'average_test_size': 0,
            'test_type_details': {
                'unit': {'files': [], 'characteristics': []},
                'integration': {'files': [], 'characteristics': []},
                'e2e': {'files': [], 'characteristics': []},
                'performance': {'files': [], 'characteristics': []},
                'unknown': {'files': [], 'characteristics': []}
            }
        }
        
        for test_file in test_files:
            full_path = os.path.join(repo_path, test_file)
            
            # Track test directories
            test_dir = str(Path(test_file).parent)
            structure['test_directories'].add(test_dir)
            
            # Analyze test type based on path and content
            test_type = self._classify_test_type(test_file, full_path)
            structure['test_types'][test_type] += 1
            
            # Store detailed information about each test type
            structure['test_type_details'][test_type]['files'].append(test_file)
            characteristics = self._analyze_test_characteristics(full_path)
            structure['test_type_details'][test_type]['characteristics'].extend(characteristics)
            
            # Get file size
            try:
                file_size = os.path.getsize(full_path)
                structure['test_file_sizes'].append(file_size)
            except:
                pass
            
            # Detect test frameworks
            frameworks = self._detect_test_frameworks(full_path)
            structure['test_frameworks'].update(frameworks)
        
        # Calculate average test file size
        if structure['test_file_sizes']:
            structure['average_test_size'] = sum(structure['test_file_sizes']) / len(structure['test_file_sizes'])
        
        # Generate test distribution analysis
        structure['test_distribution'] = self._analyze_test_distribution(structure['test_types'])
        
        # Convert sets to lists for JSON serialization
        structure['test_directories'] = list(structure['test_directories'])
        structure['test_frameworks'] = list(structure['test_frameworks'])
        
        return structure
    
    def _classify_test_type(self, test_file: str, full_path: str) -> str:
        """Classify test type based on file path and content with enhanced detection"""
        file_lower = test_file.lower()
        
        # Enhanced path-based classification
        path_classification = self._classify_by_path(file_lower)
        if path_classification != 'unknown':
            return path_classification
        
        # Enhanced content-based classification
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                return self._classify_by_content(content, test_file)
        except:
            return 'unknown'
    
    def _classify_by_path(self, file_path: str) -> str:
        """Enhanced path-based test classification"""
        # E2E/End-to-End tests
        e2e_patterns = [
            'e2e', 'end-to-end', 'endtoend', 'selenium', 'cypress', 'playwright', 
            'webdriver', 'browser', 'functional', 'acceptance', 'system'
        ]
        
        # Integration test patterns
        integration_patterns = [
            'integration', 'integr', 'int_test', 'api_test', 'service_test',
            'component_test', 'contract_test', 'database_test', 'db_test'
        ]
        
        # Performance test patterns
        performance_patterns = [
            'performance', 'perf', 'load', 'stress', 'benchmark', 'bench'
        ]
        
        # Unit test patterns (most specific last)
        unit_patterns = [
            'unit', 'spec', '_test', 'test_', '.test.', 'tests/'
        ]
        
        # Check patterns in order of specificity
        for pattern in e2e_patterns:
            if pattern in file_path:
                return 'e2e'
                
        for pattern in performance_patterns:
            if pattern in file_path:
                return 'performance'
                
        for pattern in integration_patterns:
            if pattern in file_path:
                return 'integration'
                
        for pattern in unit_patterns:
            if pattern in file_path:
                return 'unit'
                
        return 'unknown'
    
    def _classify_by_content(self, content: str, file_path: str) -> str:
        """Enhanced content-based test classification"""
        content_lower = content.lower()
        
        # Calculate content indicators
        integration_score = self._calculate_integration_score(content, content_lower)
        e2e_score = self._calculate_e2e_score(content, content_lower)
        performance_score = self._calculate_performance_score(content, content_lower)
        unit_score = self._calculate_unit_score(content, content_lower)
        
        # Determine test type based on highest score
        scores = {
            'e2e': e2e_score,
            'performance': performance_score,
            'integration': integration_score,
            'unit': unit_score
        }
        
        max_score = max(scores.values())
        if max_score > 0:
            return max(scores, key=scores.get)
        
        return 'unit'  # Default fallback
    
    def _calculate_integration_score(self, content: str, content_lower: str) -> int:
        """Calculate integration test likelihood score"""
        score = 0
        
        # Database-related patterns
        db_patterns = [
            'database', 'db_', 'session', 'transaction', 'commit', 'rollback',
            'sql', 'query', 'connection', 'cursor', 'migrate', 'schema'
        ]
        
        # API/Service patterns
        api_patterns = [
            'requests.', 'httpx', 'aiohttp', 'urllib', 'rest', 'api',
            'client.', 'service.', 'endpoint', 'response.status', 'json()'
        ]
        
        # External service patterns
        external_patterns = [
            'redis', 'mongodb', 'elasticsearch', 'rabbitmq', 'kafka',
            'aws', 'azure', 'gcp', 's3', 'sqs', 'sns'
        ]
        
        # Configuration/Environment patterns
        config_patterns = [
            'config', 'settings', 'environment', 'env', 'docker',
            'compose', 'container', 'port'
        ]
        
        # Multiple component patterns
        component_patterns = [
            'integration', 'end_to_end', 'workflow', 'pipeline',
            'multiple', 'components', 'services'
        ]
        
        # Count occurrences
        all_patterns = [db_patterns, api_patterns, external_patterns, config_patterns, component_patterns]
        pattern_weights = [3, 2, 3, 1, 2]  # Different weights for different pattern types
        
        for patterns, weight in zip(all_patterns, pattern_weights):
            for pattern in patterns:
                score += content_lower.count(pattern) * weight
        
        # File/network I/O indicators
        io_patterns = ['open(', 'file', 'path', 'directory', 'socket', 'network']
        for pattern in io_patterns:
            score += content_lower.count(pattern)
        
        return score
    
    def _calculate_e2e_score(self, content: str, content_lower: str) -> int:
        """Calculate E2E test likelihood score"""
        score = 0
        
        # Browser automation patterns
        browser_patterns = [
            'selenium', 'webdriver', 'chrome', 'firefox', 'browser',
            'playwright', 'cypress', 'page.', 'click', 'screenshot'
        ]
        
        # UI testing patterns
        ui_patterns = [
            'element', 'button', 'input', 'form', 'submit', 'wait',
            'find_element', 'get_element', 'xpath', 'css_selector'
        ]
        
        # User journey patterns
        journey_patterns = [
            'login', 'logout', 'navigate', 'user_journey', 'workflow',
            'scenario', 'feature', 'story'
        ]
        
        all_patterns = [browser_patterns, ui_patterns, journey_patterns]
        weights = [5, 3, 2]
        
        for patterns, weight in zip(all_patterns, weights):
            for pattern in patterns:
                score += content_lower.count(pattern) * weight
        
        return score
    
    def _calculate_performance_score(self, content: str, content_lower: str) -> int:
        """Calculate performance test likelihood score"""
        score = 0
        
        # Performance testing patterns
        perf_patterns = [
            'time.time', 'timeit', 'benchmark', 'performance', 'load',
            'stress', 'concurrent', 'parallel', 'threads', 'async'
        ]
        
        # Metrics patterns
        metrics_patterns = [
            'latency', 'throughput', 'response_time', 'duration',
            'memory', 'cpu', 'resources'
        ]
        
        all_patterns = [perf_patterns, metrics_patterns]
        
        for patterns in all_patterns:
            for pattern in patterns:
                score += content_lower.count(pattern) * 3
        
        return score
    
    def _calculate_unit_score(self, content: str, content_lower: str) -> int:
        """Calculate unit test likelihood score"""
        score = 0
        
        # Unit test patterns
        unit_patterns = [
            'assert', 'mock', 'patch', 'stub', 'fake', 'unittest',
            'pytest', 'test_', 'should_', 'expect'
        ]
        
        # Isolation patterns
        isolation_patterns = [
            'mock.', '@mock', '@patch', 'mocker', 'monkeypatch',
            'fixture', '@fixture'
        ]
        
        for pattern in unit_patterns:
            score += content_lower.count(pattern) * 2
            
        for pattern in isolation_patterns:
            score += content_lower.count(pattern) * 3
        
        return score
    
    def _detect_test_frameworks(self, file_path: str) -> set:
        """Detect test frameworks used in the file"""
        frameworks = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # Python frameworks
                if 'import pytest' in content or 'from pytest' in content:
                    frameworks.add('pytest')
                if 'import unittest' in content or 'from unittest' in content:
                    frameworks.add('unittest')
                if 'import nose' in content:
                    frameworks.add('nose')
                
                # JavaScript frameworks
                if 'describe(' in content or 'it(' in content:
                    frameworks.add('jest/mocha')
                if '@test' in content:
                    frameworks.add('junit')
                
                # .NET frameworks
                if '[Test]' in content or '[TestMethod]' in content:
                    frameworks.add('nunit/mstest')
        except:
            pass
        
        return frameworks
    
    def _analyze_test_characteristics(self, file_path: str) -> List[str]:
        """Analyze characteristics of a test file"""
        characteristics = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().lower()
                
                # Check for various test characteristics
                if 'mock' in content or 'patch' in content:
                    characteristics.append('uses_mocking')
                if 'database' in content or 'db' in content:
                    characteristics.append('database_interaction')
                if 'api' in content or 'http' in content or 'requests' in content:
                    characteristics.append('api_interaction')
                if 'file' in content or 'path' in content:
                    characteristics.append('file_system_interaction')
                if 'async' in content or 'await' in content:
                    characteristics.append('async_testing')
                if 'parametrize' in content or 'parameterized' in content:
                    characteristics.append('parameterized_tests')
                if 'fixture' in content:
                    characteristics.append('uses_fixtures')
                    
        except:
            pass
            
        return characteristics
    
    def _analyze_test_distribution(self, test_types: Dict[str, int]) -> Dict[str, Any]:
        """Analyze the distribution of test types"""
        total_tests = sum(test_types.values())
        
        if total_tests == 0:
            return {
                'total': 0,
                'percentages': {},
                'balance_score': 0,
                'recommendations': ['No tests found']
            }
        
        # Calculate percentages
        percentages = {
            test_type: (count / total_tests) * 100 
            for test_type, count in test_types.items()
        }
        
        # Calculate balance score (optimal distribution: 70% unit, 20% integration, 10% e2e)
        optimal_distribution = {'unit': 70, 'integration': 20, 'e2e': 10, 'performance': 0, 'unknown': 0}
        
        balance_score = 100
        for test_type in ['unit', 'integration', 'e2e']:
            actual = percentages.get(test_type, 0)
            optimal = optimal_distribution[test_type]
            deviation = abs(actual - optimal)
            balance_score -= deviation * 0.5  # Reduce score based on deviation
        
        balance_score = max(0, balance_score)
        
        # Generate recommendations
        recommendations = []
        if percentages.get('unit', 0) < 50:
            recommendations.append('Increase unit test coverage - aim for 70% of total tests')
        if percentages.get('integration', 0) < 10:
            recommendations.append('Add integration tests to verify component interactions')
        if percentages.get('integration', 0) > 40:
            recommendations.append('Consider converting some integration tests to faster unit tests')
        if percentages.get('e2e', 0) > 20:
            recommendations.append('Reduce E2E tests - they should be 5-10% of total tests')
        if percentages.get('unknown', 0) > 10:
            recommendations.append('Improve test naming and organization for better classification')
        
        return {
            'total': total_tests,
            'percentages': percentages,
            'balance_score': round(balance_score, 1),
            'recommendations': recommendations
        }
    
    def _calculate_coverage_metrics(self, repo_path: str, language: str) -> Dict[str, Any]:
        """Calculate test coverage metrics"""
        metrics = {
            'overall': 0,
            'line_coverage': 0,
            'branch_coverage': 0,
            'function_coverage': 0,
            'class_coverage': 0,
            'estimated': True,
            'tool_used': 'analysis'
        }
        
        # Try to run actual coverage analysis for Python
        if language == 'python':
            python_metrics = self._run_python_coverage(repo_path)
            if python_metrics:
                metrics.update(python_metrics)
                metrics['estimated'] = False
                return metrics
        
        # Estimate coverage based on test file analysis
        estimated_coverage = self._estimate_coverage(repo_path, language)
        metrics.update(estimated_coverage)
        
        return metrics
    
    def _run_python_coverage(self, repo_path: str) -> Optional[Dict[str, Any]]:
        """Run actual Python coverage analysis"""
        try:
            # Check if coverage tools are available
            result = subprocess.run(['python', '-m', 'coverage', '--version'], 
                                  capture_output=True, text=True, cwd=repo_path, timeout=10)
            
            if result.returncode != 0:
                return None
            
            # Run coverage analysis
            subprocess.run(['python', '-m', 'coverage', 'run', '-m', 'pytest'], 
                          capture_output=True, cwd=repo_path, timeout=60)
            
            # Get coverage report
            result = subprocess.run(['python', '-m', 'coverage', 'report', '--format=json'], 
                                  capture_output=True, text=True, cwd=repo_path, timeout=30)
            
            if result.returncode == 0:
                coverage_data = json.loads(result.stdout)
                return {
                    'overall': coverage_data.get('totals', {}).get('percent_covered', 0),
                    'line_coverage': coverage_data.get('totals', {}).get('percent_covered', 0),
                    'tool_used': 'coverage.py'
                }
        except:
            pass
        
        return None
    
    def _estimate_coverage(self, repo_path: str, language: str) -> Dict[str, Any]:
        """Estimate coverage based on code analysis"""
        source_files = self._find_source_files(repo_path, language)
        test_files = self._find_test_files(repo_path, language)
        
        if not source_files:
            return {'overall': 0}
        
        # Simple heuristic: ratio of test files to source files
        test_ratio = len(test_files) / len(source_files) if source_files else 0
        
        # Estimate based on test file ratio and quality
        if test_ratio >= 0.8:
            estimated_coverage = min(85, 60 + (test_ratio * 30))
        elif test_ratio >= 0.5:
            estimated_coverage = min(70, 40 + (test_ratio * 40))
        elif test_ratio >= 0.3:
            estimated_coverage = min(50, 20 + (test_ratio * 50))
        else:
            estimated_coverage = min(30, test_ratio * 60)
        
        return {
            'overall': round(estimated_coverage, 1),
            'line_coverage': round(estimated_coverage * 0.9, 1),
            'branch_coverage': round(estimated_coverage * 0.7, 1),
            'function_coverage': round(estimated_coverage * 0.8, 1)
        }
    
    def _find_source_files(self, repo_path: str, language: str) -> List[str]:
        """Find source code files (non-test files)"""
        if language not in self.supported_languages:
            return []
        
        config = self.supported_languages[language]
        source_files = []
        test_files = set(self._find_test_files(repo_path, language))
        
        for root, dirs, files in os.walk(repo_path):
            # Skip hidden and common non-source directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in 
                      ['node_modules', '__pycache__', 'venv', 'env', 'dist', 'build']]
            
            for file in files:
                if file.endswith(tuple(config['extensions'])):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, repo_path)
                    
                    # Exclude test files
                    if relative_path not in test_files:
                        source_files.append(relative_path)
        
        return source_files
    
    def _identify_uncovered_areas(self, repo_path: str, language: str) -> List[Dict[str, Any]]:
        """Identify areas that likely lack test coverage"""
        uncovered_areas = []
        source_files = self._find_source_files(repo_path, language)
        test_files = self._find_test_files(repo_path, language)
        
        # Find source files without corresponding test files
        for source_file in source_files:
            has_test = self._has_corresponding_test(source_file, test_files)
            if not has_test:
                uncovered_areas.append({
                    'type': 'missing_test_file',
                    'file': source_file,
                    'description': f'No test file found for {source_file}',
                    'priority': 'high' if self._is_core_file(source_file) else 'medium'
                })
        
        return uncovered_areas
    
    def _has_corresponding_test(self, source_file: str, test_files: List[str]) -> bool:
        """Check if source file has a corresponding test file"""
        source_name = Path(source_file).stem
        
        for test_file in test_files:
            test_name = Path(test_file).stem
            if source_name.lower() in test_name.lower() or test_name.lower() in source_name.lower():
                return True
        
        return False
    
    def _is_core_file(self, file_path: str) -> bool:
        """Determine if a file is a core/important file"""
        core_indicators = ['main', 'app', 'index', 'server', 'api', 'service', 'controller', 'model']
        file_name = Path(file_path).stem.lower()
        
        return any(indicator in file_name for indicator in core_indicators)
    
    def _generate_test_recommendations(self, structure: Dict, metrics: Dict) -> List[Dict[str, str]]:
        """Generate enhanced recommendations for improving test coverage and distribution"""
        recommendations = []
        
        coverage = metrics.get('overall', 0)
        test_distribution = structure.get('test_distribution', {})
        test_types = structure.get('test_types', {})
        
        # Coverage-based recommendations
        if coverage < 30:
            recommendations.append({
                'type': 'critical',
                'title': 'Very Low Test Coverage',
                'description': 'Test coverage is below 30%. Consider implementing a comprehensive testing strategy.',
                'action': 'Start by adding unit tests for core functionality and critical business logic.'
            })
        elif coverage < 50:
            recommendations.append({
                'type': 'warning',
                'title': 'Low Test Coverage',
                'description': 'Test coverage is below 50%. Add more unit tests to improve code reliability.',
                'action': 'Focus on testing public APIs and error handling scenarios.'
            })
        elif coverage < 75:
            recommendations.append({
                'type': 'info',
                'title': 'Moderate Test Coverage',
                'description': 'Test coverage is moderate. Consider adding integration tests and edge case testing.',
                'action': 'Add tests for complex interactions and boundary conditions.'
            })
        
        # Enhanced test type distribution recommendations
        percentages = test_distribution.get('percentages', {})
        
        # Unit test recommendations
        unit_percentage = percentages.get('unit', 0)
        if unit_percentage < 50:
            recommendations.append({
                'type': 'warning' if unit_percentage < 30 else 'suggestion',
                'title': 'Insufficient Unit Tests',
                'description': f'Unit tests represent only {unit_percentage:.1f}% of your test suite. Aim for 60-70%.',
                'action': 'Add more unit tests to test individual functions and classes in isolation.'
            })
        
        # Integration test recommendations
        integration_percentage = percentages.get('integration', 0)
        integration_count = test_types.get('integration', 0)
        
        if integration_count == 0:
            recommendations.append({
                'type': 'suggestion',
                'title': 'Add Integration Tests',
                'description': 'No integration tests detected. These verify component interactions.',
                'action': 'Create integration tests for API endpoints, database operations, and service interactions.'
            })
        elif integration_percentage < 10:
            recommendations.append({
                'type': 'info',
                'title': 'Low Integration Test Coverage',
                'description': f'Integration tests are {integration_percentage:.1f}% of your suite. Consider adding more.',
                'action': 'Add tests for workflows involving multiple components or external dependencies.'
            })
        elif integration_percentage > 40:
            recommendations.append({
                'type': 'warning',
                'title': 'Too Many Integration Tests',
                'description': f'Integration tests represent {integration_percentage:.1f}% of tests. This may slow execution.',
                'action': 'Consider converting some integration tests to faster unit tests where possible.'
            })
        
        # E2E test recommendations
        e2e_percentage = percentages.get('e2e', 0)
        e2e_count = test_types.get('e2e', 0)
        
        if e2e_count > 0 and e2e_percentage > 20:
            recommendations.append({
                'type': 'warning',
                'title': 'Too Many E2E Tests',
                'description': f'E2E tests are {e2e_percentage:.1f}% of your suite. Aim for 5-10% maximum.',
                'action': 'Keep E2E tests for critical user journeys only. Move detailed testing to unit/integration levels.'
            })
        elif e2e_count == 0 and test_distribution.get('total', 0) > 20:
            recommendations.append({
                'type': 'info',
                'title': 'Consider E2E Tests',
                'description': 'No end-to-end tests found. Consider adding a few for critical user flows.',
                'action': 'Add E2E tests for main user journeys and business-critical workflows.'
            })
        
        # Performance test recommendations
        performance_count = test_types.get('performance', 0)
        if performance_count == 0 and test_distribution.get('total', 0) > 50:
            recommendations.append({
                'type': 'info',
                'title': 'Consider Performance Tests',
                'description': 'No performance tests detected. Consider adding them for critical operations.',
                'action': 'Add performance tests for time-critical operations and resource-intensive functions.'
            })
        
        # Framework recommendations
        frameworks = structure.get('test_frameworks', [])
        if len(frameworks) == 0:
            recommendations.append({
                'type': 'warning',
                'title': 'No Test Framework Detected',
                'description': 'No recognized test framework found. Consider adopting a standard testing framework.',
                'action': 'Choose and implement a test framework appropriate for your language.'
            })
        elif len(frameworks) > 2:
            recommendations.append({
                'type': 'suggestion',
                'title': 'Multiple Test Frameworks',
                'description': f'Multiple frameworks detected: {", ".join(frameworks)}. Consider standardizing.',
                'action': 'Standardize on one primary test framework to reduce complexity and maintenance overhead.'
            })
        
        # Test organization recommendations
        unknown_percentage = percentages.get('unknown', 0)
        if unknown_percentage > 15:
            recommendations.append({
                'type': 'suggestion',
                'title': 'Improve Test Organization',
                'description': f'{unknown_percentage:.1f}% of tests could not be properly categorized.',
                'action': 'Use clearer naming conventions and organize tests in appropriate directories.'
            })
        
        # Test balance score recommendations
        balance_score = test_distribution.get('balance_score', 0)
        if balance_score < 50:
            recommendations.append({
                'type': 'suggestion',
                'title': 'Improve Test Distribution Balance',
                'description': f'Test distribution balance score: {balance_score}/100. Consider rebalancing test types.',
                'action': 'Follow the test pyramid: mostly unit tests, some integration tests, few E2E tests.'
            })
        
        return recommendations