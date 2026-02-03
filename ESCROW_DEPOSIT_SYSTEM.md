# Escrow + Seller Deposit System - Implementation Guide

## 🎯 Overview

This document describes the new **Platform-Managed Shipping with Seller Deposits** system that has been added to the marketplace.

**Status**: ✅ **Backend Implementation Complete** | ⏳ **Database Migration Required** | ⏳ **Frontend Integration Pending**

---

## 📋 System Flow

### 1️⃣ Buyer Places Order
- Buyer pays **$100** (example amount)
- Money goes to **Platform Wallet**
- Order status → **`PAID`** (escrowStatus)
- System automatically calculates deposit requirement: **80% of order value**

### 2️⃣ Order Assigned to Seller
- Seller sees new order in their dashboard
- Order status → **`AWAITING_SELLER_DEPOSIT`**
- **System message to seller:**
  > "Recharge $80 (80% of order) to confirm and unlock this order payout."

### 3️⃣ Seller Deposits to Wallet
- Seller adds **$80** to their Seller Wallet
- Seller confirms deposit for specific order
- Order status → **`DEPOSIT_RECEIVED`**
- Deposit amount is **locked** in `depositBalance`

### 4️⃣ Platform Ships Order
- Admin/Platform marks order as shipped
- Order status → **`SHIPPED`**
- (Optional) Tracking info added
- Auto-delivery timer starts (48 hours)

### 5️⃣ Buyer Confirms Delivery
- Buyer clicks "Confirm Delivery" button
- OR system auto-confirms after 48 hours
- Order status → **`DELIVERED`**

### 6️⃣ Automatic Settlement
**Atomic Database Transaction:**
```
- Seller receives: +$100 (order amount) → withdrawableBalance
- Seller loses: -$80 (deposit deducted) → depositBalance
- Platform keeps: $80 (profit)

Net Results:
- Seller net profit: $100 - $80 = $20
- Platform profit: $80
```

---

## 🗄️ Database Schema

### New Tables Created

#### 1. `platform_wallet`
Tracks all platform money.

```sql
- id: UUID (fixed: '00000000-0000-0000-0000-000000000001')
- balance: DECIMAL(12,2)
- totalReceived: DECIMAL(12,2)
- totalPaidOut: DECIMAL(12,2)
- updatedAt: TIMESTAMP
```

#### 2. `order_deposits`
Tracks deposit requirements per order per seller.

```sql
- id: UUID
- orderId: UUID (REFERENCES orders)
- sellerId: UUID (REFERENCES users)
- requiredAmount: DECIMAL(10,2)
- depositedAmount: DECIMAL(10,2)
- isDepositComplete: BOOLEAN
- depositedAt: TIMESTAMP
```

#### 3. `platform_transactions`
Records all platform money movements.

```sql
- id: UUID
- type: TEXT ('buyer_payment', 'seller_payout', 'deposit_collection', 'refund')
- amount: DECIMAL(10,2)
- orderId: UUID
- userId: UUID
- description: TEXT
- previousBalance: DECIMAL(10,2)
- newBalance: DECIMAL(10,2)
```

### Modified Tables

#### `orders` (New Columns Added)
```sql
- escrowStatus: TEXT ('pending', 'paid', 'awaiting_seller_deposit', 
                     'deposit_received', 'shipped', 'delivered', 'settled')
- depositRequired: DECIMAL(10,2)
- deliveryConfirmedAt: TIMESTAMP
- autoDeliveryAt: TIMESTAMP
- settlementCompletedAt: TIMESTAMP
```

#### `seller_wallets` (New Columns Added)
```sql
- withdrawableBalance: DECIMAL(10,2)  -- Amount seller can withdraw
- depositBalance: DECIMAL(10,2)       -- Amount locked as deposits
```

---

## 🔌 API Endpoints

### 1. Get Orders Pending Deposit (Seller)
```http
GET /api/seller/orders/pending-deposit
Authorization: Bearer {seller_token}
```

**Response:**
```json
{
  "orders": [
    {
      "id": "uuid",
      "totalAmount": 100.00,
      "depositRequired": 80.00,
      "escrowStatus": "awaiting_seller_deposit",
      "depositInfo": {
        "requiredAmount": 80.00,
        "depositedAmount": 0.00,
        "isComplete": false
      }
    }
  ],
  "count": 1
}
```

---

### 2. Deposit for Order (Seller)
```http
POST /api/seller/wallet/deposit-for-order
Authorization: Bearer {seller_token}
Content-Type: application/json

{
  "orderId": "uuid",
  "amount": 80.00
}
```

**Response:**
```json
{
  "success": true,
  "message": "Deposit of $80.00 completed successfully",
  "depositAmount": 80.00,
  "newBalance": 20.00,
  "depositBalance": 80.00,
  "orderStatus": "deposit_received"
}
```

**Error Cases:**
- Insufficient balance
- Order not found
- Not seller's order
- Order not awaiting deposit

---

### 3. Ship Order by Platform (Admin)
```http
POST /api/orders/{orderId}/ship-by-platform
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "trackingNumber": "TRACK123456",
  "courierName": "DHL Express"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Order marked as shipped by platform",
  "orderId": "uuid",
  "trackingNumber": "TRACK123456",
  "status": "shipped"
}
```

---

### 4. Confirm Delivery (Buyer)
```http
POST /api/orders/{orderId}/confirm-delivery
Authorization: Bearer {buyer_token}
```

**Response:**
```json
{
  "success": true,
  "message": "Delivery confirmed and settlement processed",
  "orderId": "uuid",
  "settlements": [
    {
      "sellerId": "uuid",
      "success": true,
      "amount": 100.00,
      "deposit": 80.00,
      "profit": 20.00
    }
  ]
}
```

**This triggers automatic settlement!**

---

### 5. Get Platform Wallet (Admin)
```http
GET /api/admin/platform-wallet
Authorization: Bearer {admin_token}
```

**Response:**
```json
{
  "balance": 1500.00,
  "totalReceived": 5000.00,
  "totalPaidOut": 3500.00,
  "updatedAt": "2025-02-03T12:00:00Z"
}
```

---

### 6. Get Deposit Status (Seller)
```http
GET /api/seller/deposit-status/{orderId}
Authorization: Bearer {seller_token}
```

**Response:**
```json
{
  "found": true,
  "orderId": "uuid",
  "requiredAmount": 80.00,
  "depositedAmount": 80.00,
  "isComplete": true,
  "depositedAt": "2025-02-03T12:00:00Z"
}
```

---

## 🔄 Complete Order Flow Example

### Scenario: $100 Order

1. **Buyer places order**
   ```
   POST /api/orders
   {
     "items": [...],
     "totalAmount": 100.00,
     "useWallet": true
   }
   ```
   
   **Result:**
   - Buyer wallet: -$100
   - Platform wallet: +$100
   - Order.escrowStatus = 'awaiting_seller_deposit'
   - Order.depositRequired = $80
   - order_deposits created for seller

2. **Seller checks pending deposits**
   ```
   GET /api/seller/orders/pending-deposit
   ```
   
   **Shows:** Order requiring $80 deposit

3. **Seller deposits**
   ```
   POST /api/seller/wallet/deposit-for-order
   { "orderId": "xxx", "amount": 80.00 }
   ```
   
   **Result:**
   - Seller balance: -$80
   - Seller depositBalance: +$80
   - Order.escrowStatus = 'deposit_received'

4. **Platform ships**
   ```
   POST /api/orders/{id}/ship-by-platform
   { "trackingNumber": "TRACK123" }
   ```
   
   **Result:**
   - Order.escrowStatus = 'shipped'

5. **Buyer confirms delivery**
   ```
   POST /api/orders/{id}/confirm-delivery
   ```
   
   **Settlement (Atomic Transaction):**
   ```sql
   -- Seller wallet changes:
   withdrawableBalance: +$100 (order payout)
   depositBalance: -$80 (deposit deducted)
   Net: +$20
   
   -- Platform wallet:
   balance: +$80 (deposit collection)
   
   -- Order status:
   escrowStatus: 'settled'
   settlementCompletedAt: NOW()
   ```

---

## 🔒 Security & Data Integrity

### Atomic Transactions
All settlement operations use the database function `settle_order_after_delivery()` which ensures:
- ✅ All updates succeed or all fail
- ✅ No partial settlements
- ✅ Balance checks before operations
- ✅ Transaction logging

### RLS Policies
- ✅ Sellers can only see their own deposits
- ✅ Buyers can only confirm their own deliveries
- ✅ Admin can view platform wallet
- ✅ All new tables have proper RLS

### Validations
- ✅ Deposit amount must match order requirement
- ✅ Seller must have sufficient balance
- ✅ Order status must be correct for each operation
- ✅ Only order participants can perform actions

---

## 📊 Settlement Function

The atomic settlement is handled by a PostgreSQL function:

```sql
settle_order_after_delivery(
    p_order_id UUID,
    p_seller_id UUID,
    p_order_amount DECIMAL,
    p_deposit_amount DECIMAL
)
```

**What it does:**
1. Locks seller wallet (FOR UPDATE)
2. Verifies sufficient deposit balance
3. Credits order amount to seller
4. Deducts deposit from seller
5. Updates platform wallet
6. Records all transactions
7. Updates order status to 'settled'
8. Marks deposit as complete

**Returns:**
```json
{
  "success": true,
  "sellerNetProfit": 20.00,
  "platformProfit": 80.00,
  "sellerNewBalance": 40.00
}
```

---

## 🚀 Next Steps

### Required Actions:

1. **Run Database Migration**
   ```bash
   # In Supabase SQL Editor, run:
   /app/backend/migrations/escrow_deposit_system.sql
   ```

2. **Test Backend APIs**
   - Test deposit flow
   - Test shipping flow
   - Test delivery confirmation
   - Test settlement

3. **Frontend Integration** (Coming Next)
   - Seller Dashboard: Show pending deposits
   - Seller Dashboard: Deposit button for orders
   - Buyer Dashboard: Confirm delivery button
   - Admin Dashboard: Platform wallet display
   - Admin Dashboard: Ship by platform button

4. **Auto-Delivery Feature** (Future)
   - Background job to auto-confirm after 48h
   - Cron job or scheduled function

---

## 💡 Important Notes

### This System is ADDITIVE
- ✅ Does NOT modify existing data
- ✅ Does NOT break existing order flows
- ✅ New columns have default values
- ✅ Existing orders continue to work
- ✅ New flow only applies to new orders

### Backward Compatibility
- Old orders: Use existing paymentStatus/orderStatus
- New orders: Use escrowStatus for new flow
- Both systems coexist peacefully

### Testing Checklist
- [ ] Database migration runs successfully
- [ ] Create order with wallet payment
- [ ] Seller sees order in pending deposits
- [ ] Seller can deposit successfully
- [ ] Admin can ship order
- [ ] Buyer can confirm delivery
- [ ] Settlement calculates correctly
- [ ] Platform wallet updates correctly

---

## 🔧 Troubleshooting

### Issue: Seller can't deposit
- Check seller wallet balance
- Verify order is in 'awaiting_seller_deposit' status
- Check order belongs to seller

### Issue: Settlement fails
- Check seller has deposit balance
- Verify order is in 'delivered' status
- Check platform_wallet exists

### Issue: Platform wallet not found
```sql
-- Initialize platform wallet manually:
INSERT INTO platform_wallet (id, balance)
VALUES ('00000000-0000-0000-0000-000000000001', 0.00);
```

---

## 📝 Database Migration Status

**File:** `/app/backend/migrations/escrow_deposit_system.sql`

**Status:** ✅ Created, ⏳ Not yet run in Supabase

**To Apply:**
1. Go to Supabase Dashboard
2. Navigate to SQL Editor
3. Copy contents of migration file
4. Execute SQL
5. Verify tables created successfully

---

**Implementation Date:** February 3, 2025  
**Status:** Backend Complete, Database Migration Ready  
**Next Phase:** Frontend Integration
