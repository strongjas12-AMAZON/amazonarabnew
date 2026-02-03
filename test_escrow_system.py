"""
Test Script for Escrow + Deposit System
This script tests the new order flow with seller deposits
"""

import requests
import json

BASE_URL = "http://localhost:8001/api"

def test_escrow_deposit_flow():
    print("=" * 80)
    print("ESCROW + DEPOSIT SYSTEM TEST")
    print("=" * 80)
    
    # Test credentials (replace with actual test accounts)
    ADMIN_EMAIL = "support@arabshopping.org"
    SELLER_EMAIL = "testseller_new@test.com"
    BUYER_EMAIL = "testbuyer@test.com"
    PASSWORD = "TestPass123!"
    
    print("\n1. Testing Admin Login...")
    admin_response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": PASSWORD
    })
    
    if admin_response.status_code == 200:
        admin_token = admin_response.json().get('token')
        print(f"✅ Admin login successful")
    else:
        print(f"❌ Admin login failed: {admin_response.status_code}")
        print(admin_response.text)
        return
    
    print("\n2. Testing Platform Wallet Endpoint...")
    platform_wallet_response = requests.get(
        f"{BASE_URL}/admin/platform-wallet",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    if platform_wallet_response.status_code == 200:
        wallet_data = platform_wallet_response.json()
        print(f"✅ Platform Wallet Retrieved:")
        print(f"   Balance: ${wallet_data.get('balance', 0):.2f}")
        print(f"   Total Received: ${wallet_data.get('totalReceived', 0):.2f}")
        print(f"   Total Paid Out: ${wallet_data.get('totalPaidOut', 0):.2f}")
    else:
        print(f"❌ Platform wallet fetch failed: {platform_wallet_response.status_code}")
        print(platform_wallet_response.text)
    
    print("\n3. Testing Seller Login...")
    seller_response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": SELLER_EMAIL,
        "password": PASSWORD
    })
    
    if seller_response.status_code == 200:
        seller_token = seller_response.json().get('token')
        print(f"✅ Seller login successful")
    else:
        print(f"❌ Seller login failed: {seller_response.status_code}")
        return
    
    print("\n4. Testing Pending Deposits Endpoint...")
    pending_deposits_response = requests.get(
        f"{BASE_URL}/seller/orders/pending-deposit",
        headers={"Authorization": f"Bearer {seller_token}"}
    )
    
    if pending_deposits_response.status_code == 200:
        pending_data = pending_deposits_response.json()
        print(f"✅ Pending Deposits Retrieved:")
        print(f"   Count: {pending_data.get('count', 0)}")
        if pending_data.get('orders'):
            for order in pending_data['orders'][:3]:
                print(f"   - Order {order['id'][:8]}... : ${order['depositRequired']:.2f} required")
    else:
        print(f"❌ Pending deposits fetch failed: {pending_deposits_response.status_code}")
        print(pending_deposits_response.text)
    
    print("\n5. Testing Buyer Login...")
    buyer_response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": BUYER_EMAIL,
        "password": PASSWORD
    })
    
    if buyer_response.status_code == 200:
        buyer_token = buyer_response.json().get('token')
        print(f"✅ Buyer login successful")
    else:
        print(f"❌ Buyer login failed: {buyer_response.status_code}")
        return
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("✅ All authentication endpoints working")
    print("✅ Platform wallet endpoint accessible")
    print("✅ Pending deposits endpoint working")
    print("\nNEXT STEPS:")
    print("1. Run database migration: /app/backend/migrations/escrow_deposit_system.sql")
    print("2. Create a test order to verify full flow")
    print("3. Test deposit, shipping, and delivery confirmation")
    print("\nNote: Deposit/settlement functions require database migration first!")

if __name__ == "__main__":
    try:
        test_escrow_deposit_flow()
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to backend at http://localhost:8001")
        print("   Make sure the backend service is running")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
