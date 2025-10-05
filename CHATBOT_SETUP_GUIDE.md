# 🤖 AI Chatbot Setup Guide

## Overview

Your weather trip planner now includes an intelligent AI chatbot that:
- ✅ Analyzes weather forecasts and suggests activities
- ✅ Finds local events at your destination
- ✅ Provides personalized trip recommendations
- ✅ Warns about weather-dependent outdoor events
- ✅ Suggests indoor alternatives for bad weather

## Features

### 1. Weather-Aware Planning
The chatbot has access to your weather predictions and can:
- Recommend activities based on temperature, precipitation, wind
- Warn about unsuitable conditions for outdoor events
- Suggest best days for specific activities

### 2. Local Events Integration
The chatbot knows about local events and can:
- Find events happening during your trip dates
- Assess weather suitability for each event
- Recommend indoor alternatives

### 3. Conversational Interface
- Natural language understanding
- Context-aware responses
- Remembers conversation history
- Personalized recommendations

## Quick Start

### Option 1: Use Without AI (Mock Mode)

The chatbot UI is already integrated! It will work with mock data without Azure OpenAI:

```powershell
# Just run your backend
python backend/api_server.py
```

The chatbot will show a message that AI is not configured but the UI will still work.

### Option 2: Enable Full AI with Azure OpenAI

Follow these steps to enable the full AI-powered chatbot:

## Step-by-Step Setup

### 1. Create Azure OpenAI Resource

```powershell
# Login to Azure
az login

# Create Azure OpenAI resource
az cognitiveservices account create `
    --name weather-trip-openai `
    --resource-group weather-app-rg `
    --kind OpenAI `
    --sku S0 `
    --location eastus `
    --yes
```

**Alternative**: Create via Azure Portal
1. Go to https://portal.azure.com
2. Search for "Azure OpenAI"
3. Click "Create"
4. Fill in details:
   - Resource group: `weather-app-rg`
   - Region: `East US`
   - Name: `weather-trip-openai`
   - Pricing tier: `Standard S0`

### 2. Deploy GPT-4 Model

```powershell
# Deploy GPT-4 model
az cognitiveservices account deployment create `
    --name weather-trip-openai `
    --resource-group weather-app-rg `
    --deployment-name gpt-4 `
    --model-name gpt-4 `
    --model-version "0613" `
    --model-format OpenAI `
    --sku-capacity 10 `
    --sku-name "Standard"
```

**Alternative**: Deploy via Azure Portal
1. Go to your Azure OpenAI resource
2. Click "Model deployments"
3. Click "Create new deployment"
4. Select:
   - Model: `gpt-4`
   - Deployment name: `gpt-4`
   - Version: `0613`

### 3. Get API Credentials

```powershell
# Get API key
az cognitiveservices account keys list `
    --name weather-trip-openai `
    --resource-group weather-app-rg `
    --query key1 `
    -o tsv

# Get endpoint
az cognitiveservices account show `
    --name weather-trip-openai `
    --resource-group weather-app-rg `
    --query properties.endpoint `
    -o tsv
```

**Alternative**: Get via Azure Portal
1. Go to your Azure OpenAI resource
2. Click "Keys and Endpoint"
3. Copy:
   - KEY 1
   - Endpoint

### 4. Configure Backend

#### For Local Development:

Create a `.env` file in the `backend` folder:

```env
AZURE_OPENAI_KEY=your-key-here
AZURE_OPENAI_ENDPOINT=https://weather-trip-openai.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4
```

Then run:
```powershell
python backend/api_server.py
```

#### For Azure Container Apps:

```powershell
# Update container app with environment variables
az containerapp update `
    --name weather-api `
    --resource-group weather-app-rg `
    --set-env-vars `
        AZURE_OPENAI_KEY=your-key-here `
        AZURE_OPENAI_ENDPOINT=https://weather-trip-openai.openai.azure.com/ `
        AZURE_OPENAI_DEPLOYMENT=gpt-4

# Restart to apply changes
az containerapp revision restart `
    --name weather-api `
    --resource-group weather-app-rg
```

### 5. Test the Chatbot

1. Open your frontend: http://localhost:8000 (or Azure URL)
2. Look for the chatbot in the bottom-right corner
3. Try these example questions:

```
"What's the weather like for my trip?"
"What activities do you recommend for sunny weather?"
"Are there any events happening in Chicago next week?"
"What should I do if it rains?"
"Plan a 3-day itinerary for me"
```

## Chatbot Capabilities

### Weather Analysis
```
User: "What's the weather forecast?"
Bot: "Based on the forecast, you'll have temperatures around 72°F 
      with partly cloudy skies. Perfect for outdoor activities!"
```

### Activity Recommendations
```
User: "What should I do on a rainy day?"
Bot: "For rainy weather, I recommend:
      1. Visit the Art Institute of Chicago (indoor)
      2. Explore the Museum of Science and Industry
      3. Enjoy deep-dish pizza at Lou Malnati's"
```

### Event Discovery
```
User: "Are there any events this weekend?"
Bot: "I found these events:
      📅 Chicago Jazz Festival - Outdoor (Check weather!)
      🎨 Art Institute Exhibition - Indoor (Weather-proof)
      🎵 Millennium Park Concert - Outdoor (Best if sunny)"
```

### Itinerary Planning
```
User: "Plan a 3-day trip for me"
Bot: "Here's your personalized itinerary:
      
      Day 1 (Sunny, 75°F):
      - Morning: Millennium Park
      - Afternoon: Navy Pier
      - Evening: Riverwalk dinner
      
      Day 2 (Cloudy, 68°F):
      - Morning: Art Institute
      - Afternoon: Shopping on Magnificent Mile
      - Evening: Theater show
      
      Day 3 (Rainy, 65°F):
      - Morning: Museum of Science
      - Afternoon: Indoor food tour
      - Evening: Jazz club"
```

## Integrating Real Event APIs

To get real event data, integrate with these APIs:

### Ticketmaster API

```python
# Add to backend/api_server.py
import httpx

async def search_ticketmaster_events(location, start_date, end_date, lat, lng):
    api_key = os.getenv("TICKETMASTER_API_KEY")
    url = "https://app.ticketmaster.com/discovery/v2/events.json"
    
    params = {
        "apikey": api_key,
        "latlong": f"{lat},{lng}",
        "startDateTime": f"{start_date}T00:00:00Z",
        "endDateTime": f"{end_date}T23:59:59Z",
        "size": 20
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()
        
        events = []
        if "_embedded" in data and "events" in data["_embedded"]:
            for event in data["_embedded"]["events"]:
                events.append({
                    "name": event["name"],
                    "date": event["dates"]["start"]["localDate"],
                    "location": event["_embedded"]["venues"][0]["name"],
                    "type": event["classifications"][0]["segment"]["name"],
                    "description": event.get("info", ""),
                    "weather_dependent": "outdoor" in event.get("info", "").lower()
                })
        
        return events
```

Sign up: https://developer.ticketmaster.com/

### Eventbrite API

```python
async def search_eventbrite_events(location, start_date, end_date, lat, lng):
    api_key = os.getenv("EVENTBRITE_API_KEY")
    url = "https://www.eventbriteapi.com/v3/events/search/"
    
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {
        "location.latitude": lat,
        "location.longitude": lng,
        "location.within": "10km",
        "start_date.range_start": f"{start_date}T00:00:00",
        "start_date.range_end": f"{end_date}T23:59:59"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        data = response.json()
        
        events = []
        for event in data.get("events", []):
            events.append({
                "name": event["name"]["text"],
                "date": event["start"]["local"][:10],
                "location": event.get("venue", {}).get("name", location),
                "type": event.get("category", {}).get("name", "Event"),
                "description": event.get("description", {}).get("text", ""),
                "weather_dependent": event.get("online_event", False) == False
            })
        
        return events
```

Sign up: https://www.eventbrite.com/platform/api

### Google Places API (for attractions)

```python
async def search_google_places(location, lat, lng):
    api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    
    params = {
        "key": api_key,
        "location": f"{lat},{lng}",
        "radius": 5000,
        "type": "tourist_attraction"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()
        
        places = []
        for place in data.get("results", []):
            places.append({
                "name": place["name"],
                "location": place["vicinity"],
                "type": "Attraction",
                "rating": place.get("rating", 0),
                "weather_dependent": "outdoor" in place.get("types", [])
            })
        
        return places
```

Sign up: https://developers.google.com/maps/documentation/places/web-service

## Customizing the Chatbot

### Modify System Prompt

Edit `backend/api_server.py`:

```python
messages = [
    {
        "role": "system",
        "content": """You are a helpful trip planning assistant specializing in [YOUR SPECIALTY].
        
        Your personality: [FRIENDLY/PROFESSIONAL/CASUAL]
        
        Focus on:
        1. [Your focus area 1]
        2. [Your focus area 2]
        3. [Your focus area 3]
        
        Always provide specific, actionable recommendations."""
    }
]
```

### Add Custom Features

```python
@app.post("/chat-with-preferences")
async def chat_with_preferences(request: ChatMessage, user_preferences: dict):
    """Chat with user preferences (budget, interests, etc.)"""
    
    context += f"\n\nUser Preferences:"
    context += f"\n  Budget: {user_preferences.get('budget', 'Not specified')}"
    context += f"\n  Interests: {', '.join(user_preferences.get('interests', []))}"
    context += f"\n  Dietary: {user_preferences.get('dietary', 'None')}"
    
    # Rest of chat logic...
```

## Cost Management

### Azure OpenAI Pricing

**GPT-4**:
- Input: $0.03 per 1K tokens
- Output: $0.06 per 1K tokens

**GPT-3.5-Turbo** (cheaper alternative):
- Input: $0.0015 per 1K tokens
- Output: $0.002 per 1K tokens

### Estimated Costs

**Light Usage** (100 conversations/day):
- ~$30-50/month with GPT-4
- ~$5-10/month with GPT-3.5-Turbo

**Medium Usage** (500 conversations/day):
- ~$150-250/month with GPT-4
- ~$25-50/month with GPT-3.5-Turbo

**Heavy Usage** (2000 conversations/day):
- ~$600-1000/month with GPT-4
- ~$100-200/month with GPT-3.5-Turbo

### Cost Optimization Tips

1. **Use GPT-3.5-Turbo for simple queries**:
```python
# Detect simple queries
if is_simple_query(message):
    model = "gpt-3.5-turbo"
else:
    model = "gpt-4"
```

2. **Limit conversation history**:
```python
# Keep only last 5 messages
conversation_history = conversation_history[-5:]
```

3. **Set token limits**:
```python
response = openai_client.chat.completions.create(
    model="gpt-4",
    messages=messages,
    max_tokens=500  # Limit response length
)
```

4. **Cache common responses**:
```python
# Cache FAQ responses
faq_cache = {
    "what's the weather": "cached_response",
    "best activities": "cached_response"
}
```

## Troubleshooting

### Chatbot Not Responding

**Check backend logs**:
```powershell
# Local
python backend/api_server.py

# Azure
az containerapp logs show --name weather-api --resource-group weather-app-rg --follow
```

**Common issues**:
1. Azure OpenAI credentials not set
2. Model deployment name mismatch
3. API quota exceeded
4. Network connectivity issues

### "AI chatbot is not configured" Message

This means environment variables are not set. Check:

```powershell
# Windows
echo %AZURE_OPENAI_KEY%
echo %AZURE_OPENAI_ENDPOINT%

# PowerShell
$env:AZURE_OPENAI_KEY
$env:AZURE_OPENAI_ENDPOINT
```

### Rate Limit Errors

If you hit rate limits:

1. **Increase quota** in Azure Portal:
   - Go to Azure OpenAI resource
   - Click "Quotas"
   - Request increase

2. **Add retry logic**:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def call_openai_with_retry(messages):
    return openai_client.chat.completions.create(...)
```

## Testing

### Test Chatbot Status

```powershell
curl http://localhost:8000/chat-status
```

Expected response:
```json
{
  "available": true,
  "openai_library": true,
  "configured": true,
  "endpoint": "https://weather-trip-openai.openai.azure.com/"
}
```

### Test Chat Endpoint

```powershell
curl -X POST http://localhost:8000/chat `
  -H "Content-Type: application/json" `
  -d '{
    "message": "What activities do you recommend?",
    "location": {"name": "Chicago", "lat": 41.8781, "lng": -87.6298},
    "dates": {"start": "2025-10-10", "end": "2025-10-12"}
  }'
```

### Test Events Endpoint

```powershell
curl -X POST http://localhost:8000/events `
  -H "Content-Type: application/json" `
  -d '{
    "location": "Chicago",
    "start_date": "2025-10-10",
    "end_date": "2025-10-12",
    "lat": 41.8781,
    "lng": -87.6298
  }'
```

## Security Best Practices

### 1. Use Azure Key Vault

```powershell
# Create Key Vault
az keyvault create `
    --name weather-app-kv `
    --resource-group weather-app-rg

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

### 2. Add Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/chat")
@limiter.limit("10/minute")  # 10 requests per minute
async def chat_with_planner(request: Request, chat_request: ChatMessage):
    # Your code...
```

### 3. Input Validation

```python
def validate_message(message: str) -> bool:
    # Check length
    if len(message) > 1000:
        return False
    
    # Check for malicious content
    blocked_patterns = ["<script>", "javascript:", "eval("]
    if any(pattern in message.lower() for pattern in blocked_patterns):
        return False
    
    return True
```

## Next Steps

1. ✅ Set up Azure OpenAI
2. ✅ Configure environment variables
3. ✅ Test chatbot locally
4. ✅ Deploy to Azure
5. 🔜 Integrate real event APIs
6. 🔜 Add user preferences
7. 🔜 Implement caching
8. 🔜 Add analytics

## Support

- **Azure OpenAI Docs**: https://learn.microsoft.com/azure/cognitive-services/openai/
- **OpenAI API Reference**: https://platform.openai.com/docs/api-reference
- **Ticketmaster API**: https://developer.ticketmaster.com/
- **Eventbrite API**: https://www.eventbrite.com/platform/api

---

Your AI chatbot is ready to help users plan amazing trips! 🚀
