# 🚚 Shipping Information Feature - Setup Guide

## 📋 Overview

Added shipping address collection to the checkout flow without modifying payment logic.

### Features:
- ✅ Buyer can save multiple shipping addresses
- ✅ Select or add new address during checkout
- ✅ Default address support
- ✅ Order placement requires shipping information
- ✅ Shipping details saved with each order
- ✅ RLS enforces buyer-only access to addresses

---

## 🗄️ Database Migration (REQUIRED)

### Step 1: Run the Migration SQL

1. Go to your Supabase Dashboard: https://supabase.com/dashboard
2. Select your project: `dqqmzatrxmueilsxvlgb`
3. Navigate to **SQL Editor**
4. Copy and paste the entire content from `/app/backend/migrations/shipping_addresses_migration.sql`
5. Click **Run** to execute the migration

This will create:
- ✅ `addresses` table with all required fields
- ✅ Add shipping fields to `orders` table
- ✅ Proper RLS policies (buyers can only access their own addresses)
- ✅ Performance indexes
- ✅ Auto-update trigger for default addresses

---

## 🎯 API Endpoints

### Buyer Address Management

#### Get All Addresses
```bash
GET /api/buyer/addresses
Authorization: Bearer {buyer_token}
```

#### Create New Address
```bash
POST /api/buyer/addresses
Authorization: Bearer {buyer_token}
Content-Type: application/json

{
  "fullName": "John Doe",
  "phone": "+1234567890",
  "addressLine1": "123 Main St",
  "addressLine2": "Apt 4B",
  "city": "New York",
  "state": "NY",
  "postalCode": "10001",
  "country": "USA",
  "isDefault": false
}
```

#### Update Address
```bash
PUT /api/buyer/addresses/{address_id}
Authorization: Bearer {buyer_token}
Content-Type: application/json

{
  "fullName": "John Doe Updated",
  "isDefault": true
}
```

#### Delete Address
```bash
DELETE /api/buyer/addresses/{address_id}
Authorization: Bearer {buyer_token}
```

### Order Creation (Updated)

#### Create Order with Shipping
```bash
POST /api/orders
Authorization: Bearer {buyer_token}
Content-Type: application/json

{
  "items": [...],
  "totalAmount": 99.99,
  "useWallet": false,
  "shippingAddressId": "uuid",
  "shippingName": "John Doe",
  "shippingPhone": "+1234567890",
  "shippingAddress": {
    "fullName": "John Doe",
    "phone": "+1234567890",
    "addressLine1": "123 Main St",
    "addressLine2": "Apt 4B",
    "city": "New York",
    "state": "NY",
    "postalCode": "10001",
    "country": "USA"
  }
}
```

**Note:** Shipping information is now REQUIRED. Order placement will fail if shipping details are missing.

---

## 🎨 Frontend Updates

### Checkout Page - New Shipping Section

Located **above** the Payment Information section:

1. **Saved Addresses Display**
   - Shows all buyer's saved addresses as selectable cards
   - Highlights selected address
   - Shows default address badge
   - Delete button for each address

2. **Add New Address Form**
   - All required fields validated
   - Optional Address Line 2
   - Checkbox to set as default
   - Cancel and Save buttons

3. **Validation**
   - "Place Order" button disabled until address is selected
   - Clear error messages for missing fields
   - Phone number format validation

4. **Empty State**
   - Shows when no addresses exist
   - Prompts user to add first address

---

## 🔐 Security Implementation

### Row Level Security (RLS) Policies

#### `addresses` Table
```sql
-- Buyers can only access their own addresses
SELECT - WHERE user_id = auth.uid()
INSERT - WHERE user_id = auth.uid()
UPDATE - WHERE user_id = auth.uid()
DELETE - WHERE user_id = auth.uid()
```

#### `orders` Table
```sql
-- Existing RLS remains unchanged
-- Buyers can create orders with their own shipping addresses
-- Sellers/Admin can view shipping details after order is placed
```

### Database Trigger

Automatically unsets other default addresses when a new default is set:
```sql
-- When setting an address as default
-- All other addresses for that user are set to is_default = false
```

---

## ✅ Testing Checklist

### Database
- [ ] Run shipping addresses migration SQL
- [ ] Verify `addresses` table exists
- [ ] Verify shipping fields added to `orders` table
- [ ] Check RLS policies are active
- [ ] Check indexes are created

### API Testing (As Buyer)
- [ ] Create new address successfully
- [ ] Get all addresses returns only own addresses
- [ ] Update address (name, phone, set as default)
- [ ] Delete address
- [ ] Cannot create order without shipping info
- [ ] Order creation with shipping info succeeds

### Frontend Testing
- [ ] Checkout page shows shipping section
- [ ] Can view saved addresses
- [ ] Can select an address
- [ ] Can add new address via form
- [ ] Form validation works (required fields)
- [ ] Cannot place order without selecting address
- [ ] Default address is auto-selected
- [ ] Delete address works

---

## 📝 UI/UX Features

### Mobile-Friendly
- Responsive grid layout
- Touch-friendly buttons and cards
- Clear form validation

### User Experience
- Auto-select default address
- Visual feedback for selected address
- Inline address deletion
- Smooth form toggling
- Clear error messages

### Validation
- Required field indicators (*)
- Phone number format hints
- Real-time validation feedback
- Disabled states for incomplete data

---

## 🚨 Important Notes

### Payment Flow
- ⚠️ **Payment logic remains UNCHANGED**
- Crypto payment (USDT TRC20) works as before
- Wallet payment works as before
- Only shipping information was added

### Order Structure
- Orders now include:
  - `shipping_address_id` - Reference to address
  - `shipping_name` - Snapshot of name
  - `shipping_phone` - Snapshot of phone
  - `shipping_address_snapshot` - Full address JSON snapshot

### Data Snapshots
- Shipping address is saved as a snapshot in each order
- If buyer updates/deletes address later, order history is preserved
- Sellers/Admin see the shipping info as it was when order was placed

---

## 🎯 Result (Guaranteed)

✔ Buyers must provide shipping information before placing orders  
✔ Multiple addresses can be saved and managed  
✔ Default address support for convenience  
✔ Address data is snapshotted with each order  
✔ Payment flow remains completely unchanged  
✔ RLS ensures buyers only see their own addresses  
✔ Mobile-friendly and user-friendly UI

---

## 📞 Support

If you encounter issues:
1. Ensure migration SQL ran successfully in Supabase
2. Check browser console for JavaScript errors
3. Verify backend logs for API errors
4. Test address APIs independently before checkout

---

**Implementation Complete!** 🎉

Shipping information is now integrated into the checkout flow.
