#!/usr/bin/env python3
"""
Entry point script for Profile Dynamo profile updates.

This script serves as the main entry point that can be executed directly
by GitHub Actions or manually. It handles the import path setup and
executes the profile update process.
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Now import the modules
from scripts.models import GitHubStats, WakatimeStats, PinnedRepository, LanguageTime, APIError, RateLimitError
from scripts.github_client import GitHubClient
from scripts.wakatime_client import WakatimeClient
from scripts.data_processor import DataProcessor
from scripts.template_engine import TemplateEngine
from scripts.profile_updater import ProfileUpdater

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

def main():
    """
    Main entry point for the profile updater script.
    
    This function reads environment variables for API credentials
    and executes the profile update process.
    """
    logger.info("🚀 Starting Profile Dynamo update process...")
    logger.info("=="*100)
    # Get API credentials from environment variables
    github_token = os.getenv("GH_PAT_TOKEN")
    wakatime_key = os.getenv("WAKATIME_API_KEY")
    
    if not github_token:
        logger.error("GH_PAT_TOKEN environment variable not set")
        raise ValueError("GitHub token is required")
    
    if not wakatime_key:
        logger.error("WAKATIME_API_KEY environment variable not set")
        raise ValueError("Wakatime API key is required")
    
    try:
        # Create and run the profile updater
        updater = ProfileUpdater(github_token, wakatime_key)
        updater.run()
        
        logger.info("✅ Profile update completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Profile update failed: {e}")
        # Don't raise the exception to prevent workflow failure
        # The ProfileUpdater should handle errors gracefully
        sys.exit(1)


if __name__ == "__main__":
    logger.info("🚀 Starting Profile Dynamo update process...")
    main()
