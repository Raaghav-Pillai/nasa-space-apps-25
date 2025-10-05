"""
Simple API server for the frontend
Connects to the prediction models
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sys
import os

# Add prediction module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'prediction'))

from predict_simple import predict_hourly, predict_daily_range

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

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Weather Prediction API Server...")
    print("📍 Server running at: http://localhost:8000")
    print("📖 API docs at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
