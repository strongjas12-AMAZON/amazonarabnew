# 🔧 Fix for Deposit Balance Error

## ❌ Error You're Seeing
```
Could not find the 'depositBalance' column of 'seller_wallets' in the schema cache (PGRST204)
```

## 🎯 Solution
The `depositBalance` column is missing from your `seller_wallets` table. You need to run the Escrow + Seller Deposit System migration.

---

## 📋 Quick Fix Steps

### Step 1: Go to Supabase SQL Editor
1. Open your browser and go to: **https://supabase.com/dashboard**
2. Select your project: **`dqqmzatrxmueilsxvlgb`**
3. Click on **"SQL Editor"** in the left sidebar
4. Click **"New Query"**

### Step 2: Copy the Migration SQL
The complete SQL script is located at:
```
/app/backend/migrations/escrow_deposit_system.sql
```

Copy the ENTIRE content of this file (269 lines).

### Step 3: Run the Migration
1. Paste the SQL into the Supabase SQL Editor
2. Click **"Run"** (or press Ctrl/Cmd + Enter)
3. Wait for success message: ✅ "Success. No rows returned"

---

## ✅ What This Migration Does

### New Tables Created:
- ✅ `platform_wallet` - Holds all buyer payments
- ✅ `order_deposits` - Tracks seller deposits per order
- ✅ `platform_transactions` - Tracks all platform money movements

### New Columns Added to Existing Tables:

**Orders table:**
- `escrowStatus` - Tracks order through escrow flow
- `depositRequired` - Amount seller must deposit
- `deliveryConfirmedAt` - When delivery was confirmed
- `autoDeliveryAt` - Auto-confirmation timestamp
- `settlementCompletedAt` - When payment was settled

**Seller_wallets table:**
- `withdrawableBalance` - Amount seller can withdraw
- `depositBalance` - Amount held as deposit (THIS FIXES YOUR ERROR!)

### Features Enabled:
1. **Escrow Payment System** - Buyer pays → Platform holds → Seller deposits → Order shipped
2. **Seller Deposit Requirement** - Sellers deposit 80% of order value as security
3. **Automatic Settlement** - On delivery confirmation, seller gets order amount minus deposit
4. **Platform Profit** - Platform keeps the deposit (20% of order value)

---

## 🔒 Safety Notes
- ✅ This migration is **100% SAFE** and **ADDITIVE**
- ✅ Does NOT modify or delete existing data
- ✅ All new columns have default values
- ✅ Existing order flows remain intact
- ✅ Includes proper RLS policies for security

---

## 🧪 After Running Migration

### Test the Deposit Flow:
1. **Login as Seller**
2. **Go to Wallet section**
3. **Recharge your wallet** with sufficient balance
4. **View pending orders** requiring deposit
5. **Click "Deposit Balance"** button
6. ✅ Deposit should work without the PGRST204 error!

### Expected New Order Flow:
```
1. Buyer places order & pays → Status: AWAITING_SELLER_DEPOSIT
2. Seller deposits 80% from wallet → Status: DEPOSIT_RECEIVED
3. Platform ships order → Status: SHIPPED
4. Buyer confirms delivery → Status: DELIVERED
5. Auto-settlement: Seller gets order amount, loses deposit
   → Net profit for seller: 20% of order value
   → Platform keeps: 80% deposit
```

---

## 📞 Need Help?
If you encounter any issues running the migration, let me know and I can help troubleshoot!
