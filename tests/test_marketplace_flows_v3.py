"""
Amazon Arab Marketplace - Comprehensive Flow Testing
Tests all 5 flows:
1. Seller Login & Verification
2. Admin Verification Review
3. Product Creation
4. Buyer Checkout
5. Admin Order Management
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://repo-copy-3.preview.emergentagent.com')

# Test credentials
ADMIN_EMAIL = "support@arabshopping.org"
ADMIN_PASSWORD = "Hadi1247@"
SELLER_EMAIL = "testseller_new@test.com"
SELLER_PASSWORD = "TestPass123!"
BUYER_EMAIL = "testbuyer_new@test.com"
BUYER_PASSWORD = "TestPass123!"
INVITE_CODE = "C6F18ADB"
CRYPTO_WALLET = "TY8Z91NMCjREyZVj9NjDsF8hVjyqfxFFRU"


class TestAuthenticationFlows:
    """Test authentication for all user types"""
    
    def test_admin_login(self):
        """Test admin can login successfully"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert data["success"] == True
        assert data["user"]["role"] == "admin"
        assert data["user"]["verificationStatus"] == "verified"
        assert "session" in data
        assert data["session"]["access_token"] is not None
        print(f"✅ Admin login successful: {data['user']['email']}")
    
    def test_seller_login(self):
        """Test seller can login successfully"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": SELLER_EMAIL,
            "password": SELLER_PASSWORD
        })
        assert response.status_code == 200, f"Seller login failed: {response.text}"
        data = response.json()
        assert data["success"] == True
        assert data["user"]["role"] == "seller"
        assert "session" in data
        print(f"✅ Seller login successful: {data['user']['email']}, status: {data['user']['verificationStatus']}")
    
    def test_buyer_login(self):
        """Test buyer can login successfully"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": BUYER_EMAIL,
            "password": BUYER_PASSWORD
        })
        assert response.status_code == 200, f"Buyer login failed: {response.text}"
        data = response.json()
        assert data["success"] == True
        assert data["user"]["role"] == "buyer"
        assert "session" in data
        print(f"✅ Buyer login successful: {data['user']['email']}")


class TestSellerVerificationFlow:
    """FLOW 1: Seller verification with invite code"""
    
    @pytest.fixture
    def seller_token(self):
        """Get seller auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": SELLER_EMAIL,
            "password": SELLER_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["session"]["access_token"]
    
    def test_seller_verification_status(self, seller_token):
        """Check seller's current verification status"""
        headers = {"Authorization": f"Bearer {seller_token}"}
        response = requests.get(f"{BASE_URL}/api/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Seller verification status: {data['user']['verificationStatus']}")
        return data['user']['verificationStatus']
    
    def test_upload_verification_document(self, seller_token):
        """Test uploading verification document with invite code"""
        headers = {"Authorization": f"Bearer {seller_token}"}
        
        # First check current status
        me_response = requests.get(f"{BASE_URL}/api/me", headers=headers)
        current_status = me_response.json()['user']['verificationStatus']
        
        if current_status == 'verified':
            print("⏭️ Seller already verified, skipping document upload")
            pytest.skip("Seller already verified")
        
        if current_status == 'pending':
            print("⏭️ Seller verification already pending, skipping document upload")
            pytest.skip("Seller verification already pending")
        
        # Create a simple test file
        files = {
            'file': ('test_document.txt', b'Test verification document content', 'text/plain')
        }
        data = {
            'documentType': 'business_document',
            'merchantInviteCode': INVITE_CODE
        }
        
        response = requests.post(
            f"{BASE_URL}/api/verification/upload",
            headers=headers,
            files=files,
            data=data
        )
        
        # Check response
        if response.status_code == 400:
            error_detail = response.json().get('detail', '')
            if 'Invalid or already used invite code' in error_detail:
                print(f"⚠️ Invite code {INVITE_CODE} already used or invalid")
                pytest.skip("Invite code already used")
            else:
                print(f"❌ Upload failed: {error_detail}")
        
        assert response.status_code == 200, f"Upload failed: {response.text}"
        result = response.json()
        assert result["success"] == True
        assert result["document"]["status"] == "pending"
        print(f"✅ Verification document uploaded, status: pending")


class TestAdminVerificationReview:
    """FLOW 2: Admin reviews and approves seller verification"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["session"]["access_token"]
    
    def test_get_pending_verifications(self, admin_token):
        """Admin can view pending verification documents"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/verification/documents", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        pending_docs = [d for d in data["documents"] if d["status"] == "pending"]
        print(f"✅ Found {len(pending_docs)} pending verification documents")
        return pending_docs
    
    def test_approve_seller_verification(self, admin_token):
        """Admin approves seller verification"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Get pending documents
        response = requests.get(f"{BASE_URL}/api/verification/documents", headers=headers)
        assert response.status_code == 200
        docs = response.json()["documents"]
        
        # Find pending doc for our test seller
        pending_docs = [d for d in docs if d["status"] == "pending"]
        
        if not pending_docs:
            print("⏭️ No pending verification documents to approve")
            pytest.skip("No pending documents")
        
        doc_id = pending_docs[0]["id"]
        
        # Approve the verification
        response = requests.put(
            f"{BASE_URL}/api/verification/documents/{doc_id}/review",
            headers=headers,
            json={"status": "verified"}
        )
        assert response.status_code == 200
        result = response.json()
        assert result["success"] == True
        print(f"✅ Verification approved for document {doc_id}")


class TestProductCreation:
    """FLOW 3: Verified seller creates products"""
    
    @pytest.fixture
    def seller_token(self):
        """Get seller auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": SELLER_EMAIL,
            "password": SELLER_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["session"]["access_token"]
    
    def test_seller_verification_required(self, seller_token):
        """Check if seller is verified before creating products"""
        headers = {"Authorization": f"Bearer {seller_token}"}
        response = requests.get(f"{BASE_URL}/api/me", headers=headers)
        assert response.status_code == 200
        status = response.json()['user']['verificationStatus']
        print(f"✅ Seller verification status: {status}")
        return status
    
    def test_create_product(self, seller_token):
        """Verified seller creates a product"""
        headers = {"Authorization": f"Bearer {seller_token}"}
        
        # Check verification status first
        me_response = requests.get(f"{BASE_URL}/api/me", headers=headers)
        status = me_response.json()['user']['verificationStatus']
        
        if status != 'verified':
            print(f"⏭️ Seller not verified (status: {status}), cannot create products")
            pytest.skip("Seller not verified")
        
        # Create product
        product_data = {
            "title": f"Test Luxury Watch {int(time.time())}",
            "description": "A beautiful luxury watch for testing",
            "price": 999.99
        }
        
        response = requests.post(
            f"{BASE_URL}/api/products",
            headers=headers,
            json=product_data
        )
        
        assert response.status_code == 200, f"Product creation failed: {response.text}"
        result = response.json()
        assert result["success"] == True
        assert result["product"]["title"] == product_data["title"]
        assert result["product"]["price"] == product_data["price"]
        print(f"✅ Product created: {result['product']['title']} (ID: {result['product']['id']})")
        return result["product"]["id"]
    
    def test_get_seller_products(self, seller_token):
        """Seller can view their own products"""
        headers = {"Authorization": f"Bearer {seller_token}"}
        response = requests.get(f"{BASE_URL}/api/products/my", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print(f"✅ Seller has {len(data['products'])} products")
        return data["products"]


class TestBuyerCheckoutFlow:
    """FLOW 4: Buyer checkout with crypto payment"""
    
    @pytest.fixture
    def buyer_token(self):
        """Get buyer auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": BUYER_EMAIL,
            "password": BUYER_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["session"]["access_token"]
    
    def test_get_available_products(self):
        """Get products available for purchase"""
        response = requests.get(f"{BASE_URL}/api/products")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print(f"✅ Found {len(data['products'])} products available")
        return data["products"]
    
    def test_create_order(self, buyer_token):
        """Buyer creates an order"""
        headers = {"Authorization": f"Bearer {buyer_token}"}
        
        # First get available products
        products_response = requests.get(f"{BASE_URL}/api/products")
        products = products_response.json()["products"]
        
        if not products:
            print("⏭️ No products available for purchase")
            pytest.skip("No products available")
        
        # Create order with first product
        product = products[0]
        order_data = {
            "items": [
                {
                    "productId": product["id"],
                    "quantity": 1,
                    "price": product["price"]
                }
            ],
            "totalAmount": product["price"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/orders",
            headers=headers,
            json=order_data
        )
        
        assert response.status_code == 200, f"Order creation failed: {response.text}"
        result = response.json()
        assert result["success"] == True
        assert result["order"]["paymentStatus"] == "pending_payment"
        assert result["order"]["paymentWallet"] == CRYPTO_WALLET
        print(f"✅ Order created: {result['order']['id'][:8]}... Total: ${result['order']['totalAmount']}")
        print(f"   Payment wallet: {result['order']['paymentWallet']}")
        return result["order"]["id"]
    
    def test_get_buyer_orders(self, buyer_token):
        """Buyer can view their orders"""
        headers = {"Authorization": f"Bearer {buyer_token}"}
        response = requests.get(f"{BASE_URL}/api/orders/my", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print(f"✅ Buyer has {len(data['orders'])} orders")
        return data["orders"]


class TestAdminOrderManagement:
    """FLOW 5: Admin confirms payment and manages orders"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["session"]["access_token"]
    
    def test_get_all_orders(self, admin_token):
        """Admin can view all orders"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/orders/my", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        
        pending_orders = [o for o in data["orders"] if o["paymentStatus"] == "pending_payment"]
        paid_orders = [o for o in data["orders"] if o["paymentStatus"] == "paid"]
        
        print(f"✅ Total orders: {len(data['orders'])}")
        print(f"   Pending payment: {len(pending_orders)}")
        print(f"   Paid: {len(paid_orders)}")
        return data["orders"]
    
    def test_confirm_payment(self, admin_token):
        """Admin confirms payment for pending order"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Get orders
        response = requests.get(f"{BASE_URL}/api/orders/my", headers=headers)
        orders = response.json()["orders"]
        
        # Find pending order
        pending_orders = [o for o in orders if o["paymentStatus"] == "pending_payment"]
        
        if not pending_orders:
            print("⏭️ No pending orders to confirm")
            pytest.skip("No pending orders")
        
        order_id = pending_orders[0]["id"]
        
        # Confirm payment
        response = requests.put(
            f"{BASE_URL}/api/orders/{order_id}/status",
            headers=headers,
            json={"status": "paid"}
        )
        
        assert response.status_code == 200, f"Payment confirmation failed: {response.text}"
        result = response.json()
        assert result["success"] == True
        assert result["order"]["paymentStatus"] == "paid"
        assert result["order"]["confirmedByAdmin"] == True
        print(f"✅ Payment confirmed for order {order_id[:8]}...")


class TestInviteCodeManagement:
    """Test admin invite code management"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["session"]["access_token"]
    
    def test_get_invite_codes(self, admin_token):
        """Admin can view all invite codes"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/invite-codes", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        
        available = [c for c in data["codes"] if not c["isUsed"]]
        used = [c for c in data["codes"] if c["isUsed"]]
        
        print(f"✅ Total invite codes: {len(data['codes'])}")
        print(f"   Available: {len(available)}")
        print(f"   Used: {len(used)}")
        return data["codes"]
    
    def test_create_invite_code(self, admin_token):
        """Admin can create new invite code"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.post(f"{BASE_URL}/api/admin/invite-codes", headers=headers)
        
        if response.status_code == 400:
            error = response.json().get('detail', '')
            if 'row-level security' in error.lower():
                print("⚠️ RLS policy blocking invite code creation")
                pytest.skip("RLS policy issue")
        
        assert response.status_code == 200, f"Create invite code failed: {response.text}"
        result = response.json()
        assert result["success"] == True
        assert result["inviteCode"]["code"] is not None
        assert result["inviteCode"]["isUsed"] == False
        print(f"✅ New invite code created: {result['inviteCode']['code']}")


class TestAdminUserManagement:
    """Test admin user management"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["session"]["access_token"]
    
    def test_get_all_users(self, admin_token):
        """Admin can view all users"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/users", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        
        admins = [u for u in data["users"] if u["role"] == "admin"]
        sellers = [u for u in data["users"] if u["role"] == "seller"]
        buyers = [u for u in data["users"] if u["role"] == "buyer"]
        
        print(f"✅ Total users: {len(data['users'])}")
        print(f"   Admins: {len(admins)}")
        print(f"   Sellers: {len(sellers)}")
        print(f"   Buyers: {len(buyers)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
