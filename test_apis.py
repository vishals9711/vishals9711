#!/usr/bin/env python3
"""
Test script to debug API issues locally.

This script helps test GitHub and Wakatime API connections
to identify authentication and configuration problems.
"""

import os
import sys
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scripts.github_client import GitHubClient
from scripts.wakatime_client import WakatimeClient

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_github_api():
    """Test GitHub API connection and queries."""
    print("🔍 Testing GitHub API...")
    
    # Get token from environment or prompt user
    github_token = os.getenv("GH_TOKEN")
    if not github_token:
        github_token = input("Enter your GitHub token: ").strip()
    
    if not github_token:
        print("❌ No GitHub token provided")
        return False
    
    try:
        client = GitHubClient(github_token)
        
        # Test basic connection
        print("📡 Testing basic GitHub connection...")
        response = client._execute_graphql_query("query { viewer { login } }")
        print(f"✅ GitHub connection successful! User: {response['data']['viewer']['login']}")
        
        # Test profile stats
        print("📊 Testing GitHub profile stats...")
        stats = client.fetch_profile_stats()
        print(f"✅ GitHub stats fetched: {stats}")
        
        # Test pinned repos
        print("📌 Testing GitHub pinned repositories...")
        repos = client.fetch_pinned_repositories()
        print(f"✅ GitHub repos fetched: {len(repos)} repositories")
        
        # Test language stats
        print("💻 Testing GitHub language stats...")
        languages = client.fetch_language_stats()
        print(f"✅ GitHub languages fetched: {len(languages)} languages")
        
        return True
        
    except Exception as e:
        print(f"❌ GitHub API test failed: {e}")
        return False


def test_wakatime_api():
    """Test Wakatime API connection."""
    print("\n🔍 Testing Wakatime API...")
    
    # Get API key from environment or prompt user
    wakatime_key = os.getenv("WAKATIME_API_KEY")
    if not wakatime_key:
        wakatime_key = input("Enter your Wakatime API key: ").strip()
    
    if not wakatime_key:
        print("❌ No Wakatime API key provided")
        return False
    
    try:
        client = WakatimeClient(wakatime_key)
        
        # Test basic connection
        print("📡 Testing basic Wakatime connection...")
        stats = client.fetch_coding_stats()
        print(f"✅ Wakatime connection successful!")
        print(f"📊 Total coding time: {stats['total_seconds']} seconds")
        print(f"💻 Languages: {len(stats['languages'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Wakatime API test failed: {e}")
        return False


def main():
    """Run all API tests."""
    print("🚀 Starting API tests...\n")
    
    github_success = test_github_api()
    wakatime_success = test_wakatime_api()
    
    print(f"\n📋 Test Results:")
    print(f"GitHub API: {'✅ Success' if github_success else '❌ Failed'}")
    print(f"Wakatime API: {'✅ Success' if wakatime_success else '❌ Failed'}")
    
    if github_success and wakatime_success:
        print("\n🎉 All API tests passed! Your configuration is working correctly.")
    else:
        print("\n⚠️  Some API tests failed. Please check your tokens and try again.")
        print("\n💡 Tips:")
        print("- For GitHub: Make sure your token has 'repo' and 'user' scopes")
        print("- For Wakatime: Generate a new API key from https://wakatime.com/settings/account")
        print("- Update your GitHub repository secrets with the correct tokens")


if __name__ == "__main__":
    main()
