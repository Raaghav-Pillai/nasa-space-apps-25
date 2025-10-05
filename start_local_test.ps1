# Start Local Test Environment
# This script helps you test the chatbot locally

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "STARTING LOCAL TEST ENVIRONMENT" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if port 8000 is in use
$portInUse = netstat -ano | findstr :8000
if ($portInUse) {
    Write-Host "Port 8000 is already in use." -ForegroundColor Yellow
    Write-Host "Stopping existing process..." -ForegroundColor Yellow
    
    # Get PID
    $pid = ($portInUse -split '\s+')[-1]
    Write-Host "Stopping process $pid..." -ForegroundColor Gray
    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

# Start backend in a new window
Write-Host ""
Write-Host "Starting backend server..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python api_server.py"

# Wait for server to start
Write-Host "Waiting for server to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Test backend
Write-Host ""
Write-Host "Testing backend..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
    Write-Host "✅ Backend is running!" -ForegroundColor Green
    Write-Host "   Health: $($health.status)" -ForegroundColor Gray
} catch {
    Write-Host "⚠️  Backend may still be starting..." -ForegroundColor Yellow
    Write-Host "   Wait a few seconds and try: http://localhost:8000/health" -ForegroundColor Gray
}

# Test chat status
try {
    $chatStatus = Invoke-RestMethod -Uri "http://localhost:8000/chat-status" -Method Get
    Write-Host "✅ Chat endpoint is available!" -ForegroundColor Green
    Write-Host "   AI Enabled: $($chatStatus.available)" -ForegroundColor Gray
    if (-not $chatStatus.available) {
        Write-Host "   Note: Running in mock mode (no Azure OpenAI)" -ForegroundColor Gray
    }
} catch {
    Write-Host "⚠️  Chat endpoint not responding yet" -ForegroundColor Yellow
}

# Open frontend
Write-Host ""
Write-Host "Opening frontend..." -ForegroundColor Cyan
$frontendPath = Resolve-Path "frontend_new/index.html"
Start-Process $frontendPath

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TEST ENVIRONMENT READY!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Backend: http://localhost:8000" -ForegroundColor Green
Write-Host "✅ Frontend: Opened in browser" -ForegroundColor Green
Write-Host "✅ Chatbot: Bottom-right corner" -ForegroundColor Green
Write-Host ""
Write-Host "TRY THESE QUESTIONS:" -ForegroundColor Yellow
Write-Host "  • 'What's the weather like?'" -ForegroundColor White
Write-Host "  • 'What activities do you recommend?'" -ForegroundColor White
Write-Host "  • 'Are there any events this weekend?'" -ForegroundColor White
Write-Host "  • 'Plan a 3-day trip for me'" -ForegroundColor White
Write-Host ""
Write-Host "API DOCS: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "TO ENABLE FULL AI:" -ForegroundColor Yellow
Write-Host "  Run: .\setup_chatbot.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C in the backend window to stop the server" -ForegroundColor Gray
Write-Host ""
