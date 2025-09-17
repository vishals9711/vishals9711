"""
Wakatime API client for Profile Dynamo.

This module provides a client for interacting with the Wakatime REST API
to fetch coding activity statistics and time tracking data.
"""

import json
import logging
import base64
from typing import Dict, List, Any, Optional
import requests

from scripts.models import WakatimeStats, LanguageTime, APIError, RateLimitError
from scripts.error_handling import with_retry


logger = logging.getLogger(__name__)


class WakatimeClient:
    """Client for interacting with Wakatime REST API."""

    def __init__(self, api_key: str):
        """
        Initialize the Wakatime client.
        
        Args:
            api_key: Wakatime API key for authentication
        """
        self.api_key = api_key
        self.base_url = "https://wakatime.com/api/v1"
        # Use HTTP Basic Auth with the API key base64-encoded in the Authorization header.
        # The API key is encoded as-is and prefixed with 'Basic '.
        encoded_key = base64.b64encode(api_key.encode("utf-8")).decode("utf-8")
        self.headers = {
            "Authorization": f"Basic {encoded_key}",
            "Content-Type": "application/json",
        }

    @with_retry(max_attempts=3, backoff_factor=2.0, exceptions=(APIError, RateLimitError))
    def fetch_coding_stats(self, range: str = "last_7_days") -> Dict[str, Any]:
        """
        Fetch coding activity statistics for the specified time range.
        
        Args:
            range: Time range for statistics (default: "last_7_days")
            
        Returns:
            Dictionary containing coding statistics including languages, editors, and OS data
            
        Raises:
            APIError: If the API request fails
            RateLimitError: If rate limit is exceeded
        """
        endpoint = f"/users/current/summaries"
        params = {"range": range}

        try:
            response_data = self._make_request(endpoint, params)

            # Extract summary data from the response
            if not response_data.get("data"):
                logger.warning("No data found in Wakatime response")
                return self._get_empty_stats()

            # Calculate totals and extract language data
            total_seconds = 0
            languages_data = {}
            editors_data = {}
            os_data = {}

            # Process each day's data
            for day_data in response_data["data"]:
                if not day_data.get("grand_total"):
                    continue

                # Add to total time
                total_seconds += day_data["grand_total"]["total_seconds"]

                # Aggregate language data
                for lang in day_data.get("languages", []):
                    lang_name = lang["name"]
                    lang_seconds = lang["total_seconds"]

                    if lang_name in languages_data:
                        languages_data[lang_name] += lang_seconds
                    else:
                        languages_data[lang_name] = lang_seconds

                # Aggregate editor data
                for editor in day_data.get("editors", []):
                    editor_name = editor["name"]
                    editor_seconds = editor["total_seconds"]

                    if editor_name in editors_data:
                        editors_data[editor_name] += editor_seconds
                    else:
                        editors_data[editor_name] = editor_seconds

                # Aggregate OS data
                for os in day_data.get("operating_systems", []):
                    os_name = os["name"]
                    os_seconds = os["total_seconds"]

                    if os_name in os_data:
                        os_data[os_name] += os_seconds
                    else:
                        os_data[os_name] = os_seconds

            # Convert to structured format
            languages = []
            for lang_name, lang_seconds in languages_data.items():
                percentage = (lang_seconds / total_seconds * 100) if total_seconds > 0 else 0
                languages.append({
                    "name": lang_name,
                    "total_seconds": lang_seconds,
                    "percentage": round(percentage, 2)
                })

            # Sort languages by time spent
            languages.sort(key=lambda x: x["total_seconds"], reverse=True)

            # Convert editors and OS data to list format
            editors = [{"name": name, "total_seconds": seconds} for name, seconds in editors_data.items()]
            editors.sort(key=lambda x: x["total_seconds"], reverse=True)

            operating_systems = [{"name": name, "total_seconds": seconds} for name, seconds in os_data.items()]
            operating_systems.sort(key=lambda x: x["total_seconds"], reverse=True)

            return {
                "total_seconds": total_seconds,
                "languages": languages,
                "editors": editors,
                "operating_systems": operating_systems
            }

        except (APIError, RateLimitError):
            # Re-raise API and rate limit errors as-is
            raise
        except Exception as e:
            logger.error(f"Failed to fetch coding stats: {e}")
            raise APIError(f"Failed to fetch coding stats: {e}")

    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """
        Make a request to the Wakatime API.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            JSON response from the API
            
        Raises:
            APIError: If the API request fails
            RateLimitError: If rate limit is exceeded
        """
        url = f"{self.base_url}{endpoint}"

        try:
            # Log the request for debugging (without sensitive data)
            logger.debug(f"Making request to Wakatime API: {endpoint}")

            response = requests.get(
                url,
                headers=self.headers,
                params=params or {},
                timeout=30
            )

            # Log response status for debugging
            logger.debug(f"Wakatime API response status: {response.status_code}")

            # Check for rate limiting (Wakatime uses 429 status code)
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After", "unknown")
                error = RateLimitError(f"Wakatime API rate limit exceeded. Retry after: {retry_after} seconds")
                if retry_after and retry_after != "unknown":
                    error.retry_after = retry_after
                raise error

            # Check for authentication errors
            if response.status_code == 401:
                logger.error(f"Wakatime API authentication failed. Response: {response.text[:200]}")
                raise APIError("Wakatime API authentication failed. Check your API key.")

            # Check for other HTTP errors
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request to Wakatime API failed: {e}")
            raise APIError(f"HTTP request to Wakatime API failed: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON response from Wakatime API: {e}")
            raise APIError(f"Failed to decode JSON response from Wakatime API: {e}")

    def _get_empty_stats(self) -> Dict[str, Any]:
        """
        Return empty statistics structure when no data is available.
        
        Returns:
            Dictionary with empty statistics
        """
        return {
            "total_seconds": 0,
            "languages": [],
            "editors": [],
            "operating_systems": []
        }
