"""
Main profile updater script for Profile Dynamo.

This module contains the ProfileUpdater class that serves as the central coordinator
for the entire profile update process, orchestrating data fetching, processing,
and README generation.
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from scripts.models import GitHubStats, WakatimeStats, PinnedRepository, LanguageTime, APIError, RateLimitError
from scripts.github_client import GitHubClient
from scripts.wakatime_client import WakatimeClient
from scripts.data_processor import DataProcessor
from scripts.template_engine import TemplateEngine
from scripts.error_handling import setup_logging, fallback_manager, readme_preserver


# Set up comprehensive logging
logger = setup_logging()


class ProfileUpdater:
    """
    Central coordinator for the profile update process.
    
    The ProfileUpdater orchestrates the entire workflow of fetching data from APIs,
    processing it into formatted content, and generating the final README file.
    """
    
    def __init__(self, github_token: str, wakatime_key: str):
        """
        Initialize the ProfileUpdater with API credentials.
        
        Args:
            github_token: GitHub personal access token
            wakatime_key: Wakatime API key
        """
        self.github_token = github_token
        self.wakatime_key = wakatime_key
        
        # Initialize clients and processors
        self.github_client = GitHubClient(github_token)
        self.wakatime_client = WakatimeClient(wakatime_key)
        self.data_processor = DataProcessor()
        self.template_engine = TemplateEngine()
        
        # Use enhanced fallback content manager
        self.fallback_manager = fallback_manager
        self.readme_preserver = readme_preserver
        
        logger.info("ProfileUpdater initialized successfully")
    
    def run(self) -> None:
        """
        Execute the complete profile update process with comprehensive error handling.
        
        This method orchestrates the entire workflow:
        1. Fetch data from all APIs
        2. Process raw data into formatted content
        3. Generate the final README file
        
        The process includes comprehensive error handling, retry logic,
        and README preservation to ensure the system continues working
        even if individual components fail.
        """
        logger.info("Starting profile update process")
        
        # Use README preserver to protect existing content
        def _update_process():
            # Step 1: Fetch all data from APIs
            logger.info("Fetching data from APIs...")
            raw_data = self._fetch_all_data()
            
            # Step 2: Process raw data into formatted content
            logger.info("Processing data...")
            processed_data = self._process_data(raw_data)
            
            # Step 3: Generate the final README
            logger.info("Generating README...")
            self._generate_readme(processed_data)
            
            logger.info("Profile update completed successfully")
        
        try:
            # Execute the update process with README preservation
            self.readme_preserver.preserve_on_failure(_update_process)
            
        except Exception as e:
            logger.error(f"Profile update failed: {e}")
            
            # Try to generate README with comprehensive fallback content
            try:
                logger.info("Attempting to generate README with fallback content")
                fallback_content = self.fallback_manager.get_fallback_content()
                self._generate_readme(fallback_content)
                logger.info("README generated with fallback content")
                
            except Exception as fallback_error:
                logger.critical(f"Failed to generate README with fallback content: {fallback_error}")
                logger.critical("This indicates a critical system failure")
                
                # Try to restore from backup as last resort
                if self.readme_preserver.restore_from_backup():
                    logger.info("Successfully restored README from backup as last resort")
                else:
                    logger.critical("Unable to restore README from backup - manual intervention required")
                
                raise Exception(f"Complete profile update failure: {e}")
    
    def _fetch_all_data(self) -> Dict[str, Any]:
        """
        Collect data from all APIs with error handling.
        
        Returns:
            Dictionary containing raw data from all APIs, with None values
            for failed API calls
        """
        raw_data = {
            "github_stats": None,
            "github_pinned": None,
            "github_languages": None,
            "wakatime_stats": None
        }
        
        # Fetch GitHub profile statistics
        try:
            logger.info("Fetching GitHub profile statistics...")
            github_profile = self.github_client.fetch_profile_stats()
            raw_data["github_stats"] = github_profile
            logger.info("GitHub profile statistics fetched successfully")
        except (APIError, RateLimitError) as e:
            logger.error(f"Failed to fetch GitHub profile stats: {e}")
        except Exception as e:
            logger.error(f"Unexpected error fetching GitHub profile stats: {e}")
        
        # Fetch GitHub pinned repositories
        try:
            logger.info("Fetching GitHub pinned repositories...")
            github_pinned = self.github_client.fetch_pinned_repositories()
            raw_data["github_pinned"] = github_pinned
            logger.info("GitHub pinned repositories fetched successfully")
        except (APIError, RateLimitError) as e:
            logger.error(f"Failed to fetch GitHub pinned repositories: {e}")
        except Exception as e:
            logger.error(f"Unexpected error fetching GitHub pinned repositories: {e}")
        
        # Fetch GitHub language statistics
        try:
            logger.info("Fetching GitHub language statistics...")
            github_languages = self.github_client.fetch_language_stats()
            raw_data["github_languages"] = github_languages
            logger.info("GitHub language statistics fetched successfully")
        except (APIError, RateLimitError) as e:
            logger.error(f"Failed to fetch GitHub language stats: {e}")
        except Exception as e:
            logger.error(f"Unexpected error fetching GitHub language stats: {e}")
        
        # Fetch Wakatime coding statistics
        try:
            logger.info("Fetching Wakatime coding statistics...")
            wakatime_stats = self.wakatime_client.fetch_coding_stats()
            raw_data["wakatime_stats"] = wakatime_stats
            logger.info("Wakatime coding statistics fetched successfully")
        except (APIError, RateLimitError) as e:
            logger.error(f"Failed to fetch Wakatime stats: {e}")
        except Exception as e:
            logger.error(f"Unexpected error fetching Wakatime stats: {e}")
        
        return raw_data
    
    def _process_data(self, raw_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Transform raw API data into formatted content for template replacement.
        
        Args:
            raw_data: Dictionary containing raw data from all APIs
            
        Returns:
            Dictionary mapping template placeholders to formatted content
        """
        processed_content = {}
        
        # Process GitHub data
        try:
            github_stats = self._create_github_stats(raw_data)
            if github_stats:
                github_processed = self.data_processor.process_github_data(github_stats)
                processed_content.update({
                    "CONTRIBUTION_STATS": github_processed.get("contribution_stats", fallback_manager.get_fallback_content()["CONTRIBUTION_STATS"]),
                    "PINNED_REPOS": github_processed.get("pinned_repos", fallback_manager.get_fallback_content()["PINNED_REPOS"]),
                    "GITHUB_LANGUAGES": github_processed.get("github_languages", fallback_manager.get_fallback_content()["GITHUB_LANGUAGES"])
                })
            else:
                logger.warning("No GitHub data available, using fallback content")
                github_fallback = self.fallback_manager.get_partial_fallback([
                    "CONTRIBUTION_STATS", "PINNED_REPOS", "GITHUB_LANGUAGES"
                ])
                processed_content.update(github_fallback)
        except Exception as e:
            logger.error(f"Error processing GitHub data: {e}")
            github_fallback = self.fallback_manager.get_partial_fallback([
                "CONTRIBUTION_STATS", "PINNED_REPOS", "GITHUB_LANGUAGES"
            ])
            processed_content.update(github_fallback)
        
        # Process Wakatime data
        try:
            wakatime_stats = self._create_wakatime_stats(raw_data)
            if wakatime_stats:
                # Use the new comprehensive summary method
                wakatime_summary = self.data_processor.generate_comprehensive_wakatime_summary(wakatime_stats)
                processed_content["WAKATIME_SUMMARY"] = wakatime_summary
                
                # Use Wakatime languages for main language chart if available
                wakatime_processed = self.data_processor.process_wakatime_data(wakatime_stats)
                if wakatime_processed.get('wakatime_languages') and wakatime_processed['wakatime_languages'] != "No language data available":
                    processed_content["GITHUB_LANGUAGES"] = wakatime_processed['wakatime_languages']
            else:
                logger.warning("No Wakatime data available, using fallback content")
                wakatime_fallback = self.fallback_manager.get_partial_fallback(["WAKATIME_SUMMARY"])
                processed_content.update(wakatime_fallback)
        except Exception as e:
            logger.error(f"Error processing Wakatime data: {e}")
            wakatime_fallback = self.fallback_manager.get_partial_fallback(["WAKATIME_SUMMARY"])
            processed_content.update(wakatime_fallback)
        
        # Generate dynamic sections
        try:
            github_stats_obj = self._create_github_stats(raw_data)
            wakatime_stats_obj = self._create_wakatime_stats(raw_data)
            
            if github_stats_obj and wakatime_stats_obj:
                # Generate dynamic about section
                dynamic_about = self.data_processor.generate_dynamic_about_section(github_stats_obj, wakatime_stats_obj)
                processed_content["DYNAMIC_ABOUT_SECTION"] = dynamic_about
                
                # Generate fun facts
                fun_facts = self.data_processor.generate_fun_facts(github_stats_obj, wakatime_stats_obj)
                processed_content["FUN_FACTS"] = fun_facts
                
                # Generate dynamic tech stack
                dynamic_tech_stack = self.data_processor.generate_dynamic_tech_stack(github_stats_obj, wakatime_stats_obj)
                processed_content["DYNAMIC_TECH_STACK"] = dynamic_tech_stack
                
                # Generate motivational quote
                motivational_quote = self.data_processor.generate_motivational_quote(github_stats_obj, wakatime_stats_obj)
                processed_content["MOTIVATIONAL_QUOTE"] = motivational_quote
                
                # Generate coding streak message
                streak_message = self.data_processor.generate_coding_streak_message(github_stats_obj)
                processed_content["CODING_STREAK_MESSAGE"] = streak_message
                
                logger.info("Dynamic sections generated successfully")
            else:
                # Fallback content
                processed_content.update({
                    "DYNAMIC_ABOUT_SECTION": "Software Engineer @ TNM",
                    "FUN_FACTS": "🌟 Building the future, one commit at a time",
                    "DYNAMIC_TECH_STACK": "![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E) ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![TypeScript](https://img.shields.io/badge/typescript-%23007ACC.svg?style=for-the-badge&logo=typescript&logoColor=white)",
                    "MOTIVATIONAL_QUOTE": "🚀 Code is poetry written in logic",
                    "CODING_STREAK_MESSAGE": "🌟 Ready to start my coding journey!"
                })
        except Exception as e:
            logger.error(f"Error generating dynamic sections: {e}")
            processed_content.update({
                "DYNAMIC_ABOUT_SECTION": "Software Engineer @ TNM",
                "FUN_FACTS": "🌟 Building the future, one commit at a time",
                "DYNAMIC_TECH_STACK": "![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E) ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![TypeScript](https://img.shields.io/badge/typescript-%23007ACC.svg?style=for-the-badge&logo=typescript&logoColor=white)",
                "MOTIVATIONAL_QUOTE": "🚀 Code is poetry written in logic",
                "CODING_STREAK_MESSAGE": "🌟 Ready to start my coding journey!"
            })
        
        # Generate dynamic GitHub stats URLs
        try:
            github_stats_urls = self.data_processor.generate_dynamic_github_stats_urls("vishals9711")
            processed_content.update({
                "GITHUB_STATS_CARD": github_stats_urls['stats_card'],
                "GITHUB_STREAK_STATS": github_stats_urls['streak_stats'],
                "GITHUB_TOP_LANGUAGES": github_stats_urls['top_languages'],
                "GITHUB_TROPHIES": github_stats_urls['trophies']
            })
            logger.info("Dynamic GitHub stats URLs generated successfully")
        except Exception as e:
            logger.error(f"Error generating GitHub stats URLs: {e}")
            # Fallback to static URLs
            processed_content.update({
                "GITHUB_STATS_CARD": "https://github-readme-stats.vercel.app/api?username=vishals9711&theme=dark&hide_border=false&include_all_commits=false&count_private=false",
                "GITHUB_STREAK_STATS": "https://github-readme-streak-stats.herokuapp.com/?user=vishals9711&theme=dark&hide_border=false",
                "GITHUB_TOP_LANGUAGES": "https://github-readme-stats.vercel.app/api/top-langs/?username=vishals9711&theme=dark&hide_border=false&include_all_commits=false&count_private=false&layout=compact",
                "GITHUB_TROPHIES": "https://github-profile-trophy.vercel.app/?username=vishals9711&theme=radical&no-frame=false&no-bg=true&margin-w=4"
            })
        
        # Add last updated timestamp
        processed_content["LAST_UPDATED"] = datetime.now().strftime("%B %d, %Y at %H:%M UTC")
        
        logger.info("Data processing completed")
        return processed_content
    
    def _generate_readme(self, processed_data: Dict[str, str]) -> None:
        """
        Generate the final README file using the template engine.
        
        Args:
            processed_data: Dictionary mapping placeholders to formatted content
        """
        try:
            self.template_engine.process_template(processed_data)
            logger.info("README generation completed successfully")
        except FileNotFoundError as e:
            logger.error(f"Template file not found: {e}")
            raise
        except Exception as e:
            logger.error(f"Error generating README: {e}")
            raise
    
    def _create_github_stats(self, raw_data: Dict[str, Any]) -> Optional[GitHubStats]:
        """
        Create a GitHubStats object from raw API data.
        
        Args:
            raw_data: Dictionary containing raw GitHub API responses
            
        Returns:
            GitHubStats object or None if data is insufficient
        """
        try:
            github_stats_data = raw_data.get("github_stats")
            github_pinned_data = raw_data.get("github_pinned", [])
            github_languages_data = raw_data.get("github_languages", {})
            
            if not github_stats_data:
                logger.warning("No GitHub stats data available")
                return None
            
            # Create PinnedRepository objects
            pinned_repos = []
            for repo_data in github_pinned_data:
                pinned_repo = PinnedRepository(
                    name=repo_data.get("name", "Unknown"),
                    description=repo_data.get("description", ""),
                    url=repo_data.get("url", ""),
                    primary_language=repo_data.get("primary_language", "Unknown"),
                    stars=repo_data.get("stars", 0)
                )
                pinned_repos.append(pinned_repo)
            
            # Create GitHubStats object
            github_stats = GitHubStats(
                total_contributions=github_stats_data.get("total_contributions", 0),
                total_prs=github_stats_data.get("total_prs", 0),
                total_issues=github_stats_data.get("total_issues", 0),
                pinned_repos=pinned_repos,
                top_languages=github_languages_data
            )
            
            return github_stats
            
        except Exception as e:
            logger.error(f"Error creating GitHubStats object: {e}")
            return None
    
    def _create_wakatime_stats(self, raw_data: Dict[str, Any]) -> Optional[WakatimeStats]:
        """
        Create a WakatimeStats object from raw API data.
        
        Args:
            raw_data: Dictionary containing raw Wakatime API response
            
        Returns:
            WakatimeStats object or None if data is insufficient
        """
        try:
            wakatime_data = raw_data.get("wakatime_stats")
            
            if not wakatime_data:
                logger.warning("No Wakatime data available")
                return None
            
            # Create LanguageTime objects
            languages = []
            for lang_data in wakatime_data.get("languages", []):
                language_time = LanguageTime(
                    name=lang_data.get("name", "Unknown"),
                    total_seconds=lang_data.get("total_seconds", 0),
                    percentage=lang_data.get("percentage", 0.0)
                )
                languages.append(language_time)
            
            # Create WakatimeStats object
            wakatime_stats = WakatimeStats(
                total_seconds=wakatime_data.get("total_seconds", 0),
                languages=languages,
                editors=wakatime_data.get("editors", []),
                operating_systems=wakatime_data.get("operating_systems", [])
            )
            
            return wakatime_stats
            
        except Exception as e:
            logger.error(f"Error creating WakatimeStats object: {e}")
            return None


def main():
    """
    Main entry point for the profile updater script.
    
    This function reads environment variables for API credentials
    and executes the profile update process.
    """
    # Get API credentials from environment variables
    github_token = os.getenv("GH_TOKEN")
    wakatime_key = os.getenv("WAKATIME_API_KEY")
    
    if not github_token:
        logger.error("GH_TOKEN environment variable not set")
        raise ValueError("GitHub token is required")
    
    if not wakatime_key:
        logger.error("WAKATIME_API_KEY environment variable not set")
        raise ValueError("Wakatime API key is required")
    
    # Create and run the profile updater
    updater = ProfileUpdater(github_token, wakatime_key)
    updater.run()


if __name__ == "__main__":
    main()
