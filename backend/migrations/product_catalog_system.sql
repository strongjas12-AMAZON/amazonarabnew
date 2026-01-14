-- Migration: Product Catalog System
-- Products are now admin-only managed, sellers can only select from catalog

-- 1. Create seller_products junction table (which products each seller has in their store)
CREATE TABLE IF NOT EXISTS seller_products (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    seller_id UUID REFERENCES users(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    added_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,
    UNIQUE(seller_id, product_id)
);

-- 2. Add 'is_active' column to products for admin to enable/disable products
ALTER TABLE products ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;

-- 3. Add 'created_by_admin' column to track admin-created products
ALTER TABLE products ADD COLUMN IF NOT EXISTS created_by_admin UUID REFERENCES users(id);

-- 4. Enable RLS on seller_products
ALTER TABLE seller_products ENABLE ROW LEVEL SECURITY;

-- 5. RLS Policies for seller_products
CREATE POLICY "Sellers can view their own selected products" ON seller_products
    FOR SELECT USING (auth.uid() = seller_id);

CREATE POLICY "Sellers can add products to their store" ON seller_products
    FOR INSERT WITH CHECK (auth.uid() = seller_id);

CREATE POLICY "Sellers can remove products from their store" ON seller_products
    FOR DELETE USING (auth.uid() = seller_id);

CREATE POLICY "Admins can view all seller products" ON seller_products
    FOR SELECT USING (
        EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'admin')
    );

-- 6. Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_seller_products_seller_id ON seller_products(seller_id);
CREATE INDEX IF NOT EXISTS idx_seller_products_product_id ON seller_products(product_id);
CREATE INDEX IF NOT EXISTS idx_products_is_active ON products(is_active);

-- Note: Run this SQL in Supabase SQL Editor before deploying the new backend
