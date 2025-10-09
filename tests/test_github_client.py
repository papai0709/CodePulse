import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
from analyzer.github_client import GitHubClient

class TestGitHubClient(unittest.TestCase):
    """Test cases for GitHubClient"""
    
    def setUp(self):
        self.token = "test_token"
        self.client = GitHubClient(self.token)
    
    @patch('analyzer.github_client.Github')
    def test_init(self, mock_github):
        """Test GitHubClient initialization"""
        client = GitHubClient("test_token")
        mock_github.assert_called_once_with("test_token")
        self.assertEqual(client.token, "test_token")
    
    @patch('analyzer.github_client.Github')
    def test_get_repository_info_success(self, mock_github):
        """Test successful repository info retrieval"""
        # Mock repository object
        mock_repo = Mock()
        mock_repo.name = "test-repo"
        mock_repo.full_name = "owner/test-repo"
        mock_repo.description = "Test repository"
        mock_repo.html_url = "https://github.com/owner/test-repo"
        mock_repo.clone_url = "https://github.com/owner/test-repo.git"
        mock_repo.stargazers_count = 100
        mock_repo.forks_count = 10
        mock_repo.open_issues_count = 5
        mock_repo.size = 1000
        mock_repo.default_branch = "main"
        mock_repo.has_issues = True
        mock_repo.has_projects = True
        mock_repo.has_wiki = True
        mock_repo.license = Mock()
        mock_repo.license.name = "MIT"
        
        # Mock methods
        mock_repo.get_languages.return_value = {"Python": 1000, "JavaScript": 500}
        mock_repo.get_contributors.return_value = [Mock(login="user1"), Mock(login="user2")]
        mock_repo.get_commits.return_value = [Mock() for _ in range(10)]
        mock_repo.get_issues.return_value = [Mock() for _ in range(5)]
        mock_repo.get_topics.return_value = ["python", "web"]
        
        # Mock GitHub client
        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github.return_value = mock_github_instance
        
        client = GitHubClient("test_token")
        result = client.get_repository_info("owner/test-repo")
        
        self.assertEqual(result["name"], "test-repo")
        self.assertEqual(result["full_name"], "owner/test-repo")
        self.assertEqual(result["description"], "Test repository")
        self.assertIn("languages", result)
        self.assertIn("contributors_count", result)
        self.assertEqual(result["license"], "MIT")
    
    @patch('analyzer.github_client.Github')
    def test_get_repository_info_failure(self, mock_github):
        """Test repository info retrieval failure"""
        mock_github_instance = Mock()
        mock_github_instance.get_repo.side_effect = Exception("Repository not found")
        mock_github.return_value = mock_github_instance
        
        client = GitHubClient("test_token")
        
        with self.assertRaises(Exception) as context:
            client.get_repository_info("invalid/repo")
        
        self.assertIn("Failed to fetch repository info", str(context.exception))
    
    @patch('analyzer.github_client.Repo')
    @patch('analyzer.github_client.tempfile')
    @patch('analyzer.github_client.Github')
    def test_clone_repository_success(self, mock_github, mock_tempfile, mock_repo_class):
        """Test successful repository cloning"""
        # Mock tempfile
        mock_tempfile.mkdtemp.return_value = "/tmp/test_dir"
        
        # Mock repository
        mock_repo = Mock()
        mock_repo.clone_url = "https://github.com/owner/repo.git"
        
        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github.return_value = mock_github_instance
        
        # Mock cloned repo
        mock_cloned_repo = Mock()
        mock_repo_class.clone_from.return_value = mock_cloned_repo
        
        client = GitHubClient("test_token")
        result = client.clone_repository("owner/repo")
        
        self.assertEqual(result["local_path"], "/tmp/test_dir")
        self.assertEqual(result["clone_url"], "https://github.com/owner/repo.git")
        self.assertEqual(result["repo_object"], mock_cloned_repo)
        
        mock_repo_class.clone_from.assert_called_once_with(
            "https://github.com/owner/repo.git", 
            "/tmp/test_dir"
        )
    
    @patch('analyzer.github_client.os.path.exists')
    @patch('analyzer.github_client.shutil.rmtree')
    def test_cleanup_temp_directory(self, mock_rmtree, mock_exists):
        """Test cleanup of temporary directory"""
        mock_exists.return_value = True
        
        client = GitHubClient("test_token")
        client.cleanup_temp_directory("/tmp/test_dir")
        
        mock_rmtree.assert_called_once_with("/tmp/test_dir")
    
    def test_cleanup_temp_directory_not_exists(self):
        """Test cleanup when directory doesn't exist"""
        with patch('analyzer.github_client.os.path.exists', return_value=False):
            with patch('analyzer.github_client.shutil.rmtree') as mock_rmtree:
                client = GitHubClient("test_token")
                client.cleanup_temp_directory("/tmp/nonexistent")
                
                mock_rmtree.assert_not_called()

if __name__ == '__main__':
    unittest.main()