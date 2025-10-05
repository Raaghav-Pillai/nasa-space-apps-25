@echo off
echo ========================================
echo STARTING WEATHER TRIP PLANNER
echo ========================================
echo.

REM Set Gemini API Key
set GEMINI_API_KEY=AIzaSyCRIK6ZjYpwO7YknZIO-kCFOuiPQwxrKpw

echo Starting backend server...
start "Weather API Backend" cmd /k "cd backend && set GEMINI_API_KEY=AIzaSyCRIK6ZjYpwO7YknZIO-kCFOuiPQwxrKpw && python api_server.py"

echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo Opening frontend...
start "" "frontend_new\index.html"

echo.
echo ========================================
echo WEATHER TRIP PLANNER IS RUNNING!
echo ========================================
echo.
echo Backend: http://localhost:8000
echo Frontend: Opened in your browser
echo Chatbot: Bottom-right corner
echo.
echo To stop: Close the backend window
echo.
pause
