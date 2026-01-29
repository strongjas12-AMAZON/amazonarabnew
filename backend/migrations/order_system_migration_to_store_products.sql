-- ============================================
-- ORDER SYSTEM MIGRATION TO NEW STORE SYSTEM
-- ============================================
-- This migration updates the order system to work with the NEW store_products system
-- instead of the old products table

-- Step 1: Check existing orders (informational)
-- SELECT COUNT(*) as total_orders FROM orders;
-- SELECT COUNT(*) as total_order_items FROM order_items;

-- Step 2: Drop the old foreign key constraint on order_items.product_id
-- This constraint currently references the 'products' table
ALTER TABLE order_items 
DROP CONSTRAINT IF EXISTS order_items_product_id_fkey;

-- Step 3: Add new foreign key constraint referencing store_products
-- Now order_items.product_id will reference store_products.id
ALTER TABLE order_items 
ADD CONSTRAINT order_items_product_id_fkey 
FOREIGN KEY (product_id) 
REFERENCES store_products(id) 
ON DELETE RESTRICT;

-- Step 4: Add seller_id to orders table if not exists (to track which seller the order belongs to)
-- This helps with multi-seller order management
ALTER TABLE orders 
ADD COLUMN IF NOT EXISTS seller_id UUID REFERENCES users(id);

-- Step 5: Create index for better query performance
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_orders_seller_id ON orders(seller_id);

-- Step 6: Update existing order_items to map to store_products (if any exist)
-- Note: This step may fail if there are existing orders with products not in store_products
-- In that case, you may need to manually handle existing orders

-- Optional: Add comment to document the change
COMMENT ON CONSTRAINT order_items_product_id_fkey ON order_items IS 
'References store_products table in NEW store system (migrated from products table)';

-- ============================================
-- VERIFICATION QUERIES (Run these after migration)
-- ============================================

-- Check constraint is updated
-- SELECT 
--   tc.constraint_name, 
--   tc.table_name, 
--   kcu.column_name, 
--   ccu.table_name AS foreign_table_name,
--   ccu.column_name AS foreign_column_name 
-- FROM information_schema.table_constraints AS tc 
-- JOIN information_schema.key_column_usage AS kcu
--   ON tc.constraint_name = kcu.constraint_name
-- JOIN information_schema.constraint_column_usage AS ccu
--   ON ccu.constraint_name = tc.constraint_name
-- WHERE tc.table_name = 'order_items' 
--   AND tc.constraint_type = 'FOREIGN KEY'
--   AND kcu.column_name = 'product_id';

-- Expected result: foreign_table_name should be 'store_products'

-- ============================================
-- ROLLBACK SCRIPT (In case you need to revert)
-- ============================================

-- To rollback this migration:
-- ALTER TABLE order_items DROP CONSTRAINT IF EXISTS order_items_product_id_fkey;
-- ALTER TABLE order_items ADD CONSTRAINT order_items_product_id_fkey 
--   FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT;
-- DROP INDEX IF EXISTS idx_order_items_product_id;
-- DROP INDEX IF EXISTS idx_orders_seller_id;
-- ALTER TABLE orders DROP COLUMN IF EXISTS seller_id;
