# ⚡ Quick Deploy Reference

## 🚀 Deploy Everything (One Command)

```powershell
.\deploy_full_azure.ps1
```

**Time**: ~15 minutes  
**Result**: Backend + Frontend fully on Azure

---

## 📋 Prerequisites Checklist

- [ ] Azure CLI installed: `winget install Microsoft.AzureCLI`
- [ ] Docker Desktop installed and running
- [ ] Logged into Azure: `az login`
- [ ] SWA CLI: `npm install -g @azure/static-web-apps-cli`

---

## 🎯 What You Get

### Backend
- **Service**: Azure Container Apps
- **URL**: `https://weather-api.{random}.eastus.azurecontainerapps.io`
- **Features**: Auto-scaling, HTTPS, monitoring
- **Cost**: ~$30-50/month

### Frontend
- **Service**: Azure Static Web Apps
- **URL**: `https://orange-coast-0614e430f.2.azurestaticapps.net`
- **Features**: Global CDN, HTTPS, free tier
- **Cost**: Free

---

## 🤖 Add LLM (After Deployment)

### Quick Azure OpenAI Setup

```powershell
# 1. Create OpenAI resource
az cognitiveservices account create `
    --name weather-openai `
    --resource-group weather-app-rg `
    --kind OpenAI `
    --sku S0 `
    --location eastus

# 2. Deploy GPT-4
az cognitiveservices account deployment create `
    --name weather-openai `
    --resource-group weather-app-rg `
    --deployment-name gpt-4 `
    --model-name gpt-4 `
    --model-version "0613"

# 3. Get credentials
az cognitiveservices account keys list `
    --name weather-openai `
    --resource-group weather-app-rg

# 4. Update backend with keys
az containerapp update `
    --name weather-api `
    --resource-group weather-app-rg `
    --set-env-vars `
        AZURE_OPENAI_KEY=your-key `
        AZURE_OPENAI_ENDPOINT=your-endpoint
```

### Add Chat Endpoint

Add to `backend/api_server.py`:

```python
from openai import AzureOpenAI

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-02-01",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

@app.post("/chat")
async def chat(message: str):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a weather expert."},
            {"role": "user", "content": message}
        ]
    )
    return {"response": response.choices[0].message.content}
```

Then redeploy: `.\deploy_backend_azure.ps1`

---

## 🔍 Useful Commands

### View Backend Logs
```powershell
az containerapp logs show --name weather-api --resource-group weather-app-rg --follow
```

### Restart Backend
```powershell
az containerapp revision restart --name weather-api --resource-group weather-app-rg
```

### Test Backend Health
```powershell
curl https://your-api-url/health
```

### View API Docs
```powershell
Start-Process https://your-api-url/docs
```

### Scale Backend
```powershell
az containerapp update `
    --name weather-api `
    --resource-group weather-app-rg `
    --min-replicas 2 `
    --max-replicas 10
```

---

## 🐛 Quick Fixes

### Backend not responding?
```powershell
az containerapp logs show --name weather-api --resource-group weather-app-rg --follow
```

### Frontend can't reach backend?
1. Check `frontend_new/azure-api-config.js`
2. Verify CORS in `backend/api_server.py`
3. Test: `curl https://your-api-url/health`

### Docker build fails?
```powershell
cd backend
docker build -t test .
```

### Need to update frontend?
```powershell
cd frontend_new
swa deploy . --env production
```

---

## 💰 Cost Summary

| Service | Monthly Cost |
|---------|-------------|
| Container Apps (backend) | $30-50 |
| Container Registry | $5 |
| Static Web Apps (frontend) | Free |
| **Total (no LLM)** | **$35-55** |
| + Azure OpenAI (GPT-4) | +$50-200 |
| **Total (with LLM)** | **$85-255** |

---

## 📱 Your URLs

After deployment, find your URLs in:
- `backend-deployment-config.json` (backend URL)
- Frontend: `https://orange-coast-0614e430f.2.azurestaticapps.net`

---

## 🎯 For Hackathon Demo

1. **Show Azure Portal**: Resources deployed
2. **Open Frontend**: Live weather predictions
3. **Generate Report**: Weather avatar + scoring
4. **Show API Docs**: `/docs` endpoint
5. **Demo Chat**: (if LLM added)
6. **Explain Scale**: Auto-scaling, global CDN

---

## 📚 Full Guides

- **Complete Deployment**: `DEPLOY_TO_AZURE_COMPLETE.md`
- **LLM Integration**: `AZURE_FULL_DEPLOYMENT.md`
- **Architecture**: `FINAL_DEPLOYMENT_SUMMARY.md`

---

## ⚡ TL;DR

```powershell
# Deploy everything
.\deploy_full_azure.ps1

# Add LLM later
# See DEPLOY_TO_AZURE_COMPLETE.md

# Done! 🎉
```
