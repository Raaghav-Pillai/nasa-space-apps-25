# Complete Azure Deployment Script
# Deploys frontend to Static Web Apps and backend to Azure Functions

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Azure Deployment - Weather App" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Set PATH
$env:PATH += ";C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin"

# Variables
$RESOURCE_GROUP = "nasa-weather-hackathon"
$LOCATION = "eastus"
$TIMESTAMP = Get-Date -Format "yyyyMMddHHmm"
$APP_NAME = "weather-app-$TIMESTAMP"
$STORAGE_NAME = "weatherstorage$TIMESTAMP"
$FUNCTION_APP = "weather-api-$TIMESTAMP"
$STATIC_WEB_APP = "weather-frontend-$TIMESTAMP"

Write-Host "`n1. Creating Resource Group..." -ForegroundColor Yellow
az group create --name $RESOURCE_GROUP --location $LOCATION

Write-Host "`n2. Creating Storage Account..." -ForegroundColor Yellow
az storage account create `
    --name $STORAGE_NAME `
    --resource-group $RESOURCE_GROUP `
    --location $LOCATION `
    --sku Standard_LRS

Write-Host "`n3. Creating Static Web App for Frontend..." -ForegroundColor Yellow
az staticwebapp create `
    --name $STATIC_WEB_APP `
    --resource-group $RESOURCE_GROUP `
    --location "East US 2"

# Get deployment token
$DEPLOYMENT_TOKEN = az staticwebapp secrets list `
    --name $STATIC_WEB_APP `
    --resource-group $RESOURCE_GROUP `
    --query "properties.apiKey" -o tsv

Write-Host "`n4. Deploying Frontend..." -ForegroundColor Yellow
Write-Host "Installing SWA CLI if needed..." -ForegroundColor Gray
npm list -g @azure/static-web-apps-cli 2>$null
if ($LASTEXITCODE -ne 0) {
    npm install -g @azure/static-web-apps-cli
}

# Deploy frontend
cd frontend_new
swa deploy --deployment-token $DEPLOYMENT_TOKEN --app-location . --no-use-keychain
cd ..

Write-Host "`n5. Creating Function App for Backend..." -ForegroundColor Yellow

# Create App Service Plan
az functionapp plan create `
    --resource-group $RESOURCE_GROUP `
    --name "$FUNCTION_APP-plan" `
    --location $LOCATION `
    --sku B1 `
    --is-linux

# Create Function App
az functionapp create `
    --resource-group $RESOURCE_GROUP `
    --name $FUNCTION_APP `
    --storage-account $STORAGE_NAME `
    --plan "$FUNCTION_APP-plan" `
    --runtime python `
    --runtime-version 3.9 `
    --functions-version 4

Write-Host "`n6. Preparing Backend for Deployment..." -ForegroundColor Yellow

# Create deployment package
$DEPLOY_DIR = "backend_deploy"
if (Test-Path $DEPLOY_DIR) { Remove-Item -Recurse -Force $DEPLOY_DIR }
New-Item -ItemType Directory -Path $DEPLOY_DIR | Out-Null

# Copy backend files
Copy-Item -Path "backend/api_server.py" -Destination "$DEPLOY_DIR/__init__.py"
Copy-Item -Path "backend/prediction" -Destination "$DEPLOY_DIR/prediction" -Recurse
Copy-Item -Path "backend/data" -Destination "$DEPLOY_DIR/data" -Recurse

# Create requirements.txt
@"
azure-functions
fastapi
uvicorn
pandas
numpy
scikit-learn
joblib
"@ | Out-File -FilePath "$DEPLOY_DIR/requirements.txt" -Encoding UTF8

# Create function.json
@"
{
  "scriptFile": "__init__.py",
  "bindings": [
    {
      "authLevel": "anonymous",
      "type": "httpTrigger",
      "direction": "in",
      "name": "req",
      "methods": ["get", "post"],
      "route": "{*route}"
    },
    {
      "type": "http",
      "direction": "out",
      "name": "`$return"
    }
  ]
}
"@ | Out-File -FilePath "$DEPLOY_DIR/function.json" -Encoding UTF8

# Create host.json
@"
{
  "version": "2.0",
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[3.*, 4.0.0)"
  }
}
"@ | Out-File -FilePath "$DEPLOY_DIR/host.json" -Encoding UTF8

Write-Host "`n7. Deploying Backend to Azure Functions..." -ForegroundColor Yellow

# Zip the deployment
Compress-Archive -Path "$DEPLOY_DIR/*" -DestinationPath "backend_deploy.zip" -Force

# Deploy to Azure Functions
az functionapp deployment source config-zip `
    --resource-group $RESOURCE_GROUP `
    --name $FUNCTION_APP `
    --src "backend_deploy.zip"

Write-Host "`n8. Configuring CORS..." -ForegroundColor Yellow
$STATIC_URL = az staticwebapp show `
    --name $STATIC_WEB_APP `
    --resource-group $RESOURCE_GROUP `
    --query "defaultHostname" -o tsv

az functionapp cors add `
    --resource-group $RESOURCE_GROUP `
    --name $FUNCTION_APP `
    --allowed-origins "https://$STATIC_URL" "*"

Write-Host "`n9. Updating Frontend API URL..." -ForegroundColor Yellow
$FUNCTION_URL = "https://$FUNCTION_APP.azurewebsites.net"

# Update frontend config
$configContent = @"
// Azure configuration - PRODUCTION
const API_URL = '$FUNCTION_URL';
"@

$configContent | Out-File -FilePath "frontend_new/azure-api-config.js" -Encoding UTF8

# Update index.html to include config
$indexContent = Get-Content "frontend_new/index.html" -Raw
if ($indexContent -notmatch "azure-api-config.js") {
    $indexContent = $indexContent -replace '<script src="app.js"></script>', '<script src="azure-api-config.js"></script><script src="app.js"></script>'
    $indexContent | Out-File -FilePath "frontend_new/index.html" -Encoding UTF8
}

# Redeploy frontend with updated config
cd frontend_new
swa deploy --deployment-token $DEPLOYMENT_TOKEN --app-location . --no-use-keychain
cd ..

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

Write-Host "`n📱 Frontend URL: https://$STATIC_URL" -ForegroundColor Cyan
Write-Host "🔧 Backend API: $FUNCTION_URL" -ForegroundColor Cyan
Write-Host "📦 Resource Group: $RESOURCE_GROUP" -ForegroundColor Cyan

Write-Host "`n✅ Your Weather App is now live on Azure!" -ForegroundColor Green
Write-Host "`nNote: Backend may take 2-3 minutes to warm up on first request." -ForegroundColor Yellow

# Save deployment info
$deployInfo = @"
Deployment Information
=====================
Date: $(Get-Date)
Resource Group: $RESOURCE_GROUP
Frontend: https://$STATIC_URL
Backend: $FUNCTION_URL
Storage: $STORAGE_NAME
FunctionApp: $FUNCTION_APP
StaticWebApp: $STATIC_WEB_APP
"@

$deployInfo | Out-File -FilePath "AZURE_DEPLOYMENT_INFO.txt" -Encoding UTF8

Write-Host "`nDeployment info saved to AZURE_DEPLOYMENT_INFO.txt" -ForegroundColor Gray
