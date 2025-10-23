"""
CodePulse - Unified GitHub Repository Analyzer
A single application supporting both standard and AI-enhanced analysis modes
"""

import os
import asyncio
import logging
from datetime import datetime

from flask import Flask, render_template, request, jsonify, flash, redirect, url_for

from analyzer.github_client import GitHubClient
from analyzer.test_analyzer import TestAnalyzer
from analyzer.issue_detector import IssueDetector
from analyzer.report_generator import ReportGenerator
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('codepulse.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

# Try to import AI components (optional)
try:
    from analyzer.ai_analyzer import AIAnalyzer
    from analyzer.enhanced_report_generator import EnhancedReportGenerator
    AI_AVAILABLE = True
    logger.info("🧠 AI components loaded successfully")
except ImportError:
    AI_AVAILABLE = False
    logger.warning("⚠️  AI components not available. Running in standard mode only.")
    print("⚠️  AI components not available. Running in standard mode only.")

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = os.environ.get('SECRET_KEY', 'codepulse-dev-secret-key-change-in-production')

# In-memory cache for analysis data (simple solution for demo)
analysis_cache = {}

# Validate configuration
try:
    Config.validate()
except ValueError as e:
    print(f"Configuration warning: {e}")
    print("Note: GitHub token is optional for public repositories")

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html', ai_available=AI_AVAILABLE)

@app.route('/analyze', methods=['POST'])
def analyze_repository():
    """Analyze a GitHub repository with optional AI enhancement"""
    try:
        repo_url = request.form.get('repo_url', '').strip()
        is_public = request.form.get('is_public') == 'on'
        enable_ai = request.form.get('enable_ai') == 'on' if AI_AVAILABLE else False
        
        if not repo_url:
            flash('Please provide a repository URL', 'error')
            return redirect(url_for('index'))
        
        # Parse repository from URL
        repo_path = parse_repo_url(repo_url)
        if not repo_path:
            flash('Invalid GitHub repository URL', 'error')
            return redirect(url_for('index'))
        
        # Check if token is required for private repos or AI features
        if (not is_public and not Config.GITHUB_TOKEN) or (enable_ai and not Config.GITHUB_TOKEN):
            if not is_public:
                flash('GitHub token is required for private repositories. Please set GITHUB_TOKEN in your .env file.', 'error')
            else:
                flash('GitHub token is required for AI features. Please set GITHUB_TOKEN in your .env file or disable AI enhancement.', 'error')
            return redirect(url_for('index'))
        
        # Initialize analyzers
        github_token = Config.GITHUB_TOKEN if not is_public or Config.GITHUB_TOKEN else None
        github_client = GitHubClient(github_token, is_public)
        test_analyzer = TestAnalyzer()
        issue_detector = IssueDetector()
        
        # Choose report generator based on AI setting and availability
        if enable_ai and AI_AVAILABLE:
            report_generator = EnhancedReportGenerator(github_token)
            analysis_mode = "🧠 AI-Enhanced"
            logger.info(f"🧠 Initializing AI-Enhanced analysis for {repo_path}")
        else:
            report_generator = ReportGenerator()
            analysis_mode = "📊 Standard"
            logger.info(f"📊 Initializing Standard analysis for {repo_path}")
        
        logger.info(f"{analysis_mode} Analysis: {repo_path} ({'public' if is_public else 'private'})")
        print(f"{analysis_mode} Analysis: {repo_path} ({'public' if is_public else 'private'})")
        
        # Fetch repository information with detailed error handling
        try:
            logger.info(f"🔍 Fetching repository information for: {repo_path}")
            print(f"Fetching repository information for: {repo_path}")
            repo_info = github_client.get_repository_info(repo_path)
            logger.info(f"✅ Repository info fetched successfully: {repo_info.get('name', 'Unknown')} - Language: {repo_info.get('language', 'N/A')}, Stars: {repo_info.get('stargazers_count', 0)}")
            print(f"Repository info fetched successfully: {repo_info.get('name', 'Unknown')}")
        except Exception as e:
            error_msg = f"Failed to fetch repository information: {str(e)}"
            logger.error(f"❌ {error_msg}")
            print(f"Error: {error_msg}")
            flash(error_msg, 'error')
            return redirect(url_for('index'))
        
        # Clone and analyze repository
        logger.info(f"📥 Starting repository clone for {repo_path}")
        repo_data = github_client.clone_repository(repo_path)
        logger.info(f"✅ Repository cloned successfully to {repo_data['local_path']}")
        
        # Analyze test coverage
        logger.info(f"🧪 Starting test coverage analysis")
        coverage_results = test_analyzer.analyze_coverage(repo_data['local_path'])
        logger.info(f"✅ Test coverage analysis completed - Coverage: {coverage_results.get('coverage_percentage', 0)}%")
        
        # Detect issues
        logger.info(f"🔍 Starting issue detection")
        issues = issue_detector.detect_issues(repo_data['local_path'], repo_info)
        logger.info(f"✅ Issue detection completed - Critical: {len(issues.get('critical_issues', []))}, Warnings: {len(issues.get('warnings', []))}")
        
        # Generate report (enhanced or standard)
        if enable_ai and AI_AVAILABLE:
            logger.info(f"🧠 Starting AI-Enhanced report generation")
            # Run async AI analysis
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                start_time = datetime.now()
                analysis_report = loop.run_until_complete(
                    report_generator.generate_enhanced_report(
                        repo_info, coverage_results, issues, repo_path=repo_data['local_path'], enable_ai=True
                    )
                )
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                logger.info(f"✅ AI-Enhanced report generation completed in {duration:.2f} seconds")
                
                # Log AI insights availability
                if 'ai_insights' in analysis_report:
                    ai_insights = analysis_report['ai_insights']
                    logger.info(f"🧠 AI Insights generated:")
                    if 'architecture' in ai_insights:
                        arch_score = ai_insights['architecture'].get('architecture_score', 'N/A')
                        logger.info(f"  - Architecture Score: {arch_score}")
                    if 'code_quality' in ai_insights:
                        quality_score = ai_insights['code_quality'].get('score', 'N/A')
                        logger.info(f"  - Code Quality Score: {quality_score}")
                    if 'security' in ai_insights:
                        security_score = ai_insights['security'].get('score', 'N/A')
                        logger.info(f"  - Security Score: {security_score}")
                else:
                    logger.warning("⚠️ No AI insights found in analysis report")
                    
            except Exception as e:
                logger.error(f"❌ AI-Enhanced report generation failed: {str(e)}")
                raise
            finally:
                loop.close()
        else:
            logger.info(f"📊 Starting Standard report generation")
            start_time = datetime.now()
            analysis_report = report_generator.generate_report(
                repo_info, coverage_results, issues
            )
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"✅ Standard report generation completed in {duration:.2f} seconds")
        
        # Cleanup temporary directory
        logger.info(f"🧹 Cleaning up temporary directory: {repo_data['local_path']}")
        github_client.cleanup_temp_directory(repo_data['local_path'])
        
        # Choose template based on AI enhancement
        has_ai_insights = enable_ai and AI_AVAILABLE and 'ai_insights' in analysis_report
        template = 'results_enhanced.html' if has_ai_insights else 'results.html'
        logger.info(f"📄 Rendering template: {template} (AI insights: {has_ai_insights})")
        
        total_duration = (datetime.now() - datetime.strptime(timestamp := datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')).total_seconds()
        logger.info(f"🎉 Analysis completed successfully for {repo_path}")
        
        # Store analysis data in memory cache for export functionality
        cache_key = f'analysis_{repo_path.replace("/", "_")}'
        analysis_cache[cache_key] = analysis_report
        logger.info(f"💾 Analysis data stored in cache with key: {cache_key}")
        
        return render_template(template, 
                             repo_path=repo_path,
                             analysis=analysis_report,
                             ai_enabled=enable_ai and AI_AVAILABLE,
                             ai_available=AI_AVAILABLE,
                             timestamp=timestamp)
        
    except Exception as e:
        logger.error(f"❌ Analysis error for {repo_path}: {str(e)}", exc_info=True)
        print(f"Analysis error: {str(e)}")
        flash(f'Analysis failed: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint for repository analysis with optional AI support"""
    try:
        data = request.get_json()
        repo_url = data.get('repo_url', '').strip()
        is_public = data.get('is_public', True)
        enable_ai = data.get('enable_ai', False) if AI_AVAILABLE else False
        
        if not repo_url:
            return jsonify({'error': 'Repository URL is required'}), 400
        
        repo_path = parse_repo_url(repo_url)
        if not repo_path:
            return jsonify({'error': 'Invalid GitHub repository URL'}), 400
        
        # Check if token is required
        if (not is_public and not Config.GITHUB_TOKEN) or (enable_ai and not Config.GITHUB_TOKEN):
            if not is_public:
                return jsonify({'error': 'GitHub token is required for private repositories'}), 400
            else:
                return jsonify({'error': 'GitHub token is required for AI features'}), 400
        
        # Initialize analyzers
        github_token = Config.GITHUB_TOKEN if not is_public or Config.GITHUB_TOKEN else None
        github_client = GitHubClient(github_token, is_public)
        test_analyzer = TestAnalyzer()
        issue_detector = IssueDetector()
        
        # Choose report generator
        if enable_ai and AI_AVAILABLE:
            report_generator = EnhancedReportGenerator(github_token)
        else:
            report_generator = ReportGenerator()
        
        # Perform analysis
        repo_info = github_client.get_repository_info(repo_path)
        repo_data = github_client.clone_repository(repo_path)
        coverage_results = test_analyzer.analyze_coverage(repo_data['local_path'])
        issues = issue_detector.detect_issues(repo_data['local_path'], repo_info)
        
        # Generate report
        if enable_ai and AI_AVAILABLE:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                analysis_report = loop.run_until_complete(
                    report_generator.generate_enhanced_report(
                        repo_info, coverage_results, issues, repo_path=repo_data['local_path'], enable_ai=True
                    )
                )
            finally:
                loop.close()
        else:
            analysis_report = report_generator.generate_report(
                repo_info, coverage_results, issues
            )
        
        # Cleanup temporary directory
        github_client.cleanup_temp_directory(repo_data['local_path'])
        
        return jsonify({
            'success': True,
            'repo_path': repo_path,
            'analysis': analysis_report,
            'ai_enabled': enable_ai and AI_AVAILABLE,
            'ai_available': AI_AVAILABLE,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai-insights/<path:repo_path>')
def get_ai_insights(repo_path):
    """Get AI insights for a specific repository"""
    if not AI_AVAILABLE:
        return jsonify({'error': 'AI features not available'}), 503
        
    try:
        if not Config.GITHUB_TOKEN:
            return jsonify({'error': 'GitHub token required for AI insights'}), 400
        
        ai_analyzer = AIAnalyzer(Config.GITHUB_TOKEN)
        
        # This would typically get cached analysis results
        # For now, return sample insights
        insights = {
            'architecture_score': 8.5,
            'code_quality_score': 7.8,
            'security_score': 9.2,
            'recommendations': [
                'Consider implementing unit tests for core modules',
                'Update dependencies to latest versions',
                'Add code documentation for public APIs'
            ],
            'confidence': 0.85,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(insights)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/export/<format>/<path:repo_path>')
def export_report(format, repo_path):
    """Export analysis report in various formats"""
    try:
        # Try to get cached analysis data from memory cache
        cache_key = f'analysis_{repo_path.replace("/", "_")}'
        analysis_data = analysis_cache.get(cache_key)
        
        logger.info(f"🔍 Export request for {repo_path} in {format} format")
        logger.info(f"📋 Looking for cache key: {cache_key}")
        logger.info(f"💾 Cache keys available: {list(analysis_cache.keys())}")
        
        if not analysis_data:
            return jsonify({'error': 'No analysis data found for this repository. Please run analysis first.'}), 404
        
        repo_name = repo_path.split('/')[-1]
        
        if format.lower() == 'json':
            response = jsonify(analysis_data)
            response.headers['Content-Disposition'] = f'attachment; filename={repo_path.replace("/", "_")}_analysis.json'
            return response
        
        elif format.lower() == 'markdown':
            markdown_content = generate_markdown_report(analysis_data, repo_path)
            
            from flask import Response
            response = Response(
                markdown_content,
                mimetype='text/markdown',
                headers={'Content-Disposition': f'attachment; filename={repo_path.replace("/", "_")}_analysis.md'}
            )
            return response
        
        elif format.lower() == 'html':
            html_content = generate_html_report(analysis_data, repo_path)
            
            from flask import Response
            response = Response(
                html_content,
                mimetype='text/html',
                headers={'Content-Disposition': f'attachment; filename={repo_path.replace("/", "_")}_analysis.html'}
            )
            return response
        
        elif format.lower() == 'ai-summary':
            ai_summary = generate_ai_summary_report(analysis_data, repo_path)
            
            from flask import Response
            response = Response(
                ai_summary,
                mimetype='text/markdown',
                headers={'Content-Disposition': f'attachment; filename={repo_path.replace("/", "_")}_ai_summary.md'}
            )
            return response
        
        else:
            return jsonify({'error': f'Unsupported export format: {format}'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_markdown_report(analysis_data, repo_path):
    """Generate a comprehensive markdown report"""
    repo_name = repo_path.split('/')[-1]
    metadata = analysis_data.get('metadata', {})
    scores = analysis_data.get('scores', {})
    summary = analysis_data.get('summary', {})
    recommendations = analysis_data.get('recommendations', [])
    ai_insights = analysis_data.get('ai_insights', {})
    
    report = f"""# Analysis Report: {repo_path}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Mode:** {'AI-Enhanced' if analysis_data.get('ai_enabled', False) else 'Standard'}
**Analysis Date:** {metadata.get('analysis_date', 'Unknown')}

## Repository Information
- **Stars:** {metadata.get('stars', 'N/A')}
- **Forks:** {metadata.get('forks', 'N/A')}
- **Primary Language:** {metadata.get('primary_language', 'Unknown')}
- **Description:** {metadata.get('description', 'No description available')}

## Summary Scores
- **Overall Health:** {scores.get('health_score', 'N/A')}/100
- **Test Coverage:** {scores.get('coverage_score', 'N/A')}%
- **Code Quality:** {scores.get('code_quality_score', 'N/A')}/100
- **Security Score:** {scores.get('security_score', 'N/A')}/100
- **Documentation:** {scores.get('documentation_score', 'N/A')}/100

## Issues Summary
- **Critical Issues:** {summary.get('critical_issues', 0)}
- **High Priority:** {summary.get('high_issues', 0)}
- **Medium Priority:** {summary.get('medium_issues', 0)}
- **Low Priority:** {summary.get('low_issues', 0)}
- **Total Issues:** {summary.get('total_issues', 0)}

"""
    
    # Add AI Insights if available
    if ai_insights and analysis_data.get('ai_enabled', False):
        report += """## AI-Powered Insights

### Architecture Analysis
"""
        arch = ai_insights.get('architecture', {})
        if arch:
            report += f"- **Score:** {arch.get('architecture_score', 'N/A')}/10\n"
            report += f"- **Confidence:** {arch.get('confidence', 'N/A')}\n"
            
            patterns = arch.get('patterns_detected', [])
            if patterns:
                report += f"- **Patterns Detected:** {', '.join(patterns)}\n"
            
            findings = arch.get('key_findings', [])
            if findings:
                report += "\n**Key Findings:**\n"
                for finding in findings:
                    report += f"- {finding}\n"

        report += "\n### Code Quality Analysis\n"
        quality = ai_insights.get('code_quality', {})
        if quality:
            report += f"- **Score:** {quality.get('score', 'N/A')}/10\n"
            report += f"- **Maintainability:** {quality.get('maintainability', 'N/A')}/10\n"
            report += f"- **Readability:** {quality.get('readability', 'N/A')}/10\n"
            
            strengths = quality.get('strengths', [])
            if strengths:
                report += "\n**Strengths:**\n"
                for strength in strengths:
                    report += f"- {strength}\n"
            
            weaknesses = quality.get('weaknesses', [])
            if weaknesses:
                report += "\n**Areas for Improvement:**\n"
                for weakness in weaknesses:
                    report += f"- {weakness}\n"

    # Add Recommendations
    if recommendations:
        report += "\n## Recommendations\n\n"
        for rec in recommendations:
            report += f"### {rec.get('title', 'Untitled')}\n"
            report += f"**Priority:** {rec.get('priority', 'Unknown')}\n"
            report += f"**Category:** {rec.get('category', 'General')}\n"
            report += f"**Impact:** {rec.get('impact', 'Unknown')}\n"
            report += f"**Effort:** {rec.get('estimated_effort', 'Unknown')}\n\n"
            report += f"{rec.get('description', 'No description provided')}\n\n"
            
            actions = rec.get('actions', [])
            if actions:
                report += "**Action Items:**\n"
                for action in actions:
                    report += f"- {action}\n"
            report += "\n"

    report += f"""
## Export Information
- **Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Export Format:** Markdown
- **Data Source:** {'AI-Enhanced Analysis' if analysis_data.get('ai_enabled', False) else 'Standard Analysis'}

---
*Generated by CodePulse Repository Analyzer*
"""
    
    return report

def generate_ai_summary_report(analysis_data, repo_path):
    """Generate an AI-focused summary report"""
    ai_insights = analysis_data.get('ai_insights', {})
    ai_summary = analysis_data.get('ai_summary', {})
    
    if not ai_insights and not ai_summary:
        return f"""# AI Summary Report: {repo_path}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## No AI Analysis Available

This repository was analyzed using standard analysis only. 
To get AI-powered insights, ensure:
1. GitHub token is configured
2. AI analysis is enabled during analysis

---
*Generated by CodePulse Repository Analyzer*
"""
    
    report = f"""# AI Summary Report: {repo_path}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**AI Confidence Level:** {ai_summary.get('confidence_level', 'Unknown')}
**Overall AI Score:** {ai_summary.get('overall_ai_score', 'N/A')}/10

## Key AI Findings

"""
    
    key_findings = ai_summary.get('key_findings', [])
    if key_findings:
        for finding in key_findings:
            report += f"- {finding}\n"
    else:
        report += "No specific findings available.\n"
    
    # Architecture Insights
    arch = ai_insights.get('architecture', {})
    if arch:
        report += f"""
## Architecture Analysis (AI Score: {arch.get('architecture_score', 'N/A')}/10)

**Confidence:** {arch.get('confidence', 'N/A')}

### Key Findings:
"""
        for finding in arch.get('key_findings', []):
            report += f"- {finding}\n"
        
        report += "\n### Recommendations:\n"
        for rec in arch.get('recommendations', []):
            report += f"- {rec}\n"
    
    # Code Quality Insights
    quality = ai_insights.get('code_quality', {})
    if quality:
        report += f"""
## Code Quality Analysis (AI Score: {quality.get('score', 'N/A')}/10)

**Maintainability:** {quality.get('maintainability', 'N/A')}/10
**Readability:** {quality.get('readability', 'N/A')}/10

### Strengths:
"""
        for strength in quality.get('strengths', []):
            report += f"- {strength}\n"
        
        report += "\n### Areas for Improvement:\n"
        for weakness in quality.get('weaknesses', []):
            report += f"- {weakness}\n"
    
    report += f"""

## AI Analysis Summary

Total AI insights generated: {ai_summary.get('insights_count', 0)}

---
*Generated by CodePulse Repository Analyzer with AI-Enhanced Analysis*
"""
    
    return report

def generate_html_report(analysis_data, repo_path):
    """Generate a comprehensive HTML report"""
    from flask import render_template_string
    
    repo_name = repo_path.split('/')[-1]
    metadata = analysis_data.get('metadata', {})
    scores = analysis_data.get('scores', {})
    summary = analysis_data.get('summary', {})
    recommendations = analysis_data.get('recommendations', [])
    ai_insights = analysis_data.get('ai_insights', {})
    test_analysis = analysis_data.get('test_analysis', {})
    
    # Create a comprehensive HTML template
    html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CodePulse Analysis Report - {{ repo_path }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; }
        .metric-card { padding: 1rem; border-radius: 0.5rem; background: white; margin-bottom: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .metric-value { font-size: 2rem; font-weight: bold; }
        .metric-label { color: #6c757d; font-size: 0.9rem; }
        .score-good { color: #28a745; }
        .score-warning { color: #ffc107; }
        .score-danger { color: #dc3545; }
        .score-info { color: #17a2b8; }
        .header-section { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem 0; }
        .ai-section { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .progress-custom { height: 10px; border-radius: 5px; }
        @media print { .no-print { display: none; } }
    </style>
</head>
<body>
    <!-- Header Section -->
    <div class="header-section">
        <div class="container">
            <div class="row align-items-center">
                <div class="col-lg-8">
                    <h1 class="mb-2"><i class="fas fa-chart-line me-2"></i>CodePulse Analysis Report</h1>
                    <p class="mb-1 opacity-75">{{ repo_path }}</p>
                    <p class="mb-0 small">
                        <i class="fas fa-calendar me-1"></i>Generated: {{ analysis_date }}
                        {% if ai_enabled %}
                        <span class="ms-3"><i class="fas fa-robot me-1"></i>AI-Enhanced Analysis</span>
                        {% endif %}
                    </p>
                </div>
                <div class="col-lg-4 text-lg-end">
                    <div class="d-inline-block bg-white bg-opacity-20 rounded p-3">
                        <div class="h3 mb-1">{{ health_score }}/100</div>
                        <div class="small">Health Score</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="container my-4">
        <!-- Summary Cards -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="metric-card text-center">
                    <div class="metric-value {{ coverage_color }}">{{ coverage_score }}%</div>
                    <div class="metric-label">Test Coverage</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card text-center">
                    <div class="metric-value score-info">{{ code_quality_score }}/100</div>
                    <div class="metric-label">Code Quality</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card text-center">
                    <div class="metric-value score-warning">{{ security_score }}/100</div>
                    <div class="metric-label">Security Score</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card text-center">
                    <div class="metric-value score-good">{{ documentation_score }}/100</div>
                    <div class="metric-label">Documentation</div>
                </div>
            </div>
        </div>

        <!-- Repository Information -->
        <div class="row mb-4">
            <div class="col-lg-6">
                <div class="card h-100">
                    <div class="card-header">
                        <h5 class="card-title mb-0"><i class="fab fa-github me-2"></i>Repository Information</h5>
                    </div>
                    <div class="card-body">
                        <table class="table table-borderless">
                            <tr><td><strong>Stars:</strong></td><td>{{ stars }}</td></tr>
                            <tr><td><strong>Forks:</strong></td><td>{{ forks }}</td></tr>
                            <tr><td><strong>Language:</strong></td><td>{{ primary_language }}</td></tr>
                            <tr><td><strong>Description:</strong></td><td>{{ description }}</td></tr>
                        </table>
                    </div>
                </div>
            </div>
            <div class="col-lg-6">
                <div class="card h-100">
                    <div class="card-header">
                        <h5 class="card-title mb-0"><i class="fas fa-bug me-2"></i>Issues Summary</h5>
                    </div>
                    <div class="card-body">
                        <div class="row text-center">
                            <div class="col-6"><div class="text-danger h4">{{ critical_issues }}</div><small>Critical</small></div>
                            <div class="col-6"><div class="text-warning h4">{{ high_issues }}</div><small>High</small></div>
                            <div class="col-6"><div class="text-info h4">{{ medium_issues }}</div><small>Medium</small></div>
                            <div class="col-6"><div class="text-muted h4">{{ low_issues }}</div><small>Low</small></div>
                        </div>
                        <div class="text-center mt-3">
                            <strong>Total Issues: {{ total_issues }}</strong>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Test Analysis -->
        {% if test_analysis %}
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5 class="card-title mb-0"><i class="fas fa-vial me-2"></i>Test Analysis</h5>
                    </div>
                    <div class="card-body">
                        {% if test_distribution %}
                        <div class="row">
                            <div class="col-lg-6">
                                <h6>Test Distribution</h6>
                                {% for test_type, count in test_types.items() %}
                                {% if count > 0 %}
                                <div class="d-flex justify-content-between mb-2">
                                    <span class="text-capitalize">{{ test_type }}:</span>
                                    <span><strong>{{ count }}</strong> ({{ "%.1f"|format(test_distribution.percentages[test_type]|default(0)) }}%)</span>
                                </div>
                                <div class="progress progress-custom mb-3">
                                    <div class="progress-bar {% if test_type == 'unit' %}bg-primary{% elif test_type == 'integration' %}bg-success{% elif test_type == 'e2e' %}bg-warning{% else %}bg-info{% endif %}" 
                                         style="width: {{ test_distribution.percentages[test_type]|default(0) }}%"></div>
                                </div>
                                {% endif %}
                                {% endfor %}
                            </div>
                            <div class="col-lg-6">
                                <h6>Test Balance Score</h6>
                                <div class="progress progress-custom mb-2" style="height: 20px;">
                                    <div class="progress-bar {% if test_distribution.balance_score >= 80 %}bg-success{% elif test_distribution.balance_score >= 60 %}bg-warning{% else %}bg-danger{% endif %}" 
                                         style="width: {{ test_distribution.balance_score }}%">
                                        {{ test_distribution.balance_score }}/100
                                    </div>
                                </div>
                                <small class="text-muted">Optimal: 70% Unit, 20% Integration, 10% E2E</small>
                            </div>
                        </div>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- AI Insights -->
        {% if ai_insights and ai_enabled %}
        <div class="row mb-4">
            <div class="col-12">
                <div class="card ai-section">
                    <div class="card-header border-0">
                        <h5 class="card-title mb-0 text-white"><i class="fas fa-robot me-2"></i>AI-Powered Insights</h5>
                    </div>
                    <div class="card-body text-white">
                        {% if ai_insights.architecture %}
                        <h6><i class="fas fa-sitemap me-2"></i>Architecture Analysis (Score: {{ ai_insights.architecture.architecture_score|default('N/A') }}/10)</h6>
                        <p class="small mb-3">Confidence: {{ ai_insights.architecture.confidence|default('N/A') }}</p>
                        {% if ai_insights.architecture.key_findings %}
                        <ul class="mb-3">
                            {% for finding in ai_insights.architecture.key_findings %}
                            <li>{{ finding }}</li>
                            {% endfor %}
                        </ul>
                        {% endif %}
                        {% endif %}

                        {% if ai_insights.code_quality %}
                        <h6><i class="fas fa-code me-2"></i>Code Quality Analysis</h6>
                        <div class="row text-center mb-3">
                            <div class="col-4"><div class="h5">{{ ai_insights.code_quality.score|default('N/A') }}/10</div><small>Overall</small></div>
                            <div class="col-4"><div class="h5">{{ ai_insights.code_quality.maintainability|default('N/A') }}/10</div><small>Maintainability</small></div>
                            <div class="col-4"><div class="h5">{{ ai_insights.code_quality.readability|default('N/A') }}/10</div><small>Readability</small></div>
                        </div>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- Veracode Security Analysis -->
        {% if veracode_analysis %}
        <div class="row mb-4">
            <div class="col-12">
                <div class="card border-danger">
                    <div class="card-header bg-danger text-white">
                        <h5 class="card-title mb-0"><i class="fas fa-shield-alt me-2"></i>Veracode Professional Security Analysis</h5>
                    </div>
                    <div class="card-body">
                        <!-- Security Score and Key Metrics -->
                        <div class="row mb-4">
                            <div class="col-md-3">
                                <div class="text-center">
                                    <div class="metric-value {% if veracode_analysis.security_score >= 80 %}score-good{% elif veracode_analysis.security_score >= 60 %}score-warning{% else %}score-danger{% endif %}">
                                        {{ veracode_analysis.security_score|default('N/A') }}/100
                                    </div>
                                    <div class="metric-label">Veracode Score</div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="text-center">
                                    <div class="metric-value score-danger">{{ veracode_analysis.summary.critical_flaws|default(0) }}</div>
                                    <div class="metric-label">Critical Flaws</div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="text-center">
                                    <div class="metric-value score-warning">{{ veracode_analysis.summary.high_severity|default(0) }}</div>
                                    <div class="metric-label">High Severity</div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="text-center">
                                    <div class="metric-value score-info">{{ veracode_analysis.summary.total_findings|default(0) }}</div>
                                    <div class="metric-label">Total Findings</div>
                                </div>
                            </div>
                        </div>

                        {% if veracode_analysis.vulnerability_categories %}
                        <!-- Vulnerability Categories -->
                        <h6><i class="fas fa-exclamation-triangle me-2"></i>Vulnerability Categories</h6>
                        <div class="row mb-3">
                            {% for category in veracode_analysis.vulnerability_categories %}
                            <div class="col-md-6 mb-2">
                                <div class="d-flex justify-content-between align-items-center p-2 border-start border-4 {% if category.severity == 'Critical' %}border-danger{% elif category.severity == 'High' %}border-warning{% elif category.severity == 'Medium' %}border-info{% else %}border-secondary{% endif %} bg-light">
                                    <div>
                                        <strong>{{ category.name }}</strong>
                                        <small class="d-block text-muted">{{ category.description|default('') }}</small>
                                    </div>
                                    <span class="badge bg-{% if category.severity == 'Critical' %}danger{% elif category.severity == 'High' %}warning{% elif category.severity == 'Medium' %}info{% else %}secondary{% endif %}">
                                        {{ category.count|default(0) }}
                                    </span>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                        {% endif %}

                        {% if veracode_analysis.compliance %}
                        <!-- Compliance Status -->
                        <h6><i class="fas fa-certificate me-2"></i>Compliance Status</h6>
                        <div class="row mb-3">
                            {% for standard, status in veracode_analysis.compliance.items() %}
                            <div class="col-md-4 mb-2">
                                <div class="d-flex justify-content-between align-items-center p-2 bg-light rounded">
                                    <span>{{ standard|upper }}</span>
                                    <span class="badge bg-{% if status %}success{% else %}danger{% endif %}">
                                        {% if status %}Compliant{% else %}Non-Compliant{% endif %}
                                    </span>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                        {% endif %}

                        <!-- Scan Summary -->
                        <h6><i class="fas fa-info-circle me-2"></i>Scan Summary</h6>
                        <div class="row">
                            <div class="col-md-6">
                                <ul class="list-unstyled">
                                    <li><strong>Scan Date:</strong> {{ veracode_analysis.scan_date|default('N/A') }}</li>
                                    <li><strong>Scan Duration:</strong> {{ veracode_analysis.scan_duration|default('N/A') }}</li>
                                </ul>
                            </div>
                            <div class="col-md-6">
                                <ul class="list-unstyled">
                                    <li><strong>Files Scanned:</strong> {{ veracode_analysis.files_scanned|default('N/A') }}</li>
                                    <li><strong>Lines of Code:</strong> {{ veracode_analysis.lines_of_code|default('N/A') }}</li>
                                </ul>
                            </div>
                        </div>

                        {% if veracode_analysis.recommendations %}
                        <!-- Security Recommendations -->
                        <h6 class="mt-3"><i class="fas fa-shield-alt me-2"></i>Security Recommendations</h6>
                        <ul class="mb-0">
                            {% for recommendation in veracode_analysis.recommendations %}
                            <li>{{ recommendation }}</li>
                            {% endfor %}
                        </ul>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
        {% elif veracode_configured %}
        <!-- Veracode Not Available Message -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="card border-warning">
                    <div class="card-body text-center">
                        <i class="fas fa-shield-alt fa-3x text-warning mb-3"></i>
                        <h5>Veracode Professional Security Analysis</h5>
                        <p class="text-muted">Veracode security scanning is configured but analysis is not available for this repository.</p>
                        <p class="small">This may occur if the repository cannot be processed by Veracode or if there was an issue with the scan.</p>
                    </div>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- Recommendations -->
        {% if recommendations %}
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5 class="card-title mb-0"><i class="fas fa-lightbulb me-2"></i>Recommendations</h5>
                    </div>
                    <div class="card-body">
                        {% for rec in recommendations %}
                        <div class="border-start border-4 {% if rec.priority == 'High' %}border-danger{% elif rec.priority == 'Medium' %}border-warning{% else %}border-info{% endif %} ps-3 mb-3">
                            <h6 class="mb-1">{{ rec.title }}</h6>
                            <p class="text-muted small mb-2">
                                <span class="badge bg-{% if rec.priority == 'High' %}danger{% elif rec.priority == 'Medium' %}warning{% else %}info{% endif %} me-2">{{ rec.priority }}</span>
                                <span class="me-2">{{ rec.category }}</span>
                                <span>Impact: {{ rec.impact }}</span>
                            </p>
                            <p class="mb-2">{{ rec.description }}</p>
                            {% if rec.actions %}
                            <ul class="small">
                                {% for action in rec.actions %}
                                <li>{{ action }}</li>
                                {% endfor %}
                            </ul>
                            {% endif %}
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- Footer -->
        <div class="row">
            <div class="col-12">
                <div class="text-center text-muted small">
                    <hr>
                    <p>Generated by <strong>CodePulse Repository Analyzer</strong> on {{ analysis_date }}</p>
                    <p>This is an {{ 'AI-Enhanced' if ai_enabled else 'Standard' }} analysis report</p>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
    """
    
    # Prepare template variables
    template_vars = {
        'repo_path': repo_path,
        'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'ai_enabled': analysis_data.get('ai_enabled', False),
        'health_score': scores.get('health_score', 'N/A'),
        'coverage_score': scores.get('coverage_score', 'N/A'),
        'coverage_color': test_analysis.get('coverage_color', 'score-info'),
        'code_quality_score': scores.get('code_quality_score', 'N/A'),
        'security_score': scores.get('security_score', 'N/A'),
        'documentation_score': scores.get('documentation_score', 'N/A'),
        'stars': metadata.get('stars', 'N/A'),
        'forks': metadata.get('forks', 'N/A'),
        'primary_language': metadata.get('primary_language', 'Unknown'),
        'description': metadata.get('description', 'No description available'),
        'critical_issues': summary.get('critical_issues', 0),
        'high_issues': summary.get('high_issues', 0),
        'medium_issues': summary.get('medium_issues', 0),
        'low_issues': summary.get('low_issues', 0),
        'total_issues': summary.get('total_issues', 0),
        'test_analysis': test_analysis,
        'test_distribution': test_analysis.get('test_structure', {}).get('test_distribution'),
        'test_types': test_analysis.get('test_structure', {}).get('test_types', {}),
        'ai_insights': ai_insights,
        'recommendations': recommendations,
        'veracode_analysis': analysis_data.get('veracode_analysis'),
        'veracode_configured': analysis_data.get('veracode_configured', False)
    }
    
    return render_template_string(html_template, **template_vars)

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '2.0.0',
        'mode': 'unified',
        'features': {
            'ai_available': AI_AVAILABLE,
            'ai_enabled': bool(Config.GITHUB_TOKEN and AI_AVAILABLE),
            'public_analysis': True,
            'private_analysis': bool(Config.GITHUB_TOKEN)
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/features')
def get_features():
    """Get available features and capabilities"""
    return jsonify({
        'standard_features': [
            'Repository analysis',
            'Test coverage detection',
            'Issue identification',
            'Code quality assessment',
            'Security scanning'
        ],
        'ai_features': [
            'Intelligent code review',
            'Context-aware recommendations', 
            'Architecture analysis',
            'Performance optimization',
            'Strategic roadmap generation'
        ] if AI_AVAILABLE else [],
        'ai_available': AI_AVAILABLE,
        'ai_enabled': bool(Config.GITHUB_TOKEN and AI_AVAILABLE),
        'requirements': {
            'public_repos': 'No token required',
            'private_repos': 'GitHub token required',
            'ai_features': 'GitHub token required'
        }
    })

def parse_repo_url(url):
    """Parse GitHub repository URL to extract owner/repo"""
    import re
    
    # Handle various GitHub URL formats
    patterns = [
        r'github\.com[/:]([^/]+)/([^/]+?)(?:\.git)?/?$',
        r'github\.com/([^/]+)/([^/]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            owner, repo = match.groups()
            return f"{owner}/{repo}"
    
    return None

if __name__ == '__main__':
    print("🚀 Starting CodePulse - Unified GitHub Repository Analyzer")
    print(f"🔗 Access the dashboard at: http://localhost:5050")
    print(f"📊 Standard Analysis: Always available")
    
    if AI_AVAILABLE:
        if Config.GITHUB_TOKEN:
            print(f"🧠 AI-Enhanced Analysis: Enabled")
        else:
            print(f"🧠 AI-Enhanced Analysis: Available (set GITHUB_TOKEN to enable)")
    else:
        print(f"🧠 AI-Enhanced Analysis: Not available (missing dependencies)")
    
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5050)