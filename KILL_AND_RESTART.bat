@echo off
echo ========================================
echo STOPPING OLD BACKEND AND RESTARTING
echo ========================================
echo.

echo Finding process on port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    echo Found PID: %%a
    echo Killing process...
    taskkill /F /PID %%a
    timeout /t 2 /nobreak >nul
)

echo.
echo Old backend stopped!
echo.
echo ========================================
echo STARTING NEW BACKEND WITH GEMINI
echo ========================================
echo.

REM Set Gemini API Key
set GEMINI_API_KEY=AIzaSyCRIK6ZjYpwO7YknZIO-kCFOuiPQwxrKpw

REM Change to backend directory
cd backend

REM Start the server
echo Starting server with Gemini...
echo.
echo You should see:
echo   - Google Gemini client initialized
echo   - AI Chatbot: ENABLED
echo.
python api_server.py

pause
