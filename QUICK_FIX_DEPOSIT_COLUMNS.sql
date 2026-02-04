-- ============================================================================
-- QUICK FIX: Add Missing Deposit Columns to seller_wallets
-- ============================================================================
-- Run this in Supabase SQL Editor to fix the depositBalance error
-- This is a minimal fix - just adds the two columns needed for deposits

-- Add depositBalance column (used for tracking deposit amounts)
ALTER TABLE seller_wallets
ADD COLUMN IF NOT EXISTS "depositBalance" DECIMAL(10,2) DEFAULT 0.00 CHECK ("depositBalance" >= 0);

-- Add withdrawableBalance column (used for tracking withdrawable amounts)
ALTER TABLE seller_wallets
ADD COLUMN IF NOT EXISTS "withdrawableBalance" DECIMAL(10,2) DEFAULT 0.00 CHECK ("withdrawableBalance" >= 0);

-- Update existing records to have default values
UPDATE seller_wallets
SET "depositBalance" = 0.00
WHERE "depositBalance" IS NULL;

UPDATE seller_wallets
SET "withdrawableBalance" = 0.00
WHERE "withdrawableBalance" IS NULL;

-- Verify the columns were added
SELECT 
    column_name, 
    data_type, 
    column_default
FROM information_schema.columns
WHERE table_name = 'seller_wallets' 
AND column_name IN ('depositBalance', 'withdrawableBalance');

-- ============================================================================
-- DONE! Your deposit system should now work.
-- ============================================================================
