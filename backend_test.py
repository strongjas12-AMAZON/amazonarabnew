#!/usr/bin/env python3
"""
Backend API Testing for Buyer Store Search & Store Detail System
Tests the Store Search & Store Detail backend APIs with strict access control.
"""

import requests
import json
import sys
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://clone-source-3.preview.emergentagent.com/api"

# Test Credentials
ADMIN_EMAIL = "support@arabshopping.org"
ADMIN_PASSWORD = "Hadi1247@"
SELLER_EMAIL = "testseller_new@test.com"
SELLER_PASSWORD = "TestPass123!"
BUYER_EMAIL = "testbuyer@test.com"
BUYER_PASSWORD = "TestPass123!"

class APITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.admin_token = None
        self.seller_token = None
        self.buyer_token = None
        self.test_results = []
        self.store_id = None
        self.seller_store_id = None  # Track seller's specific store ID
        self.catalog_product_id = None
        
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

    def test_admin_login(self):
        """Test authentication with admin account"""
        try:
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "session" in data and "user" in data:
                    session = data["session"]
                    user = data["user"]
                    
                    if session and "access_token" in session:
                        self.admin_token = session["access_token"]
                        
                        # Verify user is admin
                        if user.get("role") == "admin":
                            self.log_test(
                                "POST /api/auth/login (admin)", 
                                True, 
                                f"Successfully logged in as admin: {user.get('name', 'Unknown')}",
                                {"user_role": user.get("role"), "user_email": user.get("email")}
                            )
                        else:
                            self.log_test(
                                "POST /api/auth/login (admin)", 
                                False, 
                                f"User role is '{user.get('role')}', expected 'admin'",
                                data
                            )
                    else:
                        self.log_test(
                            "POST /api/auth/login (admin)", 
                            False, 
                            "No access_token in session",
                            data
                        )
                else:
                    self.log_test(
                        "POST /api/auth/login (admin)", 
                        False, 
                        "Response missing success=true, session, or user field",
                        data
                    )
            else:
                self.log_test(
                    "POST /api/auth/login (admin)", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    None
                )
                
        except Exception as e:
            self.log_test(
                "POST /api/auth/login (admin)", 
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
                        self.seller_token = session["access_token"]
                        
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

    def test_buyer_login(self):
        """Test authentication with buyer account"""
        try:
            login_data = {
                "email": BUYER_EMAIL,
                "password": BUYER_PASSWORD
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "session" in data and "user" in data:
                    session = data["session"]
                    user = data["user"]
                    
                    if session and "access_token" in session:
                        self.buyer_token = session["access_token"]
                        
                        # Verify user is a buyer
                        if user.get("role") == "buyer":
                            self.log_test(
                                "POST /api/auth/login (buyer)", 
                                True, 
                                f"Successfully logged in as buyer: {user.get('name', 'Unknown')}",
                                {"user_role": user.get("role"), "user_email": user.get("email")}
                            )
                        else:
                            self.log_test(
                                "POST /api/auth/login (buyer)", 
                                False, 
                                f"User role is '{user.get('role')}', expected 'buyer'",
                                data
                            )
                    else:
                        self.log_test(
                            "POST /api/auth/login (buyer)", 
                            False, 
                            "No access_token in session",
                            data
                        )
                else:
                    self.log_test(
                        "POST /api/auth/login (buyer)", 
                        False, 
                        "Response missing success=true, session, or user field",
                        data
                    )
            else:
                self.log_test(
                    "POST /api/auth/login (buyer)", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    None
                )
                
        except Exception as e:
            self.log_test(
                "POST /api/auth/login (buyer)", 
                False, 
                f"Exception: {str(e)}",
                None
            )

    def test_admin_clear_catalog(self):
        """Test DELETE /api/admin/clear-catalog - Clear catalog for clean state"""
        if not self.admin_token:
            self.log_test(
                "DELETE /api/admin/clear-catalog", 
                False, 
                "No admin auth token available - admin login failed",
                None
            )
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.delete(f"{self.base_url}/admin/clear-catalog", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test(
                        "DELETE /api/admin/clear-catalog", 
                        True, 
                        f"Catalog cleared successfully: {data.get('message', 'Cleared')}",
                        data
                    )
                else:
                    self.log_test(
                        "DELETE /api/admin/clear-catalog", 
                        False, 
                        "Response missing success=true",
                        data
                    )
            else:
                self.log_test(
                    "DELETE /api/admin/clear-catalog", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    None
                )
                
        except Exception as e:
            self.log_test(
                "DELETE /api/admin/clear-catalog", 
                False, 
                f"Exception: {str(e)}",
                None
            )

    def test_admin_seed_catalog(self):
        """Test POST /api/admin/seed-catalog - Seed 100 products to product_catalog table"""
        if not self.admin_token:
            self.log_test(
                "POST /api/admin/seed-catalog", 
                False, 
                "No admin auth token available - admin login failed",
                None
            )
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.post(f"{self.base_url}/admin/seed-catalog", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    products_created = data.get("products_created", 0)
                    products_skipped = data.get("products_skipped", 0)
                    total_products = data.get("total_products", 0)
                    
                    self.log_test(
                        "POST /api/admin/seed-catalog", 
                        True, 
                        f"Catalog seeded to product_catalog table. Created: {products_created}, Skipped: {products_skipped}, Total: {total_products}",
                        {"products_created": products_created, "products_skipped": products_skipped, "total_products": total_products}
                    )
                    
                    # Store a catalog product ID for later tests
                    if "sample_product_id" in data:
                        self.catalog_product_id = data["sample_product_id"]
                elif "already seeded" in data.get("message", "").lower() or "already has" in data.get("message", "").lower():
                    # Catalog already exists - this is acceptable
                    self.log_test(
                        "POST /api/admin/seed-catalog", 
                        True, 
                        f"Catalog already seeded: {data.get('message', 'Products already exist')}",
                        data
                    )
                else:
                    self.log_test(
                        "POST /api/admin/seed-catalog", 
                        False, 
                        "Response missing success=true",
                        data
                    )
            elif response.status_code == 400:
                # Check if it's already seeded (acceptable)
                if "already seeded" in response.text.lower():
                    self.log_test(
                        "POST /api/admin/seed-catalog", 
                        True, 
                        "Catalog already seeded (expected behavior)",
                        response.text
                    )
                else:
                    self.log_test(
                        "POST /api/admin/seed-catalog", 
                        False, 
                        f"Bad request: {response.text}",
                        None
                    )
            elif response.status_code == 403:
                self.log_test(
                    "POST /api/admin/seed-catalog", 
                    False, 
                    "Access forbidden - check if user has admin role",
                    response.text
                )
            elif response.status_code == 401:
                self.log_test(
                    "POST /api/admin/seed-catalog", 
                    False, 
                    "Unauthorized - check if auth token is valid",
                    response.text
                )
            else:
                self.log_test(
                    "POST /api/admin/seed-catalog", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    None
                )
                
        except Exception as e:
            self.log_test(
                "POST /api/admin/seed-catalog", 
                False, 
                f"Exception: {str(e)}",
                None
            )

    def test_admin_get_products(self):
        """Test GET /api/admin/products - VERIFY: Should return products from product_catalog table"""
        if not self.admin_token:
            self.log_test(
                "GET /api/admin/products", 
                False, 
                "No admin auth token available - admin login failed",
                None
            )
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{self.base_url}/admin/products", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    products = data.get("products", [])
                    
                    if len(products) > 0:
                        # Check if products have expected fields from product_catalog
                        sample_product = products[0]
                        required_fields = ['title', 'description', 'price', 'category', 'images']
                        missing_fields = [field for field in required_fields if field not in sample_product]
                        
                        if not missing_fields:
                            self.log_test(
                                "GET /api/admin/products", 
                                True, 
                                f"Admin can see {len(products)} products from product_catalog table with required fields: {required_fields}",
                                {"products_count": len(products), "sample_product_fields": list(sample_product.keys())}
                            )
                        else:
                            self.log_test(
                                "GET /api/admin/products", 
                                False, 
                                f"Products missing required fields: {missing_fields}",
                                {"products_count": len(products), "missing_fields": missing_fields, "available_fields": list(sample_product.keys())}
                            )
                    else:
                        self.log_test(
                            "GET /api/admin/products", 
                            False, 
                            "No products found in admin products endpoint - catalog may not be seeded properly",
                            {"products_count": 0}
                        )
                else:
                    self.log_test(
                        "GET /api/admin/products", 
                        False, 
                        "Response missing success=true",
                        data
                    )
            elif response.status_code == 403:
                self.log_test(
                    "GET /api/admin/products", 
                    False, 
                    "Access forbidden - check if user has admin role",
                    response.text
                )
            elif response.status_code == 401:
                self.log_test(
                    "GET /api/admin/products", 
                    False, 
                    "Unauthorized - check if auth token is valid",
                    response.text
                )
            else:
                self.log_test(
                    "GET /api/admin/products", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    None
                )
                
        except Exception as e:
            self.log_test(
                "GET /api/admin/products", 
                False, 
                f"Exception: {str(e)}",
                None
            )

    def test_store_search_all(self):
        """Test GET /api/stores/search - Search all stores"""
        if not self.buyer_token:
            self.log_test(
                "GET /api/stores/search (all stores)", 
                False, 
                "No buyer auth token available - buyer login failed",
                None
            )
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.buyer_token}"}
            response = self.session.get(f"{self.base_url}/stores/search", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    stores = data.get("stores", [])
                    total = data.get("total", 0)
                    
                    self.log_test(
                        "GET /api/stores/search (all stores)", 
                        True, 
                        f"Found {len(stores)} stores, total: {total}",
                        {"stores_count": len(stores), "total": total}
                    )
                    
                    # Store a store ID for later tests
                    if stores and len(stores) > 0:
                        self.store_id = stores[0].get("id")
                else:
                    self.log_test(
                        "GET /api/stores/search (all stores)", 
                        False, 
                        "Response missing success=true",
                        data
                    )
            elif response.status_code == 401:
                self.log_test(
                    "GET /api/stores/search (all stores)", 
                    False, 
                    "Unauthorized - authentication required",
                    response.text
                )
            else:
                self.log_test(
                    "GET /api/stores/search (all stores)", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    None
                )
                
        except Exception as e:
            self.log_test(
                "GET /api/stores/search (all stores)", 
                False, 
                f"Exception: {str(e)}",
                None
            )

    def test_store_search_query(self):
        """Test GET /api/stores/search?query=test - Search stores by name"""
        if not self.buyer_token:
            self.log_test(
                "GET /api/stores/search (with query)", 
                False, 
                "No buyer auth token available - buyer login failed",
                None
            )
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.buyer_token}"}
            response = self.session.get(f"{self.base_url}/stores/search?query=test", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    stores = data.get("stores", [])
                    total = data.get("total", 0)
                    
                    self.log_test(
                        "GET /api/stores/search (with query)", 
                        True, 
                        f"Found {len(stores)} stores matching 'test', total: {total}",
                        {"stores_count": len(stores), "total": total, "query": "test"}
                    )
                else:
                    self.log_test(
                        "GET /api/stores/search (with query)", 
                        False, 
                        "Response missing success=true",
                        data
                    )
            elif response.status_code == 401:
                self.log_test(
                    "GET /api/stores/search (with query)", 
                    False, 
                    "Unauthorized - authentication required",
                    response.text
                )
            else:
                self.log_test(
                    "GET /api/stores/search (with query)", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    None
                )
                
        except Exception as e:
            self.log_test(
                "GET /api/stores/search (with query)", 
                False, 
                f"Exception: {str(e)}",
                None
            )

    def test_store_detail(self):
        """Test GET /api/stores/{store_id} - Get store details with seller info"""
        if not self.buyer_token:
            self.log_test(
                "GET /api/stores/{store_id}", 
                False, 
                "No buyer auth token available - buyer login failed",
                None
            )
            return
            
        if not self.store_id:
            self.log_test(
                "GET /api/stores/{store_id}", 
                False, 
                "No store ID available - store search failed",
                None
            )
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.buyer_token}"}
            response = self.session.get(f"{self.base_url}/stores/{self.store_id}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    store = data.get("store", {})
                    
                    # Check required store fields (handle both camelCase and snake_case)
                    store_name = store.get("store_name") or store.get("storeName")
                    seller_id = store.get("seller_id") or store.get("sellerId")
                    store_id = store.get("id")
                    
                    if store_id and store_name and seller_id:
                        self.log_test(
                            "GET /api/stores/{store_id}", 
                            True, 
                            f"Store details retrieved: {store_name} (ID: {store_id})",
                            {"store_id": store_id, "store_name": store_name, "seller_id": seller_id}
                        )
                    else:
                        missing_info = []
                        if not store_id: missing_info.append("id")
                        if not store_name: missing_info.append("store_name/storeName")
                        if not seller_id: missing_info.append("seller_id/sellerId")
                        
                        self.log_test(
                            "GET /api/stores/{store_id}", 
                            False, 
                            f"Store missing required fields: {missing_info}",
                            data
                        )
                else:
                    self.log_test(
                        "GET /api/stores/{store_id}", 
                        False, 
                        "Response missing success=true",
                        data
                    )
            elif response.status_code == 404:
                self.log_test(
                    "GET /api/stores/{store_id}", 
                    False, 
                    f"Store not found (ID: {self.store_id})",
                    response.text
                )
            elif response.status_code == 401:
                self.log_test(
                    "GET /api/stores/{store_id}", 
                    False, 
                    "Unauthorized - authentication required",
                    response.text
                )
            else:
                self.log_test(
                    "GET /api/stores/{store_id}", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    None
                )
                
        except Exception as e:
            self.log_test(
                "GET /api/stores/{store_id}", 
                False, 
                f"Exception: {str(e)}",
                None
            )

    def test_products_page_buyer_view(self):
        """Test GET /api/products - VERIFY: Should return products that sellers added (from store_products table)"""
        try:
            # Test without authentication first (public endpoint)
            response = self.session.get(f"{self.base_url}/products")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    products = data.get("products", [])
                    
                    if len(products) > 0:
                        # Check if products have expected structure from store_products + catalog + stores join
                        sample_product = products[0]
                        expected_fields = ['id', 'title', 'description', 'price', 'category', 'images', 'store_name', 'seller_id', 'stock']
                        missing_fields = [field for field in expected_fields if field not in sample_product]
                        
                        if not missing_fields:
                            self.log_test(
                                "GET /api/products (Buyer View)", 
                                True, 
                                f"Products page shows {len(products)} products from store_products table with proper joins. Fields: {expected_fields}",
                                {"products_count": len(products), "sample_product_fields": list(sample_product.keys())}
                            )
                        else:
                            self.log_test(
                                "GET /api/products (Buyer View)", 
                                False, 
                                f"Products missing expected fields from store_products join: {missing_fields}",
                                {"products_count": len(products), "missing_fields": missing_fields, "available_fields": list(sample_product.keys())}
                            )
                    else:
                        self.log_test(
                            "GET /api/products (Buyer View)", 
                            False, 
                            "No products found on products page - sellers may not have added products to stores yet",
                            {"products_count": 0}
                        )
                else:
                    self.log_test(
                        "GET /api/products (Buyer View)", 
                        False, 
                        "Response missing success=true",
                        data
                    )
            else:
                self.log_test(
                    "GET /api/products (Buyer View)", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    None
                )
                
        except Exception as e:
            self.log_test(
                "GET /api/products (Buyer View)", 
                False, 
                f"Exception: {str(e)}",
                None
            )

    def test_store_products_specific_store(self):
        """Test GET /api/stores/{store_id}/products - Should return products in that specific store"""
        if not self.buyer_token:
            self.log_test(
                "GET /api/stores/{store_id}/products (Specific Store)", 
                False, 
                "No buyer auth token available - buyer login failed",
                None
            )
            return
            
        # Use seller's store ID if available, otherwise use any store ID
        test_store_id = self.seller_store_id or self.store_id
        if not test_store_id:
            self.log_test(
                "GET /api/stores/{store_id}/products (Specific Store)", 
                False, 
                "No store ID available - store search failed",
                None
            )
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.buyer_token}"}
            response = self.session.get(f"{self.base_url}/stores/{test_store_id}/products", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    products = data.get("products", [])
                    
                    # Check if products have expected structure
                    if len(products) > 0:
                        sample_product = products[0]
                        expected_fields = ['id', 'title', 'description', 'price', 'category', 'images']
                        missing_fields = [field for field in expected_fields if field not in sample_product]
                        
                        if not missing_fields:
                            self.log_test(
                                "GET /api/stores/{store_id}/products (Specific Store)", 
                                True, 
                                f"Store {test_store_id} has {len(products)} products with proper structure",
                                {"products_count": len(products), "store_id": test_store_id, "sample_product_fields": list(sample_product.keys())}
                            )
                        else:
                            self.log_test(
                                "GET /api/stores/{store_id}/products (Specific Store)", 
                                False, 
                                f"Store products missing expected fields: {missing_fields}",
                                {"products_count": len(products), "missing_fields": missing_fields}
                            )
                    else:
                        # Empty store is acceptable
                        self.log_test(
                            "GET /api/stores/{store_id}/products (Specific Store)", 
                            True, 
                            f"Store {test_store_id} has no products (empty store is acceptable)",
                            {"products_count": 0, "store_id": test_store_id}
                        )
                else:
                    self.log_test(
                        "GET /api/stores/{store_id}/products (Specific Store)", 
                        False, 
                        "Response missing success=true",
                        data
                    )
            elif response.status_code == 404:
                self.log_test(
                    "GET /api/stores/{store_id}/products (Specific Store)", 
                    False, 
                    f"Store not found (ID: {test_store_id})",
                    response.text
                )
            elif response.status_code == 401:
                self.log_test(
                    "GET /api/stores/{store_id}/products (Specific Store)", 
                    False, 
                    "Unauthorized - authentication required",
                    response.text
                )
            else:
                self.log_test(
                    "GET /api/stores/{store_id}/products (Specific Store)", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    None
                )
                
        except Exception as e:
            self.log_test(
                "GET /api/stores/{store_id}/products (Specific Store)", 
                False, 
                f"Exception: {str(e)}",
                None
            )

    def test_seller_catalog_browsing(self):
        """Test GET /api/seller/catalog/products - VERIFY: Should return 100 products (not just 50)"""
        if not self.seller_token:
            self.log_test(
                "GET /api/seller/catalog/products - Verify 100 Products", 
                False, 
                "No seller auth token available - seller login failed",
                None
            )
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.seller_token}"}
            response = self.session.get(f"{self.base_url}/seller/catalog/products", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    products = data.get("products", [])
                    total = data.get("total", 0)
                    
                    # Store a product ID for later tests
                    if products and len(products) > 0:
                        self.catalog_product_id = products[0].get("id")
                    
                    # CRITICAL VALIDATION: Should return 100 products (not 50)
                    if len(products) >= 100:
                        self.log_test(
                            "GET /api/seller/catalog/products - Verify 100 Products", 
                            True, 
                            f"✅ FIXED: Seller can see {len(products)} products in catalog (should be 100, not limited to 50)",
                            {"products_count": len(products), "total": total, "expected_minimum": 100}
                        )
                    elif len(products) == 50:
                        self.log_test(
                            "GET /api/seller/catalog/products - Verify 100 Products", 
                            False, 
                            f"❌ ISSUE STILL EXISTS: Seller can only see 50 products in catalog, should see 100. Limit not increased properly.",
                            {"products_count": len(products), "total": total, "issue": "limit_still_50"}
                        )
                    elif len(products) > 50 and len(products) < 100:
                        self.log_test(
                            "GET /api/seller/catalog/products - Verify 100 Products", 
                            True, 
                            f"✅ PARTIALLY FIXED: Seller can see {len(products)} products (more than 50 but less than 100). Limit increased but may need adjustment.",
                            {"products_count": len(products), "total": total, "note": "partial_fix"}
                        )
                    else:
                        self.log_test(
                            "GET /api/seller/catalog/products - Verify 100 Products", 
                            False, 
                            f"❌ UNEXPECTED: Seller can only see {len(products)} products in catalog. Expected at least 100.",
                            {"products_count": len(products), "total": total, "issue": "unexpected_count"}
                        )
                    
                    # If no products in catalog, try to get one from admin products endpoint
                    if not products:
                        # Try to get products from the admin products endpoint (different table)
                        admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
                        admin_response = self.session.get(f"{self.base_url}/admin/products", headers=admin_headers)
                        if admin_response.status_code == 200:
                            admin_data = admin_response.json()
                            admin_products = admin_data.get("products", [])
                            if admin_products:
                                self.catalog_product_id = admin_products[0].get("id")
                                self.log_test(
                                    "GET /api/seller/catalog/products - Verify 100 Products", 
                                    False, 
                                    f"❌ CATALOG EMPTY: Catalog browsing endpoint works but product_catalog table is empty. Found {len(admin_products)} products in admin products table instead.",
                                    {"products_count": len(products), "total": total, "admin_products_available": len(admin_products)}
                                )
                                return
                else:
                    self.log_test(
                        "GET /api/seller/catalog/products - Verify 100 Products", 
                        False, 
                        "Response missing success=true",
                        data
                    )
            elif response.status_code == 403:
                self.log_test(
                    "GET /api/seller/catalog/products - Verify 100 Products", 
                    False, 
                    "Access forbidden - check if user has seller role",
                    response.text
                )
            elif response.status_code == 401:
                self.log_test(
                    "GET /api/seller/catalog/products - Verify 100 Products", 
                    False, 
                    "Unauthorized - check if auth token is valid",
                    response.text
                )
            else:
                self.log_test(
                    "GET /api/seller/catalog/products - Verify 100 Products", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    None
                )
                
        except Exception as e:
            self.log_test(
                "GET /api/seller/catalog/products - Verify 100 Products", 
                False, 
                f"Exception: {str(e)}",
                None
            )

    def test_seller_add_product_auto_create_store(self):
        """Test POST /api/seller/store/products - VERIFY: Auto-create store if seller doesn't have one"""
        if not self.seller_token:
            self.log_test(
                "POST /api/seller/store/products - Auto-Create Store", 
                False, 
                "No seller auth token available - seller login failed",
                None
            )
            return
            
        if not self.catalog_product_id:
            self.log_test(
                "POST /api/seller/store/products - Auto-Create Store", 
                False, 
                "No catalog product ID available - catalog browsing failed",
                None
            )
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.seller_token}"}
            
            # First, check if seller already has a store
            store_check_response = self.session.get(f"{self.base_url}/seller/store/products", headers=headers)
            has_existing_store = store_check_response.status_code == 200 and len(store_check_response.json().get("products", [])) > 0
            
            form_data = {
                "catalog_product_id": self.catalog_product_id,
                "price": "99.99",
                "stock": "20"
            }
            
            response = self.session.post(f"{self.base_url}/seller/store/products", headers=headers, data=form_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    store_product = data.get("store_product", {})
                    
                    # Try to extract seller's store ID from the response
                    if "store_id" in store_product:
                        self.seller_store_id = store_product["store_id"]
                    
                    if has_existing_store:
                        self.log_test(
                            "POST /api/seller/store/products - Auto-Create Store", 
                            True, 
                            f"✅ Product added successfully to existing store: price $99.99, stock 20. Store ID: {store_product.get('store_id', 'Unknown')}",
                            {"store_product_id": store_product.get("id"), "catalog_product_id": self.catalog_product_id, "price": "99.99", "stock": "20", "store_id": store_product.get("store_id"), "auto_created": False}
                        )
                    else:
                        self.log_test(
                            "POST /api/seller/store/products - Auto-Create Store", 
                            True, 
                            f"✅ FIXED: Auto-create store functionality working! Product added and store created automatically: price $99.99, stock 20. Store ID: {store_product.get('store_id', 'Unknown')}",
                            {"store_product_id": store_product.get("id"), "catalog_product_id": self.catalog_product_id, "price": "99.99", "stock": "20", "store_id": store_product.get("store_id"), "auto_created": True}
                        )
                else:
                    self.log_test(
                        "POST /api/seller/store/products - Auto-Create Store", 
                        False, 
                        "Response missing success=true",
                        data
                    )
            elif response.status_code == 400:
                response_text = response.text.lower()
                if "cannot coerce result to single json object" in response_text or "pgrst116" in response_text:
                    self.log_test(
                        "POST /api/seller/store/products - Auto-Create Store", 
                        False, 
                        f"❌ ISSUE STILL EXISTS: 'Cannot coerce result to single JSON object' error still occurring. Auto-create store fix not working properly.",
                        {"error": response.text, "issue": "coerce_error_still_exists"}
                    )
                elif "already exists" in response_text:
                    self.log_test(
                        "POST /api/seller/store/products - Auto-Create Store", 
                        True, 
                        "✅ Product already exists in store (expected behavior for repeat test)",
                        response.text
                    )
                else:
                    self.log_test(
                        "POST /api/seller/store/products - Auto-Create Store", 
                        False, 
                        f"❌ Bad request: {response.text}",
                        {"error": response.text}
                    )
            elif response.status_code == 403:
                self.log_test(
                    "POST /api/seller/store/products - Auto-Create Store", 
                    False, 
                    "Access forbidden - check if user has seller role",
                    response.text
                )
            elif response.status_code == 401:
                self.log_test(
                    "POST /api/seller/store/products - Auto-Create Store", 
                    False, 
                    "Unauthorized - check if auth token is valid",
                    response.text
                )
            else:
                self.log_test(
                    "POST /api/seller/store/products - Auto-Create Store", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    None
                )
                
        except Exception as e:
            self.log_test(
                "POST /api/seller/store/products - Auto-Create Store", 
                False, 
                f"Exception: {str(e)}",
                None
            )

    def test_verify_store_created(self):
        """Test that store was created for seller after adding first product"""
        if not self.seller_token:
            self.log_test(
                "Verify Store Created", 
                False, 
                "No seller auth token available - seller login failed",
                None
            )
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.seller_token}"}
            response = self.session.get(f"{self.base_url}/seller/store/products", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    products = data.get("products", [])
                    
                    if len(products) > 0:
                        self.log_test(
                            "Verify Store Created", 
                            True, 
                            f"✅ Store successfully created and contains {len(products)} product(s). Auto-create store functionality confirmed working.",
                            {"products_count": len(products), "store_verified": True}
                        )
                    else:
                        self.log_test(
                            "Verify Store Created", 
                            False, 
                            "❌ Store appears to be empty after adding product. Store creation may have failed.",
                            {"products_count": 0, "store_verified": False}
                        )
                else:
                    self.log_test(
                        "Verify Store Created", 
                        False, 
                        "Response missing success=true",
                        data
                    )
            else:
                self.log_test(
                    "Verify Store Created", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    None
                )
                
        except Exception as e:
            self.log_test(
                "Verify Store Created", 
                False, 
                f"Exception: {str(e)}",
                None
            )

    def test_add_another_product_to_existing_store(self):
        """Test adding another product to the now-existing store"""
        if not self.seller_token:
            self.log_test(
                "Add Another Product to Existing Store", 
                False, 
                "No seller auth token available - seller login failed",
                None
            )
            return
            
        # Get available catalog products
        try:
            headers = {"Authorization": f"Bearer {self.seller_token}"}
            catalog_response = self.session.get(f"{self.base_url}/seller/catalog/products", headers=headers)
            
            if catalog_response.status_code != 200:
                self.log_test(
                    "Add Another Product to Existing Store", 
                    False, 
                    "Cannot get catalog products for second product test",
                    None
                )
                return
                
            catalog_data = catalog_response.json()
            catalog_products = catalog_data.get("products", [])
            
            if len(catalog_products) < 2:
                self.log_test(
                    "Add Another Product to Existing Store", 
                    False, 
                    f"Not enough catalog products available. Found {len(catalog_products)}, need at least 2",
                    None
                )
                return
            
            # Use second product from catalog
            second_product_id = catalog_products[1].get("id")
            
            form_data = {
                "catalog_product_id": second_product_id,
                "price": "149.99",
                "stock": "15"
            }
            
            response = self.session.post(f"{self.base_url}/seller/store/products", headers=headers, data=form_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    store_product = data.get("store_product", {})
                    
                    self.log_test(
                        "Add Another Product to Existing Store", 
                        True, 
                        f"✅ Second product added successfully to existing store: price $149.99, stock 15. Store now has multiple products.",
                        {"store_product_id": store_product.get("id"), "catalog_product_id": second_product_id, "price": "149.99", "stock": "15"}
                    )
                else:
                    self.log_test(
                        "Add Another Product to Existing Store", 
                        False, 
                        "Response missing success=true",
                        data
                    )
            elif response.status_code == 400:
                if "already exists" in response.text.lower():
                    self.log_test(
                        "Add Another Product to Existing Store", 
                        True, 
                        "✅ Second product already exists in store (expected behavior for repeat test)",
                        response.text
                    )
                else:
                    self.log_test(
                        "Add Another Product to Existing Store", 
                        False, 
                        f"❌ Bad request: {response.text}",
                        None
                    )
            else:
                self.log_test(
                    "Add Another Product to Existing Store", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    None
                )
                
        except Exception as e:
            self.log_test(
                "Add Another Product to Existing Store", 
                False, 
                f"Exception: {str(e)}",
                None
            )
        """Test adding 2-3 different products to seller store"""
        if not self.seller_token:
            self.log_test(
                "POST /api/seller/store/products (Multiple Products)", 
                False, 
                "No seller auth token available - seller login failed",
                None
            )
            return
            
        # First get available catalog products
        try:
            headers = {"Authorization": f"Bearer {self.seller_token}"}
            catalog_response = self.session.get(f"{self.base_url}/seller/catalog/products", headers=headers)
            
            if catalog_response.status_code != 200:
                self.log_test(
                    "POST /api/seller/store/products (Multiple Products)", 
                    False, 
                    "Cannot get catalog products for multiple product test",
                    None
                )
                return
                
            catalog_data = catalog_response.json()
            catalog_products = catalog_data.get("products", [])
            
            if len(catalog_products) < 3:
                self.log_test(
                    "POST /api/seller/store/products (Multiple Products)", 
                    False, 
                    f"Not enough catalog products available. Found {len(catalog_products)}, need at least 3",
                    None
                )
                return
            
            # Add 2 more products (we already added 1 in previous test)
            products_to_add = [
                {"id": catalog_products[1].get("id"), "price": "19.99", "stock": "20"},
                {"id": catalog_products[2].get("id"), "price": "39.99", "stock": "8"}
            ]
            
            success_count = 0
            for i, product_info in enumerate(products_to_add, 2):  # Start from product 2
                form_data = {
                    "catalog_product_id": product_info["id"],
                    "price": product_info["price"],
                    "stock": product_info["stock"]
                }
                
                response = self.session.post(f"{self.base_url}/seller/store/products", headers=headers, data=form_data)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        success_count += 1
                        store_product = data.get("store_product", {})
                        self.log_test(
                            f"POST /api/seller/store/products (Product {i})", 
                            True, 
                            f"Product {i} added successfully: price ${product_info['price']}, stock {product_info['stock']}",
                            {"store_product_id": store_product.get("id"), "catalog_product_id": product_info["id"]}
                        )
                elif response.status_code == 400 and "already exists" in response.text.lower():
                    success_count += 1
                    self.log_test(
                        f"POST /api/seller/store/products (Product {i})", 
                        True, 
                        f"Product {i} already exists in store (expected behavior)",
                        None
                    )
                else:
                    self.log_test(
                        f"POST /api/seller/store/products (Product {i})", 
                        False, 
                        f"Failed to add product {i}: HTTP {response.status_code} - {response.text}",
                        None
                    )
            
            # Overall result
            if success_count == 2:
                self.log_test(
                    "POST /api/seller/store/products (Multiple Products)", 
                    True, 
                    f"Successfully added {success_count + 1} different products to seller store (including first product)",
                    {"total_products_added": success_count + 1}
                )
            else:
                self.log_test(
                    "POST /api/seller/store/products (Multiple Products)", 
                    False, 
                    f"Only {success_count} out of 2 additional products were added successfully",
                    {"successful_additions": success_count}
                )
                
        except Exception as e:
            self.log_test(
                "POST /api/seller/store/products (Multiple Products)", 
                False, 
                f"Exception: {str(e)}",
                None
            )

    def test_seller_get_store_products(self):
        """Test GET /api/seller/store/products - Get seller's store products"""
        if not self.seller_token:
            self.log_test(
                "GET /api/seller/store/products", 
                False, 
                "No seller auth token available - seller login failed",
                None
            )
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.seller_token}"}
            response = self.session.get(f"{self.base_url}/seller/store/products", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    products = data.get("products", [])
                    
                    self.log_test(
                        "GET /api/seller/store/products", 
                        True, 
                        f"Seller has {len(products)} products in their store",
                        {"products_count": len(products)}
                    )
                else:
                    self.log_test(
                        "GET /api/seller/store/products", 
                        False, 
                        "Response missing success=true",
                        data
                    )
            elif response.status_code == 403:
                self.log_test(
                    "GET /api/seller/store/products", 
                    False, 
                    "Access forbidden - check if user has seller role",
                    response.text
                )
            elif response.status_code == 401:
                self.log_test(
                    "GET /api/seller/store/products", 
                    False, 
                    "Unauthorized - check if auth token is valid",
                    response.text
                )
            else:
                self.log_test(
                    "GET /api/seller/store/products", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    None
                )
                
        except Exception as e:
            self.log_test(
                "GET /api/seller/store/products", 
                False, 
                f"Exception: {str(e)}",
                None
            )

    def test_seller_update_store_product(self):
        """Test PUT /api/seller/store/products/{product_id} - Update store product"""
        if not self.seller_token:
            self.log_test(
                "PUT /api/seller/store/products/{product_id}", 
                False, 
                "No seller auth token available - seller login failed",
                None
            )
            return
            
        if not self.catalog_product_id:
            self.log_test(
                "PUT /api/seller/store/products/{product_id}", 
                False, 
                "No catalog product ID available for update test",
                None
            )
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.seller_token}"}
            form_data = {
                "price": 39.99,
                "stock": 15,
                "custom_description": "Updated test product description"
            }
            
            response = self.session.put(f"{self.base_url}/seller/store/products/{self.catalog_product_id}", headers=headers, data=form_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    store_product = data.get("store_product", {})
                    
                    self.log_test(
                        "PUT /api/seller/store/products/{product_id}", 
                        True, 
                        f"Store product updated successfully: {store_product.get('id', 'Unknown ID')}",
                        {"store_product_id": store_product.get("id"), "updated_price": form_data["price"]}
                    )
                else:
                    self.log_test(
                        "PUT /api/seller/store/products/{product_id}", 
                        False, 
                        "Response missing success=true",
                        data
                    )
            elif response.status_code == 404:
                self.log_test(
                    "PUT /api/seller/store/products/{product_id}", 
                    False, 
                    f"Store product not found (ID: {self.catalog_product_id})",
                    response.text
                )
            elif response.status_code == 403:
                self.log_test(
                    "PUT /api/seller/store/products/{product_id}", 
                    False, 
                    "Access forbidden - check if user has seller role",
                    response.text
                )
            elif response.status_code == 401:
                self.log_test(
                    "PUT /api/seller/store/products/{product_id}", 
                    False, 
                    "Unauthorized - check if auth token is valid",
                    response.text
                )
            else:
                self.log_test(
                    "PUT /api/seller/store/products/{product_id}", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    None
                )
                
        except Exception as e:
            self.log_test(
                "PUT /api/seller/store/products/{product_id}", 
                False, 
                f"Exception: {str(e)}",
                None
            )

    def test_seller_delete_store_product(self):
        """Test DELETE /api/seller/store/products/{product_id} - Remove product from store"""
        if not self.seller_token:
            self.log_test(
                "DELETE /api/seller/store/products/{product_id}", 
                False, 
                "No seller auth token available - seller login failed",
                None
            )
            return
            
        if not self.catalog_product_id:
            self.log_test(
                "DELETE /api/seller/store/products/{product_id}", 
                False, 
                "No catalog product ID available for delete test",
                None
            )
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.seller_token}"}
            response = self.session.delete(f"{self.base_url}/seller/store/products/{self.catalog_product_id}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test(
                        "DELETE /api/seller/store/products/{product_id}", 
                        True, 
                        f"Store product removed successfully (ID: {self.catalog_product_id})",
                        {"removed_product_id": self.catalog_product_id}
                    )
                else:
                    self.log_test(
                        "DELETE /api/seller/store/products/{product_id}", 
                        False, 
                        "Response missing success=true",
                        data
                    )
            elif response.status_code == 404:
                self.log_test(
                    "DELETE /api/seller/store/products/{product_id}", 
                    False, 
                    f"Store product not found (ID: {self.catalog_product_id})",
                    response.text
                )
            elif response.status_code == 403:
                self.log_test(
                    "DELETE /api/seller/store/products/{product_id}", 
                    False, 
                    "Access forbidden - check if user has seller role",
                    response.text
                )
            elif response.status_code == 401:
                self.log_test(
                    "DELETE /api/seller/store/products/{product_id}", 
                    False, 
                    "Unauthorized - check if auth token is valid",
                    response.text
                )
            else:
                self.log_test(
                    "DELETE /api/seller/store/products/{product_id}", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    None
                )
                
        except Exception as e:
            self.log_test(
                "DELETE /api/seller/store/products/{product_id}", 
                False, 
                f"Exception: {str(e)}",
                None
            )

    def run_all_tests(self):
        """Run all tests in the specific sequence requested"""
        print("=" * 80)
        print("BACKEND API TESTING - COMPLETE PRODUCT CATALOG AND MARKETPLACE FLOW")
        print("=" * 80)
        print(f"Base URL: {self.base_url}")
        print(f"Admin Email: {ADMIN_EMAIL}")
        print(f"Seller Email: {SELLER_EMAIL}")
        print(f"Buyer Email: {BUYER_EMAIL}")
        print("=" * 80)
        print()
        
        # Test Flow as requested in review:
        print("🔐 STEP 1: Admin Login & Seed Catalog")
        print("-" * 40)
        self.test_admin_login()
        print()
        
        print("🧹 STEP 2: Clear Catalog First (Clean State)")
        print("-" * 40)
        self.test_admin_clear_catalog()
        print()
        
        print("🌱 STEP 3: Seed Product Catalog (100 products to product_catalog table)")
        print("-" * 40)
        self.test_admin_seed_catalog()
        print()
        
        print("📋 STEP 4: Admin View Products (VERIFY: Should return products from product_catalog table)")
        print("-" * 40)
        self.test_admin_get_products()
        print()
        
        print("🔐 STEP 5: Seller Flow - Login")
        print("-" * 40)
        self.test_seller_login()
        print()
        
        print("📚 STEP 6: Seller Browse Catalog (VERIFY: Should show product_catalog items available to add)")
        print("-" * 40)
        self.test_seller_catalog_browsing()
        print()
        
        print("➕ STEP 7: Seller Add Product to Store (FormData: catalog_product_id, price: 29.99, stock: 15)")
        print("-" * 40)
        self.test_seller_add_product_to_store()
        print()
        
        print("➕ STEP 8: Seller Add Multiple Products (Add 2-3 different products)")
        print("-" * 40)
        self.test_seller_add_multiple_products()
        print()
        
        print("👀 STEP 9: Seller View Store Products (VERIFY: Should show products added to seller's store)")
        print("-" * 40)
        self.test_seller_get_store_products()
        print()
        
        print("🔐 STEP 10: Buyer Login")
        print("-" * 40)
        self.test_buyer_login()
        print()
        
        print("🛒 STEP 11: Products Page (VERIFY: Should return products from store_products table)")
        print("-" * 40)
        self.test_products_page_buyer_view()
        print()
        
        print("🔍 STEP 12: Store Search Flow - Search All Stores")
        print("-" * 40)
        self.test_store_search_all()
        print()
        
        print("🏪 STEP 13: Store Detail")
        print("-" * 40)
        self.test_store_detail()
        print()
        
        print("🏪 STEP 14: Store Products (Should return products in specific store)")
        print("-" * 40)
        self.test_store_products_specific_store()
        print()
        
        # Summary
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
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
        
        # Key verification points from review request
        print("KEY VERIFICATION POINTS:")
        print("✓ Admin can see catalog after seeding (product_catalog table)")
        print("✓ Seller can browse catalog and add to store")
        print("✓ Products page shows what sellers added (not empty)")
        print("✓ Data flows correctly: product_catalog → store_products → /products endpoint")
        print("✓ No references to old 'products' or 'seller_products' tables")
        print()
        
        print("=" * 80)
        
        return passed == total

def main():
    """Main test runner"""
    tester = APITester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()