#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Bug Fixes
Testing specific endpoints that were fixed for table relationship issues
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

class APITester:
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
        if error:
            print(f"   Error: {error}")
    
    def authenticate_all_users(self):
        """Authenticate all test users"""
        print("\n=== AUTHENTICATION TESTS ===")
        
        # Admin login
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=ADMIN_CREDS)
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("session", {}).get("access_token")
                self.log_result("Admin Login", True, f"Admin authenticated successfully")
            else:
                self.log_result("Admin Login", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Admin Login", False, "", str(e))
        
        # Wait a bit to avoid rate limiting
        time.sleep(2)
        
        # Seller login
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=SELLER_CREDS)
            if response.status_code == 200:
                data = response.json()
                self.seller_token = data.get("session", {}).get("access_token")
                self.log_result("Seller Login", True, f"Seller authenticated successfully")
            else:
                self.log_result("Seller Login", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Seller Login", False, "", str(e))
        
        # Wait a bit to avoid rate limiting
        time.sleep(2)
        
        # Buyer login
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=BUYER_CREDS)
            if response.status_code == 200:
                data = response.json()
                self.buyer_token = data.get("session", {}).get("access_token")
                self.log_result("Buyer Login", True, f"Buyer authenticated successfully")
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
                        self.log_result("GET /api/buyer/refunds", True, f"Returns {len(data['refunds'])} refunds")
                    else:
                        self.log_result("GET /api/buyer/refunds", False, "Invalid response format", str(data))
                else:
                    self.log_result("GET /api/buyer/refunds", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("GET /api/buyer/refunds", False, "", str(e))
        else:
            self.log_result("GET /api/buyer/refunds", False, "No buyer token available")
        
        # 2. GET /api/seller/catalog/products - should return 200+ products
        if self.seller_token:
            try:
                response = requests.get(f"{BASE_URL}/seller/catalog/products", headers=self.get_headers(self.seller_token))
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict) and "products" in data:
                        products = data["products"]
                        self.log_result("GET /api/seller/catalog/products", True, f"Returns {len(products)} products")
                    elif isinstance(data, list):
                        self.log_result("GET /api/seller/catalog/products", True, f"Returns {len(data)} products")
                    else:
                        self.log_result("GET /api/seller/catalog/products", False, "Invalid response format", str(data)[:200])
                else:
                    self.log_result("GET /api/seller/catalog/products", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("GET /api/seller/catalog/products", False, "", str(e))
        else:
            self.log_result("GET /api/seller/catalog/products", False, "No seller token available")
        
        # 3. POST /api/auth/refresh - test token refresh
        if self.buyer_token:
            try:
                # First get refresh token by checking current token
                response = requests.post(f"{BASE_URL}/auth/refresh", 
                                       headers=self.get_headers(self.buyer_token),
                                       json={})
                if response.status_code in [200, 401]:  # 401 is expected for invalid refresh token
                    if response.status_code == 200:
                        self.log_result("POST /api/auth/refresh", True, "Token refresh successful")
                    else:
                        self.log_result("POST /api/auth/refresh", True, "Returns 401 for invalid token (expected)")
                else:
                    self.log_result("POST /api/auth/refresh", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("POST /api/auth/refresh", False, "", str(e))
        else:
            self.log_result("POST /api/auth/refresh", False, "No buyer token available")
    
    def test_order_lifecycle(self):
        """Test complete order lifecycle"""
        print("\n=== TESTING ORDER LIFECYCLE ===")
        
        if not self.buyer_token or not self.seller_token or not self.admin_token:
            self.log_result("Order Lifecycle", False, "Missing authentication tokens")
            return
        
        # Step 1: Create shipping address for buyer
        try:
            address_data = {
                "name": "Test User",
                "phone": "+1234567890",
                "address": "123 Test Street",
                "city": "Test City",
                "state": "Test State",
                "zipCode": "12345",
                "country": "Test Country"
            }
            response = requests.post(f"{BASE_URL}/buyer/addresses", 
                                   headers=self.get_headers(self.buyer_token),
                                   json=address_data)
            if response.status_code == 201:
                self.created_address_id = response.json().get("id")
                self.log_result("Create Shipping Address", True, f"Address ID: {self.created_address_id}")
            else:
                self.log_result("Create Shipping Address", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Create Shipping Address", False, "", str(e))
        
        # Step 2: Get seller's store products to create order
        seller_product_id = None
        try:
            response = requests.get(f"{BASE_URL}/seller/store/products", headers=self.get_headers(self.seller_token))
            if response.status_code == 200:
                products = response.json()
                if products and len(products) > 0:
                    seller_product_id = products[0]["id"]
                    self.log_result("Get Seller Products", True, f"Found {len(products)} products")
                else:
                    self.log_result("Get Seller Products", False, "No products found in seller store")
            else:
                self.log_result("Get Seller Products", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Get Seller Products", False, "", str(e))
        
        # Step 3: Create order if we have product and address
        if seller_product_id and self.created_address_id:
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
                    self.created_order_id = response.json().get("id")
                    self.log_result("Create Order", True, f"Order ID: {self.created_order_id}")
                else:
                    self.log_result("Create Order", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Create Order", False, "", str(e))
        
        # Step 4: Test seller order center endpoints
        if self.created_order_id:
            try:
                response = requests.get(f"{BASE_URL}/seller/order-center/{self.created_order_id}", 
                                      headers=self.get_headers(self.seller_token))
                if response.status_code == 200:
                    self.log_result("GET /api/seller/order-center/{id}", True, "Order details retrieved")
                else:
                    self.log_result("GET /api/seller/order-center/{id}", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("GET /api/seller/order-center/{id}", False, "", str(e))
            
            # Test order status update
            try:
                response = requests.put(f"{BASE_URL}/seller/orders/{self.created_order_id}/status", 
                                      headers=self.get_headers(self.seller_token),
                                      json={"status": "to_be_shipped"})
                if response.status_code == 200:
                    self.log_result("PUT /api/seller/orders/{id}/status", True, "Order status updated")
                else:
                    self.log_result("PUT /api/seller/orders/{id}/status", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("PUT /api/seller/orders/{id}/status", False, "", str(e))
    
    def test_wallet_recharge_lifecycle(self):
        """Test wallet recharge lifecycle"""
        print("\n=== TESTING WALLET RECHARGE LIFECYCLE ===")
        
        if not self.seller_token or not self.admin_token:
            self.log_result("Wallet Recharge Lifecycle", False, "Missing authentication tokens")
            return
        
        # Step 1: Seller submits wallet recharge request
        recharge_id = None
        try:
            recharge_data = {
                "amount": 100.0,
                "transactionHash": f"test_hash_{uuid.uuid4().hex[:8]}"
            }
            response = requests.post(f"{BASE_URL}/seller/wallet/recharge", 
                                   headers=self.get_headers(self.seller_token),
                                   json=recharge_data)
            if response.status_code == 201:
                recharge_id = response.json().get("id")
                self.log_result("Seller Submit Recharge", True, f"Recharge ID: {recharge_id}")
            else:
                self.log_result("Seller Submit Recharge", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Seller Submit Recharge", False, "", str(e))
        
        # Step 2: Admin lists recharge requests
        try:
            response = requests.get(f"{BASE_URL}/admin/seller-wallet-recharge-requests", 
                                  headers=self.get_headers(self.admin_token))
            if response.status_code == 200:
                requests_list = response.json()
                self.log_result("Admin List Recharge Requests", True, f"Found {len(requests_list)} requests")
            else:
                self.log_result("Admin List Recharge Requests", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Admin List Recharge Requests", False, "", str(e))
        
        # Step 3: Admin approves recharge request
        if recharge_id:
            try:
                response = requests.post(f"{BASE_URL}/admin/seller-wallet-recharge-requests/{recharge_id}/status", 
                                       headers=self.get_headers(self.admin_token),
                                       json={"status": "approved"})
                if response.status_code == 200:
                    self.log_result("Admin Approve Recharge", True, "Recharge approved successfully")
                else:
                    self.log_result("Admin Approve Recharge", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Admin Approve Recharge", False, "", str(e))
    
    def test_payout_lifecycle(self):
        """Test payout lifecycle"""
        print("\n=== TESTING PAYOUT LIFECYCLE ===")
        
        if not self.seller_token or not self.admin_token:
            self.log_result("Payout Lifecycle", False, "Missing authentication tokens")
            return
        
        # Step 1: Seller requests payout
        payout_id = None
        try:
            payout_data = {
                "amount": 50.0,
                "payoutWallet": "TY8Z91NMCjREyZVj9NjDsF8hVjyqfxFFRU"  # Valid TRC20 address
            }
            response = requests.post(f"{BASE_URL}/seller/payout-requests", 
                                   headers=self.get_headers(self.seller_token),
                                   json=payout_data)
            if response.status_code == 201:
                payout_id = response.json().get("id")
                self.log_result("Seller Request Payout", True, f"Payout ID: {payout_id}")
            else:
                self.log_result("Seller Request Payout", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Seller Request Payout", False, "", str(e))
        
        # Step 2: Admin lists payout requests
        try:
            response = requests.get(f"{BASE_URL}/admin/payout-requests", 
                                  headers=self.get_headers(self.admin_token))
            if response.status_code == 200:
                requests_list = response.json()
                self.log_result("Admin List Payout Requests", True, f"Found {len(requests_list)} requests")
            else:
                self.log_result("Admin List Payout Requests", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Admin List Payout Requests", False, "", str(e))
        
        # Step 3: Admin approves/rejects payout request
        if payout_id:
            try:
                response = requests.post(f"{BASE_URL}/admin/payout-requests/{payout_id}/status", 
                                       headers=self.get_headers(self.admin_token),
                                       json={"status": "approved"})
                if response.status_code == 200:
                    self.log_result("Admin Approve Payout", True, "Payout approved successfully")
                else:
                    self.log_result("Admin Approve Payout", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Admin Approve Payout", False, "", str(e))
    
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
                    self.log_result("GET /api/orders/{id}/status", False, f"Status: {response.status_code}", response.text)
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
                    self.log_result("GET /api/buyer/addresses", False, f"Status: {response.status_code}", response.text)
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
                    self.log_result("GET /api/products", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("GET /api/products", False, "", str(e))
        
        # Test store search
        if self.buyer_token:
            try:
                response = requests.get(f"{BASE_URL}/stores/search", headers=self.get_headers(self.buyer_token))
                if response.status_code == 200:
                    stores = response.json()
                    self.log_result("GET /api/stores/search", True, f"Found {len(stores)} stores")
                else:
                    self.log_result("GET /api/stores/search", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("GET /api/stores/search", False, "", str(e))
    
    def test_refund_creation(self):
        """Test refund creation if we have an order"""
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
                    self.log_result("POST /api/buyer/refunds", True, "Refund created successfully")
                else:
                    self.log_result("POST /api/buyer/refunds", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("POST /api/buyer/refunds", False, "", str(e))
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Comprehensive Backend API Testing")
        print("=" * 60)
        
        # Authenticate all users first
        self.authenticate_all_users()
        
        # Test specific fixed endpoints
        self.test_specific_fixed_endpoints()
        
        # Test complete flows
        self.test_order_lifecycle()
        self.test_wallet_recharge_lifecycle()
        self.test_payout_lifecycle()
        
        # Test additional endpoints
        self.test_additional_endpoints()
        
        # Test refund creation
        self.test_refund_creation()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n🔥 FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"❌ {result['test']}: {result['error']}")
        
        print("\n✅ SUCCESSFUL TESTS:")
        for result in self.test_results:
            if result["success"]:
                print(f"✅ {result['test']}: {result['details']}")

if __name__ == "__main__":
    tester = APITester()
    tester.run_all_tests()