# Simple Azure Web App Deployment for Backend
# This deploys your FastAPI backend to Azure Web App for Containers

$RESOURCE_GROUP = "weather-app-rg"
$LOCATION = "eastus"
$APP_NAME = "weather-trip-api-$(Get-Random -Maximum 9999)"
$APP_SERVICE_PLAN = "weather-app-plan"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DEPLOYING BACKEND TO AZURE WEB APP" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "App Name: $APP_NAME" -ForegroundColor Gray
Write-Host ""

# Check if logged in to Azure
Write-Host "Checking Azure login..." -ForegroundColor Yellow
$account = az account show 2>$null
if (-not $account) {
    Write-Host "Not logged in to Azure. Please run: az login" -ForegroundColor Red
    exit 1
}
Write-Host "Azure login verified" -ForegroundColor Green

# Create resource group
Write-Host ""
Write-Host "Creating resource group..." -ForegroundColor Yellow
az group create --name $RESOURCE_GROUP --location $LOCATION --output none
Write-Host "Resource group ready" -ForegroundColor Green

# Create App Service Plan (Linux)
Write-Host ""
Write-Host "Creating App Service Plan..." -ForegroundColor Yellow
az appservice plan create `
    --name $APP_SERVICE_PLAN `
    --resource-group $RESOURCE_GROUP `
    --location $LOCATION `
    --is-linux `
    --sku B1 `
    --output none
Write-Host "App Service Plan created" -ForegroundColor Green

# Create Web App with Python runtime
Write-Host ""
Write-Host "Creating Web App..." -ForegroundColor Yellow
az webapp create `
    --name $APP_NAME `
    --resource-group $RESOURCE_GROUP `
    --plan $APP_SERVICE_PLAN `
    --runtime "PYTHON:3.10" `
    --output none
Write-Host "Web App created" -ForegroundColor Green

# Configure startup command
Write-Host ""
Write-Host "Configuring startup command..." -ForegroundColor Yellow
az webapp config set `
    --name $APP_NAME `
    --resource-group $RESOURCE_GROUP `
    --startup-file "gunicorn -w 4 -k uvicorn.workers.UvicornWorker api_server:app" `
    --output none

# Enable CORS
Write-Host "Enabling CORS..." -ForegroundColor Yellow
az webapp cors add `
    --name $APP_NAME `
    --resource-group $RESOURCE_GROUP `
    --allowed-origins "*" `
    --output none

# Deploy code using ZIP deploy
Write-Host ""
Write-Host "Preparing deployment package..." -ForegroundColor Yellow

# Create a temporary directory for deployment
$tempDir = New-Item -ItemType Directory -Path "temp_deploy" -Force

# Copy backend files
Copy-Item -Path "backend/*" -Destination $tempDir -Recurse -Force

# Create requirements.txt with gunicorn
$requirements = Get-Content "backend/requirements.txt"
$requirements += "`ngunicorn==21.2.0"
$requirements | Out-File "$tempDir/requirements.txt" -Encoding UTF8

# Create a zip file
Write-Host "Creating deployment package..." -ForegroundColor Yellow
Compress-Archive -Path "$tempDir/*" -DestinationPath "deploy.zip" -Force

# Deploy the zip file
Write-Host "Deploying to Azure..." -ForegroundColor Yellow
Write-Host "(This may take 3-5 minutes)" -ForegroundColor Gray
az webapp deployment source config-zip `
    --name $APP_NAME `
    --resource-group $RESOURCE_GROUP `
    --src "deploy.zip" `
    --output none

# Clean up
Remove-Item -Path $tempDir -Recurse -Force
Remove-Item -Path "deploy.zip" -Force

# Get the app URL
$API_URL = az webapp show `
    --name $APP_NAME `
    --resource-group $RESOURCE_GROUP `
    --query defaultHostName `
    -o tsv

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "API URL: https://$API_URL" -ForegroundColor Yellow
Write-Host "API Docs: https://$API_URL/docs" -ForegroundColor Yellow
Write-Host "Health Check: https://$API_URL/health" -ForegroundColor Yellow
Write-Host "Chat Status: https://$API_URL/chat-status" -ForegroundColor Yellow
Write-Host ""
Write-Host "Resource Group: $RESOURCE_GROUP" -ForegroundColor Gray
Write-Host "Web App: $APP_NAME" -ForegroundColor Gray
Write-Host ""
Write-Host "Testing deployment..." -ForegroundColor Yellow
Start-Sleep -Seconds 30
try {
    $response = Invoke-WebRequest -Uri "https://$API_URL/health" -UseBasicParsing -TimeoutSec 10
    Write-Host "Health check: OK" -ForegroundColor Green
} catch {
    Write-Host "Health check: Waiting for app to start (this is normal)" -ForegroundColor Yellow
    Write-Host "Try again in 1-2 minutes: https://$API_URL/health" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Wait 1-2 minutes for app to fully start" -ForegroundColor White
Write-Host "2. Test: https://$API_URL/health" -ForegroundColor White
Write-Host "3. Update frontend: .\update_frontend_api.ps1 -ApiUrl https://$API_URL" -ForegroundColor White
Write-Host "4. Run setup_chatbot.ps1 to enable AI features" -ForegroundColor White
Write-Host ""

# Save configuration
$config = @{
    apiUrl = "https://$API_URL"
    resourceGroup = $RESOURCE_GROUP
    webApp = $APP_NAME
    deploymentDate = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
}
$config | ConvertTo-Json | Out-File "backend-deployment-config.json"
Write-Host "Configuration saved to backend-deployment-config.json" -ForegroundColor Green
Write-Host ""
