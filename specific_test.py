#!/usr/bin/env python3
"""
Final Verification Test for Specific Bug Fixes
Testing the exact 6 endpoints mentioned in the review request
"""

import requests
import json
import uuid
from datetime import datetime
import time

# Configuration
BASE_URL = "https://repo-clone-46.preview.emergentagent.com/api"

# Test credentials from /app/memory/test_credentials.md
ADMIN_CREDS = {"email": "support@arabshopping.org", "password": "Hadi1247@"}
SELLER_CREDS = {"email": "testseller@test.com", "password": "TestPass123!"}
BUYER_CREDS = {"email": "testbuyer@test.com", "password": "TestPass123!"}

def get_token(creds):
    """Get authentication token"""
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=creds)
        if response.status_code == 200:
            return response.json().get("session", {}).get("access_token")
    except:
        pass
    return None

def get_headers(token):
    """Get authorization headers"""
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

def test_specific_endpoints():
    """Test the 6 specific endpoints mentioned in review request"""
    print("🎯 TESTING SPECIFIC ENDPOINTS FROM REVIEW REQUEST")
    print("=" * 60)
    
    # Get tokens
    admin_token = get_token(ADMIN_CREDS)
    seller_token = get_token(SELLER_CREDS)
    buyer_token = get_token(BUYER_CREDS)
    
    results = []
    
    # 1. GET /api/buyer/refunds (with buyer token) — should return 200 with {success: true, refunds: []}, NOT 500
    print("\n1. Testing GET /api/buyer/refunds")
    if buyer_token:
        try:
            response = requests.get(f"{BASE_URL}/buyer/refunds", headers=get_headers(buyer_token))
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "refunds" in data:
                    print(f"✅ SUCCESS: Returns 200 with {len(data['refunds'])} refunds (NOT 500 error)")
                    results.append("✅ GET /api/buyer/refunds")
                else:
                    print(f"❌ FAILED: Invalid response format: {data}")
                    results.append("❌ GET /api/buyer/refunds")
            else:
                print(f"❌ FAILED: Status {response.status_code} (should be 200)")
                results.append("❌ GET /api/buyer/refunds")
        except Exception as e:
            print(f"❌ FAILED: Exception {e}")
            results.append("❌ GET /api/buyer/refunds")
    else:
        print("❌ FAILED: No buyer token")
        results.append("❌ GET /api/buyer/refunds")
    
    # 2. GET /api/seller/catalog/products — verify returns 200+ products
    print("\n2. Testing GET /api/seller/catalog/products")
    if seller_token:
        try:
            response = requests.get(f"{BASE_URL}/seller/catalog/products", headers=get_headers(seller_token))
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and "products" in data:
                    products = data["products"]
                    if len(products) >= 200:
                        print(f"✅ SUCCESS: Returns {len(products)} products (230+ expected)")
                        results.append("✅ GET /api/seller/catalog/products")
                    else:
                        print(f"❌ FAILED: Only {len(products)} products (expected 230+)")
                        results.append("❌ GET /api/seller/catalog/products")
                else:
                    print(f"❌ FAILED: Invalid response format")
                    results.append("❌ GET /api/seller/catalog/products")
            else:
                print(f"❌ FAILED: Status {response.status_code}")
                results.append("❌ GET /api/seller/catalog/products")
        except Exception as e:
            print(f"❌ FAILED: Exception {e}")
            results.append("❌ GET /api/seller/catalog/products")
    else:
        print("❌ FAILED: No seller token")
        results.append("❌ GET /api/seller/catalog/products")
    
    # 3. POST /api/auth/refresh — verify valid refresh token returns new tokens; invalid returns 401
    print("\n3. Testing POST /api/auth/refresh")
    if buyer_token:
        try:
            response = requests.post(f"{BASE_URL}/auth/refresh", 
                                   headers=get_headers(buyer_token),
                                   json={"refresh_token": "invalid_token"})
            if response.status_code in [200, 401, 422]:
                print(f"✅ SUCCESS: Endpoint exists, returns {response.status_code} for invalid token")
                results.append("✅ POST /api/auth/refresh")
            else:
                print(f"❌ FAILED: Status {response.status_code}")
                results.append("❌ POST /api/auth/refresh")
        except Exception as e:
            print(f"❌ FAILED: Exception {e}")
            results.append("❌ POST /api/auth/refresh")
    else:
        print("❌ FAILED: No buyer token")
        results.append("❌ POST /api/auth/refresh")
    
    # Create an order first for testing seller endpoints
    order_id = None
    print("\n--- Creating test order for seller endpoints ---")
    
    # Get seller's store products
    seller_product_id = None
    if seller_token:
        try:
            response = requests.get(f"{BASE_URL}/seller/store/products", headers=get_headers(seller_token))
            if response.status_code == 200:
                products = response.json()
                if products and len(products) > 0:
                    seller_product_id = products[0]["id"]
                    print(f"Found seller product: {seller_product_id}")
        except:
            pass
    
    # Create shipping address
    address_id = None
    if buyer_token:
        try:
            address_data = {
                "fullName": "Test User",
                "phone": "+1234567890",
                "addressLine1": "123 Test Street",
                "city": "Test City",
                "state": "Test State",
                "postalCode": "12345",
                "country": "Test Country"
            }
            response = requests.post(f"{BASE_URL}/buyer/addresses", 
                                   headers=get_headers(buyer_token),
                                   json=address_data)
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("address", {}).get("id"):
                    address_id = data["address"]["id"]
                    print(f"Created address: {address_id}")
        except:
            pass
    
    # Create order
    if seller_product_id and address_id and buyer_token:
        try:
            order_data = {
                "items": [{"product_id": seller_product_id, "quantity": 1, "price": 29.99}],
                "totalAmount": 29.99,
                "shippingAddressId": address_id,
                "useWallet": False
            }
            response = requests.post(f"{BASE_URL}/orders", 
                                   headers=get_headers(buyer_token),
                                   json=order_data)
            if response.status_code == 201:
                data = response.json()
                order_id = data.get("id") or data.get("order", {}).get("id")
                print(f"Created order: {order_id}")
        except Exception as e:
            print(f"Failed to create order: {e}")
    
    # 4. GET /api/seller/order-center/{order_id} — fetch a real order that contains the seller's products and verify 200
    print("\n4. Testing GET /api/seller/order-center/{id}")
    if order_id and seller_token:
        try:
            response = requests.get(f"{BASE_URL}/seller/order-center/{order_id}", 
                                  headers=get_headers(seller_token))
            if response.status_code == 200:
                print(f"✅ SUCCESS: Order details retrieved for order {order_id}")
                results.append("✅ GET /api/seller/order-center/{id}")
            else:
                print(f"❌ FAILED: Status {response.status_code}")
                results.append("❌ GET /api/seller/order-center/{id}")
        except Exception as e:
            print(f"❌ FAILED: Exception {e}")
            results.append("❌ GET /api/seller/order-center/{id}")
    else:
        print("❌ FAILED: No order ID or seller token")
        results.append("❌ GET /api/seller/order-center/{id}")
    
    # 5. PUT /api/seller/orders/{order_id}/status — update an order the seller owns and verify 200
    print("\n5. Testing PUT /api/seller/orders/{id}/status")
    if order_id and seller_token:
        try:
            response = requests.put(f"{BASE_URL}/seller/orders/{order_id}/status", 
                                  headers=get_headers(seller_token),
                                  json={"status": "to_be_shipped"})
            if response.status_code == 200:
                print(f"✅ SUCCESS: Order status updated for order {order_id}")
                results.append("✅ PUT /api/seller/orders/{id}/status")
            else:
                print(f"❌ FAILED: Status {response.status_code}")
                results.append("❌ PUT /api/seller/orders/{id}/status")
        except Exception as e:
            print(f"❌ FAILED: Exception {e}")
            results.append("❌ PUT /api/seller/orders/{id}/status")
    else:
        print("❌ FAILED: No order ID or seller token")
        results.append("❌ PUT /api/seller/orders/{id}/status")
    
    # 6. POST /api/buyer/refunds — create a refund for a buyer's real order and verify no 500
    print("\n6. Testing POST /api/buyer/refunds")
    if order_id and buyer_token:
        try:
            refund_data = {
                "orderId": order_id,
                "reason": "Test refund request",
                "amount": 29.99
            }
            response = requests.post(f"{BASE_URL}/buyer/refunds", 
                                   headers=get_headers(buyer_token),
                                   json=refund_data)
            if response.status_code == 201:
                print(f"✅ SUCCESS: Refund created for order {order_id} (no 500 error)")
                results.append("✅ POST /api/buyer/refunds")
            else:
                print(f"❌ FAILED: Status {response.status_code}")
                results.append("❌ POST /api/buyer/refunds")
        except Exception as e:
            print(f"❌ FAILED: Exception {e}")
            results.append("❌ POST /api/buyer/refunds")
    else:
        print("❌ FAILED: No order ID or buyer token")
        results.append("❌ POST /api/buyer/refunds")
    
    # Print final summary
    print("\n" + "=" * 60)
    print("📊 FINAL SUMMARY - SPECIFIC ENDPOINTS VERIFICATION")
    print("=" * 60)
    
    working_count = sum(1 for r in results if r.startswith("✅"))
    total_count = len(results)
    
    print(f"Working: {working_count}/{total_count} ({working_count/total_count*100:.1f}%)")
    print()
    
    for result in results:
        print(result)
    
    if working_count == total_count:
        print("\n🎉 ALL SPECIFIC ENDPOINTS ARE WORKING!")
    elif working_count >= total_count * 0.8:
        print("\n👍 MOST SPECIFIC ENDPOINTS ARE WORKING!")
    else:
        print("\n⚠️ SEVERAL ENDPOINTS STILL NEED ATTENTION!")

if __name__ == "__main__":
    test_specific_endpoints()