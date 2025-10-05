# Setup AI Chatbot with Azure OpenAI
# This script helps you configure the AI chatbot feature

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🤖 AI CHATBOT SETUP" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Azure CLI is installed
$azVersion = az version 2>$null
if (-not $azVersion) {
    Write-Host "❌ Azure CLI not found. Please install it first." -ForegroundColor Red
    Write-Host "   Install: winget install Microsoft.AzureCLI" -ForegroundColor Yellow
    exit 1
}

# Check if logged in
$account = az account show 2>$null
if (-not $account) {
    Write-Host "❌ Not logged in to Azure. Running az login..." -ForegroundColor Yellow
    az login
}

Write-Host "✅ Azure CLI ready" -ForegroundColor Green
Write-Host ""

# Configuration
$RESOURCE_GROUP = "weather-app-rg"
$OPENAI_NAME = "weather-trip-openai"
$LOCATION = "eastus"
$DEPLOYMENT_NAME = "gpt-4"

Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  Resource Group: $RESOURCE_GROUP" -ForegroundColor Gray
Write-Host "  OpenAI Name: $OPENAI_NAME" -ForegroundColor Gray
Write-Host "  Location: $LOCATION" -ForegroundColor Gray
Write-Host "  Model: $DEPLOYMENT_NAME" -ForegroundColor Gray
Write-Host ""

# Ask user for confirmation
$confirm = Read-Host "Do you want to create Azure OpenAI resource? (y/n)"
if ($confirm -ne "y") {
    Write-Host "Setup cancelled." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Step 1: Creating Azure OpenAI Resource" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Create resource group if it doesn't exist
Write-Host "Checking resource group..." -ForegroundColor Yellow
$rgExists = az group exists --name $RESOURCE_GROUP
if ($rgExists -eq "false") {
    Write-Host "Creating resource group..." -ForegroundColor Yellow
    az group create --name $RESOURCE_GROUP --location $LOCATION
}
Write-Host "✅ Resource group ready" -ForegroundColor Green

# Create Azure OpenAI resource
Write-Host ""
Write-Host "Creating Azure OpenAI resource..." -ForegroundColor Yellow
Write-Host "(This may take 2-3 minutes)" -ForegroundColor Gray

$createResult = az cognitiveservices account create `
    --name $OPENAI_NAME `
    --resource-group $RESOURCE_GROUP `
    --kind OpenAI `
    --sku S0 `
    --location $LOCATION `
    --yes 2>&1

if ($LASTEXITCODE -ne 0) {
    if ($createResult -like "*already exists*") {
        Write-Host "⚠️  Resource already exists, continuing..." -ForegroundColor Yellow
    } else {
        Write-Host "❌ Failed to create Azure OpenAI resource" -ForegroundColor Red
        Write-Host $createResult -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✅ Azure OpenAI resource created" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Step 2: Deploying GPT-4 Model" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Deploying GPT-4 model..." -ForegroundColor Yellow
Write-Host "(This may take 1-2 minutes)" -ForegroundColor Gray

$deployResult = az cognitiveservices account deployment create `
    --name $OPENAI_NAME `
    --resource-group $RESOURCE_GROUP `
    --deployment-name $DEPLOYMENT_NAME `
    --model-name gpt-4 `
    --model-version "0613" `
    --model-format OpenAI `
    --sku-capacity 10 `
    --sku-name "Standard" 2>&1

if ($LASTEXITCODE -ne 0) {
    if ($deployResult -like "*already exists*") {
        Write-Host "⚠️  Deployment already exists, continuing..." -ForegroundColor Yellow
    } else {
        Write-Host "❌ Failed to deploy GPT-4 model" -ForegroundColor Red
        Write-Host $deployResult -ForegroundColor Red
        Write-Host ""
        Write-Host "Note: GPT-4 may not be available in your region." -ForegroundColor Yellow
        Write-Host "Try using GPT-3.5-Turbo instead (cheaper and faster):" -ForegroundColor Yellow
        Write-Host "  --model-name gpt-35-turbo" -ForegroundColor Gray
        exit 1
    }
} else {
    Write-Host "✅ GPT-4 model deployed" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Step 3: Getting API Credentials" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get API key
Write-Host "Retrieving API key..." -ForegroundColor Yellow
$API_KEY = az cognitiveservices account keys list `
    --name $OPENAI_NAME `
    --resource-group $RESOURCE_GROUP `
    --query key1 `
    -o tsv

# Get endpoint
Write-Host "Retrieving endpoint..." -ForegroundColor Yellow
$ENDPOINT = az cognitiveservices account show `
    --name $OPENAI_NAME `
    --resource-group $RESOURCE_GROUP `
    --query properties.endpoint `
    -o tsv

Write-Host "✅ Credentials retrieved" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Step 4: Configuring Backend" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Create .env file for local development
$envContent = @"
# Azure OpenAI Configuration
AZURE_OPENAI_KEY=$API_KEY
AZURE_OPENAI_ENDPOINT=$ENDPOINT
AZURE_OPENAI_DEPLOYMENT=$DEPLOYMENT_NAME
"@

$envPath = "backend/.env"
$envContent | Out-File $envPath -Encoding UTF8

Write-Host "✅ Created backend/.env file" -ForegroundColor Green

# Ask if user wants to update Azure Container App
Write-Host ""
$updateAzure = Read-Host "Do you want to update Azure Container App with these credentials? (y/n)"

if ($updateAzure -eq "y") {
    Write-Host ""
    Write-Host "Updating Azure Container App..." -ForegroundColor Yellow
    
    az containerapp update `
        --name weather-api `
        --resource-group $RESOURCE_GROUP `
        --set-env-vars `
            AZURE_OPENAI_KEY=$API_KEY `
            AZURE_OPENAI_ENDPOINT=$ENDPOINT `
            AZURE_OPENAI_DEPLOYMENT=$DEPLOYMENT_NAME
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Azure Container App updated" -ForegroundColor Green
        Write-Host ""
        Write-Host "Restarting container app..." -ForegroundColor Yellow
        az containerapp revision restart `
            --name weather-api `
            --resource-group $RESOURCE_GROUP
        Write-Host "✅ Container app restarted" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Container app not found or update failed" -ForegroundColor Yellow
        Write-Host "   You can update it later after deploying the backend" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🎉 SETUP COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 Configuration Summary:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Azure OpenAI Resource: $OPENAI_NAME" -ForegroundColor Cyan
Write-Host "Endpoint: $ENDPOINT" -ForegroundColor Cyan
Write-Host "Model Deployment: $DEPLOYMENT_NAME" -ForegroundColor Cyan
Write-Host "API Key: $($API_KEY.Substring(0, 10))..." -ForegroundColor Cyan
Write-Host ""

Write-Host "📁 Configuration Files:" -ForegroundColor Yellow
Write-Host "  ✅ backend/.env (for local development)" -ForegroundColor Green
if ($updateAzure -eq "y") {
    Write-Host "  ✅ Azure Container App (environment variables)" -ForegroundColor Green
}
Write-Host ""

Write-Host "🚀 Next Steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Test locally:" -ForegroundColor White
Write-Host "   cd backend" -ForegroundColor Gray
Write-Host "   python api_server.py" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Open frontend and test chatbot:" -ForegroundColor White
Write-Host "   Open frontend_new/index.html" -ForegroundColor Gray
Write-Host "   Look for chatbot in bottom-right corner" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Try these questions:" -ForegroundColor White
Write-Host "   - 'What's the weather like?'" -ForegroundColor Gray
Write-Host "   - 'What activities do you recommend?'" -ForegroundColor Gray
Write-Host "   - 'Are there any events this weekend?'" -ForegroundColor Gray
Write-Host ""

Write-Host "📚 Documentation:" -ForegroundColor Yellow
Write-Host "  See CHATBOT_SETUP_GUIDE.md for detailed information" -ForegroundColor White
Write-Host ""

Write-Host "💰 Cost Estimate:" -ForegroundColor Yellow
Write-Host "  GPT-4: ~$30-50/month for light usage" -ForegroundColor White
Write-Host "  (100 conversations/day)" -ForegroundColor Gray
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Your AI chatbot is ready! 🤖" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
