# USDT Deposit Payment System - Complete Guide

## 🎯 Overview

This system allows sellers to pay their 80% order deposit **directly via USDT TRC20** instead of only using their internal wallet balance. This is an **alternative method** added to the existing wallet deposit system.

**Status**: ✅ **Backend Complete** | ⏳ **Database Migration Required** | ⏳ **Frontend Integration Pending**

---

## 💰 How It Works

### Deposit Flow

1. **Buyer places order** → Order created, payment confirmed
2. **Order status** → `AWAITING_SELLER_DEPOSIT`
3. **Seller has 2 options**:
   - **Option A (Existing)**: Use internal wallet balance
   - **Option B (NEW)**: Pay directly via USDT TRC20

### USDT Payment Flow (NEW)

**Step 1: Seller Initiates Payment**
- Seller views order in Order Center
- Clicks "Pay Deposit with USDT"
- System shows:
  - QR Code for payment
  - Wallet Address: `TY8Z91NMCjREyZVj9NjDsF8hVjyqfxFFRU`
  - Amount to pay: 80% of order value

**Step 2: Seller Makes Payment**
- Seller scans QR code or copies wallet address
- Sends USDT (TRC20) from their crypto wallet
- Gets transaction hash from blockchain

**Step 3: Seller Submits Proof**
- Enters transaction hash in form
- Adds optional notes
- Clicks "Submit Payment Proof"
- Status: `PENDING CONFIRMATION`

**Step 4: Admin Confirms**
- Admin receives email notification
- Views pending deposits in Admin Dashboard
- Verifies transaction on blockchain
- **Approves** → Order unlocked for shipping
- **Rejects** → Seller can resubmit

**Step 5: Order Completion**
- Seller ships order
- Buyer receives and confirms
- Seller receives **100% of order amount** as earnings
- **Net profit: 20%** (paid 80%, received 100%)

---

## 🗄️ Database Schema

### Migration File
Location: `/app/backend/migrations/usdt_deposit_payment_system.sql`

### New Columns Added to `order_deposits` Table

```sql
-- Method used for deposit payment
deposit_method TEXT DEFAULT 'internal_wallet' 
  CHECK (deposit_method IN ('internal_wallet', 'usdt_payment'))

-- USDT transaction details
transaction_hash TEXT

-- Deposit confirmation status
deposit_status TEXT DEFAULT 'pending'
  CHECK (deposit_status IN ('pending', 'confirmed', 'rejected'))

-- Additional information
payment_notes TEXT
submitted_at TIMESTAMPTZ
confirmed_at TIMESTAMPTZ
confirmed_by UUID REFERENCES users(id)
rejection_reason TEXT
```

### Indexes Created
```sql
CREATE INDEX idx_order_deposits_status ON order_deposits(deposit_status);
CREATE INDEX idx_order_deposits_method ON order_deposits(deposit_method);
```

---

## 🔌 API Endpoints

### 1. Submit USDT Deposit Payment (Seller)

**Endpoint:**
```http
POST /api/seller/orders/{order_id}/submit-usdt-deposit
Authorization: Bearer {seller_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "orderId": "uuid-string",
  "transactionHash": "0x1234567890abcdef...",
  "notes": "Optional payment notes"
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Deposit payment submitted successfully. Awaiting admin confirmation.",
  "depositAmount": 80.00,
  "transactionHash": "0x1234567890abcdef...",
  "status": "pending"
}
```

**Response (Error):**
```json
{
  "detail": "This order does not contain your products"
}
```

---

### 2. Get Pending Deposit Confirmations (Admin)

**Endpoint:**
```http
GET /api/admin/deposit-confirmations
Authorization: Bearer {admin_token}
```

**Response:**
```json
{
  "success": true,
  "deposits": [
    {
      "id": "deposit-uuid",
      "orderId": "order-uuid",
      "sellerId": "seller-uuid",
      "sellerName": "John's Store",
      "sellerEmail": "john@example.com",
      "orderAmount": 100.00,
      "depositRequired": 80.00,
      "depositAmount": 80.00,
      "transactionHash": "0x1234567890abcdef...",
      "notes": "Paid via Trust Wallet",
      "submittedAt": "2025-02-03T10:30:00Z",
      "orderCreatedAt": "2025-02-03T09:00:00Z"
    }
  ],
  "count": 1
}
```

---

### 3. Confirm or Reject Deposit (Admin)

**Endpoint:**
```http
POST /api/admin/orders/{order_id}/confirm-deposit
Authorization: Bearer {admin_token}
Content-Type: application/json
```

**Request Body (Approve):**
```json
{
  "approved": true
}
```

**Request Body (Reject):**
```json
{
  "approved": false,
  "rejectionReason": "Transaction hash not found on blockchain"
}
```

**Response (Approved):**
```json
{
  "success": true,
  "message": "Deposit confirmed successfully. Order unlocked for shipping.",
  "orderId": "order-uuid",
  "status": "confirmed"
}
```

**Response (Rejected):**
```json
{
  "success": true,
  "message": "Deposit rejected. Seller has been notified.",
  "orderId": "order-uuid",
  "status": "rejected",
  "reason": "Transaction hash not found on blockchain"
}
```

---

## 📧 Email Notifications

### 1. Admin Notification (New Deposit Submission)
**Sent to:** `support@arabshopping.org`
**Trigger:** Seller submits USDT deposit payment
**Contains:**
- Seller information
- Order ID
- Deposit amount
- Transaction hash
- Payment notes
- Wallet address

### 2. Seller Notification (Deposit Confirmed)
**Sent to:** Seller email
**Trigger:** Admin approves deposit
**Contains:**
- Confirmation message
- Order ID
- Deposit amount
- Transaction hash
- Next steps (ship order)

### 3. Seller Notification (Deposit Rejected)
**Sent to:** Seller email
**Trigger:** Admin rejects deposit
**Contains:**
- Rejection notification
- Reason for rejection
- Transaction hash
- Instructions to resubmit

---

## 🖥️ Frontend Implementation

### Required Components

#### 1. Seller Order Center - Deposit Payment Modal

**Location:** `frontend/src/pages/dashboard/SellerDashboard.js` (Order Center section)

**Features:**
- **Tab 1: Wallet Balance** (existing method)
  - Use internal wallet balance
  - Instant confirmation
  
- **Tab 2: Pay with USDT** (NEW)
  - Display QR code image
  - Show wallet address (copyable)
  - Display amount: 80% of order value
  - Input: Transaction hash (required)
  - Input: Notes (optional)
  - Submit button
  - Status indicator

**Modal States:**
- **Not Submitted**: Show payment form
- **Pending**: Show "Awaiting admin confirmation" message
- **Confirmed**: Show success message + ship order button
- **Rejected**: Show rejection reason + resubmit button

---

#### 2. Admin Dashboard - Deposit Confirmations Section

**Location:** `frontend/src/pages/dashboard/AdminDashboard.js`

**New Tab:** "Deposit Confirmations"

**Table Columns:**
- Order ID (clickable)
- Seller Name
- Seller Email
- Order Amount
- Deposit Required (80%)
- Transaction Hash (copyable)
- Submission Date
- Actions (Confirm / Reject buttons)

**Features:**
- Filter by status (pending/confirmed/rejected)
- Search by order ID or seller
- Sort by submission date
- Bulk actions (optional)
- Transaction hash verification link to blockchain explorer

**Confirm Modal:**
- Show order details
- Show seller information
- Show transaction hash
- Link to verify on tronscan.org
- Confirm button

**Reject Modal:**
- Show order details
- Textarea for rejection reason (required)
- Reject button

---

#### 3. Seller Dashboard - Earnings Display

**Location:** `frontend/src/pages/dashboard/SellerDashboard.js` (Wallet section)

**Display:**
```
Total Earnings: $XXX.XX
  ├─ Completed Orders: $XXX.XX (available to withdraw)
  ├─ Pending Orders: $XXX.XX (locked until completion)
  └─ Deposits Made: $XXX.XX (will be returned on completion)

Available to Withdraw: $XXX.XX
```

---

## 🔒 Security & Validation

### Backend Validations

1. **Order Ownership**: Verify seller owns products in the order
2. **Order Status**: Must be in `awaiting_seller_deposit` status
3. **Transaction Hash**: Must be provided (minimum length check)
4. **Duplicate Prevention**: Check for existing pending submission
5. **Admin Only**: Only admins can confirm/reject deposits
6. **Amount Verification**: Deposit must be exactly 80% of order value

### Recommended Frontend Validations

1. **Transaction Hash Format**:
   - Length: 64 characters (typical USDT TRC20 hash)
   - Format: Hexadecimal (0-9, a-f)
   - Pattern: `/^0x[a-fA-F0-9]{64}$/` or `/^[a-fA-F0-9]{64}$/`

2. **Blockchain Verification Link**:
   - Generate tronscan.org link for admins to verify
   - Format: `https://tronscan.org/#/transaction/{hash}`

3. **Status Polling**:
   - Auto-refresh pending deposits every 30 seconds
   - Show real-time status updates

---

## 🎨 UI Assets Required

### QR Code Image
**File:** User provided QR code image
**Usage:** Display in payment modal
**Specifications:**
- Format: PNG/JPG
- Size: 300x300px recommended
- Location: `/frontend/public/assets/usdt-wallet-qr.png`

### Wallet Address
```
TY8Z91NMCjREyZVj9NjDsF8hVjyqfxFFRU
```
**Display:** With copy button
**Validation:** Show ✓ when valid TRC20 address

---

## 📝 Implementation Checklist

### Backend ✅
- [x] Database migration created
- [x] Pydantic models added
- [x] Submit USDT deposit endpoint
- [x] Admin view pending deposits endpoint
- [x] Admin confirm/reject deposit endpoint
- [x] Email notifications implemented
- [x] Error handling added
- [x] Logging implemented

### Database ⏳
- [ ] Run migration SQL in Supabase
- [ ] Verify new columns exist
- [ ] Test indexes created

### Frontend ⏳
- [ ] Upload QR code image
- [ ] Create deposit payment modal (Seller)
- [ ] Add deposit confirmations tab (Admin)
- [ ] Update earnings display (Seller)
- [ ] Add status indicators
- [ ] Implement real-time updates
- [ ] Add transaction hash validation
- [ ] Add blockchain verification links

### Testing ⏳
- [ ] Test seller USDT deposit submission
- [ ] Test admin deposit confirmations view
- [ ] Test admin approve deposit
- [ ] Test admin reject deposit
- [ ] Test email notifications
- [ ] Test order unlock after confirmation
- [ ] Test earnings calculation
- [ ] Test withdrawal restrictions

---

## 🚀 Deployment Steps

### Step 1: Database Migration
```sql
-- In Supabase SQL Editor, run:
-- /app/backend/migrations/usdt_deposit_payment_system.sql
```

### Step 2: Restart Backend
```bash
sudo supervisorctl restart backend
```

### Step 3: Upload Assets
- Upload QR code to `/frontend/public/assets/`
- Verify image is accessible

### Step 4: Frontend Development
- Implement seller deposit modal
- Implement admin confirmations page
- Update earnings display

### Step 5: Testing
- Create test order
- Test USDT deposit flow
- Test admin confirmation flow
- Verify email notifications
- Test order completion flow

---

## 📊 Profit Calculation Example

**Example Order: $100**

1. Buyer pays: **$100** → Platform Wallet
2. Seller deposits: **$80** → Platform Wallet (USDT TRC20)
3. Platform total in escrow: **$180**
4. Order completed
5. Seller receives: **$100** → Seller Earnings
6. Platform keeps: **$80** (deposit)

**Final Results:**
- **Seller Net Profit**: $100 - $80 = **$20 (20%)**
- **Platform Profit**: **$80**
- **Buyer Paid**: **$100**

---

## 🐛 Troubleshooting

### Issue: Deposit not showing as pending
**Solution:** Check order status is `awaiting_seller_deposit`

### Issue: Admin can't see deposit
**Solution:** Verify deposit_method is 'usdt_payment' and deposit_status is 'pending'

### Issue: Transaction hash rejected
**Solution:** Verify hash exists on Tron blockchain (tronscan.org)

### Issue: Order not unlocking after confirmation
**Solution:** Check order escrow_status updated to 'deposit_received'

---

## 📞 Support

For any issues or questions:
- **Email**: support@arabshopping.org
- **Admin Panel**: Deposit Confirmations section
- **Logs**: `/var/log/supervisor/backend.*.log`

---

**Last Updated**: February 3, 2025
**Version**: 1.0
**Author**: Development Team
