import azure.functions as func
import json
import logging
import os
from datetime import datetime
import joblib
import pandas as pd
from azure.storage.blob import BlobServiceClient
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

app = func.FunctionApp()

# Initialize Azure services
def get_blob_client():
    connection_string = os.environ.get('AzureWebJobsStorage')
    return BlobServiceClient.from_connection_string(connection_string)

def get_search_client():
    endpoint = os.environ.get('SEARCH_ENDPOINT')
    key = os.environ.get('SEARCH_KEY')
    if endpoint and key:
        return SearchClient(endpoint=endpoint, index_name="weather-predictions", credential=AzureKeyCredential(key))
    return None

@app.route(route="predict", methods=["POST"])
def predict_temperature(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Temperature prediction request received.')
    
    try:
        # Parse request
        req_body = req.get_json()
        date_str = req_body.get('date')
        hour = req_body.get('hour', 12)
        
        # Load model from blob storage (simplified for hackathon)
        # In production, cache this
        model_data = {
            'feels_like_temperature': 25.5 + (hour - 12) * 0.5,  # Mock prediction
            'description': f'Predicted temperature for {date_str} at hour {hour}',
            'time_period': get_time_period(hour),
            'confidence': 0.95
        }
        
        # Store prediction in search index
        search_client = get_search_client()
        if search_client:
            document = {
                'id': f"{date_str}-{hour}",
                'date': date_str,
                'hour': hour,
                'temperature': model_data['feels_like_temperature'],
                'time_period': model_data['time_period'],
                'timestamp': datetime.utcnow().isoformat()
            }
            search_client.upload_documents([document])
        
        return func.HttpResponse(
            json.dumps(model_data),
            status_code=200,
            headers={'Content-Type': 'application/json'}
        )
        
    except Exception as e:
        logging.error(f'Error in prediction: {str(e)}')
        return func.HttpResponse(
            json.dumps({'error': str(e)}),
            status_code=500,
            headers={'Content-Type': 'application/json'}
        )

@app.route(route="search", methods=["GET"])
def search_predictions(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Search request received.')
    
    try:
        query = req.params.get('q', '*')
        date_filter = req.params.get('date')
        
        search_client = get_search_client()
        if not search_client:
            return func.HttpResponse(
                json.dumps({'error': 'Search service not configured'}),
                status_code=500
            )
        
        # Build search parameters
        search_params = {
            'search_text': query,
            'top': 50,
            'order_by': ['timestamp desc']
        }
        
        if date_filter:
            search_params['filter'] = f"date eq '{date_filter}'"
        
        results = search_client.search(**search_params)
        
        # Convert results to list
        predictions = []
        for result in results:
            predictions.append({
                'date': result['date'],
                'hour': result['hour'],
                'temperature': result['temperature'],
                'time_period': result['time_period'],
                'timestamp': result['timestamp']
            })
        
        return func.HttpResponse(
            json.dumps({'predictions': predictions}),
            status_code=200,
            headers={'Content-Type': 'application/json'}
        )
        
    except Exception as e:
        logging.error(f'Error in search: {str(e)}')
        return func.HttpResponse(
            json.dumps({'error': str(e)}),
            status_code=500
        )

@app.route(route="health", methods=["GET"])
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
        json.dumps({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}),
        status_code=200,
        headers={'Content-Type': 'application/json'}
    )

def get_time_period(hour):
    if 6 <= hour < 12:
        return 'morning'
    elif 12 <= hour < 18:
        return 'afternoon'
    elif 18 <= hour < 21:
        return 'evening'
    else:
        return 'night'