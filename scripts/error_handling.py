"""
Error handling utilities for Profile Dynamo.

This module provides robust error handling mechanisms including retry logic,
fallback content management, and comprehensive logging configuration.
"""

import time
import logging
import functools
from typing import Dict, Any, Callable, Optional, Type, Union
from datetime import datetime

from scripts.models import APIError, RateLimitError


# Configure comprehensive logging
def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Set up comprehensive logging configuration for debugging and monitoring.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger instance
    """
    # Create formatter with detailed information
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Create file handler for persistent logging
    try:
        file_handler = logging.FileHandler('profile_dynamo.log')
        file_handler.setLevel(logging.DEBUG)  # Always log debug to file
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        # If file logging fails, continue with console only
        root_logger.warning(f"Could not set up file logging: {e}")
    
    return root_logger


def with_retry(
    max_attempts: int = 3,
    backoff_factor: float = 2.0,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exceptions: tuple = (APIError, RateLimitError, Exception)
) -> Callable:
    """
    Decorator that adds retry logic with exponential backoff to API calls.
    
    Args:
        max_attempts: Maximum number of retry attempts
        backoff_factor: Multiplier for exponential backoff
        initial_delay: Initial delay in seconds before first retry
        max_delay: Maximum delay between retries in seconds
        exceptions: Tuple of exception types to retry on
        
    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(func.__module__)
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    logger.debug(f"Attempting {func.__name__} (attempt {attempt + 1}/{max_attempts})")
                    result = func(*args, **kwargs)
                    
                    if attempt > 0:
                        logger.info(f"{func.__name__} succeeded on attempt {attempt + 1}")
                    
                    return result
                    
                except exceptions as e:
                    last_exception = e
                    
                    # Don't retry on the last attempt
                    if attempt == max_attempts - 1:
                        logger.error(f"{func.__name__} failed after {max_attempts} attempts: {e}")
                        break
                    
                    # Calculate delay with exponential backoff
                    delay = min(initial_delay * (backoff_factor ** attempt), max_delay)
                    
                    # Special handling for rate limit errors
                    if isinstance(e, RateLimitError):
                        # Extract retry-after time if available
                        retry_after = getattr(e, 'retry_after', None)
                        if retry_after:
                            try:
                                delay = max(delay, float(retry_after))
                            except (ValueError, TypeError):
                                pass
                        
                        logger.warning(f"{func.__name__} hit rate limit, retrying in {delay:.1f}s (attempt {attempt + 1}/{max_attempts})")
                    else:
                        logger.warning(f"{func.__name__} failed, retrying in {delay:.1f}s (attempt {attempt + 1}/{max_attempts}): {e}")
                    
                    time.sleep(delay)
                
                except Exception as e:
                    # For unexpected exceptions, log and re-raise immediately
                    logger.error(f"{func.__name__} failed with unexpected error: {e}")
                    raise
            
            # If we get here, all retries failed
            logger.error(f"{func.__name__} exhausted all {max_attempts} retry attempts")
            if last_exception:
                raise last_exception
            else:
                raise APIError(f"{func.__name__} failed after {max_attempts} attempts")
        
        return wrapper
    return decorator


class FallbackContentManager:
    """
    Manages fallback content for when APIs fail.
    
    This class provides comprehensive fallback content that maintains
    the structure and appearance of the README even when APIs are unavailable.
    """
    
    def __init__(self):
        """Initialize the fallback content manager."""
        self.logger = logging.getLogger(__name__)
        self._fallback_content = self._create_fallback_content()
    
    def _create_fallback_content(self) -> Dict[str, str]:
        """
        Create comprehensive fallback content dictionary.
        
        Returns:
            Dictionary mapping template placeholders to fallback content
        """
        current_time = datetime.now().strftime("%B %d, %Y at %H:%M UTC")
        
        return {
            "WAKATIME_STATS": self._get_wakatime_fallback(),
            "GITHUB_LANGUAGES": self._get_languages_fallback(),
            "CONTRIBUTION_STATS": self._get_contributions_fallback(),
            "PINNED_REPOS": self._get_repos_fallback(),
            "LAST_UPDATED": current_time
        }
    
    def _get_wakatime_fallback(self) -> str:
        """Generate fallback content for Wakatime statistics."""
        return """📊 **Coding Activity (Last 7 Days)**

⏱️ Total coding time temporarily unavailable

**Top Languages:**
```
Data will be updated soon...
```

**Editors:**
- Information loading...

**Operating Systems:**
- Data refreshing..."""
    
    def _get_languages_fallback(self) -> str:
        """Generate fallback content for language statistics."""
        return """```
Language stats will be updated soon...
Please check back later for detailed breakdown.
```"""
    
    def _get_contributions_fallback(self) -> str:
        """Generate fallback content for contribution statistics."""
        return """📈 **GitHub Activity**

- 🔥 Contributions: *Loading...*
- 🔀 Pull Requests: *Loading...*
- 🐛 Issues: *Loading...*

*Statistics will be updated shortly*"""
    
    def _get_repos_fallback(self) -> str:
        """Generate fallback content for pinned repositories."""
        return """📌 **Featured Repositories**

Repository information is currently being updated. Please check back soon for the latest projects and contributions."""
    
    def get_fallback_content(self) -> Dict[str, str]:
        """
        Get the current fallback content dictionary.
        
        Returns:
            Dictionary with fallback content for all placeholders
        """
        # Update timestamp each time it's requested
        self._fallback_content["LAST_UPDATED"] = datetime.now().strftime("%B %d, %Y at %H:%M UTC")
        return self._fallback_content.copy()
    
    def get_partial_fallback(self, failed_components: list) -> Dict[str, str]:
        """
        Get fallback content for specific failed components only.
        
        Args:
            failed_components: List of component names that failed
            
        Returns:
            Dictionary with fallback content for specified components
        """
        fallback = {}
        full_fallback = self.get_fallback_content()
        
        for component in failed_components:
            if component in full_fallback:
                fallback[component] = full_fallback[component]
                self.logger.info(f"Using fallback content for {component}")
        
        return fallback


class ReadmePreserver:
    """
    Handles preservation of existing README when operations fail.
    
    This class ensures that the existing README.md is preserved
    when the update process encounters critical failures.
    """
    
    def __init__(self, readme_path: str = "README.md", backup_path: str = "README.md.backup"):
        """
        Initialize the README preserver.
        
        Args:
            readme_path: Path to the main README file
            backup_path: Path for backup README file
        """
        self.readme_path = readme_path
        self.backup_path = backup_path
        self.logger = logging.getLogger(__name__)
    
    def create_backup(self) -> bool:
        """
        Create a backup of the current README file.
        
        Returns:
            True if backup was created successfully, False otherwise
        """
        try:
            import shutil
            
            # Check if README exists
            if not self._file_exists(self.readme_path):
                self.logger.warning(f"No existing README found at {self.readme_path}")
                return False
            
            # Create backup
            shutil.copy2(self.readme_path, self.backup_path)
            self.logger.info(f"Created README backup at {self.backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create README backup: {e}")
            return False
    
    def restore_from_backup(self) -> bool:
        """
        Restore README from backup file.
        
        Returns:
            True if restore was successful, False otherwise
        """
        try:
            import shutil
            
            # Check if backup exists
            if not self._file_exists(self.backup_path):
                self.logger.error(f"No backup file found at {self.backup_path}")
                return False
            
            # Restore from backup
            shutil.copy2(self.backup_path, self.readme_path)
            self.logger.info(f"Restored README from backup")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to restore README from backup: {e}")
            return False
    
    def preserve_on_failure(self, operation_func: Callable, *args, **kwargs) -> Any:
        """
        Execute an operation with README preservation on failure.
        
        Args:
            operation_func: Function to execute
            *args: Arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Result of the operation function
            
        Raises:
            Exception: Re-raises the original exception after attempting restoration
        """
        # Create backup before attempting operation
        backup_created = self.create_backup()
        
        try:
            # Execute the operation
            result = operation_func(*args, **kwargs)
            self.logger.debug("Operation completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Operation failed: {e}")
            
            # Attempt to restore from backup if it was created
            if backup_created:
                self.logger.info("Attempting to restore README from backup")
                if self.restore_from_backup():
                    self.logger.info("README successfully restored from backup")
                else:
                    self.logger.error("Failed to restore README from backup")
            else:
                self.logger.warning("No backup available for restoration")
            
            # Re-raise the original exception
            raise
    
    def _file_exists(self, file_path: str) -> bool:
        """
        Check if a file exists.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            import os
            return os.path.isfile(file_path)
        except Exception:
            return False


# Global instances for easy access
fallback_manager = FallbackContentManager()
readme_preserver = ReadmePreserver()