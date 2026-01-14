"""
Backend API Tests for Product Catalog System
Tests: Products display, Admin CRUD, Seller catalog browsing
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://catalog-refactor.preview.emergentagent.com').rstrip('/')

# Test credentials
ADMIN_CREDS = {"email": "support@arabshopping.org", "password": "Hadi1247@"}
SELLER_CREDS = {"email": "testseller_new@test.com", "password": "TestPass123!"}
BUYER_CREDS = {"email": "testbuyer_new@test.com", "password": "TestPass123!"}


class TestPublicProductsAPI:
    """Test public products endpoint - no auth required"""
    
    def test_get_all_products(self):
        """GET /api/products - Should return all 100 seeded products"""
        response = requests.get(f"{BASE_URL}/api/products")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("success") == True
        assert "products" in data
        products = data["products"]
        assert len(products) == 100, f"Expected 100 products, got {len(products)}"
        print(f"✓ GET /api/products returned {len(products)} products")
    
    def test_products_have_required_fields(self):
        """Verify each product has required fields: id, title, description, price, images, category"""
        response = requests.get(f"{BASE_URL}/api/products")
        assert response.status_code == 200
        
        products = response.json()["products"]
        required_fields = ["id", "title", "description", "price", "images", "category"]
        
        for product in products[:10]:  # Check first 10 products
            for field in required_fields:
                assert field in product, f"Product missing field: {field}"
            assert product["price"] > 0, "Price should be positive"
            assert isinstance(product["images"], list), "Images should be a list"
            assert len(product["images"]) > 0, "Product should have at least one image"
        print("✓ Products have all required fields")
    
    def test_products_have_categories(self):
        """Verify products have category information"""
        response = requests.get(f"{BASE_URL}/api/products")
        assert response.status_code == 200
        
        products = response.json()["products"]
        categories_found = set()
        
        for product in products:
            if product.get("category"):
                categories_found.add(product["category"])
        
        assert len(categories_found) > 0, "Products should have categories"
        print(f"✓ Found {len(categories_found)} unique categories: {categories_found}")
    
    def test_get_categories(self):
        """GET /api/categories - Should return all product categories"""
        response = requests.get(f"{BASE_URL}/api/categories")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") == True
        assert "categories" in data
        categories = data["categories"]
        assert len(categories) == 10, f"Expected 10 categories, got {len(categories)}"
        
        # Verify category structure
        for cat in categories:
            assert "id" in cat
            assert "name" in cat
            assert "icon" in cat
        print(f"✓ GET /api/categories returned {len(categories)} categories")


class TestAdminAuthentication:
    """Test admin login and authentication"""
    
    def test_admin_login(self):
        """POST /api/auth/login - Admin should be able to login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=ADMIN_CREDS)
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        assert "session" in data
        assert "user" in data
        assert data["user"]["role"] == "admin"
        print("✓ Admin login successful")
        return data["session"]["access_token"]
    
    def test_admin_products_requires_auth(self):
        """GET /api/admin/products - Should require authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/products")
        assert response.status_code == 401 or response.status_code == 403
        print("✓ Admin products endpoint requires authentication")


class TestAdminProductManagement:
    """Test admin product CRUD operations"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=ADMIN_CREDS)
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        return response.json()["session"]["access_token"]
    
    def test_admin_get_all_products(self, admin_token):
        """GET /api/admin/products - Admin should see all products"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/products", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        assert "products" in data
        products = data["products"]
        assert len(products) == 100, f"Expected 100 products, got {len(products)}"
        print(f"✓ Admin GET /api/admin/products returned {len(products)} products")
    
    def test_admin_create_product(self, admin_token):
        """POST /api/admin/products - Admin should be able to create a product"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        new_product = {
            "title": "TEST_Admin_Created_Product",
            "description": "This is a test product created by admin",
            "price": 99.99,
            "category": "electronics"
        }
        
        response = requests.post(f"{BASE_URL}/api/admin/products", json=new_product, headers=headers)
        assert response.status_code in [200, 201], f"Create failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        assert "product" in data
        created = data["product"]
        assert created["title"] == new_product["title"]
        assert created["price"] == new_product["price"]
        print(f"✓ Admin created product: {created['id']}")
        return created["id"]
    
    def test_admin_update_product(self, admin_token):
        """PUT /api/admin/products/{id} - Admin should be able to update a product"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # First create a product to update
        new_product = {
            "title": "TEST_Product_To_Update",
            "description": "Original description",
            "price": 50.00,
            "category": "fashion"
        }
        create_response = requests.post(f"{BASE_URL}/api/admin/products", json=new_product, headers=headers)
        assert create_response.status_code in [200, 201]
        product_id = create_response.json()["product"]["id"]
        
        # Update the product
        update_data = {
            "title": "TEST_Updated_Product_Title",
            "price": 75.00
        }
        update_response = requests.put(f"{BASE_URL}/api/admin/products/{product_id}", json=update_data, headers=headers)
        assert update_response.status_code == 200, f"Update failed: {update_response.status_code} - {update_response.text}"
        
        data = update_response.json()
        assert data.get("success") == True
        updated = data["product"]
        assert updated["title"] == update_data["title"]
        assert updated["price"] == update_data["price"]
        print(f"✓ Admin updated product: {product_id}")
        return product_id
    
    def test_admin_delete_product(self, admin_token):
        """DELETE /api/admin/products/{id} - Admin should be able to delete a product"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # First create a product to delete
        new_product = {
            "title": "TEST_Product_To_Delete",
            "description": "This product will be deleted",
            "price": 25.00,
            "category": "home"
        }
        create_response = requests.post(f"{BASE_URL}/api/admin/products", json=new_product, headers=headers)
        assert create_response.status_code in [200, 201]
        product_id = create_response.json()["product"]["id"]
        
        # Delete the product
        delete_response = requests.delete(f"{BASE_URL}/api/admin/products/{product_id}", headers=headers)
        assert delete_response.status_code == 200, f"Delete failed: {delete_response.status_code} - {delete_response.text}"
        
        data = delete_response.json()
        assert data.get("success") == True
        print(f"✓ Admin deleted product: {product_id}")


class TestSellerCatalogAccess:
    """Test seller catalog browsing functionality"""
    
    @pytest.fixture
    def seller_token(self):
        """Get seller authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=SELLER_CREDS)
        if response.status_code != 200:
            pytest.skip(f"Seller login failed: {response.text}")
        return response.json()["session"]["access_token"]
    
    def test_seller_login(self):
        """POST /api/auth/login - Seller should be able to login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=SELLER_CREDS)
        assert response.status_code == 200, f"Seller login failed: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        assert data["user"]["role"] == "seller"
        print(f"✓ Seller login successful, verification status: {data['user'].get('verificationStatus')}")
    
    def test_seller_get_catalog(self, seller_token):
        """GET /api/catalog/products - Verified seller should see catalog"""
        headers = {"Authorization": f"Bearer {seller_token}"}
        response = requests.get(f"{BASE_URL}/api/catalog/products", headers=headers)
        assert response.status_code == 200, f"Catalog access failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        assert "products" in data
        products = data["products"]
        assert len(products) == 100, f"Expected 100 catalog products, got {len(products)}"
        print(f"✓ Seller can access catalog with {len(products)} products")
    
    def test_seller_my_products(self, seller_token):
        """GET /api/products/my - Seller should see their store products"""
        headers = {"Authorization": f"Bearer {seller_token}"}
        response = requests.get(f"{BASE_URL}/api/products/my", headers=headers)
        assert response.status_code == 200, f"My products failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        assert "products" in data
        print(f"✓ Seller my products returned {len(data['products'])} products")


class TestBuyerAccess:
    """Test buyer product browsing"""
    
    def test_buyer_login(self):
        """POST /api/auth/login - Buyer should be able to login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=BUYER_CREDS)
        assert response.status_code == 200, f"Buyer login failed: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        assert data["user"]["role"] == "buyer"
        print("✓ Buyer login successful")
    
    def test_buyer_can_browse_products(self):
        """Buyer can browse public products without auth"""
        response = requests.get(f"{BASE_URL}/api/products")
        assert response.status_code == 200
        
        products = response.json()["products"]
        assert len(products) == 100
        print(f"✓ Buyer can browse {len(products)} products")


class TestCleanup:
    """Cleanup test data"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=ADMIN_CREDS)
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        return response.json()["session"]["access_token"]
    
    def test_cleanup_test_products(self, admin_token):
        """Delete all TEST_ prefixed products"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Get all products
        response = requests.get(f"{BASE_URL}/api/admin/products", headers=headers)
        if response.status_code != 200:
            print("Could not get products for cleanup")
            return
        
        products = response.json().get("products", [])
        deleted_count = 0
        
        for product in products:
            if product.get("title", "").startswith("TEST_"):
                delete_response = requests.delete(f"{BASE_URL}/api/admin/products/{product['id']}", headers=headers)
                if delete_response.status_code == 200:
                    deleted_count += 1
        
        print(f"✓ Cleanup: Deleted {deleted_count} test products")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
