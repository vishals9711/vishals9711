"""
Tests for data models and exception classes.
"""

import pytest
from scripts.models import (
    GitHubStats, PinnedRepository, WakatimeStats, LanguageTime,
    ProcessedData, APIError, RateLimitError
)


def test_pinned_repository_creation():
    """Test PinnedRepository dataclass creation."""
    repo = PinnedRepository(
        name="test-repo",
        description="A test repository",
        url="https://github.com/user/test-repo",
        primary_language="Python",
        stars=42
    )
    
    assert repo.name == "test-repo"
    assert repo.description == "A test repository"
    assert repo.url == "https://github.com/user/test-repo"
    assert repo.primary_language == "Python"
    assert repo.stars == 42


def test_github_stats_creation():
    """Test GitHubStats dataclass creation."""
    pinned_repo = PinnedRepository(
        name="test-repo",
        description="A test repository",
        url="https://github.com/user/test-repo",
        primary_language="Python",
        stars=42
    )
    
    stats = GitHubStats(
        total_contributions=150,
        total_prs=25,
        total_issues=10,
        pinned_repos=[pinned_repo],
        top_languages={"Python": 1000, "JavaScript": 500}
    )
    
    assert stats.total_contributions == 150
    assert stats.total_prs == 25
    assert stats.total_issues == 10
    assert len(stats.pinned_repos) == 1
    assert stats.pinned_repos[0].name == "test-repo"
    assert stats.top_languages["Python"] == 1000


def test_language_time_creation():
    """Test LanguageTime dataclass creation."""
    lang_time = LanguageTime(
        name="Python",
        total_seconds=3600,
        percentage=65.5
    )
    
    assert lang_time.name == "Python"
    assert lang_time.total_seconds == 3600
    assert lang_time.percentage == 65.5


def test_wakatime_stats_creation():
    """Test WakatimeStats dataclass creation."""
    lang_time = LanguageTime(
        name="Python",
        total_seconds=3600,
        percentage=65.5
    )
    
    stats = WakatimeStats(
        total_seconds=5500,
        languages=[lang_time],
        editors=[{"name": "VS Code", "total_seconds": 5500}],
        operating_systems=[{"name": "macOS", "total_seconds": 5500}]
    )
    
    assert stats.total_seconds == 5500
    assert len(stats.languages) == 1
    assert stats.languages[0].name == "Python"
    assert len(stats.editors) == 1
    assert stats.editors[0]["name"] == "VS Code"


def test_processed_data_creation():
    """Test ProcessedData dataclass creation."""
    data = ProcessedData(
        wakatime_summary="📊 1 hr 30 mins coding time",
        language_chart="Python ████████░░ 80%",
        contribution_summary="150 contributions this year",
        pinned_repos_list="• test-repo - A test repository",
        last_updated="2024-01-15"
    )
    
    assert data.wakatime_summary == "📊 1 hr 30 mins coding time"
    assert data.language_chart == "Python ████████░░ 80%"
    assert data.contribution_summary == "150 contributions this year"
    assert data.pinned_repos_list == "• test-repo - A test repository"
    assert data.last_updated == "2024-01-15"


def test_api_error_exception():
    """Test APIError exception class."""
    with pytest.raises(APIError):
        raise APIError("API request failed")


def test_rate_limit_error_exception():
    """Test RateLimitError exception class."""
    with pytest.raises(RateLimitError):
        raise RateLimitError("Rate limit exceeded")
    
    # Test that RateLimitError is a subclass of APIError
    with pytest.raises(APIError):
        raise RateLimitError("Rate limit exceeded")


def test_rate_limit_error_inheritance():
    """Test that RateLimitError inherits from APIError."""
    assert issubclass(RateLimitError, APIError)