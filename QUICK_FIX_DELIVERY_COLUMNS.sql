-- ============================================================================
-- QUICK FIX: Add Missing Delivery Confirmation Columns to Orders Table
-- ============================================================================
-- Run this in Supabase SQL Editor to fix the deliveryConfirmedAt error
-- ============================================================================

-- Add escrow and delivery tracking columns to orders table
-- ============================================================================

-- 1. Add escrowStatus column (tracks order through escrow flow)
ALTER TABLE orders 
ADD COLUMN IF NOT EXISTS escrow_status TEXT DEFAULT 'pending' 
CHECK (escrow_status IN ('pending', 'paid', 'awaiting_seller_deposit', 'deposit_received', 'shipped', 'delivered', 'settled', 'cancelled'));

-- 2. Add depositRequired column (amount seller must deposit)
ALTER TABLE orders 
ADD COLUMN IF NOT EXISTS deposit_required DECIMAL(10,2) DEFAULT 0.00;

-- 3. Add deliveryConfirmedAt column (when buyer confirmed delivery) ← THIS FIXES YOUR ERROR
ALTER TABLE orders 
ADD COLUMN IF NOT EXISTS delivery_confirmed_at TIMESTAMPTZ;

-- 4. Add autoDeliveryAt column (auto-confirm delivery timestamp)
ALTER TABLE orders 
ADD COLUMN IF NOT EXISTS auto_delivery_at TIMESTAMPTZ;

-- 5. Add settlementCompletedAt column (when settlement was completed)
ALTER TABLE orders 
ADD COLUMN IF NOT EXISTS settlement_completed_at TIMESTAMPTZ;


-- Create indexes for better query performance
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_orders_escrow_status ON orders(escrow_status);
CREATE INDEX IF NOT EXISTS idx_orders_delivery_confirmed ON orders(delivery_confirmed_at);


-- Update existing orders to have default escrow status
-- ============================================================================

UPDATE orders 
SET escrow_status = COALESCE(escrow_status, 'pending')
WHERE escrow_status IS NULL;


-- Verify all columns were added successfully
-- ============================================================================

SELECT 
    column_name, 
    data_type, 
    column_default,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'orders' 
AND column_name IN ('escrow_status', 'deposit_required', 'delivery_confirmed_at', 'auto_delivery_at', 'settlement_completed_at')
ORDER BY column_name;


-- ============================================================================
-- ✅ MIGRATION COMPLETE!
-- ============================================================================
-- You should see output showing all 5 columns were added successfully.
-- Now you can:
-- 1. Confirm delivery as a buyer (no more deliveryConfirmedAt error)
-- 2. Automatic settlement will trigger
-- 3. Track orders through complete escrow flow
-- ============================================================================
