# Azure Container Apps Deployment Script for Backend
# This deploys your FastAPI backend to Azure Container Apps

$RESOURCE_GROUP = "weather-app-rg"
$LOCATION = "eastus"
$CONTAINER_APP_ENV = "weather-app-env"
$CONTAINER_APP_NAME = "weather-api"
$ACR_NAME = "weatherappreg$(Get-Random -Maximum 9999)"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DEPLOYING BACKEND TO AZURE" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
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
az group create --name $RESOURCE_GROUP --location $LOCATION
Write-Host "Resource group created" -ForegroundColor Green

# Create Azure Container Registry
Write-Host ""
Write-Host "Creating Azure Container Registry..." -ForegroundColor Yellow
az acr create `
    --resource-group $RESOURCE_GROUP `
    --name $ACR_NAME `
    --sku Basic `
    --admin-enabled true
Write-Host "Container Registry created" -ForegroundColor Green

# Build and push Docker image
Write-Host ""
Write-Host "Building and pushing Docker image..." -ForegroundColor Yellow
Set-Location backend
az acr build `
    --registry $ACR_NAME `
    --image weather-api:latest `
    .
Set-Location ..
Write-Host "Docker image built and pushed" -ForegroundColor Green

# Get ACR credentials
Write-Host ""
Write-Host "Getting ACR credentials..." -ForegroundColor Yellow
$ACR_USERNAME = az acr credential show --name $ACR_NAME --query username -o tsv
$ACR_PASSWORD = az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv
$ACR_LOGIN_SERVER = az acr show --name $ACR_NAME --query loginServer -o tsv

# Create Container Apps environment
Write-Host ""
Write-Host "Creating Container Apps environment..." -ForegroundColor Yellow
az containerapp env create `
    --name $CONTAINER_APP_ENV `
    --resource-group $RESOURCE_GROUP `
    --location $LOCATION
Write-Host "Container Apps environment created" -ForegroundColor Green

# Deploy Container App
Write-Host ""
Write-Host "Deploying Container App..." -ForegroundColor Yellow
az containerapp create `
    --name $CONTAINER_APP_NAME `
    --resource-group $RESOURCE_GROUP `
    --environment $CONTAINER_APP_ENV `
    --image "$ACR_LOGIN_SERVER/weather-api:latest" `
    --registry-server $ACR_LOGIN_SERVER `
    --registry-username $ACR_USERNAME `
    --registry-password $ACR_PASSWORD `
    --target-port 8000 `
    --ingress external `
    --cpu 1.0 `
    --memory 2.0Gi `
    --min-replicas 1 `
    --max-replicas 3
Write-Host "Container App deployed" -ForegroundColor Green

# Get the app URL
Write-Host ""
Write-Host "Getting application URL..." -ForegroundColor Yellow
$API_URL = az containerapp show `
    --name $CONTAINER_APP_NAME `
    --resource-group $RESOURCE_GROUP `
    --query properties.configuration.ingress.fqdn `
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
Write-Host "Container App: $CONTAINER_APP_NAME" -ForegroundColor Gray
Write-Host "Container Registry: $ACR_NAME" -ForegroundColor Gray
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Update frontend with new API URL" -ForegroundColor White
Write-Host "2. Redeploy frontend to Azure Static Web Apps" -ForegroundColor White
Write-Host "3. Run setup_chatbot.ps1 to enable AI features" -ForegroundColor White
Write-Host ""

# Save configuration
$config = @{
    apiUrl = "https://$API_URL"
    resourceGroup = $RESOURCE_GROUP
    containerApp = $CONTAINER_APP_NAME
    containerRegistry = $ACR_NAME
    deploymentDate = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
}
$config | ConvertTo-Json | Out-File "backend-deployment-config.json"
Write-Host "Configuration saved to backend-deployment-config.json" -ForegroundColor Green
