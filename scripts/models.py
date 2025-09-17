"""
Data models and exception classes for Profile Dynamo.

This module contains all the dataclasses used to structure data from APIs
and the custom exception classes for error handling.
"""

from dataclasses import dataclass
from typing import List, Dict, Any


# Exception Classes
class APIError(Exception):
    """Base exception for API-related errors."""
    pass


class RateLimitError(APIError):
    """Exception raised when API rate limits are exceeded."""
    pass


# GitHub Data Models
@dataclass
class PinnedRepository:
    """Represents a pinned GitHub repository."""
    name: str
    description: str
    url: str
    primary_language: str
    stars: int


@dataclass
class GitHubStats:
    """Represents GitHub profile statistics."""
    total_contributions: int
    total_prs: int
    total_issues: int
    pinned_repos: List[PinnedRepository]
    top_languages: Dict[str, int]


# Wakatime Data Models
@dataclass
class LanguageTime:
    """Represents time spent coding in a specific language."""
    name: str
    total_seconds: int
    percentage: float


@dataclass
class WakatimeStats:
    """Represents Wakatime coding statistics."""
    total_seconds: int
    languages: List[LanguageTime]
    editors: List[Dict[str, Any]]  # Flexible structure for editor data
    operating_systems: List[Dict[str, Any]]  # Flexible structure for OS data


# Processed Data Model
@dataclass
class ProcessedData:
    """Represents processed and formatted data ready for template insertion."""
    wakatime_summary: str
    language_chart: str
    contribution_summary: str
    pinned_repos_list: str
    last_updated: str