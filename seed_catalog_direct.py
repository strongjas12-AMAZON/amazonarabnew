#!/usr/bin/env python3
"""
Direct script to seed the product_catalog table with 100 products.
This bypasses the API and seeds directly to Supabase.
"""
import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Add backend to path
sys.path.insert(0, '/app/backend')

# Load environment
load_dotenv('/app/backend/.env')

# Import the product catalog
from product_catalog import PRODUCT_CATALOG

# Initialize Supabase client
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("ERROR: Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in .env file")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

print(f"Connecting to Supabase: {SUPABASE_URL}")
print(f"Found {len(PRODUCT_CATALOG)} products in catalog")

# Check if already seeded
print("\nChecking if catalog is already seeded...")
try:
    existing = supabase.table('product_catalog').select('id').limit(1).execute()
    if existing.data:
        print(f"⚠️  Catalog already has products ({len(existing.data)} found)")
        response = input("Clear existing products and re-seed? (yes/no): ")
        if response.lower() != 'yes':
            print("Cancelled.")
            sys.exit(0)
        
        # Clear existing products
        print("Clearing product_catalog and store_products...")
        supabase.table('store_products').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        supabase.table('product_catalog').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        print("✅ Cleared successfully")
except Exception as e:
    print(f"Note: Could not check existing products: {e}")

# Prepare catalog items
print("\nPreparing catalog items...")
catalog_items = []
for product in PRODUCT_CATALOG:
    catalog_items.append({
        'name': product['title'],
        'description': product['description'],
        'base_price': product['price'],
        'images': product['images'],
        'category': product['category']
    })

print(f"Prepared {len(catalog_items)} items")

# Insert in batches (Supabase has limits)
batch_size = 50
total_inserted = 0

for i in range(0, len(catalog_items), batch_size):
    batch = catalog_items[i:i + batch_size]
    print(f"\nInserting batch {i//batch_size + 1} ({len(batch)} items)...")
    
    try:
        result = supabase.table('product_catalog').insert(batch).execute()
        total_inserted += len(result.data)
        print(f"✅ Inserted {len(result.data)} products")
    except Exception as e:
        print(f"❌ Error inserting batch: {e}")
        sys.exit(1)

print(f"\n🎉 SUCCESS! Seeded {total_inserted} products to product_catalog table")

# Verify
verify = supabase.table('product_catalog').select('id, name').limit(5).execute()
print(f"\nVerification - First 5 products:")
for p in verify.data:
    print(f"  - {p['name']}")
