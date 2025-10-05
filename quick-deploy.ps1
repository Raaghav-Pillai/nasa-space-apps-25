# Quick deployment script for Windows/PowerShell
Write-Host "🚀 NASA Weather App - Quick Azure Deployment" -ForegroundColor Green

# Check if Azure CLI is installed
if (!(Get-Command az -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Azure CLI not found. Please install it first." -ForegroundColor Red
    Write-Host "Download from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
}

# Login to Azure
Write-Host "🔐 Logging into Azure..." -ForegroundColor Yellow
az login

# Set variables
$RESOURCE_GROUP = "nasa-weather-hackathon"
$LOCATION = "eastus"
$APP_NAME = "nasa-weather-$(Get-Date -Format 'yyyyMMddHHmm')"

Write-Host "📦 Deploying with app name: $APP_NAME" -ForegroundColor Cyan

# Create resource group
Write-Host "🏗️ Creating resource group..." -ForegroundColor Yellow
az group create --name $RESOURCE_GROUP --location $LOCATION

# Deploy infrastructure
Write-Host "☁️ Deploying Azure resources..." -ForegroundColor Yellow
az deployment group create `
  --resource-group $RESOURCE_GROUP `
  --template-file azure-deploy.json `
  --parameters appName=$APP_NAME

# Get deployment outputs
$FUNCTION_APP = az deployment group show --resource-group $RESOURCE_GROUP --name azure-deploy --query properties.outputs.functionAppName.value -o tsv
$STATIC_WEB_APP = az deployment group show --resource-group $RESOURCE_GROUP --name azure-deploy --query properties.outputs.staticWebAppName.value -o tsv
$SEARCH_SERVICE = az deployment group show --resource-group $RESOURCE_GROUP --name azure-deploy --query properties.outputs.searchServiceName.value -o tsv

Write-Host "✅ Infrastructure deployed!" -ForegroundColor Green
Write-Host "Function App: $FUNCTION_APP" -ForegroundColor Cyan
Write-Host "Static Web App: $STATIC_WEB_APP" -ForegroundColor Cyan
Write-Host "Search Service: $SEARCH_SERVICE" -ForegroundColor Cyan

# Deploy backend
Write-Host "🐍 Deploying backend functions..." -ForegroundColor Yellow
cd backend
az functionapp deployment source config-zip --resource-group $RESOURCE_GROUP --name $FUNCTION_APP --src (Compress-Archive -Path * -DestinationPath ../backend.zip -Force; "../backend.zip")
cd ..

# Update frontend config
Write-Host "🌐 Updating frontend configuration..." -ForegroundColor Yellow
$configContent = @"
const AZURE_CONFIG = {
    FUNCTION_APP_URL: 'https://$FUNCTION_APP.azurewebsites.net',
    SEARCH_ENDPOINT: 'https://$SEARCH_SERVICE.search.windows.net',
    ENDPOINTS: {
        PREDICT: '/api/predict',
        SEARCH: '/api/search',
        HEALTH: '/api/health'
    }
};
window.AzureAPI = AzureAPI;
window.AZURE_CONFIG = AZURE_CONFIG;
"@

$configContent | Out-File -FilePath "frontend/azure-config.js" -Encoding UTF8

# Deploy frontend (manual step for hackathon speed)
Write-Host "📱 Frontend files updated!" -ForegroundColor Green
Write-Host "🎯 Next steps:" -ForegroundColor Yellow
Write-Host "1. Go to Azure Portal -> Static Web Apps -> $STATIC_WEB_APP"
Write-Host "2. Upload the frontend folder contents"
Write-Host "3. Or use: az staticwebapp environment set-env --name $STATIC_WEB_APP"

# Setup Elasticsearch
Write-Host "🔍 Setting up Elasticsearch..." -ForegroundColor Yellow
Write-Host "Run: python elasticsearch-setup.py"
Write-Host "Make sure to set ELASTICSEARCH_HOST environment variable"

Write-Host "🎉 Deployment complete!" -ForegroundColor Green
Write-Host "Your app will be available at: https://$STATIC_WEB_APP.azurestaticapps.net"