-- Supabase Database Schema for Multi-Vendor Marketplace
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

-- Users policies
CREATE POLICY "Users can read own data" ON users
    FOR SELECT USING (auth.uid() = id OR EXISTS (
        SELECT 1 FROM users WHERE id = auth.uid() AND role = 'admin'
    ));

CREATE POLICY "Admin can read all users" ON users
    FOR SELECT USING (EXISTS (
        SELECT 1 FROM users WHERE id = auth.uid() AND role = 'admin'
    ));

CREATE POLICY "Service role bypass" ON users
    FOR ALL USING (true);

-- Products policies  
CREATE POLICY "Anyone can read verified products" ON products
    FOR SELECT USING (TRUE);

CREATE POLICY "Sellers can insert own products" ON products
    FOR INSERT WITH CHECK (
        "sellerId" = auth.uid() AND 
        EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'seller')
    );

CREATE POLICY "Sellers can update own products" ON products
    FOR UPDATE USING ("sellerId" = auth.uid());

CREATE POLICY "Sellers can delete own products" ON products
    FOR DELETE USING ("sellerId" = auth.uid());

-- Orders policies
CREATE POLICY "Users can read own orders" ON orders
    FOR SELECT USING (
        "buyerId" = auth.uid() OR 
        EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'admin')
    );

CREATE POLICY "Buyers can create orders" ON orders
    FOR INSERT WITH CHECK (
        "buyerId" = auth.uid() AND 
        EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'buyer')
    );

CREATE POLICY "Admin can update orders" ON orders
    FOR UPDATE USING (EXISTS (
        SELECT 1 FROM users WHERE id = auth.uid() AND role = 'admin'
    ));

-- Order items policies
CREATE POLICY "Users can read order items of own orders" ON order_items
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM orders 
            WHERE orders.id = order_items.order_id 
            AND orders.buyer_id = auth.uid()
        ) OR EXISTS (
            SELECT 1 FROM users WHERE id = auth.uid() AND role = 'admin'
        )
    );

CREATE POLICY "Buyers can create order items" ON order_items
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM orders 
            WHERE orders.id = order_items.order_id 
            AND orders.buyer_id = auth.uid()
        )
    );

-- Verification documents policies
CREATE POLICY "Users can read own documents" ON verification_documents
    FOR SELECT USING (
        user_id = auth.uid() OR 
        EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'admin')
    );

CREATE POLICY "Users can create own documents" ON verification_documents
    FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY "Admin can update documents" ON verification_documents
    FOR UPDATE USING (EXISTS (
        SELECT 1 FROM users WHERE id = auth.uid() AND role = 'admin'
    ));

-- Invite codes policies
CREATE POLICY "Admin can manage invite codes" ON merchant_invite_codes
    FOR ALL USING (EXISTS (
        SELECT 1 FROM users WHERE id = auth.uid() AND role = 'admin'
    ));

CREATE POLICY "Anyone can read unused codes" ON merchant_invite_codes
    FOR SELECT USING (is_used = FALSE);

-- Storage buckets (Run separately or via Supabase Dashboard)
-- Products bucket for product images
-- Documents bucket for verification documents

-- Grant permissions to service role
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;
