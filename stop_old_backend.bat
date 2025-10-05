@echo off
echo Stopping old backend...
taskkill /F /PID 15404
timeout /t 2
echo.
echo Old backend stopped!
echo.
echo Now run in PowerShell:
echo $env:GEMINI_API_KEY = 'AIzaSyCRIK6ZjYpwO7YknZIO-kCFOuiPQwxrKpw'
echo cd backend
echo python api_server.py
pause
