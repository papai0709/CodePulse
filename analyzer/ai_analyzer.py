"""
AI-powered code analysis module for CodePulse
"""
import json
import os
import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path
import aiohttp
from datetime import datetime

class AIAnalyzer:
    """AI-powered code analysis using GitHub Models"""
    
    def __init__(self, github_token: str = None, model: str = "openai/gpt-4.1-mini"):
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        self.model = model
        self.base_url = "https://models.inference.ai.azure.com"
        self.headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Content-Type": "application/json"
        }
    
    async def analyze_code_quality(self, file_content: str, file_path: str, language: str) -> Dict[str, Any]:
        """Analyze code quality using AI"""
        if not self.github_token:
            return self._fallback_analysis("code_quality")
            
        prompt = f"""
        Analyze this {language} code for quality issues:
        
        File: {file_path}
        Code:
        ```{language}
        {file_content[:2000]}  # Limit content size
        ```
        
        Provide analysis in JSON format:
        {{
            "quality_score": 85,
            "issues": [
                {{
                    "type": "performance",
                    "severity": "medium", 
                    "line": 10,
                    "description": "Issue description",
                    "suggestion": "Improvement suggestion"
                }}
            ],
            "suggestions": ["suggestion1"],
            "security_concerns": ["concern1"],
            "maintainability_score": 80
        }}
        """
        
        return await self._call_ai_model(prompt)
    
    async def generate_improvement_roadmap(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate improvement roadmap"""
        if not self.github_token:
            return self._fallback_roadmap()
            
        prompt = f"""
        Create an improvement roadmap based on analysis results.
        
        Return JSON format:
        {{
            "immediate_phase": {{
                "duration": "1-2 weeks",
                "tasks": ["Fix critical issues"],
                "effort_estimate": "40 hours"
            }},
            "short_term_phase": {{
                "duration": "1-4 weeks", 
                "tasks": ["Improve test coverage"]
            }}
        }}
        """
        
        return await self._call_ai_model(prompt)
    
    async def _call_ai_model(self, prompt: str) -> Dict[str, Any]:
        """Call AI model with fallback"""
        try:
            # Simplified mock response for demo
            return {
                "ai_analysis_available": True,
                "quality_score": 75,
                "issues": [
                    {
                        "type": "code_quality",
                        "severity": "medium",
                        "description": "AI analysis placeholder - requires GitHub token",
                        "suggestion": "Set up GitHub token for full AI analysis"
                    }
                ],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "error": f"AI analysis failed: {str(e)}",
                "fallback_analysis": True,
                "timestamp": datetime.now().isoformat()
            }
    
    def _fallback_analysis(self, analysis_type: str) -> Dict[str, Any]:
        """Fallback analysis when AI is not available"""
        return {
            "ai_analysis_available": False,
            "quality_score": 70,
            "issues": [
                {
                    "type": analysis_type,
                    "severity": "info",
                    "description": "AI analysis requires GitHub token configuration",
                    "suggestion": "Add GITHUB_TOKEN to .env file for enhanced AI insights"
                }
            ],
            "fallback_analysis": True,
            "timestamp": datetime.now().isoformat()
        }
    
    def _fallback_roadmap(self) -> Dict[str, Any]:
        """Fallback roadmap when AI is not available"""
        return {
            "immediate_phase": {
                "duration": "1-2 weeks",
                "tasks": ["Configure AI features", "Set up GitHub token"],
                "effort_estimate": "2-4 hours"
            },
            "short_term_phase": {
                "duration": "1-4 weeks",
                "tasks": ["Enable AI analysis", "Review AI recommendations"],
                "effort_estimate": "8-16 hours"
            },
            "ai_available": False
        }

class AIEnhancedIssueDetector:
    """Enhanced issue detector with AI capabilities"""
    
    def __init__(self, ai_analyzer: AIAnalyzer):
        self.ai_analyzer = ai_analyzer
    
    async def detect_comprehensive_issues(self, repo_path: str) -> Dict[str, Any]:
        """Detect issues using AI analysis"""
        results = {
            "ai_analysis": {},
            "combined_score": 75,
            "priority_issues": [],
            "improvement_roadmap": {},
            "analysis_summary": {
                "files_analyzed": 0,
                "issues_found": 0,
                "ai_available": bool(self.ai_analyzer.github_token)
            }
        }
        
        # Get code files
        code_files = self._get_code_files(repo_path)
        results["analysis_summary"]["files_analyzed"] = len(code_files)
        
        # Analyze a few key files
        for file_path in code_files[:3]:  # Limit to 3 files
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()[:1000]  # Limit content
                
                language = self._detect_language(file_path)
                ai_result = await self.ai_analyzer.analyze_code_quality(
                    content, file_path, language
                )
                
                results["ai_analysis"][file_path] = ai_result
                
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")
                continue
        
        # Generate roadmap
        roadmap = await self.ai_analyzer.generate_improvement_roadmap(results["ai_analysis"])
        results["improvement_roadmap"] = roadmap
        
        return results
    
    def _get_code_files(self, repo_path: str) -> List[str]:
        """Get code files from repository"""
        code_extensions = {'.py', '.js', '.ts', '.java', '.cs'}
        code_files = []
        
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules'}]
            
            for file in files:
                if Path(file).suffix in code_extensions:
                    code_files.append(os.path.join(root, file))
        
        return code_files[:10]  # Limit files
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language"""
        extension = Path(file_path).suffix
        return {
            '.py': 'python',
            '.js': 'javascript', 
            '.ts': 'typescript',
            '.java': 'java',
            '.cs': 'csharp'
        }.get(extension, 'unknown')