"""
CodePulse - Unified GitHub Repository Analyzer
A single application supporting both standard and AI-enhanced analysis modes
"""

from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import os
import json
import asyncio
import logging
from datetime import datetime
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
                        repo_info, coverage_results, issues, enable_ai=True
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
                        repo_info, coverage_results, issues, enable_ai=True
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
        # This would typically retrieve cached analysis data
        # For demonstration, return a sample export
        
        if format.lower() == 'json':
            sample_data = {
                'repository': repo_path,
                'analysis_date': datetime.now().isoformat(),
                'summary': 'Sample export data',
                'export_format': format,
                'ai_available': AI_AVAILABLE
            }
            
            response = jsonify(sample_data)
            response.headers['Content-Disposition'] = f'attachment; filename={repo_path.replace("/", "_")}_analysis.json'
            return response
        
        elif format.lower() == 'markdown':
            markdown_content = f"""# Analysis Report: {repo_path}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Mode:** {'AI-Enhanced' if AI_AVAILABLE and Config.GITHUB_TOKEN else 'Standard'}

## Summary
This is a sample markdown export of the analysis report.

## Key Metrics
- Health Score: 85/100
- Test Coverage: 78%
- Issues Found: 5

## Recommendations
1. Improve test coverage
2. Update dependencies
3. Add documentation
"""
            
            from flask import Response
            response = Response(
                markdown_content,
                mimetype='text/markdown',
                headers={'Content-Disposition': f'attachment; filename={repo_path.replace("/", "_")}_analysis.md'}
            )
            return response
        
        else:
            return jsonify({'error': f'Unsupported export format: {format}'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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