from typing import Dict, Any, List
from datetime import datetime
import json

class ReportGenerator:
    """Generates comprehensive analysis reports"""
    
    def __init__(self):
        self.report_template = {
            'metadata': {},
            'summary': {},
            'test_analysis': {},
            'issues_analysis': {},
            'recommendations': {},
            'scores': {}
        }
    
    def generate_report(self, repo_info: Dict[str, Any], coverage_results: Dict[str, Any], 
                       issues: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        
        report = {
            'metadata': self._generate_metadata(repo_info),
            'summary': self._generate_summary(repo_info, coverage_results, issues),
            'test_analysis': self._generate_test_analysis(coverage_results),
            'issues_analysis': self._generate_issues_analysis(issues),
            'recommendations': self._generate_recommendations(coverage_results, issues),
            'scores': self._calculate_scores(coverage_results, issues),
            'improvement_areas': self._identify_improvement_areas(coverage_results, issues),
            'action_plan': self._create_action_plan(issues)
        }
        
        return report
    
    def _generate_metadata(self, repo_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate report metadata"""
        return {
            'repository': repo_info.get('full_name', 'Unknown'),
            'description': repo_info.get('description', 'No description available'),
            'url': repo_info.get('url', ''),
            'primary_language': repo_info.get('languages', {}).get('primary', 'Unknown'),
            'languages': list(repo_info.get('languages', {}).keys()),
            'stars': repo_info.get('stats', {}).get('stars', 0),
            'forks': repo_info.get('stats', {}).get('forks', 0),
            'contributors': repo_info.get('contributors_count', 0),
            'last_updated': repo_info.get('stats', {}).get('updated_at', ''),
            'analysis_date': datetime.now().isoformat(),
            'license': repo_info.get('license', 'Not specified')
        }
    
    def _generate_summary(self, repo_info: Dict[str, Any], coverage_results: Dict[str, Any], 
                         issues: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary"""
        
        # Calculate overall health score
        health_score = self._calculate_health_score(coverage_results, issues)
        
        # Count issues by severity
        severity_summary = issues.get('severity_summary', {})
        total_issues = sum(severity_summary.values())
        
        # Get test coverage
        coverage = coverage_results.get('coverage_metrics', {}).get('overall', 0)
        
        # Determine status
        if health_score >= 80:
            status = 'Excellent'
            status_color = 'green'
        elif health_score >= 60:
            status = 'Good'
            status_color = 'blue'
        elif health_score >= 40:
            status = 'Fair'
            status_color = 'orange'
        else:
            status = 'Needs Improvement'
            status_color = 'red'
        
        return {
            'health_score': health_score,
            'status': status,
            'status_color': status_color,
            'test_coverage': coverage,
            'total_issues': total_issues,
            'critical_issues': severity_summary.get('critical', 0),
            'high_issues': severity_summary.get('high', 0),
            'medium_issues': severity_summary.get('medium', 0),
            'low_issues': severity_summary.get('low', 0),
            'test_files_count': coverage_results.get('test_files_count', 0),
            'primary_concerns': self._identify_primary_concerns(coverage_results, issues)
        }
    
    def _generate_test_analysis(self, coverage_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed test analysis"""
        
        metrics = coverage_results.get('coverage_metrics', {})
        structure = coverage_results.get('test_structure', {})
        
        # Determine coverage level
        overall_coverage = metrics.get('overall', 0)
        if overall_coverage >= 90:
            coverage_level = 'Excellent'
            coverage_color = 'green'
        elif overall_coverage >= 75:
            coverage_level = 'Good'
            coverage_color = 'blue'
        elif overall_coverage >= 50:
            coverage_level = 'Fair'
            coverage_color = 'orange'
        else:
            coverage_level = 'Poor'
            coverage_color = 'red'
        
        return {
            'coverage_metrics': {
                'overall': overall_coverage,
                'line_coverage': metrics.get('line_coverage', overall_coverage),
                'branch_coverage': metrics.get('branch_coverage', overall_coverage * 0.8),
                'function_coverage': metrics.get('function_coverage', overall_coverage * 0.9)
            },
            'coverage_level': coverage_level,
            'coverage_color': coverage_color,
            'test_structure': {
                'total_files': structure.get('total_test_files', 0),
                'test_directories': structure.get('test_directories', []),
                'test_types': structure.get('test_types', {}),
                'frameworks': structure.get('test_frameworks', []),
                'average_file_size': structure.get('average_test_size', 0)
            },
            'uncovered_areas': coverage_results.get('uncovered_areas', []),
            'recommendations': coverage_results.get('recommendations', [])
        }
    
    def _generate_issues_analysis(self, issues: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed issues analysis"""
        
        return {
            'security': {
                'count': len(issues.get('security_issues', [])),
                'issues': issues.get('security_issues', []),
                'critical_count': len([i for i in issues.get('security_issues', []) 
                                     if i.get('severity') == 'critical'])
            },
            'code_quality': {
                'count': len(issues.get('code_quality_issues', [])),
                'issues': issues.get('code_quality_issues', []),
                'major_issues': [i for i in issues.get('code_quality_issues', []) 
                               if i.get('severity') in ['critical', 'high']]
            },
            'documentation': {
                'count': len(issues.get('documentation_issues', [])),
                'issues': issues.get('documentation_issues', []),
                'missing_items': [i['type'] for i in issues.get('documentation_issues', [])]
            },
            'performance': {
                'count': len(issues.get('performance_issues', [])),
                'issues': issues.get('performance_issues', [])
            },
            'dependencies': {
                'count': len(issues.get('dependency_issues', [])),
                'issues': issues.get('dependency_issues', [])
            },
            'structure': {
                'count': len(issues.get('structure_issues', [])),
                'issues': issues.get('structure_issues', [])
            },
            'maintenance': {
                'count': len(issues.get('maintenance_issues', [])),
                'issues': issues.get('maintenance_issues', [])
            }
        }
    
    def _generate_recommendations(self, coverage_results: Dict[str, Any], 
                                issues: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate comprehensive recommendations"""
        
        recommendations = []
        
        # Test coverage recommendations
        coverage = coverage_results.get('coverage_metrics', {}).get('overall', 0)
        if coverage < 50:
            recommendations.append({
                'category': 'Testing',
                'priority': 'High',
                'title': 'Implement Comprehensive Testing Strategy',
                'description': f'Current test coverage is {coverage}%, which is below acceptable standards.',
                'actions': [
                    'Add unit tests for core business logic',
                    'Implement integration tests for key workflows',
                    'Set up automated test running in CI/CD pipeline',
                    'Aim for minimum 75% test coverage'
                ],
                'estimated_effort': 'High',
                'impact': 'High'
            })
        elif coverage < 75:
            recommendations.append({
                'category': 'Testing',
                'priority': 'Medium',
                'title': 'Improve Test Coverage',
                'description': f'Test coverage at {coverage}% could be improved.',
                'actions': [
                    'Identify and test uncovered code paths',
                    'Add edge case testing',
                    'Implement boundary condition tests'
                ],
                'estimated_effort': 'Medium',
                'impact': 'Medium'
            })
        
        # Security recommendations
        security_issues = issues.get('security_issues', [])
        critical_security = [i for i in security_issues if i.get('severity') == 'critical']
        if critical_security:
            recommendations.append({
                'category': 'Security',
                'priority': 'Critical',
                'title': 'Address Critical Security Vulnerabilities',
                'description': f'Found {len(critical_security)} critical security issues.',
                'actions': [
                    'Remove hardcoded secrets and use environment variables',
                    'Implement parameterized queries to prevent SQL injection',
                    'Sanitize user inputs to prevent XSS attacks',
                    'Conduct security code review'
                ],
                'estimated_effort': 'Medium',
                'impact': 'Critical'
            })
        
        # Documentation recommendations
        doc_issues = issues.get('documentation_issues', [])
        if doc_issues:
            recommendations.append({
                'category': 'Documentation',
                'priority': 'Medium',
                'title': 'Improve Project Documentation',
                'description': f'Found {len(doc_issues)} documentation issues.',
                'actions': [
                    'Add comprehensive README with setup instructions',
                    'Include API documentation',
                    'Add code comments and docstrings',
                    'Create contributor guidelines'
                ],
                'estimated_effort': 'Low',
                'impact': 'Medium'
            })
        
        # Code quality recommendations
        quality_issues = issues.get('code_quality_issues', [])
        if quality_issues:
            long_functions = [i for i in quality_issues if i.get('type') == 'long_function']
            if long_functions:
                recommendations.append({
                    'category': 'Code Quality',
                    'priority': 'Medium',
                    'title': 'Refactor Complex Functions',
                    'description': f'Found {len(long_functions)} functions that are too long.',
                    'actions': [
                        'Break down long functions into smaller, focused functions',
                        'Apply single responsibility principle',
                        'Improve code readability and maintainability'
                    ],
                    'estimated_effort': 'Medium',
                    'impact': 'Medium'
                })
        
        return recommendations
    
    def _calculate_scores(self, coverage_results: Dict[str, Any], 
                         issues: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate various quality scores"""
        
        # Test coverage score
        coverage = coverage_results.get('coverage_metrics', {}).get('overall', 0)
        coverage_score = min(100, coverage * 1.1)  # Slight boost for good coverage
        
        # Security score
        security_issues = issues.get('security_issues', [])
        critical_security = len([i for i in security_issues if i.get('severity') == 'critical'])
        high_security = len([i for i in security_issues if i.get('severity') == 'high'])
        
        security_score = 100
        security_score -= critical_security * 30  # Critical issues heavily penalized
        security_score -= high_security * 15
        security_score = max(0, security_score)
        
        # Documentation score
        doc_issues = issues.get('documentation_issues', [])
        documentation_score = max(0, 100 - len(doc_issues) * 10)
        
        # Code quality score
        quality_issues = issues.get('code_quality_issues', [])
        code_quality_score = max(0, 100 - len(quality_issues) * 5)
        
        # Overall health score
        health_score = (
            coverage_score * 0.3 +
            security_score * 0.3 +
            documentation_score * 0.2 +
            code_quality_score * 0.2
        )
        
        return {
            'health_score': round(health_score, 1),
            'coverage_score': round(coverage_score, 1),
            'security_score': round(security_score, 1),
            'documentation_score': round(documentation_score, 1),
            'code_quality_score': round(code_quality_score, 1)
        }
    
    def _calculate_health_score(self, coverage_results: Dict[str, Any], 
                              issues: Dict[str, Any]) -> float:
        """Calculate overall repository health score"""
        scores = self._calculate_scores(coverage_results, issues)
        return scores['health_score']
    
    def _identify_improvement_areas(self, coverage_results: Dict[str, Any], 
                                  issues: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify key areas for improvement"""
        
        improvement_areas = []
        
        # Test coverage improvements
        coverage = coverage_results.get('coverage_metrics', {}).get('overall', 0)
        if coverage < 75:
            improvement_areas.append({
                'area': 'Test Coverage',
                'current_score': coverage,
                'target_score': 80,
                'priority': 'High' if coverage < 50 else 'Medium',
                'description': 'Increase automated test coverage for better code reliability',
                'key_actions': [
                    'Add unit tests for core functionality',
                    'Implement integration testing',
                    'Set up continuous testing pipeline'
                ]
            })
        
        # Security improvements
        security_issues = issues.get('security_issues', [])
        if security_issues:
            critical_count = len([i for i in security_issues if i.get('severity') == 'critical'])
            improvement_areas.append({
                'area': 'Security',
                'current_score': max(0, 100 - len(security_issues) * 10),
                'target_score': 95,
                'priority': 'Critical' if critical_count > 0 else 'High',
                'description': 'Address security vulnerabilities and implement secure coding practices',
                'key_actions': [
                    'Fix critical security issues immediately',
                    'Implement secure coding guidelines',
                    'Add security testing to CI/CD pipeline'
                ]
            })
        
        # Documentation improvements
        doc_issues = issues.get('documentation_issues', [])
        if len(doc_issues) > 2:
            improvement_areas.append({
                'area': 'Documentation',
                'current_score': max(0, 100 - len(doc_issues) * 10),
                'target_score': 85,
                'priority': 'Medium',
                'description': 'Improve project documentation for better maintainability',
                'key_actions': [
                    'Add comprehensive README',
                    'Document API endpoints',
                    'Include setup and deployment guides'
                ]
            })
        
        return improvement_areas
    
    def _identify_primary_concerns(self, coverage_results: Dict[str, Any], 
                                 issues: Dict[str, Any]) -> List[str]:
        """Identify primary concerns for the repository"""
        
        concerns = []
        
        # Check test coverage
        coverage = coverage_results.get('coverage_metrics', {}).get('overall', 0)
        if coverage < 30:
            concerns.append('Very low test coverage')
        elif coverage < 50:
            concerns.append('Low test coverage')
        
        # Check security issues
        security_issues = issues.get('security_issues', [])
        critical_security = [i for i in security_issues if i.get('severity') == 'critical']
        if critical_security:
            concerns.append('Critical security vulnerabilities')
        elif len(security_issues) > 3:
            concerns.append('Multiple security issues')
        
        # Check documentation
        doc_issues = issues.get('documentation_issues', [])
        missing_readme = any(i.get('type') == 'missing_readme' for i in doc_issues)
        if missing_readme:
            concerns.append('Missing project documentation')
        
        # Check code quality
        quality_issues = issues.get('code_quality_issues', [])
        if len(quality_issues) > 10:
            concerns.append('Code quality issues')
        
        # Check maintenance
        maintenance_issues = issues.get('maintenance_issues', [])
        stale_repo = any(i.get('type') == 'stale_repository' for i in maintenance_issues)
        if stale_repo:
            concerns.append('Repository appears unmaintained')
        
        return concerns[:3]  # Return top 3 concerns
    
    def _create_action_plan(self, issues: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create prioritized action plan"""
        
        action_items = issues.get('action_items', [])
        
        # Add timeline estimates
        for item in action_items:
            if item.get('category') == 'Security':
                item['timeline'] = 'Immediate (1-2 days)'
            elif item.get('priority', 0) <= 2:
                item['timeline'] = 'Short term (1-2 weeks)'
            elif item.get('priority', 0) <= 4:
                item['timeline'] = 'Medium term (1-2 months)'
            else:
                item['timeline'] = 'Long term (3+ months)'
        
        return action_items