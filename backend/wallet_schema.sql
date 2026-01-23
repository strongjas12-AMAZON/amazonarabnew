-- Wallet System Schema for Multi-Vendor Marketplace
-- Run this in Supabase SQL Editor after init_database.sql

-- Buyer Wallets table
CREATE TABLE IF NOT EXISTS buyer_wallets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "userId" UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE NOT NULL,
    balance DECIMAL(10,2) DEFAULT 0.00 CHECK (balance >= 0),
    "createdAt" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Seller Wallets table
CREATE TABLE IF NOT EXISTS seller_wallets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "userId" UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE NOT NULL,
    balance DECIMAL(10,2) DEFAULT 0.00 CHECK (balance >= 0),
    "totalEarnings" DECIMAL(10,2) DEFAULT 0.00 CHECK ("totalEarnings" >= 0),
    "createdAt" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Wallet Transactions table (for both buyer and seller)
CREATE TABLE IF NOT EXISTS wallet_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "userId" UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    "userRole" TEXT NOT NULL CHECK ("userRole" IN ('buyer', 'seller')),
    type TEXT NOT NULL CHECK (type IN ('recharge', 'purchase', 'refund', 'earning', 'withdrawal', 'payout')),
    amount DECIMAL(10,2) NOT NULL,
    "previousBalance" DECIMAL(10,2) NOT NULL,
    "newBalance" DECIMAL(10,2) NOT NULL,
    "orderId" UUID REFERENCES orders(id) ON DELETE SET NULL,
    "rechargeRequestId" UUID,
    "payoutRequestId" UUID REFERENCES payout_requests(id) ON DELETE SET NULL,
    description TEXT,
    "createdAt" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Wallet Recharge Requests table (buyer recharge requests requiring admin approval)
CREATE TABLE IF NOT EXISTS wallet_recharge_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "buyerId" UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    amount DECIMAL(10,2) NOT NULL CHECK (amount > 0),
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    "paymentMethod" TEXT DEFAULT 'USDT_TRON',
    "paymentWallet" TEXT,
    "adminId" UUID REFERENCES users(id),
    "adminActionTimestamp" TIMESTAMP WITH TIME ZONE,
    "adminNote" TEXT,
    "createdAt" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_buyer_wallets_user ON buyer_wallets("userId");
CREATE INDEX IF NOT EXISTS idx_seller_wallets_user ON seller_wallets("userId");
CREATE INDEX IF NOT EXISTS idx_wallet_transactions_user ON wallet_transactions("userId");
CREATE INDEX IF NOT EXISTS idx_wallet_transactions_order ON wallet_transactions("orderId");
CREATE INDEX IF NOT EXISTS idx_wallet_recharge_requests_buyer ON wallet_recharge_requests("buyerId");
CREATE INDEX IF NOT EXISTS idx_wallet_recharge_requests_status ON wallet_recharge_requests(status);

-- Enable RLS
ALTER TABLE buyer_wallets ENABLE ROW LEVEL SECURITY;
ALTER TABLE seller_wallets ENABLE ROW LEVEL SECURITY;
ALTER TABLE wallet_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE wallet_recharge_requests ENABLE ROW LEVEL SECURITY;

-- RLS Policies for buyer_wallets
CREATE POLICY "buyer_wallets_select_own"
ON buyer_wallets FOR SELECT
TO authenticated
USING (auth.uid() = "userId");

-- RLS Policies for seller_wallets
CREATE POLICY "seller_wallets_select_own"
ON seller_wallets FOR SELECT
TO authenticated
USING (auth.uid() = "userId");

-- RLS Policies for wallet_transactions
CREATE POLICY "wallet_transactions_select_own"
ON wallet_transactions FOR SELECT
TO authenticated
USING (auth.uid() = "userId");

-- RLS Policies for wallet_recharge_requests
CREATE POLICY "wallet_recharge_requests_select_own"
ON wallet_recharge_requests FOR SELECT
TO authenticated
USING (auth.uid() = "buyerId");

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON buyer_wallets TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON seller_wallets TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON wallet_transactions TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON wallet_recharge_requests TO authenticated;

-- Grant permissions to service role
GRANT ALL ON buyer_wallets TO service_role;
GRANT ALL ON seller_wallets TO service_role;
GRANT ALL ON wallet_transactions TO service_role;
GRANT ALL ON wallet_recharge_requests TO service_role;

