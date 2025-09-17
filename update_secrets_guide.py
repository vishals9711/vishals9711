#!/usr/bin/env python3
"""
GitHub Secrets Update Helper

This script provides instructions for updating GitHub repository secrets
with the correct API keys for Profile Dynamo.
"""

def print_instructions():
    """Print step-by-step instructions for updating GitHub secrets."""
    
    print("🔧 GitHub Secrets Update Instructions")
    print("=" * 50)
    
    print("\n📋 Step 1: Get Your API Keys")
    print("-" * 30)
    print("GitHub Token:")
    print("  1. Go to: https://github.com/settings/tokens")
    print("  2. Click 'Generate new token' → 'Generate new token (classic)'")
    print("  3. Select scopes: 'repo', 'user', 'read:org'")
    print("  4. Copy the generated token")
    
    print("\nWakatime API Key:")
    print("  1. Go to: https://wakatime.com/settings/account")
    print("  2. Scroll to 'API Keys' section")
    print("  3. Click 'Generate API Key' or 'Regenerate API Key'")
    print("  4. Copy the generated key (starts with 'waka_')")
    
    print("\n📋 Step 2: Update GitHub Repository Secrets")
    print("-" * 40)
    print("  1. Go to your repository: https://github.com/vishals9711/vishals9711")
    print("  2. Click 'Settings' tab")
    print("  3. In left sidebar, click 'Secrets and variables' → 'Actions'")
    print("  4. Update these secrets:")
    print("     - GH_TOKEN: Your GitHub token")
    print("     - WAKATIME_API_KEY: Your Wakatime API key")
    
    print("\n📋 Step 3: Test the Configuration")
    print("-" * 35)
    print("  1. Run: python test_apis_comprehensive.py")
    print("  2. Enter your API keys when prompted")
    print("  3. Verify both APIs return '✅ Success'")
    
    print("\n📋 Step 4: Deploy and Test")
    print("-" * 25)
    print("  1. Commit your changes:")
    print("     git add .")
    print("     git commit -m 'feat: improve API resilience and error handling'")
    print("     git push")
    print("  2. Go to Actions tab in your repository")
    print("  3. Click 'Update Profile README' workflow")
    print("  4. Click 'Run workflow' button")
    print("  5. Monitor the logs for successful API calls")
    
    print("\n🎯 Expected Results")
    print("-" * 20)
    print("✅ GitHub API: Should fetch real contribution stats")
    print("✅ Wakatime API: Should fetch real coding activity")
    print("✅ README: Should update with actual data instead of fallback content")
    
    print("\n🆘 Troubleshooting")
    print("-" * 18)
    print("If APIs still fail:")
    print("  - Double-check API key formats")
    print("  - Verify token permissions")
    print("  - Check GitHub Actions logs for detailed error messages")
    print("  - The system will use fallback content if APIs fail")


if __name__ == "__main__":
    print_instructions()
