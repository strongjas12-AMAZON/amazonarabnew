# 🚀 Setup and Run Guide

## Step 1: Create Environment Files

### Backend Environment File

Create `backend/.env` with the following content:

```bash
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://dqqmzatrxmueilsxvlgb.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRxcW16YXRyeG11ZWlsc3h2bGdiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY4MjIwMzMsImV4cCI6MjA4MjM5ODAzM30.cCkKIYZejc00R1luf1R3nAKzNgkmXgrIBJqwWBRkWGw
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRxcW16YXRyeG11ZWlsc3h2bGdiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjgyMjAzMywiZXhwIjoyMDgyMzk4MDMzfQ.MdWsu2dpwOQPKwlYSJ8O9KbdSh0--triMTd4azyCum4

# Email Service
RESEND_API_KEY=re_vHtccec5_Pix8bqH4J2axQA692HYmFH8w

# App Configuration
ENV=production
ADMIN_SETUP_COMPLETE=false
ADMIN_CRYPTO_WALLET=TY8Z91NMCjREyZVj9NjDsF8hVjyqfxFFRU
CORS_ORIGINS=https://arabshopping.org,https://www.arabshopping.org
SENDER_EMAIL=support@arabshopping.org
```

### Frontend Environment File

Create `frontend/.env` with the following content:

```bash
REACT_APP_BACKEND_URL=https://arabshopping.org
REACT_APP_SUPABASE_URL=https://dqqmzatrxmueilsxvlgb.supabase.co
REACT_APP_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRxcW16YXRyeG11ZWlsc3h2bGdiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY4MjIwMzMsImV4cCI6MjA4MjM5ODAzM30.cCkKIYZejc00R1luf1R3nAKzNgkmXgrIBJqwWBRkWGw
REACT_APP_ADMIN_WALLET=TY8Z91NMCjREyZVj9NjDsF8hVjyqfxFFRU
```

## Step 2: Database Setup

### 2.1 Run Main Database Schema

1. Go to Supabase Dashboard: https://supabase.com/dashboard
2. Select project: `dqqmzatrxmueilsxvlgb`
3. Open SQL Editor
4. Run `backend/init_database.sql` (if not already run)

### 2.2 Run Wallet Schema (NEW)

1. In Supabase SQL Editor
2. Run `backend/wallet_schema.sql` to create wallet tables

## Step 3: Install Dependencies

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

## Step 4: Run the Application

### Terminal 1 - Backend Server

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python server.py
```

Backend will run on: `http://localhost:8001`

### Terminal 2 - Frontend Server

```bash
cd frontend
npm start
```

Frontend will run on: `http://localhost:3000`

## Step 5: Setup Admin Account (First Time Only)

Once backend is running, create admin account:

```bash
curl -X POST http://localhost:8001/api/setup-admin
```

Or use browser:
- Open: `http://localhost:8001/api/setup-admin`
- Method: POST
- Expected response: `{"success": true, "message": "Admin account created successfully"}`

**Admin Credentials:**
- Email: `support@arabshopping.org`
- Password: Check your backend logs or Supabase Auth

## Step 6: Access the Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8001/api
- **API Docs:** http://localhost:8001/docs (FastAPI Swagger UI)

## Troubleshooting

### Backend Issues

1. **Port already in use:**
   ```bash
   # Find process using port 8001
   lsof -i:8001  # Linux/Mac
   netstat -ano | findstr :8001  # Windows
   
   # Kill process or change port in server.py
   ```

2. **Missing dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment variables not loading:**
   - Ensure `.env` file is in `backend/` directory
   - Check file has no extra spaces or quotes

### Frontend Issues

1. **Port 3000 in use:**
   ```bash
   # React will automatically use next available port (3001, 3002, etc.)
   ```

2. **Module not found:**
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **Environment variables not loading:**
   - Ensure `.env` file is in `frontend/` directory
   - Restart dev server after creating `.env`
   - Variables must start with `REACT_APP_`

### Database Issues

1. **Tables not found:**
   - Run `backend/init_database.sql` in Supabase SQL Editor
   - Run `backend/wallet_schema.sql` for wallet tables

2. **RLS errors:**
   - Verify RLS policies in Supabase Dashboard
   - Check that policies were created from SQL scripts

## Production Deployment

For production, update these environment variables:

**Backend:**
- `CORS_ORIGINS`: Set to your production domain
- `ENV=production`
- `ADMIN_SETUP_COMPLETE=true` (after admin is created)

**Frontend:**
- `REACT_APP_BACKEND_URL`: Set to your production backend URL

## Quick Commands Reference

```bash
# Backend
cd backend && python server.py

# Frontend  
cd frontend && npm start

# Install dependencies
cd backend && pip install -r requirements.txt
cd frontend && npm install

# Create admin (first time)
curl -X POST http://localhost:8001/api/setup-admin
```

