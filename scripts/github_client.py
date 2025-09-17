"""
GitHub API client for Profile Dynamo.

This module provides a client for interacting with the GitHub GraphQL API
to fetch profile statistics, pinned repositories, and language usage data.
"""

import json
import logging
from typing import Dict, List, Any, Optional
import requests

from scripts.models import GitHubStats, PinnedRepository, APIError, RateLimitError
from scripts.error_handling import with_retry


logger = logging.getLogger(__name__)


class GitHubClient:
    """Client for interacting with GitHub GraphQL API."""
    
    def __init__(self, token: str):
        """
        Initialize the GitHub client.
        
        Args:
            token: GitHub personal access token with repo and user scopes
        """
        self.token = token
        self.base_url = "https://api.github.com/graphql"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
    
    @with_retry(max_attempts=3, backoff_factor=2.0, exceptions=(APIError, RateLimitError))
    def fetch_profile_stats(self) -> Dict[str, Any]:
        """
        Fetch GitHub profile statistics including contributions, PRs, and issues.
        
        Returns:
            Dictionary containing profile statistics
            
        Raises:
            APIError: If the API request fails
            RateLimitError: If rate limit is exceeded
        """
        query = """
        query {
          viewer {
            contributionsCollection {
              totalCommitContributions
              totalPullRequestContributions
              totalIssueContributions
            }
          }
        }
        """
        
        try:
            response = self._execute_graphql_query(query)
            contributions = response["data"]["viewer"]["contributionsCollection"]
            
            return {
                "total_contributions": contributions["totalCommitContributions"],
                "total_prs": contributions["totalPullRequestContributions"],
                "total_issues": contributions["totalIssueContributions"]
            }
        except (APIError, RateLimitError):
            # Re-raise API and rate limit errors as-is
            raise
        except Exception as e:
            logger.error(f"Failed to fetch profile stats: {e}")
            raise APIError(f"Failed to fetch profile stats: {e}")
    
    @with_retry(max_attempts=3, backoff_factor=2.0, exceptions=(APIError, RateLimitError))
    def fetch_pinned_repositories(self) -> List[Dict]:
        """
        Fetch the user's top 5 pinned repositories.
        
        Returns:
            List of dictionaries containing pinned repository data
            
        Raises:
            APIError: If the API request fails
            RateLimitError: If rate limit is exceeded
        """
        query = """
        query {
          viewer {
            pinnedItems(first: 5, types: [REPOSITORY]) {
              nodes {
                ... on Repository {
                  name
                  description
                  url
                  primaryLanguage {
                    name
                  }
                  stargazerCount
                }
              }
            }
          }
        }
        """
        
        try:
            response = self._execute_graphql_query(query)
            pinned_items = response["data"]["viewer"]["pinnedItems"]["nodes"]
            
            repositories = []
            for repo in pinned_items:
                repositories.append({
                    "name": repo["name"],
                    "description": repo.get("description", ""),
                    "url": repo["url"],
                    "primary_language": repo["primaryLanguage"]["name"] if repo.get("primaryLanguage") else "Unknown",
                    "stars": repo["stargazerCount"]
                })
            
            return repositories
        except (APIError, RateLimitError):
            # Re-raise API and rate limit errors as-is
            raise
        except Exception as e:
            logger.error(f"Failed to fetch pinned repositories: {e}")
            raise APIError(f"Failed to fetch pinned repositories: {e}")
    
    @with_retry(max_attempts=3, backoff_factor=2.0, exceptions=(APIError, RateLimitError))
    def fetch_language_stats(self) -> Dict[str, int]:
        """
        Fetch and aggregate programming language usage across repositories.
        
        Returns:
            Dictionary mapping language names to total bytes of code
            
        Raises:
            APIError: If the API request fails
            RateLimitError: If rate limit is exceeded
        """
        query = """
        query {
          viewer {
            repositories(first: 100, ownerAffiliations: OWNER, orderBy: {field: UPDATED_AT, direction: DESC}) {
              nodes {
                languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
                  edges {
                    size
                    node {
                      name
                    }
                  }
                }
              }
            }
          }
        }
        """
        
        try:
            response = self._execute_graphql_query(query)
            repositories = response["data"]["viewer"]["repositories"]["nodes"]
            
            language_stats = {}
            for repo in repositories:
                for language_edge in repo["languages"]["edges"]:
                    language_name = language_edge["node"]["name"]
                    language_size = language_edge["size"]
                    
                    if language_name in language_stats:
                        language_stats[language_name] += language_size
                    else:
                        language_stats[language_name] = language_size
            
            # Sort by size and return top languages
            sorted_languages = dict(sorted(language_stats.items(), key=lambda x: x[1], reverse=True))
            return sorted_languages
        except (APIError, RateLimitError):
            # Re-raise API and rate limit errors as-is
            raise
        except Exception as e:
            logger.error(f"Failed to fetch language stats: {e}")
            raise APIError(f"Failed to fetch language stats: {e}")
    
    def _execute_graphql_query(self, query: str) -> Dict:
        """
        Execute a GraphQL query against the GitHub API.
        
        Args:
            query: GraphQL query string
            
        Returns:
            JSON response from the API
            
        Raises:
            APIError: If the API request fails
            RateLimitError: If rate limit is exceeded
        """
        payload = {"query": query}
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            # Check for rate limiting
            if response.status_code == 403:
                rate_limit_remaining = response.headers.get("X-RateLimit-Remaining", "0")
                if rate_limit_remaining == "0":
                    reset_time = response.headers.get("X-RateLimit-Reset", "unknown")
                    retry_after = response.headers.get("Retry-After")
                    error = RateLimitError(f"GitHub API rate limit exceeded. Resets at: {reset_time}")
                    if retry_after:
                        error.retry_after = retry_after
                    raise error
            
            # Check for other HTTP errors
            response.raise_for_status()
            
            json_response = response.json()
            
            # Check for GraphQL errors
            if "errors" in json_response:
                error_messages = [error.get("message", "Unknown error") for error in json_response["errors"]]
                raise APIError(f"GraphQL errors: {', '.join(error_messages)}")
            
            return json_response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request failed: {e}")
            raise APIError(f"HTTP request failed: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON response: {e}")
            raise APIError(f"Failed to decode JSON response: {e}")