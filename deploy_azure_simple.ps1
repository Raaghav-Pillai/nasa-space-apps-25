# Simple Azure Deployment Script
Write-Host "Azure Deployment Starting..." -ForegroundColor Cyan

# Set PATH
$env:PATH += ";C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin"

# Variables
$RESOURCE_GROUP = "nasa-weather-hackathon"
$LOCATION = "eastus"
$STATIC_WEB_APP = "weather-frontend-final"

Write-Host "Step 1: Creating Static Web App..." -ForegroundColor Yellow
az staticwebapp create --name $STATIC_WEB_APP --resource-group $RESOURCE_GROUP --location "East US 2"

Write-Host "Step 2: Getting deployment token..." -ForegroundColor Yellow
$TOKEN = az staticwebapp secrets list --name $STATIC_WEB_APP --resource-group $RESOURCE_GROUP --query "properties.apiKey" -o tsv

Write-Host "Step 3: Deploying frontend..." -ForegroundColor Yellow
cd frontend_new
swa deploy --deployment-token $TOKEN --app-location . --no-use-keychain
cd ..

$URL = az staticwebapp show --name $STATIC_WEB_APP --resource-group $RESOURCE_GROUP --query "defaultHostname" -o tsv

Write-Host "DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "Frontend URL: https://$URL" -ForegroundColor Cyan
Write-Host "Note: Backend will run locally for now" -ForegroundColor Yellow
