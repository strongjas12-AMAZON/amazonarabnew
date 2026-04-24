"""
Directly insert the 200 luxury products from luxury_catalog.py into the
Supabase product_catalog table.

- Skips any products whose title already exists in product_catalog.
- Inserts in batches for reliability.
- Prints a summary at the end.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load backend .env
BACKEND_DIR = Path(__file__).parent
load_dotenv(BACKEND_DIR / ".env")

from supabase import create_client  # noqa: E402

SUPABASE_URL = os.environ["NEXT_PUBLIC_SUPABASE_URL"]
SUPABASE_SERVICE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

supabase_admin = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

from luxury_catalog import LUXURY_CATALOG  # noqa: E402


def main():
    print(f"Loaded {len(LUXURY_CATALOG)} luxury products")

    # Fetch existing product names to avoid duplicates
    existing_names = set()
    page = 0
    page_size = 1000
    while True:
        res = (
            supabase_admin
            .table("product_catalog")
            .select("name")
            .range(page * page_size, (page + 1) * page_size - 1)
            .execute()
        )
        rows = res.data or []
        for r in rows:
            if r.get("name"):
                existing_names.add(r["name"].strip().lower())
        if len(rows) < page_size:
            break
        page += 1

    print(f"Existing catalog entries: {len(existing_names)}")

    # Build items to insert (skip duplicates by title)
    new_items = []
    for product in LUXURY_CATALOG:
        if product["title"].strip().lower() in existing_names:
            continue
        new_items.append({
            "name": product["title"],
            "description": product["description"],
            "base_price": product["price"],
            "images": product["images"],
            "category": product["category"],
        })

    print(f"New products to insert: {len(new_items)}")

    if not new_items:
        print("Nothing to insert.")
        return

    # Insert in batches of 50
    batch_size = 50
    inserted_total = 0
    for i in range(0, len(new_items), batch_size):
        batch = new_items[i:i + batch_size]
        try:
            result = supabase_admin.table("product_catalog").insert(batch).execute()
            inserted_total += len(result.data or [])
            print(f"  Inserted batch {i // batch_size + 1}: {len(result.data or [])} rows")
        except Exception as e:
            print(f"  ❌ Batch {i // batch_size + 1} failed: {e}")
            # Try one-by-one as fallback
            for item in batch:
                try:
                    r = supabase_admin.table("product_catalog").insert(item).execute()
                    inserted_total += len(r.data or [])
                except Exception as ex:
                    print(f"    ⚠️  Skip '{item['name']}': {ex}")

    # Final count
    count_res = supabase_admin.table("product_catalog").select("id", count="exact").execute()
    total = count_res.count if hasattr(count_res, "count") else "?"
    print(f"\n✅ Done. Inserted {inserted_total} new products.")
    print(f"📦 product_catalog now contains ~{total} products total.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"FATAL: {e}")
        sys.exit(1)
