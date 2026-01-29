#!/usr/bin/env python3
"""
Check stores table and seller accounts
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv('/app/backend/.env')

SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

print("=" * 60)
print("STORES AND SELLERS CHECK")
print("=" * 60)

# Check sellers
sellers = supabase.table('users').select('id, email, name, role, verification_status, store_name').eq('role', 'seller').execute()
print(f"\n📊 Total Sellers: {len(sellers.data)}")
for seller in sellers.data[:5]:
    print(f"  - {seller.get('email')} | Status: {seller.get('verification_status')} | Store: {seller.get('store_name', 'N/A')}")

# Check stores table
stores = supabase.table('stores').select('id, seller_id, store_name, status').execute()
print(f"\n🏪 Total Stores: {len(stores.data)}")
for store in stores.data[:5]:
    print(f"  - Store: {store.get('store_name')} | Seller: {store.get('seller_id')[:8]}... | Status: {store.get('status')}")

# Check for sellers without stores
sellers_with_stores = set(s['seller_id'] for s in stores.data)
sellers_without_stores = [s for s in sellers.data if s['id'] not in sellers_with_stores]

if sellers_without_stores:
    print(f"\n⚠️  Sellers WITHOUT stores: {len(sellers_without_stores)}")
    for seller in sellers_without_stores[:3]:
        print(f"  - {seller.get('email')} (ID: {seller['id'][:8]}...)")
else:
    print(f"\n✅ All sellers have stores")

print("\n" + "=" * 60)
