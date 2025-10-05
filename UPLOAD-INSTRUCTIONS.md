# 📤 How to Upload Your Frontend Files

## Your Static Web App URL
**https://zealous-rock-0ff90f10f.2.azurestaticapps.net**

## Files to Upload
All files are ready in the `temp-deploy` folder:
- index.html
- inputForm.js
- azure-config.js
- README.md

## Method 1: Azure Portal (Recommended for Hackathon)

### Step-by-Step:

1. **Open Azure Portal**
   ```
   https://portal.azure.com
   ```

2. **Navigate to Your App**
   - Click the search bar at the top
   - Type: `nasa-weather-frontend`
   - Click on the result

3. **Go to Deployment**
   - In the left menu, find **"Deployment"**
   - Click **"Deployment Center"**

4. **Choose Deployment Method**
   - Select **"Local Git"** or **"External Git"**
   - Or use **"GitHub Actions"** if you have GitHub connected

5. **Alternative: Use the Browse Feature**
   - Click **"Overview"** in the left menu
   - Click the **URL** link: https://zealous-rock-0ff90f10f.2.azurestaticapps.net
   - This opens your current site

## Method 2: Using SWA CLI (Fastest)

### Install SWA CLI:
```powershell
npm install -g @azure/static-web-apps-cli
```

### Deploy:
```powershell
cd temp-deploy
swa deploy --deployment-token 9262c7e57a0cdef544de76c155fd93ef9430fc470f781edee18de3bfc52ba3c802-6694dd21-415a-4c84-90ac-2781880cfe8200f31180ff90f10f
```

## Method 3: GitHub Integration (Best for Continuous Deployment)

### Setup:
1. Push your code to GitHub
2. In Azure Portal → Static Web App → Deployment Center
3. Connect to your GitHub repository
4. Azure will automatically deploy on every push!

## Quick Test After Upload

Once uploaded, test your app:

1. **Visit**: https://zealous-rock-0ff90f10f.2.azurestaticapps.net
2. **Check**: You should see the "Chicago Event Planner" interface
3. **Test API**: Make sure the backend is running at http://localhost:8000

## Current Status

✅ **Backend API**: Running at http://localhost:8000
✅ **Azure Storage**: nasaweatherstorage3896
✅ **Static Web App**: nasa-weather-frontend
✅ **Frontend Files**: Ready in temp-deploy/

## Need Help?

If you see a blank page after upload:
1. Check browser console for errors (F12)
2. Make sure backend is running: http://localhost:8000/health
3. Check CORS settings in backend

## For Your Hackathon Demo

You can demo the app in two ways:
1. **Cloud**: https://zealous-rock-0ff90f10f.2.azurestaticapps.net (after upload)
2. **Local**: Open temp-deploy/index.html in browser (works with local backend)

Good luck! 🚀