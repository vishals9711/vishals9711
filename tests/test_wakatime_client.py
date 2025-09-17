"""
Unit tests for WakatimeClient.

This module contains tests for the Wakatime API client functionality,
including successful responses, error handling, and edge cases.
"""

import json
import pytest
from unittest.mock import Mock, patch
import requests

from scripts.wakatime_client import WakatimeClient
from scripts.models import APIError, RateLimitError


class TestWakatimeClient:
    """Test cases for WakatimeClient class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.api_key = "test_api_key"
        self.client = WakatimeClient(self.api_key)
    
    def test_init(self):
        """Test WakatimeClient initialization."""
        assert self.client.api_key == self.api_key
        assert self.client.base_url == "https://wakatime.com/api/v1"
        assert self.client.headers["Authorization"] == f"Bearer {self.api_key}"
        assert self.client.headers["Content-Type"] == "application/json"
    
    @patch('scripts.wakatime_client.requests.get')
    def test_fetch_coding_stats_success(self, mock_get):
        """Test successful fetch of coding statistics."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "grand_total": {"total_seconds": 3600},
                    "languages": [
                        {"name": "Python", "total_seconds": 2400},
                        {"name": "JavaScript", "total_seconds": 1200}
                    ],
                    "editors": [
                        {"name": "VS Code", "total_seconds": 3600}
                    ],
                    "operating_systems": [
                        {"name": "macOS", "total_seconds": 3600}
                    ]
                },
                {
                    "grand_total": {"total_seconds": 1800},
                    "languages": [
                        {"name": "Python", "total_seconds": 1800}
                    ],
                    "editors": [
                        {"name": "VS Code", "total_seconds": 1800}
                    ],
                    "operating_systems": [
                        {"name": "macOS", "total_seconds": 1800}
                    ]
                }
            ]
        }
        mock_get.return_value = mock_response
        
        result = self.client.fetch_coding_stats()
        
        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            "https://wakatime.com/api/v1/users/current/summaries",
            headers=self.client.headers,
            params={"range": "last_7_days"},
            timeout=30
        )
        
        # Verify the processed data
        assert result["total_seconds"] == 5400  # 3600 + 1800
        assert len(result["languages"]) == 2
        
        # Check Python language data (should be aggregated)
        python_lang = next(lang for lang in result["languages"] if lang["name"] == "Python")
        assert python_lang["total_seconds"] == 4200  # 2400 + 1800
        assert python_lang["percentage"] == 77.78  # 4200/5400 * 100
        
        # Check JavaScript language data
        js_lang = next(lang for lang in result["languages"] if lang["name"] == "JavaScript")
        assert js_lang["total_seconds"] == 1200
        assert js_lang["percentage"] == 22.22  # 1200/5400 * 100
        
        # Verify languages are sorted by time spent (Python first)
        assert result["languages"][0]["name"] == "Python"
        assert result["languages"][1]["name"] == "JavaScript"
        
        # Check editors data
        assert len(result["editors"]) == 1
        assert result["editors"][0]["name"] == "VS Code"
        assert result["editors"][0]["total_seconds"] == 5400
        
        # Check OS data
        assert len(result["operating_systems"]) == 1
        assert result["operating_systems"][0]["name"] == "macOS"
        assert result["operating_systems"][0]["total_seconds"] == 5400
    
    @patch('scripts.wakatime_client.requests.get')
    def test_fetch_coding_stats_empty_data(self, mock_get):
        """Test handling of empty data response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        mock_get.return_value = mock_response
        
        result = self.client.fetch_coding_stats()
        
        assert result["total_seconds"] == 0
        assert result["languages"] == []
        assert result["editors"] == []
        assert result["operating_systems"] == []
    
    @patch('scripts.wakatime_client.requests.get')
    def test_fetch_coding_stats_no_data_key(self, mock_get):
        """Test handling of response without data key."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response
        
        result = self.client.fetch_coding_stats()
        
        assert result["total_seconds"] == 0
        assert result["languages"] == []
        assert result["editors"] == []
        assert result["operating_systems"] == []
    
    @patch('scripts.wakatime_client.requests.get')
    def test_fetch_coding_stats_custom_range(self, mock_get):
        """Test fetch with custom time range."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        mock_get.return_value = mock_response
        
        self.client.fetch_coding_stats(range="last_30_days")
        
        mock_get.assert_called_once_with(
            "https://wakatime.com/api/v1/users/current/summaries",
            headers=self.client.headers,
            params={"range": "last_30_days"},
            timeout=30
        )
    
    @patch('scripts.wakatime_client.requests.get')
    def test_fetch_coding_stats_rate_limit_error(self, mock_get):
        """Test handling of rate limit errors."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "60"}
        mock_get.return_value = mock_response
        
        with pytest.raises(RateLimitError) as exc_info:
            self.client.fetch_coding_stats()
        
        assert "rate limit exceeded" in str(exc_info.value).lower()
        assert "60 seconds" in str(exc_info.value)
    
    @patch('scripts.wakatime_client.requests.get')
    def test_fetch_coding_stats_auth_error(self, mock_get):
        """Test handling of authentication errors."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        with pytest.raises(APIError) as exc_info:
            self.client.fetch_coding_stats()
        
        assert "authentication failed" in str(exc_info.value).lower()
        assert "api key" in str(exc_info.value).lower()
    
    @patch('scripts.wakatime_client.requests.get')
    def test_fetch_coding_stats_http_error(self, mock_get):
        """Test handling of HTTP errors."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Server Error")
        mock_get.return_value = mock_response
        
        with pytest.raises(APIError) as exc_info:
            self.client.fetch_coding_stats()
        
        assert "http request" in str(exc_info.value).lower()
    
    @patch('scripts.wakatime_client.requests.get')
    def test_fetch_coding_stats_connection_error(self, mock_get):
        """Test handling of connection errors."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        with pytest.raises(APIError) as exc_info:
            self.client.fetch_coding_stats()
        
        assert "http request" in str(exc_info.value).lower()
        assert "connection failed" in str(exc_info.value).lower()
    
    @patch('scripts.wakatime_client.requests.get')
    def test_fetch_coding_stats_json_decode_error(self, mock_get):
        """Test handling of JSON decode errors."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_get.return_value = mock_response
        
        with pytest.raises(APIError) as exc_info:
            self.client.fetch_coding_stats()
        
        assert "decode json" in str(exc_info.value).lower()
    
    @patch('scripts.wakatime_client.requests.get')
    def test_make_request_success(self, mock_get):
        """Test successful API request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"test": "data"}
        mock_get.return_value = mock_response
        
        result = self.client._make_request("/test", {"param": "value"})
        
        mock_get.assert_called_once_with(
            "https://wakatime.com/api/v1/test",
            headers=self.client.headers,
            params={"param": "value"},
            timeout=30
        )
        assert result == {"test": "data"}
    
    @patch('scripts.wakatime_client.requests.get')
    def test_make_request_no_params(self, mock_get):
        """Test API request without parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"test": "data"}
        mock_get.return_value = mock_response
        
        result = self.client._make_request("/test")
        
        mock_get.assert_called_once_with(
            "https://wakatime.com/api/v1/test",
            headers=self.client.headers,
            params={},
            timeout=30
        )
        assert result == {"test": "data"}
    
    def test_get_empty_stats(self):
        """Test empty statistics structure."""
        result = self.client._get_empty_stats()
        
        assert result["total_seconds"] == 0
        assert result["languages"] == []
        assert result["editors"] == []
        assert result["operating_systems"] == []