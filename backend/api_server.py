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
        # Get local events if location and dates provided
        events = []
        if request.location and request.dates:
            events = await search_local_events(
                request.location.get('name', 'Unknown'),
                request.dates.get('start', ''),
                request.dates.get('end', ''),
                request.location.get('lat', 0),
                request.location.get('lng', 0)
            )
        
        # Build context for the AI
        system_prompt = """You are a helpful trip planning assistant. You help users plan their trips by:
1. Analyzing weather forecasts and suggesting suitable activities
2. Recommending local events based on weather conditions
3. Providing personalized itineraries
4. Warning about weather-dependent outdoor events
5. Suggesting indoor alternatives when weather is poor

Be conversational, helpful, and specific. Use the weather data and events provided to give actionable recommendations."""
        
        context = f"""You are an intelligent trip planning assistant with access to:
1. Real-time weather predictions (NASA MODIS satellite data, 1.72°F accuracy)
2. Local events and activities
3. Activity suitability scoring

Current Context:
"""
        
        if request.location:
            context += f"\nLocation: {request.location.get('name', 'Unknown')} (Lat: {request.location.get('lat')}, Lng: {request.location.get('lng')})"
        
        if request.dates:
            context += f"\nDates: {request.dates.get('start')} to {request.dates.get('end')}"
        
        if request.weather_data:
            context += f"\n\nWeather Forecast:"
            for key, value in request.weather_data.items():
                context += f"\n  - {key}: {value}"
        
        if events:
            context += f"\n\nLocal Events:"
            for event in events:
                context += f"\n  - {event['name']} ({event['type']}): {event['description']}"
                if event['weather_dependent']:
                    context += " [Weather-dependent activity]"
        
        context += f"\n\nUser Question: {request.message}"
        
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
            else:
                # If blocked or no text, provide a helpful fallback
                ai_response = "I can help you plan your trip! Based on the weather data, I can suggest activities and create an itinerary. What would you like to know?"
        except Exception as e:
            # Fallback response if Gemini fails
            print(f"Gemini error: {e}")
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
