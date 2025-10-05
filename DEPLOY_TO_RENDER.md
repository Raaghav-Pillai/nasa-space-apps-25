# Deploy Backend to Render.com (FREE)

## Quick Deploy (5 minutes)

1. **Go to Render.com**
   - Visit: https://render.com
   - Sign up with GitHub (free, no credit card)

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - OR use "Deploy from Git URL"

3. **Configure Service**
   - **Name**: weather-trip-api
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api_server:app --host 0.0.0.0 --port $PORT`
   - **Root Directory**: `backend`

4. **Add Environment Variable**
   - Key: `GEMINI_API_KEY`
   - Value: `AIzaSyCRIK6ZjYpwO7YknZIO-kCFOuiPQwxrKpw`

5. **Deploy**
   - Click "Create Web Service"
   - Wait 3-5 minutes
   - You'll get a URL like: `https://weather-trip-api.onrender.com`

6. **Update Frontend**
   - Edit `frontend_new/azure-api-config.js`
   - Change: `window.API_URL = 'https://weather-trip-api.onrender.com';`
   - Redeploy frontend to Azure

## Alternative: Railway.app (Also FREE)

1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repo
5. Add environment variable: `GEMINI_API_KEY`
6. Railway will auto-detect Python and deploy

## Alternative: Vercel (FREE)

1. Go to https://vercel.com
2. Import your GitHub repo
3. Configure as Python project
4. Add environment variable
5. Deploy

All three are FREE and don't require credit cards!
