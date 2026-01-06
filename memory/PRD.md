# Amazon Arab - Multi-Vendor Marketplace PRD

## Project Overview
A premium multi-vendor marketplace with dark UI and gold accents, featuring crypto payments (USDT TRC20).

## Tech Stack
- **Frontend**: React + TailwindCSS + shadcn/ui
- **Backend**: FastAPI (Python)
- **Database**: Supabase (PostgreSQL with RLS)
- **Storage**: Supabase Storage (documents bucket - private, products bucket - public)
- **Authentication**: Supabase Auth + JWT

## User Roles
1. **Admin** - Manages users, verifications, orders, invite codes
2. **Seller** - Creates products, views orders (requires verification + invite code)
3. **Buyer** - Browses products, places orders (requires verification for checkout)

## Core Features

### ✅ Implemented
- [x] User registration (buyer/seller roles)
- [x] User authentication (login/logout)
- [x] Admin dashboard with stats
- [x] Admin: View all users
- [x] Admin: Create/view merchant invite codes
- [x] Admin: View pending verifications
- [x] Admin: Order management (confirm payments, complete orders)
- [x] Products listing page
- [x] Contact Us page
- [x] Dark premium UI with gold accents
- [x] Logo "A" branding as "Amazon Arab"
- [x] Database schema with RLS security policies
- [x] Rate limiting on sensitive endpoints

### 🔄 Partially Implemented
- [ ] Seller Dashboard - View Orders (placeholder exists)
- [ ] Buyer Dashboard - Order History (placeholder exists)
- [ ] Document verification flow (backend ready, needs full testing)
- [ ] Crypto checkout with QR code (UI exists, needs e2e testing)

### 📋 Not Yet Implemented
- [ ] Product image uploads via Supabase Storage
- [ ] Product CRUD for verified sellers
- [ ] Shopping cart persistence
- [ ] Order email notifications
- [ ] Seller revenue tracking

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

## Credentials
- **Admin**: support@arabshopping.org / Hadi1247@
- **Crypto Wallet**: TY8Z91NMCjREyZVj9NjDsF8hVjyqfxFFRU (USDT TRC20)

## Changelog

### 2026-01-06
- Fixed database schema (switched to snake_case columns)
- Updated backend to convert snake_case to camelCase for frontend
- Fixed admin setup endpoint to handle existing auth users
- Added RLS policies for merchant_invite_codes (admin insert/update/delete)
- All core admin features tested and working
- Testing: 93% backend tests passing, 100% frontend pages working

## Next Priority Tasks (P0/P1)
1. Complete seller verification flow testing
2. Implement product creation with image uploads
3. Complete buyer checkout flow with crypto payment
4. Add seller dashboard order viewing functionality
5. Add buyer dashboard order history

## Future Enhancements (P2)
- Email notifications for orders
- Seller analytics dashboard
- Product search and filtering
- Product categories
- Reviews and ratings system
