# Arab Shopping Marketplace - Product Requirements Document

## Project Overview
A luxury multi-vendor marketplace for the Arab market, featuring an admin-controlled product catalog system where sellers can browse and add products to their stores from a centrally managed catalog.

## Tech Stack
- **Frontend**: React, React Router, TailwindCSS
- **Backend**: FastAPI (Python)
- **Database**: Supabase (PostgreSQL with RLS)
- **Authentication**: Supabase client-side authentication
- **Storage**: Supabase Storage for product images
- **Email**: Resend for transactional emails

## Core Architecture

### Admin-Controlled Product Catalog (NEW - Implemented 2026-01-14)
1. **Admin-Only Product Management**: Only the admin can create, edit, and manage the central product catalog
2. **Central Catalog**: All products are managed centrally by admin with unique photos and descriptions
3. **Seller Product Selection**: Sellers browse the admin catalog and select products to add to their store
4. **Data Consistency**: Product details remain the same across all seller stores

### Key Endpoints
- `GET /api/products` - Public product listing
- `GET /api/admin/products` - Admin product management
- `POST /api/admin/products` - Admin creates product
- `PUT /api/admin/products/{id}` - Admin updates product
- `DELETE /api/admin/products/{id}` - Admin deletes product
- `POST /api/admin/seed-catalog` - Seed 100 products to catalog
- `DELETE /api/admin/clear-catalog` - Clear all products
- `GET /api/catalog/products` - Seller browses catalog
- `POST /api/seller/products/{id}` - Seller adds product to store (REQUIRES MANUAL DB SETUP)
- `DELETE /api/seller/products/{id}` - Seller removes from store (REQUIRES MANUAL DB SETUP)

## Completed Features

### Authentication System ✅
- Supabase client-side authentication
- Role-based access (admin, seller, buyer)
- Protected routes with role verification
- Session management with token refresh

### Admin Dashboard ✅
- Overview tab with stats (products, orders, users, revenue)
- Products tab with search, filter, and CRUD operations
- Seed 100 Products button (pre-populates catalog)
- Clear All button (removes products without orders)
- Orders tab with payment confirmation
- Users management
- Verification document review
- Invite code generation

### Seller Dashboard ✅
- My Store tab (shows selected products)
- Browse Catalog tab (100+ products with Add to Store)
- Orders tab (shows seller's orders)
- Verification status display
- Revenue tracking

### Product Catalog ✅
- 100 pre-seeded products across 7 categories:
  - Electronics (20)
  - Fashion (20)
  - Jewelry (15)
  - Beauty (15)
  - Home (15)
  - Sports (10)
  - Books (5)
- Each product has unique Unsplash images, descriptions, and prices
- Category filtering
- Search functionality

### Public Products Page ✅
- All products displayed with images
- Category filtering
- Search functionality
- Add to cart capability

## Known Limitations / Manual Setup Required

### seller_products Table
The `seller_products` junction table does NOT exist in Supabase. To enable seller "Add to Store" functionality, create this table manually in Supabase:

```sql
CREATE TABLE seller_products (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    seller_id UUID REFERENCES users(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    added_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,
    UNIQUE(seller_id, product_id)
);

CREATE INDEX idx_seller_products_seller_id ON seller_products(seller_id);
CREATE INDEX idx_seller_products_product_id ON seller_products(product_id);
```

## Test Credentials
- **Admin**: support@arabshopping.org / Hadi1247@
- **Verified Seller**: testseller_new@test.com / TestPass123!
- **Test Buyer**: testbuyer_new@test.com / TestPass123!

## Frontend Build Notes
Required installation process to fix dependency conflicts:
```bash
npm install --legacy-peer-deps
npm dedupe
npm run build
```

## Upcoming Tasks (P2-P3)
1. Product Reviews and Ratings
2. Seller Analytics Dashboard
3. Subcategories for products
4. Order Tracking/Shipping Integration
5. Email Notifications for Sellers

## File Structure
```
/app/
├── backend/
│   ├── server.py           # Main FastAPI app with all endpoints
│   ├── product_catalog.py  # 100 product definitions for seeding
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── pages/dashboard/
│   │   │   ├── AdminDashboard.js   # Admin product CRUD
│   │   │   ├── SellerDashboard.js  # Catalog browser
│   │   │   └── BuyerDashboard.js
│   │   ├── context/AuthContext.js
│   │   └── lib/
│   │       ├── api.js
│   │       ├── auth.js
│   │       └── supabase.js
│   └── package.json
├── tests/
│   └── test_product_catalog.py  # 16 API tests
└── memory/
    └── PRD.md
```

## Last Updated
2026-01-14 - Admin-controlled product catalog system implemented and tested
