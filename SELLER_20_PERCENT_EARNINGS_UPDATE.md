# Seller 20% Earnings & Wallet Withdrawal System

## 🎯 Overview

This document describes the implementation of the **20% seller earnings system** and the **wallet balance withdrawal feature**.

### Key Changes:
1. **Sellers now earn 20% of each order** (instead of 100%)
2. **20% earnings are added to BOTH**:
   - `totalEarnings` (for tracking total revenue)
   - `balance` (for immediate withdrawal)
3. **New wallet balance withdrawal feature** - sellers can withdraw their wallet balance at any time
4. **Separate payout systems**: 
   - Earnings payout (traditional)
   - Wallet balance withdrawal (new)

---

## 📊 How It Works

### Order Completion Flow:
When an order is marked as **completed** by admin:

1. **Calculate 20% earnings**: 
   ```javascript
   full_amount = price × quantity
   seller_earnings = full_amount × 0.20  // 20% commission
   ```

2. **Update seller wallet**:
   - Add 20% to `totalEarnings` (cumulative tracking)
   - Add 20% to `balance` (withdrawable amount)
   - Both fields increase by the same amount

3. **Create transaction record**:
   - Type: "earning"
   - Description: "20% earnings from order"
   - Updates wallet balance

### Example:
- Order total: **$100**
- Seller earnings: **$20** (20%)
- Added to `totalEarnings`: **+$20**
- Added to `balance`: **+$20**
- Seller can immediately withdraw this $20

---

## 🔧 Backend Changes

### 1. Order Completion (server.py line ~2698)
```python
# Calculate 20% of the order amount as seller earnings
full_amount = float(item.get('price', 0)) * int(item.get('quantity', 0))
earnings = full_amount * 0.20  # 20% commission
```

### 2. Wallet Update (server.py line ~2720)
```python
# Add 20% earnings to BOTH totalEarnings AND balance
new_balance = current_balance + earnings_amount
new_total_earnings = current_total_earnings + earnings_amount

wallet_update = {
    'balance': new_balance,  # Can be withdrawn
    'totalEarnings': new_total_earnings,  # Tracking
    'updatedAt': datetime.now(timezone.utc).isoformat()
}
```

### 3. Earnings Calculation (server.py line ~2140)
```python
# Sellers earn 20% of each order amount
full_amount = float(item.get("price", 0)) * int(item.get("quantity", 0))
total_earnings += full_amount * 0.20  # 20% commission
```

### 4. New Endpoints

#### POST `/seller/wallet/payout-requests`
Create a wallet balance withdrawal request.

**Request:**
```json
{
  "requestedAmount": 50.00,
  "payoutWallet": "TY8Z91NMCjREyZVj9NjDsF8hVjyqfxFFRU"
}
```

**Response:**
```json
{
  "success": true,
  "payoutRequest": {
    "id": "uuid",
    "requestedAmount": 50.00,
    "status": "pending",
    "payoutWallet": "TY8Z91NMCjREyZVj9NjDsF8hVjyqfxFFRU",
    "payoutType": "wallet_balance"
  }
}
```

#### GET `/seller/wallet/payout-requests`
Get wallet balance payout history.

**Response:**
```json
{
  "success": true,
  "payoutRequests": [
    {
      "id": "uuid",
      "requestedAmount": 50.00,
      "status": "pending",
      "payoutWallet": "TY8Z91NMCjREyZVj9NjDsF8hVjyqfxFFRU",
      "requestDate": "2025-02-05T10:00:00Z"
    }
  ]
}
```

### 5. Database Changes

**New Column**: `payoutType` in `payout_requests` table

```sql
ALTER TABLE payout_requests 
ADD COLUMN IF NOT EXISTS "payoutType" TEXT DEFAULT 'earnings' 
CHECK ("payoutType" IN ('earnings', 'wallet_balance'));
```

**Values**:
- `earnings`: Traditional earnings payout
- `wallet_balance`: Wallet balance withdrawal

---

## 🎨 Frontend Changes

### SellerDashboard - Payouts Tab

#### New Section: "Wallet Balance Withdrawal"

Located below the existing "Payouts & Earnings" section.

**Features**:
1. **Wallet Balance Display**:
   - Shows available wallet balance
   - Shows total recharged amount
   - Note: "Includes 20% earnings from completed orders + recharges"

2. **Withdrawal Form**:
   - Amount input
   - USDT TRC20 wallet address input (34 chars, starts with 'T')
   - Submit button: "Request Wallet Withdrawal"

3. **Withdrawal History Table**:
   - Date
   - Amount
   - Wallet Address
   - Status (pending/approved/paid/rejected)
   - Admin Note

---

## 🗂️ Database Migration

**File**: `/app/backend/migrations/add_payout_type_column.sql`

Run this SQL in your Supabase SQL Editor:

```sql
-- Add payoutType column
ALTER TABLE payout_requests 
ADD COLUMN IF NOT EXISTS "payoutType" TEXT DEFAULT 'earnings' 
CHECK ("payoutType" IN ('earnings', 'wallet_balance'));

-- Create index
CREATE INDEX IF NOT EXISTS idx_payout_requests_payout_type 
ON payout_requests("payoutType");

-- Update existing records
UPDATE payout_requests 
SET "payoutType" = 'earnings' 
WHERE "payoutType" IS NULL;
```

---

## 📝 Admin Approval Process

When admin approves a **wallet_balance** payout:

1. Payout request status changes to `approved` or `paid`
2. Amount is **deducted from seller's wallet balance**
3. Transaction record is created
4. Seller's balance is updated in real-time

**Backend Logic** (server.py line ~3195):
```python
if payout_type == "wallet_balance" and req.status in ("approved", "paid"):
    # Deduct from wallet balance
    new_balance = current_balance - payout_amount
    
    # Update wallet
    supabase_admin.table('seller_wallets').update({
        'balance': new_balance,
        'updatedAt': datetime.now(timezone.utc).isoformat()
    }).eq('userId', seller_id).execute()
```

---

## 🔍 Testing Checklist

### Backend Testing:
- [ ] Place an order and mark it as completed
- [ ] Verify seller earns 20% (not 100%)
- [ ] Verify both `totalEarnings` and `balance` increase by 20%
- [ ] Create wallet balance withdrawal request
- [ ] Verify withdrawal amount is validated against wallet balance
- [ ] Admin approves withdrawal
- [ ] Verify wallet balance is deducted

### Frontend Testing:
- [ ] View wallet balance in Payouts tab
- [ ] Submit wallet withdrawal request with TRC20 address
- [ ] View wallet withdrawal history
- [ ] Verify earnings payout and wallet withdrawal are separate sections
- [ ] Check form validation (amount, TRC20 address format)

---

## 🚀 Deployment Steps

1. **Run Database Migration**:
   ```sql
   -- In Supabase SQL Editor
   \i /app/backend/migrations/add_payout_type_column.sql
   ```

2. **Restart Backend**:
   ```bash
   sudo supervisorctl restart backend
   ```

3. **Clear Frontend Cache**:
   ```bash
   sudo supervisorctl restart frontend
   ```

4. **Test with real orders**:
   - Create order as buyer
   - Admin marks as completed
   - Verify seller gets 20% in wallet balance
   - Seller requests wallet withdrawal
   - Admin approves
   - Verify balance is deducted

---

## 📊 Comparison: Old vs New

| Feature | Old System | New System |
|---------|-----------|------------|
| **Earnings %** | 100% of order | 20% of order |
| **Where earnings go** | Only `totalEarnings` | Both `totalEarnings` AND `balance` |
| **Can withdraw earnings?** | Only via earnings payout | Via earnings payout OR wallet withdrawal |
| **Withdrawal types** | 1 type (earnings) | 2 types (earnings + wallet_balance) |
| **Immediate withdrawal** | No (must wait for earnings calculation) | Yes (from wallet balance) |

---

## 🎯 Benefits

1. **Fair Commission**: Sellers earn 20% per order (standard marketplace rate)
2. **Flexible Withdrawals**: Sellers can withdraw wallet balance anytime
3. **Clear Separation**: Earnings tracking vs. withdrawable balance
4. **Multiple Withdrawal Options**: Choose earnings payout or wallet withdrawal
5. **Real-time Balance**: 20% is immediately available in wallet

---

## 🔐 Security

- TRC20 wallet validation (34 chars, starts with 'T')
- Amount validation (must not exceed available balance)
- Admin approval required for all withdrawals
- Transaction records for audit trail
- Separate payout types prevent confusion

---

## 📞 Support

For issues or questions:
1. Check wallet balance endpoint: `GET /seller/wallet/balance`
2. Check wallet transactions: `GET /seller/wallet-transactions`
3. Review admin payout management
4. Verify database migration was run successfully

---

**Last Updated**: February 5, 2025
**Version**: 1.0
