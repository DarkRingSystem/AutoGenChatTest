@echo off
REM AutoGen AI Chat - Windows Start Script (with Virtual Environment)

echo ================================================================
echo   AutoGen AI Chat - Development Environment (Windows)
echo ================================================================
echo.

REM Check .env file
if not exist backend\.env (
    echo [WARNING] Backend .env file not found!
    echo Creating .env from .env.example...
    copy backend\.env.example backend\.env
    echo [WARNING] Please edit backend\.env and add your API keys
    echo.
    pause
)

REM Check virtual environment
echo Checking virtual environment...
if not exist .venv (
    echo [ERROR] Virtual environment not found!
    echo Creating virtual environment...
    python -m venv .venv
    echo [OK] Virtual environment created
)

REM Activate virtual environment and check dependencies
echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Checking dependencies...
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo [WARNING] Some dependencies are missing
    echo Installing dependencies...
    pip install -r requirements.txt
    pip install "pillow>=11.0.0" --upgrade
    echo [OK] Dependencies installed
) else (
    echo [OK] All dependencies are installed
)

REM Start backend
echo.
echo ================================================================
echo   Starting Backend Server (Virtual Environment)
echo ================================================================
echo.

start "Backend Server" cmd /k "cd backend && ..\.venv\Scripts\activate.bat && python main.py"

REM Wait for backend to start
echo Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

REM Check Node.js
echo.
echo ================================================================
echo   Starting Frontend Server
echo ================================================================
echo.

where node >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Node.js is not installed!
    echo Please install Node.js from https://nodejs.org/
    exit /b 1
)

REM Check node_modules
if not exist frontend\node_modules (
    echo Installing frontend dependencies...
    cd frontend
    call npm install
    cd ..
)

REM Start frontend
start "Frontend Server" cmd /k "cd frontend && npm run dev"

REM Wait for frontend to start
timeout /t 3 /nobreak >nul

echo.
echo ================================================================
echo   Application Started Successfully!
echo ================================================================
echo.
echo [OK] Backend API:    http://localhost:8000
echo [OK] Frontend UI:    http://localhost:3000
echo [OK] API Docs:       http://localhost:8000/docs
echo [OK] ReDoc:          http://localhost:8000/redoc
echo.
echo Tips:
echo    - Backend uses virtual environment: .venv
echo    - Backend auto-reloads on code changes
echo    - Frontend auto-reloads on code changes
echo    - Close the terminal windows to stop servers
echo.
echo ================================================================
echo.
echo Press any key to exit this window...
echo (Backend and Frontend will continue running in separate windows)
pause >nul

