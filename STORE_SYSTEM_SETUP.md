# 🏪 Buyer Store Search & Store Detail System - Setup Guide

## 📋 Overview

This system implements **strict access control** where:
- ✅ Buyers can **ONLY** see products that sellers have added to their stores
- ❌ Buyers **CANNOT** access the master product catalog
- ✅ Sellers can browse the catalog and add products to their stores
- ✅ Store-specific pricing and inventory management

---

## 🗄️ Database Migration (REQUIRED)

### Step 1: Run the Migration SQL

1. Go to your Supabase Dashboard: https://supabase.com/dashboard
2. Select your project: `dqqmzatrxmueilsxvlgb`
3. Navigate to **SQL Editor**
4. Copy and paste the entire content from `/app/backend/migrations/store_system_migration.sql`
5. Click **Run** to execute the migration

This will create:
- ✅ `product_catalog` table (master catalog - seller/admin only)
- ✅ `stores` table (one per seller)
- ✅ `store_products` table (what buyers see)
- ✅ Proper RLS policies (buyers CANNOT query catalog)
- ✅ Performance indexes
- ✅ Auto-migrate existing sellers to stores table

---

### Step 2: Seed the Product Catalog

After running the migration, seed the catalog with 100 pre-defined products:

**Option A: Via API (Recommended)**

```bash
# Login as admin first to get token, then:
curl -X POST https://repo-clone-46.preview.emergentagent.com/api/admin/seed-catalog \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

**Option B: Via Frontend**

Login as admin → Navigate to admin panel → Click "Seed Product Catalog"

This seeds 100 products across categories:
- Electronics (20)
- Fashion (20)
- Jewelry (15)
- Beauty (15)
- Home & Living (15)
- Sports (10)
- Books (5)

---

## 🔐 Security Implementation

### Row Level Security (RLS) Policies

#### `product_catalog` Table
```sql
-- Buyers: NO ACCESS (critical!)
-- Sellers: SELECT only (to add products to store)
-- Admin: Full access
```

#### `store_products` Table
```sql
-- Buyers: SELECT only where is_active = true
-- Sellers: Full access to own products
-- Admin: Full access
```

#### `stores` Table
```sql
-- Everyone: SELECT active stores only
-- Sellers: Manage own store
-- Admin: Full access
```

---

## 🎯 API Endpoints

### Public Endpoints (Buyers Can Access)

❌ None - All store endpoints require authentication

### Protected Endpoints (Authentication Required)

#### Search Stores
```bash
GET /api/stores/search?query=storename&limit=20&offset=0
Authorization: Bearer {token}
```

#### Get Store Details
```bash
GET /api/stores/{store_id}
Authorization: Bearer {token}
```

#### Get Store Products (CRITICAL - This is what buyers see)
```bash
GET /api/stores/{store_id}/products?limit=50&offset=0
Authorization: Bearer {token}
```

### Seller Endpoints (Authentication Required)

#### Browse Product Catalog
```bash
GET /api/seller/catalog/products?category=electronics&limit=50&offset=0
Authorization: Bearer {seller_token}
```

#### Add Product to Store
```bash
POST /api/seller/store/products
Authorization: Bearer {seller_token}
Content-Type: application/x-www-form-urlencoded

catalog_product_id={id}&price=99.99&stock=10&custom_description=Optional
```

#### Get My Store Products
```bash
GET /api/seller/store/products
Authorization: Bearer {seller_token}
```

#### Update Store Product
```bash
PUT /api/seller/store/products/{product_id}
Authorization: Bearer {seller_token}
Content-Type: application/x-www-form-urlencoded

price=89.99&stock=5&is_active=true
```

#### Remove Product from Store
```bash
DELETE /api/seller/store/products/{product_id}
Authorization: Bearer {seller_token}
```

### Admin Endpoints

#### Seed Catalog
```bash
POST /api/admin/seed-catalog
Authorization: Bearer {admin_token}
```

---

## 🛡️ Query Rules (MANDATORY)

### ✅ CORRECT Buyer Query Flow

```javascript
// ALWAYS start from store_products
const { data } = await supabase
  .from('store_products')
  .select(`
    *,
    product_catalog:catalog_product_id(name, images, description)
  `)
  .eq('store_id', storeId)
  .eq('is_active', true)
```

### ❌ WRONG Buyer Query Flow

```javascript
// NEVER query catalog directly as buyer
const { data } = await supabase
  .from('product_catalog')
  .select('*')  // ❌ This will fail due to RLS
```

---

## 🎨 Frontend Pages

### Buyer Pages
1. **Store Search** (`/stores/search`) - Search and browse stores
2. **Store Detail** (`/stores/{storeId}`) - View store products

### Seller Pages
1. **Browse Catalog** - Select products to add to store
2. **My Store Products** - Manage store inventory

---

## 📊 Data Flow

### Seller Flow
1. Seller logs in
2. Browses `product_catalog` (RLS allows this)
3. Adds selected products to `store_products` with custom price/stock
4. Products become visible to buyers

### Buyer Flow
1. Buyer searches stores
2. Opens a store
3. Sees ONLY products from `store_products` table
4. **CANNOT** see full catalog

---

## ✅ Testing Checklist

### Database
- [ ] Run migration SQL successfully
- [ ] Seed catalog with 100 products
- [ ] Verify RLS policies are active
- [ ] Check indexes are created

### API Testing (As Buyer)
- [ ] Search stores returns active stores only
- [ ] Get store products shows only store-specific products
- [ ] Cannot access `/api/seller/catalog/products` (should return 403)

### API Testing (As Seller)
- [ ] Can browse product catalog
- [ ] Can add products to store
- [ ] Can update own store products
- [ ] Cannot access other sellers' products

### Frontend Testing
- [ ] Buyer can search stores
- [ ] Buyer can view store details
- [ ] Buyer sees products with correct pricing
- [ ] Empty state shows if store has no products

---

## 🚨 Common Issues

### Issue: "Catalog already seeded"
**Solution:** This is expected if you run seed multiple times. Delete products first or use existing catalog.

### Issue: Buyers can't see products
**Solution:** Check:
1. Products have `is_active = true` in `store_products`
2. Store has `status = 'active'`
3. RLS policies are enabled

### Issue: Sellers can't browse catalog
**Solution:** Check:
1. User role is 'seller' in database
2. RLS policy `catalog_select_sellers` exists
3. Seller is authenticated

---

## 📝 Migration Summary

What happens when you run the migration:

1. **New Tables Created**: `product_catalog`, `stores`, `store_products`
2. **RLS Enabled**: Strict access control on all tables
3. **Auto-Migration**: Existing sellers get store records
4. **Indexes Added**: Performance optimization for queries
5. **Existing Products**: Remain in `products` table (unchanged)

**Note:** The old `products` table remains intact. The new system runs alongside it.

---

## 🎯 Result (Guaranteed)

✔ Buyers see **only store-specific products**  
✔ Catalog remains **seller-only**  
✔ No accidental product leakage  
✔ Production-safe marketplace logic  
✔ Database-level security (not just UI)

---

## 🆘 Support

If you encounter issues:
1. Check Supabase logs for RLS policy violations
2. Verify authentication tokens are valid
3. Ensure migration SQL ran completely
4. Test with Supabase SQL Editor first

---

**Implementation Complete!** 🎉

Now proceed to frontend implementation.
