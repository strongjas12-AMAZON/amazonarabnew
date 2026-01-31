# Payout Wallet Address Update

## Summary
Updated seller payout system to require USDT TRC20 wallet address before submitting payout requests.

## Changes Made

### Backend (`/app/backend/server.py`)
1. **Made wallet address required**: Changed `payoutWallet` from `Optional[str]` to `str` in `CreatePayoutRequest` model
2. **Added validation**:
   - Wallet address cannot be empty
   - Must be valid TRC20 address (starts with 'T', exactly 34 characters)
   - Provides clear error messages for invalid addresses

### Frontend (`/app/frontend/src/pages/dashboard/SellerDashboard.js`)
1. **Enhanced form validation**:
   - Added HTML5 validation attributes (minLength, maxLength, pattern, required)
   - Clear placeholder text explaining format requirements
   - Added visual indicator (*) for required field
   - Added help text below input field
2. **Added information box**: 
   - Prominent blue notice box explaining TRC20 wallet requirements
   - Uses Wallet icon for visual clarity
3. **Updated payout history table**:
   - Added "Wallet Address" column to show where payouts were sent
   - Displays wallet addresses in monospace font for readability

## Database Migration Required

**IMPORTANT**: Before testing, run this SQL in Supabase SQL Editor:

```sql
-- Add wallet address field to payout_requests table
ALTER TABLE payout_requests 
ADD COLUMN IF NOT EXISTS "payoutWallet" TEXT;

-- Add comment for documentation
COMMENT ON COLUMN payout_requests."payoutWallet" IS 'Seller wallet address (TRC20) for receiving payouts';
```

This migration is also available in `/app/backend/add_payout_wallet.sql`

## Testing Checklist

### 1. Verify Database Migration
- [ ] Run the SQL migration in Supabase SQL Editor
- [ ] Confirm `payoutWallet` column exists in `payout_requests` table

### 2. Test Payout Request Form
- [ ] Login as a verified seller with available balance
- [ ] Navigate to Seller Dashboard → Payouts tab
- [ ] Try submitting without wallet address (should show validation error)
- [ ] Try submitting with invalid wallet (e.g., not starting with 'T')
- [ ] Try submitting with wallet that's too short/long
- [ ] Submit valid payout request with proper TRC20 address (34 chars, starts with 'T')

### 3. Verify Display
- [ ] Check that wallet address appears in payout history table
- [ ] Verify information box is clearly visible above the form
- [ ] Confirm help text appears below wallet input field

## Example Valid TRC20 Address
```
TYourWalletAddressHere1234567890
```
(Must be exactly 34 characters and start with 'T')

## Error Messages
- Missing wallet: "USDT TRC20 wallet address is required"
- Invalid format: "Invalid USDT TRC20 wallet address. Must start with 'T' and be 34 characters long"
- Amount too high: "Requested amount exceeds available balance"

## Features
✅ Sellers must provide USDT TRC20 wallet address
✅ Frontend validation prevents submission of invalid addresses
✅ Backend validation ensures data integrity
✅ Wallet addresses displayed in payout history
✅ Clear error messages guide sellers
✅ Visual indicators (*, help text, info box) improve UX
