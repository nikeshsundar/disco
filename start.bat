@echo off
echo Starting CYGNUSA Elite-Hire...
echo.

:: Start Backend in a new window
start "Backend Server" cmd /k "cd /d %~dp0backend && venv\Scripts\activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

:: Wait a moment for backend to start
timeout /t 3 /nobreak >nul

:: Start Frontend in a new window
start "Frontend Server" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo Servers starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to open the application in browser...
pause >nul

start http://localhost:3000
