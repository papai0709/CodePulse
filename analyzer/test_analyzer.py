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
        """Analyze the structure and quality of test files"""
        structure = {
            'total_test_files': len(test_files),
            'test_directories': set(),
            'test_types': {'unit': 0, 'integration': 0, 'e2e': 0, 'unknown': 0},
            'test_frameworks': set(),
            'test_file_sizes': [],
            'average_test_size': 0
        }
        
        for test_file in test_files:
            full_path = os.path.join(repo_path, test_file)
            
            # Track test directories
            test_dir = str(Path(test_file).parent)
            structure['test_directories'].add(test_dir)
            
            # Analyze test type based on path and content
            test_type = self._classify_test_type(test_file, full_path)
            structure['test_types'][test_type] += 1
            
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
        
        # Convert sets to lists for JSON serialization
        structure['test_directories'] = list(structure['test_directories'])
        structure['test_frameworks'] = list(structure['test_frameworks'])
        
        return structure
    
    def _classify_test_type(self, test_file: str, full_path: str) -> str:
        """Classify test type based on file path and content"""
        file_lower = test_file.lower()
        
        if 'integration' in file_lower or 'int' in file_lower:
            return 'integration'
        elif 'e2e' in file_lower or 'end-to-end' in file_lower or 'selenium' in file_lower:
            return 'e2e'
        elif 'unit' in file_lower or '/test' in file_lower or '\\test' in file_lower:
            return 'unit'
        
        # Analyze content for more clues
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().lower()
                if 'selenium' in content or 'webdriver' in content:
                    return 'e2e'
                elif 'integration' in content:
                    return 'integration'
                else:
                    return 'unit'
        except:
            return 'unknown'
    
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
        """Generate recommendations for improving test coverage"""
        recommendations = []
        
        coverage = metrics.get('overall', 0)
        
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
        
        if structure['test_types']['integration'] == 0:
            recommendations.append({
                'type': 'suggestion',
                'title': 'Add Integration Tests',
                'description': 'No integration tests detected. Consider adding tests for component interactions.',
                'action': 'Create integration tests for key workflows and data flows.'
            })
        
        if len(structure['test_frameworks']) == 0:
            recommendations.append({
                'type': 'warning',
                'title': 'No Test Framework Detected',
                'description': 'No recognized test framework found. Consider adopting a standard testing framework.',
                'action': 'Choose and implement a test framework appropriate for your language.'
            })
        
        return recommendations