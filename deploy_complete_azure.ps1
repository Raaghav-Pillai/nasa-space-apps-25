# Complete Azure + Elasticsearch Deployment
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Complete Azure Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$env:PATH += ";C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin"

$RESOURCE_GROUP = "nasa-weather-hackathon"
$LOCATION = "eastus"
$CONTAINER_NAME = "weather-api-backend"
$ACR_NAME = "weatherreg$(Get-Random -Maximum 9999)"
$DNS_LABEL = "weather-api-$(Get-Random -Maximum 9999)"

Write-Host "`n1. Creating Azure Container Registry..." -ForegroundColor Yellow
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true

Write-Host "`n2. Building and pushing Docker image..." -ForegroundColor Yellow

# Create Dockerfile
@'
FROM python:3.9-slim

WORKDIR /app

# Copy requirements
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY backend/prediction /app/prediction
COPY backend/data /app/data
COPY backend/api_server.py /app/api_server.py

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "api_server.py"]
'@ | Out-File -FilePath "Dockerfile" -Encoding UTF8

# Build image
docker build -t weather-api:latest .

# Get ACR credentials
$ACR_SERVER = az acr show --name $ACR_NAME --query loginServer -o tsv
$ACR_USERNAME = az acr credential show --name $ACR_NAME --query username -o tsv
$ACR_PASSWORD = az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv

# Login and push
az acr login --name $ACR_NAME
docker tag weather-api:latest "$ACR_SERVER/weather-api:latest"
docker push "$ACR_SERVER/weather-api:latest"

Write-Host "`n3. Deploying to Azure Container Instances..." -ForegroundColor Yellow
az container create `
    --resource-group $RESOURCE_GROUP `
    --name $CONTAINER_NAME `
    --image "$ACR_SERVER/weather-api:latest" `
    --cpu 2 --memory 4 `
    --registry-login-server $ACR_SERVER `
    --registry-username $ACR_USERNAME `
    --registry-password $ACR_PASSWORD `
    --dns-name-label $DNS_LABEL `
    --ports 8000 `
    --environment-variables ELASTICSEARCH_URL=http://localhost:9200

Write-Host "`n4. Getting backend URL..." -ForegroundColor Yellow
$BACKEND_FQDN = az container show --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --query "ipAddress.fqdn" -o tsv
$BACKEND_URL = "http://${BACKEND_FQDN}:8000"

Write-Host "`n5. Updating frontend with backend URL..." -ForegroundColor Yellow
$FRONTEND_URL = "https://orange-coast-0614e430f.2.azurestaticapps.net"

# Create API config for frontend
@"
// Azure Production Configuration
window.API_URL = '$BACKEND_URL';
console.log('Using Azure Backend:', window.API_URL);
"@ | Out-File -FilePath "frontend_new/azure-api-config.js" -Encoding UTF8

# Update index.html to include config
$indexPath = "frontend_new/index.html"
$indexContent = Get-Content $indexPath -Raw
if ($indexContent -notmatch "azure-api-config.js") {
    $indexContent = $indexContent -replace '(<script src="app.js"></script>)', '<script src="azure-api-config.js"></script>`n    $1'
    $indexContent | Out-File -FilePath $indexPath -Encoding UTF8 -NoNewline
}

Write-Host "`n6. Redeploying frontend with backend URL..." -ForegroundColor Yellow
$TOKEN = az staticwebapp secrets list --name "weather-frontend-final" --resource-group $RESOURCE_GROUP --query "properties.apiKey" -o tsv

cd frontend_new
swa deploy --deployment-token $TOKEN --app-location . --no-use-keychain
cd ..

Write-Host "`n7. Setting up Elasticsearch..." -ForegroundColor Yellow
Write-Host "For Elasticsearch, you have two options:" -ForegroundColor Cyan
Write-Host "  A) Use Elastic Cloud (recommended): https://cloud.elastic.co" -ForegroundColor Gray
Write-Host "  B) Deploy Elasticsearch on Azure VM" -ForegroundColor Gray
Write-Host "`nCreating Elasticsearch setup script..." -ForegroundColor Yellow

# Create Elasticsearch data indexing script
@'
import sys
sys.path.insert(0, 'backend/prediction')
from predict_simple import predict_daily_range
from elasticsearch import Elasticsearch
import pandas as pd
from datetime import datetime, timedelta

# Elasticsearch configuration
ES_HOST = input("Enter Elasticsearch URL (e.g., https://your-deployment.es.io:9243): ")
ES_USERNAME = input("Enter Elasticsearch username (default: elastic): ") or "elastic"
ES_PASSWORD = input("Enter Elasticsearch password: ")

# Connect to Elasticsearch
es = Elasticsearch(
    [ES_HOST],
    basic_auth=(ES_USERNAME, ES_PASSWORD),
    verify_certs=True
)

print("Testing connection...")
if es.ping():
    print("✅ Connected to Elasticsearch!")
else:
    print("❌ Connection failed")
    exit(1)

# Create index
index_name = "weather-predictions"
mapping = {
    "mappings": {
        "properties": {
            "date": {"type": "date"},
            "location": {"type": "geo_point"},
            "avg_temperature_f": {"type": "float"},
            "avg_feels_like_f": {"type": "float"},
            "total_precipitation_mm": {"type": "float"},
            "avg_humidity_percent": {"type": "float"},
            "avg_cloud_cover_percent": {"type": "float"},
            "avg_wind_speed_mph": {"type": "float"},
            "timestamp": {"type": "date"}
        }
    }
}

if es.indices.exists(index=index_name):
    print(f"Deleting existing index: {index_name}")
    es.indices.delete(index=index_name)

es.indices.create(index=index_name, body=mapping)
print(f"✅ Created index: {index_name}")

# Generate and index predictions
print("\nGenerating predictions for next 30 days...")
start_date = datetime.now().strftime('%Y-%m-%d')
end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')

df = predict_daily_range(start_date, end_date)

# Index data
for idx, row in df.iterrows():
    doc = {
        "date": row['date'],
        "location": {"lat": 41.8781, "lon": -87.6298},
        "avg_temperature_f": float(row['avg_temperature_f']),
        "avg_feels_like_f": float(row['avg_feels_like_f']),
        "total_precipitation_mm": float(row['total_precipitation_mm']),
        "avg_humidity_percent": float(row['avg_humidity_percent']),
        "avg_cloud_cover_percent": float(row['avg_cloud_cover_percent']),
        "avg_wind_speed_mph": float(row['avg_wind_speed_mph']),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    es.index(index=index_name, id=row['date'], body=doc)
    print(f"Indexed: {row['date']}")

print(f"\n✅ Indexed {len(df)} predictions to Elasticsearch!")
print(f"\nYou can now search your data at: {ES_HOST}")
'@ | Out-File -FilePath "index_to_elasticsearch.py" -Encoding UTF8

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

Write-Host "`n📱 Frontend: $FRONTEND_URL" -ForegroundColor Cyan
Write-Host "🔧 Backend API: $BACKEND_URL" -ForegroundColor Cyan
Write-Host "📦 Container: $CONTAINER_NAME" -ForegroundColor Cyan
Write-Host "🐳 Registry: $ACR_NAME" -ForegroundColor Cyan

Write-Host "`n🔍 Elasticsearch Setup:" -ForegroundColor Yellow
Write-Host "1. Sign up at https://cloud.elastic.co (14-day free trial)" -ForegroundColor Gray
Write-Host "2. Create a deployment" -ForegroundColor Gray
Write-Host "3. Run: python index_to_elasticsearch.py" -ForegroundColor Gray
Write-Host "4. Enter your Elasticsearch credentials" -ForegroundColor Gray

Write-Host "`n✅ Your app is fully deployed to Azure!" -ForegroundColor Green
Write-Host "Backend may take 2-3 minutes to start up." -ForegroundColor Yellow

# Save deployment info
@"
Azure Deployment Complete
========================
Date: $(Get-Date)
Resource Group: $RESOURCE_GROUP
Frontend: $FRONTEND_URL
Backend: $BACKEND_URL
Container: $CONTAINER_NAME
Registry: $ACR_NAME

Next Steps:
1. Test backend: curl $BACKEND_URL/health
2. Open frontend: $FRONTEND_URL
3. Setup Elasticsearch: python index_to_elasticsearch.py
"@ | Out-File -FilePath "DEPLOYMENT_INFO.txt" -Encoding UTF8

Write-Host "`nDeployment info saved to DEPLOYMENT_INFO.txt" -ForegroundColor Gray
