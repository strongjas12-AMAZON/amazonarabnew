-- ============================================================================
-- QUICK FIX: Add Missing Deposit Columns
-- ============================================================================
-- Run this ENTIRE script in Supabase SQL Editor
-- This fixes BOTH the depositBalance error AND enables USDT deposit status
-- ============================================================================

-- PART 1: Fix seller_wallets table (fixes depositBalance error)
-- ============================================================================

ALTER TABLE seller_wallets
ADD COLUMN IF NOT EXISTS "depositBalance" DECIMAL(10,2) DEFAULT 0.00 CHECK ("depositBalance" >= 0);

ALTER TABLE seller_wallets
ADD COLUMN IF NOT EXISTS "withdrawableBalance" DECIMAL(10,2) DEFAULT 0.00 CHECK ("withdrawableBalance" >= 0);

UPDATE seller_wallets
SET "depositBalance" = COALESCE("depositBalance", 0.00),
    "withdrawableBalance" = COALESCE("withdrawableBalance", 0.00);


-- PART 2: Add USDT deposit columns to order_deposits table
-- ============================================================================

ALTER TABLE order_deposits 
ADD COLUMN IF NOT EXISTS deposit_method TEXT DEFAULT 'internal_wallet' CHECK (deposit_method IN ('internal_wallet', 'usdt_payment'));

ALTER TABLE order_deposits
ADD COLUMN IF NOT EXISTS transaction_hash TEXT;

ALTER TABLE order_deposits
ADD COLUMN IF NOT EXISTS deposit_status TEXT DEFAULT 'pending' CHECK (deposit_status IN ('pending', 'confirmed', 'rejected'));

ALTER TABLE order_deposits
ADD COLUMN IF NOT EXISTS payment_notes TEXT;

ALTER TABLE order_deposits
ADD COLUMN IF NOT EXISTS submitted_at TIMESTAMPTZ;

ALTER TABLE order_deposits
ADD COLUMN IF NOT EXISTS confirmed_at TIMESTAMPTZ;

ALTER TABLE order_deposits
ADD COLUMN IF NOT EXISTS confirmed_by UUID REFERENCES users(id);

ALTER TABLE order_deposits
ADD COLUMN IF NOT EXISTS rejection_reason TEXT;


-- PART 3: Create indexes for better performance
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_order_deposits_status ON order_deposits(deposit_status);
CREATE INDEX IF NOT EXISTS idx_order_deposits_method ON order_deposits(deposit_method);


-- PART 4: Update existing deposit records (mark as confirmed)
-- ============================================================================

UPDATE order_deposits 
SET deposit_method = COALESCE(deposit_method, 'internal_wallet'),
    deposit_status = CASE 
        WHEN is_deposit_complete = true THEN COALESCE(deposit_status, 'confirmed')
        ELSE COALESCE(deposit_status, 'pending')
    END
WHERE deposit_method IS NULL OR deposit_status IS NULL;


-- PART 5: Verify all columns were added successfully
-- ============================================================================

-- Check seller_wallets columns
SELECT 'seller_wallets' as table_name, column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'seller_wallets' 
AND column_name IN ('depositBalance', 'withdrawableBalance')

UNION ALL

-- Check order_deposits columns
SELECT 'order_deposits' as table_name, column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'order_deposits' 
AND column_name IN ('deposit_method', 'transaction_hash', 'deposit_status', 'payment_notes', 'submitted_at', 'confirmed_at', 'confirmed_by', 'rejection_reason')
ORDER BY table_name, column_name;


-- ============================================================================
-- ✅ MIGRATION COMPLETE!
-- ============================================================================
-- You should see output showing all the columns were added successfully.
-- Now you can:
-- 1. Use wallet balance to deposit for orders
-- 2. Submit USDT payment proof for deposits
-- 3. See "Pending Admin Approval" status after submission
-- 4. Admin can confirm/reject USDT deposits
-- ============================================================================
