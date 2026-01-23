#!/bin/bash

# Amazon Arab Marketplace - Run Script
# This script helps you run both backend and frontend

echo "🚀 Amazon Arab Marketplace - Setup & Run"
echo "=========================================="
echo ""

# Check if .env files exist
if [ ! -f "backend/.env" ]; then
    echo "❌ Error: backend/.env not found!"
    echo "Please create backend/.env file with your environment variables"
    exit 1
fi

if [ ! -f "frontend/.env" ]; then
    echo "❌ Error: frontend/.env not found!"
    echo "Please create frontend/.env file with your environment variables"
    exit 1
fi

echo "✅ Environment files found"
echo ""

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0
    else
        return 1
    fi
}

# Check ports
if check_port 8001; then
    echo "⚠️  Warning: Port 8001 is already in use (backend)"
    echo "   You may need to stop the existing process or change the port"
fi

if check_port 3000; then
    echo "⚠️  Warning: Port 3000 is already in use (frontend)"
    echo "   React will automatically use the next available port"
fi

echo ""
echo "📦 Checking dependencies..."
echo ""

# Check backend dependencies
if [ ! -d "backend/venv" ]; then
    echo "📥 Setting up backend virtual environment..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
    echo "✅ Backend dependencies installed"
else
    echo "✅ Backend virtual environment exists"
fi

# Check frontend dependencies
if [ ! -d "frontend/node_modules" ]; then
    echo "📥 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
    echo "✅ Frontend dependencies installed"
else
    echo "✅ Frontend dependencies exist"
fi

echo ""
echo "🎯 Starting servers..."
echo ""
echo "Backend will run on: http://localhost:8001"
echo "Frontend will run on: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Start backend in background
cd backend
source venv/bin/activate
python server.py &
BACKEND_PID=$!
cd ..

# Wait a bit for backend to start
sleep 3

# Start frontend
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Servers stopped"
    exit 0
}

# Trap Ctrl+C
trap cleanup SIGINT SIGTERM

# Wait for processes
wait

