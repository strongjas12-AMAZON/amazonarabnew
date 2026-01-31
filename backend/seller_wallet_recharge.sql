-- Create seller wallet recharge requests table
CREATE TABLE IF NOT EXISTS seller_wallet_recharge_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "sellerId" UUID NOT NULL REFERENCES users(id),
    amount DECIMAL(10,2) NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    "paymentMethod" TEXT DEFAULT 'USDT_TRON',
    "paymentWallet" TEXT,
    "transactionHash" TEXT,
    "adminNote" TEXT,
    "createdAt" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_seller_recharge_seller_id ON seller_wallet_recharge_requests("sellerId");
CREATE INDEX IF NOT EXISTS idx_seller_recharge_status ON seller_wallet_recharge_requests(status);

-- Add RLS policies
ALTER TABLE seller_wallet_recharge_requests ENABLE ROW LEVEL SECURITY;

-- Sellers can view their own recharge requests
CREATE POLICY seller_view_own_recharges ON seller_wallet_recharge_requests
    FOR SELECT
    USING (auth.uid() = "sellerId");

-- Sellers can insert their own recharge requests
CREATE POLICY seller_insert_own_recharges ON seller_wallet_recharge_requests
    FOR INSERT
    WITH CHECK (auth.uid() = "sellerId");

-- Comment
COMMENT ON TABLE seller_wallet_recharge_requests IS 'Seller wallet recharge requests via USDT TRC20';
