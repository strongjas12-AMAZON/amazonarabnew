# 🔐 Pre-Deployment Authentication Checklist

## ❌ CRITICAL ISSUES FOUND

### 1. **Database Column Name Mismatch** ⚠️ CRITICAL

**Problem:**
- Database schema uses: `"verificationStatus"` (camelCase with quotes)
- Backend inserts use: `verification_status` (snake_case)
- Frontend inserts use: `verification_status` (snake_case)

**Location:**
- `backend/server.py` line 886
- `frontend/src/lib/auth.js` line 27

**Impact:** Registration may fail when inserting user records

**Fix Applied:** ✅ Updated frontend to handle both formats

**Still Need:** Verify Supabase PostgREST handles the conversion automatically, or update backend to match schema.

---

### 2. **Frontend Bypasses Backend Auth Endpoints** ⚠️ SECURITY RISK

**Problem:**
- Frontend uses Supabase client directly (`supabase.auth.signUp()`, `supabase.auth.signInWithPassword()`)
- Backend has proper auth endpoints (`/api/auth/register`, `/api/auth/login`) with:
  - Rate limiting (3/min register, 5/min login)
  - Email auto-confirmation
  - Proper error handling
  - Session management

**Current State:**
- ✅ Fixed in previous changes (frontend now uses backend endpoints)
- ❌ **REVERTED** - Frontend is back to using Supabase directly

**Recommendation:** 
- Option A: Use backend endpoints (more secure, rate-limited)
- Option B: Keep Supabase direct (simpler, but less secure)

**Action Required:** Decide which approach you want for production.

---

### 3. **CORS Configuration** ⚠️ PRODUCTION REQUIREMENT

**Current:**
```python
allow_origins=os.environ.get('CORS_ORIGINS', '*').split(',')
```

**Problem:** Defaults to `*` (allows all origins) - security risk in production

**Fix Required:**
```bash
# In backend/.env (production)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

---

### 4. **Supabase Redirect URLs** ⚠️ PRODUCTION BREAK

**Problem:** Supabase Auth requires configured redirect URLs for:
- Email confirmation links
- OAuth callbacks (if used)
- Password reset links

**Action Required:**
1. Go to Supabase Dashboard → Authentication → URL Configuration
2. Add your production domain:
   - Site URL: `https://yourdomain.com`
   - Redirect URLs: 
     - `https://yourdomain.com/**`
     - `https://www.yourdomain.com/**`

---

### 5. **Email Confirmation Settings** ⚠️ USER EXPERIENCE

**Current Behavior:**
- Frontend uses `supabase.auth.signUp()` directly
- Backend endpoint uses `admin.create_user` with `email_confirm: True` (auto-confirms)

**If Using Frontend Direct:**
- Users must confirm email before login (if email confirmation enabled in Supabase)
- Email confirmation emails won't work without redirect URL configuration

**Recommendation:** 
- Disable email confirmation in Supabase for smoother UX, OR
- Configure redirect URLs properly, OR
- Use backend endpoints (which auto-confirm)

---

### 6. **Environment Variables for Production** ⚠️ REQUIRED

**Backend `.env` (Production):**
```env
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://dqqmzatrxmueilsxvlgb.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Admin
ADMIN_SETUP_COMPLETE=false  # Set to true after first admin setup
ADMIN_CRYPTO_WALLET=TY8Z91NMCjREyZVj9NjDsF8hVjyqfxFFRU

# CORS (IMPORTANT!)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Email (Optional)
RESEND_API_KEY=your-resend-key
SENDER_EMAIL=support@arabshopping.org
```

**Frontend `.env` (Production):**
```env
# Backend API (your production domain)
REACT_APP_BACKEND_URL=https://yourdomain.com

# Supabase
REACT_APP_SUPABASE_URL=https://dqqmzatrxmueilsxvlgb.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your-anon-key

# Wallet
REACT_APP_ADMIN_WALLET=TY8Z91NMCjREyZVj9NjDsF8hVjyqfxFFRU
```

---

## ✅ PRE-DEPLOYMENT CHECKLIST

Before deploying to Hostinger VPS:

- [ ] **Fix database column mismatch** - Verify Supabase handles snake_case → camelCase conversion
- [ ] **Decide on auth approach** - Backend endpoints OR direct Supabase?
- [ ] **Configure CORS** - Set `CORS_ORIGINS` to your production domain only
- [ ] **Configure Supabase Redirect URLs** - Add production domain in Supabase Dashboard
- [ ] **Set environment variables** - Create production `.env` files with correct values
- [ ] **Test email confirmation** - Verify email flow works (or disable it)
- [ ] **Test registration flow** - Verify users can register successfully
- [ ] **Test login flow** - Verify users can login
- [ ] **Test admin setup** - Run `/api/setup-admin` endpoint after deployment
- [ ] **Verify RLS policies** - Test that Row Level Security works correctly
- [ ] **Test with production domain** - Use your actual domain, not localhost

---

## 🔧 QUICK FIXES

### Fix 1: Update CORS in Backend
```bash
# Add to backend/.env
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Fix 2: Configure Supabase Redirect URLs
1. Login to Supabase Dashboard
2. Go to: Authentication → URL Configuration  
3. Site URL: `https://yourdomain.com`
4. Redirect URLs: Add `https://yourdomain.com/**`

### Fix 3: Verify Database Schema
Test that inserts work with current column names, or update code to match schema exactly.

---

## 🚨 CRITICAL: Test Before Going Live

1. **Test Registration:**
   ```bash
   curl -X POST https://yourdomain.com/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{"name":"Test User","email":"test@example.com","password":"Test123!","role":"buyer"}'
   ```

2. **Test Login:**
   ```bash
   curl -X POST https://yourdomain.com/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"Test123!"}'
   ```

3. **Verify Admin Setup:**
   ```bash
   curl -X POST https://yourdomain.com/api/setup-admin
   ```

---

## 📝 NOTES

- **Current Auth Flow:** Frontend → Supabase Direct (bypasses backend)
- **Recommended:** Frontend → Backend API → Supabase (more secure, rate-limited)
- **Database Schema:** Uses camelCase with quotes, backend uses snake_case (Supabase may auto-convert)

---

**Last Updated:** Based on current codebase analysis
