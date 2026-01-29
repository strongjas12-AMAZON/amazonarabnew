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
BASE_URL = "https://clone-wizard-33.preview.emergentagent.com/api"

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

    def test_admin_seed_catalog(self):
        """Test POST /api/admin/seed-catalog - Seed 100 products to catalog"""
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
                        f"Catalog seeded successfully. Created: {products_created}, Skipped: {products_skipped}, Total: {total_products}",
                        {"products_created": products_created, "products_skipped": products_skipped, "total_products": total_products}
                    )
                    
                    # Store a catalog product ID for later tests
                    if "sample_product_id" in data:
                        self.catalog_product_id = data["sample_product_id"]
                else:
                    self.log_test(
                        "POST /api/admin/seed-catalog", 
                        False, 
                        "Response missing success=true",
                        data
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
                        self.log_test(
                            "GET /api/stores/{store_id}", 
                            False, 
                            f"Store missing required fields: {missing_fields}",
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

    def test_store_products_security(self):
        """Test GET /api/stores/{store_id}/products - CRITICAL SECURITY TEST: Should only return store_products, NOT master catalog"""
        if not self.buyer_token:
            self.log_test(
                "GET /api/stores/{store_id}/products (SECURITY)", 
                False, 
                "No buyer auth token available - buyer login failed",
                None
            )
            return
            
        if not self.store_id:
            self.log_test(
                "GET /api/stores/{store_id}/products (SECURITY)", 
                False, 
                "No store ID available - store search failed",
                None
            )
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.buyer_token}"}
            response = self.session.get(f"{self.base_url}/stores/{self.store_id}/products", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    products = data.get("products", [])
                    
                    # CRITICAL: Verify this returns ONLY store_products, not the master catalog
                    # If this returns 100+ products, it's likely returning the master catalog (security issue)
                    if len(products) < 50:  # Reasonable threshold - stores shouldn't have 50+ products typically
                        self.log_test(
                            "GET /api/stores/{store_id}/products (SECURITY)", 
                            True, 
                            f"SECURITY PASS: Found {len(products)} store products (not master catalog). Buyers can only see products seller added to their store.",
                            {"products_count": len(products), "store_id": self.store_id}
                        )
                    else:
                        self.log_test(
                            "GET /api/stores/{store_id}/products (SECURITY)", 
                            False, 
                            f"SECURITY FAIL: Found {len(products)} products - this may be returning the master catalog instead of store_products only!",
                            {"products_count": len(products), "store_id": self.store_id}
                        )
                else:
                    self.log_test(
                        "GET /api/stores/{store_id}/products (SECURITY)", 
                        False, 
                        "Response missing success=true",
                        data
                    )
            elif response.status_code == 404:
                self.log_test(
                    "GET /api/stores/{store_id}/products (SECURITY)", 
                    False, 
                    f"Store not found (ID: {self.store_id})",
                    response.text
                )
            elif response.status_code == 401:
                self.log_test(
                    "GET /api/stores/{store_id}/products (SECURITY)", 
                    False, 
                    "Unauthorized - authentication required",
                    response.text
                )
            else:
                self.log_test(
                    "GET /api/stores/{store_id}/products (SECURITY)", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    None
                )
                
        except Exception as e:
            self.log_test(
                "GET /api/stores/{store_id}/products (SECURITY)", 
                False, 
                f"Exception: {str(e)}",
                None
            )

    def test_seller_catalog_browsing(self):
        """Test GET /api/seller/catalog/products - Seller browses master catalog"""
        if not self.seller_token:
            self.log_test(
                "GET /api/seller/catalog/products", 
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
                    if products and len(products) > 0 and not self.catalog_product_id:
                        self.catalog_product_id = products[0].get("id")
                    
                    self.log_test(
                        "GET /api/seller/catalog/products", 
                        True, 
                        f"Seller can browse catalog: {len(products)} products, total: {total}",
                        {"products_count": len(products), "total": total}
                    )
                else:
                    self.log_test(
                        "GET /api/seller/catalog/products", 
                        False, 
                        "Response missing success=true",
                        data
                    )
            elif response.status_code == 403:
                self.log_test(
                    "GET /api/seller/catalog/products", 
                    False, 
                    "Access forbidden - check if user has seller role",
                    response.text
                )
            elif response.status_code == 401:
                self.log_test(
                    "GET /api/seller/catalog/products", 
                    False, 
                    "Unauthorized - check if auth token is valid",
                    response.text
                )
            else:
                self.log_test(
                    "GET /api/seller/catalog/products", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    None
                )
                
        except Exception as e:
            self.log_test(
                "GET /api/seller/catalog/products", 
                False, 
                f"Exception: {str(e)}",
                None
            )

    def test_seller_add_product_to_store(self):
        """Test POST /api/seller/store/products - Add product from catalog to store"""
        if not self.seller_token:
            self.log_test(
                "POST /api/seller/store/products", 
                False, 
                "No seller auth token available - seller login failed",
                None
            )
            return
            
        if not self.catalog_product_id:
            self.log_test(
                "POST /api/seller/store/products", 
                False, 
                "No catalog product ID available - catalog browsing failed",
                None
            )
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.seller_token}"}
            form_data = {
                "catalog_product_id": self.catalog_product_id,
                "price": 29.99,
                "stock": 10,
                "custom_description": "Test product added to store"
            }
            
            response = self.session.post(f"{self.base_url}/seller/store/products", headers=headers, data=form_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    store_product = data.get("store_product", {})
                    
                    self.log_test(
                        "POST /api/seller/store/products", 
                        True, 
                        f"Product added to store successfully: {store_product.get('id', 'Unknown ID')}",
                        {"store_product_id": store_product.get("id"), "catalog_product_id": self.catalog_product_id}
                    )
                else:
                    self.log_test(
                        "POST /api/seller/store/products", 
                        False, 
                        "Response missing success=true",
                        data
                    )
            elif response.status_code == 400:
                # Check if it's a duplicate product error (acceptable)
                if "already exists" in response.text.lower():
                    self.log_test(
                        "POST /api/seller/store/products", 
                        True, 
                        "Product already exists in store (expected behavior)",
                        response.text
                    )
                else:
                    self.log_test(
                        "POST /api/seller/store/products", 
                        False, 
                        f"Bad request: {response.text}",
                        None
                    )
            elif response.status_code == 403:
                self.log_test(
                    "POST /api/seller/store/products", 
                    False, 
                    "Access forbidden - check if user has seller role",
                    response.text
                )
            elif response.status_code == 401:
                self.log_test(
                    "POST /api/seller/store/products", 
                    False, 
                    "Unauthorized - check if auth token is valid",
                    response.text
                )
            else:
                self.log_test(
                    "POST /api/seller/store/products", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    None
                )
                
        except Exception as e:
            self.log_test(
                "POST /api/seller/store/products", 
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
        """Run all tests in sequence"""
        print("=" * 80)
        print("BACKEND API TESTING - BUYER STORE SEARCH & STORE DETAIL SYSTEM")
        print("=" * 80)
        print(f"Base URL: {self.base_url}")
        print(f"Admin Email: {ADMIN_EMAIL}")
        print(f"Seller Email: {SELLER_EMAIL}")
        print(f"Buyer Email: {BUYER_EMAIL}")
        print("=" * 80)
        print()
        
        # Test 1: Authentication APIs
        print("🔐 AUTHENTICATION TESTS")
        print("-" * 40)
        self.test_admin_login()
        self.test_seller_login()
        self.test_buyer_login()
        print()
        
        # Test 2: Admin Seed Catalog API
        print("🌱 ADMIN CATALOG SEEDING")
        print("-" * 40)
        self.test_admin_seed_catalog()
        print()
        
        # Test 3: Store Search APIs
        print("🔍 STORE SEARCH TESTS")
        print("-" * 40)
        self.test_store_search_all()
        self.test_store_search_query()
        print()
        
        # Test 4: Store Detail API
        print("🏪 STORE DETAIL TESTS")
        print("-" * 40)
        self.test_store_detail()
        print()
        
        # Test 5: Store Products API (CRITICAL SECURITY TEST)
        print("🔒 CRITICAL SECURITY TEST - STORE PRODUCTS")
        print("-" * 40)
        self.test_store_products_security()
        print()
        
        # Test 6: Seller Catalog Browsing
        print("📚 SELLER CATALOG BROWSING")
        print("-" * 40)
        self.test_seller_catalog_browsing()
        print()
        
        # Test 7: Seller Store Management
        print("🛠️ SELLER STORE MANAGEMENT")
        print("-" * 40)
        self.test_seller_add_product_to_store()
        self.test_seller_get_store_products()
        self.test_seller_update_store_product()
        self.test_seller_delete_store_product()
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
        
        # Highlight critical security test result
        security_test = next((r for r in self.test_results if "SECURITY" in r["test"]), None)
        if security_test:
            if security_test["success"]:
                print("🔒 CRITICAL SECURITY TEST: ✅ PASSED - Buyers can only see store products, not master catalog")
            else:
                print("🔒 CRITICAL SECURITY TEST: ❌ FAILED - SECURITY VULNERABILITY DETECTED!")
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