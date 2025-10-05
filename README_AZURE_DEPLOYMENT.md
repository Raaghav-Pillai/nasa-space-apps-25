# 🌤️ NASA Weather Trip Planner - Azure Deployment

Complete deployment package for moving your weather trip planner to Azure, with LLM integration ready.

## 🎯 What This Package Does

Deploys your entire application to Azure:
- ✅ **Backend**: Azure Container Apps (auto-scaling, HTTPS)
- ✅ **Frontend**: Azure Static Web Apps (global CDN, free tier)
- ✅ **ML Models**: Containerized with Docker
- ✅ **LLM Ready**: Prepared for Azure OpenAI integration

## ⚡ Quick Start (5 Minutes)

```powershell
# 1. Check prerequisites
az --version          # Azure CLI
docker --version      # Docker Desktop
az login             # Login to Azure

# 2. Deploy everything
.\deploy_full_azure.ps1

# 3. Done! Your app is on Azure
```

## 📚 Documentation

### Start Here
- **[START_HERE.md](START_HERE.md)** - Complete getting started guide
- **[DEPLOYMENT_SUMMARY.txt](DEPLOYMENT_SUMMARY.txt)** - Visual overview

### Deployment Guides
- **[QUICK_DEPLOY_REFERENCE.md](QUICK_DEPLOY_REFERENCE.md)** - Quick commands and reference
- **[DEPLOY_TO_AZURE_COMPLETE.md](DEPLOY_TO_AZURE_COMPLETE.md)** - Full deployment documentation
- **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - Step-by-step checklist

### Advanced Topics
- **[AZURE_FULL_DEPLOYMENT.md](AZURE_FULL_DEPLOYMENT.md)** - LLM integration guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture details

## 🚀 Deployment Scripts

### Main Scripts
- `deploy_full_azure.ps1` - Deploy both backend and frontend
- `deploy_backend_azure.ps1` - Deploy backend only
- `update_frontend_api.ps1` - Update frontend with backend URL

### Usage

**Full Deployment** (Recommended):
```powershell
.\deploy_full_azure.ps1
```

**Backend Only**:
```powershell
.\deploy_backend_azure.ps1
```

**Update Frontend**:
```powershell
.\update_frontend_api.ps1 -ApiUrl "https://your-api-url"
```

## 📋 Prerequisites

### Required Software
1. **Azure CLI**: `winget install Microsoft.AzureCLI`
2. **Docker Desktop**: https://www.docker.com/products/docker-desktop
3. **Node.js & npm**: https://nodejs.org/
4. **SWA CLI**: `npm install -g @azure/static-web-apps-cli`

### Azure Account
- Sign up: https://azure.microsoft.com/free/
- Free tier includes:
  - $200 credit for 30 days
  - 12 months of free services
  - Always-free services

## 🏗️ What Gets Deployed

### Backend (Azure Container Apps)
```
Service: Azure Container Apps
URL: https://weather-api.{random}.eastus.azurecontainerapps.io
Features:
  - Auto-scaling (1-3 instances)
  - HTTPS with custom domain support
  - Built-in monitoring and logging
  - Environment variables for secrets
  - Health checks and auto-restart
Cost: ~$30-50/month
```

### Frontend (Azure Static Web Apps)
```
Service: Azure Static Web Apps
URL: https://orange-coast-0614e430f.2.azurestaticapps.net
Features:
  - Global CDN (fast worldwide)
  - Automatic HTTPS
  - Custom domain support
  - GitHub Actions integration
Cost: Free tier
```

## 🤖 LLM Integration (Optional)

After deployment, add Azure OpenAI for chat features:

```powershell
# 1. Create Azure OpenAI resource
az cognitiveservices account create \
    --name weather-openai \
    --resource-group weather-app-rg \
    --kind OpenAI \
    --sku S0 \
    --location eastus

# 2. Deploy GPT-4 model
az cognitiveservices account deployment create \
    --name weather-openai \
    --resource-group weather-app-rg \
    --deployment-name gpt-4 \
    --model-name gpt-4 \
    --model-version "0613"

# 3. Get API key
az cognitiveservices account keys list \
    --name weather-openai \
    --resource-group weather-app-rg
```

See [DEPLOY_TO_AZURE_COMPLETE.md](DEPLOY_TO_AZURE_COMPLETE.md) for detailed LLM integration steps.

## 💰 Cost Estimates

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

## 📊 Architecture

```
User Browser
    ↓
Azure Static Web Apps (Frontend)
    ↓ HTTPS API calls
Azure Container Apps (Backend)
    ↓ ML Predictions
Trained Models (Temperature, Precipitation, etc.)
    ↓ (Future)
Azure OpenAI (Chat & Recommendations)
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture diagrams.

## 🔍 Monitoring

### View Backend Logs
```powershell
az containerapp logs show \
    --name weather-api \
    --resource-group weather-app-rg \
    --follow
```

### Check Backend Health
```powershell
curl https://your-api-url/health
```

### View in Azure Portal
```powershell
Start-Process "https://portal.azure.com"
# Navigate to: Resource Groups → weather-app-rg
```

## 🐛 Troubleshooting

### Backend Deployment Fails
- Ensure Docker Desktop is running
- Verify Azure login: `az account show`
- Check error messages in output
- Try building Docker image locally first

### Frontend Can't Reach Backend
- Verify `frontend_new/azure-api-config.js` has correct URL
- Check CORS settings in `backend/api_server.py`
- Test backend directly: `curl https://your-api-url/health`
- Check browser console for errors

### Out of Memory
```powershell
az containerapp update \
    --name weather-api \
    --resource-group weather-app-rg \
    --memory 4.0Gi
```

See [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) for complete troubleshooting guide.

## 🎉 For Hackathon Demo

### Demo Flow
1. Show Azure Portal with deployed resources
2. Open frontend URL
3. Generate weather report
4. Show weather avatar changing clothes
5. Explain suitability scoring
6. Show API documentation
7. Demo chat feature (if LLM added)
8. Explain scalability

### Key Talking Points
- ✅ NASA MODIS satellite data
- ✅ 1.72°F prediction accuracy
- ✅ Cloud-native architecture
- ✅ Auto-scaling backend
- ✅ Global CDN frontend
- ✅ Ready for AI integration

## 📁 Project Structure

```
weather-trip-planner/
├── Documentation/
│   ├── START_HERE.md
│   ├── DEPLOYMENT_SUMMARY.txt
│   ├── DEPLOYMENT_CHECKLIST.md
│   ├── QUICK_DEPLOY_REFERENCE.md
│   ├── DEPLOY_TO_AZURE_COMPLETE.md
│   ├── AZURE_FULL_DEPLOYMENT.md
│   └── ARCHITECTURE.md
│
├── Deployment Scripts/
│   ├── deploy_full_azure.ps1
│   ├── deploy_backend_azure.ps1
│   └── update_frontend_api.ps1
│
├── backend/
│   ├── api_server.py
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── requirements.txt
│   └── prediction/
│       ├── predict_simple.py
│       └── temperature/
│
└── frontend_new/
    ├── index.html
    ├── app.js
    ├── styles.css
    └── azure-api-config.js
```

## 🔒 Security

- ✅ HTTPS enforced on all services
- ✅ CORS properly configured
- ✅ Environment variables for secrets
- ✅ Azure Key Vault integration available
- ✅ Managed identities supported

## 🚀 Next Steps

1. **Deploy to Azure**: Run `.\deploy_full_azure.ps1`
2. **Test Integration**: Verify frontend can reach backend
3. **Add LLM**: Follow Azure OpenAI setup guide
4. **Custom Domain**: Configure custom domain (optional)
5. **Monitoring**: Set up Application Insights
6. **CI/CD**: Configure GitHub Actions (optional)

## 📞 Support

- **Azure Documentation**: https://docs.microsoft.com/azure
- **Container Apps**: https://docs.microsoft.com/azure/container-apps
- **Static Web Apps**: https://docs.microsoft.com/azure/static-web-apps
- **Azure OpenAI**: https://docs.microsoft.com/azure/cognitive-services/openai

## 🎯 Success Criteria

- [ ] Backend deployed and accessible
- [ ] Frontend deployed and accessible
- [ ] Frontend successfully calls backend
- [ ] Weather predictions work correctly
- [ ] All UI features functional
- [ ] No errors in logs
- [ ] Ready for demo

## 🧹 Cleanup

To remove all Azure resources after the hackathon:

```powershell
az group delete --name weather-app-rg --yes
```

This will delete:
- Container Apps
- Container Registry
- Container Apps Environment
- All associated resources

**Note**: Static Web App is separate and won't be deleted.

## 📝 License

This deployment package is part of the NASA Weather Trip Planner project.

## 🌟 Credits

- **ML Models**: Trained on NASA MODIS satellite data
- **Weather Data**: MODIS Terra/Aqua satellites
- **Cloud Platform**: Microsoft Azure
- **AI Integration**: Azure OpenAI (optional)

---

## ⚡ TL;DR

```powershell
# Install prerequisites
winget install Microsoft.AzureCLI
# Install Docker Desktop from docker.com
npm install -g @azure/static-web-apps-cli

# Login to Azure
az login

# Deploy everything
.\deploy_full_azure.ps1

# Done! 🎉
```

Your weather app will be fully deployed to Azure in ~15 minutes.

Good luck with your hackathon! 🚀
