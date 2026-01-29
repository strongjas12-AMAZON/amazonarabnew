-- ============================================
-- QUICK MIGRATION: Order System → Store Products
-- ============================================
-- Copy and paste this entire script into Supabase SQL Editor
-- URL: https://supabase.com/dashboard/project/dqqmzatrxmueilsxvlgb/sql

-- Step 1: Drop old foreign key constraint
ALTER TABLE order_items 
DROP CONSTRAINT IF EXISTS order_items_product_id_fkey;

-- Step 2: Add new foreign key referencing store_products
ALTER TABLE order_items 
ADD CONSTRAINT order_items_product_id_fkey 
FOREIGN KEY (product_id) 
REFERENCES store_products(id) 
ON DELETE RESTRICT;

-- Step 3: Add seller_id to orders table
ALTER TABLE orders 
ADD COLUMN IF NOT EXISTS seller_id UUID REFERENCES users(id);

-- Step 4: Create performance indexes
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_orders_seller_id ON orders(seller_id);

-- Done! Migration complete.
-- Expected result: "Success. No rows returned"
