#!/usr/bin/env python3
"""
Simple FastAPI server for NASA Weather App
Runs locally and integrates with Elasticsearch
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import json
import os
from typing import Optional, Dict, Any
import requests

app = FastAPI(title="NASA Weather API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Elasticsearch configuration
ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL', 'http://localhost:9200')

class PredictionRequest(BaseModel):
    date: str
    hour: int = 12
    location: Optional[Dict[str, float]] = None

class SearchRequest(BaseModel):
    query: str = "*"
    date: Optional[str] = None
    limit: int = 50

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "NASA Weather API",
        "elasticsearch": await check_elasticsearch()
    }

async def check_elasticsearch():
    """Check if Elasticsearch is available"""
    try:
        response = requests.get(f"{ELASTICSEARCH_URL}/_cluster/health", timeout=5)
        return response.status_code == 200
    except:
        return False

@app.post("/predict")
async def predict_temperature(request: PredictionRequest):
    """Predict temperature for a given date and hour"""
    try:
        # Mock prediction logic (replace with your actual model)
        base_temp = 20.0  # Base temperature in Celsius
        hour_adjustment = (request.hour - 12) * 0.8  # Temperature varies by hour
        seasonal_adjustment = 5.0 if "07" in request.date or "08" in request.date else 0.0
        
        predicted_temp = base_temp + hour_adjustment + seasonal_adjustment
        feels_like = predicted_temp + 2.5  # Simple feels-like calculation
        
        # Determine time period
        if 6 <= request.hour < 12:
            time_period = "morning"
        elif 12 <= request.hour < 18:
            time_period = "afternoon"
        elif 18 <= request.hour < 21:
            time_period = "evening"
        else:
            time_period = "night"
        
        # Create prediction result
        result = {
            "date": request.date,
            "hour": request.hour,
            "time_period": time_period,
            "predicted_temperature": round(predicted_temp, 2),
            "feels_like_temperature": round(feels_like, 2),
            "confidence": 0.92,
            "description": f"Predicted {time_period} temperature",
            "location": request.location,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Store in Elasticsearch if available
        await store_prediction(result)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/search")
async def search_predictions(q: str = "*", date: Optional[str] = None, limit: int = 50):
    """Search historical predictions"""
    try:
        # Build Elasticsearch query
        query = {
            "query": {
                "bool": {
                    "must": []
                }
            },
            "sort": [{"timestamp": {"order": "desc"}}],
            "size": limit
        }
        
        if q != "*":
            query["query"]["bool"]["must"].append({
                "multi_match": {
                    "query": q,
                    "fields": ["description", "time_period"]
                }
            })
        
        if date:
            query["query"]["bool"]["must"].append({
                "term": {"date": date}
            })
        
        # If no specific conditions, match all
        if not query["query"]["bool"]["must"]:
            query["query"] = {"match_all": {}}
        
        # Search Elasticsearch
        try:
            response = requests.post(
                f"{ELASTICSEARCH_URL}/weather-predictions/_search",
                json=query,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                es_result = response.json()
                predictions = []
                
                for hit in es_result.get("hits", {}).get("hits", []):
                    predictions.append(hit["_source"])
                
                return {"predictions": predictions, "total": len(predictions)}
            else:
                # Return mock data if Elasticsearch is not available
                return await get_mock_search_results(q, date, limit)
                
        except requests.exceptions.RequestException:
            # Return mock data if Elasticsearch is not available
            return await get_mock_search_results(q, date, limit)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

async def store_prediction(prediction: Dict[str, Any]):
    """Store prediction in Elasticsearch"""
    try:
        doc_id = f"{prediction['date']}-{prediction['hour']}"
        response = requests.put(
            f"{ELASTICSEARCH_URL}/weather-predictions/_doc/{doc_id}",
            json=prediction,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        return response.status_code in [200, 201]
    except:
        return False

async def get_mock_search_results(query: str, date: Optional[str], limit: int):
    """Return mock search results when Elasticsearch is not available"""
    mock_predictions = [
        {
            "date": "2024-07-15",
            "hour": 14,
            "time_period": "afternoon",
            "predicted_temperature": 28.5,
            "feels_like_temperature": 31.0,
            "confidence": 0.94,
            "description": "Warm afternoon temperature",
            "timestamp": "2024-07-15T14:00:00Z"
        },
        {
            "date": "2024-07-15",
            "hour": 20,
            "time_period": "evening",
            "predicted_temperature": 24.2,
            "feels_like_temperature": 26.7,
            "confidence": 0.91,
            "description": "Pleasant evening temperature",
            "timestamp": "2024-07-15T20:00:00Z"
        }
    ]
    
    # Filter by date if specified
    if date:
        mock_predictions = [p for p in mock_predictions if p["date"] == date]
    
    return {"predictions": mock_predictions[:limit], "total": len(mock_predictions)}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "NASA Weather API",
        "version": "1.0.0",
        "endpoints": ["/health", "/predict", "/search"],
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)