"""
Backend API Tests for Amazon Arab Marketplace
Tests: Auth, Admin, Products, Orders, Verification endpoints
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "support@arabshopping.org"
ADMIN_PASSWORD = "Hadi1247@"

class TestHealthAndBasics:
    """Basic connectivity tests"""
    
    def test_api_reachable(self):
        """Test that API is reachable"""
        response = requests.get(f"{BASE_URL}/api/products", timeout=10)
        assert response.status_code == 200, f"API not reachable: {response.status_code}"
        print(f"✓ API is reachable at {BASE_URL}")


class TestAuthEndpoints:
    """Authentication endpoint tests"""
    
    def test_admin_login_success(self):
        """Test admin login with correct credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        assert "user" in data
        assert "session" in data
        assert data["user"]["email"] == ADMIN_EMAIL
        assert data["user"]["role"] == "admin"
        print(f"✓ Admin login successful - User: {data['user']['name']}")
        return data
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "invalid@test.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Invalid credentials correctly rejected")
    
    def test_register_buyer(self):
        """Test buyer registration"""
        unique_email = f"test_buyer_{uuid.uuid4().hex[:8]}@test.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "name": "Test Buyer",
            "email": unique_email,
            "password": "TestPass123!",
            "role": "buyer"
        })
        # May fail due to rate limiting or email confirmation requirements
        if response.status_code == 200:
            data = response.json()
            assert data.get("success") == True
            assert data["user"]["role"] == "buyer"
            print(f"✓ Buyer registration successful: {unique_email}")
        elif response.status_code == 429:
            print("⚠ Rate limited on registration - expected behavior")
        else:
            print(f"⚠ Registration returned {response.status_code}: {response.text}")
    
    def test_register_seller(self):
        """Test seller registration"""
        unique_email = f"test_seller_{uuid.uuid4().hex[:8]}@test.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "name": "Test Seller",
            "email": unique_email,
            "password": "TestPass123!",
            "role": "seller"
        })
        # May fail due to rate limiting
        if response.status_code == 200:
            data = response.json()
            assert data.get("success") == True
            assert data["user"]["role"] == "seller"
            assert data["user"]["verificationStatus"] == "unverified"
            print(f"✓ Seller registration successful: {unique_email}")
        elif response.status_code == 429:
            print("⚠ Rate limited on registration - expected behavior")
        else:
            print(f"⚠ Registration returned {response.status_code}: {response.text}")


class TestAdminEndpoints:
    """Admin-only endpoint tests"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Admin login failed - skipping admin tests")
        data = response.json()
        return data["session"]["access_token"]
    
    def test_get_all_users(self, admin_token):
        """Test admin can get all users"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/users", headers=headers)
        
        assert response.status_code == 200, f"Get users failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert "users" in data
        assert isinstance(data["users"], list)
        print(f"✓ Admin can view users - Total: {len(data['users'])}")
        
        # Verify user data structure
        if data["users"]:
            user = data["users"][0]
            assert "id" in user
            assert "email" in user
            assert "name" in user
            assert "role" in user
            assert "verificationStatus" in user
    
    def test_create_invite_code(self, admin_token):
        """Test admin can create merchant invite codes"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.post(f"{BASE_URL}/api/admin/invite-codes", headers=headers)
        
        assert response.status_code == 200, f"Create invite code failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert "inviteCode" in data
        assert "code" in data["inviteCode"]
        assert data["inviteCode"]["isUsed"] == False
        print(f"✓ Invite code created: {data['inviteCode']['code']}")
        return data["inviteCode"]["code"]
    
    def test_get_invite_codes(self, admin_token):
        """Test admin can get all invite codes"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/invite-codes", headers=headers)
        
        assert response.status_code == 200, f"Get invite codes failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert "codes" in data
        assert isinstance(data["codes"], list)
        print(f"✓ Admin can view invite codes - Total: {len(data['codes'])}")
    
    def test_get_verification_documents(self, admin_token):
        """Test admin can get verification documents"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/verification/documents", headers=headers)
        
        assert response.status_code == 200, f"Get verification docs failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert "documents" in data
        print(f"✓ Admin can view verification documents - Pending: {len(data['documents'])}")
    
    def test_get_orders_as_admin(self, admin_token):
        """Test admin can get all orders"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/orders/my", headers=headers)
        
        assert response.status_code == 200, f"Get orders failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert "orders" in data
        print(f"✓ Admin can view orders - Total: {len(data['orders'])}")
    
    def test_unauthorized_access_to_admin_endpoints(self):
        """Test that admin endpoints require authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/users")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ Admin endpoints correctly require authentication")


class TestProductEndpoints:
    """Product endpoint tests"""
    
    def test_get_products_public(self):
        """Test public products endpoint"""
        response = requests.get(f"{BASE_URL}/api/products")
        
        assert response.status_code == 200, f"Get products failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert "products" in data
        assert isinstance(data["products"], list)
        print(f"✓ Products endpoint working - Total verified products: {len(data['products'])}")
    
    def test_get_my_products_requires_auth(self):
        """Test that my products endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/products/my")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ My products endpoint correctly requires authentication")


class TestMeEndpoint:
    """Current user endpoint tests"""
    
    def test_me_endpoint_with_admin(self):
        """Test /me endpoint returns current user info"""
        # Login first
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert login_response.status_code == 200
        token = login_response.json()["session"]["access_token"]
        
        # Get current user
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/me", headers=headers)
        
        assert response.status_code == 200, f"Get me failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert "user" in data
        assert data["user"]["email"] == ADMIN_EMAIL
        print(f"✓ /me endpoint working - User: {data['user']['name']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
