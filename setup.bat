@echo off
echo ========================================
echo CYGNUSA Elite-Hire Setup Script
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

:: Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    pause
    exit /b 1
)

echo [1/4] Setting up Backend...
cd backend

:: Create virtual environment if not exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate and install dependencies
call venv\Scripts\activate
pip install -r requirements.txt

echo.
echo [2/4] Backend dependencies installed!
echo.

echo [3/4] Setting up Frontend...
cd ..\frontend
call npm install

echo.
echo [4/4] Frontend dependencies installed!
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo IMPORTANT: Make sure PostgreSQL is running and create the database:
echo   psql -U postgres -c "CREATE DATABASE hr_evaluation;"
echo.
echo To start the application:
echo.
echo   1. Start Backend (Terminal 1):
echo      cd backend
echo      venv\Scripts\activate
echo      uvicorn app.main:app --reload
echo.
echo   2. Seed Data (Optional - Terminal 1):
echo      python seed_data.py
echo.
echo   3. Start Frontend (Terminal 2):
echo      cd frontend
echo      npm run dev
echo.
echo   4. Open http://localhost:3000 in your browser
echo.
echo Test Credentials:
echo   Recruiter: recruiter@cygnusa.com / password123
echo.
pause
