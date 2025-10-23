import os
import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from config import Config

class IssueDetector:
    """Detects various issues in code repositories and suggests corrections"""
    
    def __init__(self):
        # Initialize Veracode analyzer if enabled
        self.veracode_analyzer = None
        if Config.VERACODE_ENABLED:
            try:
                from .veracode_analyzer import VeracodeAnalyzer
                self.veracode_analyzer = VeracodeAnalyzer()
            except ImportError:
                # Veracode analyzer not available
                self.veracode_analyzer = None
        
        self.issue_patterns = {
            'security': {
                'hardcoded_secrets': [
                    r'password\s*=\s*["\'][^"\']+["\']',
                    r'api_key\s*=\s*["\'][^"\']+["\']',
                    r'secret\s*=\s*["\'][^"\']+["\']',
                    r'token\s*=\s*["\'][^"\']+["\']'
                ],
                'sql_injection': [
                    r'execute\s*\(\s*["\'].*\+.*["\']',
                    r'query\s*\(\s*["\'].*\+.*["\']'
                ],
                'xss_vulnerabilities': [
                    r'innerHTML\s*=\s*.*\+',
                    r'document\.write\s*\(',
                    r'eval\s*\('
                ]
            },
            'code_quality': {
                'long_functions': 50,  # lines
                'deep_nesting': 5,     # levels
                'magic_numbers': r'\b\d{3,}\b',
                'todo_comments': r'(TODO|FIXME|HACK|XXX)',
                'dead_code': r'#.*dead|#.*unused|#.*remove'
            },
            'documentation': {
                'missing_docstrings': True,
                'missing_readme': True,
                'missing_license': True,
                'outdated_dependencies': True
            },
            'performance': {
                'inefficient_loops': [
                    r'for.*in.*range\(len\(',
                    r'while.*len\('
                ],
                'memory_leaks': [
                    r'global\s+\w+\s*=\s*\[\]',
                    r'cache\s*=\s*\{\}'
                ]
            }
        }
    
    def detect_issues(self, repo_path: str, repo_info: Dict[str, Any]) -> Dict[str, Any]:
        """Detect various issues in the repository"""
        try:
            issues = {
                'security_issues': self._detect_security_issues(repo_path),
                'code_quality_issues': self._detect_code_quality_issues(repo_path),
                'documentation_issues': self._detect_documentation_issues(repo_path, repo_info),
                'performance_issues': self._detect_performance_issues(repo_path),
                'dependency_issues': self._detect_dependency_issues(repo_path),
                'structure_issues': self._detect_structure_issues(repo_path),
                'maintenance_issues': self._detect_maintenance_issues(repo_info)
            }
            
            # Add Veracode security issues if available
            # Note: Veracode analysis is async and handled in enhanced report generator
            # Here we just mark that Veracode results should be included if available
            issues['veracode_integration_enabled'] = self.veracode_analyzer is not None
            
            # Calculate severity scores
            issues['severity_summary'] = self._calculate_severity_summary(issues)
            
            # Generate prioritized action items
            issues['action_items'] = self._generate_action_items(issues)
            
            return issues
            
        except Exception as e:
            return {
                'error': f"Issue detection failed: {str(e)}",
                'security_issues': [],
                'code_quality_issues': [],
                'documentation_issues': [],
                'performance_issues': [],
                'dependency_issues': [],
                'structure_issues': [],
                'maintenance_issues': []
            }
    
    def _detect_security_issues(self, repo_path: str) -> List[Dict[str, Any]]:
        """Detect security-related issues"""
        security_issues = []
        
        for root, dirs, files in os.walk(repo_path):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.java', '.cs', '.php')):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, repo_path)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            lines = content.split('\n')
                            
                            # Check for hardcoded secrets
                            for i, line in enumerate(lines, 1):
                                for pattern in self.issue_patterns['security']['hardcoded_secrets']:
                                    if re.search(pattern, line, re.IGNORECASE):
                                        security_issues.append({
                                            'type': 'hardcoded_secret',
                                            'severity': 'critical',
                                            'file': relative_path,
                                            'line': i,
                                            'description': 'Potential hardcoded secret detected',
                                            'suggestion': 'Move secrets to environment variables or secure configuration'
                                        })
                            
                            # Check for SQL injection vulnerabilities
                            for i, line in enumerate(lines, 1):
                                for pattern in self.issue_patterns['security']['sql_injection']:
                                    if re.search(pattern, line, re.IGNORECASE):
                                        security_issues.append({
                                            'type': 'sql_injection',
                                            'severity': 'critical',
                                            'file': relative_path,
                                            'line': i,
                                            'description': 'Potential SQL injection vulnerability',
                                            'suggestion': 'Use parameterized queries or ORM methods'
                                        })
                            
                            # Check for XSS vulnerabilities
                            for i, line in enumerate(lines, 1):
                                for pattern in self.issue_patterns['security']['xss_vulnerabilities']:
                                    if re.search(pattern, line):
                                        security_issues.append({
                                            'type': 'xss_vulnerability',
                                            'severity': 'high',
                                            'file': relative_path,
                                            'line': i,
                                            'description': 'Potential XSS vulnerability',
                                            'suggestion': 'Sanitize user input and use safe DOM manipulation methods'
                                        })
                    except:
                        continue
        
        return security_issues
    
    def _detect_code_quality_issues(self, repo_path: str) -> List[Dict[str, Any]]:
        """Detect code quality issues"""
        quality_issues = []
        
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.java', '.cs')):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, repo_path)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            lines = content.split('\n')
                            
                            # Check for long functions
                            function_lines = self._count_function_lines(lines, file)
                            for func_name, line_count, start_line in function_lines:
                                if line_count > self.issue_patterns['code_quality']['long_functions']:
                                    quality_issues.append({
                                        'type': 'long_function',
                                        'severity': 'medium',
                                        'file': relative_path,
                                        'line': start_line,
                                        'description': f'Function "{func_name}" has {line_count} lines',
                                        'suggestion': 'Consider breaking down into smaller functions'
                                    })
                            
                            # Check for TODO comments
                            for i, line in enumerate(lines, 1):
                                if re.search(self.issue_patterns['code_quality']['todo_comments'], line):
                                    quality_issues.append({
                                        'type': 'todo_comment',
                                        'severity': 'low',
                                        'file': relative_path,
                                        'line': i,
                                        'description': 'TODO/FIXME comment found',
                                        'suggestion': 'Address pending tasks or create proper issues'
                                    })
                            
                            # Check for magic numbers
                            for i, line in enumerate(lines, 1):
                                matches = re.findall(self.issue_patterns['code_quality']['magic_numbers'], line)
                                if matches and not re.search(r'#.*\d+', line):  # Ignore comments
                                    quality_issues.append({
                                        'type': 'magic_number',
                                        'severity': 'low',
                                        'file': relative_path,
                                        'line': i,
                                        'description': f'Magic number(s) found: {", ".join(matches)}',
                                        'suggestion': 'Replace with named constants'
                                    })
                    except:
                        continue
        
        return quality_issues
    
    def _detect_documentation_issues(self, repo_path: str, repo_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect documentation-related issues"""
        doc_issues = []
        
        # Check for README
        readme_files = ['README.md', 'README.rst', 'README.txt', 'README']
        has_readme = any(os.path.exists(os.path.join(repo_path, readme)) for readme in readme_files)
        
        if not has_readme:
            doc_issues.append({
                'type': 'missing_readme',
                'severity': 'medium',
                'file': 'root',
                'description': 'No README file found',
                'suggestion': 'Add a comprehensive README.md with project description, setup instructions, and usage examples'
            })
        
        # Check for LICENSE
        license_files = ['LICENSE', 'LICENSE.md', 'LICENSE.txt', 'COPYING']
        has_license = any(os.path.exists(os.path.join(repo_path, license_file)) for license_file in license_files)
        
        if not has_license and not repo_info.get('license'):
            doc_issues.append({
                'type': 'missing_license',
                'severity': 'medium',
                'file': 'root',
                'description': 'No license file found',
                'suggestion': 'Add an appropriate license file (MIT, Apache 2.0, GPL, etc.)'
            })
        
        # Check for API documentation
        api_doc_files = ['docs/', 'documentation/', 'api/', 'swagger.yaml', 'openapi.yaml']
        has_api_docs = any(os.path.exists(os.path.join(repo_path, doc_path)) for doc_path in api_doc_files)
        
        if not has_api_docs:
            doc_issues.append({
                'type': 'missing_api_docs',
                'severity': 'low',
                'file': 'root',
                'description': 'No API documentation found',
                'suggestion': 'Consider adding API documentation using tools like Swagger/OpenAPI'
            })
        
        # Check for missing docstrings in Python files
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, repo_path)
                    
                    missing_docstrings = self._check_python_docstrings(file_path)
                    for item in missing_docstrings:
                        doc_issues.append({
                            'type': 'missing_docstring',
                            'severity': 'low',
                            'file': relative_path,
                            'line': item['line'],
                            'description': f'Missing docstring for {item["type"]}: {item["name"]}',
                            'suggestion': 'Add comprehensive docstrings following PEP 257'
                        })
        
        return doc_issues
    
    def _detect_performance_issues(self, repo_path: str) -> List[Dict[str, Any]]:
        """Detect potential performance issues"""
        performance_issues = []
        
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if file.endswith(('.py', '.js', '.ts')):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, repo_path)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            lines = content.split('\n')
                            
                            # Check for inefficient loops
                            for i, line in enumerate(lines, 1):
                                for pattern in self.issue_patterns['performance']['inefficient_loops']:
                                    if re.search(pattern, line):
                                        performance_issues.append({
                                            'type': 'inefficient_loop',
                                            'severity': 'medium',
                                            'file': relative_path,
                                            'line': i,
                                            'description': 'Potentially inefficient loop pattern',
                                            'suggestion': 'Consider using enumerate() or direct iteration'
                                        })
                            
                            # Check for potential memory leaks
                            for i, line in enumerate(lines, 1):
                                for pattern in self.issue_patterns['performance']['memory_leaks']:
                                    if re.search(pattern, line):
                                        performance_issues.append({
                                            'type': 'memory_leak_risk',
                                            'severity': 'medium',
                                            'file': relative_path,
                                            'line': i,
                                            'description': 'Potential memory leak: global mutable default',
                                            'suggestion': 'Use None as default and initialize inside function'
                                        })
                    except:
                        continue
        
        return performance_issues
    
    def _detect_dependency_issues(self, repo_path: str) -> List[Dict[str, Any]]:
        """Detect dependency-related issues"""
        dependency_issues = []
        
        # Check Python dependencies
        requirements_files = ['requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile']
        python_deps = None
        
        for req_file in requirements_files:
            req_path = os.path.join(repo_path, req_file)
            if os.path.exists(req_path):
                python_deps = req_file
                break
        
        if not python_deps:
            # Check if Python files exist
            has_python = any(file.endswith('.py') for root, dirs, files in os.walk(repo_path) for file in files)
            if has_python:
                dependency_issues.append({
                    'type': 'missing_requirements',
                    'severity': 'medium',
                    'file': 'root',
                    'description': 'Python project without dependency management',
                    'suggestion': 'Add requirements.txt or pyproject.toml for dependency management'
                })
        
        # Check JavaScript dependencies
        package_json_path = os.path.join(repo_path, 'package.json')
        if os.path.exists(package_json_path):
            try:
                with open(package_json_path, 'r') as f:
                    package_data = json.loads(f.read())
                    
                # Check for missing package-lock.json or yarn.lock
                has_lockfile = (os.path.exists(os.path.join(repo_path, 'package-lock.json')) or 
                               os.path.exists(os.path.join(repo_path, 'yarn.lock')))
                
                if not has_lockfile:
                    dependency_issues.append({
                        'type': 'missing_lockfile',
                        'severity': 'medium',
                        'file': 'package.json',
                        'description': 'No lock file found for JavaScript dependencies',
                        'suggestion': 'Commit package-lock.json or yarn.lock for reproducible builds'
                    })
            except:
                pass
        else:
            # Check if JavaScript files exist
            has_js = any(file.endswith(('.js', '.ts', '.jsx', '.tsx')) 
                        for root, dirs, files in os.walk(repo_path) for file in files)
            if has_js:
                dependency_issues.append({
                    'type': 'missing_package_json',
                    'severity': 'medium',
                    'file': 'root',
                    'description': 'JavaScript project without package.json',
                    'suggestion': 'Add package.json for dependency and script management'
                })
        
        return dependency_issues
    
    def _detect_structure_issues(self, repo_path: str) -> List[Dict[str, Any]]:
        """Detect project structure issues"""
        structure_issues = []
        
        # Check for proper project structure
        root_files = os.listdir(repo_path)
        
        # Check for scattered files in root
        code_files_in_root = [f for f in root_files if f.endswith(('.py', '.js', '.ts', '.java', '.cs'))]
        if len(code_files_in_root) > 3:  # Allow a few main files
            structure_issues.append({
                'type': 'scattered_files',
                'severity': 'low',
                'file': 'root',
                'description': f'{len(code_files_in_root)} code files in root directory',
                'suggestion': 'Organize code files into appropriate directories (src/, lib/, etc.)'
            })
        
        # Check for missing .gitignore
        if '.gitignore' not in root_files:
            structure_issues.append({
                'type': 'missing_gitignore',
                'severity': 'low',
                'file': 'root',
                'description': 'No .gitignore file found',
                'suggestion': 'Add .gitignore to exclude build artifacts, dependencies, and sensitive files'
            })
        
        # Check for appropriate directory structure
        common_dirs = ['src', 'lib', 'tests', 'test', 'docs', 'documentation']
        has_organized_structure = any(d in root_files for d in common_dirs)
        
        if not has_organized_structure and len(code_files_in_root) > 5:
            structure_issues.append({
                'type': 'poor_organization',
                'severity': 'medium',
                'file': 'root',
                'description': 'Project lacks organized directory structure',
                'suggestion': 'Create organized directories for source code, tests, and documentation'
            })
        
        return structure_issues
    
    def _detect_maintenance_issues(self, repo_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect maintenance-related issues"""
        maintenance_issues = []
        
        # Check last update time
        last_updated = repo_info.get('stats', {}).get('updated_at')
        if last_updated:
            try:
                from datetime import datetime
                last_update_date = datetime.strptime(last_updated.split('T')[0], '%Y-%m-%d')
                days_since_update = (datetime.now() - last_update_date).days
                
                if days_since_update > 365:
                    maintenance_issues.append({
                        'type': 'stale_repository',
                        'severity': 'medium',
                        'file': 'repository',
                        'description': f'Repository not updated for {days_since_update} days',
                        'suggestion': 'Consider archiving if no longer maintained, or update dependencies and documentation'
                    })
                elif days_since_update > 180:
                    maintenance_issues.append({
                        'type': 'infrequent_updates',
                        'severity': 'low',
                        'file': 'repository',
                        'description': f'Repository not updated for {days_since_update} days',
                        'suggestion': 'Consider regular maintenance and dependency updates'
                    })
            except:
                pass
        
        # Check open issues ratio
        open_issues = repo_info.get('open_issues', 0)
        if open_issues > 20:
            maintenance_issues.append({
                'type': 'high_open_issues',
                'severity': 'medium',
                'file': 'repository',
                'description': f'{open_issues} open issues',
                'suggestion': 'Address or triage open issues to improve project health'
            })
        
        return maintenance_issues
    
    def _count_function_lines(self, lines: List[str], filename: str) -> List[tuple]:
        """Count lines in functions for different languages"""
        function_data = []
        
        if filename.endswith('.py'):
            function_data = self._count_python_function_lines(lines)
        elif filename.endswith(('.js', '.ts')):
            function_data = self._count_js_function_lines(lines)
        
        return function_data
    
    def _count_python_function_lines(self, lines: List[str]) -> List[tuple]:
        """Count lines in Python functions"""
        functions = []
        current_function = None
        function_start = 0
        indent_level = 0
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Find function definition
            if stripped.startswith('def ') and ':' in stripped:
                if current_function:
                    # End previous function
                    functions.append((current_function, i - function_start, function_start + 1))
                
                # Start new function
                current_function = stripped.split('(')[0].replace('def ', '')
                function_start = i
                indent_level = len(line) - len(line.lstrip())
            
            elif current_function and stripped and not line.startswith(' ' * (indent_level + 1)) and not stripped.startswith('#'):
                # Function ended
                if not stripped.startswith('def '):
                    functions.append((current_function, i - function_start, function_start + 1))
                    current_function = None
        
        # Handle last function
        if current_function:
            functions.append((current_function, len(lines) - function_start, function_start + 1))
        
        return functions
    
    def _count_js_function_lines(self, lines: List[str]) -> List[tuple]:
        """Count lines in JavaScript/TypeScript functions"""
        functions = []
        brace_count = 0
        current_function = None
        function_start = 0
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Find function definition
            if ('function ' in stripped or '=>' in stripped) and '{' in stripped:
                if current_function is None:
                    # Extract function name
                    if 'function ' in stripped:
                        func_match = re.search(r'function\s+(\w+)', stripped)
                        current_function = func_match.group(1) if func_match else 'anonymous'
                    else:
                        current_function = 'arrow_function'
                    
                    function_start = i
                    brace_count = stripped.count('{') - stripped.count('}')
            
            elif current_function:
                brace_count += stripped.count('{') - stripped.count('}')
                
                if brace_count <= 0:
                    # Function ended
                    functions.append((current_function, i - function_start + 1, function_start + 1))
                    current_function = None
                    brace_count = 0
        
        return functions
    
    def _check_python_docstrings(self, file_path: str) -> List[Dict[str, Any]]:
        """Check for missing docstrings in Python files"""
        missing_docstrings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines):
                stripped = line.strip()
                
                # Check for class definitions
                if stripped.startswith('class ') and ':' in stripped:
                    class_name = stripped.split('(')[0].replace('class ', '').strip()
                    if not self._has_docstring(lines, i + 1):
                        missing_docstrings.append({
                            'type': 'class',
                            'name': class_name,
                            'line': i + 1
                        })
                
                # Check for function definitions
                elif stripped.startswith('def ') and ':' in stripped:
                    func_name = stripped.split('(')[0].replace('def ', '').strip()
                    if not func_name.startswith('_') and not self._has_docstring(lines, i + 1):
                        missing_docstrings.append({
                            'type': 'function',
                            'name': func_name,
                            'line': i + 1
                        })
        except:
            pass
        
        return missing_docstrings
    
    def _has_docstring(self, lines: List[str], start_line: int) -> bool:
        """Check if there's a docstring after the definition"""
        if start_line >= len(lines):
            return False
        
        # Look for docstring in next few lines
        for i in range(start_line, min(start_line + 3, len(lines))):
            stripped = lines[i].strip()
            if stripped.startswith('"""') or stripped.startswith("'''"):
                return True
        
        return False
    
    def _calculate_severity_summary(self, issues: Dict[str, Any]) -> Dict[str, int]:
        """Calculate summary of issue severities"""
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        
        for category, issue_list in issues.items():
            if isinstance(issue_list, list):
                for issue in issue_list:
                    if isinstance(issue, dict) and 'severity' in issue:
                        severity = issue['severity']
                        if severity in severity_counts:
                            severity_counts[severity] += 1
        
        return severity_counts
    
    def _generate_action_items(self, issues: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate prioritized action items based on detected issues"""
        action_items = []
        
        # Security issues - highest priority
        security_issues = issues.get('security_issues', [])
        if security_issues:
            critical_security = [i for i in security_issues if i.get('severity') == 'critical']
            if critical_security:
                action_items.append({
                    'priority': 1,
                    'category': 'Security',
                    'title': 'Address Critical Security Issues',
                    'description': f'Found {len(critical_security)} critical security issues',
                    'action': 'Immediately review and fix hardcoded secrets, SQL injection, and XSS vulnerabilities',
                    'impact': 'High - Security vulnerabilities can lead to data breaches'
                })
        
        # Test coverage - high priority
        coverage_issues = []
        for category in ['code_quality_issues', 'structure_issues']:
            coverage_issues.extend([i for i in issues.get(category, []) if 'test' in i.get('description', '').lower()])
        
        if coverage_issues:
            action_items.append({
                'priority': 2,
                'category': 'Testing',
                'title': 'Improve Test Coverage',
                'description': 'Low test coverage detected',
                'action': 'Add unit tests for core functionality and critical business logic',
                'impact': 'Medium - Poor test coverage increases bug risk'
            })
        
        # Documentation - medium priority
        doc_issues = issues.get('documentation_issues', [])
        if doc_issues:
            action_items.append({
                'priority': 3,
                'category': 'Documentation',
                'title': 'Improve Documentation',
                'description': f'Found {len(doc_issues)} documentation issues',
                'action': 'Add README, license, and code documentation',
                'impact': 'Medium - Poor documentation reduces maintainability'
            })
        
        # Code quality - medium priority
        quality_issues = issues.get('code_quality_issues', [])
        if quality_issues:
            high_impact_quality = [i for i in quality_issues if i.get('type') in ['long_function', 'deep_nesting']]
            if high_impact_quality:
                action_items.append({
                    'priority': 4,
                    'category': 'Code Quality',
                    'title': 'Refactor Complex Code',
                    'description': f'Found {len(high_impact_quality)} complex code issues',
                    'action': 'Break down long functions and reduce nesting complexity',
                    'impact': 'Medium - Complex code is harder to maintain and debug'
                })
        
        # Dependencies - lower priority
        dep_issues = issues.get('dependency_issues', [])
        if dep_issues:
            action_items.append({
                'priority': 5,
                'category': 'Dependencies',
                'title': 'Improve Dependency Management',
                'description': f'Found {len(dep_issues)} dependency issues',
                'action': 'Add proper dependency management files and lock files',
                'impact': 'Low - Improves build reproducibility'
            })
        
        return action_items
    
    def merge_veracode_issues(self, existing_issues: Dict[str, Any], 
                             veracode_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge Veracode security issues with existing issues
        
        Args:
            existing_issues: Current issues detected by CodePulse
            veracode_analysis: Veracode analysis results
            
        Returns:
            Updated issues dictionary with Veracode findings integrated
        """
        if not veracode_analysis or not veracode_analysis.get('security_issues'):
            return existing_issues
        
        # Get Veracode security issues
        veracode_security_issues = veracode_analysis.get('security_issues', [])
        
        # Merge with existing security issues
        existing_security_issues = existing_issues.get('security_issues', [])
        
        # Add Veracode issues to security issues
        merged_security_issues = existing_security_issues + veracode_security_issues
        
        # Update the issues dictionary
        updated_issues = existing_issues.copy()
        updated_issues['security_issues'] = merged_security_issues
        updated_issues['veracode_security_issues'] = veracode_security_issues
        updated_issues['veracode_analysis_available'] = True
        
        # Recalculate severity summary with Veracode findings
        updated_issues['severity_summary'] = self._calculate_severity_summary(updated_issues)
        
        # Regenerate action items with Veracode findings
        updated_issues['action_items'] = self._generate_action_items(updated_issues)
        
        return updated_issues