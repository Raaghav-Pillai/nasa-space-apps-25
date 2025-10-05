# 🚀 Complete Azure Deployment Guide

## Quick Start (5 Minutes)

```powershell
# 1. Deploy everything to Azure
.\deploy_full_azure.ps1

# That's it! Your app is now fully on Azure.
```

## What Gets Deployed

### Backend (Azure Container Apps)
- ✅ FastAPI server with ML models
- ✅ Auto-scaling (1-3 instances)
- ✅ HTTPS with custom domain support
- ✅ Ready for LLM integration
- ✅ Monitoring and logging

### Frontend (Azure Static Web Apps)
- ✅ Already deployed at: https://orange-coast-0614e430f.2.azurestaticapps.net
- ✅ Will be updated with new backend URL
- ✅ Global CDN
- ✅ Automatic HTTPS

## Prerequisites

### 1. Install Azure CLI
```powershell
winget install Microsoft.AzureCLI
```

### 2. Install Docker Desktop
Download from: https://www.docker.com/products/docker-desktop
Make sure it's running before deployment.

### 3. Login to Azure
```powershell
az login
```

### 4. Install SWA CLI (if not already installed)
```powershell
npm install -g @azure/static-web-apps-cli
```

## Deployment Steps

### Option 1: One-Click Deployment (Recommended)

```powershell
.\deploy_full_azure.ps1
```

This script will:
1. ✅ Deploy backend to Azure Container Apps (~10 min)
2. ✅ Update frontend with backend URL
3. ✅ Redeploy frontend to Azure Static Web Apps (~2 min)
4. ✅ Give you all URLs

### Option 2: Step-by-Step Deployment

#### Step 1: Deploy Backend

```powershell
.\deploy_backend_azure.ps1
```

Wait for completion (~10-15 minutes). You'll get an API URL like:
`https://weather-api.something.eastus.azurecontainerapps.io`

#### Step 2: Update Frontend

```powershell
.\update_frontend_api.ps1
```

This reads the backend URL from `backend-deployment-config.json` and updates `frontend_new/azure-api-config.js`.

#### Step 3: Deploy Frontend

```powershell
cd frontend_new
swa deploy . --env production
```

## After Deployment

### Test Your App

1. **Open Frontend**: https://orange-coast-0614e430f.2.azurestaticapps.net
2. **Select Location**: Choose Chicago or any location
3. **Pick Activity**: Select "Beach Day" or custom profile
4. **Choose Dates**: Pick a date range
5. **Generate Report**: See weather predictions with avatar

### Check Backend Health

```powershell
# Get your API URL from backend-deployment-config.json
$config = Get-Content backend-deployment-config.json | ConvertFrom-Json
$apiUrl = $config.apiUrl

# Test health endpoint
curl "$apiUrl/health"

# View API docs
Start-Process "$apiUrl/docs"
```

### View Logs

```powershell
az containerapp logs show `
    --name weather-api `
    --resource-group weather-app-rg `
    --follow
```

## 🤖 Adding LLM Integration

Your backend is now ready for LLM! Here's how to add it:

### Option 1: Azure OpenAI (Recommended for Hackathon)

#### 1. Create Azure OpenAI Resource

```powershell
az cognitiveservices account create `
    --name weather-openai `
    --resource-group weather-app-rg `
    --kind OpenAI `
    --sku S0 `
    --location eastus
```

#### 2. Deploy GPT-4 Model

```powershell
az cognitiveservices account deployment create `
    --name weather-openai `
    --resource-group weather-app-rg `
    --deployment-name gpt-4 `
    --model-name gpt-4 `
    --model-version "0613" `
    --model-format OpenAI `
    --sku-capacity 10 `
    --sku-name "Standard"
```

#### 3. Get API Key

```powershell
az cognitiveservices account keys list `
    --name weather-openai `
    --resource-group weather-app-rg
```

#### 4. Update Backend Code

Add to `backend/api_server.py`:

```python
from openai import AzureOpenAI
import os

# Initialize Azure OpenAI client
openai_client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-02-01",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

@app.post("/chat")
async def chat_weather(message: str, weather_data: dict = None):
    """Chat with AI about weather"""
    
    system_prompt = """You are a friendly weather expert assistant. 
    Help users understand weather predictions and plan their activities.
    Be conversational and helpful."""
    
    user_message = message
    if weather_data:
        user_message += f"\n\nCurrent weather data: {weather_data}"
    
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=0.7,
        max_tokens=500
    )
    
    return {
        "response": response.choices[0].message.content,
        "model": "gpt-4"
    }

@app.post("/recommend")
async def get_recommendations(weather_data: dict, preferences: dict):
    """Get AI-powered activity recommendations"""
    
    prompt = f"""Based on this weather forecast:
    Temperature: {weather_data.get('temperature')}°F
    Precipitation: {weather_data.get('precipitation')}mm
    Wind: {weather_data.get('wind_speed')}mph
    Cloud Cover: {weather_data.get('cloud_cover')}%
    
    And these preferences:
    {preferences}
    
    Suggest 3 specific activities with explanations."""
    
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful activity planner."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
        max_tokens=400
    )
    
    return {
        "recommendations": response.choices[0].message.content
    }
```

#### 5. Add Environment Variables to Container App

```powershell
# Get your OpenAI endpoint
$endpoint = az cognitiveservices account show `
    --name weather-openai `
    --resource-group weather-app-rg `
    --query properties.endpoint `
    -o tsv

# Get your API key
$key = az cognitiveservices account keys list `
    --name weather-openai `
    --resource-group weather-app-rg `
    --query key1 `
    -o tsv

# Update container app
az containerapp update `
    --name weather-api `
    --resource-group weather-app-rg `
    --set-env-vars `
        AZURE_OPENAI_KEY=$key `
        AZURE_OPENAI_ENDPOINT=$endpoint
```

#### 6. Update requirements.txt

Add to `backend/requirements.txt`:
```
openai==1.12.0
```

#### 7. Rebuild and Redeploy

```powershell
.\deploy_backend_azure.ps1
```

### Option 2: Hugging Face Models (Self-Hosted)

For running your own LLM models:

```python
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM

# Load model at startup (do this once)
model_name = "meta-llama/Llama-2-7b-chat-hf"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
llm = pipeline("text-generation", model=model, tokenizer=tokenizer)

@app.post("/chat")
async def chat_weather(message: str):
    response = llm(message, max_length=200, temperature=0.7)
    return {"response": response[0]["generated_text"]}
```

**Note**: For self-hosted models, you'll need larger instances:

```powershell
az containerapp update `
    --name weather-api `
    --resource-group weather-app-rg `
    --cpu 4.0 `
    --memory 8.0Gi `
    --min-replicas 1 `
    --max-replicas 2
```

## Frontend LLM Integration

Add chat interface to `frontend_new/index.html`:

```html
<!-- Add to your report section -->
<div class="chat-section">
    <h3>💬 Ask About This Weather</h3>
    <div id="chat-messages"></div>
    <input type="text" id="chat-input" placeholder="Ask me anything about this weather...">
    <button onclick="sendChatMessage()">Send</button>
</div>
```

Add to `frontend_new/app.js`:

```javascript
async function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value;
    
    const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            message: message,
            weather_data: state.weatherData
        })
    });
    
    const data = await response.json();
    displayChatMessage(message, data.response);
    input.value = '';
}
```

## Cost Estimates

### Current Setup (No LLM)
- **Container Apps**: ~$30-50/month
- **Container Registry**: ~$5/month
- **Static Web Apps**: Free
- **Total**: ~$35-55/month

### With Azure OpenAI
- **Base**: ~$35-55/month
- **GPT-4**: ~$0.03 per 1K tokens (~$50-200/month depending on usage)
- **Total**: ~$85-255/month

### With Self-Hosted LLM
- **Container Apps** (larger): ~$150-300/month
- **Storage**: ~$10/month
- **Total**: ~$160-310/month

## Monitoring & Scaling

### View Application Insights

```powershell
# Enable Application Insights
az containerapp update `
    --name weather-api `
    --resource-group weather-app-rg `
    --enable-app-insights

# View metrics in Azure Portal
Start-Process "https://portal.azure.com"
```

### Scale for Production

```powershell
# Increase capacity
az containerapp update `
    --name weather-api `
    --resource-group weather-app-rg `
    --min-replicas 2 `
    --max-replicas 10 `
    --cpu 2.0 `
    --memory 4.0Gi
```

### Set Up Alerts

```powershell
# Alert on high CPU
az monitor metrics alert create `
    --name high-cpu-alert `
    --resource-group weather-app-rg `
    --scopes /subscriptions/{subscription-id}/resourceGroups/weather-app-rg/providers/Microsoft.App/containerApps/weather-api `
    --condition "avg Percentage CPU > 80" `
    --description "Alert when CPU exceeds 80%"
```

## Troubleshooting

### Backend Not Responding

```powershell
# Check logs
az containerapp logs show `
    --name weather-api `
    --resource-group weather-app-rg `
    --follow

# Restart app
az containerapp revision restart `
    --name weather-api `
    --resource-group weather-app-rg
```

### Frontend Can't Reach Backend

1. Check `frontend_new/azure-api-config.js` has correct URL
2. Verify CORS settings in `backend/api_server.py`
3. Test backend directly: `curl https://your-api-url/health`
4. Check browser console for errors

### Docker Build Fails

```powershell
# Test build locally first
cd backend
docker build -t test-weather-api .
docker run -p 8000:8000 test-weather-api

# If successful, then deploy to Azure
```

### Out of Memory

```powershell
# Increase memory
az containerapp update `
    --name weather-api `
    --resource-group weather-app-rg `
    --memory 4.0Gi
```

## Security Best Practices

### 1. Use Azure Key Vault for Secrets

```powershell
# Create Key Vault
az keyvault create `
    --name weather-app-kv `
    --resource-group weather-app-rg `
    --location eastus

# Store OpenAI key
az keyvault secret set `
    --vault-name weather-app-kv `
    --name openai-key `
    --value "your-key"

# Grant Container App access
az containerapp identity assign `
    --name weather-api `
    --resource-group weather-app-rg `
    --system-assigned
```

### 2. Enable HTTPS Only

Already enabled by default on Azure Container Apps and Static Web Apps.

### 3. Add Rate Limiting

Add to `backend/api_server.py`:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/chat")
@limiter.limit("10/minute")
async def chat_weather(request: Request, message: str):
    # Your code here
    pass
```

## Next Steps

1. ✅ Deploy backend and frontend to Azure
2. ✅ Test the integration
3. 🔜 Add Azure OpenAI for chat features
4. 🔜 Implement activity recommendations
5. 🔜 Add voice interface with Azure Speech
6. 🔜 Set up monitoring and alerts
7. 🔜 Configure custom domain

## Support

- **Azure Documentation**: https://docs.microsoft.com/azure
- **Container Apps**: https://docs.microsoft.com/azure/container-apps
- **Azure OpenAI**: https://docs.microsoft.com/azure/cognitive-services/openai

## 🎉 You're Ready!

Your weather app is now fully deployed on Azure and ready for LLM integration. Perfect for your hackathon presentation!

**Demo Flow**:
1. Show Azure Portal with deployed resources
2. Open frontend URL
3. Generate weather report
4. Show API docs
5. Demo chat feature (after LLM integration)
6. Explain scalability and future features

Good luck! 🚀
