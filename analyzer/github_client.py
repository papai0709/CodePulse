import os
import tempfile
import shutil
import subprocess
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
            # Validate repo_path format
            if not repo_path or '/' not in repo_path:
                raise Exception(f"Invalid repository path format: {repo_path}")
            
            # Split and validate parts
            path_parts = repo_path.split('/')
            if len(path_parts) != 2:
                raise Exception(f"Repository path must be in format 'owner/repo', got: {repo_path}")
            
            owner, repo_name = path_parts
            if not owner or not repo_name:
                raise Exception(f"Invalid owner or repository name in: {repo_path}")
            
            print(f"Fetching repository info for: {owner}/{repo_name}")
            
            repo = self.github.get_repo(repo_path)
            
            # Get languages with error handling
            try:
                languages = repo.get_languages()
            except Exception as e:
                print(f"Warning: Could not fetch languages: {e}")
                languages = {}
            
            # Get contributors with error handling
            try:
                contributors = list(repo.get_contributors())
            except Exception as e:
                print(f"Warning: Could not fetch contributors: {e}")
                contributors = []
            
            # Get recent commits with error handling
            try:
                commits = list(repo.get_commits()[:10])
            except Exception as e:
                print(f"Warning: Could not fetch commits: {e}")
                commits = []
            
            # Get open issues with error handling
            try:
                open_issues = list(repo.get_issues(state='open')[:20])
            except Exception as e:
                print(f"Warning: Could not fetch issues: {e}")
                open_issues = []
            
            # Get repository stats
            stats = {
                'stars': getattr(repo, 'stargazers_count', 0),
                'forks': getattr(repo, 'forks_count', 0),
                'open_issues': getattr(repo, 'open_issues_count', 0),
                'size': getattr(repo, 'size', 0),
                'created_at': getattr(repo, 'created_at', None),
                'updated_at': getattr(repo, 'updated_at', None),
                'default_branch': getattr(repo, 'default_branch', 'main'),
                'has_issues': getattr(repo, 'has_issues', False),
                'has_projects': getattr(repo, 'has_projects', False),
                'has_wiki': getattr(repo, 'has_wiki', False)
            }
            
            # Get topics with error handling
            try:
                topics = repo.get_topics()
            except Exception as e:
                print(f"Warning: Could not fetch topics: {e}")
                topics = []
            
            # Get license with error handling
            try:
                license_name = repo.license.name if repo.license else None
            except Exception as e:
                print(f"Warning: Could not fetch license: {e}")
                license_name = None
            
            return {
                'name': getattr(repo, 'name', ''),
                'full_name': getattr(repo, 'full_name', ''),
                'description': getattr(repo, 'description', ''),
                'url': getattr(repo, 'html_url', ''),
                'clone_url': getattr(repo, 'clone_url', ''),
                'languages': languages,
                'contributors_count': len(contributors),
                'contributors': [getattr(c, 'login', 'unknown') for c in contributors[:5]],
                'recent_commits': len(commits),
                'open_issues': len(open_issues),
                'stats': stats,
                'topics': topics,
                'license': license_name
            }
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error in _get_authenticated_repo_info: {error_details}")
            raise Exception(f"Failed to fetch authenticated repository info: {str(e)}")
    
    def clone_repository(self, repo_path: str) -> Dict[str, str]:
        """Clone repository to temporary directory"""
        try:
            if self.is_public and not self.token:
                # For public repositories without token, construct clone URL directly
                clone_url = f"https://github.com/{repo_path}.git"
            else:
                # For private repositories or when token is available, use authenticated clone URL
                if self.token:
                    # Use token authentication in the clone URL
                    clone_url = f"https://{self.token}@github.com/{repo_path}.git"
                else:
                    # Fallback to regular clone URL (might fail for private repos)
                    repo = self.github.get_repo(repo_path)
                    clone_url = repo.clone_url
            
            # Create temporary directory
            temp_dir = tempfile.mkdtemp(prefix='repo_analyzer_')
            
            # Clone repository
            print(f"Cloning {repo_path} to {temp_dir}")
            
            # Use GitPython's clone_from with authenticated URL
            cloned_repo = Repo.clone_from(clone_url, temp_dir)
            
            return {
                'local_path': temp_dir,
                'repo_object': cloned_repo,
                'clone_url': clone_url
            }
            
        except Exception as e:
            # Clean up on failure
            if 'temp_dir' in locals() and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
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