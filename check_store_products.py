#!/usr/bin/env python3
"""
Check Store Products Table - Diagnostic Script
This script checks what products exist in store_products table
"""

import os
from supabase import create_client

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("❌ ERROR: Supabase credentials not found in environment")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

print("=" * 60)
print("🔍 CHECKING STORE_PRODUCTS TABLE")
print("=" * 60)

try:
    # Check store_products
    result = supabase.table('store_products').select('id, price, stock_quantity, is_active, catalog_product_id, seller_id').eq('is_active', True).limit(10).execute()
    
    if result.data:
        print(f"\n✅ Found {len(result.data)} active products in store_products table")
        print("\nSample Products:")
        print("-" * 60)
        for idx, product in enumerate(result.data[:5], 1):
            print(f"{idx}. Product ID: {product['id']}")
            print(f"   Price: ${product['price']}")
            print(f"   Stock: {product['stock_quantity']}")
            print(f"   Catalog ID: {product['catalog_product_id']}")
            print(f"   Seller ID: {product['seller_id'][:8]}...")
            print()
    else:
        print("\n⚠️  WARNING: No active products found in store_products table")
        print("   Sellers need to add products to their stores first!")
        print("\n   Steps to fix:")
        print("   1. Login as seller")
        print("   2. Go to Seller Dashboard")
        print("   3. Browse product catalog")
        print("   4. Add products to your store")
    
    # Count total products
    count_result = supabase.table('store_products').select('id', count='exact').eq('is_active', True).execute()
    print(f"\n📊 Total active store products: {count_result.count}")
    
    # Check product_catalog
    catalog_result = supabase.table('product_catalog').select('id', count='exact').execute()
    print(f"📦 Total products in catalog: {catalog_result.count}")
    
    print("\n" + "=" * 60)
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    print("\nThis might mean:")
    print("1. store_products table doesn't exist")
    print("2. Database connection issue")
    print("3. Need to run migrations")
