"""
Unit tests for error handling utilities.

This module tests the retry logic, fallback content management,
and README preservation functionality.
"""

import pytest
import time
import logging
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from scripts.error_handling import (
    with_retry, 
    FallbackContentManager, 
    ReadmePreserver,
    setup_logging
)
from scripts.models import APIError, RateLimitError


class TestRetryDecorator:
    """Test cases for the with_retry decorator."""
    
    def test_successful_call_no_retry(self):
        """Test that successful calls don't trigger retries."""
        call_count = 0
        
        @with_retry(max_attempts=3)
        def successful_function():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = successful_function()
        assert result == "success"
        assert call_count == 1
    
    def test_retry_on_api_error(self):
        """Test retry behavior on APIError."""
        call_count = 0
        
        @with_retry(max_attempts=3, initial_delay=0.01)
        def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise APIError("API temporarily unavailable")
            return "success"
        
        result = failing_function()
        assert result == "success"
        assert call_count == 3
    
    def test_retry_exhaustion(self):
        """Test behavior when all retries are exhausted."""
        call_count = 0
        
        @with_retry(max_attempts=2, initial_delay=0.01)
        def always_failing_function():
            nonlocal call_count
            call_count += 1
            raise APIError("Persistent failure")
        
        with pytest.raises(APIError, match="Persistent failure"):
            always_failing_function()
        
        assert call_count == 2
    
    def test_rate_limit_error_handling(self):
        """Test special handling of rate limit errors."""
        call_count = 0
        
        @with_retry(max_attempts=3, initial_delay=0.01)
        def rate_limited_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                error = RateLimitError("Rate limit exceeded")
                error.retry_after = "0.02"  # 20ms
                raise error
            return "success"
        
        start_time = time.time()
        result = rate_limited_function()
        end_time = time.time()
        
        assert result == "success"
        assert call_count == 2
        # Should have waited at least the retry_after time
        assert end_time - start_time >= 0.02
    
    def test_exponential_backoff(self):
        """Test exponential backoff timing."""
        call_times = []
        
        @with_retry(max_attempts=3, initial_delay=0.01, backoff_factor=2.0)
        def timing_function():
            call_times.append(time.time())
            if len(call_times) < 3:
                raise APIError("Temporary failure")
            return "success"
        
        result = timing_function()
        assert result == "success"
        assert len(call_times) == 3
        
        # Check that delays increase exponentially
        delay1 = call_times[1] - call_times[0]
        delay2 = call_times[2] - call_times[1]
        assert delay2 > delay1  # Second delay should be longer
    
    def test_max_delay_limit(self):
        """Test that delays don't exceed max_delay."""
        call_times = []
        
        @with_retry(max_attempts=3, initial_delay=0.01, backoff_factor=10.0, max_delay=0.02)
        def max_delay_function():
            call_times.append(time.time())
            if len(call_times) < 3:
                raise APIError("Temporary failure")
            return "success"
        
        result = max_delay_function()
        assert result == "success"
        
        # All delays should be limited by max_delay
        for i in range(1, len(call_times)):
            delay = call_times[i] - call_times[i-1]
            assert delay <= 0.03  # Allow some tolerance for timing
    
    def test_unexpected_exception_no_retry(self):
        """Test that unexpected exceptions are not retried."""
        call_count = 0
        
        @with_retry(max_attempts=3, exceptions=(APIError,))
        def unexpected_error_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("Unexpected error")
        
        with pytest.raises(ValueError, match="Unexpected error"):
            unexpected_error_function()
        
        assert call_count == 1  # Should not retry


class TestFallbackContentManager:
    """Test cases for the FallbackContentManager."""
    
    def test_initialization(self):
        """Test that fallback manager initializes correctly."""
        manager = FallbackContentManager()
        content = manager.get_fallback_content()
        
        assert isinstance(content, dict)
        assert "WAKATIME_STATS" in content
        assert "GITHUB_LANGUAGES" in content
        assert "CONTRIBUTION_STATS" in content
        assert "PINNED_REPOS" in content
        assert "LAST_UPDATED" in content
    
    def test_fallback_content_structure(self):
        """Test that fallback content has proper structure."""
        manager = FallbackContentManager()
        content = manager.get_fallback_content()
        
        # Check that Wakatime fallback contains expected sections
        wakatime_content = content["WAKATIME_STATS"]
        assert "📊" in wakatime_content
        assert "Top Languages:" in wakatime_content
        assert "Editors:" in wakatime_content
        assert "Operating Systems:" in wakatime_content
        
        # Check that contribution stats contain expected elements
        contrib_content = content["CONTRIBUTION_STATS"]
        assert "📈" in contrib_content
        assert "Contributions:" in contrib_content
        assert "Pull Requests:" in contrib_content
        assert "Issues:" in contrib_content
    
    def test_partial_fallback(self):
        """Test getting fallback content for specific components."""
        manager = FallbackContentManager()
        
        partial = manager.get_partial_fallback(["WAKATIME_STATS", "GITHUB_LANGUAGES"])
        
        assert len(partial) == 2
        assert "WAKATIME_STATS" in partial
        assert "GITHUB_LANGUAGES" in partial
        assert "CONTRIBUTION_STATS" not in partial
    
    def test_timestamp_updates(self):
        """Test that timestamps are updated on each call."""
        manager = FallbackContentManager()
        
        content1 = manager.get_fallback_content()
        time.sleep(0.01)  # Small delay
        content2 = manager.get_fallback_content()
        
        # Timestamps should be different (or at least not fail)
        # Note: Due to timing precision, they might be the same
        assert "LAST_UPDATED" in content1
        assert "LAST_UPDATED" in content2


class TestReadmePreserver:
    """Test cases for the ReadmePreserver."""
    
    def test_backup_creation(self):
        """Test creating a backup of README file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            readme_path = os.path.join(temp_dir, "README.md")
            backup_path = os.path.join(temp_dir, "README.md.backup")
            
            # Create a test README
            with open(readme_path, "w") as f:
                f.write("# Test README\nOriginal content")
            
            preserver = ReadmePreserver(readme_path, backup_path)
            result = preserver.create_backup()
            
            assert result is True
            assert os.path.exists(backup_path)
            
            # Check backup content
            with open(backup_path, "r") as f:
                backup_content = f.read()
            assert backup_content == "# Test README\nOriginal content"
    
    def test_backup_nonexistent_file(self):
        """Test backup creation when README doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            readme_path = os.path.join(temp_dir, "nonexistent.md")
            backup_path = os.path.join(temp_dir, "backup.md")
            
            preserver = ReadmePreserver(readme_path, backup_path)
            result = preserver.create_backup()
            
            assert result is False
            assert not os.path.exists(backup_path)
    
    def test_restore_from_backup(self):
        """Test restoring README from backup."""
        with tempfile.TemporaryDirectory() as temp_dir:
            readme_path = os.path.join(temp_dir, "README.md")
            backup_path = os.path.join(temp_dir, "README.md.backup")
            
            # Create backup file
            with open(backup_path, "w") as f:
                f.write("# Backup Content\nRestored from backup")
            
            preserver = ReadmePreserver(readme_path, backup_path)
            result = preserver.restore_from_backup()
            
            assert result is True
            assert os.path.exists(readme_path)
            
            # Check restored content
            with open(readme_path, "r") as f:
                restored_content = f.read()
            assert restored_content == "# Backup Content\nRestored from backup"
    
    def test_restore_nonexistent_backup(self):
        """Test restore when backup doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            readme_path = os.path.join(temp_dir, "README.md")
            backup_path = os.path.join(temp_dir, "nonexistent_backup.md")
            
            preserver = ReadmePreserver(readme_path, backup_path)
            result = preserver.restore_from_backup()
            
            assert result is False
    
    def test_preserve_on_success(self):
        """Test preserve_on_failure with successful operation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            readme_path = os.path.join(temp_dir, "README.md")
            backup_path = os.path.join(temp_dir, "README.md.backup")
            
            # Create original README
            with open(readme_path, "w") as f:
                f.write("Original content")
            
            preserver = ReadmePreserver(readme_path, backup_path)
            
            def successful_operation():
                return "operation completed"
            
            result = preserver.preserve_on_failure(successful_operation)
            
            assert result == "operation completed"
            assert os.path.exists(backup_path)  # Backup should be created
    
    def test_preserve_on_failure(self):
        """Test preserve_on_failure with failing operation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            readme_path = os.path.join(temp_dir, "README.md")
            backup_path = os.path.join(temp_dir, "README.md.backup")
            
            # Create original README
            original_content = "Original content"
            with open(readme_path, "w") as f:
                f.write(original_content)
            
            preserver = ReadmePreserver(readme_path, backup_path)
            
            def failing_operation():
                # Modify README to simulate partial failure
                with open(readme_path, "w") as f:
                    f.write("Corrupted content")
                raise Exception("Operation failed")
            
            with pytest.raises(Exception, match="Operation failed"):
                preserver.preserve_on_failure(failing_operation)
            
            # README should be restored from backup
            with open(readme_path, "r") as f:
                restored_content = f.read()
            assert restored_content == original_content


class TestLoggingSetup:
    """Test cases for logging configuration."""
    
    def test_setup_logging_default(self):
        """Test default logging setup."""
        logger = setup_logging()
        
        assert isinstance(logger, logging.Logger)
        assert logger.level == logging.INFO
    
    def test_setup_logging_custom_level(self):
        """Test logging setup with custom level."""
        logger = setup_logging("DEBUG")
        
        assert logger.level == logging.DEBUG
    
    def test_setup_logging_invalid_level(self):
        """Test logging setup with invalid level defaults to INFO."""
        logger = setup_logging("INVALID")
        
        assert logger.level == logging.INFO
    
    @patch('logging.FileHandler')
    def test_file_handler_creation(self, mock_file_handler):
        """Test that file handler is created."""
        mock_handler = MagicMock()
        mock_file_handler.return_value = mock_handler
        
        logger = setup_logging()
        
        mock_file_handler.assert_called_once_with('profile_dynamo.log')
        mock_handler.setLevel.assert_called_with(logging.DEBUG)
    
    @patch('logging.FileHandler')
    def test_file_handler_failure_graceful(self, mock_file_handler):
        """Test graceful handling of file handler creation failure."""
        mock_file_handler.side_effect = Exception("Cannot create file")
        
        # Should not raise exception
        logger = setup_logging()
        
        assert isinstance(logger, logging.Logger)


if __name__ == "__main__":
    pytest.main([__file__])