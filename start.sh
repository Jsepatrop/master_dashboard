#!/bin/bash

echo "🚀 Starting Master Dashboard Revolutionary..."
echo "=============================================="

# Check if required directories exist
if [ ! -d "frontend" ]; then
    echo "❌ Frontend directory not found!"
    exit 1
fi

if [ ! -d "backend" ]; then
    echo "❌ Backend directory not found!"
    exit 1
fi

# Start backend server in background
echo "🐍 Starting Backend Server..."
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend server
echo "⚛️  Starting Frontend Server..."
cd frontend
npm run dev --host 0.0.0.0 --port 3000 &
FRONTEND_PID=$!
cd ..

# Function to cleanup processes on exit
cleanup() {
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit
}

# Trap signals to cleanup on exit
trap cleanup SIGINT SIGTERM

echo "✅ Master Dashboard Revolutionary started!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers..."

# Wait for processes
wait
