#!/usr/bin/env python3
"""
Comprehensive API testing script for Profile Dynamo.

This script tests both GitHub and Wakatime APIs to identify
authentication and configuration issues.
"""

import os
import sys
import requests
import json
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_github_api(github_token):
    """Test GitHub API with detailed debugging."""
    print("🔍 Testing GitHub API...")
    print(f"Token format: {github_token[:10]}...{github_token[-4:]}")
    
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Content-Type": "application/json",
    }
    
    # Test 1: REST API - Basic user info
    print("\n📡 Testing GitHub REST API...")
    try:
        response = requests.get("https://api.github.com/user", headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ GitHub REST API working!")
            print(f"User: {user_data.get('login', 'Unknown')}")
            print(f"Public repos: {user_data.get('public_repos', 0)}")
            print(f"Followers: {user_data.get('followers', 0)}")
            return True
        else:
            print(f"❌ GitHub REST API failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ GitHub REST API error: {e}")
        return False
    
    # Test 2: GraphQL API - Simple query
    print("\n📊 Testing GitHub GraphQL API...")
    try:
        query = """
        query {
          viewer {
            login
          }
        }
        """
        
        response = requests.post(
            "https://api.github.com/graphql",
            headers=headers,
            json={"query": query},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        response_data = response.json()
        
        if response.status_code == 200 and "errors" not in response_data:
            print("✅ GitHub GraphQL API working!")
            print(f"User: {response_data['data']['viewer']['login']}")
            return True
        else:
            print(f"❌ GitHub GraphQL API failed:")
            print(f"Response: {json.dumps(response_data, indent=2)}")
            return False
            
    except Exception as e:
        print(f"❌ GitHub GraphQL API error: {e}")
        return False


def test_wakatime_api(wakatime_key):
    """Test Wakatime API with detailed debugging."""
    print("\n🔍 Testing Wakatime API...")
    print(f"Key format: {wakatime_key[:8]}...{wakatime_key[-4:]}")
    
    headers = {
        "Authorization": f"Bearer {wakatime_key}",
        "Content-Type": "application/json",
    }
    
    # Test 1: Basic user info
    print("\n📡 Testing Wakatime user endpoint...")
    try:
        response = requests.get(
            "https://wakatime.com/api/v1/users/current",
            headers=headers,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            user_data = response.json()
            print("✅ Wakatime API working!")
            print(f"User: {user_data['data']['display_name']}")
            print(f"Username: {user_data['data']['username']}")
            return True
        elif response.status_code == 401:
            print("❌ Wakatime API authentication failed")
            print("This usually means:")
            print("  - API key is invalid or expired")
            print("  - API key format is incorrect")
            print("  - API key doesn't have required permissions")
            return False
        else:
            print(f"⚠️ Unexpected Wakatime API response: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Wakatime API error: {e}")
        return False
    
    # Test 2: Summaries endpoint
    print("\n📊 Testing Wakatime summaries endpoint...")
    try:
        response = requests.get(
            "https://wakatime.com/api/v1/users/current/summaries",
            headers=headers,
            params={"range": "last_7_days"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Wakatime summaries API working!")
            return True
        else:
            print(f"❌ Wakatime summaries API failed: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Wakatime summaries API error: {e}")
        return False


def main():
    """Run comprehensive API tests."""
    print("🚀 Starting comprehensive API tests...\n")
    
    # Get API credentials
    github_token = os.getenv("GH_TOKEN")
    wakatime_key = os.getenv("WAKATIME_API_KEY")
    
    if not github_token:
        github_token = input("Enter your GitHub token: ").strip()
    
    if not wakatime_key:
        wakatime_key = input("Enter your Wakatime API key: ").strip()
    
    if not github_token or not wakatime_key:
        print("❌ Both GitHub token and Wakatime API key are required")
        sys.exit(1)
    
    # Test APIs
    github_success = test_github_api(github_token)
    wakatime_success = test_wakatime_api(wakatime_key)
    
    # Summary
    print(f"\n📋 Test Results:")
    print(f"GitHub API: {'✅ Success' if github_success else '❌ Failed'}")
    print(f"Wakatime API: {'✅ Success' if wakatime_success else '❌ Failed'}")
    
    if github_success and wakatime_success:
        print("\n🎉 All API tests passed! Your configuration is working correctly.")
        print("\n💡 Next steps:")
        print("1. Update your GitHub repository secrets with these working tokens")
        print("2. Commit and push your changes")
        print("3. Trigger the workflow manually to test")
    else:
        print("\n⚠️ Some API tests failed. Please fix the issues above.")
        print("\n💡 Common solutions:")
        print("GitHub:")
        print("  - Ensure token has 'repo' and 'user' scopes")
        print("  - Check token hasn't expired")
        print("Wakatime:")
        print("  - Generate new API key from https://wakatime.com/settings/account")
        print("  - Ensure API key starts with 'waka_'")
        print("  - Check API key has required permissions")


if __name__ == "__main__":
    main()
