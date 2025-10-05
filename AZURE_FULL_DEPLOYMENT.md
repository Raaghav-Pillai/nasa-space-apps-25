# 🚀 Complete Azure Deployment Guide

## Overview
This guide deploys both frontend and backend to Azure, preparing your app for LLM integration.

## Architecture
```
Frontend (Azure Static Web Apps)
    ↓ HTTPS
Backend (Azure Container Apps)
    ↓ Future: Azure OpenAI
LLM Integration (Coming Soon)
```

## Prerequisites

1. **Azure CLI** installed
   ```powershell
   winget install Microsoft.AzureCLI
   ```

2. **Docker Desktop** installed and running
   - Download from: https://www.docker.com/products/docker-desktop

3. **Azure Static Web Apps CLI**
   ```powershell
   npm install -g @azure/static-web-apps-cli
   ```

4. **Azure Account**
   - Sign up at: https://azure.microsoft.com/free/

## Step 1: Deploy Backend to Azure Container Apps

```powershell
# Login to Azure
az login

# Run deployment script
.\deploy_backend_azure.ps1
```

This will:
- ✅ Create Azure Container Registry
- ✅ Build Docker image with your ML models
- ✅ Deploy to Azure Container Apps
- ✅ Auto-scale (1-3 instances)
- ✅ Give you a public HTTPS URL

**Time**: ~10-15 minutes

## Step 2: Update Frontend with Backend URL

After backend deployment completes, you'll get an API URL like:
`https://weather-api.something.eastus.azurecontainerapps.io`

Update frontend:
```powershell
.\update_frontend_api.ps1 -ApiUrl "https://YOUR-API-URL"
```

## Step 3: Redeploy Frontend

```powershell
cd frontend_new
swa deploy . --env production
```

## Step 4: Test Integration

Visit your frontend URL and test:
- ✅ Location selection
- ✅ Activity profile
- ✅ Date range prediction
- ✅ Weather avatar
- ✅ Score calculation

## 🤖 Future: LLM Integration

Your backend is now ready for LLM integration. Here's how you'll add it:

### Option 1: Azure OpenAI (Recommended)

```python
# Add to backend/api_server.py
from openai import AzureOpenAI

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-02-01",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

@app.post("/chat")
async def chat_weather(message: str):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a weather expert assistant."},
            {"role": "user", "content": message}
        ]
    )
    return {"response": response.choices[0].message.content}
```

### Option 2: Hugging Face Models

```python
from transformers import pipeline

# Load model once at startup
llm = pipeline("text-generation", model="meta-llama/Llama-2-7b-chat-hf")

@app.post("/chat")
async def chat_weather(message: str):
    response = llm(message, max_length=200)
    return {"response": response[0]["generated_text"]}
```

### Update Container App with Environment Variables

```powershell
az containerapp update `
    --name weather-api `
    --resource-group weather-app-rg `
    --set-env-vars `
        AZURE_OPENAI_KEY=your-key `
        AZURE_OPENAI_ENDPOINT=your-endpoint
```

## 📊 Monitoring & Scaling

### View Logs
```powershell
az containerapp logs show `
    --name weather-api `
    --resource-group weather-app-rg `
    --follow
```

### Scale Up for LLM
```powershell
az containerapp update `
    --name weather-api `
    --resource-group weather-app-rg `
    --cpu 2.0 `
    --memory 4.0Gi `
    --min-replicas 1 `
    --max-replicas 5
```

### Enable Application Insights
```powershell
az containerapp update `
    --name weather-api `
    --resource-group weather-app-rg `
    --enable-app-insights
```

## 💰 Cost Estimates

### Current Setup (No LLM)
- **Container Apps**: ~$30-50/month (1-3 instances)
- **Container Registry**: ~$5/month (Basic tier)
- **Static Web Apps**: Free tier
- **Total**: ~$35-55/month

### With Azure OpenAI
- **GPT-4**: ~$0.03 per 1K tokens
- **GPT-3.5-turbo**: ~$0.002 per 1K tokens
- Estimate: $50-200/month depending on usage

### With Self-Hosted LLM
- **Container Apps**: ~$100-200/month (larger instances)
- **Storage**: ~$10/month
- **Total**: ~$110-210/month

## 🔒 Security Best Practices

1. **API Keys**: Use Azure Key Vault
   ```powershell
   az keyvault create --name weather-app-kv --resource-group weather-app-rg
   az keyvault secret set --vault-name weather-app-kv --name openai-key --value "your-key"
   ```

2. **CORS**: Already configured in backend
3. **HTTPS**: Automatic with Azure
4. **Rate Limiting**: Add to backend for LLM endpoints

## 🎯 URLs After Deployment

- **Frontend**: https://orange-coast-0614e430f.2.azurestaticapps.net
- **Backend API**: https://weather-api.{random}.eastus.azurecontainerapps.io
- **API Docs**: https://weather-api.{random}.eastus.azurecontainerapps.io/docs
- **Health Check**: https://weather-api.{random}.eastus.azurecontainerapps.io/health

## 🐛 Troubleshooting

### Backend not responding
```powershell
# Check logs
az containerapp logs show --name weather-api --resource-group weather-app-rg --follow

# Restart app
az containerapp revision restart --name weather-api --resource-group weather-app-rg
```

### Frontend can't reach backend
1. Check CORS settings in `backend/api_server.py`
2. Verify API URL in `frontend_new/app.js`
3. Check browser console for errors

### Docker build fails
1. Ensure Docker Desktop is running
2. Check `backend/requirements.txt` for version conflicts
3. Try building locally first: `docker build -t test ./backend`

## 📚 Next Steps

1. ✅ Deploy backend to Azure
2. ✅ Update frontend with backend URL
3. ✅ Test full integration
4. 🔜 Add Azure OpenAI for chat features
5. 🔜 Implement weather recommendations with LLM
6. 🔜 Add voice interface with Azure Speech

## 🎉 Benefits of This Setup

- ✅ **Scalable**: Auto-scales based on traffic
- ✅ **Global**: CDN for frontend, multi-region backend
- ✅ **Secure**: HTTPS, managed identities, Key Vault
- ✅ **LLM-Ready**: Easy to add Azure OpenAI or custom models
- ✅ **Cost-Effective**: Pay only for what you use
- ✅ **Production-Ready**: Monitoring, logging, auto-restart

Your app is now enterprise-grade and ready for the hackathon! 🚀
