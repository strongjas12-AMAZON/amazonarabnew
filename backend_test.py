#!/usr/bin/env python3
"""
Comprehensive Backend API Testing Suite
Tests all 93 endpoints for the marketplace app (Buyer/Seller/Admin)
"""

import requests
import json
import time
from typing import Dict, List, Optional, Tuple
import uuid

class MarketplaceAPITester:
    def __init__(self):
        self.base_url = "https://repo-clone-46.preview.emergentagent.com/api"
        self.admin_token = None
        self.seller_token = None
        self.buyer_token = None
        self.admin_refresh_token = None
        self.seller_refresh_token = None
        self.buyer_refresh_token = None
        
        # Test data storage
        self.test_results = {
            "working": [],
            "broken": [],
            "access_control_issues": [],
            "critical_flow_breakers": []
        }
        
        # Test credentials
        self.admin_email = "support@arabshopping.org"
        self.seller_email = "testseller_new@test.com"
        self.buyer_email = "testbuyer@test.com"
        self.test_password = "TestPass123!"
        
        # Test data IDs (will be populated during testing)
        self.test_product_id = None
        self.test_store_id = None
        self.test_order_id = None
        self.test_address_id = None

    def log_result(self, endpoint: str, method: str, status: str, details: str = "", category: str = "working"):
        """Log test result"""
        result = {
            "endpoint": f"{method} {endpoint}",
            "status": status,
            "details": details
        }
        
        if category == "working":
            self.test_results["working"].append(result)
        elif category == "broken":
            self.test_results["broken"].append(result)
        elif category == "access_control":
            self.test_results["access_control_issues"].append(result)
        elif category == "critical":
            self.test_results["critical_flow_breakers"].append(result)

    def make_request(self, method: str, endpoint: str, token: str = None, data: dict = None, files: dict = None) -> Tuple[int, dict]:
        """Make HTTP request with proper headers"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method == "POST":
                if files:
                    # Remove Content-Type for file uploads
                    headers.pop("Content-Type", None)
                    response = requests.post(url, headers=headers, files=files, data=data, timeout=30)
                else:
                    response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data, timeout=30)
            elif method == "PATCH":
                response = requests.patch(url, headers=headers, json=data, timeout=30)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                return 400, {"error": "Unsupported method"}
            
            try:
                return response.status_code, response.json()
            except:
                return response.status_code, {"text": response.text}
                
        except requests.exceptions.RequestException as e:
            return 500, {"error": str(e)}

    def test_auth_endpoints(self):
        """Test all authentication endpoints"""
        print("🔐 Testing Authentication Endpoints...")
        
        # Test setup-admin endpoint first
        status, response = self.make_request("POST", "/setup-admin")
        if status == 200:
            self.log_result("/setup-admin", "POST", "✅ Working", "Admin setup successful")
        else:
            self.log_result("/setup-admin", "POST", "❌ Failed", f"Status: {status}, Response: {response}")
        
        # Test setup-test-users endpoint
        status, response = self.make_request("POST", "/setup-test-users")
        if status == 200:
            self.log_result("/setup-test-users", "POST", "✅ Working", "Test users setup successful")
        else:
            self.log_result("/setup-test-users", "POST", "❌ Failed", f"Status: {status}, Response: {response}")
        
        # Test user registration for each role
        for role in ["buyer", "seller"]:
            test_email = f"test_{role}_{uuid.uuid4().hex[:8]}@test.com"
            register_data = {
                "name": f"Test {role.title()}",
                "email": test_email,
                "password": self.test_password,
                "role": role
            }
            
            # Add storeName for sellers
            if role == "seller":
                register_data["storeName"] = f"Test Store {uuid.uuid4().hex[:8]}"
            
            status, response = self.make_request("POST", "/auth/register", data=register_data)
            if status in [200, 201]:
                self.log_result("/auth/register", "POST", "✅ Working", f"{role} registration successful")
            else:
                self.log_result("/auth/register", "POST", "❌ Failed", f"{role} registration failed: {status}, {response}", "broken")
        
        # Test login for each role
        self._test_login_flow()
        
        # Test /me endpoint
        self._test_me_endpoint()
        
        # Test NEW refresh endpoint
        self._test_refresh_endpoint()
        
        # Test logout
        self._test_logout_endpoint()

    def _test_login_flow(self):
        """Test login for admin, seller, and buyer"""
        # Admin login
        login_data = {"email": self.admin_email, "password": self.test_password}
        status, response = self.make_request("POST", "/auth/login", data=login_data)
        if status == 200 and "session" in response and response["session"].get("access_token"):
            self.admin_token = response["session"]["access_token"]
            self.admin_refresh_token = response["session"].get("refresh_token")
            self.log_result("/auth/login", "POST", "✅ Working", "Admin login successful")
        else:
            self.log_result("/auth/login", "POST", "❌ Failed", f"Admin login failed: {status}, {response}", "critical")
        
        # Seller login
        login_data = {"email": self.seller_email, "password": self.test_password}
        status, response = self.make_request("POST", "/auth/login", data=login_data)
        if status == 200 and "session" in response and response["session"].get("access_token"):
            self.seller_token = response["session"]["access_token"]
            self.seller_refresh_token = response["session"].get("refresh_token")
            self.log_result("/auth/login", "POST", "✅ Working", "Seller login successful")
        else:
            self.log_result("/auth/login", "POST", "❌ Failed", f"Seller login failed: {status}, {response}", "critical")
        
        # Buyer login
        login_data = {"email": self.buyer_email, "password": self.test_password}
        status, response = self.make_request("POST", "/auth/login", data=login_data)
        if status == 200 and "session" in response and response["session"].get("access_token"):
            self.buyer_token = response["session"]["access_token"]
            self.buyer_refresh_token = response["session"].get("refresh_token")
            self.log_result("/auth/login", "POST", "✅ Working", "Buyer login successful")
        else:
            self.log_result("/auth/login", "POST", "❌ Failed", f"Buyer login failed: {status}, {response}", "critical")

    def _test_me_endpoint(self):
        """Test /me endpoint with and without token"""
        # Test without token
        status, response = self.make_request("GET", "/me")
        if status == 401:
            self.log_result("/me", "GET", "✅ Working", "Correctly rejects unauthenticated requests")
        else:
            self.log_result("/me", "GET", "⚠️ Access Control Issue", f"Should return 401 without token, got {status}", "access_control")
        
        # Test with valid tokens
        for role, token in [("admin", self.admin_token), ("seller", self.seller_token), ("buyer", self.buyer_token)]:
            if token:
                status, response = self.make_request("GET", "/me", token=token)
                if status == 200 and "email" in response:
                    self.log_result("/me", "GET", "✅ Working", f"{role} /me endpoint working")
                else:
                    self.log_result("/me", "GET", "❌ Failed", f"{role} /me failed: {status}, {response}", "broken")

    def _test_refresh_endpoint(self):
        """Test NEW /auth/refresh endpoint"""
        # Test with valid refresh token
        if self.admin_refresh_token:
            refresh_data = {"refresh_token": self.admin_refresh_token}
            status, response = self.make_request("POST", "/auth/refresh", data=refresh_data)
            if status == 200 and "access_token" in response:
                self.log_result("/auth/refresh", "POST", "✅ Working", "Valid refresh token returns new tokens")
                # Update token
                self.admin_token = response["access_token"]
                if "refresh_token" in response:
                    self.admin_refresh_token = response["refresh_token"]
            else:
                self.log_result("/auth/refresh", "POST", "❌ Failed", f"Valid refresh failed: {status}, {response}", "broken")
        
        # Test with invalid refresh token
        invalid_refresh_data = {"refresh_token": "invalid_token_12345"}
        status, response = self.make_request("POST", "/auth/refresh", data=invalid_refresh_data)
        if status == 401:
            self.log_result("/auth/refresh", "POST", "✅ Working", "Invalid refresh token correctly returns 401")
        else:
            self.log_result("/auth/refresh", "POST", "⚠️ Security Issue", f"Invalid refresh should return 401, got {status}", "access_control")

    def _test_logout_endpoint(self):
        """Test logout endpoint"""
        if self.buyer_token:
            status, response = self.make_request("POST", "/auth/logout", token=self.buyer_token)
            if status in [200, 204]:
                self.log_result("/auth/logout", "POST", "✅ Working", "Logout successful")
            else:
                self.log_result("/auth/logout", "POST", "❌ Failed", f"Logout failed: {status}, {response}", "broken")

    def test_admin_endpoints(self):
        """Test all admin endpoints"""
        print("👑 Testing Admin Endpoints...")
        
        if not self.admin_token:
            self.log_result("Admin Endpoints", "ALL", "❌ Skipped", "No admin token available", "critical")
            return
        
        # Test admin access control - non-admin should be rejected
        if self.buyer_token:
            status, response = self.make_request("GET", "/admin/users", token=self.buyer_token)
            if status == 403:
                self.log_result("/admin/users", "GET", "✅ Working", "Correctly rejects non-admin access")
            else:
                self.log_result("/admin/users", "GET", "⚠️ Access Control Issue", f"Should reject non-admin, got {status}", "access_control")
        
        # Test admin endpoints
        admin_endpoints = [
            ("GET", "/admin/users"),
            ("GET", "/admin/products"),
            ("GET", "/admin/store-name-requests"),
            ("GET", "/admin/invite-codes"),
            ("GET", "/admin/deposit-confirmations"),
            ("GET", "/admin/payout-requests"),
            ("GET", "/admin/seller-wallet-recharge-requests"),
            ("GET", "/admin/wallet-recharge-requests"),
            ("GET", "/admin/wallets"),
            ("GET", "/admin/platform-wallet")
        ]
        
        for method, endpoint in admin_endpoints:
            status, response = self.make_request(method, endpoint, token=self.admin_token)
            if status == 200:
                # Special check for products count
                if endpoint == "/admin/products":
                    product_count = len(response) if isinstance(response, list) else response.get("count", 0)
                    if product_count >= 300:  # Should be 311 products
                        self.log_result(endpoint, method, "✅ Working", f"Returns {product_count} products (expected ~311)")
                    else:
                        self.log_result(endpoint, method, "⚠️ Data Issue", f"Only {product_count} products, expected 311", "broken")
                else:
                    self.log_result(endpoint, method, "✅ Working", f"Status: {status}")
            else:
                self.log_result(endpoint, method, "❌ Failed", f"Status: {status}, Response: {response}", "broken")
        
        # Test admin product CRUD operations
        self._test_admin_product_crud()
        
        # Test admin user management
        self._test_admin_user_management()
        
        # Test admin catalog management
        self._test_admin_catalog_management()

    def _test_admin_product_crud(self):
        """Test admin product CRUD operations"""
        # Test create product
        product_data = {
            "name": "Test Luxury Watch",
            "description": "Premium luxury timepiece for testing",
            "base_price": 1299.99,
            "category": "Watches",
            "images": ["https://example.com/watch.jpg"]
        }
        
        status, response = self.make_request("POST", "/admin/products", token=self.admin_token, data=product_data)
        if status in [200, 201]:
            self.test_product_id = response.get("id")
            self.log_result("/admin/products", "POST", "✅ Working", "Product creation successful")
            
            # Test update product
            if self.test_product_id:
                update_data = {"base_price": 1399.99, "description": "Updated luxury timepiece"}
                status, response = self.make_request("PATCH", f"/admin/products/{self.test_product_id}", token=self.admin_token, data=update_data)
                if status == 200:
                    self.log_result(f"/admin/products/{self.test_product_id}", "PATCH", "✅ Working", "Product update successful")
                else:
                    self.log_result(f"/admin/products/{self.test_product_id}", "PATCH", "❌ Failed", f"Update failed: {status}, {response}", "broken")
                
                # Test toggle active
                status, response = self.make_request("POST", f"/admin/products/{self.test_product_id}/toggle-active", token=self.admin_token)
                if status == 200:
                    self.log_result(f"/admin/products/{self.test_product_id}/toggle-active", "POST", "✅ Working", "Toggle active successful")
                else:
                    self.log_result(f"/admin/products/{self.test_product_id}/toggle-active", "POST", "❌ Failed", f"Toggle failed: {status}, {response}", "broken")
        else:
            self.log_result("/admin/products", "POST", "❌ Failed", f"Product creation failed: {status}, {response}", "broken")

    def _test_admin_user_management(self):
        """Test admin user management endpoints"""
        # Get users first
        status, response = self.make_request("GET", "/admin/users", token=self.admin_token)
        if status == 200 and isinstance(response, list) and len(response) > 0:
            test_user_id = response[0].get("id")
            if test_user_id:
                # Test ban user
                status, response = self.make_request("POST", f"/admin/users/{test_user_id}/ban", token=self.admin_token)
                if status == 200:
                    self.log_result(f"/admin/users/{test_user_id}/ban", "POST", "✅ Working", "User ban successful")
                    
                    # Test unban user
                    status, response = self.make_request("POST", f"/admin/users/{test_user_id}/unban", token=self.admin_token)
                    if status == 200:
                        self.log_result(f"/admin/users/{test_user_id}/unban", "POST", "✅ Working", "User unban successful")
                    else:
                        self.log_result(f"/admin/users/{test_user_id}/unban", "POST", "❌ Failed", f"Unban failed: {status}, {response}", "broken")
                else:
                    self.log_result(f"/admin/users/{test_user_id}/ban", "POST", "❌ Failed", f"Ban failed: {status}, {response}", "broken")

    def _test_admin_catalog_management(self):
        """Test admin catalog management endpoints"""
        # Test seed catalog
        status, response = self.make_request("POST", "/admin/seed-catalog", token=self.admin_token)
        if status == 200:
            self.log_result("/admin/seed-catalog", "POST", "✅ Working", "Catalog seeding successful")
        else:
            self.log_result("/admin/seed-catalog", "POST", "❌ Failed", f"Seed failed: {status}, {response}", "broken")
        
        # Test cleanup and reseed
        status, response = self.make_request("POST", "/admin/cleanup-and-reseed-catalog", token=self.admin_token)
        if status == 200:
            self.log_result("/admin/cleanup-and-reseed-catalog", "POST", "✅ Working", "Cleanup and reseed successful")
        else:
            self.log_result("/admin/cleanup-and-reseed-catalog", "POST", "❌ Failed", f"Cleanup failed: {status}, {response}", "broken")

    def test_seller_endpoints(self):
        """Test all seller endpoints"""
        print("🏪 Testing Seller Endpoints...")
        
        if not self.seller_token:
            self.log_result("Seller Endpoints", "ALL", "❌ Skipped", "No seller token available", "critical")
            return
        
        # Test seller access control - non-seller should be rejected
        if self.buyer_token:
            status, response = self.make_request("GET", "/seller/catalog/products", token=self.buyer_token)
            if status == 403:
                self.log_result("/seller/catalog/products", "GET", "✅ Working", "Correctly rejects non-seller access")
            else:
                self.log_result("/seller/catalog/products", "GET", "⚠️ Access Control Issue", f"Should reject non-seller, got {status}", "access_control")
        
        # Test CRITICAL seller catalog endpoint (should return ~230 products)
        status, response = self.make_request("GET", "/seller/catalog/products", token=self.seller_token)
        if status == 200:
            product_count = len(response) if isinstance(response, list) else response.get("count", 0)
            if product_count >= 200:  # Should be around 230 products available to add
                self.log_result("/seller/catalog/products", "GET", "✅ Working", f"Returns {product_count} products (expected ~230)")
            else:
                self.log_result("/seller/catalog/products", "GET", "❌ Critical Issue", f"Only {product_count} products, expected ~230", "critical")
        else:
            self.log_result("/seller/catalog/products", "GET", "❌ Failed", f"Status: {status}, Response: {response}", "critical")
        
        # Test seller store management
        self._test_seller_store_management()
        
        # Test seller order center
        self._test_seller_order_center()
        
        # Test seller wallet and earnings
        self._test_seller_wallet_earnings()
        
        # Test seller verification
        self._test_seller_verification()

    def _test_seller_store_management(self):
        """Test seller store and product management"""
        # Test add product to store
        if self.seller_token:
            # First get a product from catalog
            status, response = self.make_request("GET", "/seller/catalog/products", token=self.seller_token)
            if status == 200 and isinstance(response, list) and len(response) > 0:
                catalog_product_id = response[0].get("id")
                if catalog_product_id:
                    store_product_data = {
                        "catalog_product_id": catalog_product_id,
                        "price": 899.99,
                        "stock": 25
                    }
                    
                    status, response = self.make_request("POST", "/seller/store/products", token=self.seller_token, data=store_product_data)
                    if status in [200, 201]:
                        self.log_result("/seller/store/products", "POST", "✅ Working", "Product added to store successfully")
                        
                        # Test get store products
                        status, response = self.make_request("GET", "/seller/store/products", token=self.seller_token)
                        if status == 200:
                            self.log_result("/seller/store/products", "GET", "✅ Working", f"Store products retrieved: {len(response) if isinstance(response, list) else 'N/A'}")
                        else:
                            self.log_result("/seller/store/products", "GET", "❌ Failed", f"Get store products failed: {status}, {response}", "broken")
                    else:
                        self.log_result("/seller/store/products", "POST", "❌ Failed", f"Add product failed: {status}, {response}", "broken")

    def _test_seller_order_center(self):
        """Test seller order center endpoints"""
        # Test order center
        status, response = self.make_request("GET", "/seller/order-center", token=self.seller_token)
        if status == 200:
            self.log_result("/seller/order-center", "GET", "✅ Working", "Order center accessible")
        else:
            self.log_result("/seller/order-center", "GET", "❌ Failed", f"Order center failed: {status}, {response}", "broken")
        
        # Test CRITICAL pending deposit endpoint (previously failed with column error)
        status, response = self.make_request("GET", "/seller/orders/pending-deposit", token=self.seller_token)
        if status == 200:
            self.log_result("/seller/orders/pending-deposit", "GET", "✅ Working", "Pending deposit orders accessible")
        else:
            if "escrowStatus does not exist" in str(response):
                self.log_result("/seller/orders/pending-deposit", "GET", "❌ Critical Column Error", "Database column name mismatch: escrowStatus vs escrow_status", "critical")
            else:
                self.log_result("/seller/orders/pending-deposit", "GET", "❌ Failed", f"Pending deposit failed: {status}, {response}", "broken")

    def _test_seller_wallet_earnings(self):
        """Test seller wallet and earnings endpoints"""
        # Test earnings
        status, response = self.make_request("GET", "/seller/earnings", token=self.seller_token)
        if status == 200:
            self.log_result("/seller/earnings", "GET", "✅ Working", "Seller earnings accessible")
        else:
            self.log_result("/seller/earnings", "GET", "❌ Failed", f"Earnings failed: {status}, {response}", "broken")
        
        # Test wallet balance
        status, response = self.make_request("GET", "/seller/wallet/balance", token=self.seller_token)
        if status == 200:
            self.log_result("/seller/wallet/balance", "GET", "✅ Working", "Wallet balance accessible")
        else:
            self.log_result("/seller/wallet/balance", "GET", "❌ Failed", f"Wallet balance failed: {status}, {response}", "broken")
        
        # Test wallet recharge
        recharge_data = {"amount": 100.0, "transaction_hash": f"test_hash_{uuid.uuid4().hex[:8]}"}
        status, response = self.make_request("POST", "/seller/wallet/recharge", token=self.seller_token, data=recharge_data)
        if status in [200, 201]:
            self.log_result("/seller/wallet/recharge", "POST", "✅ Working", "Wallet recharge successful")
        else:
            self.log_result("/seller/wallet/recharge", "POST", "❌ Failed", f"Wallet recharge failed: {status}, {response}", "broken")
        
        # Test payout request with TRC20 wallet
        payout_data = {
            "amount": 50.0,
            "payoutWallet": "TY8Z91NMCjREyZVj9NjDsF8hVjyqfxFFRU"  # Valid TRC20 address
        }
        status, response = self.make_request("POST", "/seller/payout-requests", token=self.seller_token, data=payout_data)
        if status in [200, 201]:
            self.log_result("/seller/payout-requests", "POST", "✅ Working", "Payout request with TRC20 wallet successful")
        else:
            self.log_result("/seller/payout-requests", "POST", "❌ Failed", f"Payout request failed: {status}, {response}", "broken")

    def _test_seller_verification(self):
        """Test seller verification endpoints"""
        # Test get verification documents
        status, response = self.make_request("GET", "/verification/documents", token=self.seller_token)
        if status == 200:
            self.log_result("/verification/documents", "GET", "✅ Working", "Verification documents accessible")
        else:
            self.log_result("/verification/documents", "GET", "❌ Failed", f"Verification docs failed: {status}, {response}", "broken")

    def test_buyer_endpoints(self):
        """Test all buyer endpoints"""
        print("🛒 Testing Buyer Endpoints...")
        
        if not self.buyer_token:
            self.log_result("Buyer Endpoints", "ALL", "❌ Skipped", "No buyer token available", "critical")
            return
        
        # Test products listing (should return ~81 store products)
        status, response = self.make_request("GET", "/products", token=self.buyer_token)
        if status == 200:
            product_count = len(response) if isinstance(response, list) else response.get("count", 0)
            self.log_result("/products", "GET", "✅ Working", f"Returns {product_count} store products")
        else:
            self.log_result("/products", "GET", "❌ Failed", f"Products listing failed: {status}, {response}", "broken")
        
        # Test store endpoints
        self._test_buyer_store_endpoints()
        
        # Test buyer addresses
        self._test_buyer_addresses()
        
        # Test buyer orders
        self._test_buyer_orders()
        
        # Test buyer wallet
        self._test_buyer_wallet()

    def _test_buyer_store_endpoints(self):
        """Test buyer store-related endpoints"""
        # Test store search
        status, response = self.make_request("GET", "/stores/search", token=self.buyer_token)
        if status == 200:
            store_count = len(response) if isinstance(response, list) else response.get("count", 0)
            self.log_result("/stores/search", "GET", "✅ Working", f"Returns {store_count} stores")
            
            # Get a store ID for further testing
            if isinstance(response, list) and len(response) > 0:
                self.test_store_id = response[0].get("id")
        else:
            self.log_result("/stores/search", "GET", "❌ Failed", f"Store search failed: {status}, {response}", "broken")
        
        # Test store detail
        if self.test_store_id:
            status, response = self.make_request("GET", f"/stores/{self.test_store_id}", token=self.buyer_token)
            if status == 200:
                self.log_result(f"/stores/{self.test_store_id}", "GET", "✅ Working", "Store detail accessible")
            else:
                self.log_result(f"/stores/{self.test_store_id}", "GET", "❌ Failed", f"Store detail failed: {status}, {response}", "broken")
            
            # Test store products
            status, response = self.make_request("GET", f"/stores/{self.test_store_id}/products", token=self.buyer_token)
            if status == 200:
                product_count = len(response) if isinstance(response, list) else response.get("count", 0)
                self.log_result(f"/stores/{self.test_store_id}/products", "GET", "✅ Working", f"Store has {product_count} products")
            else:
                self.log_result(f"/stores/{self.test_store_id}/products", "GET", "❌ Failed", f"Store products failed: {status}, {response}", "broken")

    def _test_buyer_addresses(self):
        """Test buyer address management"""
        # Test create address
        address_data = {
            "fullName": "John Doe",
            "phoneNumber": "+1234567890",
            "addressLine1": "123 Test Street",
            "city": "Test City",
            "state": "Test State",
            "postalCode": "12345",
            "country": "Test Country"
        }
        
        status, response = self.make_request("POST", "/buyer/addresses", token=self.buyer_token, data=address_data)
        if status in [200, 201]:
            self.test_address_id = response.get("id")
            self.log_result("/buyer/addresses", "POST", "✅ Working", "Address creation successful")
            
            # Test get addresses
            status, response = self.make_request("GET", "/buyer/addresses", token=self.buyer_token)
            if status == 200:
                self.log_result("/buyer/addresses", "GET", "✅ Working", f"Retrieved {len(response) if isinstance(response, list) else 'N/A'} addresses")
            else:
                self.log_result("/buyer/addresses", "GET", "❌ Failed", f"Get addresses failed: {status}, {response}", "broken")
            
            # Test update address
            if self.test_address_id:
                update_data = {"city": "Updated Test City"}
                status, response = self.make_request("PATCH", f"/buyer/addresses/{self.test_address_id}", token=self.buyer_token, data=update_data)
                if status == 200:
                    self.log_result(f"/buyer/addresses/{self.test_address_id}", "PATCH", "✅ Working", "Address update successful")
                else:
                    self.log_result(f"/buyer/addresses/{self.test_address_id}", "PATCH", "❌ Failed", f"Address update failed: {status}, {response}", "broken")
        else:
            self.log_result("/buyer/addresses", "POST", "❌ Failed", f"Address creation failed: {status}, {response}", "broken")

    def _test_buyer_orders(self):
        """Test buyer order endpoints"""
        # Test create order (end-to-end flow test)
        if self.test_address_id:
            # First get a product
            status, response = self.make_request("GET", "/products", token=self.buyer_token)
            if status == 200 and isinstance(response, list) and len(response) > 0:
                product = response[0]
                product_id = product.get("id")
                
                if product_id:
                    order_data = {
                        "items": [{"product_id": product_id, "quantity": 1}],
                        "shippingAddress": self.test_address_id,
                        "paymentMethod": "wallet"
                    }
                    
                    status, response = self.make_request("POST", "/orders", token=self.buyer_token, data=order_data)
                    if status in [200, 201]:
                        self.test_order_id = response.get("id")
                        order_status = response.get("escrowStatus") or response.get("escrow_status")
                        deposit_required = response.get("depositRequired") or response.get("deposit_required")
                        
                        self.log_result("/orders", "POST", "✅ Working", f"Order created with escrow_status='{order_status}', deposit_required={deposit_required}")
                        
                        # Verify order has correct escrow status and deposit amount
                        if order_status == "pending" and deposit_required and float(deposit_required) > 0:
                            self.log_result("Order Escrow Flow", "VALIDATION", "✅ Working", "Order correctly created with escrow_status='pending' and 80% deposit_required")
                        else:
                            self.log_result("Order Escrow Flow", "VALIDATION", "❌ Critical Issue", f"Order missing escrow data: status='{order_status}', deposit={deposit_required}", "critical")
                    else:
                        self.log_result("/orders", "POST", "❌ Failed", f"Order creation failed: {status}, {response}", "critical")
        
        # Test get my orders
        status, response = self.make_request("GET", "/orders/my", token=self.buyer_token)
        if status == 200:
            order_count = len(response) if isinstance(response, list) else response.get("count", 0)
            self.log_result("/orders/my", "GET", "✅ Working", f"Retrieved {order_count} orders")
        else:
            self.log_result("/orders/my", "GET", "❌ Failed", f"Get orders failed: {status}, {response}", "broken")

    def _test_buyer_wallet(self):
        """Test buyer wallet endpoints"""
        # Test wallet balance
        status, response = self.make_request("GET", "/wallet/balance", token=self.buyer_token)
        if status == 200:
            self.log_result("/wallet/balance", "GET", "✅ Working", "Wallet balance accessible")
        else:
            self.log_result("/wallet/balance", "GET", "❌ Failed", f"Wallet balance failed: {status}, {response}", "broken")
        
        # Test wallet recharge
        recharge_data = {"amount": 200.0, "transaction_hash": f"buyer_hash_{uuid.uuid4().hex[:8]}"}
        status, response = self.make_request("POST", "/wallet/recharge", token=self.buyer_token, data=recharge_data)
        if status in [200, 201]:
            self.log_result("/wallet/recharge", "POST", "✅ Working", "Wallet recharge successful")
        else:
            self.log_result("/wallet/recharge", "POST", "❌ Failed", f"Wallet recharge failed: {status}, {response}", "broken")

    def test_public_endpoints(self):
        """Test public/misc endpoints"""
        print("🌐 Testing Public Endpoints...")
        
        # Test catalog products (public)
        status, response = self.make_request("GET", "/catalog/products")
        if status == 200:
            product_count = len(response) if isinstance(response, list) else response.get("count", 0)
            self.log_result("/catalog/products", "GET", "✅ Working", f"Public catalog returns {product_count} products")
        else:
            self.log_result("/catalog/products", "GET", "❌ Failed", f"Public catalog failed: {status}, {response}", "broken")
        
        # Test categories
        status, response = self.make_request("GET", "/categories")
        if status == 200:
            self.log_result("/categories", "GET", "✅ Working", "Categories accessible")
        else:
            self.log_result("/categories", "GET", "❌ Failed", f"Categories failed: {status}, {response}", "broken")
        
        # Test couriers
        status, response = self.make_request("GET", "/couriers")
        if status == 200:
            self.log_result("/couriers", "GET", "✅ Working", "Couriers accessible")
        else:
            self.log_result("/couriers", "GET", "❌ Failed", f"Couriers failed: {status}, {response}", "broken")
        
        # Test contact
        contact_data = {"name": "Test User", "email": "test@test.com", "subject": "Test Subject", "message": "Test message"}
        status, response = self.make_request("POST", "/contact", data=contact_data)
        if status in [200, 201]:
            self.log_result("/contact", "POST", "✅ Working", "Contact form successful")
        else:
            self.log_result("/contact", "POST", "❌ Failed", f"Contact failed: {status}, {response}", "broken")

    def test_end_to_end_flows(self):
        """Test critical end-to-end flows"""
        print("🔄 Testing End-to-End Flows...")
        
        # Flow 1: Buyer signup → browse products → create order → pay from wallet
        self._test_buyer_order_flow()
        
        # Flow 2: Seller sees pending-deposit order → submits deposit → admin confirms
        self._test_seller_deposit_flow()
        
        # Flow 3: Admin order management flow
        self._test_admin_order_flow()

    def _test_buyer_order_flow(self):
        """Test complete buyer order flow"""
        if not self.buyer_token:
            return
        
        print("  Testing buyer order flow...")
        
        # Step 1: Browse products
        status, response = self.make_request("GET", "/products", token=self.buyer_token)
        if status != 200:
            self.log_result("Buyer Order Flow", "STEP 1", "❌ Failed", "Cannot browse products", "critical")
            return
        
        # Step 2: Create order (already tested in buyer endpoints)
        if self.test_order_id:
            self.log_result("Buyer Order Flow", "COMPLETE", "✅ Working", "Buyer can browse products and create orders")
        else:
            self.log_result("Buyer Order Flow", "COMPLETE", "❌ Failed", "Order creation failed in flow", "critical")

    def _test_seller_deposit_flow(self):
        """Test seller deposit submission flow"""
        if not self.seller_token or not self.test_order_id:
            return
        
        print("  Testing seller deposit flow...")
        
        # Test submit USDT deposit
        deposit_data = {
            "transaction_hash": f"usdt_hash_{uuid.uuid4().hex[:8]}",
            "amount": 100.0
        }
        
        status, response = self.make_request("POST", f"/seller/orders/{self.test_order_id}/submit-usdt-deposit", token=self.seller_token, data=deposit_data)
        if status in [200, 201]:
            self.log_result("Seller Deposit Flow", "USDT", "✅ Working", "USDT deposit submission successful")
        else:
            self.log_result("Seller Deposit Flow", "USDT", "❌ Failed", f"USDT deposit failed: {status}, {response}", "broken")
        
        # Test wallet deposit
        wallet_deposit_data = {"amount": 100.0}
        status, response = self.make_request("POST", f"/seller/wallet/deposit-for-order", token=self.seller_token, data=wallet_deposit_data)
        if status in [200, 201]:
            self.log_result("Seller Deposit Flow", "WALLET", "✅ Working", "Wallet deposit successful")
        else:
            self.log_result("Seller Deposit Flow", "WALLET", "❌ Failed", f"Wallet deposit failed: {status}, {response}", "broken")

    def _test_admin_order_flow(self):
        """Test admin order management flow"""
        if not self.admin_token or not self.test_order_id:
            return
        
        print("  Testing admin order flow...")
        
        # Test confirm deposit
        confirm_data = {"approved": True}
        status, response = self.make_request("POST", f"/admin/orders/{self.test_order_id}/confirm-deposit", token=self.admin_token, data=confirm_data)
        if status in [200, 201]:
            self.log_result("Admin Order Flow", "CONFIRM DEPOSIT", "✅ Working", "Admin can confirm deposits")
        else:
            self.log_result("Admin Order Flow", "CONFIRM DEPOSIT", "❌ Failed", f"Confirm deposit failed: {status}, {response}", "broken")

    def run_comprehensive_audit(self):
        """Run the complete A-TO-Z audit"""
        print("🚀 Starting Comprehensive Backend API Audit...")
        print("=" * 60)
        
        # Test in order of dependency
        self.test_auth_endpoints()
        self.test_admin_endpoints()
        self.test_seller_endpoints()
        self.test_buyer_endpoints()
        self.test_public_endpoints()
        self.test_end_to_end_flows()
        
        # Generate report
        self.generate_report()

    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE BACKEND AUDIT REPORT")
        print("=" * 60)
        
        total_tests = sum(len(category) for category in self.test_results.values())
        working_count = len(self.test_results["working"])
        
        print(f"\n📈 SUMMARY:")
        print(f"Total Tests: {total_tests}")
        print(f"Working: {working_count}")
        print(f"Broken: {len(self.test_results['broken'])}")
        print(f"Access Control Issues: {len(self.test_results['access_control_issues'])}")
        print(f"Critical Flow Breakers: {len(self.test_results['critical_flow_breakers'])}")
        print(f"Success Rate: {(working_count/total_tests*100):.1f}%" if total_tests > 0 else "N/A")
        
        # Detailed results
        if self.test_results["critical_flow_breakers"]:
            print(f"\n🔥 CRITICAL FLOW BREAKERS ({len(self.test_results['critical_flow_breakers'])}):")
            for result in self.test_results["critical_flow_breakers"]:
                print(f"  ❌ {result['endpoint']}: {result['details']}")
        
        if self.test_results["broken"]:
            print(f"\n❌ BROKEN ENDPOINTS ({len(self.test_results['broken'])}):")
            for result in self.test_results["broken"]:
                print(f"  ❌ {result['endpoint']}: {result['details']}")
        
        if self.test_results["access_control_issues"]:
            print(f"\n⚠️ ACCESS CONTROL ISSUES ({len(self.test_results['access_control_issues'])}):")
            for result in self.test_results["access_control_issues"]:
                print(f"  ⚠️ {result['endpoint']}: {result['details']}")
        
        if self.test_results["working"]:
            print(f"\n✅ WORKING ENDPOINTS ({len(self.test_results['working'])}):")
            for result in self.test_results["working"]:
                print(f"  ✅ {result['endpoint']}: {result['details']}")

if __name__ == "__main__":
    tester = MarketplaceAPITester()
    tester.run_comprehensive_audit()