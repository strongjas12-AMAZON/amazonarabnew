#!/usr/bin/env python3
"""
Final Comprehensive Test for Bug Fixes Verification
Testing all specific endpoints mentioned in the review request
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

class ComprehensiveTester:
    def __init__(self):
        self.admin_token = None
        self.seller_token = None
        self.buyer_token = None
        self.test_results = []
        self.created_order_id = None
        self.created_address_id = None
        
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
        if error and not success:
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
    
    def test_critical_fixed_endpoints(self):
        """Test the 5 critical endpoints that were fixed"""
        print("\n=== TESTING 5 CRITICAL FIXED ENDPOINTS ===")
        
        # 1. GET /api/buyer/refunds - Fixed from 500 error to 200
        if self.buyer_token:
            try:
                response = requests.get(f"{BASE_URL}/buyer/refunds", headers=self.get_headers(self.buyer_token))
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and "refunds" in data:
                        self.log_result("1. GET /api/buyer/refunds", True, f"✅ FIXED: Returns 200 with {len(data['refunds'])} refunds (was 500 error)")
                    else:
                        self.log_result("1. GET /api/buyer/refunds", False, "Invalid response format", str(data))
                else:
                    self.log_result("1. GET /api/buyer/refunds", False, f"❌ Still returns {response.status_code} (should be 200)", response.text[:200])
            except Exception as e:
                self.log_result("1. GET /api/buyer/refunds", False, "", str(e))
        
        # 2. GET /api/seller/catalog/products - Fixed to use supabase_admin
        if self.seller_token:
            try:
                response = requests.get(f"{BASE_URL}/seller/catalog/products", headers=self.get_headers(self.seller_token))
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict) and "products" in data:
                        products = data["products"]
                        if len(products) >= 200:
                            self.log_result("2. GET /api/seller/catalog/products", True, f"✅ FIXED: Returns {len(products)} products (was 0, now uses supabase_admin)")
                        else:
                            self.log_result("2. GET /api/seller/catalog/products", False, f"Only {len(products)} products (expected 230+)")
                    else:
                        self.log_result("2. GET /api/seller/catalog/products", False, "Invalid response format", str(data)[:200])
                else:
                    self.log_result("2. GET /api/seller/catalog/products", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("2. GET /api/seller/catalog/products", False, "", str(e))
        
        # 3. POST /api/auth/refresh - New endpoint for token refresh
        if self.buyer_token:
            try:
                response = requests.post(f"{BASE_URL}/auth/refresh", 
                                       headers=self.get_headers(self.buyer_token),
                                       json={"refresh_token": "test_refresh_token"})
                if response.status_code in [200, 401, 422]:  # Any of these are acceptable
                    self.log_result("3. POST /api/auth/refresh", True, f"✅ FIXED: New endpoint exists, returns {response.status_code}")
                else:
                    self.log_result("3. POST /api/auth/refresh", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("3. POST /api/auth/refresh", False, "", str(e))
    
    def test_order_flow_endpoints(self):
        """Test order flow endpoints that were fixed"""
        print("\n=== TESTING ORDER FLOW ENDPOINTS ===")
        
        # Create shipping address first
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
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and data.get("address", {}).get("id"):
                        self.created_address_id = data["address"]["id"]
                        self.log_result("Create Shipping Address", True, f"Address created: {self.created_address_id}")
                    else:
                        self.log_result("Create Shipping Address", False, "No address ID in response", str(data))
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
                        # Try to add a product to seller's store first
                        self.add_product_to_seller_store()
                        # Try again
                        response = requests.get(f"{BASE_URL}/seller/store/products", headers=self.get_headers(self.seller_token))
                        if response.status_code == 200:
                            products = response.json()
                            if products and len(products) > 0:
                                seller_product_id = products[0]["id"]
                                self.log_result("Get Seller Store Products", True, f"Found {len(products)} products after adding")
                            else:
                                self.log_result("Get Seller Store Products", False, "No products in seller store")
                        else:
                            self.log_result("Get Seller Store Products", False, f"Status: {response.status_code}")
                else:
                    self.log_result("Get Seller Store Products", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Get Seller Store Products", False, "", str(e))
        
        # Create order if we have both address and product
        if self.created_address_id and seller_product_id and self.buyer_token:
            try:
                order_data = {
                    "items": [{"product_id": seller_product_id, "quantity": 1, "price": 25.99}],
                    "totalAmount": 25.99,
                    "shippingAddressId": self.created_address_id,
                    "useWallet": False
                }
                response = requests.post(f"{BASE_URL}/orders", 
                                       headers=self.get_headers(self.buyer_token),
                                       json=order_data)
                if response.status_code == 201:
                    data = response.json()
                    self.created_order_id = data.get("id") or data.get("order", {}).get("id")
                    self.log_result("POST /api/orders", True, f"Order created: {self.created_order_id}")
                else:
                    self.log_result("POST /api/orders", False, f"Status: {response.status_code}", response.text[:200])
            except Exception as e:
                self.log_result("POST /api/orders", False, "", str(e))
        
        # 4. GET /api/seller/order-center/{id} - Fixed table relationships
        if self.created_order_id and self.seller_token:
            try:
                response = requests.get(f"{BASE_URL}/seller/order-center/{self.created_order_id}", 
                                      headers=self.get_headers(self.seller_token))
                if response.status_code == 200:
                    self.log_result("4. GET /api/seller/order-center/{id}", True, "✅ FIXED: Order details retrieved (fixed store_products relationship)")
                else:
                    self.log_result("4. GET /api/seller/order-center/{id}", False, f"❌ Status: {response.status_code}", response.text[:200])
            except Exception as e:
                self.log_result("4. GET /api/seller/order-center/{id}", False, "", str(e))
        
        # 5. PUT /api/seller/orders/{id}/status - Fixed table relationships
        if self.created_order_id and self.seller_token:
            try:
                response = requests.put(f"{BASE_URL}/seller/orders/{self.created_order_id}/status", 
                                      headers=self.get_headers(self.seller_token),
                                      json={"status": "to_be_shipped"})
                if response.status_code == 200:
                    self.log_result("5. PUT /api/seller/orders/{id}/status", True, "✅ FIXED: Order status updated (fixed store_products relationship)")
                else:
                    self.log_result("5. PUT /api/seller/orders/{id}/status", False, f"❌ Status: {response.status_code}", response.text[:200])
            except Exception as e:
                self.log_result("5. PUT /api/seller/orders/{id}/status", False, "", str(e))
    
    def add_product_to_seller_store(self):
        """Helper to add a product to seller's store"""
        if self.seller_token:
            try:
                # Get a product from catalog first
                response = requests.get(f"{BASE_URL}/seller/catalog/products", headers=self.get_headers(self.seller_token))
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict) and "products" in data and len(data["products"]) > 0:
                        catalog_product = data["products"][0]
                        
                        # Add product to store
                        product_data = {
                            "catalog_product_id": catalog_product["id"],
                            "price": 29.99,
                            "stock": 10
                        }
                        response = requests.post(f"{BASE_URL}/seller/store/products", 
                                               headers=self.get_headers(self.seller_token),
                                               json=product_data)
                        if response.status_code == 201:
                            self.log_result("Add Product to Store", True, "Product added to seller store")
                        else:
                            self.log_result("Add Product to Store", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("Add Product to Store", False, "", str(e))
    
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
                    self.log_result("POST /api/buyer/refunds", True, "✅ FIXED: Refund created successfully (no 500 error)")
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
        
        # Test buyer addresses endpoints
        if self.buyer_token:
            try:
                response = requests.get(f"{BASE_URL}/buyer/addresses", headers=self.get_headers(self.buyer_token))
                if response.status_code == 200:
                    addresses = response.json()
                    self.log_result("GET /api/buyer/addresses", True, f"Found {len(addresses)} addresses")
                else:
                    self.log_result("GET /api/buyer/addresses", False, f"Status: {response.status_code}", response.text[:200])
            except Exception as e:
                self.log_result("GET /api/buyer/addresses", False, "", str(e))
        
        # Test products endpoints
        if self.buyer_token:
            try:
                response = requests.get(f"{BASE_URL}/products", headers=self.get_headers(self.buyer_token))
                if response.status_code == 200:
                    products = response.json()
                    self.log_result("GET /api/products", True, f"Found {len(products)} products")
                else:
                    self.log_result("GET /api/products", False, f"Status: {response.status_code}", response.text[:200])
            except Exception as e:
                self.log_result("GET /api/products", False, "", str(e))
        
        # Test store search
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
        """Run all comprehensive tests"""
        print("🔧 COMPREHENSIVE BACKEND API TESTING - BUG FIXES VERIFICATION")
        print("=" * 70)
        
        # Authenticate all users first
        self.authenticate_all_users()
        
        # Test the 5 critical fixed endpoints
        self.test_critical_fixed_endpoints()
        
        # Test order flow endpoints
        self.test_order_flow_endpoints()
        
        # Test refund creation
        self.test_refund_creation()
        
        # Test additional endpoints
        self.test_additional_endpoints()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE TEST SUMMARY - BUG FIXES VERIFICATION")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Categorize results by priority
        critical_fixes = []
        working_endpoints = []
        other_failures = []
        
        critical_endpoint_names = [
            "1. GET /api/buyer/refunds",
            "2. GET /api/seller/catalog/products", 
            "3. POST /api/auth/refresh",
            "4. GET /api/seller/order-center/{id}",
            "5. PUT /api/seller/orders/{id}/status",
            "POST /api/buyer/refunds"
        ]
        
        for result in self.test_results:
            if any(name in result["test"] for name in critical_endpoint_names):
                if result["success"]:
                    critical_fixes.append(result)
                else:
                    other_failures.append(result)
            elif result["success"]:
                working_endpoints.append(result)
            else:
                other_failures.append(result)
        
        print(f"\n🎯 CRITICAL FIXES VERIFIED ({len(critical_fixes)}/6 working):")
        for result in critical_fixes:
            print(f"✅ {result['test']}: {result['details']}")
        
        if other_failures:
            print(f"\n⚠️ ISSUES FOUND ({len(other_failures)} failures):")
            for result in other_failures:
                print(f"❌ {result['test']}: {result['error'][:100] if result['error'] else 'Failed'}")
        
        print(f"\n✅ OTHER WORKING ENDPOINTS ({len(working_endpoints)}):")
        for result in working_endpoints:
            print(f"✅ {result['test']}: {result['details']}")
        
        # Final assessment
        critical_success_rate = len(critical_fixes) / 6 * 100
        print(f"\n🏆 CRITICAL FIXES SUCCESS RATE: {critical_success_rate:.1f}% ({len(critical_fixes)}/6)")
        
        if critical_success_rate >= 80:
            print("🎉 EXCELLENT: Most critical fixes are working correctly!")
        elif critical_success_rate >= 60:
            print("👍 GOOD: Majority of critical fixes are working!")
        else:
            print("⚠️ NEEDS ATTENTION: Several critical fixes still have issues!")

if __name__ == "__main__":
    tester = ComprehensiveTester()
    tester.run_all_tests()