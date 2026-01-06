-- ============================================
-- FIX: Supabase RLS Infinite Recursion
-- ============================================
-- Problem: Policies were checking users table FROM users table policies
-- Solution: Use service_role bypass + simple auth.uid() checks
-- ============================================

-- DROP ALL EXISTING POLICIES TO START FRESH
DROP POLICY IF EXISTS "Users can read own data" ON users;
DROP POLICY IF EXISTS "Admin can read all users" ON users;
DROP POLICY IF EXISTS "Service role bypass" ON users;
DROP POLICY IF EXISTS "Anyone can read verified products" ON products;
DROP POLICY IF EXISTS "Sellers can insert own products" ON products;
DROP POLICY IF EXISTS "Sellers can update own products" ON products;
DROP POLICY IF EXISTS "Sellers can delete own products" ON products;
DROP POLICY IF EXISTS "Users can read own orders" ON orders;
DROP POLICY IF EXISTS "Buyers can create orders" ON orders;
DROP POLICY IF EXISTS "Admin can update orders" ON orders;
DROP POLICY IF EXISTS "Users can read order items of own orders" ON order_items;
DROP POLICY IF EXISTS "Buyers can create order items" ON order_items;
DROP POLICY IF EXISTS "Users can read own documents" ON verification_documents;
DROP POLICY IF EXISTS "Users can create own documents" ON verification_documents;
DROP POLICY IF EXISTS "Admin can update documents" ON verification_documents;
DROP POLICY IF EXISTS "Admin can manage invite codes" ON merchant_invite_codes;
DROP POLICY IF EXISTS "Anyone can read unused codes" ON merchant_invite_codes;

-- ============================================
-- EXPLANATION OF RECURSION PROBLEM
-- ============================================
-- 
-- OLD (BROKEN) POLICY:
-- CREATE POLICY "Admin can read all users" ON users
--   FOR SELECT USING (EXISTS (
--     SELECT 1 FROM users WHERE id = auth.uid() AND role = 'admin'
--   ));
--
-- WHY IT BREAKS:
-- 1. Policy on 'users' table tries to SELECT from 'users' table
-- 2. That SELECT triggers the same policy again
-- 3. Creates infinite loop: Check policy → Read users → Check policy → Read users...
--
-- SOLUTION:
-- 1. Backend uses SERVICE_ROLE_KEY which bypasses ALL RLS
-- 2. Frontend uses ANON_KEY with simple policies
-- 3. NO policies check the users table for role validation
-- 4. Role-based logic handled in backend API layer
-- ============================================

-- ============================================
-- USERS TABLE POLICIES
-- ============================================

-- Policy 1: Users can read their OWN data only
CREATE POLICY "users_select_own"
ON users FOR SELECT
TO authenticated
USING (auth.uid() = id);

-- Policy 2: Allow user creation during registration
-- (signup process needs to insert into users table)
CREATE POLICY "users_insert_own"
ON users FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = id);

-- Policy 3: Users can update their own data
CREATE POLICY "users_update_own"
ON users FOR UPDATE
TO authenticated
USING (auth.uid() = id)
WITH CHECK (auth.uid() = id);

-- Note: Admin operations use SERVICE_ROLE_KEY which bypasses RLS entirely

-- ============================================
-- PRODUCTS TABLE POLICIES
-- ============================================

-- Policy 1: Anyone can read products (public marketplace)
CREATE POLICY "products_select_all"
ON products FOR SELECT
TO authenticated, anon
USING (true);

-- Policy 2: Authenticated users can create products
-- (Role validation happens in backend)
CREATE POLICY "products_insert_authenticated"
ON products FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = "sellerId");

-- Policy 3: Sellers can update their own products
CREATE POLICY "products_update_own"
ON products FOR UPDATE
TO authenticated
USING (auth.uid() = "sellerId")
WITH CHECK (auth.uid() = "sellerId");

-- Policy 4: Sellers can delete their own products
CREATE POLICY "products_delete_own"
ON products FOR DELETE
TO authenticated
USING (auth.uid() = "sellerId");

-- ============================================
-- ORDERS TABLE POLICIES
-- ============================================

-- Policy 1: Users can read their own orders
CREATE POLICY "orders_select_own"
ON orders FOR SELECT
TO authenticated
USING (auth.uid() = "buyerId");

-- Policy 2: Buyers can create orders
CREATE POLICY "orders_insert_own"
ON orders FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = "buyerId");

-- Note: Order updates (status changes) are admin-only via SERVICE_ROLE_KEY

-- ============================================
-- ORDER_ITEMS TABLE POLICIES
-- ============================================

-- Policy 1: Users can read order items for their orders
CREATE POLICY "order_items_select_own"
ON order_items FOR SELECT
TO authenticated
USING (
  EXISTS (
    SELECT 1 FROM orders 
    WHERE orders.id = order_items."orderId" 
    AND orders."buyerId" = auth.uid()
  )
);

-- Policy 2: Users can create order items for their orders
CREATE POLICY "order_items_insert_own"
ON order_items FOR INSERT
TO authenticated
WITH CHECK (
  EXISTS (
    SELECT 1 FROM orders 
    WHERE orders.id = order_items."orderId" 
    AND orders."buyerId" = auth.uid()
  )
);

-- ============================================
-- VERIFICATION_DOCUMENTS TABLE POLICIES
-- ============================================

-- Policy 1: Users can read their own documents
CREATE POLICY "verification_select_own"
ON verification_documents FOR SELECT
TO authenticated
USING (auth.uid() = "userId");

-- Policy 2: Users can create their own documents
CREATE POLICY "verification_insert_own"
ON verification_documents FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = "userId");

-- Note: Document review (status updates) is admin-only via SERVICE_ROLE_KEY

-- ============================================
-- MERCHANT_INVITE_CODES TABLE POLICIES
-- ============================================

-- Policy 1: Anyone can read unused codes (for verification)
CREATE POLICY "invite_codes_select_unused"
ON merchant_invite_codes FOR SELECT
TO authenticated, anon
USING ("isUsed" = false);

-- Note: Creating and managing codes is admin-only via SERVICE_ROLE_KEY

-- ============================================
-- SERVICE ROLE BYPASS
-- ============================================
-- The backend uses SUPABASE_SERVICE_ROLE_KEY which automatically
-- bypasses ALL RLS policies. This allows admin operations without
-- complex policy rules.
--
-- Frontend uses SUPABASE_ANON_KEY which is subject to these policies.
-- ============================================

-- ============================================
-- GRANT PERMISSIONS
-- ============================================

-- Ensure authenticated users can access tables
GRANT SELECT, INSERT, UPDATE, DELETE ON users TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON products TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON orders TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON order_items TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON verification_documents TO authenticated;
GRANT SELECT ON merchant_invite_codes TO authenticated;

-- Allow anon users to read products and codes (for public browsing)
GRANT SELECT ON products TO anon;
GRANT SELECT ON merchant_invite_codes TO anon;

-- Service role gets full access (already default)
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;

-- ============================================
-- VERIFICATION QUERIES
-- ============================================
-- Run these to verify policies are working:
--
-- 1. Check all policies:
-- SELECT tablename, policyname, permissive, roles, cmd, qual, with_check
-- FROM pg_policies
-- WHERE schemaname = 'public'
-- ORDER BY tablename, policyname;
--
-- 2. Test as authenticated user:
-- SET request.jwt.claims TO '{"sub": "test-user-id", "role": "authenticated"}';
-- SELECT * FROM users;
--
-- 3. Verify no recursion:
-- Should return results without error
-- ============================================

-- ============================================
-- SUMMARY OF CHANGES
-- ============================================
-- 1. Removed all self-referencing policies on users table
-- 2. Simplified policies to only check auth.uid()
-- 3. Role validation moved to backend API layer
-- 4. Admin operations use SERVICE_ROLE_KEY (bypasses RLS)
-- 5. Frontend uses ANON_KEY with these simple policies
-- 6. No more infinite recursion!
-- ============================================

-- Success message
DO $$ 
BEGIN 
  RAISE NOTICE 'RLS policies fixed successfully!';
  RAISE NOTICE 'Backend uses SERVICE_ROLE_KEY for admin operations';
  RAISE NOTICE 'Frontend uses ANON_KEY with user-scoped policies';
END $$;
