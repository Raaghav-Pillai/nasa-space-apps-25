@echo off
echo ========================================
echo STARTING BACKEND WITH GEMINI
echo ========================================
echo.

REM Set Gemini API Key
set GEMINI_API_KEY=AIzaSyCRIK6ZjYpwO7YknZIO-kCFOuiPQwxrKpw

REM Change to backend directory
cd backend

REM Start the server
echo Starting server...
echo.
python api_server.py

pause
