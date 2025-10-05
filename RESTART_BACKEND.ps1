# Restart Backend with Gemini
# This stops the old backend and starts the new one with Gemini

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RESTARTING BACKEND WITH GEMINI" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Stop old backend
Write-Host "Stopping old backend..." -ForegroundColor Yellow
$portInUse = netstat -ano | findstr :8000
if ($portInUse) {
    $pid = ($portInUse -split '\s+')[-1]
    Write-Host "  Found process: $pid" -ForegroundColor Gray
    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 3
    Write-Host "✅ Old backend stopped" -ForegroundColor Green
} else {
    Write-Host "  No backend running" -ForegroundColor Gray
}

# Set Gemini API key
$env:GEMINI_API_KEY = "AIzaSyCRIK6ZjYpwO7YknZIO-kCFOuiPQwxrKpw"

# Start new backend
Write-Host ""
Write-Host "Starting new backend with Gemini..." -ForegroundColor Cyan
Write-Host ""

$backendScript = @"
`$env:GEMINI_API_KEY = 'AIzaSyCRIK6ZjYpwO7YknZIO-kCFOuiPQwxrKpw'
Write-Host '========================================' -ForegroundColor Cyan
Write-Host 'BACKEND WITH GEMINI' -ForegroundColor Green
Write-Host '========================================' -ForegroundColor Cyan
Write-Host ''
Write-Host 'API Key: Set' -ForegroundColor Green
Write-Host 'Provider: Google Gemini 2.5 Flash' -ForegroundColor Green
Write-Host ''
cd backend
python api_server.py
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript

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

# Test chat status
Write-Host ""
Write-Host "Testing chat endpoint..." -ForegroundColor Yellow
try {
    $chatStatus = Invoke-RestMethod -Uri "http://localhost:8000/chat-status" -Method Get -TimeoutSec 2
    Write-Host "✅ Chat Status:" -ForegroundColor Green
    Write-Host "   Available: $($chatStatus.available)" -ForegroundColor Cyan
    Write-Host "   Provider: $($chatStatus.provider)" -ForegroundColor Cyan
    Write-Host "   Model: $($chatStatus.model)" -ForegroundColor Cyan
    
    if ($chatStatus.available) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "✅ CHATBOT IS READY!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Now refresh your browser and try the chatbot!" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "If browser is not open, open: frontend_new/index.html" -ForegroundColor White
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "⚠️  Chat is not available yet" -ForegroundColor Yellow
        Write-Host "   Check the backend window for errors" -ForegroundColor Gray
    }
} catch {
    Write-Host "⚠️  Could not reach chat endpoint" -ForegroundColor Yellow
    Write-Host "   Wait a few seconds and try: http://localhost:8000/chat-status" -ForegroundColor Gray
}

Write-Host ""
