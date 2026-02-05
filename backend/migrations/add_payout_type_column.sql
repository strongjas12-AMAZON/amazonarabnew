-- Add payoutType column to differentiate between earnings and wallet_balance payouts
-- This migration should be run in your Supabase SQL Editor

-- Add new column with default value 'earnings' for backward compatibility
ALTER TABLE payout_requests 
ADD COLUMN IF NOT EXISTS "payoutType" TEXT DEFAULT 'earnings' CHECK ("payoutType" IN ('earnings', 'wallet_balance'));

-- Create index for better query performance
CREATE INDEX IF NOT EXISTS idx_payout_requests_payout_type ON payout_requests("payoutType");

-- Update existing records to have payoutType = 'earnings' (for backward compatibility)
UPDATE payout_requests 
SET "payoutType" = 'earnings' 
WHERE "payoutType" IS NULL;

-- Verify the migration
SELECT 
    COUNT(*) as total_payouts,
    "payoutType",
    status
FROM payout_requests
GROUP BY "payoutType", status
ORDER BY "payoutType", status;
