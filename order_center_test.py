#!/usr/bin/env python3
"""
Focused Order Center Testing Script
Tests the complete Seller Order Center functionality as requested in the review.
"""

import requests
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://git-copier-1.preview.emergentagent.com/api"

# Test Credentials
ADMIN_EMAIL = "support@arabshopping.org"
ADMIN_PASSWORD = "Hadi1247@"
SELLER_EMAIL = "testseller_new@test.com"
SELLER_PASSWORD = "TestPass123!"
BUYER_EMAIL = "testbuyer@test.com"
BUYER_PASSWORD = "TestPass123!"

class OrderCenterTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.admin_token = None
        self.seller_token = None
        self.buyer_token = None
        self.test_results = []
        self.test_order_id = None
        self.store_product_id = None
        self.store_product_price = None
        
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
        
    def login_user(self, email: str, password: str, role: str) -> Optional[str]:
        """Login user and return token"""
        try:
            response = self.session.post(f"{self.base_url}/auth/login", json={
                "email": email,
                "password": password
            })
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('session', {}).get('access_token')
                self.log_test(f"POST /api/auth/login ({role})", True, 
                            f"Successfully logged in as {role}: {data.get('user', {}).get('name')}")
                return token
            else:
                self.log_test(f"POST /api/auth/login ({role})", False, 
                            f"Login failed: HTTP {response.status_code}", response.text)
                return None
        except Exception as e:
            self.log_test(f"POST /api/auth/login ({role})", False, f"Login error: {str(e)}")
            return None

    def test_seller_order_center_main(self):
        """Test 1: Seller Order Center API (GET /api/seller/order-center)"""
        if not self.seller_token:
            self.log_test("Seller Order Center - Main View", False, "No seller token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.seller_token}"}
            response = self.session.get(f"{self.base_url}/seller/order-center", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                orders = data.get('orders', [])
                counts = data.get('counts', {})
                
                # Validate response structure
                required_counts = ['pending_payment', 'to_be_shipped', 'to_be_received', 'to_be_evaluated', 'after_sales', 'completed']
                counts_complete = all(status in counts for status in required_counts)
                
                success = True
                details_parts = []
                
                details_parts.append(f"Orders returned: {len(orders)}")
                details_parts.append(f"Counts complete: {counts_complete}")
                details_parts.append(f"Counts: {counts}")
                
                # Check if orders have required fields
                if orders:
                    sample_order = orders[0]
                    required_fields = ['id', 'totalAmount', 'orderStatus', 'paymentStatus', 'orderItems']
                    order_fields_complete = all(field in sample_order for field in required_fields)
                    details_parts.append(f"Order fields complete: {order_fields_complete}")
                    
                    if not order_fields_complete:
                        success = False
                
                self.log_test("Seller Order Center - Main View", success, 
                            "; ".join(details_parts), data)
                return success
            else:
                self.log_test("Seller Order Center - Main View", False, 
                            f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Seller Order Center - Main View", False, f"Error: {str(e)}")
            return False

    def find_or_create_shippable_order(self):
        """Find an order with status 'to_be_shipped' or create one"""
        if not self.seller_token:
            return False
            
        try:
            # First, check if there are any orders with status 'to_be_shipped'
            headers = {"Authorization": f"Bearer {self.seller_token}"}
            response = self.session.get(f"{self.base_url}/seller/order-center?status=to_be_shipped", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                orders = data.get('orders', [])
                
                if orders:
                    # Found existing shippable order
                    self.test_order_id = orders[0]['id']
                    self.log_test("Find Shippable Order", True, 
                                f"Found existing order to ship: {self.test_order_id}")
                    return True
            
            # No shippable order found, need to create one
            self.log_test("Find Shippable Order", False, 
                        "No existing shippable orders found, need to create test order")
            
            # Try to create a new order
            return self.create_test_order()
            
        except Exception as e:
            self.log_test("Find Shippable Order", False, f"Error: {str(e)}")
            return False

    def create_test_order(self):
        """Create a test order for shipping tests"""
        try:
            # Step 1: Get seller's store products
            if not self.seller_token:
                return False
                
            headers = {"Authorization": f"Bearer {self.seller_token}"}
            response = self.session.get(f"{self.base_url}/seller/store/products", headers=headers)
            
            if response.status_code != 200:
                self.log_test("Create Test Order - Get Products", False, 
                            f"Failed to get seller products: HTTP {response.status_code}")
                return False
                
            products_data = response.json()
            products = products_data.get('products', [])
            
            if not products:
                self.log_test("Create Test Order - Get Products", False, 
                            "No products available in seller's store")
                return False
                
            # Use first available product
            product = products[0]
            self.store_product_id = product['id']
            self.store_product_price = product['price']
            
            # Step 2: Login as buyer and create order
            if not self.buyer_token:
                self.buyer_token = self.login_user(BUYER_EMAIL, BUYER_PASSWORD, "buyer")
                if not self.buyer_token:
                    return False
            
            # Step 3: Create order as buyer
            buyer_headers = {"Authorization": f"Bearer {self.buyer_token}"}
            order_data = {
                "items": [{
                    "productId": self.store_product_id,
                    "quantity": 1,
                    "price": self.store_product_price
                }],
                "totalAmount": self.store_product_price,
                "useWallet": False,
                "shippingName": "Test Buyer",
                "shippingPhone": "+1234567890",
                "shippingAddress": {
                    "fullName": "Test Buyer",
                    "phone": "+1234567890",
                    "addressLine1": "123 Test Street",
                    "city": "Test City",
                    "state": "Test State",
                    "postalCode": "12345",
                    "country": "Test Country"
                }
            }
            
            response = self.session.post(f"{self.base_url}/orders", 
                                       headers=buyer_headers, json=order_data)
            
            if response.status_code != 200:
                self.log_test("Create Test Order - Place Order", False, 
                            f"Failed to create order: HTTP {response.status_code}", response.text)
                return False
                
            order_response = response.json()
            self.test_order_id = order_response.get('order', {}).get('id')
            
            if not self.test_order_id:
                self.log_test("Create Test Order - Place Order", False, 
                            "Order created but no ID returned")
                return False
            
            # Step 4: Login as admin and confirm payment
            if not self.admin_token:
                self.admin_token = self.login_user(ADMIN_EMAIL, ADMIN_PASSWORD, "admin")
                if not self.admin_token:
                    return False
            
            admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
            confirm_data = {"status": "paid"}
            
            response = self.session.put(f"{self.base_url}/admin/orders/{self.test_order_id}/payment-status", 
                                      headers=admin_headers, json=confirm_data)
            
            if response.status_code == 200:
                self.log_test("Create Test Order - Complete Flow", True, 
                            f"Successfully created and confirmed order: {self.test_order_id}")
                return True
            else:
                self.log_test("Create Test Order - Confirm Payment", False, 
                            f"Failed to confirm payment: HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Create Test Order", False, f"Error: {str(e)}")
            return False

    def test_ship_order(self):
        """Test 2: Ship Order Flow (POST /api/seller/orders/{id}/ship)"""
        if not self.seller_token or not self.test_order_id:
            self.log_test("Ship Order Flow", False, "No seller token or test order ID available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.seller_token}"}
            
            # Prepare shipment data
            future_date = (datetime.now() + timedelta(days=7)).isoformat()
            shipment_data = {
                "trackingNumber": "TEST123456789",
                "courierName": "DHL Express", 
                "courierCode": "dhl",
                "estimatedDelivery": future_date
            }
            
            response = self.session.post(f"{self.base_url}/seller/orders/{self.test_order_id}/ship", 
                                       headers=headers, json=shipment_data)
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                
                if success:
                    self.log_test("Ship Order Flow", True, 
                                f"Order shipped successfully with tracking: {shipment_data['trackingNumber']}")
                    return True
                else:
                    self.log_test("Ship Order Flow", False, 
                                "API returned success=false", data)
                    return False
            else:
                self.log_test("Ship Order Flow", False, 
                            f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Ship Order Flow", False, f"Error: {str(e)}")
            return False

    def test_order_status_transition(self):
        """Test 3: Verify order status updated to 'to_be_received'"""
        if not self.seller_token or not self.test_order_id:
            self.log_test("Order Status Transition", False, "No seller token or test order ID available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.seller_token}"}
            response = self.session.get(f"{self.base_url}/seller/order-center?status=to_be_received", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                orders = data.get('orders', [])
                
                # Check if our test order is in the to_be_received status
                order_found = any(order['id'] == self.test_order_id for order in orders)
                
                if order_found:
                    self.log_test("Order Status Transition", True, 
                                f"Order {self.test_order_id} successfully transitioned to 'to_be_received'")
                    return True
                else:
                    self.log_test("Order Status Transition", False, 
                                f"Order {self.test_order_id} not found in 'to_be_received' status")
                    return False
            else:
                self.log_test("Order Status Transition", False, 
                            f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Order Status Transition", False, f"Error: {str(e)}")
            return False

    def test_mark_delivered(self):
        """Test 4: Mark Delivered (PUT /api/seller/orders/{id}/shipment)"""
        if not self.seller_token or not self.test_order_id:
            self.log_test("Mark Delivered", False, "No seller token or test order ID available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.seller_token}"}
            update_data = {
                "deliveryStatus": "delivered"
            }
            
            response = self.session.put(f"{self.base_url}/seller/orders/{self.test_order_id}/shipment", 
                                      headers=headers, json=update_data)
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                
                if success:
                    self.log_test("Mark Delivered", True, 
                                f"Order {self.test_order_id} marked as delivered successfully")
                    return True
                else:
                    self.log_test("Mark Delivered", False, 
                                "API returned success=false", data)
                    return False
            else:
                self.log_test("Mark Delivered", False, 
                            f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Mark Delivered", False, f"Error: {str(e)}")
            return False

    def test_refunds_api(self):
        """Test 5: Refunds API (GET /api/seller/refunds)"""
        if not self.seller_token:
            self.log_test("Refunds API", False, "No seller token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.seller_token}"}
            response = self.session.get(f"{self.base_url}/seller/refunds", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                refunds = data.get('refunds', [])
                counts = data.get('counts', {})
                
                self.log_test("Refunds API", True, 
                            f"Refunds API working. Found {len(refunds)} refunds. Counts: {counts}")
                return True
            else:
                error_detail = response.text
                if "Could not find a relationship between 'order_items' and 'products'" in error_detail:
                    self.log_test("Refunds API", False, 
                                "KNOWN ISSUE: Refunds endpoint still references old 'products' table instead of 'store_products'", 
                                error_detail)
                else:
                    self.log_test("Refunds API", False, 
                                f"HTTP {response.status_code}", error_detail)
                return False
                
        except Exception as e:
            self.log_test("Refunds API", False, f"Error: {str(e)}")
            return False

    def run_comprehensive_test(self):
        """Run all Order Center tests"""
        print("=" * 80)
        print("🛒 COMPREHENSIVE ORDER CENTER FUNCTIONALITY TESTING")
        print("Testing complete Seller Order Center functionality as requested")
        print("=" * 80)
        print()
        
        # Step 1: Authentication
        print("🔐 AUTHENTICATION")
        self.admin_token = self.login_user(ADMIN_EMAIL, ADMIN_PASSWORD, "admin")
        self.seller_token = self.login_user(SELLER_EMAIL, SELLER_PASSWORD, "seller")
        self.buyer_token = self.login_user(BUYER_EMAIL, BUYER_PASSWORD, "buyer")
        print()
        
        if not self.seller_token:
            print("❌ Cannot proceed without seller authentication")
            return
        
        # Step 2: Test Order Center Main View
        print("📋 PHASE 1: ORDER CENTER DATA DISPLAY")
        self.test_seller_order_center_main()
        
        # Step 3: Find or Create Shippable Order
        print("🔍 PHASE 2: ORDER PREPARATION")
        order_ready = self.find_or_create_shippable_order()
        
        if order_ready:
            # Step 4: Test Shipping Flow
            print("🚚 PHASE 3: SHIPPING FUNCTIONALITY")
            ship_success = self.test_ship_order()
            
            if ship_success:
                # Step 5: Test Status Transition
                self.test_order_status_transition()
                
                # Step 6: Test Mark Delivered
                self.test_mark_delivered()
        
        # Step 7: Test Refunds (independent of order creation)
        print("💰 PHASE 4: REFUNDS")
        self.test_refunds_api()
        
        # Summary
        print()
        print("=" * 80)
        print("📊 ORDER CENTER TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {total - passed}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Critical validations
        print("🎯 CRITICAL VALIDATIONS:")
        critical_tests = [
            "Seller Order Center - Main View",
            "Ship Order Flow", 
            "Order Status Transition",
            "Mark Delivered",
            "Refunds API"
        ]
        
        for test_name in critical_tests:
            result = next((r for r in self.test_results if r['test'] == test_name), None)
            if result:
                status = "✅" if result['success'] else "❌"
                print(f"{status} {test_name}")
        
        # Failed tests details
        failed_tests = [r for r in self.test_results if not r['success']]
        if failed_tests:
            print()
            print("❌ FAILED TESTS:")
            for result in failed_tests:
                print(f"   • {result['test']}: {result['details']}")
        
        print()
        print("=" * 80)

if __name__ == "__main__":
    tester = OrderCenterTester()
    tester.run_comprehensive_test()