# 🎯 START HERE - Complete Azure Deployment

## What You're Deploying

A **NASA Weather Trip Planner** with:
- ✅ ML-powered weather predictions (1.72°F accuracy)
- ✅ Beautiful UI with weather avatar
- ✅ Activity suitability scoring
- ✅ Ready for LLM integration (Azure OpenAI)

## Current Status

### ✅ Already Deployed
- **Frontend**: https://orange-coast-0614e430f.2.azurestaticapps.net
  - Running on Azure Static Web Apps
  - Connected to local backend

### 🔄 Need to Deploy
- **Backend**: Currently running locally
  - Need to move to Azure Container Apps
  - Will enable LLM integration

---

## 🚀 Deploy to Azure (15 Minutes)

### Step 1: Check Prerequisites

```powershell
# Check Azure CLI
az --version

# Check Docker
docker --version

# Login to Azure
az login
```

**Don't have these?** See [Prerequisites](#prerequisites) below.

### Step 2: Deploy Everything

```powershell
.\deploy_full_azure.ps1
```

This will:
1. Build Docker image with your ML models
2. Deploy backend to Azure Container Apps
3. Update frontend with new backend URL
4. Redeploy frontend

**Time**: ~15 minutes  
**Cost**: ~$35-55/month

### Step 3: Test Your App

After deployment completes, you'll get URLs like:

```
Frontend: https://orange-coast-0614e430f.2.azurestaticapps.net
Backend: https://weather-api.{random}.eastus.azurecontainerapps.io
API Docs: https://weather-api.{random}.eastus.azurecontainerapps.io/docs
```

Open the frontend and test:
1. Select location (Chicago)
2. Choose activity (Beach Day)
3. Pick dates (next week)
4. Generate report
5. See weather avatar and scores

---

## 🤖 Add LLM Integration (Optional, 10 Minutes)

After backend is deployed, add Azure OpenAI:

```powershell
# 1. Create Azure OpenAI resource
az cognitiveservices account create `
    --name weather-openai `
    --resource-group weather-app-rg `
    --kind OpenAI `
    --sku S0 `
    --location eastus

# 2. Deploy GPT-4 model
az cognitiveservices account deployment create `
    --name weather-openai `
    --resource-group weather-app-rg `
    --deployment-name gpt-4 `
    --model-name gpt-4 `
    --model-version "0613"

# 3. Get API key
az cognitiveservices account keys list `
    --name weather-openai `
    --resource-group weather-app-rg
```

Then add chat endpoint to your backend (see `DEPLOY_TO_AZURE_COMPLETE.md` for code).

**Cost**: +$50-200/month depending on usage

---

## Prerequisites

### 1. Azure CLI

**Windows**:
```powershell
winget install Microsoft.AzureCLI
```

**Mac**:
```bash
brew install azure-cli
```

**Linux**:
```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

### 2. Docker Desktop

Download from: https://www.docker.com/products/docker-desktop

**Important**: Make sure Docker Desktop is running before deployment!

### 3. Azure Account

Sign up for free: https://azure.microsoft.com/free/

You get:
- $200 credit for 30 days
- 12 months of free services
- Always-free services

### 4. Node.js & npm (for SWA CLI)

Download from: https://nodejs.org/

Then install SWA CLI:
```powershell
npm install -g @azure/static-web-apps-cli
```

---

## 📁 Project Structure

```
weather-trip-planner/
├── backend/
│   ├── api_server.py          # FastAPI server
│   ├── Dockerfile             # Docker configuration
│   ├── requirements.txt       # Python dependencies
│   └── prediction/
│       ├── predict_simple.py  # ML prediction logic
│       └── temperature/       # Trained models
├── frontend_new/
│   ├── index.html            # Main UI
│   ├── app.js                # Frontend logic
│   ├── styles.css            # Styling
│   └── azure-api-config.js   # API URL config
├── deploy_full_azure.ps1     # ⭐ Main deployment script
├── deploy_backend_azure.ps1  # Backend-only deployment
└── update_frontend_api.ps1   # Update frontend config
```

---

## 🎯 Deployment Options

### Option 1: Full Deployment (Recommended)
```powershell
.\deploy_full_azure.ps1
```
Deploys both backend and frontend.

### Option 2: Backend Only
```powershell
.\deploy_backend_azure.ps1
```
Just deploy the backend API.

### Option 3: Update Frontend Only
```powershell
.\update_frontend_api.ps1
cd frontend_new
swa deploy . --env production
```
Update frontend with new backend URL.

---

## 📊 What Gets Deployed

### Backend (Azure Container Apps)

**Features**:
- Auto-scaling (1-3 instances)
- HTTPS with custom domain support
- Built-in monitoring and logging
- Environment variables for secrets
- Health checks and auto-restart

**Includes**:
- FastAPI server
- ML models (temperature, precipitation, etc.)
- Elasticsearch integration (optional)
- Ready for LLM endpoints

**Cost**: ~$30-50/month

### Frontend (Azure Static Web Apps)

**Features**:
- Global CDN (fast worldwide)
- Automatic HTTPS
- Custom domain support
- GitHub Actions integration
- Free tier available

**Includes**:
- Weather trip planner UI
- Weather avatar with dynamic clothing
- Activity suitability scoring
- Stacked bar chart visualization

**Cost**: Free tier

---

## 🔍 Monitoring & Management

### View Backend Logs
```powershell
az containerapp logs show `
    --name weather-api `
    --resource-group weather-app-rg `
    --follow
```

### Check Backend Health
```powershell
# Get your API URL
$config = Get-Content backend-deployment-config.json | ConvertFrom-Json
$apiUrl = $config.apiUrl

# Test health endpoint
curl "$apiUrl/health"
```

### View in Azure Portal
```powershell
Start-Process "https://portal.azure.com"
```

Navigate to: Resource Groups → weather-app-rg

### Restart Backend
```powershell
az containerapp revision restart `
    --name weather-api `
    --resource-group weather-app-rg
```

---

## 💰 Cost Breakdown

### Without LLM
| Service | Cost/Month |
|---------|-----------|
| Azure Container Apps | $30-50 |
| Azure Container Registry | $5 |
| Azure Static Web Apps | Free |
| **Total** | **$35-55** |

### With Azure OpenAI
| Service | Cost/Month |
|---------|-----------|
| Base infrastructure | $35-55 |
| Azure OpenAI (GPT-4) | $50-200 |
| **Total** | **$85-255** |

**Note**: Costs depend on usage. Free tier credits apply for new accounts.

---

## 🐛 Troubleshooting

### "Docker not found"
Make sure Docker Desktop is installed and running.

### "az command not found"
Install Azure CLI (see Prerequisites).

### Backend deployment fails
```powershell
# Check Docker is running
docker ps

# Check Azure login
az account show

# View detailed logs
az containerapp logs show --name weather-api --resource-group weather-app-rg
```

### Frontend can't reach backend
1. Check `frontend_new/azure-api-config.js` has correct URL
2. Test backend: `curl https://your-api-url/health`
3. Check browser console for CORS errors

### Out of memory
```powershell
# Increase memory
az containerapp update `
    --name weather-api `
    --resource-group weather-app-rg `
    --memory 4.0Gi
```

---

## 📚 Documentation

- **Quick Reference**: `QUICK_DEPLOY_REFERENCE.md`
- **Complete Guide**: `DEPLOY_TO_AZURE_COMPLETE.md`
- **LLM Integration**: `AZURE_FULL_DEPLOYMENT.md`
- **Architecture**: `FINAL_DEPLOYMENT_SUMMARY.md`

---

## 🎉 For Your Hackathon

### Demo Flow

1. **Show Azure Portal**
   - Navigate to Resource Groups → weather-app-rg
   - Show Container Apps, Container Registry, Static Web Apps

2. **Open Frontend**
   - https://orange-coast-0614e430f.2.azurestaticapps.net
   - Show responsive design

3. **Generate Weather Report**
   - Select Chicago
   - Choose "Beach Day" profile
   - Pick next week
   - Show weather avatar changing clothes
   - Explain suitability scoring

4. **Show API Documentation**
   - Open `/docs` endpoint
   - Show available endpoints
   - Test prediction API

5. **Explain Architecture**
   - Frontend: Azure Static Web Apps (global CDN)
   - Backend: Azure Container Apps (auto-scaling)
   - ML Models: Trained on NASA MODIS data
   - Future: Azure OpenAI integration

6. **Highlight Features**
   - 1.72°F prediction accuracy
   - Real-time weather predictions
   - Activity suitability algorithm
   - Scalable cloud architecture
   - Ready for LLM chat features

### Key Talking Points

- ✅ **NASA Data**: Trained on MODIS satellite imagery
- ✅ **ML Accuracy**: 1.72°F MAE, 98.68% R²
- ✅ **Cloud Native**: Fully deployed on Azure
- ✅ **Scalable**: Auto-scales based on demand
- ✅ **AI-Ready**: Prepared for LLM integration
- ✅ **Production**: HTTPS, monitoring, logging

---

## 🚀 Next Steps

1. ✅ Deploy to Azure: `.\deploy_full_azure.ps1`
2. ✅ Test the integration
3. 🔜 Add Azure OpenAI for chat
4. 🔜 Implement voice interface
5. 🔜 Add custom domain
6. 🔜 Set up monitoring alerts

---

## ⚡ Quick Commands

```powershell
# Deploy everything
.\deploy_full_azure.ps1

# View logs
az containerapp logs show --name weather-api --resource-group weather-app-rg --follow

# Restart backend
az containerapp revision restart --name weather-api --resource-group weather-app-rg

# Test health
curl https://your-api-url/health

# Update frontend
cd frontend_new
swa deploy . --env production
```

---

## 🎯 Ready to Deploy?

```powershell
# Make sure you're in the project root
cd path\to\weather-trip-planner

# Run the deployment
.\deploy_full_azure.ps1
```

**That's it!** Your app will be fully deployed to Azure in ~15 minutes.

Good luck with your hackathon! 🌟
