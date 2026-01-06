# 🚀 PRODUCTION DEPLOYMENT CHECKLIST - Amazon Arab Marketplace
## For Real Users - Complete Step-by-Step Guide

---

## ⚠️ CRITICAL: READ THIS FIRST

This deployment is for **REAL USERS** with **REAL MONEY** (crypto payments).

**DO NOT SKIP ANY STEPS**

Estimated Time: 2-3 hours  
Difficulty: Intermediate  
Prerequisites: VPS with root access, domain name, Supabase account

---

## 📋 PRE-DEPLOYMENT CHECKLIST

### Before You Start:
- [ ] VPS with Ubuntu 20.04+ (minimum 2GB RAM, 2 CPU cores)
- [ ] Domain name pointing to VPS IP
- [ ] SSH access to VPS
- [ ] Supabase account created
- [ ] Backup of current code (if updating)
- [ ] Admin password ready (change from default)

---

## 🗄️ PHASE 1: SUPABASE SETUP (30 minutes)

### Step 1.1: Create Supabase Project
```
1. Go to: https://supabase.com/dashboard
2. Click "New Project"
3. Project Name: amazonarab-prod
4. Database Password: [STRONG PASSWORD - SAVE THIS]
5. Region: Choose closest to your users
6. Wait 2-3 minutes for project creation
```

**✅ Checkpoint:** Project status shows "Healthy" in green

---

### Step 1.2: Run Database Schema

```
1. Open Supabase Dashboard → SQL Editor
2. Copy ENTIRE content from /app/backend/init_database.sql
3. Paste into SQL Editor
4. Click "Run"
5. Wait for "Success" message
```

**Verify Tables Created:**
```sql
-- Run this query to verify
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY table_name;

-- Should show:
-- merchant_invite_codes
-- order_items
-- orders
-- products
-- users
-- verification_documents
```

**✅ Checkpoint:** All 6 tables exist, no errors

---

### Step 1.3: Apply Security Fixes

```
1. Still in SQL Editor
2. Copy ENTIRE content from /app/backend/security_fixes.sql
3. Paste and click "Run"
4. Verify success message appears
```

**Verify RLS Policies:**
```sql
-- Run this query
SELECT tablename, policyname 
FROM pg_policies 
WHERE schemaname = 'public'
ORDER BY tablename, policyname;

-- Should show policies for all tables
```

**✅ Checkpoint:** "Security fixes applied successfully!" message appears

---

### Step 1.4: Create Storage Buckets

**Products Bucket (PUBLIC):**
```
1. Supabase Dashboard → Storage
2. Click "New bucket"
3. Name: products
4. Public bucket: YES (toggle ON)
5. File size limit: 10MB
6. Allowed MIME types: image/jpeg, image/png, image/webp
7. Click "Create bucket"
```

**Documents Bucket (PRIVATE):**
```
1. Click "New bucket" again
2. Name: documents
3. Public bucket: NO (toggle OFF) ← CRITICAL
4. File size limit: 10MB
5. Allowed MIME types: image/jpeg, image/png, application/pdf
6. Click "Create bucket"
```

**✅ Checkpoint:** Two buckets exist (products=public, documents=private)

---

### Step 1.5: Get Supabase Credentials

```
1. Supabase Dashboard → Settings → API
2. Copy and SAVE these values:

Project URL: https://[your-project].supabase.co
anon public key: eyJhbGci... (starts with eyJ)
service_role key: eyJhbGci... (starts with eyJ, DIFFERENT from anon)

⚠️ NEVER expose service_role key to frontend!
⚠️ Keep these credentials SECURE
```

**✅ Checkpoint:** You have 3 values saved (URL + 2 keys)

---

## 🔐 PHASE 2: SECURITY SETUP (20 minutes)

### Step 2.1: Change Admin Password

**Current Default:**
```
Email: support@arabshopping.org
Password: Hadi1247@  ← MUST CHANGE THIS
```

**Generate Strong Password:**
```bash
# On your local machine
openssl rand -base64 32

# Or use: https://passwordsgenerator.net/
# Requirements: 
# - Minimum 16 characters
# - Include uppercase, lowercase, numbers, symbols
# - No dictionary words
```

**Update in Code:**
```bash
# Edit /app/backend/server.py line 107
# Change from:
admin_password = "Hadi1247@"

# Change to:
admin_password = "YOUR_STRONG_PASSWORD_HERE"

⚠️ Save this password in your password manager
⚠️ DO NOT commit this to git
```

**✅ Checkpoint:** Strong password generated and saved securely

---

### Step 2.2: Verify Wallet Address

**CRITICAL CHECK:**
```bash
# Verify in both files:
grep "ADMIN_WALLET\|ADMIN_CRYPTO_WALLET" /app/backend/.env /app/frontend/.env

# Should show:
# TY8Z91NMCjREyZVj9NjDsF8hVjyqfxFFRU

⚠️ This is YOUR wallet - all payments go here
⚠️ Verify you control this wallet
⚠️ Test by sending $1 USDT to it first
```

**Test Wallet Access:**
```
1. Open TronLink wallet or TronScan
2. Paste address: TY8Z91NMCjREyZVj9NjDsF8hVjyqfxFFRU
3. Send $1 USDT (TRC20 network) as test
4. Verify you receive it
5. If received, proceed. If not, STOP and fix wallet.
```

**✅ Checkpoint:** You can receive USDT at the wallet address

---

### Step 2.3: Prepare Environment Variables

**Backend .env (Production):**
```bash
# Create: /app/backend/.env.production

# MongoDB (not used but required by template)
MONGO_URL=mongodb://localhost:27017
DB_NAME=prod_database

# CORS (your domain)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Supabase (from Step 1.5)
NEXT_PUBLIC_SUPABASE_URL=https://[your-project].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGci...YOUR_ANON_KEY...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...YOUR_SERVICE_KEY...

# Admin Setup
ADMIN_SETUP_COMPLETE=false
ADMIN_CRYPTO_WALLET=TY8Z91NMCjREyZVj9NjDsF8hVjyqfxFFRU
```

**Frontend .env (Production):**
```bash
# Create: /app/frontend/.env.production

# Backend API (your domain)
REACT_APP_BACKEND_URL=https://yourdomain.com

# Socket (for hot reload - production doesn't need this)
WDS_SOCKET_PORT=443
ENABLE_HEALTH_CHECK=false

# Supabase (same as backend)
REACT_APP_SUPABASE_URL=https://[your-project].supabase.co
REACT_APP_SUPABASE_ANON_KEY=eyJhbGci...YOUR_ANON_KEY...

# Wallet
REACT_APP_ADMIN_WALLET=TY8Z91NMCjREyZVj9NjDsF8hVjyqfxFFRU
```

**✅ Checkpoint:** Both .env.production files created with correct values

---

## 🖥️ PHASE 3: VPS SETUP (45 minutes)

### Step 3.1: Connect to VPS

```bash
ssh root@YOUR_VPS_IP

# Or if using key:
ssh -i ~/.ssh/your-key.pem root@YOUR_VPS_IP
```

**✅ Checkpoint:** Successfully connected to VPS

---

### Step 3.2: Install Dependencies

```bash
# Update system
apt update && apt upgrade -y

# Install Node.js 18.x
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs

# Install Python 3.11
apt install -y python3.11 python3.11-venv python3-pip

# Install Nginx
apt install -y nginx

# Install Yarn
npm install -g yarn

# Install PM2
npm install -g pm2

# Install certbot for SSL
apt install -y certbot python3-certbot-nginx

# Verify installations
node --version    # Should be v18.x
python3.11 --version  # Should be 3.11.x
nginx -v          # Should show version
pm2 --version     # Should show version
```

**✅ Checkpoint:** All dependencies installed, versions verified

---

### Step 3.3: Upload Application

**Option A: Via Git (Recommended)**
```bash
# On VPS
cd /var/www
git clone YOUR_REPO_URL amazonarab
cd amazonarab

# Copy production env files
cp /app/backend/.env.production /var/www/amazonarab/backend/.env
cp /app/frontend/.env.production /var/www/amazonarab/frontend/.env
```

**Option B: Via SCP**
```bash
# On your local machine
scp -r /app root@YOUR_VPS_IP:/var/www/amazonarab
```

**Option C: Via SFTP**
```
Use FileZilla or similar:
1. Connect to YOUR_VPS_IP
2. Upload /app folder to /var/www/amazonarab
```

**✅ Checkpoint:** Application files on VPS at /var/www/amazonarab

---

### Step 3.4: Setup Backend

```bash
cd /var/www/amazonarab/backend

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep -i supabase
# Should show: supabase, postgrest-py, realtime-py, etc.

# Test backend (should start without errors)
python server.py &
sleep 5
curl http://localhost:8001/api/me || echo "Needs auth token - this is expected"
pkill -f "python server.py"
```

**✅ Checkpoint:** Backend dependencies installed, server can start

---

### Step 3.5: Setup Frontend

```bash
cd /var/www/amazonarab/frontend

# Install dependencies
yarn install

# Build for production
NODE_ENV=production yarn build

# Verify build
ls -la build/
# Should show: index.html, static/, asset-manifest.json

# Check build size
du -sh build/
# Should be reasonable (< 50MB)
```

**⚠️ If build fails:**
```bash
# Increase memory limit
export NODE_OPTIONS="--max-old-space-size=4096"
yarn build
```

**✅ Checkpoint:** Frontend built successfully, build/ folder exists

---

## 🔒 PHASE 4: NGINX & SSL SETUP (30 minutes)

### Step 4.1: Configure Nginx

```bash
# Create Nginx config
nano /etc/nginx/sites-available/amazonarab
```

**Paste this configuration:**
```nginx
# HTTP (will redirect to HTTPS after SSL)
server {
    listen 80;
    listen [::]:80;
    server_name yourdomain.com www.yourdomain.com;

    # Let's Encrypt verification
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    # Redirect to HTTPS (after SSL is set up)
    # location / {
    #     return 301 https://$server_name$request_uri;
    # }

    # Temporary: serve site over HTTP first
    location / {
        root /var/www/amazonarab/frontend/build;
        try_files $uri /index.html;
        
        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Security: Block access to sensitive files
    location ~ /\. {
        deny all;
    }
    
    location ~ /\.env {
        deny all;
    }
}
```

**Enable site:**
```bash
# Create symlink
ln -s /etc/nginx/sites-available/amazonarab /etc/nginx/sites-enabled/

# Remove default site
rm /etc/nginx/sites-enabled/default

# Test configuration
nginx -t
# Should show: "test is successful"

# Reload Nginx
systemctl reload nginx
```

**✅ Checkpoint:** Nginx configured and running

---

### Step 4.2: Test Domain (Before SSL)

```bash
# On VPS - check if domain resolves
dig +short yourdomain.com
# Should show your VPS IP

# Test HTTP access
curl -I http://yourdomain.com
# Should return 200 OK and HTML

# From your browser:
# Visit: http://yourdomain.com
# Should show Amazon Arab marketplace
```

**If site doesn't load:**
```bash
# Check Nginx error logs
tail -f /var/log/nginx/error.log

# Check Nginx is running
systemctl status nginx

# Check DNS propagation
nslookup yourdomain.com
```

**✅ Checkpoint:** Site loads over HTTP (no SSL yet)

---

### Step 4.3: Install SSL Certificate

```bash
# Stop Nginx temporarily
systemctl stop nginx

# Request certificate
certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Follow prompts:
# - Enter email: your-email@example.com
# - Agree to Terms: Y
# - Share email: Y or N (your choice)
# - Wait for verification (30 seconds)

# Should see: "Successfully received certificate"

# Start Nginx
systemctl start nginx
```

**✅ Checkpoint:** SSL certificates obtained

---

### Step 4.4: Configure Nginx with SSL

```bash
# Edit Nginx config
nano /etc/nginx/sites-available/amazonarab
```

**Replace with this SSL-enabled config:**
```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name yourdomain.com www.yourdomain.com;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Frontend
    location / {
        root /var/www/amazonarab/frontend/build;
        try_files $uri /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Security: Block sensitive files
    location ~ /\. {
        deny all;
    }
    
    location ~ /\.env {
        deny all;
    }

    # Robots.txt and sitemap
    location = /robots.txt {
        log_not_found off;
    }
}
```

**Apply changes:**
```bash
# Test config
nginx -t

# Reload Nginx
systemctl reload nginx
```

**✅ Checkpoint:** Site loads over HTTPS with green padlock

---

### Step 4.5: Setup SSL Auto-Renewal

```bash
# Test renewal
certbot renew --dry-run
# Should say "Congratulations, all simulated renewals succeeded"

# Add cron job for auto-renewal
crontab -e

# Add this line (renews daily at 3am):
0 3 * * * certbot renew --quiet --post-hook "systemctl reload nginx"
```

**✅ Checkpoint:** SSL auto-renewal configured

---

## 🚀 PHASE 5: PM2 PROCESS MANAGEMENT (15 minutes)

### Step 5.1: Create PM2 Ecosystem File

```bash
# Create PM2 config
nano /var/www/amazonarab/ecosystem.config.js
```

**Paste this configuration:**
```javascript
module.exports = {
  apps: [
    {
      name: 'amazonarab-backend',
      cwd: '/var/www/amazonarab/backend',
      script: 'venv/bin/python',
      args: 'server.py',
      interpreter: 'none',
      env: {
        PYTHONUNBUFFERED: '1',
      },
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      error_file: '/var/log/amazonarab-backend-error.log',
      out_file: '/var/log/amazonarab-backend-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      min_uptime: '10s',
      max_restarts: 10,
      restart_delay: 4000,
    }
  ]
};
```

**✅ Checkpoint:** PM2 config file created

---

### Step 5.2: Start Backend with PM2

```bash
# Start backend
pm2 start /var/www/amazonarab/ecosystem.config.js

# Check status
pm2 status
# Should show: amazonarab-backend | online

# View logs
pm2 logs amazonarab-backend --lines 50

# Should NOT see errors
# Should see: "Application startup complete" or similar
```

**If backend fails:**
```bash
# Check detailed logs
pm2 logs amazonarab-backend

# Common issues:
# - Missing dependencies: cd backend && pip install -r requirements.txt
# - Wrong Python version: use python3.11
# - .env file missing: check /var/www/amazonarab/backend/.env exists
# - Port in use: lsof -i:8001 (kill conflicting process)
```

**✅ Checkpoint:** Backend running via PM2, no errors in logs

---

### Step 5.3: Configure PM2 Startup

```bash
# Generate startup script
pm2 startup

# Copy and run the command it outputs (example):
# sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u root --hp /root

# Save current PM2 processes
pm2 save

# Verify
systemctl status pm2-root
# Should show: "active (running)"
```

**✅ Checkpoint:** PM2 will auto-start on server reboot

---

### Step 5.4: Test Backend API

```bash
# Test health endpoint
curl https://yourdomain.com/api/me
# Should return: 401 Unauthorized (this is correct - needs auth)

# Test setup-admin endpoint
curl -X POST https://yourdomain.com/api/setup-admin
# Should return: {"success": true, ...} or "Admin setup already complete"
```

**✅ Checkpoint:** Backend API responding via HTTPS

---

## 🔐 PHASE 6: ADMIN ENDPOINT LOCKDOWN (10 minutes)

### Step 6.1: Disable setup-admin Endpoint

**After running setup-admin once:**

```bash
# Verify admin was created successfully
curl -X POST https://yourdomain.com/api/setup-admin

# Should return: "Admin setup already complete"
# If not, run it once until you get success

# After success, lock it down:
nano /var/www/amazonarab/backend/.env

# Change this line:
ADMIN_SETUP_COMPLETE=false

# To:
ADMIN_SETUP_COMPLETE=true

# Restart backend
pm2 restart amazonarab-backend

# Verify endpoint is locked
curl -X POST https://yourdomain.com/api/setup-admin
# Should return: 403 Forbidden "Admin setup already complete"
```

**✅ Checkpoint:** setup-admin endpoint returns 403

---

### Step 6.2: Add IP Whitelist for Admin Panel (Optional but Recommended)

```bash
# Edit Nginx config
nano /etc/nginx/sites-available/amazonarab

# Add this INSIDE the "server" block (after ssl_certificate lines):
```

```nginx
    # Admin dashboard IP whitelist
    location /dashboard/admin {
        # Allow your office IP
        allow YOUR.OFFICE.IP.ADDRESS;
        
        # Allow your home IP (get from: curl ifconfig.me)
        allow YOUR.HOME.IP.ADDRESS;
        
        # Block everyone else
        deny all;
        
        # Pass to frontend
        root /var/www/amazonarab/frontend/build;
        try_files $uri /index.html;
    }
```

**Apply:**
```bash
nginx -t && systemctl reload nginx
```

**✅ Checkpoint:** Admin panel only accessible from whitelisted IPs

---

## 💳 PHASE 7: PAYMENT SYSTEM TESTING (30 minutes)

### Step 7.1: Test Wallet Integration

```bash
# Verify wallet address in all configs
grep -r "TY8Z91NMCjREyZVj9NjDsF8hVjyqfxFFRU" /var/www/amazonarab/

# Should appear in:
# - backend/.env
# - frontend/.env (or .env.production)
# - Any compiled/built files
```

**Test 1: View Checkout Page**
```
1. Open: https://yourdomain.com
2. Register as buyer
3. Add product to cart
4. Go to checkout
5. Verify wallet address shown: TY8Z91NMCjREyZVj9NjDsF8hVjyqfxFFRU
6. Verify QR code displays
7. Verify warning about TRC20 network
```

**✅ Checkpoint:** Checkout page shows correct wallet and QR code

---

### Step 7.2: Test Order Creation (No Payment Yet)

```
1. On checkout page, check the confirmation box
2. Click "Place Order"
3. Should redirect to /orders
4. Order should show status: "pending_payment"
5. Order should be visible in buyer dashboard
```

**Verify in Backend:**
```bash
# Check backend logs for order creation
pm2 logs amazonarab-backend | grep -i "order"

# Should see: Order created with ID: xxx-xxx-xxx
```

**✅ Checkpoint:** Orders create successfully without errors

---

### Step 7.3: Small Payment Test ($1 USDT)

⚠️ **USE REAL MONEY - Start small!**

**Test Payment Flow:**
```
1. Have $2 USDT in your test wallet (TRC20 network)
2. Create a test product (as verified seller)
3. As buyer, add to cart
4. Proceed to checkout
5. Copy wallet address: TY8Z91NMCjREyZVj9NjDsF8hVjyqfxFFRU
6. Send $1 USDT on TRC20 network
7. Wait for blockchain confirmation (1-2 minutes)
8. Check on TronScan: https://tronscan.org/#/address/TY8Z91NMCjREyZVj9NjDsF8hVjyqfxFFRU
9. Verify transaction appears
```

**✅ Checkpoint:** You received $1 USDT at the admin wallet

---

### Step 7.4: Test Admin Payment Confirmation

```
1. Login as admin: support@arabshopping.org
2. Go to Admin Dashboard
3. Click "Orders" tab
4. Should see test order in "Pending Payment" section
5. Click "Confirm Payment Received"
6. Order should move to "Paid" section
7. Order status should change to "paid"
8. confirmedByAdmin should be true
9. confirmedAt timestamp should be set
```

**Verify in Database:**
```bash
# If you have direct database access or via Supabase Dashboard
# Check orders table:
# - paymentStatus should be 'paid'
# - confirmedByAdmin should be true
# - confirmedAt should have timestamp
```

**✅ Checkpoint:** Admin can confirm payment, order status updates

---

### Step 7.5: Test Order Completion

```
1. Still in Admin Dashboard, "Orders" tab
2. Find the paid order (now in "Paid Orders" section)
3. Click "Mark as Completed"
4. Order should move to "Completed Orders" section
5. Status should be "completed"
```

**✅ Checkpoint:** Full order lifecycle works (pending → paid → completed)

---

### Step 7.6: Test Wrong Network Protection

⚠️ **DO NOT actually send money on wrong network**

**Verify Warning is Clear:**
```
1. Go to checkout page
2. Verify warning text is prominent:
   "⚠️ Send USDT on TRC20 network ONLY"
   "❌ Sending via ERC20/BEP20 will result in permanent loss"
3. Verify network is mentioned multiple times
4. Consider adding even more warnings if needed
```

**✅ Checkpoint:** Warnings are clear and prominent

---

## ✅ PHASE 8: FINAL VERIFICATION (30 minutes)

### Step 8.1: Complete User Flow Test

**Test as Seller:**
```
1. Register as seller: seller@test.com
2. Verify "Verification Required" message shown
3. Request merchant invite code from admin
4. Admin creates invite code in dashboard
5. Seller uploads verification documents with code
6. Admin approves seller verification
7. Seller status becomes "verified"
8. Seller creates test product with images
9. Product visible on marketplace
```

**Test as Buyer:**
```
1. Register as buyer: buyer@test.com
2. Browse products
3. Add to cart
4. View cart
5. Proceed to checkout
6. Verify wallet and QR code shown
7. Create order (without payment)
8. Check order in "My Orders"
9. Verify status is "pending_payment"
```

**Test as Admin:**
```
1. Login as admin
2. View all users
3. Create merchant invite codes
4. Review verification documents
5. Approve/reject verifications
6. View all orders
7. Confirm payments
8. Mark orders as completed
```

**✅ Checkpoint:** All user roles work as expected

---

### Step 8.2: Security Verification

```bash
# Test 1: Service key not in frontend
curl https://yourdomain.com/static/js/main*.js | grep -i "service_role"
# Should return: (no matches)

# Test 2: .env files not accessible
curl https://yourdomain.com/.env
curl https://yourdomain.com/backend/.env
# Should return: 403 Forbidden or 404

# Test 3: Admin panel requires auth
curl https://yourdomain.com/dashboard/admin
# Should redirect to login or show 403

# Test 4: API requires auth
curl https://yourdomain.com/api/products/my
# Should return: 401 Unauthorized

# Test 5: Role escalation blocked (if security fixes applied)
# Try updating role via Supabase client - should fail
```

**✅ Checkpoint:** All security checks pass

---

### Step 8.3: Performance Check

```bash
# Test 1: Page load speed
curl -o /dev/null -s -w 'Total: %{time_total}s\n' https://yourdomain.com
# Should be < 3 seconds

# Test 2: API response time
curl -o /dev/null -s -w 'Total: %{time_total}s\n' https://yourdomain.com/api/products
# Should be < 1 second

# Test 3: Backend memory usage
pm2 info amazonarab-backend | grep memory
# Should be < 300MB

# Test 4: Check for errors in logs
pm2 logs amazonarab-backend --lines 100 | grep -i "error"
# Should have no critical errors
```

**✅ Checkpoint:** Site performs well, no memory leaks

---

### Step 8.4: Browser Testing

**Test in Multiple Browsers:**
```
Chrome/Edge:
- [ ] Homepage loads
- [ ] Registration works
- [ ] Login works
- [ ] Checkout displays correctly
- [ ] QR code visible

Firefox:
- [ ] Homepage loads
- [ ] Registration works
- [ ] Login works
- [ ] Checkout displays correctly
- [ ] QR code visible

Safari (if available):
- [ ] Homepage loads
- [ ] Registration works
- [ ] Login works
- [ ] Checkout displays correctly
- [ ] QR code visible

Mobile (Chrome on Android or Safari on iOS):
- [ ] Site is responsive
- [ ] QR code scannable
- [ ] All features work
```

**✅ Checkpoint:** Site works across all browsers

---

## 📊 PHASE 9: MONITORING SETUP (15 minutes)

### Step 9.1: Setup Log Monitoring

```bash
# Create log rotation config
nano /etc/logrotate.d/amazonarab
```

**Paste:**
```
/var/log/amazonarab-*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 root root
    sharedscripts
    postrotate
        pm2 reloadLogs
    endscript
}
```

**Test:**
```bash
logrotate -d /etc/logrotate.d/amazonarab
```

**✅ Checkpoint:** Log rotation configured

---

### Step 9.2: Setup Basic Monitoring

```bash
# Install monitoring tools
apt install -y htop nethogs

# Monitor CPU/Memory in real-time
htop

# Monitor network usage
nethogs

# Check disk usage
df -h
# Should have at least 2GB free

# Monitor PM2 processes
pm2 monit
```

**✅ Checkpoint:** Can monitor server resources

---

### Step 9.3: Setup Uptime Monitoring (External)

**Use a Service (Choose One):**

1. **UptimeRobot (Free):**
   ```
   - Go to: https://uptimerobot.com
   - Add monitor: https://yourdomain.com
   - Set check interval: 5 minutes
   - Add alert email
   ```

2. **Pingdom:**
   ```
   - Go to: https://www.pingdom.com
   - Add check: https://yourdomain.com
   - Configure alerts
   ```

3. **StatusCake:**
   ```
   - Go to: https://www.statuscake.com
   - Add test: https://yourdomain.com
   - Set alert email
   ```

**✅ Checkpoint:** Uptime monitoring active, alerts configured

---

## 🎯 PHASE 10: LAUNCH PREPARATION (10 minutes)

### Step 10.1: Pre-Launch Checklist

**Critical Items:**
```
Database:
- [ ] Supabase project created
- [ ] All tables created (6 tables)
- [ ] RLS policies applied
- [ ] Security fixes applied
- [ ] Storage buckets created (products, documents)

Backend:
- [ ] Deployed to VPS
- [ ] Running via PM2
- [ ] .env configured with production values
- [ ] Admin password changed from default
- [ ] setup-admin endpoint locked (ADMIN_SETUP_COMPLETE=true)
- [ ] Logs show no errors

Frontend:
- [ ] Built for production
- [ ] Served via Nginx
- [ ] .env configured with production values
- [ ] Wallet address correct everywhere

Security:
- [ ] SSL certificate installed (HTTPS working)
- [ ] SSL auto-renewal configured
- [ ] SERVICE_ROLE_KEY not in frontend
- [ ] .env files not publicly accessible
- [ ] Admin panel IP whitelist (optional but recommended)

Testing:
- [ ] Seller registration and verification works
- [ ] Product creation works
- [ ] Buyer can add to cart and checkout
- [ ] Order creation works
- [ ] Payment test completed ($1 USDT)
- [ ] Admin can confirm payments
- [ ] Order completion works
- [ ] All user roles tested

Payment:
- [ ] Wallet address verified (can receive USDT)
- [ ] Test payment received
- [ ] Wallet address displayed on checkout
- [ ] QR code displays correctly
- [ ] Warning about TRC20 network prominent

Monitoring:
- [ ] PM2 monitoring active
- [ ] Logs configured
- [ ] Uptime monitor active
- [ ] Alert email configured
```

**✅ Checkpoint:** All checklist items completed

---

### Step 10.2: Create Admin Account

```bash
# Run setup-admin endpoint (if not already done)
curl -X POST https://yourdomain.com/api/setup-admin

# Should return:
# {
#   "success": true,
#   "message": "Admin account created successfully",
#   "email": "support@arabshopping.org"
# }

# Test admin login
# Go to: https://yourdomain.com/login
# Email: support@arabshopping.org
# Password: [YOUR_NEW_STRONG_PASSWORD]

# Should redirect to: https://yourdomain.com/dashboard/admin
```

**✅ Checkpoint:** Admin account created and can login

---

### Step 10.3: Create Initial Merchant Invite Codes

```
1. Login as admin
2. Go to "Invite Codes" tab
3. Click "Create New Code" 10 times
4. Save these codes somewhere safe
5. You'll give these to sellers you want to onboard
```

**✅ Checkpoint:** 10 invite codes created and saved

---

### Step 10.4: Backup Configuration

```bash
# Backup all configs
mkdir -p /root/amazonarab-backup-$(date +%Y%m%d)

# Copy files
cp /var/www/amazonarab/backend/.env /root/amazonarab-backup-$(date +%Y%m%d)/
cp /var/www/amazonarab/frontend/.env /root/amazonarab-backup-$(date +%Y%m%d)/
cp /etc/nginx/sites-available/amazonarab /root/amazonarab-backup-$(date +%Y%m%d)/
cp /var/www/amazonarab/ecosystem.config.js /root/amazonarab-backup-$(date +%Y%m%d)/

# Export PM2 config
pm2 save

# Create backup archive
cd /root
tar -czf amazonarab-backup-$(date +%Y%m%d).tar.gz amazonarab-backup-$(date +%Y%m%d)/

# Save to secure location (download to your computer)
```

**✅ Checkpoint:** Configuration backed up

---

## 🚀 LAUNCH!

### Your marketplace is now LIVE at: https://yourdomain.com

---

## 📞 POST-LAUNCH SUPPORT

### Daily Checks (First Week)
```bash
# Check backend status
pm2 status

# Check recent logs
pm2 logs amazonarab-backend --lines 50

# Check disk space
df -h

# Check SSL expiry
certbot certificates
```

### Weekly Checks
```bash
# Update system
apt update && apt upgrade -y

# Restart PM2 if needed
pm2 restart amazonarab-backend

# Check for SSL renewal
certbot renew --dry-run
```

### Monthly Checks
```bash
# Backup database (Supabase auto-backs up)
# Review logs for patterns
# Check analytics
# Update dependencies if needed
```

---

## 🆘 TROUBLESHOOTING

### Issue: Site not loading
```bash
# Check Nginx
systemctl status nginx
nginx -t

# Check DNS
dig +short yourdomain.com

# Check SSL
certbot certificates
```

### Issue: Backend not responding
```bash
# Check PM2
pm2 status
pm2 logs amazonarab-backend

# Restart backend
pm2 restart amazonarab-backend

# Check port
lsof -i:8001
```

### Issue: Orders not creating
```bash
# Check backend logs
pm2 logs amazonarab-backend | grep -i error

# Check Supabase connection
# Verify SUPABASE_SERVICE_ROLE_KEY in .env

# Test database connection
curl https://yourdomain.com/api/products
```

### Issue: Payment not confirmed
```
1. Check blockchain explorer for transaction
2. Verify correct wallet address
3. Verify TRC20 network used (not ERC20)
4. Check admin has role='admin' in database
5. Try confirming again
```

---

## 🎉 SUCCESS!

Your Amazon Arab marketplace is now live and accepting real payments!

**Next Steps:**
1. Announce launch to initial sellers
2. Provide merchant invite codes
3. Monitor closely for first 48 hours
4. Gather user feedback
5. Iterate and improve

**Support:**
- Documentation: /app/README.md
- Security: /app/backend/FULL_SECURITY_AUDIT.md
- Contact: support@arabshopping.org

**Good luck with your marketplace!** 🚀
