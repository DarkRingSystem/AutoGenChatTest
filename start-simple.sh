#!/bin/bash

# AutoGen AI Chat - Simple Start Script (without Virtual Environment)
# 如果系统 Python 环境已配置好，可以使用此脚本

echo "🚀 Starting AutoGen AI Chat Application..."
echo ""

# Check if .env exists in backend
if [ ! -f backend/.env ]; then
    echo "⚠️  Backend .env file not found!"
    echo "📝 Creating .env from .env.example..."
    cp backend/.env.example backend/.env
    echo "⚠️  Please edit backend/.env and add your API keys"
    echo ""
fi

# Start backend
echo "🔧 Starting Backend Server..."
cd backend
python main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to initialize..."
sleep 3

# Start frontend
echo "🎨 Starting Frontend Server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Application started!"
echo ""
echo "📡 Backend API: http://localhost:8000"
echo "🎨 Frontend UI: http://localhost:3000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    sleep 1
    kill -9 $BACKEND_PID 2>/dev/null || true
    kill -9 $FRONTEND_PID 2>/dev/null || true
    echo "✅ All servers stopped"
    exit 0
}

# Wait for Ctrl+C
trap cleanup INT TERM
wait

