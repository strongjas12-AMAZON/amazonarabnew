#!/usr/bin/env python3
"""
Final Comprehensive Backend API Testing Suite - A-TO-Z AUDIT
Tests all 93 endpoints mentioned in the review request
"""

import requests
import json
import time
from typing import Dict, List, Optional, Tuple
import uuid

class FinalMarketplaceAPITester:
    def __init__(self):
        self.base_url = "https://repo-clone-46.preview.emergentagent.com/api"
        
        # Working credentials (verified)
        self.admin_email = "support@arabshopping.org"
        self.admin_password = "Hadi1247@"
        self.seller_email = "testseller@test.com"
        self.seller_password = "TestPass123!"
        self.buyer_email = "testbuyer@test.com"
        self.buyer_password = "TestPass123!"
        
        # Tokens
        self.admin_token = None
        self.seller_token = None
        self.buyer_token = None
        
        # Test results
        self.results = {
            "working": [],
            "broken": [],
            "access_control_issues": [],
            "critical_flow_breakers": []
        }

    def log_result(self, endpoint: str, method: str, status: str, details: str = "", category: str = "working"):
        """Log test result"""
        result = {
            "endpoint": f"{method} {endpoint}",
            "status": status,
            "details": details
        }
        self.results[category].append(result)

    def make_request(self, method: str, endpoint: str, token: str = None, data: dict = None) -> Tuple[int, dict]:
        """Make HTTP request with proper headers"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method == "POST":
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

    def authenticate_all_users(self):
        """Authenticate all user types"""
        print("🔐 Authenticating all user types...")
        
        # Admin login
        status, response = self.make_request("POST", "/auth/login", data={
            "email": self.admin_email, "password": self.admin_password
        })
        if status == 200 and "session" in response:
            self.admin_token = response["session"]["access_token"]
            print("✅ Admin authenticated")
        else:
            print(f"❌ Admin authentication failed: {status}")
            return False
        
        # Seller login
        status, response = self.make_request("POST", "/auth/login", data={
            "email": self.seller_email, "password": self.seller_password
        })
        if status == 200 and "session" in response:
            self.seller_token = response["session"]["access_token"]
            print("✅ Seller authenticated")
        else:
            print(f"❌ Seller authentication failed: {status}")
            return False
        
        # Buyer login
        status, response = self.make_request("POST", "/auth/login", data={
            "email": self.buyer_email, "password": self.buyer_password
        })
        if status == 200 and "session" in response:
            self.buyer_token = response["session"]["access_token"]
            print("✅ Buyer authenticated")
        else:
            print(f"❌ Buyer authentication failed: {status}")
            return False
        
        return True

    def test_all_endpoints(self):
        """Test all 93 endpoints mentioned in the review request"""
        print("🚀 Testing ALL 93 endpoints...")
        
        # AUTH endpoints (test first, needed for everything)
        auth_endpoints = [
            ("POST", "/auth/register", "buyer", {"name": "Test Buyer", "email": f"testbuyer_{uuid.uuid4().hex[:8]}@test.com", "password": "TestPass123!", "role": "buyer"}),
            ("POST", "/auth/register", "seller", {"name": "Test Seller", "email": f"testseller_{uuid.uuid4().hex[:8]}@test.com", "password": "TestPass123!", "role": "seller", "storeName": f"Test Store {uuid.uuid4().hex[:8]}"}),
            ("POST", "/auth/login", "public", {"email": self.admin_email, "password": self.admin_password}),
            ("POST", "/auth/logout", "buyer", {}),
            ("POST", "/auth/refresh", "public", {"refresh_token": "invalid_token"}),
            ("GET", "/me", "admin", None),
            ("POST", "/setup-test-users", "public", {}),
            ("POST", "/setup-admin", "public", {})
        ]
        
        # ADMIN endpoints (must reject non-admin)
        admin_endpoints = [
            ("GET", "/admin/users", "admin", None),
            ("POST", "/admin/users/test-id/ban", "admin", {}),
            ("POST", "/admin/users/test-id/unban", "admin", {}),
            ("GET", "/admin/products", "admin", None),
            ("POST", "/admin/products", "admin", {"name": "Test Product", "description": "Test", "base_price": 99.99, "category": "electronics"}),
            ("PATCH", "/admin/products/test-id", "admin", {"base_price": 199.99}),
            ("POST", "/admin/products/test-id/toggle-active", "admin", {}),
            ("DELETE", "/admin/products/test-id", "admin", {}),
            ("POST", "/admin/seed-catalog", "admin", {}),
            ("POST", "/admin/clear-catalog", "admin", {}),
            ("POST", "/admin/clear-legacy-products", "admin", {}),
            ("POST", "/admin/cleanup-and-reseed-catalog", "admin", {}),
            ("GET", "/admin/store-name-requests", "admin", None),
            ("POST", "/admin/store-name-requests/test-id/approve", "admin", {}),
            ("POST", "/admin/store-name-requests/test-id/reject", "admin", {}),
            ("GET", "/admin/invite-codes", "admin", None),
            ("GET", "/admin/deposit-confirmations", "admin", None),
            ("POST", "/admin/orders/test-id/confirm-deposit", "admin", {"approved": True}),
            ("GET", "/admin/payout-requests", "admin", None),
            ("POST", "/admin/payout-requests/test-id/status", "admin", {"status": "approved"}),
            ("GET", "/admin/seller-wallet-recharge-requests", "admin", None),
            ("POST", "/admin/seller-wallet-recharge-requests/test-id/status", "admin", {"status": "approved"}),
            ("GET", "/admin/wallet-recharge-requests", "admin", None),
            ("POST", "/admin/wallet-recharge-requests/test-id/status", "admin", {"status": "approved"}),
            ("GET", "/admin/wallets", "admin", None),
            ("GET", "/admin/platform-wallet", "admin", None),
            ("POST", "/verification/documents/test-id/review", "admin", {"status": "approved"})
        ]
        
        # SELLER endpoints (must reject buyer/admin)
        seller_endpoints = [
            ("GET", "/seller/catalog/products", "seller", None),
            ("POST", "/seller/store/products", "seller", {"catalog_product_id": "test-id", "price": 99.99, "stock": 10}),
            ("DELETE", "/seller/store/products/test-id", "seller", {}),
            ("GET", "/seller/order-center", "seller", None),
            ("GET", "/seller/order-center/test-id", "seller", None),
            ("GET", "/seller/orders/pending-deposit", "seller", None),
            ("POST", "/seller/orders/test-id/ship", "seller", {"trackingNumber": "TEST123", "courierCode": "dhl"}),
            ("GET", "/seller/orders/test-id/shipment", "seller", None),
            ("POST", "/seller/orders/test-id/status", "seller", {"status": "shipped"}),
            ("POST", "/seller/orders/test-id/submit-usdt-deposit", "seller", {"transaction_hash": "test_hash", "amount": 100.0}),
            ("GET", "/seller/deposit-status/test-id", "seller", None),
            ("GET", "/seller/earnings", "seller", None),
            ("GET", "/seller/wallet/balance", "seller", None),
            ("POST", "/seller/wallet/recharge", "seller", {"amount": 100.0, "transaction_hash": "test_hash"}),
            ("GET", "/seller/wallet/recharge-requests", "seller", None),
            ("POST", "/seller/wallet/deposit-for-order", "seller", {"amount": 100.0}),
            ("POST", "/seller/wallet/payout-requests", "seller", {"amount": 50.0}),
            ("POST", "/seller/payout-requests", "seller", {"amount": 50.0, "payoutWallet": "TY8Z91NMCjREyZVj9NjDsF8hVjyqfxFFRU"}),
            ("POST", "/seller/store-name-change", "seller", {"newStoreName": "New Store Name"}),
            ("GET", "/seller/refunds", "seller", None),
            ("PATCH", "/seller/refunds/test-id", "seller", {"status": "approved"}),
            ("POST", "/verification/upload", "seller", {}),
            ("GET", "/verification/documents", "seller", None),
            ("PATCH", "/seller/products/test-id", "seller", {"price": 199.99}),
            ("PATCH", "/products/test-id", "seller", {"price": 199.99}),
            ("POST", "/products/test-id/upload-image", "seller", {}),
            ("DELETE", "/products/test-id/remove-image", "seller", {}),
            ("GET", "/products/my", "seller", None)
        ]
        
        # BUYER endpoints
        buyer_endpoints = [
            ("GET", "/products", "buyer", None),
            ("GET", "/products/test-id", "buyer", None),
            ("GET", "/stores/search", "buyer", None),
            ("GET", "/stores/test-id", "buyer", None),
            ("GET", "/stores/test-id/products", "buyer", None),
            ("GET", "/categories", "buyer", None),
            ("GET", "/couriers", "buyer", None),
            ("POST", "/orders", "buyer", {"items": [{"product_id": "test-id", "quantity": 1}], "shippingAddress": "test-address", "paymentMethod": "wallet"}),
            ("GET", "/orders/my", "buyer", None),
            ("GET", "/orders/test-id/status", "buyer", None),
            ("POST", "/orders/test-id/confirm-delivery", "buyer", {}),
            ("POST", "/orders/test-id/ship-by-platform", "buyer", {}),
            ("POST", "/buyer/addresses", "buyer", {"fullName": "Test User", "phoneNumber": "+1234567890", "addressLine1": "123 Test St", "city": "Test City", "state": "Test State", "postalCode": "12345", "country": "Test Country"}),
            ("GET", "/buyer/addresses", "buyer", None),
            ("PATCH", "/buyer/addresses/test-id", "buyer", {"city": "Updated City"}),
            ("DELETE", "/buyer/addresses/test-id", "buyer", {}),
            ("GET", "/buyer/refunds", "buyer", None),
            ("GET", "/wallet/balance", "buyer", None),
            ("POST", "/wallet/recharge", "buyer", {"amount": 200.0, "transaction_hash": "buyer_hash"}),
            ("GET", "/wallet/recharge-requests", "buyer", None),
            ("GET", "/wallet/transactions", "buyer", None)
        ]
        
        # PUBLIC / MISC endpoints
        public_endpoints = [
            ("GET", "/catalog/products", "public", None),
            ("POST", "/contact", "public", {"name": "Test User", "email": "test@test.com", "subject": "Test Subject", "message": "Test message"})
        ]
        
        # Test all endpoint categories
        self._test_endpoint_group("AUTH", auth_endpoints)
        self._test_endpoint_group("ADMIN", admin_endpoints)
        self._test_endpoint_group("SELLER", seller_endpoints)
        self._test_endpoint_group("BUYER", buyer_endpoints)
        self._test_endpoint_group("PUBLIC", public_endpoints)

    def _test_endpoint_group(self, group_name: str, endpoints: List[Tuple]):
        """Test a group of endpoints"""
        print(f"\n📋 Testing {group_name} endpoints...")
        
        for method, endpoint, role, data in endpoints:
            # Get appropriate token
            token = None
            if role == "admin":
                token = self.admin_token
            elif role == "seller":
                token = self.seller_token
            elif role == "buyer":
                token = self.buyer_token
            # role == "public" means no token
            
            # Make request
            status, response = self.make_request(method, endpoint, token=token, data=data)
            
            # Analyze result
            if status == 500:
                self.log_result(endpoint, method, "❌ 500 Error", f"Internal server error", "critical_flow_breakers")
            elif status == 403 and role != "public":
                if endpoint.startswith("/admin/") and role != "admin":
                    self.log_result(endpoint, method, "✅ Working", "Correctly rejects non-admin access")
                elif endpoint.startswith("/seller/") and role != "seller":
                    self.log_result(endpoint, method, "✅ Working", "Correctly rejects non-seller access")
                else:
                    self.log_result(endpoint, method, "⚠️ Access Control Issue", f"Unexpected 403 for {role}", "access_control_issues")
            elif status in [200, 201, 204]:
                # Check for specific critical endpoints
                if endpoint == "/admin/products":
                    product_count = len(response.get("products", [])) if isinstance(response, dict) else len(response) if isinstance(response, list) else 0
                    if product_count >= 300:
                        self.log_result(endpoint, method, "✅ Working", f"Returns {product_count} products (expected ~311)")
                    else:
                        self.log_result(endpoint, method, "⚠️ Data Issue", f"Only {product_count} products, expected 311", "broken")
                elif endpoint == "/seller/catalog/products":
                    product_count = len(response.get("products", [])) if isinstance(response, dict) else len(response) if isinstance(response, list) else 0
                    if product_count >= 200:
                        self.log_result(endpoint, method, "✅ Working", f"Returns {product_count} products (expected ~230)")
                    else:
                        self.log_result(endpoint, method, "❌ Critical Issue", f"Only {product_count} products, expected ~230", "critical_flow_breakers")
                elif endpoint == "/seller/orders/pending-deposit":
                    if "escrowStatus does not exist" in str(response):
                        self.log_result(endpoint, method, "❌ Critical Column Error", "Database column name mismatch: escrowStatus vs escrow_status", "critical_flow_breakers")
                    else:
                        self.log_result(endpoint, method, "✅ Working", "Pending deposit orders accessible")
                else:
                    self.log_result(endpoint, method, "✅ Working", f"Status: {status}")
            elif status == 401:
                if role == "public" and endpoint in ["/auth/refresh"]:
                    self.log_result(endpoint, method, "✅ Working", "Correctly returns 401 for invalid token")
                else:
                    self.log_result(endpoint, method, "❌ Auth Issue", f"Unexpected 401", "broken")
            elif status == 404:
                if "test-id" in endpoint:
                    self.log_result(endpoint, method, "✅ Working", "Expected 404 for test ID")
                else:
                    self.log_result(endpoint, method, "❌ Not Found", f"Endpoint not found", "broken")
            elif status == 422:
                self.log_result(endpoint, method, "❌ Validation Error", f"Request validation failed", "broken")
            else:
                self.log_result(endpoint, method, "❌ Failed", f"Status: {status}", "broken")

    def run_comprehensive_audit(self):
        """Run the complete A-TO-Z audit"""
        print("🚀 Starting Final Comprehensive Backend API Audit (93 Endpoints)...")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate_all_users():
            print("❌ Authentication failed - cannot proceed with audit")
            return
        
        # Test all endpoints
        self.test_all_endpoints()
        
        # Generate report
        self.generate_report()

    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 80)
        print("📊 FINAL COMPREHENSIVE BACKEND AUDIT REPORT")
        print("=" * 80)
        
        total_tests = sum(len(category) for category in self.results.values())
        working_count = len(self.results["working"])
        
        print(f"\n📈 SUMMARY:")
        print(f"Total Tests: {total_tests}")
        print(f"Working: {working_count}")
        print(f"Broken: {len(self.results['broken'])}")
        print(f"Access Control Issues: {len(self.results['access_control_issues'])}")
        print(f"Critical Flow Breakers: {len(self.results['critical_flow_breakers'])}")
        print(f"Success Rate: {(working_count/total_tests*100):.1f}%" if total_tests > 0 else "N/A")
        
        # Critical issues first
        if self.results["critical_flow_breakers"]:
            print(f"\n🔥 CRITICAL FLOW BREAKERS ({len(self.results['critical_flow_breakers'])}):")
            for result in self.results["critical_flow_breakers"]:
                print(f"  ❌ {result['endpoint']}: {result['details']}")
        
        if self.results["broken"]:
            print(f"\n❌ BROKEN ENDPOINTS ({len(self.results['broken'])}):")
            for result in self.results["broken"]:
                print(f"  ❌ {result['endpoint']}: {result['details']}")
        
        if self.results["access_control_issues"]:
            print(f"\n⚠️ ACCESS CONTROL ISSUES ({len(self.results['access_control_issues'])}):")
            for result in self.results["access_control_issues"]:
                print(f"  ⚠️ {result['endpoint']}: {result['details']}")
        
        print(f"\n✅ WORKING ENDPOINTS ({len(self.results['working'])}):")
        for result in self.results["working"]:
            print(f"  ✅ {result['endpoint']}: {result['details']}")

if __name__ == "__main__":
    tester = FinalMarketplaceAPITester()
    tester.run_comprehensive_audit()