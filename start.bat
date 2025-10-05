@echo off
echo Starting Weather App...
echo.

REM Check if frontend node_modules exists
if not exist "frontend\node_modules\" (
    echo Installing frontend dependencies...
    cd frontend
    call npm install
    cd ..
    echo.
)

REM Check if backend dependencies are installed
echo Checking backend dependencies...
cd backend
pip show flask >nul 2>&1
if errorlevel 1 (
    echo Installing backend dependencies...
    pip install -r requirements.txt
)
cd ..
echo.

REM Start backend in a new window
echo Starting Backend Server...
start "Backend Server" cmd /k "cd backend && python app.py"

REM Wait a moment for backend to initialize
timeout /t 3 /nobreak >nul

REM Start frontend in a new window
echo Starting Frontend...
start "Frontend Dev Server" cmd /k "cd frontend && call npm run dev"

echo.
echo Both servers are starting in separate windows.
echo Backend: http://localhost:5000
echo Frontend: Check the Frontend window for the URL (usually http://localhost:5173)
echo.
echo Close this window or press any key to exit this launcher.
pause >nul
