-- =====================================================
-- BUYER STORE SEARCH & STORE DETAIL SYSTEM MIGRATION
-- =====================================================
-- This migration creates a proper store system with:
-- 1. product_catalog (master - buyers CANNOT access)
-- 2. stores (seller stores)
-- 3. store_products (what buyers see)
-- =====================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- 1. PRODUCT CATALOG (MASTER - SELLER/ADMIN ONLY)
-- =====================================================
CREATE TABLE IF NOT EXISTS product_catalog (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    description TEXT,
    base_price DECIMAL(10,2) NOT NULL,
    images TEXT[] DEFAULT '{}',
    category TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add column to users table for store_name if not exists
ALTER TABLE users ADD COLUMN IF NOT EXISTS store_name TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS store_status TEXT DEFAULT 'active' CHECK (store_status IN ('active', 'inactive'));

-- =====================================================
-- 2. STORES TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS stores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    seller_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    store_name TEXT NOT NULL,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(seller_id)
);

-- =====================================================
-- 3. STORE PRODUCTS (WHAT BUYERS SEE)
-- =====================================================
CREATE TABLE IF NOT EXISTS store_products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    store_id UUID NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    seller_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    catalog_product_id UUID NOT NULL REFERENCES product_catalog(id) ON DELETE CASCADE,
    price DECIMAL(10,2) NOT NULL,
    stock INTEGER DEFAULT 0,
    custom_description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- 4. INDEXES FOR PERFORMANCE
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_stores_seller_id ON stores(seller_id);
CREATE INDEX IF NOT EXISTS idx_stores_store_name ON stores(store_name);
CREATE INDEX IF NOT EXISTS idx_stores_status ON stores(status);
CREATE INDEX IF NOT EXISTS idx_store_products_store_id ON store_products(store_id);
CREATE INDEX IF NOT EXISTS idx_store_products_catalog_id ON store_products(catalog_product_id);
CREATE INDEX IF NOT EXISTS idx_store_products_seller_id ON store_products(seller_id);
CREATE INDEX IF NOT EXISTS idx_store_products_is_active ON store_products(is_active);
CREATE INDEX IF NOT EXISTS idx_product_catalog_category ON product_catalog(category);

-- =====================================================
-- 5. ROW LEVEL SECURITY POLICIES
-- =====================================================

-- Enable RLS
ALTER TABLE product_catalog ENABLE ROW LEVEL SECURITY;
ALTER TABLE stores ENABLE ROW LEVEL SECURITY;
ALTER TABLE store_products ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- PRODUCT CATALOG POLICIES (BUYERS CANNOT ACCESS)
-- =====================================================

-- Sellers can SELECT to add products to their store
DROP POLICY IF EXISTS "catalog_select_sellers" ON product_catalog;
CREATE POLICY "catalog_select_sellers" ON product_catalog 
    FOR SELECT TO authenticated 
    USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = auth.uid() 
            AND users.role = 'seller'
        )
    );

-- Admin can do everything
DROP POLICY IF EXISTS "catalog_all_admin" ON product_catalog;
CREATE POLICY "catalog_all_admin" ON product_catalog 
    FOR ALL TO authenticated 
    USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = auth.uid() 
            AND users.role = 'admin'
        )
    );

-- Service role has full access
GRANT ALL ON product_catalog TO service_role;

-- =====================================================
-- STORES POLICIES
-- =====================================================

-- Everyone can view active stores
DROP POLICY IF EXISTS "stores_select_active" ON stores;
CREATE POLICY "stores_select_active" ON stores 
    FOR SELECT TO authenticated, anon
    USING (status = 'active');

-- Sellers can manage their own stores
DROP POLICY IF EXISTS "stores_manage_own" ON stores;
CREATE POLICY "stores_manage_own" ON stores 
    FOR ALL TO authenticated 
    USING (seller_id = auth.uid());

-- Service role has full access
GRANT ALL ON stores TO service_role;

-- =====================================================
-- STORE PRODUCTS POLICIES (STRICT BUYER ACCESS)
-- =====================================================

-- Buyers can ONLY SELECT active products
DROP POLICY IF EXISTS "store_products_select_active" ON store_products;
CREATE POLICY "store_products_select_active" ON store_products 
    FOR SELECT TO authenticated, anon
    USING (is_active = true);

-- Sellers can manage their own store products
DROP POLICY IF EXISTS "store_products_manage_own" ON store_products;
CREATE POLICY "store_products_manage_own" ON store_products 
    FOR ALL TO authenticated 
    USING (seller_id = auth.uid())
    WITH CHECK (seller_id = auth.uid());

-- Service role has full access
GRANT ALL ON store_products TO service_role;

-- =====================================================
-- 6. GRANT PERMISSIONS
-- =====================================================
GRANT SELECT ON product_catalog TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON stores TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON store_products TO authenticated;
GRANT SELECT ON stores TO anon;
GRANT SELECT ON store_products TO anon;

-- =====================================================
-- 7. DATA MIGRATION
-- =====================================================

-- Create stores for existing sellers
INSERT INTO stores (seller_id, store_name, status)
SELECT 
    id as seller_id,
    COALESCE(store_name, name || '''s Store') as store_name,
    CASE 
        WHEN verification_status = 'verified' THEN 'active'
        ELSE 'inactive'
    END as status
FROM users
WHERE role = 'seller'
ON CONFLICT (seller_id) DO NOTHING;

-- Note: Existing products table remains unchanged
-- We'll handle linking existing products to store_products via API

-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================
