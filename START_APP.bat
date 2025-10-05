@echo off
echo ========================================
echo   Weather Trip Planner - Quick Start
echo ========================================
echo.

echo Starting backend server...
start "Weather API Server" cmd /k "python backend/api_server.py"

timeout /t 3 /nobreak > nul

echo Opening frontend...
start frontend_new/index.html

echo.
echo ========================================
echo   App is starting!
echo ========================================
echo.
echo Backend API: http://localhost:8000
echo Frontend: Opening in your browser...
echo.
echo Press any key to stop the backend server...
pause > nul
