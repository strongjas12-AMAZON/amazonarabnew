# Amazon Arab - Premium Multi-Vendor Marketplace

A complete, production-ready multi-vendor marketplace with crypto payments, user verification, and admin management.

## 🌟 Features

### Core Functionality
- ✅ Multi-vendor marketplace (Admin, Seller, Buyer roles)
- ✅ Supabase Authentication & PostgreSQL Database
- ✅ USDT (TRC20) Crypto Payment System
- ✅ Manual Admin Payment Verification
- ✅ Seller Verification with Invite Codes
- ✅ Document Upload (ID & Business Documents)
- ✅ Product Management (CRUD with image upload)
- ✅ Shopping Cart & Checkout
- ✅ Order Management & Tracking
- ✅ Dark Luxury UI with Gold Accents

### Security
- 🔒 Supabase Row Level Security (RLS)
- 🔒 Admin-only payment confirmation
- 🔒 Role-based access control
- 🔒 Merchant invite code system
- 🔒 Document verification workflow

## 🚀 Quick Start

### 1. Database Setup

**IMPORTANT:** Run the database initialization script first!

1. Go to your Supabase Dashboard: https://supabase.com/dashboard
2. Select your project: `dqqmzatrxmueilsxvlgb`
3. Navigate to SQL Editor
4. Copy and paste the entire content from `/app/backend/init_database.sql`
5. Execute the SQL script
6. Create two storage buckets in Supabase Storage:
   - `products` (for product images)
   - `documents` (for verification documents)
   - Set both to **public** access

### 2. Setup Admin Account

The admin account must be created before you can use the system:

```bash
# Via API call
curl -X POST https://repo-clone-46.preview.emergentagent.com/api/setup-admin
```

**Admin Credentials:**
- Email: `support@arabshopping.org`


⚠️ **IMPORTANT:** This endpoint runs only once. After successful creation, it's disabled automatically.

### 3. Access Application

- Frontend: https://repo-clone-46.preview.emergentagent.com
- Backend API: https://repo-clone-46.preview.emergentagent.com/api

## 💳 Payment System

### USDT Wallet (Admin-Controlled)
- **Network:** TRC20 ONLY
- **Address:** 
- **QR Code:** Displayed at checkout
- **Verification:** Manual admin confirmation

⚠️ **WARNING:** Sending USDT via wrong network (ERC20/BEP20) will result in permanent loss!

## 📋 User Workflows

### For Buyers
1. Register with role "buyer"
2. Browse products from verified sellers
3. Add products to cart
4. Checkout with USDT (TRC20)
5. Scan QR code or copy wallet address
6. Confirm payment
7. Track order status

### For Sellers
1. Register with role "seller"
2. Upload verification documents with invite code
3. Wait for admin approval
4. Once verified, add products
5. Upload up to 10 images per product
6. Manage products and view orders

### For Admin
1. Login with admin credentials
2. Review seller verification documents
3. Create merchant invite codes
4. Confirm crypto payments manually
5. Manage all users and orders
6. Update order statuses

## 🔑 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user

### Products
- `GET /api/products` - Get all products
- `GET /api/products/my` - Get seller's products
- `POST /api/products` - Create product (seller)
- `PUT /api/products/:id` - Update product (seller)
- `DELETE /api/products/:id` - Delete product (seller)
- `POST /api/products/:id/upload-image` - Upload product image

### Orders
- `POST /api/orders` - Create order (buyer)
- `GET /api/orders/my` - Get user's orders
- `PUT /api/orders/:id/status` - Update order status (admin)

### Verification
- `POST /api/verification/upload` - Upload verification document
- `GET /api/verification/documents` - Get verification documents
- `PUT /api/verification/documents/:id/review` - Review document (admin)

### Admin
- `GET /api/admin/users` - Get all users
- `POST /api/admin/invite-codes` - Create invite code
- `GET /api/admin/invite-codes` - Get all invite codes
- `POST /api/setup-admin` - One-time admin setup

## 📦 Tech Stack

### Backend
- FastAPI + Supabase Python Client
- PostgreSQL (via Supabase)
- Supabase Storage
- Supabase Auth

### Frontend
- React 19
- React Router v7
- Supabase JS Client
- TailwindCSS
- Shadcn/UI Components
- Axios, Sonner, Lucide Icons

## ⚠️ Important Notes

1. **Database Schema:** MUST run `init_database.sql` in Supabase first
2. **Storage Buckets:** Create `products` and `documents` buckets in Supabase
3. **Admin Account:** Create admin account via `/api/setup-admin` endpoint
4. **Crypto Wallet:** Fixed admin wallet address for all payments
5. **Manual Verification:** All payments require manual admin confirmation
6. **Image Limit:** Maximum 10 images per product
7. **Network:** USDT must be sent on TRC20 network only

---

**Built for:** Multi-vendor luxury marketplace with secure crypto payments
