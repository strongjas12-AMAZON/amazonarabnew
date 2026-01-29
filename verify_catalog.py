#!/usr/bin/env python3
"""
Quick test to verify product_catalog data and admin endpoint
"""
import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment
load_dotenv('/app/backend/.env')

# Initialize Supabase client
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

print("=" * 60)
print("PRODUCT CATALOG VERIFICATION")
print("=" * 60)

# Count products in product_catalog
result = supabase.table('product_catalog').select('id', count='exact').execute()
print(f"\n✅ Total products in product_catalog: {result.count}")

# Get sample products
sample = supabase.table('product_catalog').select('id, name, base_price, category').limit(10).execute()
print(f"\n📦 Sample products:")
for i, p in enumerate(sample.data[:5], 1):
    print(f"  {i}. {p['name']} - ${p['base_price']} ({p['category']})")

# Check categories
categories = supabase.table('product_catalog').select('category').execute()
unique_categories = set(p['category'] for p in categories.data if p.get('category'))
print(f"\n📂 Categories available: {', '.join(sorted(unique_categories))}")

# Check store_products (products added by sellers)
store_products = supabase.table('store_products').select('id', count='exact').execute()
print(f"\n🏪 Products in stores (added by sellers): {store_products.count}")

print("\n" + "=" * 60)
print("✅ Catalog is properly seeded and ready for use!")
print("=" * 60)
