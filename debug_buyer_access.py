#!/usr/bin/env python3
"""
Debug buyer store access
"""

import requests
import json

BASE_URL = "https://repo-copy-4.preview.emergentagent.com/api"
SELLER_EMAIL = "testseller_new@test.com"
SELLER_PASSWORD = "TestPass123!"
BUYER_EMAIL = "testbuyer@test.com"
BUYER_PASSWORD = "TestPass123!"

def main():
    # Login as seller and get store ID
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": SELLER_EMAIL,
        "password": SELLER_PASSWORD
    })
    seller_token = response.json()["session"]["access_token"]
    
    headers = {"Authorization": f"Bearer {seller_token}"}
    response = requests.get(f"{BASE_URL}/seller/store/products", headers=headers)
    products = response.json()["products"]
    store_id = products[0]["storeId"]
    
    print(f"Store ID: {store_id}")
    
    # Login as buyer
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": BUYER_EMAIL,
        "password": BUYER_PASSWORD
    })
    buyer_token = response.json()["session"]["access_token"]
    
    # Try to access store products
    buyer_headers = {"Authorization": f"Bearer {buyer_token}"}
    response = requests.get(f"{BASE_URL}/stores/{store_id}/products", headers=buyer_headers)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    main()