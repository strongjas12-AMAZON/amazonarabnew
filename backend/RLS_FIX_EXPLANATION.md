# Supabase RLS Infinite Recursion - Fixed

## 🔴 The Problem

### Error Message:
```
infinite recursion detected in policy for relation users
```

### Root Cause:

The original RLS policies had **self-referencing checks** that created circular dependencies:

```sql
-- BROKEN POLICY (OLD):
CREATE POLICY "Admin can read all users" ON users
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM users 
      WHERE id = auth.uid() AND role = 'admin'
    )
  );
```

### Why This Breaks:

1. **User tries to read from `users` table**
2. **RLS policy activates** to check permissions
3. **Policy tries to SELECT from `users` table** to check if user is admin
4. **This SELECT triggers the same policy again** (step 2)
5. **Infinite loop**: Check policy → Query users → Check policy → Query users → ...
6. **Supabase detects recursion and throws error**

### The Recursion Chain:

```
Query users table
    ↓
Policy checks: "Is user an admin?"
    ↓
Queries users table to check role
    ↓
Policy checks: "Is user an admin?"
    ↓
Queries users table to check role
    ↓
INFINITE RECURSION!
```

## ✅ The Solution

### Architecture Changes:

1. **Backend uses SERVICE_ROLE_KEY**
   - Bypasses ALL RLS policies automatically
   - Full database access for admin operations
   - Role validation in API layer (server.py)

2. **Frontend uses ANON_KEY**
   - Subject to RLS policies
   - Simple user-scoped policies only
   - No role checking in database policies

3. **No Self-Referencing Policies**
   - Policies NEVER query the table they're protecting
   - Use only `auth.uid()` comparisons
   - No `EXISTS (SELECT FROM users)` in user policies

### New Policy Structure:

#### ✅ SAFE: Direct UID Comparison
```sql
CREATE POLICY "users_select_own"
ON users FOR SELECT
TO authenticated
USING (auth.uid() = id);  -- Simple, no recursion
```

#### ❌ BROKEN: Self-Referencing Check
```sql
CREATE POLICY "admin_read_all"
ON users FOR SELECT
USING (
  EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'admin')
  -- ❌ Queries users FROM users policy = recursion!
);
```

## 📋 Fixed Policies Summary

### Users Table:
- ✅ Users read their own data (`auth.uid() = id`)
- ✅ Users can register (insert own record)
- ✅ Users can update their own data
- ✅ Admin operations via SERVICE_ROLE_KEY

### Products Table:
- ✅ Public read for all
- ✅ Sellers insert with their UID
- ✅ Sellers update/delete their own products

### Orders Table:
- ✅ Buyers read their own orders
- ✅ Buyers create orders with their UID
- ✅ Admin updates via SERVICE_ROLE_KEY

### Order Items Table:
- ✅ Read items for own orders (checks orders table, not users)
- ✅ Create items for own orders

### Verification Documents:
- ✅ Users read/create their own documents
- ✅ Admin reviews via SERVICE_ROLE_KEY

### Invite Codes:
- ✅ Anyone can read unused codes
- ✅ Admin creates/manages via SERVICE_ROLE_KEY

## 🔑 Key Concept: Service Role vs Anon Key

### SERVICE_ROLE_KEY (Backend):
```python
# Backend uses this
supabase_admin = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Bypasses ALL RLS policies
# Can read/write any data
# Used for admin operations
```

### ANON_KEY (Frontend):
```javascript
// Frontend uses this
const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)

// Subject to RLS policies
// Limited to user's own data
// Used for user operations
```

## 🛠️ How to Apply the Fix

### Step 1: Backup Your Data
```sql
-- In Supabase SQL Editor
-- Backup users table
CREATE TABLE users_backup AS SELECT * FROM users;
```

### Step 2: Run the Fix
1. Open Supabase Dashboard → SQL Editor
2. Copy contents of `/app/backend/fix_rls_policies.sql`
3. Paste and execute
4. Verify "RLS policies fixed successfully!" message

### Step 3: Verify No Recursion
```sql
-- Test query (should work without error)
SELECT * FROM users WHERE id = auth.uid();
```

### Step 4: Test Backend Operations
```bash
# Test admin endpoint
curl -X POST https://your-domain.com/api/setup-admin
```

## 🎯 Role Validation Strategy

### ❌ OLD (Broken):
```
Policy → Check users table for role → Recursion
```

### ✅ NEW (Fixed):
```
Frontend → API Request → Backend validates role → Uses SERVICE_ROLE_KEY → Success
```

### Example Flow:

1. **Seller tries to create product:**
   - Frontend sends request to `/api/products`
   - Backend checks: `if current_user['role'] != 'seller': raise 403`
   - Backend uses SERVICE_ROLE_KEY to create product
   - Returns success

2. **Admin approves verification:**
   - Frontend sends request to `/api/verification/documents/:id/review`
   - Backend checks: `if current_user['role'] != 'admin': raise 403`
   - Backend uses SERVICE_ROLE_KEY to update document
   - Returns success

## 📊 Before vs After

### Before (Broken):
```
❌ Policies check users table from users table
❌ Infinite recursion errors
❌ Database queries fail
❌ Authentication broken
```

### After (Fixed):
```
✅ Policies use simple auth.uid() checks
✅ No recursion errors
✅ Backend uses SERVICE_ROLE_KEY
✅ Frontend uses ANON_KEY
✅ Clean separation of concerns
```

## 🔍 Debugging RLS Issues

### Check Active Policies:
```sql
SELECT tablename, policyname, permissive, roles, cmd
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;
```

### Test Policy as User:
```sql
-- Simulate authenticated user
SET request.jwt.claims TO '{"sub": "test-user-id", "role": "authenticated"}';

-- Try query (should work)
SELECT * FROM users WHERE id = 'test-user-id';
```

### Check for Recursion:
```sql
-- If this hangs or errors, there's recursion
EXPLAIN SELECT * FROM users;
```

## 🚀 Best Practices

### DO ✅:
- Use SERVICE_ROLE_KEY in backend
- Use ANON_KEY in frontend
- Keep policies simple (auth.uid() only)
- Validate roles in backend API
- Use `USING (auth.uid() = column)` pattern

### DON'T ❌:
- Check users table FROM users policies
- Use complex EXISTS clauses on same table
- Validate roles in database policies
- Use SERVICE_ROLE_KEY in frontend
- Create circular policy dependencies

## 📝 Notes

1. **Admin operations always use SERVICE_ROLE_KEY** from backend
2. **Role validation happens in FastAPI** (server.py)
3. **RLS policies are user-scoped only** (not role-scoped)
4. **This is the recommended Supabase pattern** for multi-role apps
5. **Policies are simple and maintainable** without recursion risk

## ✅ Verification Checklist

After applying the fix:

- [ ] No "infinite recursion" errors
- [ ] Users can register successfully
- [ ] Users can login successfully
- [ ] Admin can create invite codes
- [ ] Sellers can create products (when verified)
- [ ] Buyers can place orders
- [ ] All API endpoints work
- [ ] No console errors in browser
- [ ] Backend logs show no RLS errors

## 🎉 Success!

Your RLS policies are now fixed and follow Supabase best practices!

The key takeaway: **Never check the same table a policy is protecting.**
