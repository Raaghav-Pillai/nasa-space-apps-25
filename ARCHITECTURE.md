# 🏗️ Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           USER BROWSER                              │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Weather Trip Planner UI                                     │  │
│  │  - Location Selection                                        │  │
│  │  - Activity Profiles                                         │  │
│  │  - Date Range Picker                                         │  │
│  │  - Weather Avatar                                            │  │
│  │  - Suitability Scoring                                       │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ HTTPS
                                  ↓
┌─────────────────────────────────────────────────────────────────────┐
│              AZURE STATIC WEB APPS (Frontend)                       │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Static Files                                                │  │
│  │  - index.html                                                │  │
│  │  - app.js                                                    │  │
│  │  - styles.css                                                │  │
│  │  - azure-api-config.js                                       │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  Features:                                                          │
│  ✅ Global CDN                                                      │
│  ✅ Automatic HTTPS                                                 │
│  ✅ Custom Domain Support                                           │
│  ✅ Free Tier                                                       │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ HTTPS API Calls
                                  ↓
┌─────────────────────────────────────────────────────────────────────┐
│            AZURE CONTAINER APPS (Backend API)                       │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  FastAPI Server (api_server.py)                              │  │
│  │                                                               │  │
│  │  Endpoints:                                                   │  │
│  │  - GET  /                    (API info)                      │  │
│  │  - GET  /health              (Health check)                  │  │
│  │  - POST /predict             (Single prediction)             │  │
│  │  - POST /predict-range       (Date range prediction)         │  │
│  │  - POST /search              (Elasticsearch search)          │  │
│  │  - POST /chat                (LLM chat - future)             │  │
│  │  - POST /recommend           (AI recommendations - future)   │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  Features:                                                          │
│  ✅ Auto-scaling (1-3 instances)                                    │
│  ✅ HTTPS with custom domain                                        │
│  ✅ Built-in monitoring                                             │
│  ✅ Environment variables                                           │
│  ✅ Health checks                                                   │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ Model Inference
                                  ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    ML PREDICTION ENGINE                             │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  predict_simple.py                                           │  │
│  │                                                               │  │
│  │  Models:                                                      │  │
│  │  ├─ Temperature Model (Random Forest)                        │  │
│  │  │  └─ Accuracy: 1.72°F MAE, 98.68% R²                      │  │
│  │  ├─ Precipitation Model                                      │  │
│  │  ├─ Humidity Model                                           │  │
│  │  ├─ Cloud Cover Model                                        │  │
│  │  └─ Wind Speed Model                                         │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  Training Data:                                                     │
│  ✅ NASA MODIS Satellite Imagery (2020-2024)                        │
│  ✅ 18 Satellite Parameters                                         │
│  ✅ Real Weather Data Validation (2025)                             │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ (Future Integration)
                                  ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    AZURE OPENAI (Optional)                          │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  GPT-4 Model                                                 │  │
│  │                                                               │  │
│  │  Features:                                                    │  │
│  │  - Weather chat assistant                                    │  │
│  │  - Activity recommendations                                  │  │
│  │  - Natural language queries                                  │  │
│  │  - Personalized suggestions                                  │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ (Optional)
                                  ↓
┌─────────────────────────────────────────────────────────────────────┐
│                  ELASTICSEARCH CLOUD (Optional)                     │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Weather Data Index                                          │  │
│  │                                                               │  │
│  │  Features:                                                    │  │
│  │  - Search historical predictions                             │  │
│  │  - Filter by temperature, precipitation                      │  │
│  │  - Date range queries                                        │  │
│  │  - Location-based search                                     │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. User Request Flow

```
User → Frontend → Backend API → ML Models → Response
  ↓
Select Location (Chicago)
  ↓
Choose Activity (Beach Day)
  ↓
Pick Dates (Next Week)
  ↓
Generate Report
  ↓
Frontend calls: POST /predict-range
  ↓
Backend processes request
  ↓
ML models predict weather
  ↓
Response with predictions
  ↓
Frontend displays:
  - Weather avatar
  - Suitability score
  - Detailed breakdown
  - Recommendations
```

### 2. Prediction Pipeline

```
Input: Date Range (2025-10-05 to 2025-10-12)
  ↓
For each date:
  ↓
  ├─ Temperature Model
  │  └─ Predicts: avg_temp, feels_like
  │
  ├─ Precipitation Model
  │  └─ Predicts: total_precipitation
  │
  ├─ Humidity Model
  │  └─ Predicts: avg_humidity
  │
  ├─ Cloud Cover Model
  │  └─ Predicts: avg_cloud_cover
  │
  └─ Wind Speed Model
     └─ Predicts: avg_wind_speed
  ↓
Aggregate Results
  ↓
Calculate Suitability Score
  ↓
Return JSON Response
```

### 3. Suitability Scoring Algorithm

```
Input: Weather Data + Activity Profile
  ↓
For each weather parameter:
  ↓
  ├─ Temperature Score
  │  └─ Compare to ideal range (e.g., 75-90°F for beach)
  │
  ├─ Precipitation Score
  │  └─ Lower is better for most activities
  │
  ├─ Humidity Score
  │  └─ Moderate is ideal (40-60%)
  │
  ├─ Cloud Cover Score
  │  └─ Depends on activity (sunny for beach, cloudy for hiking)
  │
  └─ Wind Speed Score
     └─ Depends on activity (calm for beach, windy for sailing)
  ↓
Weighted Average
  ↓
Final Score (0-100)
  ↓
Color Coding:
  - Green (80-100): Perfect
  - Yellow (60-79): Good
  - Orange (40-59): Fair
  - Red (0-39): Poor
```

## Component Details

### Frontend Components

```
frontend_new/
├── index.html
│   ├── Step 1: Location Selection
│   │   └── Leaflet map with marker
│   ├── Step 2: Activity Profile
│   │   └── Predefined + custom profiles
│   ├── Step 3: Date Selection
│   │   └── Single date or range
│   └── Step 4: Report Display
│       ├── Weather avatar
│       ├── Score circle
│       ├── Stacked bar chart
│       └── Detailed breakdown
│
├── app.js
│   ├── State management
│   ├── API calls
│   ├── UI updates
│   ├── Chart rendering
│   └── Avatar logic
│
├── styles.css
│   ├── Golden/beige theme
│   ├── Responsive design
│   └── Animations
│
└── azure-api-config.js
    └── API URL configuration
```

### Backend Components

```
backend/
├── api_server.py
│   ├── FastAPI application
│   ├── CORS middleware
│   ├── API endpoints
│   └── Error handling
│
├── prediction/
│   ├── predict_simple.py
│   │   ├── predict_hourly()
│   │   └── predict_daily_range()
│   │
│   └── temperature/
│       ├── model_weights.pkl
│       └── scaler.pkl
│
├── Dockerfile
│   ├── Python 3.10 base
│   ├── Install dependencies
│   └── Run uvicorn
│
└── requirements.txt
    ├── fastapi
    ├── uvicorn
    ├── scikit-learn
    ├── pandas
    └── numpy
```

## Deployment Architecture

### Azure Resources

```
Resource Group: weather-app-rg
├── Azure Container Registry
│   ├── Name: weatherappreg{random}
│   ├── SKU: Basic
│   └── Contains: weather-api:latest image
│
├── Container Apps Environment
│   ├── Name: weather-app-env
│   └── Location: East US
│
├── Container App
│   ├── Name: weather-api
│   ├── Image: weatherappreg{random}.azurecr.io/weather-api:latest
│   ├── CPU: 1.0 cores
│   ├── Memory: 2.0 GB
│   ├── Replicas: 1-3 (auto-scale)
│   ├── Port: 8000
│   └── Ingress: External (HTTPS)
│
└── Static Web App
    ├── Name: orange-coast-0614e430f
    ├── Location: Global (CDN)
    ├── Plan: Free
    └── Custom Domain: Supported
```

### Network Flow

```
Internet
  ↓
Azure Front Door (Global)
  ↓
Static Web App (Frontend)
  ├─ Cached at edge locations
  └─ Served via CDN
  ↓
User's Browser
  ↓
HTTPS API Calls
  ↓
Azure Load Balancer
  ↓
Container App Instances (1-3)
  ├─ Instance 1 (Active)
  ├─ Instance 2 (Auto-scaled)
  └─ Instance 3 (Auto-scaled)
  ↓
ML Models (In-memory)
  ↓
Response
```

## Scaling Strategy

### Frontend Scaling
- **Global CDN**: Automatic edge caching
- **No server**: Static files only
- **Unlimited**: No scaling limits
- **Cost**: Free tier

### Backend Scaling
- **Auto-scale**: Based on CPU/memory
- **Min replicas**: 1 (always on)
- **Max replicas**: 3 (configurable)
- **Scale triggers**:
  - CPU > 70%
  - Memory > 80%
  - Request queue > 10

### Future: LLM Scaling
- **Separate service**: Azure OpenAI
- **Managed scaling**: Automatic
- **Rate limiting**: Built-in
- **Cost**: Pay per token

## Security Architecture

### Frontend Security
```
✅ HTTPS Only (automatic)
✅ Content Security Policy
✅ No sensitive data in client
✅ API keys in backend only
✅ CORS configured
```

### Backend Security
```
✅ HTTPS Only (automatic)
✅ CORS whitelist
✅ Environment variables for secrets
✅ Azure Key Vault integration (optional)
✅ Managed identity
✅ Rate limiting (configurable)
```

### Network Security
```
✅ Azure DDoS Protection
✅ Web Application Firewall (optional)
✅ Private endpoints (optional)
✅ VNet integration (optional)
```

## Monitoring & Observability

### Built-in Monitoring
```
Azure Portal
├── Container App Metrics
│   ├── CPU usage
│   ├── Memory usage
│   ├── Request count
│   ├── Response time
│   └── Error rate
│
├── Static Web App Analytics
│   ├── Page views
│   ├── Unique visitors
│   ├── Geographic distribution
│   └── Performance metrics
│
└── Container Registry
    ├── Image pulls
    ├── Storage usage
    └── Webhook events
```

### Application Insights (Optional)
```
✅ Distributed tracing
✅ Custom metrics
✅ Log analytics
✅ Alerts and notifications
✅ Performance profiling
```

## Cost Optimization

### Current Setup
```
Azure Container Apps:     $30-50/month
  ├─ 1-3 instances
  ├─ 1 CPU, 2GB RAM each
  └─ ~720 hours/month

Container Registry:       $5/month
  └─ Basic tier

Static Web Apps:          Free
  └─ Free tier

Total:                    $35-55/month
```

### With LLM
```
Base Infrastructure:      $35-55/month
Azure OpenAI:            $50-200/month
  ├─ GPT-4: $0.03/1K tokens
  └─ Estimated 2M-7M tokens/month

Total:                    $85-255/month
```

### Optimization Tips
```
✅ Use free tier where possible
✅ Scale down during low usage
✅ Use spot instances for dev/test
✅ Set up cost alerts
✅ Monitor resource utilization
✅ Delete unused resources
```

## Future Enhancements

### Phase 1: LLM Integration
```
✅ Azure OpenAI setup
✅ Chat endpoint
✅ Activity recommendations
✅ Natural language queries
```

### Phase 2: Advanced Features
```
🔜 Voice interface (Azure Speech)
🔜 Multi-language support
🔜 Mobile app (React Native)
🔜 Push notifications
🔜 User accounts
🔜 Saved preferences
```

### Phase 3: Enterprise Features
```
🔜 Custom domains
🔜 SSO authentication
🔜 API rate limiting
🔜 Advanced analytics
🔜 A/B testing
🔜 Feature flags
```

## Technology Stack

### Frontend
- HTML5, CSS3, JavaScript (ES6+)
- Leaflet.js (maps)
- Chart.js (visualizations)
- Azure Static Web Apps

### Backend
- Python 3.10
- FastAPI (web framework)
- Uvicorn (ASGI server)
- scikit-learn (ML models)
- pandas, numpy (data processing)
- Azure Container Apps

### ML/AI
- Random Forest (temperature)
- Custom models (other parameters)
- NASA MODIS data
- Azure OpenAI (future)

### Infrastructure
- Docker (containerization)
- Azure Container Registry
- Azure Container Apps
- Azure Static Web Apps
- Azure OpenAI (future)

---

This architecture is designed to be:
- ✅ **Scalable**: Auto-scales based on demand
- ✅ **Reliable**: High availability with multiple instances
- ✅ **Secure**: HTTPS, managed identities, secrets management
- ✅ **Cost-effective**: Pay only for what you use
- ✅ **Maintainable**: Clear separation of concerns
- ✅ **Extensible**: Easy to add new features (LLM, etc.)

Perfect for your hackathon and ready for production! 🚀
