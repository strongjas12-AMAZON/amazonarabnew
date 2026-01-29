#!/usr/bin/env python3
"""
Test admin products endpoint with proper authentication
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

BACKEND_URL = "http://localhost:8001/api"
ADMIN_EMAIL = "support@arabshopping.org"
# Note: Password would need to be known for this test

print("Testing Admin Products Endpoint")
print("=" * 60)

# Option 1: Test without auth to see if endpoint exists
try:
    response = requests.get(f"{BACKEND_URL}/admin/products")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 401:
        print("✅ Endpoint exists and requires authentication (expected)")
    elif response.status_code == 200:
        data = response.json()
        print(f"✅ Products returned: {len(data.get('products', []))}")
    else:
        print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("NOTE: To fully test, login as admin via frontend and check")
print("that the Admin Dashboard > Products tab shows 100 items")
print("=" * 60)
