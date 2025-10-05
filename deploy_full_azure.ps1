# Complete Azure Deployment Script
# Deploys both backend and frontend to Azure

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 COMPLETE AZURE DEPLOYMENT" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This will deploy:" -ForegroundColor Yellow
Write-Host "  1. Backend API → Azure Container Apps" -ForegroundColor White
Write-Host "  2. Frontend → Azure Static Web Apps" -ForegroundColor White
Write-Host ""

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

# Check Azure CLI
$azVersion = az version 2>$null
if (-not $azVersion) {
    Write-Host "❌ Azure CLI not found. Install from: https://aka.ms/installazurecli" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Azure CLI installed" -ForegroundColor Green

# Check Docker
$dockerVersion = docker --version 2>$null
if (-not $dockerVersion) {
    Write-Host "❌ Docker not found. Install Docker Desktop from: https://www.docker.com/products/docker-desktop" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Docker installed" -ForegroundColor Green

# Check SWA CLI
$swaVersion = swa --version 2>$null
if (-not $swaVersion) {
    Write-Host "⚠️  Azure Static Web Apps CLI not found" -ForegroundColor Yellow
    Write-Host "Installing SWA CLI..." -ForegroundColor Yellow
    npm install -g @azure/static-web-apps-cli
}
Write-Host "✅ SWA CLI ready" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "STEP 1: Deploy Backend" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Deploy backend
.\deploy_backend_azure.ps1

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Backend deployment failed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "STEP 2: Update Frontend Configuration" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Update frontend with backend URL
.\update_frontend_api.ps1

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "STEP 3: Deploy Frontend" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Deploy frontend
Set-Location frontend_new
Write-Host "Deploying frontend to Azure Static Web Apps..." -ForegroundColor Yellow
swa deploy . --env production

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Frontend deployment failed" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Set-Location ..

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🎉 DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Read deployment config
$backendConfig = Get-Content "backend-deployment-config.json" | ConvertFrom-Json

Write-Host "📱 Your Application URLs:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Frontend: https://orange-coast-0614e430f.2.azurestaticapps.net" -ForegroundColor Cyan
Write-Host "Backend API: $($backendConfig.apiUrl)" -ForegroundColor Cyan
Write-Host "API Docs: $($backendConfig.apiUrl)/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "🎯 Test Your App:" -ForegroundColor Yellow
Write-Host "1. Open the frontend URL in your browser" -ForegroundColor White
Write-Host "2. Select a location (Chicago)" -ForegroundColor White
Write-Host "3. Choose an activity profile" -ForegroundColor White
Write-Host "4. Pick dates and generate report" -ForegroundColor White
Write-Host ""
Write-Host "🤖 Ready for LLM Integration!" -ForegroundColor Yellow
Write-Host "Your backend is now on Azure and ready to add:" -ForegroundColor White
Write-Host "  - Azure OpenAI for chat features" -ForegroundColor Gray
Write-Host "  - Custom LLM models" -ForegroundColor Gray
Write-Host "  - Voice interface with Azure Speech" -ForegroundColor Gray
Write-Host ""
Write-Host "📚 See AZURE_FULL_DEPLOYMENT.md for LLM integration guide" -ForegroundColor Cyan
Write-Host ""
