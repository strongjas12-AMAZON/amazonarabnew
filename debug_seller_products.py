#!/usr/bin/env python3
"""
Debug seller store products response
"""

import requests
import json

BASE_URL = "https://repo-twin-1.preview.emergentagent.com/api"
SELLER_EMAIL = "testseller_new@test.com"
SELLER_PASSWORD = "TestPass123!"

def main():
    # Login as seller
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": SELLER_EMAIL,
        "password": SELLER_PASSWORD
    })
    
    if response.status_code != 200:
        print("❌ Seller login failed")
        return
    
    data = response.json()
    seller_token = data["session"]["access_token"]
    
    # Get seller's store products
    headers = {"Authorization": f"Bearer {seller_token}"}
    response = requests.get(f"{BASE_URL}/seller/store/products", headers=headers)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    main()