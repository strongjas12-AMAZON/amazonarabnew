-- Supabase Database Schema for Amazon Arab Multi-Vendor Marketplace
-- Run this in Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (Note: camelCase for JSON compatibility)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('admin', 'seller', 'buyer')),
    "verificationStatus" TEXT DEFAULT 'unverified' CHECK ("verificationStatus" IN ('unverified', 'pending', 'verified', 'rejected')),
    "createdAt" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Products table
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    images TEXT[] DEFAULT '{}',
    "sellerId" UUID REFERENCES users(id) ON DELETE CASCADE,
    "createdAt" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "buyerId" UUID REFERENCES users(id) ON DELETE CASCADE,
    "totalAmount" DECIMAL(10,2) NOT NULL,
    "paymentMethod" TEXT DEFAULT 'USDT_TRON',
    "paymentWallet" TEXT NOT NULL,
    "paymentStatus" TEXT DEFAULT 'pending_payment' CHECK ("paymentStatus" IN ('pending_payment', 'paid', 'completed', 'cancelled')),
    "confirmedByAdmin" BOOLEAN DEFAULT FALSE,
    "confirmedAt" TIMESTAMP WITH TIME ZONE,
    "createdAt" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Order Items table
CREATE TABLE IF NOT EXISTS order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "orderId" UUID REFERENCES orders(id) ON DELETE CASCADE,
    "productId" UUID REFERENCES products(id),
    quantity INTEGER NOT NULL,
    price DECIMAL(10,2) NOT NULL
);

-- Verification Documents table
CREATE TABLE IF NOT EXISTS verification_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "userId" UUID REFERENCES users(id) ON DELETE CASCADE,
    "documentType" TEXT NOT NULL,
    "documentUrl" TEXT NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'verified', 'rejected')),
    "merchantInviteCode" TEXT,
    "rejectionReason" TEXT,
    "reviewedAt" TIMESTAMP WITH TIME ZONE,
    "createdAt" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Merchant Invite Codes table
CREATE TABLE IF NOT EXISTS merchant_invite_codes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code TEXT UNIQUE NOT NULL,
    "isUsed" BOOLEAN DEFAULT FALSE,
    "createdByAdmin" UUID REFERENCES users(id),
    "usedByUserId" UUID REFERENCES users(id),
    "usedAt" TIMESTAMP WITH TIME ZONE,
    "createdAt" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_products_seller ON products("sellerId");
CREATE INDEX IF NOT EXISTS idx_orders_buyer ON orders("buyerId");
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items("orderId");
CREATE INDEX IF NOT EXISTS idx_verification_user ON verification_documents("userId");
CREATE INDEX IF NOT EXISTS idx_invite_codes_code ON merchant_invite_codes(code);

-- Row Level Security (RLS) Policies

-- Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE verification_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE merchant_invite_codes ENABLE ROW LEVEL SECURITY;

-- ============================================
-- IMPORTANT: NO RECURSIVE POLICIES
-- ============================================
-- Policies NEVER check the same table they protect
-- Backend uses SERVICE_ROLE_KEY (bypasses all RLS)
-- Frontend uses ANON_KEY (subject to these policies)
-- Role validation happens in backend API layer
-- ============================================

-- Users policies
CREATE POLICY "users_select_own"
ON users FOR SELECT
TO authenticated
USING (auth.uid() = id);

CREATE POLICY "users_insert_own"
ON users FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = id);

CREATE POLICY "users_update_own"
ON users FOR UPDATE
TO authenticated
USING (auth.uid() = id)
WITH CHECK (auth.uid() = id);

-- Products policies  
CREATE POLICY "products_select_all"
ON products FOR SELECT
TO authenticated, anon
USING (true);

CREATE POLICY "products_insert_authenticated"
ON products FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = "sellerId");

CREATE POLICY "products_update_own"
ON products FOR UPDATE
TO authenticated
USING (auth.uid() = "sellerId")
WITH CHECK (auth.uid() = "sellerId");

CREATE POLICY "products_delete_own"
ON products FOR DELETE
TO authenticated
USING (auth.uid() = "sellerId");

-- Orders policies
CREATE POLICY "orders_select_own"
ON orders FOR SELECT
TO authenticated
USING (auth.uid() = "buyerId");

CREATE POLICY "orders_insert_own"
ON orders FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = "buyerId");

-- Order items policies
CREATE POLICY "order_items_select_own"
ON order_items FOR SELECT
TO authenticated
USING (
  EXISTS (
    SELECT 1 FROM orders 
    WHERE orders.id = order_items."orderId" 
    AND orders."buyerId" = auth.uid()
  )
);

CREATE POLICY "order_items_insert_own"
ON order_items FOR INSERT
TO authenticated
WITH CHECK (
  EXISTS (
    SELECT 1 FROM orders 
    WHERE orders.id = order_items."orderId" 
    AND orders."buyerId" = auth.uid()
  )
);

-- Verification documents policies
CREATE POLICY "verification_select_own"
ON verification_documents FOR SELECT
TO authenticated
USING (auth.uid() = "userId");

CREATE POLICY "verification_insert_own"
ON verification_documents FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = "userId");

-- Invite codes policies
CREATE POLICY "invite_codes_select_unused"
ON merchant_invite_codes FOR SELECT
TO authenticated, anon
USING ("isUsed" = false);

-- Storage buckets (Run separately or via Supabase Dashboard)
-- Products bucket for product images
-- Documents bucket for verification documents

-- Grant permissions to service role
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;
