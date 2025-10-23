"""
Enhanced Report Generator with AI Insights
Integrates traditional analysis with AI-powered recommendations and insights
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import asyncio
import logging
from .report_generator import ReportGenerator
from .ai_analyzer import AIAnalyzer
from .veracode_analyzer import VeracodeAnalyzer
from config import Config

# Configure logger for Enhanced Report Generator
logger = logging.getLogger(__name__)

class EnhancedReportGenerator(ReportGenerator):
    """Enhanced report generator with AI insights and Veracode security analysis"""
    
    def __init__(self, github_token: Optional[str] = None):
        super().__init__()
        self.ai_analyzer = AIAnalyzer(github_token)
        
        # Initialize Veracode analyzer if enabled
        self.veracode_analyzer = None
        if Config.VERACODE_ENABLED:
            self.veracode_analyzer = VeracodeAnalyzer()
            logger.info(f"🔒 Veracode analyzer initialized: {self.veracode_analyzer.is_available}")
        
        logger.info(f"🧠 Enhanced Report Generator initialized with AI support: {bool(github_token)}")
        
    async def generate_enhanced_report(self, repo_info: Dict[str, Any], 
                                     coverage_results: Dict[str, Any], 
                                     issues: Dict[str, Any],
                                     repo_path: str = None,
                                     enable_ai: bool = False) -> Dict[str, Any]:
        """Generate comprehensive analysis report with optional AI insights and Veracode security analysis"""
        repo_name = repo_info.get('name', 'Unknown')
        logger.info(f"📊 Generating enhanced report for {repo_name} (AI enabled: {enable_ai})")
        
        # Generate base report
        logger.info("📋 Generating base report")
        base_report = self.generate_report(repo_info, coverage_results, issues)
        logger.info("✅ Base report generated successfully")
        
        # Add AI insights if enabled
        if enable_ai:
            try:
                logger.info("🧠 Starting AI insights generation")
                ai_insights = await self._generate_ai_insights(
                    repo_info, coverage_results, issues
                )
                base_report['ai_insights'] = ai_insights
                logger.info(f"✅ AI insights generated with {len(ai_insights)} components")
                
                logger.info("💡 Generating AI recommendations")
                base_report['enhanced_recommendations'] = await self._generate_ai_recommendations(
                    base_report, ai_insights
                )
                logger.info("✅ AI recommendations generated")
                
                # Generate AI summary for template display
                logger.info("📊 Generating AI summary")
                base_report['ai_summary'] = self.generate_ai_summary(ai_insights)
                logger.info(f"✅ AI summary generated - Overall score: {base_report['ai_summary'].get('overall_ai_score', 0):.1f}/10")
                
                base_report['ai_enabled'] = True
                logger.info(f"🎉 Enhanced report completed successfully for {repo_name}")
            except Exception as e:
                logger.error(f"❌ AI analysis failed for {repo_name}: {str(e)}", exc_info=True)
                base_report['ai_error'] = f"AI analysis failed: {str(e)}"
                base_report['ai_enabled'] = False
        else:
            logger.info("📊 AI features disabled, using standard report")
            base_report['ai_enabled'] = False
            
        # Add Veracode security analysis if enabled and repo_path is provided
        if self.veracode_analyzer and repo_path:
            try:
                logger.info("🔒 Starting Veracode security analysis")
                veracode_analysis = await self.veracode_analyzer.analyze_repository(repo_path, repo_name)
                base_report['veracode_analysis'] = veracode_analysis
                
                # Update security score with Veracode results
                if 'scores' in base_report and veracode_analysis.get('security_score') is not None:
                    # Use the lower of existing security score and Veracode score
                    existing_score = base_report['scores'].get('security_score', 100)
                    veracode_score = veracode_analysis.get('security_score', 100)
                    base_report['scores']['security_score'] = min(existing_score, veracode_score)
                    base_report['scores']['veracode_score'] = veracode_score
                
                base_report['veracode_enabled'] = True
                logger.info(f"✅ Veracode analysis completed - Security score: {veracode_analysis.get('security_score', 'N/A')}")
                
            except Exception as e:
                logger.error(f"❌ Veracode analysis failed for {repo_name}: {str(e)}", exc_info=True)
                base_report['veracode_error'] = f"Veracode analysis failed: {str(e)}"
                base_report['veracode_enabled'] = False
        else:
            if self.veracode_analyzer:
                logger.info("⚠️ Veracode analyzer available but repo_path not provided")
            else:
                logger.info("📊 Veracode analysis disabled")
            base_report['veracode_enabled'] = False
            
        return base_report
    
    async def _generate_ai_insights(self, repo_info: Dict[str, Any], 
                                   coverage_results: Dict[str, Any], 
                                   issues: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-powered insights about the repository"""
        repo_name = repo_info.get('name', 'Unknown')
        logger.info(f"🔍 Generating AI insights for {repo_name}")
        
        insights = {}
        
        try:
            # Architecture analysis
            logger.info("🏗️ Starting architecture analysis")
            insights['architecture'] = await self.ai_analyzer.analyze_architecture(
                repo_info, coverage_results, issues
            )
            logger.info(f"✅ Architecture analysis completed - Score: {insights['architecture'].get('architecture_score', 'N/A')}")
            
            # Code quality insights
            logger.info("🔍 Starting code quality analysis")
            # Code quality insights
            logger.info("🔍 Starting code quality analysis")
            insights['code_quality'] = await self.ai_analyzer.analyze_code_quality(
                issues,
                coverage_results
            )
            logger.info(f"✅ Code quality analysis completed - Score: {insights['code_quality'].get('score', 'N/A')}")
            
            # Performance analysis
            logger.info("⚡ Starting performance analysis")
            insights['performance'] = await self.ai_analyzer.analyze_performance_patterns(
                repo_info.get('file_structure', {}),
                issues
            )
            logger.info(f"✅ Performance analysis completed - Score: {insights['performance'].get('score', 'N/A')}")
            
            # Security assessment
            logger.info("🔒 Starting security analysis")
            insights['security'] = await self.ai_analyzer.analyze_security(
                issues,
                repo_info.get('dependencies', [])
            )
            logger.info(f"✅ Security analysis completed - Risk Score: {insights['security'].get('risk_score', 'N/A')}")
            
            logger.info(f"✅ All AI insights generated successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to generate AI insights: {str(e)}", exc_info=True)
            insights['error'] = f"Failed to generate AI insights: {str(e)}"
            
        return insights
    
    async def _generate_ai_recommendations(self, base_report: Dict[str, Any], 
                                         ai_insights: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-enhanced recommendations"""
        
        recommendations = {
            'priority_actions': [],
            'quick_wins': [],
            'long_term_goals': [],
            'technology_upgrades': [],
            'security_improvements': [],
            'performance_optimizations': [],
            'code_quality_enhancements': []
        }
        
        try:
            # Priority actions based on critical issues and AI analysis
            if base_report.get('summary', {}).get('critical_issues', 0) > 0:
                recommendations['priority_actions'].extend([
                    {
                        'title': 'Address Critical Security Issues',
                        'description': 'Fix critical security vulnerabilities immediately',
                        'effort': 'High',
                        'impact': 'Critical',
                        'ai_confidence': 0.95
                    }
                ])
            
            # Architecture improvements
            if 'architecture' in ai_insights:
                arch_insights = ai_insights['architecture']
                if arch_insights.get('complexity_score', 0) > 7:
                    recommendations['long_term_goals'].append({
                        'title': 'Refactor Complex Components',
                        'description': arch_insights.get('recommendations', ['Consider breaking down complex modules']),
                        'effort': 'High',
                        'impact': 'High',
                        'ai_confidence': arch_insights.get('confidence', 0.8)
                    })
            
            # Quick wins from AI analysis
            if base_report.get('summary', {}).get('test_coverage', 0) < 70:
                recommendations['quick_wins'].append({
                    'title': 'Improve Test Coverage',
                    'description': 'Add unit tests for uncovered components',
                    'effort': 'Medium',
                    'impact': 'High',
                    'ai_confidence': 0.9,
                    'suggested_files': self._suggest_test_files(base_report)
                })
            
            # Technology upgrades
            if 'technology_stack' in ai_insights:
                tech_insights = ai_insights['technology_stack']
                if tech_insights.get('outdated_dependencies'):
                    recommendations['technology_upgrades'].extend([
                        {
                            'title': f'Update {dep}',
                            'description': f'Upgrade to latest version for security and performance',
                            'effort': 'Low',
                            'impact': 'Medium',
                            'ai_confidence': 0.85
                        } for dep in tech_insights['outdated_dependencies'][:3]
                    ])
            
            # Security improvements
            if 'security' in ai_insights:
                sec_insights = ai_insights['security']
                if sec_insights.get('risk_score', 0) > 6:
                    recommendations['security_improvements'].extend(
                        sec_insights.get('recommendations', [])
                    )
            
            # Performance optimizations
            if 'performance' in ai_insights:
                perf_insights = ai_insights['performance']
                recommendations['performance_optimizations'].extend(
                    perf_insights.get('optimizations', [])
                )
            
            # Code quality enhancements
            if 'code_quality' in ai_insights:
                quality_insights = ai_insights['code_quality']
                recommendations['code_quality_enhancements'].extend(
                    quality_insights.get('improvements', [])
                )
                
        except Exception as e:
            recommendations['error'] = f"Failed to generate AI recommendations: {str(e)}"
            
        return recommendations
    
    def _suggest_test_files(self, report: Dict[str, Any]) -> List[str]:
        """Suggest files that need test coverage"""
        suggestions = []
        
        # Get uncovered files from coverage analysis
        test_analysis = report.get('test_analysis', {})
        uncovered_files = test_analysis.get('uncovered_files', [])
        
        # Prioritize critical files
        critical_extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.c']
        for file in uncovered_files[:5]:  # Top 5 suggestions
            if any(file.endswith(ext) for ext in critical_extensions):
                suggestions.append(file)
                
        return suggestions
    
    def generate_ai_summary(self, ai_insights: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of AI insights"""
        
        summary = {
            'overall_ai_score': 0,
            'key_findings': [],
            'confidence_level': 'medium',
            'insights_count': 0
        }
        
        try:
            # Calculate overall AI score
            scores = []
            insights_count = 0
            
            for category, insights in ai_insights.items():
                if isinstance(insights, dict):
                    # Check for different score field names
                    score = None
                    if 'score' in insights:
                        score = insights['score']
                    elif 'architecture_score' in insights:
                        score = insights['architecture_score']
                    elif 'quality_score' in insights:
                        score = insights['quality_score']
                    
                    if score is not None:
                        scores.append(score)
                        insights_count += 1
                    
                    # Add key findings
                    if insights.get('key_findings'):
                        summary['key_findings'].extend(insights['key_findings'][:2])
            
            if scores:
                summary['overall_ai_score'] = sum(scores) / len(scores)
                summary['insights_count'] = insights_count
                
                # Determine confidence level
                avg_confidence = sum(
                    insights.get('confidence', 0.5) 
                    for insights in ai_insights.values() 
                    if isinstance(insights, dict)
                ) / len(ai_insights)
                
                if avg_confidence > 0.8:
                    summary['confidence_level'] = 'high'
                elif avg_confidence > 0.6:
                    summary['confidence_level'] = 'medium'
                else:
                    summary['confidence_level'] = 'low'
                    
        except Exception as e:
            summary['error'] = f"Failed to generate AI summary: {str(e)}"
            
        return summary
    
    def generate_enhanced_action_plan(self, enhanced_recommendations: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate prioritized action plan based on AI recommendations"""
        
        action_plan = []
        
        try:
            # Priority 1: Critical issues
            for action in enhanced_recommendations.get('priority_actions', []):
                action_plan.append({
                    'priority': 1,
                    'category': 'Critical',
                    'title': action['title'],
                    'description': action['description'],
                    'effort': action['effort'],
                    'impact': action['impact'],
                    'ai_enhanced': True,
                    'confidence': action.get('ai_confidence', 0.8)
                })
            
            # Priority 2: Quick wins
            for action in enhanced_recommendations.get('quick_wins', []):
                action_plan.append({
                    'priority': 2,
                    'category': 'Quick Win',
                    'title': action['title'],
                    'description': action['description'],
                    'effort': action['effort'],
                    'impact': action['impact'],
                    'ai_enhanced': True,
                    'confidence': action.get('ai_confidence', 0.8)
                })
            
            # Priority 3: Security improvements
            for action in enhanced_recommendations.get('security_improvements', [])[:3]:
                if isinstance(action, dict):
                    action_plan.append({
                        'priority': 3,
                        'category': 'Security',
                        'title': action.get('title', 'Security Improvement'),
                        'description': action.get('description', 'Enhance security measures'),
                        'effort': action.get('effort', 'Medium'),
                        'impact': action.get('impact', 'High'),
                        'ai_enhanced': True,
                        'confidence': action.get('confidence', 0.8)
                    })
            
            # Priority 4: Performance optimizations
            for action in enhanced_recommendations.get('performance_optimizations', [])[:2]:
                if isinstance(action, dict):
                    action_plan.append({
                        'priority': 4,
                        'category': 'Performance',
                        'title': action.get('title', 'Performance Optimization'),
                        'description': action.get('description', 'Optimize performance'),
                        'effort': action.get('effort', 'Medium'),
                        'impact': action.get('impact', 'Medium'),
                        'ai_enhanced': True,
                        'confidence': action.get('confidence', 0.7)
                    })
            
            # Sort by priority and confidence
            action_plan.sort(key=lambda x: (x['priority'], -x['confidence']))
            
        except Exception as e:
            action_plan.append({
                'priority': 999,
                'category': 'Error',
                'title': 'Action Plan Generation Failed',
                'description': f"Failed to generate enhanced action plan: {str(e)}",
                'effort': 'Unknown',
                'impact': 'Unknown',
                'ai_enhanced': False,
                'confidence': 0.0
            })
            
        return action_plan[:10]  # Limit to top 10 actions
    
    def export_enhanced_report(self, report: Dict[str, Any], format: str = 'json') -> str:
        """Export enhanced report in various formats"""
        
        if format.lower() == 'json':
            return json.dumps(report, indent=2, default=str)
        elif format.lower() == 'markdown':
            return self._generate_markdown_report(report)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _generate_markdown_report(self, report: Dict[str, Any]) -> str:
        """Generate markdown formatted report"""
        
        md_content = []
        
        # Header
        metadata = report.get('metadata', {})
        md_content.append(f"# CodePulse Analysis Report")
        md_content.append(f"**Repository:** {metadata.get('repository', 'Unknown')}")
        md_content.append(f"**Analysis Date:** {metadata.get('analysis_date', 'Unknown')}")
        md_content.append("")
        
        # Summary
        summary = report.get('summary', {})
        md_content.append("## Executive Summary")
        md_content.append(f"**Health Score:** {summary.get('health_score', 0)}/100")
        md_content.append(f"**Status:** {summary.get('status', 'Unknown')}")
        md_content.append(f"**Test Coverage:** {summary.get('test_coverage', 0):.1f}%")
        md_content.append("")
        
        # AI Insights (if available)
        if report.get('ai_enabled') and 'ai_insights' in report:
            md_content.append("## AI-Powered Insights")
            ai_summary = self.generate_ai_summary(report['ai_insights'])
            md_content.append(f"**AI Score:** {ai_summary.get('overall_ai_score', 0):.1f}/10")
            md_content.append(f"**Confidence Level:** {ai_summary.get('confidence_level', 'medium').title()}")
            
            if ai_summary.get('key_findings'):
                md_content.append("### Key Findings")
                for finding in ai_summary['key_findings']:
                    md_content.append(f"- {finding}")
                md_content.append("")
        
        # Action Plan
        if 'enhanced_recommendations' in report:
            action_plan = self.generate_enhanced_action_plan(report['enhanced_recommendations'])
            md_content.append("## Recommended Actions")
            for i, action in enumerate(action_plan[:5], 1):
                md_content.append(f"### {i}. {action['title']}")
                md_content.append(f"**Category:** {action['category']}")
                md_content.append(f"**Effort:** {action['effort']} | **Impact:** {action['impact']}")
                md_content.append(f"{action['description']}")
                if action.get('ai_enhanced'):
                    md_content.append(f"*AI Confidence: {action['confidence']:.1%}*")
                md_content.append("")
        
        return "\n".join(md_content)
