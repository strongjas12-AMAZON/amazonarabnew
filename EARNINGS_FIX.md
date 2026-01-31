# Seller Earnings Calculation Fix

## Problem
Seller earnings were not displaying correctly on the seller dashboard. The Total Earnings stat was showing incorrect values or zero.

## Root Cause
The `/api/seller/earnings` endpoint was using the old database structure:
- Joining `order_items` with `products` table
- Checking `product.seller_id` to calculate earnings

However, the system has been migrated to the new store products system:
- `order_items.product_id` now references `store_products.id` (not `products.id`)
- `store_products` table has `seller_id` column for direct seller identification

## Solution Applied

### Updated Query Structure
**Before:**
```python
orders_result = (
    supabase_admin.table("orders")
    .select("*, order_items(*, products(*))")
    .in_("payment_status", ["paid", "completed"])
    .execute()
)
# Checking: if product.get("seller_id") == current_user["id"]
```

**After:**
```python
orders_result = (
    supabase_admin.table("orders")
    .select("*, order_items(*, store_products!inner(seller_id))")
    .in_("payment_status", ["paid", "completed"])
    .execute()
)
# Checking: if store_product.get("seller_id") == current_user["id"]
```

### Key Changes
1. Changed join from `products` to `store_products` table
2. Added `!inner` to ensure proper filtering
3. Updated seller_id check to use `store_products.seller_id`
4. Calculations now accurately reflect seller's earnings from their store products

## Earnings Calculation Logic
The endpoint now correctly calculates:

1. **Total Earnings**: Sum of (price × quantity) for all paid/completed orders containing seller's products
2. **Available Balance**: Total Earnings - Total Withdrawn (approved/paid payouts)
3. **Pending Withdrawals**: Sum of pending payout requests
4. **Completed Withdrawals**: Sum of paid payout requests

## Impact
✅ Sellers can now see accurate earnings data
✅ Available balance correctly reflects withdrawable amount
✅ Payout requests work with accurate balance checks
✅ Compatible with new store_products system

## Related Tables
- `orders` - Contains buyer orders with payment status
- `order_items` - Links orders to products with quantities
- `store_products` - New system table with seller_id
- `payout_requests` - Tracks seller withdrawal requests

## Testing Required
1. Login as a verified seller with completed orders
2. Navigate to Seller Dashboard → Payouts tab
3. Verify "Total Earnings" displays correct amount
4. Verify "Available Balance" shows earnings minus withdrawals
5. Verify payout request form uses correct available balance
