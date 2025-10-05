"""
Azure Functions wrapper for the Weather Prediction API
"""

import azure.functions as func
import json
import sys
import os
from pathlib import Path

# Add prediction module to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / 'prediction'))

from predict_simple import predict_hourly, predict_daily_range

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="health", methods=["GET"])
def health(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
        json.dumps({"status": "healthy"}),
        mimetype="application/json"
    )

@app.route(route="predict", methods=["POST"])
def predict(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        date_str = req_body.get('date')
        hour = req_body.get('hour', 12)
        
        result = predict_hourly(date_str, hour)
        
        return func.HttpResponse(
            json.dumps(result, default=str),
            mimetype="application/json"
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="predict-range", methods=["POST"])
def predict_range(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        start_date = req_body.get('start_date')
        end_date = req_body.get('end_date')
        
        df = predict_daily_range(start_date, end_date)
        results = df.to_dict('records')
        
        return func.HttpResponse(
            json.dumps(results, default=str),
            mimetype="application/json"
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
