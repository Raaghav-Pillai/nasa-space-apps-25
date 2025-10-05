#!/bin/bash

# Quick Azure deployment script for hackathon
echo "🚀 Starting Azure deployment..."

# Variables
RESOURCE_GROUP="nasa-weather-hackathon"
LOCATION="eastus"
APP_NAME="nasa-weather-$(date +%s)"

# Create resource group
echo "Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# Deploy infrastructure
echo "Deploying Azure resources..."
az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --template-file azure-deploy.json \
  --parameters appName=$APP_NAME

# Get deployment outputs
FUNCTION_APP=$(az deployment group show --resource-group $RESOURCE_GROUP --name azure-deploy --query properties.outputs.functionAppName.value -o tsv)
STATIC_WEB_APP=$(az deployment group show --resource-group $RESOURCE_GROUP --name azure-deploy --query properties.outputs.staticWebAppName.value -o tsv)
SEARCH_SERVICE=$(az deployment group show --resource-group $RESOURCE_GROUP --name azure-deploy --query properties.outputs.searchServiceName.value -o tsv)

echo "✅ Deployment complete!"
echo "Function App: $FUNCTION_APP"
echo "Static Web App: $STATIC_WEB_APP"
echo "Search Service: $SEARCH_SERVICE"

# Save config for later use
cat > azure-config.json << EOF
{
  "resourceGroup": "$RESOURCE_GROUP",
  "functionApp": "$FUNCTION_APP",
  "staticWebApp": "$STATIC_WEB_APP",
  "searchService": "$SEARCH_SERVICE"
}
EOF

echo "Config saved to azure-config.json"