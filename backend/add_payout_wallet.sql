-- Add wallet address field to payout_requests table
-- This allows sellers to specify where they want to receive their payout

ALTER TABLE payout_requests 
ADD COLUMN IF NOT EXISTS "payoutWallet" TEXT;

-- Add comment for documentation
COMMENT ON COLUMN payout_requests."payoutWallet" IS 'Seller wallet address (TRC20) for receiving payouts';
