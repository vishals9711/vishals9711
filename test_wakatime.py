#!/usr/bin/env python3
"""
Simple Wakatime API test script.
"""

import requests
import sys

def test_wakatime_api(api_key):
    """Test Wakatime API with the provided key."""
    print(f"Testing Wakatime API with key: {api_key[:8]}...")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    try:
        # Test basic connection
        response = requests.get(
            "https://wakatime.com/api/v1/users/current",
            headers=headers,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("✅ Wakatime API key is valid!")
            return True
        elif response.status_code == 401:
            print("❌ Wakatime API key is invalid or expired")
            return False
        else:
            print(f"⚠️ Unexpected status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Wakatime API: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    else:
        api_key = input("Enter your Wakatime API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided")
        sys.exit(1)
    
    success = test_wakatime_api(api_key)
    sys.exit(0 if success else 1)
