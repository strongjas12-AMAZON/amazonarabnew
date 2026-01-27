#!/usr/bin/env python3
"""
Backend API Testing for Seller Order Center
Tests the new Seller Order Center backend APIs as specified in the review request.
"""

import requests
import json
import sys
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://code-mirror-48.preview.emergentagent.com/api"
SELLER_EMAIL = "testseller_new@test.com"
SELLER_PASSWORD = "TestPass123!"

class APITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "response_data": response_data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {response_data}")
        print()

    def test_couriers_endpoint(self):
        """Test GET /api/couriers - Should return list of courier options (public endpoint, no auth needed)"""
        try:
            response = self.session.get(f"{self.base_url}/couriers")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "couriers" in data:
                    couriers = data["couriers"]
                    if isinstance(couriers, list) and len(couriers) > 0:
                        # Check if couriers have expected structure
                        first_courier = couriers[0]
                        if all(key in first_courier for key in ["code", "name", "icon"]):
                            self.log_test(
                                "GET /api/couriers", 
                                True, 
                                f"Found {len(couriers)} courier options",
                                data
                            )
                        else:
                            self.log_test(
                                "GET /api/couriers", 
                                False, 
                                "Courier objects missing required fields (code, name, icon)",
                                data
                            )
                    else:
                        self.log_test(
                            "GET /api/couriers", 
                            False, 
                            "No couriers found or invalid format",
                            data
                        )
                else:
                    self.log_test(
                        "GET /api/couriers", 
                        False, 
                        "Response missing success=true or couriers field",
                        data
                    )
            else:
                self.log_test(
                    "GET /api/couriers", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    None
                )
                
        except Exception as e:
            self.log_test(
                "GET /api/couriers", 
                False, 
                f"Exception: {str(e)}",
                None
            )

    def test_seller_login(self):
        """Test authentication with seller account"""
        try:
            login_data = {
                "email": SELLER_EMAIL,
                "password": SELLER_PASSWORD
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "session" in data and "user" in data:
                    session = data["session"]
                    user = data["user"]
                    
                    if session and "access_token" in session:
                        self.auth_token = session["access_token"]
                        
                        # Verify user is a seller
                        if user.get("role") == "seller":
                            self.log_test(
                                "POST /api/auth/login (seller)", 
                                True, 
                                f"Successfully logged in as seller: {user.get('name', 'Unknown')}",
                                {"user_role": user.get("role"), "user_email": user.get("email")}
                            )
                        else:
                            self.log_test(
                                "POST /api/auth/login (seller)", 
                                False, 
                                f"User role is '{user.get('role')}', expected 'seller'",
                                data
                            )
                    else:
                        self.log_test(
                            "POST /api/auth/login (seller)", 
                            False, 
                            "No access_token in session",
                            data
                        )
                else:
                    self.log_test(
                        "POST /api/auth/login (seller)", 
                        False, 
                        "Response missing success=true, session, or user field",
                        data
                    )
            else:
                self.log_test(
                    "POST /api/auth/login (seller)", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    None
                )
                
        except Exception as e:
            self.log_test(
                "POST /api/auth/login (seller)", 
                False, 
                f"Exception: {str(e)}",
                None
            )

    def test_seller_order_center(self):
        """Test GET /api/seller/order-center - Should return orders with status counts"""
        if not self.auth_token:
            self.log_test(
                "GET /api/seller/order-center", 
                False, 
                "No auth token available - login failed",
                None
            )
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = self.session.get(f"{self.base_url}/seller/order-center", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    # Check required fields
                    required_fields = ["orders", "counts", "total"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        orders = data["orders"]
                        counts = data["counts"]
                        total = data["total"]
                        
                        # Validate structure
                        if isinstance(orders, list) and isinstance(counts, dict) and isinstance(total, int):
                            # Check if counts has expected status fields
                            expected_statuses = ["pending_payment", "to_be_shipped", "to_be_received", "to_be_evaluated", "after_sales", "completed"]
                            missing_statuses = [status for status in expected_statuses if status not in counts]
                            
                            if not missing_statuses:
                                self.log_test(
                                    "GET /api/seller/order-center", 
                                    True, 
                                    f"Found {len(orders)} orders, total: {total}, counts: {counts}",
                                    {"orders_count": len(orders), "total": total, "counts": counts}
                                )
                            else:
                                self.log_test(
                                    "GET /api/seller/order-center", 
                                    False, 
                                    f"Missing status counts: {missing_statuses}",
                                    data
                                )
                        else:
                            self.log_test(
                                "GET /api/seller/order-center", 
                                False, 
                                f"Invalid data types - orders: {type(orders)}, counts: {type(counts)}, total: {type(total)}",
                                data
                            )
                    else:
                        self.log_test(
                            "GET /api/seller/order-center", 
                            False, 
                            f"Missing required fields: {missing_fields}",
                            data
                        )
                else:
                    self.log_test(
                        "GET /api/seller/order-center", 
                        False, 
                        "Response missing success=true",
                        data
                    )
            elif response.status_code == 500:
                # Check if this is the expected database migration issue
                response_text = response.text
                if "shipments" in response_text and "relationship" in response_text:
                    self.log_test(
                        "GET /api/seller/order-center", 
                        False, 
                        "Database migration needed - shipments/refunds tables missing foreign key relationships (EXPECTED ISSUE)",
                        response_text
                    )
                else:
                    self.log_test(
                        "GET /api/seller/order-center", 
                        False, 
                        f"HTTP 500 - Unexpected server error: {response_text}",
                        None
                    )
            elif response.status_code == 403:
                self.log_test(
                    "GET /api/seller/order-center", 
                    False, 
                    "Access forbidden - check if user has seller role",
                    response.text
                )
            elif response.status_code == 401:
                self.log_test(
                    "GET /api/seller/order-center", 
                    False, 
                    "Unauthorized - check if auth token is valid",
                    response.text
                )
            else:
                self.log_test(
                    "GET /api/seller/order-center", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    None
                )
                
        except Exception as e:
            self.log_test(
                "GET /api/seller/order-center", 
                False, 
                f"Exception: {str(e)}",
                None
            )

    def test_seller_refunds(self):
        """Test GET /api/seller/refunds - Should return refund requests for seller"""
        if not self.auth_token:
            self.log_test(
                "GET /api/seller/refunds", 
                False, 
                "No auth token available - login failed",
                None
            )
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = self.session.get(f"{self.base_url}/seller/refunds", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    # Check required fields
                    required_fields = ["refunds", "counts"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        refunds = data["refunds"]
                        counts = data["counts"]
                        
                        # Validate structure
                        if isinstance(refunds, list) and isinstance(counts, dict):
                            # Check if counts has expected status fields (be flexible about which ones exist)
                            expected_statuses = ["pending", "approved", "rejected", "completed"]
                            optional_statuses = ["seller_review", "processing"]
                            
                            # Check for core required statuses
                            missing_core_statuses = [status for status in expected_statuses if status not in counts]
                            
                            if not missing_core_statuses:
                                # Note any missing optional statuses but don't fail the test
                                missing_optional = [status for status in optional_statuses if status not in counts]
                                note = f" (missing optional statuses: {missing_optional})" if missing_optional else ""
                                
                                self.log_test(
                                    "GET /api/seller/refunds", 
                                    True, 
                                    f"Found {len(refunds)} refunds, counts: {counts}{note}",
                                    {"refunds_count": len(refunds), "counts": counts}
                                )
                            else:
                                self.log_test(
                                    "GET /api/seller/refunds", 
                                    False, 
                                    f"Missing core refund status counts: {missing_core_statuses}",
                                    data
                                )
                        else:
                            self.log_test(
                                "GET /api/seller/refunds", 
                                False, 
                                f"Invalid data types - refunds: {type(refunds)}, counts: {type(counts)}",
                                data
                            )
                    else:
                        self.log_test(
                            "GET /api/seller/refunds", 
                            False, 
                            f"Missing required fields: {missing_fields}",
                            data
                        )
                else:
                    self.log_test(
                        "GET /api/seller/refunds", 
                        False, 
                        "Response missing success=true",
                        data
                    )
            elif response.status_code == 403:
                self.log_test(
                    "GET /api/seller/refunds", 
                    False, 
                    "Access forbidden - check if user has seller role",
                    response.text
                )
            elif response.status_code == 401:
                self.log_test(
                    "GET /api/seller/refunds", 
                    False, 
                    "Unauthorized - check if auth token is valid",
                    response.text
                )
            else:
                self.log_test(
                    "GET /api/seller/refunds", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    None
                )
                
        except Exception as e:
            self.log_test(
                "GET /api/seller/refunds", 
                False, 
                f"Exception: {str(e)}",
                None
            )

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("=" * 60)
        print("BACKEND API TESTING - SELLER ORDER CENTER")
        print("=" * 60)
        print(f"Base URL: {self.base_url}")
        print(f"Seller Email: {SELLER_EMAIL}")
        print("=" * 60)
        print()
        
        # Test 1: Public courier endpoint
        self.test_couriers_endpoint()
        
        # Test 2: Seller authentication
        self.test_seller_login()
        
        # Test 3: Seller order center (requires auth)
        self.test_seller_order_center()
        
        # Test 4: Seller refunds (requires auth)
        self.test_seller_refunds()
        
        # Summary
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print()
        
        if total - passed > 0:
            print("FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"❌ {result['test']}: {result['details']}")
            print()
        
        print("=" * 60)
        
        return passed == total

def main():
    """Main test runner"""
    tester = APITester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()