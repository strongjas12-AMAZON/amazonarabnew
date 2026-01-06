-- ============================================
-- SECURITY FIXES - Amazon Arab Marketplace
-- ============================================
-- Apply these fixes to resolve critical vulnerabilities
-- Run in Supabase SQL Editor
-- ============================================

-- ============================================
-- FIX #1: Prevent Role Escalation
-- ============================================

-- Drop the overly permissive update policy
DROP POLICY IF EXISTS "users_update_own" ON users;

-- Create restrictive update policy that prevents role/status changes
CREATE POLICY "users_update_profile_only"
ON users FOR UPDATE
TO authenticated
USING (auth.uid() = id)
WITH CHECK (
    auth.uid() = id AND
    -- Ensure role cannot be changed (must match current value)
    role = (SELECT role FROM users WHERE id = auth.uid()) AND
    -- Ensure verificationStatus cannot be changed (must match current value)
    "verificationStatus" = (SELECT "verificationStatus" FROM users WHERE id = auth.uid())
);

-- Alternative: Even more restrictive - only allow specific fields
-- Uncomment if you want to explicitly control which fields can be updated
/*
CREATE POLICY "users_update_name_only"
ON users FOR UPDATE
TO authenticated
USING (auth.uid() = id)
WITH CHECK (
    auth.uid() = id AND
    -- Only these fields can be updated by users
    role = (SELECT role FROM users WHERE id = auth.uid()) AND
    "verificationStatus" = (SELECT "verificationStatus" FROM users WHERE id = auth.uid()) AND
    email = (SELECT email FROM users WHERE id = auth.uid())
    -- Allow: name updates
    -- Prevent: role, verificationStatus, email changes
);
*/

-- ============================================
-- FIX #2: Secure Verification Documents
-- ============================================

-- Add Storage RLS Policies for documents bucket

-- Policy 1: Users can only upload to their own folder
CREATE POLICY "users_upload_own_documents"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
    bucket_id = 'documents' AND
    (storage.foldername(name))[1] = auth.uid()::text
);

-- Policy 2: Users can only read their own documents
CREATE POLICY "users_read_own_documents"  
ON storage.objects FOR SELECT
TO authenticated
USING (
    bucket_id = 'documents' AND
    (storage.foldername(name))[1] = auth.uid()::text
);

-- Policy 3: Users can only delete their own documents
CREATE POLICY "users_delete_own_documents"
ON storage.objects FOR DELETE
TO authenticated
USING (
    bucket_id = 'documents' AND
    (storage.foldername(name))[1] = auth.uid()::text
);

-- Note: Admin access via SERVICE_ROLE_KEY automatically bypasses these policies

-- ============================================
-- VERIFICATION QUERIES
-- ============================================

-- Test #1: Verify role escalation is blocked
-- Should return: new row violates row-level security policy
-- SELECT * FROM users WHERE id = auth.uid();
-- UPDATE users SET role = 'admin' WHERE id = auth.uid();  -- Should FAIL

-- Test #2: Verify profile updates still work
-- SELECT * FROM users WHERE id = auth.uid();
-- UPDATE users SET name = 'New Name' WHERE id = auth.uid();  -- Should SUCCEED

-- Test #3: Check policies are active
SELECT tablename, policyname, permissive, roles, cmd
FROM pg_policies
WHERE schemaname = 'public' AND tablename = 'users'
ORDER BY policyname;

-- Test #4: Check storage policies
SELECT * FROM storage.policies
WHERE bucket_id = 'documents'
ORDER BY name;

-- ============================================
-- ROLLBACK (if needed)
-- ============================================

-- If fixes cause issues, rollback with:
/*
-- Rollback users policy
DROP POLICY IF EXISTS "users_update_profile_only" ON users;
DROP POLICY IF EXISTS "users_update_name_only" ON users;

-- Restore original (INSECURE) policy
CREATE POLICY "users_update_own"
ON users FOR UPDATE
TO authenticated
USING (auth.uid() = id)
WITH CHECK (auth.uid() = id);

-- Rollback storage policies
DROP POLICY IF EXISTS "users_upload_own_documents" ON storage.objects;
DROP POLICY IF EXISTS "users_read_own_documents" ON storage.objects;
DROP POLICY IF EXISTS "users_delete_own_documents" ON storage.objects;
*/

-- ============================================
-- ADDITIONAL RECOMMENDED POLICIES
-- ============================================

-- Prevent users from deleting their own account
CREATE POLICY "users_no_self_delete"
ON users FOR DELETE
TO authenticated
USING (false);  -- Nobody can delete via client

-- Only allow admin to delete users (via SERVICE_ROLE_KEY)

-- ============================================
-- SUCCESS MESSAGE
-- ============================================

DO $$ 
BEGIN 
  RAISE NOTICE '========================================';
  RAISE NOTICE 'Security fixes applied successfully!';
  RAISE NOTICE '========================================';
  RAISE NOTICE 'Fixed:';
  RAISE NOTICE '1. Role escalation prevention';
  RAISE NOTICE '2. Verification status protection';
  RAISE NOTICE '3. Document storage security';
  RAISE NOTICE '========================================';
  RAISE NOTICE 'Next steps:';
  RAISE NOTICE '1. Test user profile updates';
  RAISE NOTICE '2. Update backend for signed URLs';
  RAISE NOTICE '3. Add rate limiting to backend';
  RAISE NOTICE '========================================';
END $$;
