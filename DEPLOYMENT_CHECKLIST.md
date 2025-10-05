# ✅ Azure Deployment Checklist

## Pre-Deployment

### Prerequisites
- [ ] Azure CLI installed (`az --version`)
- [ ] Docker Desktop installed and running (`docker --version`)
- [ ] Node.js and npm installed (`node --version`)
- [ ] Azure account created (https://azure.microsoft.com/free/)
- [ ] Logged into Azure (`az login`)
- [ ] SWA CLI installed (`npm install -g @azure/static-web-apps-cli`)

### Verify Project Files
- [ ] `backend/api_server.py` exists
- [ ] `backend/Dockerfile` exists
- [ ] `backend/requirements.txt` exists
- [ ] `backend/prediction/predict_simple.py` exists
- [ ] `backend/prediction/temperature/` folder has model files
- [ ] `frontend_new/index.html` exists
- [ ] `frontend_new/app.js` exists
- [ ] `frontend_new/azure-api-config.js` exists
- [ ] `deploy_full_azure.ps1` exists

## Deployment Steps

### Step 1: Backend Deployment
- [ ] Open PowerShell in project root
- [ ] Ensure Docker Desktop is running
- [ ] Run: `.\deploy_backend_azure.ps1`
- [ ] Wait for completion (~10-15 minutes)
- [ ] Note the API URL from output
- [ ] Verify `backend-deployment-config.json` was created
- [ ] Test backend health: `curl https://your-api-url/health`
- [ ] Check API docs: Open `https://your-api-url/docs` in browser

### Step 2: Frontend Update
- [ ] Run: `.\update_frontend_api.ps1`
- [ ] Verify `frontend_new/azure-api-config.js` has correct API URL
- [ ] Test locally: Open `frontend_new/index.html` in browser
- [ ] Verify frontend can reach backend

### Step 3: Frontend Deployment
- [ ] Navigate to frontend: `cd frontend_new`
- [ ] Deploy: `swa deploy . --env production`
- [ ] Wait for completion (~2-5 minutes)
- [ ] Note the frontend URL
- [ ] Return to root: `cd ..`

## Post-Deployment Testing

### Backend Tests
- [ ] Health check: `curl https://your-api-url/health`
- [ ] API docs accessible: `https://your-api-url/docs`
- [ ] Test prediction endpoint in API docs
- [ ] Check logs: `az containerapp logs show --name weather-api --resource-group weather-app-rg`

### Frontend Tests
- [ ] Open frontend URL in browser
- [ ] Test location selection (Chicago)
- [ ] Test activity profile selection (Beach Day)
- [ ] Test date range selection
- [ ] Generate weather report
- [ ] Verify weather avatar displays
- [ ] Verify score calculation works
- [ ] Check browser console for errors
- [ ] Test on mobile device

### Integration Tests
- [ ] Frontend successfully calls backend API
- [ ] Weather predictions display correctly
- [ ] No CORS errors in browser console
- [ ] All weather parameters show data
- [ ] Charts render properly

## Optional: LLM Integration

### Azure OpenAI Setup
- [ ] Create Azure OpenAI resource
- [ ] Deploy GPT-4 model
- [ ] Get API key and endpoint
- [ ] Update backend code with chat endpoint
- [ ] Add `openai` to `requirements.txt`
- [ ] Update container app with environment variables
- [ ] Redeploy backend
- [ ] Test chat endpoint

### Frontend LLM Integration
- [ ] Add chat UI to frontend
- [ ] Add chat JavaScript functions
- [ ] Test chat functionality
- [ ] Verify responses are relevant

## Monitoring Setup

### Azure Portal
- [ ] Login to Azure Portal (https://portal.azure.com)
- [ ] Navigate to Resource Group: `weather-app-rg`
- [ ] Verify all resources are running
- [ ] Check Container App metrics
- [ ] Review Static Web App analytics

### Application Insights (Optional)
- [ ] Enable Application Insights on Container App
- [ ] Configure alerts for high CPU/memory
- [ ] Set up availability tests
- [ ] Configure log analytics

## Documentation

### Update Documentation
- [ ] Document your API URL
- [ ] Document your frontend URL
- [ ] Update README with deployment info
- [ ] Document any custom configurations
- [ ] Note any issues encountered

### Save Configuration
- [ ] Save `backend-deployment-config.json`
- [ ] Document Azure resource names
- [ ] Save API keys securely (use Azure Key Vault)
- [ ] Document environment variables

## Hackathon Preparation

### Demo Preparation
- [ ] Test complete user flow
- [ ] Prepare demo script
- [ ] Take screenshots of Azure Portal
- [ ] Prepare architecture diagram
- [ ] Test on different devices/browsers
- [ ] Prepare backup plan (local version)

### Presentation Materials
- [ ] Highlight NASA MODIS data usage
- [ ] Emphasize ML accuracy (1.72°F)
- [ ] Show Azure cloud architecture
- [ ] Demonstrate scalability features
- [ ] Explain LLM integration readiness
- [ ] Prepare cost analysis slide

### Demo Flow
- [ ] Show Azure Portal resources
- [ ] Open frontend URL
- [ ] Select location
- [ ] Choose activity profile
- [ ] Generate weather report
- [ ] Show weather avatar
- [ ] Explain scoring algorithm
- [ ] Show API documentation
- [ ] Demo chat feature (if LLM added)
- [ ] Explain future enhancements

## Troubleshooting Checklist

### If Backend Deployment Fails
- [ ] Check Docker is running
- [ ] Verify Azure login: `az account show`
- [ ] Check Azure subscription has quota
- [ ] Review error messages
- [ ] Check `backend/Dockerfile` syntax
- [ ] Verify `requirements.txt` has no conflicts
- [ ] Try building Docker image locally first

### If Frontend Can't Reach Backend
- [ ] Verify `azure-api-config.js` has correct URL
- [ ] Check CORS settings in `api_server.py`
- [ ] Test backend directly with curl
- [ ] Check browser console for errors
- [ ] Verify backend is running in Azure Portal
- [ ] Check network tab in browser dev tools

### If Predictions Don't Work
- [ ] Verify model files exist in backend
- [ ] Check backend logs for errors
- [ ] Test prediction endpoint in API docs
- [ ] Verify date format is correct
- [ ] Check for missing dependencies

## Cost Management

### Monitor Costs
- [ ] Set up Azure cost alerts
- [ ] Review daily spending
- [ ] Check resource utilization
- [ ] Optimize instance sizes if needed
- [ ] Use free tier where possible

### Cost Optimization
- [ ] Scale down when not in use
- [ ] Use spot instances for dev/test
- [ ] Delete unused resources
- [ ] Use Azure Cost Management tools

## Security Checklist

### Backend Security
- [ ] HTTPS enabled (automatic)
- [ ] CORS properly configured
- [ ] API keys in environment variables
- [ ] Use Azure Key Vault for secrets
- [ ] Enable authentication (if needed)
- [ ] Set up rate limiting

### Frontend Security
- [ ] HTTPS enabled (automatic)
- [ ] No sensitive data in client code
- [ ] API keys not exposed
- [ ] Content Security Policy configured

## Cleanup (After Hackathon)

### If Keeping the App
- [ ] Set up custom domain
- [ ] Configure production monitoring
- [ ] Set up automated backups
- [ ] Configure auto-scaling rules
- [ ] Set up CI/CD pipeline

### If Removing the App
- [ ] Delete resource group: `az group delete --name weather-app-rg`
- [ ] Verify all resources deleted
- [ ] Check for any remaining costs
- [ ] Remove local configuration files

## Success Criteria

- [ ] ✅ Backend deployed and accessible
- [ ] ✅ Frontend deployed and accessible
- [ ] ✅ Frontend successfully calls backend
- [ ] ✅ Weather predictions work correctly
- [ ] ✅ All UI features functional
- [ ] ✅ No errors in logs
- [ ] ✅ Performance is acceptable
- [ ] ✅ Ready for demo

## Notes

**Deployment Date**: _______________

**Backend URL**: _______________________________________________

**Frontend URL**: _______________________________________________

**Resource Group**: weather-app-rg

**Issues Encountered**: 
_______________________________________________________________
_______________________________________________________________
_______________________________________________________________

**Solutions Applied**:
_______________________________________________________________
_______________________________________________________________
_______________________________________________________________

**Additional Notes**:
_______________________________________________________________
_______________________________________________________________
_______________________________________________________________

---

## Quick Reference

**Deploy Everything**: `.\deploy_full_azure.ps1`

**View Logs**: `az containerapp logs show --name weather-api --resource-group weather-app-rg --follow`

**Restart Backend**: `az containerapp revision restart --name weather-api --resource-group weather-app-rg`

**Test Health**: `curl https://your-api-url/health`

**Delete Everything**: `az group delete --name weather-app-rg`

---

Good luck with your deployment! 🚀
