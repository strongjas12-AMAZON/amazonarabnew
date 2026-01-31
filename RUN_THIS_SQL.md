# URGENT: Run This SQL in Supabase SQL Editor

## Error You're Getting
```
Could not find the table 'public.seller_wallet_recharge_requests'
```

## Solution: Run This SQL

**Step 1**: Go to your Supabase Dashboard
- Open: https://supabase.com/dashboard
- Select your project
- Click "SQL Editor" in the left sidebar

**Step 2**: Copy and paste this SQL:

```sql
-- Create seller wallet recharge requests table
CREATE TABLE IF NOT EXISTS seller_wallet_recharge_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "sellerId" UUID NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    "paymentMethod" TEXT DEFAULT 'USDT_TRON',
    "paymentWallet" TEXT,
    "transactionHash" TEXT,
    "adminNote" TEXT,
    "createdAt" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_seller_recharge_seller_id ON seller_wallet_recharge_requests("sellerId");
CREATE INDEX IF NOT EXISTS idx_seller_recharge_status ON seller_wallet_recharge_requests(status);

-- Add comment
COMMENT ON TABLE seller_wallet_recharge_requests IS 'Seller wallet recharge requests via USDT TRC20';
```

**Step 3**: Click "RUN" button

**Step 4**: You should see "Success. No rows returned"

**Step 5**: Test the recharge feature again - it will work now!

---

## What This Creates

A database table to store seller wallet recharge requests with:
- Seller ID
- Amount
- Status (pending/approved/rejected)
- Payment method (USDT TRC20)
- Transaction hash
- Admin notes
- Timestamps

After running this SQL, the "Recharge Wallet" feature will work perfectly!
