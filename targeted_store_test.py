#!/usr/bin/env python3
"""
Targeted test to verify buyer can see seller's specific store products
"""

import requests
import json

BASE_URL = "https://clone-master-88.preview.emergentagent.com/api"
SELLER_EMAIL = "testseller_new@test.com"
SELLER_PASSWORD = "TestPass123!"
BUYER_EMAIL = "testbuyer@test.com"
BUYER_PASSWORD = "TestPass123!"

def login_user(email, password):
    """Login and return token"""
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": email,
        "password": password
    })
    if response.status_code == 200:
        data = response.json()
        return data["session"]["access_token"]
    return None

def main():
    print("=== TARGETED STORE TEST ===")
    
    # Login as seller
    seller_token = login_user(SELLER_EMAIL, SELLER_PASSWORD)
    if not seller_token:
        print("❌ Seller login failed")
        return
    print("✅ Seller logged in")
    
    # Get seller's store products to find their store ID
    headers = {"Authorization": f"Bearer {seller_token}"}
    response = requests.get(f"{BASE_URL}/seller/store/products", headers=headers)
    
    if response.status_code != 200:
        print("❌ Failed to get seller store products")
        return
    
    data = response.json()
    products = data.get("products", [])
    
    if not products:
        print("❌ Seller has no products in store")
        return
    
    # Extract store ID from first product (try both camelCase and snake_case)
    store_id = products[0].get("storeId") or products[0].get("store_id")
    if not store_id:
        print("❌ No store_id/storeId found in seller products")
        print(f"Product keys: {list(products[0].keys())}")
        return
    
    print(f"✅ Found seller's store ID: {store_id}")
    print(f"✅ Seller has {len(products)} products in their store")
    
    # Login as buyer
    buyer_token = login_user(BUYER_EMAIL, BUYER_PASSWORD)
    if not buyer_token:
        print("❌ Buyer login failed")
        return
    print("✅ Buyer logged in")
    
    # Check if buyer can see seller's store products
    buyer_headers = {"Authorization": f"Bearer {buyer_token}"}
    response = requests.get(f"{BASE_URL}/stores/{store_id}/products", headers=buyer_headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to get store products: {response.status_code}")
        return
    
    data = response.json()
    buyer_visible_products = data.get("products", [])
    
    print(f"✅ Buyer can see {len(buyer_visible_products)} products in seller's store")
    
    if len(buyer_visible_products) == len(products):
        print("✅ SUCCESS: Buyer can see all products that seller added to their store")
    else:
        print(f"⚠️  MISMATCH: Seller has {len(products)} products, buyer sees {len(buyer_visible_products)}")
    
    # Test store search to see if seller's store appears
    response = requests.get(f"{BASE_URL}/stores/search", headers=buyer_headers)
    if response.status_code == 200:
        data = response.json()
        stores = data.get("stores", [])
        seller_store_found = any(store.get("id") == store_id for store in stores)
        
        if seller_store_found:
            print("✅ Seller's store appears in store search results")
        else:
            print("⚠️  Seller's store not found in search results")
        
        print(f"✅ Total stores found: {len(stores)}")

if __name__ == "__main__":
    main()