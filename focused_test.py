#!/usr/bin/env python3
"""
Focused test for public forgot password functionality
"""

import requests
import json
import uuid
import time

BASE_URL = "https://repo-clone-47.preview.emergentagent.com/api"

def test_public_forgot_password():
    print("Testing public forgot password functionality...")
    
    # Wait a bit to avoid rate limit
    print("Waiting 10 seconds to avoid rate limit...")
    time.sleep(10)
    
    # Test with existing email
    print("\n1. Testing with existing email...")
    payload = {
        "email": "testbuyer@test.com",
        "redirect_url": "https://example.com"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/forgot-password", json=payload, timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and 'If an account exists' in data.get('message', ''):
                print("✅ PASS: Existing email test")
            else:
                print("❌ FAIL: Unexpected response format")
        else:
            print(f"❌ FAIL: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ FAIL: Exception {e}")
    
    # Wait before next test
    time.sleep(2)
    
    # Test with non-existent email
    print("\n2. Testing with non-existent email...")
    fake_email = f"nobody-xyz-{uuid.uuid4()}@example.com"
    payload = {
        "email": fake_email,
        "redirect_url": "https://example.com"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/forgot-password", json=payload, timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and 'If an account exists' in data.get('message', ''):
                print("✅ PASS: Non-existent email test (anti-enumeration working)")
            else:
                print("❌ FAIL: Unexpected response format")
        else:
            print(f"❌ FAIL: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ FAIL: Exception {e}")

if __name__ == "__main__":
    test_public_forgot_password()
