"""
Tests for the GitHub API client.
"""

import json
import pytest
from unittest.mock import Mock, patch
import requests

from scripts.github_client import GitHubClient
from scripts.models import APIError, RateLimitError


class TestGitHubClient:
    """Test cases for GitHubClient class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = GitHubClient("test_token")
    
    @patch('scripts.github_client.requests.post')
    def test_fetch_profile_stats_success(self, mock_post):
        """Test successful profile stats fetching."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "viewer": {
                    "contributionsCollection": {
                        "totalCommitContributions": 150,
                        "totalPullRequestContributions": 25,
                        "totalIssueContributions": 10
                    }
                }
            }
        }
        mock_post.return_value = mock_response
        
        result = self.client.fetch_profile_stats()
        
        assert result["total_contributions"] == 150
        assert result["total_prs"] == 25
        assert result["total_issues"] == 10
    
    @patch('scripts.github_client.requests.post')
    def test_fetch_pinned_repositories_success(self, mock_post):
        """Test successful pinned repositories fetching."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "viewer": {
                    "pinnedItems": {
                        "nodes": [
                            {
                                "name": "test-repo",
                                "description": "A test repository",
                                "url": "https://github.com/user/test-repo",
                                "primaryLanguage": {"name": "Python"},
                                "stargazerCount": 42
                            }
                        ]
                    }
                }
            }
        }
        mock_post.return_value = mock_response
        
        result = self.client.fetch_pinned_repositories()
        
        assert len(result) == 1
        assert result[0]["name"] == "test-repo"
        assert result[0]["description"] == "A test repository"
        assert result[0]["primary_language"] == "Python"
        assert result[0]["stars"] == 42
    
    @patch('scripts.github_client.requests.post')
    def test_fetch_language_stats_success(self, mock_post):
        """Test successful language stats fetching."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "viewer": {
                    "repositories": {
                        "nodes": [
                            {
                                "languages": {
                                    "edges": [
                                        {"size": 1000, "node": {"name": "Python"}},
                                        {"size": 500, "node": {"name": "JavaScript"}}
                                    ]
                                }
                            },
                            {
                                "languages": {
                                    "edges": [
                                        {"size": 800, "node": {"name": "Python"}},
                                        {"size": 300, "node": {"name": "TypeScript"}}
                                    ]
                                }
                            }
                        ]
                    }
                }
            }
        }
        mock_post.return_value = mock_response
        
        result = self.client.fetch_language_stats()
        
        # Python should be aggregated: 1000 + 800 = 1800
        assert result["Python"] == 1800
        assert result["JavaScript"] == 500
        assert result["TypeScript"] == 300
    
    @patch('scripts.github_client.requests.post')
    def test_rate_limit_error(self, mock_post):
        """Test rate limit error handling."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.headers = {
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": "1234567890"
        }
        mock_post.return_value = mock_response
        
        with pytest.raises(RateLimitError) as exc_info:
            self.client.fetch_profile_stats()
        
        assert "rate limit exceeded" in str(exc_info.value).lower()
    
    @patch('scripts.github_client.requests.post')
    def test_graphql_error_handling(self, mock_post):
        """Test GraphQL error handling."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "errors": [
                {"message": "Field 'invalidField' doesn't exist on type 'User'"}
            ]
        }
        mock_post.return_value = mock_response
        
        with pytest.raises(APIError) as exc_info:
            self.client.fetch_profile_stats()
        
        assert "GraphQL errors" in str(exc_info.value)
    
    @patch('scripts.github_client.requests.post')
    def test_http_error_handling(self, mock_post):
        """Test HTTP error handling."""
        mock_post.side_effect = requests.exceptions.RequestException("Connection error")
        
        with pytest.raises(APIError) as exc_info:
            self.client.fetch_profile_stats()
        
        assert "HTTP request failed" in str(exc_info.value)
    
    @patch('scripts.github_client.requests.post')
    def test_json_decode_error(self, mock_post):
        """Test JSON decode error handling."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_post.return_value = mock_response
        
        with pytest.raises(APIError) as exc_info:
            self.client.fetch_profile_stats()
        
        assert "Failed to decode JSON response" in str(exc_info.value)