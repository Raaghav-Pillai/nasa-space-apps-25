# Simple Backend Deployment using Azure Web App
Write-Host "Deploying Backend to Azure Web App..." -ForegroundColor Cyan

$env:PATH += ";C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin"

$RESOURCE_GROUP = "nasa-weather-hackathon"
$LOCATION = "eastus"
$APP_NAME = "weather-api-$(Get-Random -Maximum 9999)"
$PLAN_NAME = "weather-plan"

Write-Host "Step 1: Creating App Service Plan..." -ForegroundColor Yellow
az appservice plan create `
    --name $PLAN_NAME `
    --resource-group $RESOURCE_GROUP `
    --location $LOCATION `
    --sku B1 `
    --is-linux

Write-Host "Step 2: Creating Web App..." -ForegroundColor Yellow
az webapp create `
    --resource-group $RESOURCE_GROUP `
    --plan $PLAN_NAME `
    --name $APP_NAME `
    --runtime "PYTHON:3.9"

Write-Host "Step 3: Configuring deployment..." -ForegroundColor Yellow

# Create deployment package
$DEPLOY_DIR = "backend_package"
if (Test-Path $DEPLOY_DIR) { Remove-Item -Recurse -Force $DEPLOY_DIR }
New-Item -ItemType Directory -Path $DEPLOY_DIR | Out-Null

# Copy files
Copy-Item -Path "backend/api_server.py" -Destination "$DEPLOY_DIR/application.py"
Copy-Item -Path "backend/prediction" -Destination "$DEPLOY_DIR/prediction" -Recurse
Copy-Item -Path "backend/data" -Destination "$DEPLOY_DIR/data" -Recurse
Copy-Item -Path "backend/requirements.txt" -Destination "$DEPLOY_DIR/requirements.txt"

# Create startup command
@"
gunicorn --bind=0.0.0.0:8000 --timeout 600 application:app
"@ | Out-File -FilePath "$DEPLOY_DIR/startup.txt" -Encoding UTF8

# Zip it
Compress-Archive -Path "$DEPLOY_DIR/*" -DestinationPath "backend_deploy.zip" -Force

Write-Host "Step 4: Deploying to Azure..." -ForegroundColor Yellow
az webapp deployment source config-zip `
    --resource-group $RESOURCE_GROUP `
    --name $APP_NAME `
    --src "backend_deploy.zip"

Write-Host "Step 5: Configuring app settings..." -ForegroundColor Yellow
az webapp config appsettings set `
    --resource-group $RESOURCE_GROUP `
    --name $APP_NAME `
    --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true

az webapp config set `
    --resource-group $RESOURCE_GROUP `
    --name $APP_NAME `
    --startup-file "gunicorn --bind=0.0.0.0:8000 --timeout 600 --worker-class uvicorn.workers.UvicornWorker application:app"

$BACKEND_URL = "https://$APP_NAME.azurewebsites.net"

Write-Host "`nBackend deployed!" -ForegroundColor Green
Write-Host "Backend URL: $BACKEND_URL" -ForegroundColor Cyan
Write-Host "`nUpdating frontend..." -ForegroundColor Yellow

# Update frontend
@"
// Azure Production Configuration
window.API_URL = '$BACKEND_URL';
console.log('Using Azure Backend:', window.API_URL);
"@ | Out-File -FilePath "frontend_new/azure-api-config.js" -Encoding UTF8

# Redeploy frontend
$TOKEN = az staticwebapp secrets list --name "weather-frontend-final" --resource-group $RESOURCE_GROUP --query "properties.apiKey" -o tsv
cd frontend_new
swa deploy --deployment-token $TOKEN --app-location . --no-use-keychain
cd ..

Write-Host "`nDEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "Frontend: https://orange-coast-0614e430f.2.azurestaticapps.net" -ForegroundColor Cyan
Write-Host "Backend: $BACKEND_URL" -ForegroundColor Cyan
Write-Host "`nTest backend: curl $BACKEND_URL/health" -ForegroundColor Yellow
