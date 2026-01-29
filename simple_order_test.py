#!/usr/bin/env python3
"""
Simple Order Center Verification Test
Tests the existing Order Center functionality without creating new orders.
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "https://git-copier-1.preview.emergentagent.com/api"

# Test Credentials
SELLER_EMAIL = "testseller_new@test.com"
SELLER_PASSWORD = "TestPass123!"

def login_seller():
    """Login as seller"""
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": SELLER_EMAIL,
        "password": SELLER_PASSWORD
    })
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('session', {}).get('access_token')
        print(f"✅ Seller login successful: {data.get('user', {}).get('name')}")
        return token
    else:
        print(f"❌ Seller login failed: HTTP {response.status_code}")
        return None

def test_order_center_main(token):
    """Test main Order Center view"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/seller/order-center", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        orders = data.get('orders', [])
        counts = data.get('counts', {})
        
        print(f"✅ Order Center Main View:")
        print(f"   - Total orders: {len(orders)}")
        print(f"   - Status counts: {counts}")
        
        if orders:
            sample_order = orders[0]
            print(f"   - Sample order fields: {list(sample_order.keys())}")
            print(f"   - Order ID: {sample_order.get('id')}")
            print(f"   - Status: {sample_order.get('orderStatus')}")
            print(f"   - Payment: {sample_order.get('paymentStatus')}")
            print(f"   - Total: ${sample_order.get('totalAmount')}")
        
        return True, orders
    else:
        print(f"❌ Order Center failed: HTTP {response.status_code}")
        print(f"   Response: {response.text}")
        return False, []

def test_order_filtering(token):
    """Test order filtering by status"""
    headers = {"Authorization": f"Bearer {token}"}
    statuses = ['pending_payment', 'to_be_shipped', 'to_be_received', 'to_be_evaluated', 'after_sales', 'completed']
    
    print(f"✅ Order Status Filtering:")
    for status in statuses:
        response = requests.get(f"{BASE_URL}/seller/order-center?status={status}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            orders = data.get('orders', [])
            counts = data.get('counts', {})
            print(f"   - {status}: {len(orders)} orders (count: {counts.get(status, 0)})")
        else:
            print(f"   - {status}: ERROR HTTP {response.status_code}")

def test_ship_existing_order(token, orders):
    """Test shipping an existing order if available"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Look for an order that can be shipped (status: to_be_shipped)
    response = requests.get(f"{BASE_URL}/seller/order-center?status=to_be_shipped", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        shippable_orders = data.get('orders', [])
        
        if shippable_orders:
            order_id = shippable_orders[0]['id']
            print(f"✅ Found shippable order: {order_id}")
            
            # Try to ship it
            future_date = (datetime.now() + timedelta(days=7)).isoformat()
            shipment_data = {
                "trackingNumber": "TEST123456789",
                "courierName": "DHL Express",
                "courierCode": "dhl", 
                "estimatedDelivery": future_date
            }
            
            ship_response = requests.post(f"{BASE_URL}/seller/orders/{order_id}/ship", 
                                        headers=headers, json=shipment_data)
            
            if ship_response.status_code == 200:
                print(f"✅ Order shipped successfully")
                return True
            else:
                print(f"❌ Shipping failed: HTTP {ship_response.status_code}")
                print(f"   Response: {ship_response.text}")
                return False
        else:
            print(f"ℹ️  No orders available for shipping (status: to_be_shipped)")
            return True  # Not a failure, just no data
    else:
        print(f"❌ Failed to get shippable orders: HTTP {response.status_code}")
        return False

def test_refunds_api(token):
    """Test refunds API"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/seller/refunds", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        refunds = data.get('refunds', [])
        counts = data.get('counts', {})
        
        print(f"✅ Refunds API:")
        print(f"   - Total refunds: {len(refunds)}")
        print(f"   - Status counts: {counts}")
        return True
    else:
        print(f"❌ Refunds API failed: HTTP {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def main():
    print("=" * 60)
    print("🛒 ORDER CENTER VERIFICATION TEST")
    print("=" * 60)
    print()
    
    # Login
    token = login_seller()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    print()
    
    # Test Order Center main view
    success, orders = test_order_center_main(token)
    if not success:
        return
    
    print()
    
    # Test filtering
    test_order_filtering(token)
    
    print()
    
    # Test shipping if possible
    test_ship_existing_order(token, orders)
    
    print()
    
    # Test refunds
    test_refunds_api(token)
    
    print()
    print("=" * 60)
    print("✅ ORDER CENTER VERIFICATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()