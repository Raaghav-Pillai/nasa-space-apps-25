# Quick Start Script for Chatbot with Gemini
# This starts everything you need to test the chatbot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 STARTING CHATBOT TEST ENVIRONMENT" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set Gemini API key
$env:GEMINI_API_KEY = "AIzaSyCRIK6ZjYpwO7YknZIO-kCFOuiPQwxrKpw"

# Kill any existing process on port 8000
Write-Host "Checking for existing backend..." -ForegroundColor Yellow
$portInUse = netstat -ano | findstr :8000
if ($portInUse) {
    $pid = ($portInUse -split '\s+')[-1]
    Write-Host "Stopping existing process ($pid)..." -ForegroundColor Gray
    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

# Start backend in new window
Write-Host "Starting backend with Gemini..." -ForegroundColor Cyan
$backendScript = @"
`$env:GEMINI_API_KEY = 'AIzaSyCRIK6ZjYpwO7YknZIO-kCFOuiPQwxrKpw'
cd backend
python api_server.py
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript

# Wait for backend to start
Write-Host "Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Test backend
Write-Host ""
Write-Host "Testing backend..." -ForegroundColor Yellow
$maxRetries = 5
$retryCount = 0
$backendReady = $false

while (-not $backendReady -and $retryCount -lt $maxRetries) {
    try {
        $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 2
        Write-Host "✅ Backend is running!" -ForegroundColor Green
        $backendReady = $true
    } catch {
        $retryCount++
        Write-Host "  Attempt $retryCount/$maxRetries..." -ForegroundColor Gray
        Start-Sleep -Seconds 2
    }
}

if (-not $backendReady) {
    Write-Host "⚠️  Backend may still be starting. Give it a few more seconds." -ForegroundColor Yellow
}

# Test chat status
try {
    $chatStatus = Invoke-RestMethod -Uri "http://localhost:8000/chat-status" -Method Get -TimeoutSec 2
    Write-Host "✅ Chat endpoint is available!" -ForegroundColor Green
    Write-Host "   Provider: $($chatStatus.provider)" -ForegroundColor Gray
    Write-Host "   Model: $($chatStatus.model)" -ForegroundColor Gray
    Write-Host "   AI Enabled: $($chatStatus.available)" -ForegroundColor Gray
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
Write-Host "✅ CHATBOT TEST ENVIRONMENT READY!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🤖 AI Chatbot: Google Gemini 2.5 Flash" -ForegroundColor Green
Write-Host "💰 Cost: FREE!" -ForegroundColor Green
Write-Host ""
Write-Host "WHAT TO DO:" -ForegroundColor Yellow
Write-Host "1. Look for the chatbot in the bottom-right corner" -ForegroundColor White
Write-Host "2. Click the yellow/beige header to open it" -ForegroundColor White
Write-Host "3. Try these questions:" -ForegroundColor White
Write-Host "   • 'What's the weather like?'" -ForegroundColor Gray
Write-Host "   • 'What should I do if it rains?'" -ForegroundColor Gray
Write-Host "   • 'Are there any events this weekend?'" -ForegroundColor Gray
Write-Host "   • 'Plan a 3-day trip for me'" -ForegroundColor Gray
Write-Host ""
Write-Host "USEFUL LINKS:" -ForegroundColor Yellow
Write-Host "  • API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  • Health: http://localhost:8000/health" -ForegroundColor Cyan
Write-Host "  • Chat Status: http://localhost:8000/chat-status" -ForegroundColor Cyan
Write-Host ""
Write-Host "To stop: Close the backend PowerShell window" -ForegroundColor Gray
Write-Host ""
