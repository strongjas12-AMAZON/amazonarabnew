# 🚀 Amazon Arab Deployment Guide

Complete step-by-step guide to deploy your multi-vendor marketplace.

## 📋 Pre-Deployment Checklist

Before you begin, ensure you have:
- ✅ Supabase account and project created
- ✅ Access to Supabase Dashboard
- ✅ VPS or hosting server (for production deployment)
- ✅ Domain name (optional, for production)

## 🗄️ Step 1: Database Setup (CRITICAL)

### 1.1 Run SQL Schema in Supabase

1. **Login to Supabase Dashboard:**
   - Go to: https://supabase.com/dashboard
   - Select your project: `dqqmzatrxmueilsxvlgb`

2. **Open SQL Editor:**
   - Click "SQL Editor" in left sidebar
   - Click "New Query"

3. **Copy and Execute Schema:**
   - Open file: `/app/backend/init_database.sql`
   - Copy the ENTIRE content
   - Paste into Supabase SQL Editor
   - Click "Run" button
   - Wait for completion (should show "Success")

4. **Verify Tables Created:**
   - Go to "Table Editor" in Supabase
   - You should see these tables:
     * users
     * products
     * orders
     * order_items
     * verification_documents
     * merchant_invite_codes

### 1.2 Create Storage Buckets

1. **Go to Storage Section:**
   - Click "Storage" in Supabase sidebar

2. **Create Products Bucket:**
   - Click "New bucket"
   - Name: `products`
   - Public bucket: **YES** (toggle ON)
   - Click "Create bucket"

3. **Create Documents Bucket:**
   - Click "New bucket"
   - Name: `documents`
   - Public bucket: **YES** (toggle ON)
   - Click "Create bucket"

### 1.3 Verify Row Level Security (RLS)

- Go to "Authentication" > "Policies"
- Verify RLS is enabled on all tables
- Policies should be automatically created from SQL script

## 👤 Step 2: Create Admin Account

### Method 1: Using cURL (Recommended)

```bash
curl -X POST https://luxmarket-4.preview.emergentagent.com/api/setup-admin
```

### Method 2: Using Browser Console

1. Open your deployed site
2. Open Browser Console (F12)
3. Run:
```javascript
fetch('https://luxmarket-4.preview.emergentagent.com/api/setup-admin', { 
  method: 'POST' 
})
.then(r => r.json())
.then(data => console.log(data))
```

### Expected Response:
```json
{
  "success": true,
  "message": "Admin account created successfully",
  "email": "support@arabshopping.org"
}
```

### Admin Credentials:
- **Email:** support@arabshopping.org
- **Password:** Hadi1247@

⚠️ **IMPORTANT:** 
- This endpoint runs ONLY ONCE
- After successful creation, it's automatically disabled
- Change password after first login!

## 🧪 Step 3: Test the Application

### 3.1 Test Admin Login

1. Go to: https://luxmarket-4.preview.emergentagent.com/login
2. Login with admin credentials
3. You should be redirected to Admin Dashboard
4. Verify you see:
   - User management
   - Order management
   - Verification documents
   - Invite code creation

### 3.2 Create Test Seller

1. Click "Invite Codes" tab in Admin Dashboard
2. Click "Create New Code"
3. Copy the generated code (e.g., `ABC12345`)
4. Logout from admin account
5. Go to Register page
6. Create a seller account
7. In Seller Dashboard, click "Start Verification"
8. Upload a test document (any image/PDF)
9. Enter the invite code
10. Submit

### 3.3 Approve Seller (as Admin)

1. Login as admin again
2. Go to "Verifications" tab
3. You should see pending verification
4. Click "View Document" to review
5. Click "Approve"
6. Seller is now verified!

### 3.4 Create Test Product (as Seller)

1. Logout and login as seller
2. Go to Seller Dashboard
3. Click "Add Product"
4. Fill in:
   - Title: "Luxury Watch"
   - Description: "Premium Swiss timepiece"
   - Price: 999.99
5. Click "Create"
6. Upload product images (drag & drop)

### 3.5 Test Buyer Flow

1. Register a new buyer account
2. Go to Products page
3. You should see the seller's products
4. Add product to cart
5. Go to Cart
6. Click "Proceed to Checkout"
7. You should see:
   - QR Code for USDT payment
   - Wallet address
   - Payment instructions
8. Check the confirmation checkbox
9. Click "Place Order"

### 3.6 Confirm Order (as Admin)

1. Login as admin
2. Go to "Orders" tab
3. You should see pending order
4. Click "Confirm Payment"
5. Order status changes to "paid"

## 🌐 Step 4: Production Deployment

### Option A: Deploy on VPS (Ubuntu 20.04+)

#### 4.1 Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3-pip

# Install Nginx
sudo apt install -y nginx

# Install Yarn
npm install -g yarn
```

#### 4.2 Clone/Upload Application

```bash
# Create directory
sudo mkdir -p /var/www/luxmarket
cd /var/www/luxmarket

# Upload your application files here
# (Use SCP, SFTP, or Git)
```

#### 4.3 Setup Backend

```bash
cd /var/www/luxmarket/backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify .env file has correct values
nano .env

# Test backend
uvicorn server:app --host 0.0.0.0 --port 8001
```

#### 4.4 Setup Frontend

```bash
cd /var/www/luxmarket/frontend

# Install dependencies
yarn install

# Update .env with your domain
nano .env
# Change REACT_APP_BACKEND_URL to your domain

# Build for production
yarn build
```

#### 4.5 Configure Nginx

```bash
# Create Nginx config
sudo nano /etc/nginx/sites-available/luxmarket
```

Paste this configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # Change this!

    # Frontend
    location / {
        root /var/www/luxmarket/frontend/build;
        try_files $uri /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/luxmarket /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 4.6 Setup Process Manager (PM2)

```bash
# Install PM2
npm install -g pm2

# Start backend
cd /var/www/luxmarket/backend
source venv/bin/activate
pm2 start "uvicorn server:app --host 0.0.0.0 --port 8001" --name luxmarket-backend

# Save PM2 configuration
pm2 save
pm2 startup
```

#### 4.7 Setup SSL (Let's Encrypt)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
```

### Option B: Deploy on Vercel/Netlify (Frontend Only)

If you want to deploy just the frontend:

1. **Build Frontend:**
   ```bash
   cd /app/frontend
   yarn build
   ```

2. **Deploy to Vercel:**
   - Install Vercel CLI: `npm i -g vercel`
   - Run: `vercel deploy --prod`
   - Set environment variables in Vercel dashboard

3. **Backend:** Keep running on current server or deploy to Heroku/Railway

## 🔒 Security Hardening

### Update Default Credentials

1. **Change Admin Password:**
   - Login as admin
   - (Feature to add: Password change in settings)
   - For now, change directly in Supabase Auth

2. **Rotate Supabase Keys:**
   - Generate new anon key in Supabase settings
   - Update .env files
   - Restart services

### Environment Variables Security

- Never commit .env files to Git
- Use environment variables on production
- Keep SERVICE_ROLE_KEY secret (never expose to frontend)

### Firewall Setup

```bash
# Allow SSH, HTTP, HTTPS
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

## 📊 Monitoring

### Check Backend Logs

```bash
# PM2 logs
pm2 logs luxmarket-backend

# Supervisor logs (current setup)
tail -f /var/log/supervisor/backend.err.log
tail -f /var/log/supervisor/backend.out.log
```

### Check Frontend Build

```bash
# Build errors
yarn build

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Monitor Supabase

- Go to Supabase Dashboard
- Check "Logs" section
- Monitor database queries
- Check API usage

## 🐛 Troubleshooting

### Issue: Database Connection Failed

**Solution:**
1. Verify Supabase credentials in .env
2. Check if SQL schema was executed
3. Verify RLS policies are enabled

### Issue: Admin Setup Fails

**Solution:**
1. Check if tables exist in Supabase
2. Verify SERVICE_ROLE_KEY is correct
3. Check backend logs for detailed error
4. Ensure ADMIN_SETUP_COMPLETE=false in .env

### Issue: Images Not Uploading

**Solution:**
1. Verify storage buckets exist in Supabase
2. Check buckets are set to PUBLIC
3. Verify file size limits
4. Check backend logs

### Issue: Orders Not Creating

**Solution:**
1. Verify user is logged in
2. Check user role is 'buyer'
3. Verify cart has items
4. Check backend API logs

### Issue: Can't Login After Registration

**Solution:**
1. Check Supabase Auth logs
2. Verify email confirmation is disabled (or enabled with email service)
3. Check if user exists in users table

## 📞 Support & Maintenance

### Regular Maintenance Tasks

1. **Backup Database:**
   - Use Supabase automatic backups
   - Export database weekly via Supabase dashboard

2. **Update Dependencies:**
   ```bash
   # Backend
   pip list --outdated
   pip install --upgrade <package>
   
   # Frontend
   yarn outdated
   yarn upgrade
   ```

3. **Monitor Storage:**
   - Check Supabase storage usage
   - Clean up old verification documents if needed

4. **Security Updates:**
   - Update system packages monthly
   - Monitor Supabase security advisories

### Contact

For issues specific to LuxMarket:
- Email: support@arabshopping.org
- Check logs in `/var/log/supervisor/` (current setup)
- Review code in `/app/backend` and `/app/frontend`

---

## ✅ Final Checklist

Before going live:
- [ ] Database schema executed successfully
- [ ] Storage buckets created and public
- [ ] Admin account created and tested
- [ ] Can create sellers with invite codes
- [ ] Can approve seller verification
- [ ] Can create and view products
- [ ] Can add products to cart
- [ ] Checkout shows correct QR code and wallet
- [ ] Can place orders
- [ ] Admin can confirm payments
- [ ] SSL certificate installed (production)
- [ ] Domain configured (production)
- [ ] Environment variables secured
- [ ] Backup strategy in place
- [ ] Monitoring configured

🎉 **Congratulations! Your LuxMarket is ready for production!**
