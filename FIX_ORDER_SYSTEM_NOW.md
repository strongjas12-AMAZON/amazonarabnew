# 🚨 URGENT FIX: Order System Foreign Key Error

## Error You're Getting
```
insert or update on table "order_items" violates foreign key constraint "order_items_product_id_fkey"
Key (product_id) is not present in table "store_products".
```

## Root Cause
The `order_items` table's foreign key is still pointing to the old `products` table, but your system now uses the new `store_products` table. This migration was never run in your Supabase database.

## ✅ Solution: Run This SQL in Supabase

### Step 1: Open Supabase SQL Editor
1. Go to: https://supabase.com/dashboard
2. Select your project: `dqqmzatrxmueilsxvlgb`
3. Click **"SQL Editor"** in the left sidebar
4. Click **"New Query"**

### Step 2: Copy and Paste This SQL

```sql
-- ============================================
-- FIX ORDER SYSTEM - UPDATE FOREIGN KEY
-- ============================================

-- Step 1: Drop the old foreign key constraint
-- This currently references the old 'products' table
ALTER TABLE order_items 
DROP CONSTRAINT IF EXISTS order_items_product_id_fkey;

-- Step 2: Add new foreign key constraint referencing store_products
-- Now order_items.product_id will reference store_products.id
ALTER TABLE order_items 
ADD CONSTRAINT order_items_product_id_fkey 
FOREIGN KEY (product_id) 
REFERENCES store_products(id) 
ON DELETE RESTRICT;

-- Step 3: Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items(product_id);

-- Step 4: Verify the fix
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

### Step 3: Click "RUN"

You should see output showing:
- First 3 commands: "Success. No rows returned"
- Last verification query: Should show `foreign_table_name = 'store_products'`

### Step 4: Test Your Order System

1. **Clear your cart**: Go to cart page and clear all items
2. **Add fresh products**: Browse products and add new items to cart
3. **Place order**: Go to checkout and place an order
4. **Verify**: 
   - Order should appear in buyer dashboard
   - Order should appear in seller's Order Center
   - No errors!

---

## Why This Happened

Your application migrated from:
- **OLD SYSTEM**: `products` table → `seller_products` table
- **NEW SYSTEM**: `product_catalog` table → `store_products` table

The frontend and backend code was updated, but the **database foreign key constraint** was not updated. This SQL fixes that final piece.

---

## ⚠️ Important Notes

1. **This is a one-time fix** - You only need to run this SQL once
2. **No data loss** - This only updates the constraint, doesn't delete any data
3. **Stale cart data** - After running the SQL, users should clear their cart and add products again
4. **Safe to run** - This SQL is safe and can be run even if the constraint is already updated

---

## Need Help?

If you see any errors when running the SQL, please share:
1. The exact error message
2. Screenshot of the SQL Editor
3. I'll help you resolve it immediately!

---

**After running this SQL, your order system will work perfectly!** ✅
