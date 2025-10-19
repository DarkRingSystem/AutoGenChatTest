#!/bin/bash

# AutoGen AI Chat - Development Start Script (with Virtual Environment)
# 本地调试推荐使用此脚本启动

set -e  # 遇到错误立即退出

echo "════════════════════════════════════════════════════════════════"
echo "  🚀 AutoGen AI Chat - 开发环境启动"
echo "════════════════════════════════════════════════════════════════"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查 .env 文件
if [ ! -f backend/.env ]; then
    echo -e "${YELLOW}⚠️  Backend .env file not found!${NC}"
    echo "📝 Creating .env from .env.example..."
    cp backend/.env.example backend/.env
    echo -e "${YELLOW}⚠️  Please edit backend/.env and add your API keys${NC}"
    echo ""
    read -p "Press Enter to continue after editing .env file..."
fi

# 检查虚拟环境
echo "🔍 Checking virtual environment..."
if [ ! -d ".venv" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# 激活虚拟环境并检查依赖
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# 检查关键依赖
echo "📦 Checking dependencies..."
MISSING_DEPS=0

python -c "import fastapi" 2>/dev/null || MISSING_DEPS=1
python -c "import autogen_agentchat" 2>/dev/null || MISSING_DEPS=1

if [ $MISSING_DEPS -eq 1 ]; then
    echo -e "${YELLOW}⚠️  Some dependencies are missing${NC}"
    echo "📦 Installing dependencies..."
    pip install -r backend/requirements.txt
    pip install "pillow>=11.0.0" --upgrade
    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    echo -e "${GREEN}✅ All dependencies are installed${NC}"
fi

# 启动后端
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  🔧 Starting Backend Server (Virtual Environment)"
echo "════════════════════════════════════════════════════════════════"
echo ""

source .venv/bin/activate
cd backend
python main.py &
BACKEND_PID=$!
cd ..

# 等待后端启动
echo "⏳ Waiting for backend to initialize..."
sleep 5

# 检查后端是否启动成功
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Backend may not be ready yet, continuing...${NC}"
fi

# 检查 Node.js 和 npm
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  🎨 Starting Frontend Server"
echo "════════════════════════════════════════════════════════════════"
echo ""

if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed!${NC}"
    echo "Please install Node.js from https://nodejs.org/"
    kill $BACKEND_PID
    exit 1
fi

# 检查 node_modules
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

# 启动前端
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# 等待前端启动
sleep 3

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  ✅ Application Started Successfully!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}📡 Backend API:${NC}    http://localhost:8000"
echo -e "${GREEN}🎨 Frontend UI:${NC}    http://localhost:3000"
echo -e "${GREEN}📚 API Docs:${NC}       http://localhost:8000/docs"
echo -e "${GREEN}📖 ReDoc:${NC}          http://localhost:8000/redoc"
echo ""
echo -e "${BLUE}💡 Tips:${NC}"
echo "   - Backend uses virtual environment: .venv"
echo "   - Backend auto-reloads on code changes"
echo "   - Frontend auto-reloads on code changes"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all servers${NC}"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""

# 清理函数
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true

    # 等待进程结束
    sleep 2

    # 强制杀死如果还在运行
    kill -9 $BACKEND_PID 2>/dev/null || true
    kill -9 $FRONTEND_PID 2>/dev/null || true

    echo "✅ All servers stopped"
    exit 0
}

# 捕获 Ctrl+C
trap cleanup INT TERM

# 等待
wait

