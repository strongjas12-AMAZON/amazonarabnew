# Amazon Arab - Multi-Vendor Marketplace PRD

## Project Overview
A premium multi-vendor marketplace with dark UI and gold accents, featuring crypto payments (USDT TRC20) and email notifications.

## Tech Stack
- **Frontend**: React + TailwindCSS + shadcn/ui
- **Backend**: FastAPI (Python)
- **Database**: Supabase (PostgreSQL with RLS)
- **Storage**: Supabase Storage (documents bucket - private, products bucket - public)
- **Authentication**: Supabase Auth + JWT
- **Email**: Resend (transactional emails)

## User Roles
1. **Admin** - Manages users, verifications, orders, invite codes
2. **Seller** - Creates products, views orders (requires verification + invite code)
3. **Buyer** - Browses products, places orders, pays with crypto

## Core Features

### ✅ Fully Implemented & Tested
- [x] User registration (buyer/seller roles)
- [x] User authentication (login/logout)
- [x] Admin dashboard with stats (users, orders, verifications, invite codes)
- [x] Admin: View/manage all users
- [x] Admin: Create/view merchant invite codes
- [x] Admin: Review and approve/reject verifications
- [x] Admin: View orders and confirm payments
- [x] Admin: Mark orders as completed
- [x] Seller: Dashboard with verification status
- [x] Seller: Upload verification documents with invite code
- [x] Seller: Create products after verification
- [x] Seller: View orders containing their products
- [x] Seller: Product image upload capability
- [x] Seller: Remove product images
- [x] Buyer: Browse products page with search
- [x] Buyer: Add products to cart
- [x] Buyer: Checkout with crypto payment (USDT TRC20)
- [x] Buyer: View order history with payment status
- [x] Products listing with "Verified Seller" badges
- [x] **Product Categories** (10 predefined):
  - Electronics & Gadgets, Fashion & Clothing, Home & Living
  - Beauty & Health, Food & Beverages, Jewelry & Watches
  - Books & Stationery, Sports & Outdoors, Baby & Kids, Automotive
- [x] Category filter on Products page
- [x] Category selection when creating/editing products
- [x] Contact Us page
- [x] Dark premium UI with gold accents
- [x] Logo "A" branding as "Amazon Arab"
- [x] Database schema with RLS security policies
- [x] Rate limiting on sensitive endpoints
- [x] **Email Notifications (Resend)**:
  - Order placed confirmation to buyer (with crypto wallet)
  - Payment confirmed notification to buyer
  - New order notification to seller
  - New order notification to admin
  - Order completed notification to buyer
  - Order fulfilled notification to seller
  - Verification approved email to seller
  - Verification rejected email to seller (with reason)

## Complete User Flows (All Tested ✅)

### Flow 1: Seller Verification
1. Seller registers → Status: "unverified"
2. Seller goes to dashboard → Sees verification required
3. Seller enters invite code + uploads document
4. Status changes to "pending"
5. Admin approves → Status: "verified"

### Flow 2: Product Creation
1. Verified seller logs in
2. Goes to Seller Dashboard
3. Clicks "Add Product"
4. Fills title, description, price
5. Product appears on Products page with "Verified Seller" badge

### Flow 3: Buyer Checkout
1. Buyer browses Products page
2. Adds items to cart
3. Proceeds to checkout
4. Sees crypto wallet address + QR code
5. Confirms payment checkbox
6. Places order → Status: "pending_payment"

### Flow 4: Admin Order Management
1. Admin views Orders tab
2. Sees pending payments
3. Clicks "Confirm Payment" after verifying transaction
4. Order status → "paid"
5. Can mark as "completed" when fulfilled

## Database Schema (Supabase)
Tables use snake_case columns:
- `users`: id, email, name, role, verification_status, created_at
- `products`: id, title, description, price, images, seller_id, created_at
- `orders`: id, buyer_id, total_amount, payment_method, payment_wallet, payment_status, confirmed_by_admin, confirmed_at, created_at
- `order_items`: id, order_id, product_id, quantity, price
- `verification_documents`: id, user_id, document_type, document_url, status, merchant_invite_code, rejection_reason, reviewed_at, created_at
- `merchant_invite_codes`: id, code, is_used, created_by_admin, used_by_user_id, used_at, created_at

## API Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/products` - List all products
- `GET /api/products/my` - Seller's products
- `POST /api/products` - Create product (verified sellers)
- `PUT /api/products/{id}` - Update product
- `DELETE /api/products/{id}` - Delete product
- `POST /api/products/{id}/upload-image` - Upload product image
- `POST /api/orders` - Create order
- `GET /api/orders/my` - User's orders
- `PUT /api/orders/{id}/status` - Update order status (admin)
- `POST /api/verification/upload` - Upload verification document
- `GET /api/verification/documents` - Get verification documents
- `PUT /api/verification/documents/{id}/review` - Review document (admin)
- `GET /api/admin/users` - Get all users (admin)
- `POST /api/admin/invite-codes` - Create invite code (admin)
- `GET /api/admin/invite-codes` - Get all invite codes (admin)
- `GET /api/me` - Get current user info
- `POST /api/setup-admin` - One-time admin setup

## Test Credentials
- **Admin**: support@arabshopping.org / Hadi1247@
- **Seller**: testseller_new@test.com / TestPass123! (verified)
- **Buyer**: testbuyer_new@test.com / TestPass123!
- **Crypto Wallet**: TY8Z91NMCjREyZVj9NjDsF8hVjyqfxFFRU (USDT TRC20)

## Changelog

### 2026-01-07
- ✅ Fixed Supabase auth trigger issue (dropped conflicting trigger)
- ✅ Completed seller verification flow with document upload
- ✅ Tested product creation by verified seller
- ✅ Tested complete buyer checkout flow
- ✅ Tested admin order confirmation flow
- ✅ All 5 user flows fully functional and tested
- ✅ **Added Email Notifications via Resend**:
  - Buyer receives order confirmation with crypto wallet details
  - Buyer receives payment confirmation when admin confirms
  - Seller receives notification when their product is ordered
  - Admin receives notification for all new orders
- ✅ Testing: 100% of core flows passing

### 2026-01-06
- Fixed database schema (switched to snake_case columns)
- Updated backend to convert snake_case to camelCase for frontend
- Fixed admin setup endpoint to handle existing auth users
- Added RLS policies for merchant_invite_codes

## Future Enhancements (P2)
- Email notifications for orders
- Seller analytics dashboard
- Product search and filtering improvements
- Product categories
- Reviews and ratings system
- Multi-image product galleries
- Order tracking/shipping integration
