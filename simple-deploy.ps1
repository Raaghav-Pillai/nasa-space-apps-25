# Simple deployment script
Write-Host "Deploying frontend to Azure Static Web Apps..." -ForegroundColor Green

# Create deployment directory
$tempDir = "temp-deploy"
if (Test-Path $tempDir) { Remove-Item -Recurse -Force $tempDir }
New-Item -ItemType Directory -Path $tempDir

# Copy frontend files
Copy-Item -Path "frontend/*" -Destination $tempDir -Recurse

Write-Host "Frontend package ready in $tempDir folder!" -ForegroundColor Green
Write-Host "Your Static Web App URL: https://zealous-rock-0ff90f10f.2.azurestaticapps.net" -ForegroundColor Cyan

Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Go to https://portal.azure.com"
Write-Host "2. Navigate to Static Web App: nasa-weather-frontend"
Write-Host "3. Upload the files from temp-deploy folder"

Get-ChildItem $tempDir