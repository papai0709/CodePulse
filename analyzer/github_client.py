import os
import tempfile
import shutil
from github import Github
from git import Repo
import requests
from typing import Dict, Optional, Any

class GitHubClient:
    """GitHub API client for repository operations"""
    
    def __init__(self, token: str = None, is_public: bool = True):
        """Initialize GitHub client with optional access token"""
        self.token = token
        self.is_public = is_public
        
        if token:
            self.github = Github(token)
        else:
            # For public repositories, use unauthenticated access
            self.github = Github()
        
        self.session = requests.Session()
        if token:
            self.session.headers.update({'Authorization': f'token {token}'})
        
    def get_repository_info(self, repo_path: str) -> Dict[str, Any]:
        """Get detailed repository information"""
        try:
            if self.is_public and not self.token:
                # For public repositories without token, use GitHub API directly
                return self._get_public_repo_info(repo_path)
            else:
                return self._get_authenticated_repo_info(repo_path)
                
        except Exception as e:
            raise Exception(f"Failed to fetch repository info: {str(e)}")
    
    def _get_public_repo_info(self, repo_path: str) -> Dict[str, Any]:
        """Get repository info for public repos without authentication"""
        try:
            # Use GitHub REST API directly
            api_url = f"https://api.github.com/repos/{repo_path}"
            response = self.session.get(api_url)
            
            if response.status_code == 404:
                raise Exception("Repository not found or is private")
            elif response.status_code != 200:
                raise Exception(f"GitHub API error: {response.status_code}")
            
            repo_data = response.json()
            
            # Get languages (limited info without auth)
            languages_url = f"https://api.github.com/repos/{repo_path}/languages"
            lang_response = self.session.get(languages_url)
            languages = lang_response.json() if lang_response.status_code == 200 else {}
            
            # Get recent commits (limited without auth)
            commits_url = f"https://api.github.com/repos/{repo_path}/commits?per_page=10"
            commits_response = self.session.get(commits_url)
            commits = commits_response.json() if commits_response.status_code == 200 else []
            
            return {
                'name': repo_data.get('name', ''),
                'full_name': repo_data.get('full_name', ''),
                'description': repo_data.get('description', ''),
                'url': repo_data.get('html_url', ''),
                'clone_url': repo_data.get('clone_url', ''),
                'languages': languages,
                'contributors_count': 0,  # Limited without auth
                'contributors': [],
                'recent_commits': len(commits),
                'open_issues': 0,  # Limited without auth
                'stats': {
                    'stars': repo_data.get('stargazers_count', 0),
                    'forks': repo_data.get('forks_count', 0),
                    'open_issues': repo_data.get('open_issues_count', 0),
                    'size': repo_data.get('size', 0),
                    'created_at': repo_data.get('created_at', ''),
                    'updated_at': repo_data.get('updated_at', ''),
                    'default_branch': repo_data.get('default_branch', 'main'),
                    'has_issues': repo_data.get('has_issues', False),
                    'has_projects': repo_data.get('has_projects', False),
                    'has_wiki': repo_data.get('has_wiki', False)
                },
                'topics': repo_data.get('topics', []),
                'license': repo_data.get('license', {}).get('name') if repo_data.get('license') else None
            }
            
        except Exception as e:
            raise Exception(f"Failed to fetch public repository info: {str(e)}")
    
    def _get_authenticated_repo_info(self, repo_path: str) -> Dict[str, Any]:
        """Get repository info using authenticated GitHub client"""
    def _get_authenticated_repo_info(self, repo_path: str) -> Dict[str, Any]:
        """Get repository info using authenticated GitHub client"""
        try:
            repo = self.github.get_repo(repo_path)
            
            # Get languages
            languages = repo.get_languages()
            
            # Get contributors
            contributors = list(repo.get_contributors())
            
            # Get recent commits
            commits = list(repo.get_commits()[:10])
            
            # Get open issues
            open_issues = list(repo.get_issues(state='open')[:20])
            
            # Get repository stats
            stats = {
                'stars': repo.stargazers_count,
                'forks': repo.forks_count,
                'open_issues': repo.open_issues_count,
                'size': repo.size,
                'created_at': repo.created_at,
                'updated_at': repo.updated_at,
                'default_branch': repo.default_branch,
                'has_issues': repo.has_issues,
                'has_projects': repo.has_projects,
                'has_wiki': repo.has_wiki
            }
            
            return {
                'name': repo.name,
                'full_name': repo.full_name,
                'description': repo.description,
                'url': repo.html_url,
                'clone_url': repo.clone_url,
                'languages': languages,
                'contributors_count': len(contributors),
                'contributors': [c.login for c in contributors[:5]],
                'recent_commits': len(commits),
                'open_issues': len(open_issues),
                'stats': stats,
                'topics': repo.get_topics(),
                'license': repo.license.name if repo.license else None
            }
            
        except Exception as e:
            raise Exception(f"Failed to fetch authenticated repository info: {str(e)}")
    
    def clone_repository(self, repo_path: str) -> Dict[str, str]:
        """Clone repository to temporary directory"""
        try:
            if self.is_public and not self.token:
                # For public repositories without token, construct clone URL directly
                clone_url = f"https://github.com/{repo_path}.git"
            else:
                repo = self.github.get_repo(repo_path)
                clone_url = repo.clone_url
            
            # Create temporary directory
            temp_dir = tempfile.mkdtemp(prefix='repo_analyzer_')
            
            # Clone repository
            print(f"Cloning {repo_path} to {temp_dir}")
            cloned_repo = Repo.clone_from(clone_url, temp_dir)
            
            return {
                'local_path': temp_dir,
                'repo_object': cloned_repo,
                'clone_url': clone_url
            }
            
        except Exception as e:
            raise Exception(f"Failed to clone repository: {str(e)}")
    
    def get_file_content(self, repo_path: str, file_path: str, ref: str = None) -> Optional[str]:
        """Get content of a specific file from repository"""
        try:
            repo = self.github.get_repo(repo_path)
            file_content = repo.get_contents(file_path, ref=ref)
            
            if file_content.encoding == 'base64':
                import base64
                return base64.b64decode(file_content.content).decode('utf-8')
            else:
                return file_content.content
                
        except Exception as e:
            print(f"Could not fetch file {file_path}: {str(e)}")
            return None
    
    def search_files(self, repo_path: str, query: str) -> list:
        """Search for files in repository"""
        try:
            repo = self.github.get_repo(repo_path)
            contents = repo.get_contents("")
            
            def search_recursive(contents, query_lower):
                files = []
                for content in contents:
                    if content.type == "dir":
                        files.extend(search_recursive(repo.get_contents(content.path), query_lower))
                    else:
                        if query_lower in content.name.lower():
                            files.append(content.path)
                return files
            
            return search_recursive(contents, query.lower())
            
        except Exception as e:
            print(f"Search failed: {str(e)}")
            return []
    
    def cleanup_temp_directory(self, temp_dir: str):
        """Clean up temporary directory"""
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                print(f"Cleaned up temporary directory: {temp_dir}")
        except Exception as e:
            print(f"Failed to cleanup {temp_dir}: {str(e)}")