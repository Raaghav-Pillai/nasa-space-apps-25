# 🚀 HACKATHON QUICK DEPLOY GUIDE

## Prerequisites (5 minutes)
1. **Azure CLI**: `winget install Microsoft.AzureCLI`
2. **Azure Account**: Sign up at portal.azure.com (free tier works)
3. **Docker Desktop**: For local Elasticsearch testing

## Option 1: Full Azure Deployment (15 minutes)

### Step 1: Deploy Infrastructure
```powershell
# Run the deployment script
.\quick-deploy.ps1
```

### Step 2: Setup Elasticsearch
```bash
# Option A: Use Azure Cognitive Search (recommended for hackathon)
# Already included in deployment script

# Option B: Use Elastic Cloud
# 1. Go to cloud.elastic.co
# 2. Create free trial
# 3. Get connection details
# 4. Update environment variables
```

### Step 3: Test Everything
```bash
# Test the API
curl https://your-function-app.azurewebsites.net/api/health

# Test prediction
curl -X POST https://your-function-app.azurewebsites.net/api/predict \
  -H "Content-Type: application/json" \
  -d '{"date": "2024-07-15", "hour": 14}'
```

## Option 2: Local Development with Docker (10 minutes)

### Step 1: Start Services
```bash
# Start Elasticsearch and Kibana
docker-compose up -d

# Wait for services to start (30 seconds)
```

### Step 2: Setup Elasticsearch
```bash
# Setup indices and sample data
python elasticsearch-setup.py
```

### Step 3: Run Backend Locally
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn function_app:app --host 0.0.0.0 --port 8000
```

### Step 4: Serve Frontend
```bash
cd frontend
# Use any local server, e.g.:
python -m http.server 3000
# Or use Live Server in VS Code
```

## Quick URLs After Deployment

- **Frontend**: https://your-static-web-app.azurestaticapps.net
- **API**: https://your-function-app.azurewebsites.net
- **Kibana**: http://localhost:5601 (local only)
- **Elasticsearch**: http://localhost:9200 (local only)

## Environment Variables to Set

```bash
# In Azure Function App Settings
SEARCH_ENDPOINT=https://your-search-service.search.windows.net
SEARCH_KEY=your-admin-key
ELASTICSEARCH_HOST=your-elasticsearch-host:9200
```

## Testing the Integration

### 1. Health Check
```javascript
// In browser console
AzureAPI.healthCheck().then(console.log)
```

### 2. Make a Prediction
```javascript
// In browser console
AzureAPI.predict('2024-07-15', 14).then(console.log)
```

### 3. Search Historical Data
```javascript
// In browser console
AzureAPI.search('temperature', {date: '2024-07-15'}).then(console.log)
```

## Troubleshooting

### Common Issues:
1. **CORS errors**: Add your domain to Function App CORS settings
2. **Search not working**: Check search service key and endpoint
3. **Functions not deploying**: Ensure Python 3.9 runtime

### Quick Fixes:
```bash
# Restart function app
az functionapp restart --name your-function-app --resource-group nasa-weather-hackathon

# Check logs
az functionapp log tail --name your-function-app --resource-group nasa-weather-hackathon

# Update app settings
az functionapp config appsettings set --name your-function-app --resource-group nasa-weather-hackathon --settings SEARCH_ENDPOINT=your-endpoint
```

## Demo Data

The system includes sample weather predictions for testing:
- Chicago coordinates: 41.8826, -87.6227
- Sample dates: 2024-01-15, various hours
- Temperature predictions with confidence scores

## Next Steps for Production

1. **Scale up**: Move from free tiers to production tiers
2. **Security**: Add authentication and API keys
3. **Monitoring**: Set up Application Insights alerts
4. **Data**: Connect real NASA satellite data feeds
5. **ML Models**: Deploy your trained models to Azure ML

## Support

If you run into issues during the hackathon:
1. Check the Azure portal for error messages
2. Use browser dev tools to debug API calls
3. Check function app logs in Azure portal
4. Test locally with docker-compose first

Good luck! 🎉