#!/usr/bin/env python3
"""
Check specific product ID in database
"""

import os
from supabase import create_client

SUPABASE_URL = "https://dqqmzatrxmueilsxvlgb.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRxcW16YXRyeG11ZWlsc3h2bGdiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjgyMjAzMywiZXhwIjoyMDgyMzk4MDMzfQ.MdWsu2dpwOQPKwlYSJ8O9KbdSh0--triMTd4azyCum4"

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

product_id = "31d5cbab-3517-494f-a63e-76aa9ad762b6"

print("=" * 60)
print(f"🔍 CHECKING PRODUCT ID: {product_id}")
print("=" * 60)

# Check in store_products
print("\n1. Checking store_products table...")
sp_result = supabase.table('store_products').select('*').eq('id', product_id).execute()
if sp_result.data:
    print(f"✅ FOUND in store_products!")
    print(f"   Data: {sp_result.data[0]}")
else:
    print(f"❌ NOT FOUND in store_products")

# Check in product_catalog
print("\n2. Checking product_catalog table...")
pc_result = supabase.table('product_catalog').select('*').eq('id', product_id).execute()
if pc_result.data:
    print(f"✅ FOUND in product_catalog!")
    print(f"   Name: {pc_result.data[0].get('name')}")
    print(f"   Price: ${pc_result.data[0].get('base_price')}")
    print(f"   Category: {pc_result.data[0].get('category')}")
else:
    print(f"❌ NOT FOUND in product_catalog")

# Check if it's a catalog_product_id in store_products
print("\n3. Checking if this ID is used as catalog_product_id...")
sp_catalog = supabase.table('store_products').select('*').eq('catalog_product_id', product_id).execute()
if sp_catalog.data:
    print(f"⚠️  This is a CATALOG ID being used by {len(sp_catalog.data)} store products:")
    for sp in sp_catalog.data:
        print(f"   Store Product ID: {sp['id']}")
        print(f"   Price: ${sp.get('price')}")
        print(f"   Seller: {sp.get('seller_id')}")
else:
    print(f"❌ Not used as catalog_product_id either")

# Check recent orders
print("\n4. Checking recent orders...")
orders = supabase.table('orders').select('id, created_at, buyer_id').order('created_at', desc=True).limit(5).execute()
if orders.data:
    print(f"✅ Found {len(orders.data)} recent orders:")
    for order in orders.data:
        print(f"   Order: {order['id'][:8]}... at {order['created_at']}")

# Check order_items with this product_id
print("\n5. Checking order_items with this product_id...")
oi = supabase.table('order_items').select('*').eq('product_id', product_id).execute()
print(f"   Found {len(oi.data) if oi.data else 0} order items with this product_id")

print("\n" + "=" * 60)
