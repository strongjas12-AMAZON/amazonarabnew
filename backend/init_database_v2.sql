-- Supabase Database Schema for Amazon Arab Multi-Vendor Marketplace
-- Run this in Supabase SQL Editor
-- VERSION 2 - Fixed for Supabase compatibility

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('admin', 'seller', 'buyer')),
    verification_status TEXT DEFAULT 'unverified' CHECK (verification_status IN ('unverified', 'pending', 'verified', 'rejected')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Products table
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    images TEXT[] DEFAULT '{}',
    seller_id UUID REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    buyer_id UUID REFERENCES users(id) ON DELETE CASCADE,
    total_amount DECIMAL(10,2) NOT NULL,
    payment_method TEXT DEFAULT 'USDT_TRON',
    payment_wallet TEXT NOT NULL,
    payment_status TEXT DEFAULT 'pending_payment' CHECK (payment_status IN ('pending_payment', 'paid', 'completed', 'cancelled')),
    confirmed_by_admin BOOLEAN DEFAULT FALSE,
    confirmed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Order Items table
CREATE TABLE IF NOT EXISTS order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID REFERENCES orders(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id),
    quantity INTEGER NOT NULL,
    price DECIMAL(10,2) NOT NULL
);

-- Verification Documents table
CREATE TABLE IF NOT EXISTS verification_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    document_type TEXT NOT NULL,
    document_url TEXT NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'verified', 'rejected')),
    merchant_invite_code TEXT,
    rejection_reason TEXT,
    reviewed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Merchant Invite Codes table
CREATE TABLE IF NOT EXISTS merchant_invite_codes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code TEXT UNIQUE NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    created_by_admin UUID REFERENCES users(id),
    used_by_user_id UUID REFERENCES users(id),
    used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_products_seller ON products(seller_id);
CREATE INDEX IF NOT EXISTS idx_orders_buyer ON orders(buyer_id);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_verification_user ON verification_documents(user_id);
CREATE INDEX IF NOT EXISTS idx_invite_codes_code ON merchant_invite_codes(code);

-- Row Level Security (RLS) Policies

-- Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE verification_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE merchant_invite_codes ENABLE ROW LEVEL SECURITY;

-- Users policies
DROP POLICY IF EXISTS "users_select_own" ON users;
CREATE POLICY "users_select_own"
ON users FOR SELECT
TO authenticated
USING (auth.uid() = id);

DROP POLICY IF EXISTS "users_insert_own" ON users;
CREATE POLICY "users_insert_own"
ON users FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = id);

DROP POLICY IF EXISTS "users_update_name_only" ON users;
CREATE POLICY "users_update_name_only"
ON users FOR UPDATE
TO authenticated
USING (auth.uid() = id)
WITH CHECK (
    auth.uid() = id AND
    role = (SELECT role FROM users WHERE id = auth.uid()) AND
    verification_status = (SELECT verification_status FROM users WHERE id = auth.uid()) AND
    email = (SELECT email FROM users WHERE id = auth.uid())
);

DROP POLICY IF EXISTS "users_no_delete" ON users;
CREATE POLICY "users_no_delete"
ON users FOR DELETE
TO authenticated
USING (false);

-- Products policies  
DROP POLICY IF EXISTS "products_select_all" ON products;
CREATE POLICY "products_select_all"
ON products FOR SELECT
TO authenticated, anon
USING (true);

DROP POLICY IF EXISTS "products_insert_authenticated" ON products;
CREATE POLICY "products_insert_authenticated"
ON products FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = seller_id);

DROP POLICY IF EXISTS "products_update_own" ON products;
CREATE POLICY "products_update_own"
ON products FOR UPDATE
TO authenticated
USING (auth.uid() = seller_id)
WITH CHECK (auth.uid() = seller_id);

DROP POLICY IF EXISTS "products_delete_own" ON products;
CREATE POLICY "products_delete_own"
ON products FOR DELETE
TO authenticated
USING (auth.uid() = seller_id);

-- Orders policies
DROP POLICY IF EXISTS "orders_select_own" ON orders;
CREATE POLICY "orders_select_own"
ON orders FOR SELECT
TO authenticated
USING (auth.uid() = buyer_id);

DROP POLICY IF EXISTS "orders_insert_own" ON orders;
CREATE POLICY "orders_insert_own"
ON orders FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = buyer_id);

-- Order items policies
DROP POLICY IF EXISTS "order_items_select_own" ON order_items;
CREATE POLICY "order_items_select_own"
ON order_items FOR SELECT
TO authenticated
USING (
  EXISTS (
    SELECT 1 FROM orders 
    WHERE orders.id = order_items.order_id 
    AND orders.buyer_id = auth.uid()
  )
);

DROP POLICY IF EXISTS "order_items_insert_own" ON order_items;
CREATE POLICY "order_items_insert_own"
ON order_items FOR INSERT
TO authenticated
WITH CHECK (
  EXISTS (
    SELECT 1 FROM orders 
    WHERE orders.id = order_items.order_id 
    AND orders.buyer_id = auth.uid()
  )
);

-- Verification documents policies
DROP POLICY IF EXISTS "verification_select_own" ON verification_documents;
CREATE POLICY "verification_select_own"
ON verification_documents FOR SELECT
TO authenticated
USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "verification_insert_own" ON verification_documents;
CREATE POLICY "verification_insert_own"
ON verification_documents FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = user_id);

-- Invite codes policies
DROP POLICY IF EXISTS "invite_codes_select_unused" ON merchant_invite_codes;
CREATE POLICY "invite_codes_select_unused"
ON merchant_invite_codes FOR SELECT
TO authenticated, anon
USING (is_used = false);

-- Grant permissions to service role (backend uses this)
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;

-- Grant permissions to authenticated users
GRANT SELECT, INSERT, UPDATE, DELETE ON users TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON products TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON orders TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON order_items TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON verification_documents TO authenticated;
GRANT SELECT ON merchant_invite_codes TO authenticated;

-- Allow anon users to read products
GRANT SELECT ON products TO anon;
GRANT SELECT ON merchant_invite_codes TO anon;
