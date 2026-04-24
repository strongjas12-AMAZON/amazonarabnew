#!/usr/bin/env python3
"""
Focused Testing for Specific Bug Fixes
Testing the exact endpoints mentioned in the review request
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

class FocusedAPITester:
    def __init__(self):
        self.admin_token = None
        self.seller_token = None
        self.buyer_token = None
        self.test_results = []
        self.created_order_id = None
        
    def log_result(self, test_name, success, details="", error=""):
        """Log test result"""
        status = "✅" if success else "❌"
        self.test_results.append({
            "test": test_name,
            "success": success,
            "status": status,
            "details": details,
            "error": error
        })
        print(f"{status} {test_name}: {details}")
        if error:
            print(f"   Error: {error}")
    
    def authenticate_all_users(self):
        """Authenticate all test users"""
        print("\n=== AUTHENTICATION ===")
        
        # Admin login
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=ADMIN_CREDS)
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("session", {}).get("access_token")
                self.log_result("Admin Login", True, "Admin authenticated")
            else:
                self.log_result("Admin Login", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Admin Login", False, "", str(e))
        
        time.sleep(2)
        
        # Seller login
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=SELLER_CREDS)
            if response.status_code == 200:
                data = response.json()
                self.seller_token = data.get("session", {}).get("access_token")
                self.log_result("Seller Login", True, "Seller authenticated")
            else:
                self.log_result("Seller Login", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Seller Login", False, "", str(e))
        
        time.sleep(2)
        
        # Buyer login
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=BUYER_CREDS)
            if response.status_code == 200:
                data = response.json()
                self.buyer_token = data.get("session", {}).get("access_token")
                self.log_result("Buyer Login", True, "Buyer authenticated")
            else:
                self.log_result("Buyer Login", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Buyer Login", False, "", str(e))
    
    def get_headers(self, token):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    def test_specific_fixed_endpoints(self):
        """Test the specific endpoints that were fixed for table relationship issues"""
        print("\n=== TESTING SPECIFIC FIXED ENDPOINTS ===")
        
        # 1. GET /api/buyer/refunds - should return 200 with {success: true, refunds: []}
        if self.buyer_token:
            try:
                response = requests.get(f"{BASE_URL}/buyer/refunds", headers=self.get_headers(self.buyer_token))
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and "refunds" in data:
                        self.log_result("GET /api/buyer/refunds", True, f"SUCCESS: Returns {len(data['refunds'])} refunds (NOT 500 error)")
                    else:
                        self.log_result("GET /api/buyer/refunds", False, "Invalid response format", str(data))
                else:
                    self.log_result("GET /api/buyer/refunds", False, f"FAILED: Status {response.status_code} (should be 200)", response.text[:200])
            except Exception as e:
                self.log_result("GET /api/buyer/refunds", False, "", str(e))
        
        # 2. GET /api/seller/catalog/products - should return 200+ products (using supabase_admin)
        if self.seller_token:
            try:
                response = requests.get(f"{BASE_URL}/seller/catalog/products", headers=self.get_headers(self.seller_token))
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict) and "products" in data:
                        products = data["products"]
                        if len(products) >= 200:
                            self.log_result("GET /api/seller/catalog/products", True, f"SUCCESS: Returns {len(products)} products (230+ expected)")
                        else:
                            self.log_result("GET /api/seller/catalog/products", False, f"Only {len(products)} products (expected 230+)")
                    else:
                        self.log_result("GET /api/seller/catalog/products", False, "Invalid response format", str(data)[:200])
                else:
                    self.log_result("GET /api/seller/catalog/products", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("GET /api/seller/catalog/products", False, "", str(e))
        
        # 3. POST /api/auth/refresh - test token refresh endpoint exists
        if self.buyer_token:
            try:
                # Test with proper refresh token format
                response = requests.post(f"{BASE_URL}/auth/refresh", 
                                       headers=self.get_headers(self.buyer_token),
                                       json={"refresh_token": "test_refresh_token"})
                if response.status_code in [200, 401, 422]:  # Any of these are acceptable
                    if response.status_code == 200:
                        self.log_result("POST /api/auth/refresh", True, "Token refresh endpoint working")
                    else:
                        self.log_result("POST /api/auth/refresh", True, f"Endpoint exists, returns {response.status_code} for invalid token (expected)")
                else:
                    self.log_result("POST /api/auth/refresh", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("POST /api/auth/refresh", False, "", str(e))
    
    def test_order_creation_and_seller_endpoints(self):
        """Test order creation and seller order endpoints"""
        print("\n=== TESTING ORDER CREATION & SELLER ENDPOINTS ===")
        
        # First, create a proper shipping address
        address_id = None
        if self.buyer_token:
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
                                       headers=self.get_headers(self.buyer_token),
                                       json=address_data)
                if response.status_code == 201:
                    address_id = response.json().get("id")
                    self.log_result("Create Shipping Address", True, f"Address created: {address_id}")
                else:
                    self.log_result("Create Shipping Address", False, f"Status: {response.status_code}", response.text[:200])
            except Exception as e:
                self.log_result("Create Shipping Address", False, "", str(e))
        
        # Get seller's store products
        seller_product_id = None
        if self.seller_token:
            try:
                response = requests.get(f"{BASE_URL}/seller/store/products", headers=self.get_headers(self.seller_token))
                if response.status_code == 200:
                    products = response.json()
                    if products and len(products) > 0:
                        seller_product_id = products[0]["id"]
                        self.log_result("Get Seller Store Products", True, f"Found {len(products)} products")
                    else:
                        self.log_result("Get Seller Store Products", False, "No products in seller store")
                else:
                    self.log_result("Get Seller Store Products", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Get Seller Store Products", False, "", str(e))
        
        # Create order if we have both address and product
        if address_id and seller_product_id and self.buyer_token:
            try:
                order_data = {
                    "items": [{"product_id": seller_product_id, "quantity": 1, "price": 25.99}],
                    "totalAmount": 25.99,
                    "shippingAddressId": address_id,
                    "useWallet": False
                }
                response = requests.post(f"{BASE_URL}/orders", 
                                       headers=self.get_headers(self.buyer_token),
                                       json=order_data)
                if response.status_code == 201:
                    self.created_order_id = response.json().get("id")
                    self.log_result("POST /api/orders", True, f"Order created: {self.created_order_id}")
                else:
                    self.log_result("POST /api/orders", False, f"Status: {response.status_code}", response.text[:200])
            except Exception as e:
                self.log_result("POST /api/orders", False, "", str(e))
        
        # Test seller order center endpoint
        if self.created_order_id and self.seller_token:
            try:
                response = requests.get(f"{BASE_URL}/seller/order-center/{self.created_order_id}", 
                                      headers=self.get_headers(self.seller_token))
                if response.status_code == 200:
                    self.log_result("GET /api/seller/order-center/{id}", True, "Order details retrieved successfully")
                else:
                    self.log_result("GET /api/seller/order-center/{id}", False, f"Status: {response.status_code}", response.text[:200])
            except Exception as e:
                self.log_result("GET /api/seller/order-center/{id}", False, "", str(e))
            
            # Test order status update
            try:
                response = requests.put(f"{BASE_URL}/seller/orders/{self.created_order_id}/status", 
                                      headers=self.get_headers(self.seller_token),
                                      json={"status": "to_be_shipped"})
                if response.status_code == 200:
                    self.log_result("PUT /api/seller/orders/{id}/status", True, "Order status updated successfully")
                else:
                    self.log_result("PUT /api/seller/orders/{id}/status", False, f"Status: {response.status_code}", response.text[:200])
            except Exception as e:
                self.log_result("PUT /api/seller/orders/{id}/status", False, "", str(e))
    
    def test_refund_creation(self):
        """Test refund creation endpoint"""
        print("\n=== TESTING REFUND CREATION ===")
        
        if self.created_order_id and self.buyer_token:
            try:
                refund_data = {
                    "orderId": self.created_order_id,
                    "reason": "Test refund request",
                    "amount": 25.99
                }
                response = requests.post(f"{BASE_URL}/buyer/refunds", 
                                       headers=self.get_headers(self.buyer_token),
                                       json=refund_data)
                if response.status_code == 201:
                    self.log_result("POST /api/buyer/refunds", True, "Refund created successfully (no 500 error)")
                else:
                    self.log_result("POST /api/buyer/refunds", False, f"Status: {response.status_code}", response.text[:200])
            except Exception as e:
                self.log_result("POST /api/buyer/refunds", False, "", str(e))
        else:
            self.log_result("POST /api/buyer/refunds", False, "No order ID available for refund test")
    
    def test_additional_endpoints(self):
        """Test additional endpoints mentioned in review"""
        print("\n=== TESTING ADDITIONAL ENDPOINTS ===")
        
        # Test order status endpoint
        if self.created_order_id and self.buyer_token:
            try:
                response = requests.get(f"{BASE_URL}/orders/{self.created_order_id}/status", 
                                      headers=self.get_headers(self.buyer_token))
                if response.status_code == 200:
                    self.log_result("GET /api/orders/{id}/status", True, "Order status retrieved")
                else:
                    self.log_result("GET /api/orders/{id}/status", False, f"Status: {response.status_code}", response.text[:200])
            except Exception as e:
                self.log_result("GET /api/orders/{id}/status", False, "", str(e))
        
        # Test confirm delivery endpoint
        if self.created_order_id and self.buyer_token:
            try:
                response = requests.post(f"{BASE_URL}/orders/{self.created_order_id}/confirm-delivery", 
                                       headers=self.get_headers(self.buyer_token),
                                       json={})
                if response.status_code in [200, 400]:  # 400 might be expected if order not shipped yet
                    self.log_result("POST /api/orders/{id}/confirm-delivery", True, f"Endpoint exists (status: {response.status_code})")
                else:
                    self.log_result("POST /api/orders/{id}/confirm-delivery", False, f"Status: {response.status_code}", response.text[:200])
            except Exception as e:
                self.log_result("POST /api/orders/{id}/confirm-delivery", False, "", str(e))
        
        # Test ship by platform endpoint
        if self.created_order_id and self.admin_token:
            try:
                response = requests.post(f"{BASE_URL}/orders/{self.created_order_id}/ship-by-platform", 
                                       headers=self.get_headers(self.admin_token),
                                       json={"trackingNumber": "TEST123", "courierName": "Test Courier"})
                if response.status_code in [200, 400]:  # 400 might be expected for various reasons
                    self.log_result("POST /api/orders/{id}/ship-by-platform", True, f"Endpoint exists (status: {response.status_code})")
                else:
                    self.log_result("POST /api/orders/{id}/ship-by-platform", False, f"Status: {response.status_code}", response.text[:200])
            except Exception as e:
                self.log_result("POST /api/orders/{id}/ship-by-platform", False, "", str(e))
        
        # Test store endpoints
        if self.buyer_token:
            try:
                response = requests.get(f"{BASE_URL}/stores/search", headers=self.get_headers(self.buyer_token))
                if response.status_code == 200:
                    stores = response.json()
                    if len(stores) > 0:
                        store_id = stores[0]["id"]
                        self.log_result("GET /api/stores/search", True, f"Found {len(stores)} stores")
                        
                        # Test store detail
                        response = requests.get(f"{BASE_URL}/stores/{store_id}", headers=self.get_headers(self.buyer_token))
                        if response.status_code == 200:
                            self.log_result("GET /api/stores/{id}", True, "Store details retrieved")
                        else:
                            self.log_result("GET /api/stores/{id}", False, f"Status: {response.status_code}")
                        
                        # Test store products
                        response = requests.get(f"{BASE_URL}/stores/{store_id}/products", headers=self.get_headers(self.buyer_token))
                        if response.status_code == 200:
                            products = response.json()
                            self.log_result("GET /api/stores/{id}/products", True, f"Found {len(products)} store products")
                        else:
                            self.log_result("GET /api/stores/{id}/products", False, f"Status: {response.status_code}")
                    else:
                        self.log_result("GET /api/stores/search", False, "No stores found")
                else:
                    self.log_result("GET /api/stores/search", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("GET /api/stores/search", False, "", str(e))
    
    def run_all_tests(self):
        """Run all focused tests"""
        print("🎯 Starting Focused Backend API Testing for Bug Fixes")
        print("=" * 60)
        
        # Authenticate all users first
        self.authenticate_all_users()
        
        # Test specific fixed endpoints
        self.test_specific_fixed_endpoints()
        
        # Test order creation and seller endpoints
        self.test_order_creation_and_seller_endpoints()
        
        # Test refund creation
        self.test_refund_creation()
        
        # Test additional endpoints
        self.test_additional_endpoints()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 FOCUSED TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Categorize results
        critical_failures = []
        working_endpoints = []
        
        for result in self.test_results:
            if not result["success"]:
                if any(endpoint in result["test"] for endpoint in ["GET /api/buyer/refunds", "GET /api/seller/catalog/products", "POST /api/buyer/refunds", "GET /api/seller/order-center", "PUT /api/seller/orders"]):
                    critical_failures.append(result)
            else:
                working_endpoints.append(result)
        
        if critical_failures:
            print("\n🔥 CRITICAL FAILURES (Specific Fix Targets):")
            for result in critical_failures:
                print(f"❌ {result['test']}: {result['error'][:100]}")
        
        print("\n✅ WORKING ENDPOINTS:")
        for result in working_endpoints:
            print(f"✅ {result['test']}: {result['details']}")

if __name__ == "__main__":
    tester = FocusedAPITester()
    tester.run_all_tests()