-- =====================================================
-- USDT Deposit Payment System Migration
-- =====================================================
-- This migration adds support for sellers to pay deposits
-- directly via USDT TRC20 instead of only using internal wallet
-- =====================================================

-- 1. Add new columns to order_deposits table
ALTER TABLE order_deposits 
ADD COLUMN IF NOT EXISTS deposit_method TEXT DEFAULT 'internal_wallet' CHECK (deposit_method IN ('internal_wallet', 'usdt_payment')),
ADD COLUMN IF NOT EXISTS transaction_hash TEXT,
ADD COLUMN IF NOT EXISTS deposit_status TEXT DEFAULT 'pending' CHECK (deposit_status IN ('pending', 'confirmed', 'rejected')),
ADD COLUMN IF NOT EXISTS payment_notes TEXT,
ADD COLUMN IF NOT EXISTS submitted_at TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS confirmed_at TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS confirmed_by UUID REFERENCES users(id),
ADD COLUMN IF NOT EXISTS rejection_reason TEXT;

-- 2. Create index for faster queries on deposit confirmations
CREATE INDEX IF NOT EXISTS idx_order_deposits_status ON order_deposits(deposit_status);
CREATE INDEX IF NOT EXISTS idx_order_deposits_method ON order_deposits(deposit_method);

-- 3. Update existing records to use internal_wallet method
UPDATE order_deposits 
SET deposit_method = 'internal_wallet',
    deposit_status = 'confirmed'
WHERE deposit_method IS NULL 
AND is_deposit_complete = true;

-- 4. Add comment to table
COMMENT ON COLUMN order_deposits.deposit_method IS 'Method used for deposit: internal_wallet (from seller wallet) or usdt_payment (direct USDT TRC20 payment)';
COMMENT ON COLUMN order_deposits.transaction_hash IS 'USDT TRC20 transaction hash when using usdt_payment method';
COMMENT ON COLUMN order_deposits.deposit_status IS 'Status of deposit: pending (awaiting admin confirmation), confirmed (approved), rejected (denied)';

-- =====================================================
-- Migration Complete
-- =====================================================
-- After running this migration, sellers will be able to:
-- 1. Pay deposits using their internal wallet balance (existing)
-- 2. Pay deposits directly via USDT TRC20 (new alternative)
-- 
-- Admins will have new endpoints to:
-- - View pending deposit confirmations
-- - Approve or reject USDT deposit payments
-- =====================================================
