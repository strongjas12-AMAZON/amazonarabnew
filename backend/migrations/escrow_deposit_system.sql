-- Escrow + Seller Deposit System Migration
-- Run this in Supabase SQL Editor
-- WARNING: This adds new tables and columns - does NOT modify existing data

-- ============================================================================
-- 1. Platform Wallet - Holds all buyer payments
-- ============================================================================
CREATE TABLE IF NOT EXISTS platform_wallet (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    balance DECIMAL(12,2) DEFAULT 0.00 CHECK (balance >= 0),
    "totalReceived" DECIMAL(12,2) DEFAULT 0.00 CHECK ("totalReceived" >= 0),
    "totalPaidOut" DECIMAL(12,2) DEFAULT 0.00 CHECK ("totalPaidOut" >= 0),
    "updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "createdAt" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Initialize platform wallet if doesn't exist
INSERT INTO platform_wallet (id, balance, "totalReceived", "totalPaidOut")
VALUES ('00000000-0000-0000-0000-000000000001', 0.00, 0.00, 0.00)
ON CONFLICT (id) DO NOTHING;


-- ============================================================================
-- 2. Order Deposits - Track seller deposits per order
-- ============================================================================
CREATE TABLE IF NOT EXISTS order_deposits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "orderId" UUID REFERENCES orders(id) ON DELETE CASCADE UNIQUE NOT NULL,
    "sellerId" UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    "requiredAmount" DECIMAL(10,2) NOT NULL CHECK ("requiredAmount" > 0),
    "depositedAmount" DECIMAL(10,2) DEFAULT 0.00 CHECK ("depositedAmount" >= 0),
    "isDepositComplete" BOOLEAN DEFAULT FALSE,
    "depositedAt" TIMESTAMP WITH TIME ZONE,
    "createdAt" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


-- ============================================================================
-- 3. Platform Transactions - Track all platform money movements
-- ============================================================================
CREATE TABLE IF NOT EXISTS platform_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type TEXT NOT NULL CHECK (type IN ('buyer_payment', 'seller_payout', 'deposit_collection', 'refund')),
    amount DECIMAL(10,2) NOT NULL,
    "orderId" UUID REFERENCES orders(id) ON DELETE SET NULL,
    "userId" UUID REFERENCES users(id) ON DELETE SET NULL,
    description TEXT,
    "previousBalance" DECIMAL(10,2) NOT NULL,
    "newBalance" DECIMAL(10,2) NOT NULL,
    "createdAt" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


-- ============================================================================
-- 4. Add new status columns to orders table (ADDITIVE - keeps existing)
-- ============================================================================
ALTER TABLE orders 
ADD COLUMN IF NOT EXISTS "escrowStatus" TEXT DEFAULT 'pending' 
CHECK ("escrowStatus" IN ('pending', 'paid', 'awaiting_seller_deposit', 'deposit_received', 'shipped', 'delivered', 'settled', 'cancelled'));

ALTER TABLE orders 
ADD COLUMN IF NOT EXISTS "depositRequired" DECIMAL(10,2) DEFAULT 0.00;

ALTER TABLE orders 
ADD COLUMN IF NOT EXISTS "deliveryConfirmedAt" TIMESTAMP WITH TIME ZONE;

ALTER TABLE orders 
ADD COLUMN IF NOT EXISTS "autoDeliveryAt" TIMESTAMP WITH TIME ZONE;

ALTER TABLE orders 
ADD COLUMN IF NOT EXISTS "settlementCompletedAt" TIMESTAMP WITH TIME ZONE;


-- ============================================================================
-- 5. Seller Withdrawable Balance - Track what sellers can withdraw
-- ============================================================================
ALTER TABLE seller_wallets
ADD COLUMN IF NOT EXISTS "withdrawableBalance" DECIMAL(10,2) DEFAULT 0.00 CHECK ("withdrawableBalance" >= 0);

ALTER TABLE seller_wallets
ADD COLUMN IF NOT EXISTS "depositBalance" DECIMAL(10,2) DEFAULT 0.00 CHECK ("depositBalance" >= 0);


-- ============================================================================
-- 6. Create indexes for performance
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_order_deposits_order ON order_deposits("orderId");
CREATE INDEX IF NOT EXISTS idx_order_deposits_seller ON order_deposits("sellerId");
CREATE INDEX IF NOT EXISTS idx_order_deposits_status ON order_deposits("isDepositComplete");
CREATE INDEX IF NOT EXISTS idx_orders_escrow_status ON orders("escrowStatus");
CREATE INDEX IF NOT EXISTS idx_platform_transactions_order ON platform_transactions("orderId");
CREATE INDEX IF NOT EXISTS idx_platform_transactions_user ON platform_transactions("userId");


-- ============================================================================
-- 7. Enable RLS on new tables
-- ============================================================================
ALTER TABLE platform_wallet ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_deposits ENABLE ROW LEVEL SECURITY;
ALTER TABLE platform_transactions ENABLE ROW LEVEL SECURITY;


-- ============================================================================
-- 8. RLS Policies
-- ============================================================================

-- Platform wallet - Admin only
CREATE POLICY "platform_wallet_admin_only"
ON platform_wallet FOR ALL
TO authenticated
USING (EXISTS (
    SELECT 1 FROM users WHERE users.id = auth.uid() AND users.role = 'admin'
));

-- Order deposits - Seller can view their own
CREATE POLICY "order_deposits_seller_view_own"
ON order_deposits FOR SELECT
TO authenticated
USING ("sellerId" = auth.uid());

-- Order deposits - Admin can view all
CREATE POLICY "order_deposits_admin_view_all"
ON order_deposits FOR SELECT
TO authenticated
USING (EXISTS (
    SELECT 1 FROM users WHERE users.id = auth.uid() AND users.role = 'admin'
));

-- Platform transactions - Admin only
CREATE POLICY "platform_transactions_admin_only"
ON platform_transactions FOR SELECT
TO authenticated
USING (EXISTS (
    SELECT 1 FROM users WHERE users.id = auth.uid() AND users.role = 'admin'
));


-- ============================================================================
-- 9. Grant permissions
-- ============================================================================
GRANT SELECT, INSERT, UPDATE ON platform_wallet TO authenticated;
GRANT SELECT, INSERT, UPDATE ON order_deposits TO authenticated;
GRANT SELECT, INSERT ON platform_transactions TO authenticated;

-- Service role gets full access
GRANT ALL ON platform_wallet TO service_role;
GRANT ALL ON order_deposits TO service_role;
GRANT ALL ON platform_transactions TO service_role;


-- ============================================================================
-- 10. Helper function for settlement (atomic transaction)
-- ============================================================================
CREATE OR REPLACE FUNCTION settle_order_after_delivery(
    p_order_id UUID,
    p_seller_id UUID,
    p_order_amount DECIMAL(10,2),
    p_deposit_amount DECIMAL(10,2)
) RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_seller_wallet_id UUID;
    v_old_balance DECIMAL(10,2);
    v_new_balance DECIMAL(10,2);
    v_platform_old_balance DECIMAL(10,2);
    v_platform_new_balance DECIMAL(10,2);
BEGIN
    -- Start transaction (implicit in function)
    
    -- 1. Get seller wallet
    SELECT id, balance INTO v_seller_wallet_id, v_old_balance
    FROM seller_wallets
    WHERE "userId" = p_seller_id
    FOR UPDATE;
    
    IF v_seller_wallet_id IS NULL THEN
        RETURN jsonb_build_object('success', false, 'error', 'Seller wallet not found');
    END IF;
    
    -- 2. Check if seller has deposit amount
    IF v_old_balance < p_deposit_amount THEN
        RETURN jsonb_build_object('success', false, 'error', 'Insufficient deposit balance');
    END IF;
    
    -- 3. Credit seller with order amount, deduct deposit
    v_new_balance := v_old_balance + p_order_amount - p_deposit_amount;
    
    UPDATE seller_wallets
    SET 
        balance = v_new_balance,
        "withdrawableBalance" = COALESCE("withdrawableBalance", 0) + p_order_amount - p_deposit_amount,
        "depositBalance" = COALESCE("depositBalance", 0) - p_deposit_amount,
        "updatedAt" = NOW()
    WHERE id = v_seller_wallet_id;
    
    -- 4. Record seller payout transaction
    INSERT INTO wallet_transactions (
        "userId", "userRole", type, amount, "previousBalance", "newBalance", "orderId", description
    ) VALUES (
        p_seller_id, 'seller', 'earning', p_order_amount, v_old_balance, v_new_balance, p_order_id,
        'Order payout after delivery confirmation'
    );
    
    -- 5. Record deposit deduction
    INSERT INTO wallet_transactions (
        "userId", "userRole", type, amount, "previousBalance", "newBalance", "orderId", description
    ) VALUES (
        p_seller_id, 'seller', 'withdrawal', p_deposit_amount, v_new_balance, v_new_balance, p_order_id,
        'Deposit deduction for completed order'
    );
    
    -- 6. Update platform wallet
    SELECT balance INTO v_platform_old_balance
    FROM platform_wallet
    WHERE id = '00000000-0000-0000-0000-000000000001'
    FOR UPDATE;
    
    v_platform_new_balance := v_platform_old_balance + p_deposit_amount;
    
    UPDATE platform_wallet
    SET 
        balance = v_platform_new_balance,
        "totalPaidOut" = COALESCE("totalPaidOut", 0) + p_order_amount,
        "updatedAt" = NOW()
    WHERE id = '00000000-0000-0000-0000-000000000001';
    
    -- 7. Record platform transaction
    INSERT INTO platform_transactions (
        type, amount, "orderId", "userId", description, "previousBalance", "newBalance"
    ) VALUES (
        'deposit_collection', p_deposit_amount, p_order_id, p_seller_id,
        'Deposit collected from seller after delivery',
        v_platform_old_balance, v_platform_new_balance
    );
    
    -- 8. Update order
    UPDATE orders
    SET 
        "escrowStatus" = 'settled',
        "settlementCompletedAt" = NOW()
    WHERE id = p_order_id;
    
    -- 9. Mark deposit as complete
    UPDATE order_deposits
    SET "isDepositComplete" = TRUE
    WHERE "orderId" = p_order_id;
    
    RETURN jsonb_build_object(
        'success', true,
        'sellerNetProfit', p_order_amount - p_deposit_amount,
        'platformProfit', p_deposit_amount,
        'sellerNewBalance', v_new_balance
    );
    
EXCEPTION WHEN OTHERS THEN
    RETURN jsonb_build_object('success', false, 'error', SQLERRM);
END;
$$;


-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================
-- This migration is safe and additive - it does not modify existing data
-- All new columns have defaults and are nullable where appropriate
-- Existing order flows remain completely intact
