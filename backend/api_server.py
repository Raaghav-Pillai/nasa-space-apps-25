"""
Simple API server for the frontend
Connects to the prediction models
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import sys
import os
import json
from datetime import datetime
import httpx

# Add prediction module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'prediction'))

from predict_simple import predict_hourly, predict_daily_range

# Google Gemini integration
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Initialize Gemini client
gemini_model = None
if GEMINI_AVAILABLE and os.getenv("GEMINI_API_KEY"):
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        # Use gemini-2.5-flash (latest, fastest, free)
        gemini_model = genai.GenerativeModel('gemini-2.5-flash')
        print("✅ Google Gemini client initialized (gemini-2.5-flash)")
    except Exception as e:
        print(f"⚠️  Gemini initialization failed: {e}")
elif GEMINI_AVAILABLE:
    print("⚠️  Gemini API key not set. Set GEMINI_API_KEY environment variable.")

app = FastAPI(title="Weather Prediction API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PredictRequest(BaseModel):
    date: str
    hour: int = 12

class RangeRequest(BaseModel):
    start_date: str
    end_date: str

@app.get("/")
async def root():
    return {
        "message": "Weather Prediction API",
        "endpoints": ["/predict", "/predict-range", "/health"]
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/predict")
async def predict(request: PredictRequest):
    """Predict weather for a specific date and hour"""
    try:
        result = predict_hourly(request.date, request.hour)
        return result
    except Exception as e:
        return {"error": str(e)}

@app.post("/predict-range")
async def predict_range(request: RangeRequest):
    """Predict weather for a date range"""
    try:
        df = predict_daily_range(request.start_date, request.end_date)
        results = df.to_dict('records')
        return results
    except Exception as e:
        return {"error": str(e)}

class ChatMessage(BaseModel):
    message: str
    location: Optional[dict] = None
    dates: Optional[dict] = None
    weather_data: Optional[dict] = None
    conversation_history: Optional[List[dict]] = []

class EventSearchRequest(BaseModel):
    location: str
    start_date: str
    end_date: str
    lat: float
    lng: float

async def search_local_events(location: str, start_date: str, end_date: str, lat: float, lng: float):
    """Search for local events using external APIs"""
    # This is a placeholder - you can integrate with real event APIs like:
    # - Ticketmaster API
    # - Eventbrite API
    # - Google Places API
    # For demo purposes, returning mock data
    
    mock_events = [
        {
            "name": "Chicago Jazz Festival",
            "date": start_date,
            "location": location,
            "type": "Music",
            "description": "Annual jazz festival featuring local and international artists",
            "weather_dependent": True
        },
        {
            "name": "Millennium Park Concert",
            "date": start_date,
            "location": "Millennium Park",
            "type": "Music",
            "description": "Free outdoor concert series",
            "weather_dependent": True
        },
        {
            "name": "Art Institute Exhibition",
            "date": start_date,
            "location": "Art Institute of Chicago",
            "type": "Art",
            "description": "Indoor art exhibition - weather independent",
            "weather_dependent": False
        }
    ]
    
    return mock_events

@app.post("/chat")
async def chat_with_planner(request: ChatMessage):
    """Chat with AI trip planner that knows about weather and local events"""
    
    if not gemini_model:
        return {
            "response": "AI chatbot is not configured. Please set GEMINI_API_KEY environment variable. Get your free API key at: https://makersuite.google.com/app/apikey",
            "events": [],
            "recommendations": []
        }
    
    try:
        # Extract dates from message if not provided
        import re
        from datetime import datetime, timedelta
        
        message_lower = request.message.lower()
        auto_fetch_weather = False
        start_date = None
        end_date = None
        
        # Check if user is asking about weather or planning activities
        weather_keywords = ['weather', 'forecast', 'temperature', 'rain', 'conditions', 'picnic', 'trip', 'visit', 'plan', 'go', 'outdoor', 'activities', 'suitable', 'good day']
        if any(word in message_lower for word in weather_keywords):
            # Try to extract dates from message
            if 'october' in message_lower or 'oct' in message_lower:
                start_date = '2025-10-01'
                end_date = '2025-10-07'
                auto_fetch_weather = True
            elif 'next week' in message_lower:
                today = datetime.now()
                next_week = today + timedelta(days=7)
                start_date = next_week.strftime('%Y-%m-%d')
                end_date = (next_week + timedelta(days=6)).strftime('%Y-%m-%d')
                auto_fetch_weather = True
            elif 'this week' in message_lower:
                today = datetime.now()
                start_date = today.strftime('%Y-%m-%d')
                end_date = (today + timedelta(days=6)).strftime('%Y-%m-%d')
                auto_fetch_weather = True
            elif 'tomorrow' in message_lower:
                tomorrow = datetime.now() + timedelta(days=1)
                start_date = tomorrow.strftime('%Y-%m-%d')
                end_date = start_date
                auto_fetch_weather = True
        
        # Fetch weather if dates detected or provided
        weather_forecast = None
        if auto_fetch_weather or (request.dates and request.dates.get('start')):
            if not start_date and request.dates:
                start_date = request.dates.get('start')
                end_date = request.dates.get('end', start_date)
            
            if start_date:
                try:
                    # Fetch weather predictions
                    df = predict_daily_range(start_date, end_date)
                    if df is not None and len(df) > 0:
                        weather_forecast = df.to_dict('records')
                        print(f"✅ Fetched weather for {len(df)} days")
                    else:
                        print("⚠️ No weather data returned")
                except Exception as e:
                    print(f"❌ Weather fetch error: {e}")
                    import traceback
                    traceback.print_exc()
        
        # Extract location from message if not provided
        location_to_use = request.location
        if not location_to_use and 'chicago' in message_lower:
            location_to_use = {'name': 'Chicago', 'lat': 41.8781, 'lng': -87.6298}
        
        # Get local events if location and dates provided
        events = []
        if location_to_use and (request.dates or start_date):
            event_start = start_date or request.dates.get('start', '')
            event_end = end_date or request.dates.get('end', '')
            events = await search_local_events(
                location_to_use.get('name', 'Unknown'),
                event_start,
                event_end,
                location_to_use.get('lat', 0),
                location_to_use.get('lng', 0)
            )
        
        # Build context for the AI
        system_prompt = """You are an intelligent trip planning assistant with expertise in weather analysis and activity planning.

Your capabilities:
1. Analyze weather forecasts and determine suitability for specific activities
2. Intelligently weight weather factors based on the activity:
   - For PICNICS: Temperature (40%), Precipitation (40%), Wind (10%), Humidity (10%)
   - For BEACH: Temperature (35%), Precipitation (30%), Cloud cover (25%), Wind (10%)
   - For HIKING: Temperature (30%), Precipitation (30%), Cloud cover (20%), Wind (20%)
   - For SAILING: Wind (50%), Temperature (20%), Precipitation (20%), Cloud cover (10%)
   - For SKIING: Temperature (60%), Precipitation (20%), Wind (15%), Cloud cover (5%)
   - For OUTDOOR SPORTS: Temperature (35%), Precipitation (35%), Wind (20%), Humidity (10%)

3. Provide specific recommendations:
   - Calculate suitability scores (0-100%) based on weighted factors
   - Identify the BEST days for the activity
   - Explain WHY certain days are better
   - Warn about unsuitable conditions
   - Suggest alternatives if weather is poor

4. Be specific and actionable:
   - "Tuesday is PERFECT (95% suitable) - 72°F, sunny, light breeze"
   - "Avoid Wednesday (30% suitable) - heavy rain expected"
   - "Best window: Thursday-Saturday (85%+ suitable)"

Always analyze the actual weather data provided and give data-driven recommendations."""
        
        context = f"""You are an intelligent trip planning assistant with access to:
1. Real-time weather predictions (NASA MODIS satellite data, 1.72°F accuracy)
2. Local events and activities
3. Activity suitability scoring

Current Context:
"""
        
        if location_to_use:
            context += f"\nLocation: {location_to_use.get('name', 'Unknown')} (Lat: {location_to_use.get('lat')}, Lng: {location_to_use.get('lng')})"
        
        if request.dates:
            context += f"\nDates: {request.dates.get('start')} to {request.dates.get('end')}"
        
        # Use fetched weather or provided weather data
        weather_to_use = weather_forecast or (request.weather_data if request.weather_data else None)
        
        if weather_to_use:
            context += f"\n\nWeather Forecast:"
            if isinstance(weather_to_use, list):
                # Multiple days
                for day in weather_to_use[:7]:  # Limit to 7 days
                    context += f"\n\n{day.get('date', 'Unknown date')}:"
                    context += f"\n  - Temperature: {day.get('avg_temperature_f', 'N/A')}°F"
                    context += f"\n  - Feels like: {day.get('avg_feels_like_f', 'N/A')}°F"
                    context += f"\n  - Precipitation: {day.get('total_precipitation_mm', 'N/A')}mm"
                    context += f"\n  - Humidity: {day.get('avg_humidity_percent', 'N/A')}%"
                    context += f"\n  - Cloud cover: {day.get('avg_cloud_cover_percent', 'N/A')}%"
                    context += f"\n  - Wind: {day.get('avg_wind_speed_mph', 'N/A')}mph"
            else:
                # Single day or summary
                for key, value in weather_to_use.items():
                    context += f"\n  - {key}: {value}"
        
        if events:
            context += f"\n\nLocal Events:"
            for event in events:
                context += f"\n  - {event['name']} ({event['type']}): {event['description']}"
                if event['weather_dependent']:
                    context += " [Weather-dependent activity]"
        
        context += f"\n\nUser Question: {request.message}"
        
        # Add analysis instructions if weather data is available
        if weather_to_use:
            context += f"\n\nPlease analyze this weather data for the requested activity and recommend the best days."
        
        # Build conversation history for Gemini
        conversation_text = system_prompt + "\n\n"
        for msg in request.conversation_history[-5:]:  # Last 5 messages for context
            role = "User" if msg.get("role") == "user" else "Assistant"
            conversation_text += f"{role}: {msg.get('content', '')}\n\n"
        
        # Add current context and message
        conversation_text += context
        
        # Call Google Gemini with proper safety settings
        try:
            from google.generativeai.types import HarmCategory, HarmBlockThreshold
            
            response = gemini_model.generate_content(
                conversation_text,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=800,
                ),
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                }
            )
            
            # Check if response has valid text
            if hasattr(response, 'text') and response.text:
                ai_response = response.text
            elif hasattr(response, 'candidates') and response.candidates:
                # Try to get text from candidates
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    ai_response = ''.join([part.text for part in candidate.content.parts if hasattr(part, 'text')])
                else:
                    ai_response = "I understand you want to plan a trip! However, I'm having trouble generating a detailed response. Could you rephrase your question?"
            else:
                # If blocked, provide helpful response based on what we know
                if weather_to_use and isinstance(weather_to_use, list) and len(weather_to_use) > 0:
                    # Generate a simple response from the weather data
                    best_day = weather_to_use[0]
                    ai_response = f"Great idea! Based on the weather forecast:\n\n"
                    ai_response += f"📅 Best day: {best_day.get('date', 'Unknown')}\n"
                    ai_response += f"🌡️ Temperature: {best_day.get('avg_temperature_f', 'N/A')}°F\n"
                    ai_response += f"💧 Precipitation: {best_day.get('total_precipitation_mm', 'N/A')}mm\n"
                    ai_response += f"💨 Wind: {best_day.get('avg_wind_speed_mph', 'N/A')}mph\n\n"
                    ai_response += f"This looks like a good day for your activity!"
                else:
                    ai_response = "I can help you plan your trip! Let me know your location and dates, and I'll analyze the weather for you."
        except Exception as e:
            # Fallback response if Gemini fails
            print(f"Gemini error: {e}")
            if weather_to_use and isinstance(weather_to_use, list) and len(weather_to_use) > 0:
                # At least show the weather data
                ai_response = f"I found weather data for your dates! Here's a quick summary:\n\n"
                for day in weather_to_use[:3]:
                    ai_response += f"📅 {day.get('date')}: {day.get('avg_temperature_f')}°F, {day.get('total_precipitation_mm')}mm rain\n"
            else:
                ai_response = "I'm here to help with your trip planning! I can analyze weather forecasts, suggest activities, and recommend events. What would you like to know about your trip?"
        
        # Generate specific recommendations
        recommendations = []
        if request.weather_data and events:
            # Analyze weather suitability for each event
            for event in events:
                if event['weather_dependent']:
                    # Simple logic - you can make this more sophisticated
                    temp = request.weather_data.get('avg_temperature_f', 70)
                    precip = request.weather_data.get('total_precipitation_mm', 0)
                    
                    suitable = temp > 60 and temp < 85 and precip < 5
                    recommendations.append({
                        "event": event['name'],
                        "suitable": suitable,
                        "reason": f"Temperature: {temp}°F, Precipitation: {precip}mm"
                    })
                else:
                    recommendations.append({
                        "event": event['name'],
                        "suitable": True,
                        "reason": "Indoor event - weather independent"
                    })
        
        return {
            "response": ai_response,
            "events": events,
            "recommendations": recommendations,
            "context_used": bool(request.weather_data or events)
        }
        
    except Exception as e:
        return {
            "response": f"I encountered an error: {str(e)}. Please try again.",
            "events": [],
            "recommendations": [],
            "error": str(e)
        }

@app.post("/events")
async def get_local_events(request: EventSearchRequest):
    """Get local events for a specific location and date range"""
    try:
        events = await search_local_events(
            request.location,
            request.start_date,
            request.end_date,
            request.lat,
            request.lng
        )
        return {"events": events, "count": len(events)}
    except Exception as e:
        return {"error": str(e), "events": []}

@app.get("/chat-status")
async def chat_status():
    """Check if AI chat is available"""
    return {
        "available": gemini_model is not None,
        "gemini_library": GEMINI_AVAILABLE,
        "configured": bool(os.getenv("GEMINI_API_KEY")),
        "provider": "Google Gemini",
        "model": "gemini-pro"
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Weather Prediction API Server...")
    print("📍 Server running at: http://localhost:8000")
    print("📖 API docs at: http://localhost:8000/docs")
    if gemini_model:
        print("🤖 AI Chatbot: ENABLED (Google Gemini)")
    else:
        print("⚠️  AI Chatbot: DISABLED (set GEMINI_API_KEY to enable)")
        print("    Get your free API key at: https://makersuite.google.com/app/apikey")
    uvicorn.run(app, host="0.0.0.0", port=8000)
