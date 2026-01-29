# Order System Migration Guide - NEW Store Products System

## Overview
This migration updates the order system to work exclusively with the **NEW store_products system** instead of the old products table.

---

## What This Migration Does

### Database Changes
1. **Drops** old foreign key: `order_items.product_id` → `products.id`
2. **Creates** new foreign key: `order_items.product_id` → `store_products.id`
3. **Adds** `seller_id` column to `orders` table for multi-seller support
4. **Creates** indexes for better query performance

### Backend Changes (Already Applied)
- ✅ Order Center endpoints updated to query `store_products`
- ✅ Ship order endpoint updated to verify `store_products`
- ✅ Product catalog and seller endpoints using `store_products`

---

## Migration Steps

### Step 1: Backup Your Data (IMPORTANT!)
Before proceeding, ensure you have a backup of your Supabase database.

### Step 2: Run the Migration SQL

**Option A: Using Supabase Dashboard (Recommended)**

1. Go to Supabase SQL Editor:
   ```
   https://supabase.com/dashboard/project/dqqmzatrxmueilsxvlgb/sql
   ```

2. Copy the SQL from this file:
   ```
   /app/backend/migrations/order_system_migration_to_store_products.sql
   ```

3. Paste into SQL Editor and click "Run"

4. Verify success - you should see:
   ```
   Success. No rows returned
   ```

**Option B: Using Migration Script**

Run the Python helper script:
```bash
python3 /app/migrate_order_system.py
```

This script will:
- Check current database state
- Guide you through manual SQL execution
- Verify migration success

### Step 3: Verify Migration

Run this SQL in Supabase to verify the constraint is updated:

```sql
SELECT 
  tc.constraint_name, 
  tc.table_name, 
  kcu.column_name, 
  ccu.table_name AS foreign_table_name,
  ccu.column_name AS foreign_column_name 
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
WHERE tc.table_name = 'order_items' 
  AND tc.constraint_type = 'FOREIGN KEY'
  AND kcu.column_name = 'product_id';
```

**Expected Result:**
- `foreign_table_name` should be `store_products` (not `products`)

---

## Testing After Migration

### Test 1: Seller Adds Products
```bash
1. Login as seller
2. Browse catalog (GET /api/seller/catalog/products)
3. Add product to store (POST /api/seller/store/products)
4. Verify product appears in store
```

### Test 2: Buyer Creates Order
```bash
1. Login as buyer
2. View products (GET /api/products)
3. Create order with store_product IDs
4. Verify order created successfully
```

### Test 3: Seller Order Center
```bash
1. Login as seller
2. View Order Center (GET /api/seller/order-center)
3. Verify orders appear correctly
4. Ship an order (POST /api/seller/orders/{id}/ship)
5. Verify shipment created
```

### Test 4: Complete Order Flow
```bash
Buyer: Browse products → Add to cart → Checkout
Admin: Confirm payment
Seller: View in Order Center → Ship order
Buyer: Track shipment → Confirm delivery
```

---

## What Happens to Existing Orders?

### If You Have Existing Orders (Before Migration)

**Scenario 1: Orders reference old 'products' table**
- These orders will become **orphaned** after migration
- Foreign key will break the link
- **Recommendation**: Archive old orders or manually migrate them

**Scenario 2: No existing orders**
- ✅ Clean migration, no issues

### Migration Strategy for Existing Orders

If you have important existing orders that must be preserved:

1. **Option A**: Keep old orders unchanged
   - Old orders stay linked to `products` table
   - New orders use `store_products` table
   - Requires keeping both tables

2. **Option B**: Migrate old orders (Complex)
   - Map old product IDs to new store_product IDs
   - Update order_items records
   - More complex but cleaner

**For this marketplace, we recommend Option A** since the migration is being done early in development.

---

## Troubleshooting

### Error: Foreign key constraint violation
**Problem**: Trying to create order with invalid product_id  
**Solution**: Ensure product_id references a valid store_products.id

### Error: Seller can't see orders
**Problem**: Orders not linked to seller correctly  
**Solution**: Ensure orders.seller_id is set when order is created/confirmed

### Error: Product info not showing in Order Center
**Problem**: Join query failing  
**Solution**: Verify store_products has corresponding product_catalog entries

---

## Rollback (If Needed)

If you need to revert this migration:

```sql
-- Restore old foreign key
ALTER TABLE order_items DROP CONSTRAINT IF EXISTS order_items_product_id_fkey;
ALTER TABLE order_items ADD CONSTRAINT order_items_product_id_fkey 
  FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT;

-- Remove new columns
ALTER TABLE orders DROP COLUMN IF EXISTS seller_id;

-- Remove indexes
DROP INDEX IF EXISTS idx_order_items_product_id;
DROP INDEX IF EXISTS idx_orders_seller_id;
```

---

## Summary

After this migration:
- ✅ Orders use NEW `store_products` system exclusively
- ✅ Sellers can view orders in Order Center
- ✅ Complete order flow works end-to-end
- ✅ Multi-seller support enabled
- ✅ Clean, consistent data model

**Total Downtime**: ~2 minutes (during SQL execution)

**Risk Level**: Low (if no existing orders) / Medium (if existing orders)

---

## Files Created

1. `/app/backend/migrations/order_system_migration_to_store_products.sql` - Migration SQL
2. `/app/migrate_order_system.py` - Migration helper script
3. `/app/ORDER_MIGRATION_GUIDE.md` - This guide

---

## Support

If you encounter issues during migration:
1. Check Supabase logs for detailed error messages
2. Verify all tables exist: orders, order_items, store_products, product_catalog
3. Ensure store_products table has data (from sellers adding products)
4. Contact support with error details if needed
