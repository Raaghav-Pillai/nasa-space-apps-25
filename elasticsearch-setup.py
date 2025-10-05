#!/usr/bin/env python3
"""
Quick Elasticsearch setup for hackathon
"""

from elasticsearch import Elasticsearch
import json
import os
from datetime import datetime

# Elasticsearch configuration
ES_HOST = os.environ.get('ELASTICSEARCH_HOST', 'localhost:9200')
ES_USERNAME = os.environ.get('ELASTICSEARCH_USERNAME', 'elastic')
ES_PASSWORD = os.environ.get('ELASTICSEARCH_PASSWORD', 'changeme')

def setup_elasticsearch():
    """Setup Elasticsearch indices and mappings"""
    
    # Connect to Elasticsearch
    es = Elasticsearch(
        [ES_HOST],
        basic_auth=(ES_USERNAME, ES_PASSWORD),
        verify_certs=False
    )
    
    # Test connection
    if not es.ping():
        print("❌ Cannot connect to Elasticsearch")
        return False
    
    print("✅ Connected to Elasticsearch")
    
    # Create weather predictions index
    weather_mapping = {
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "date": {"type": "date", "format": "yyyy-MM-dd"},
                "hour": {"type": "integer"},
                "temperature": {"type": "float"},
                "feels_like": {"type": "float"},
                "time_period": {"type": "keyword"},
                "location": {"type": "geo_point"},
                "cloud_cover_day": {"type": "float"},
                "cloud_cover_night": {"type": "float"},
                "lst_day": {"type": "float"},
                "lst_night": {"type": "float"},
                "prediction_confidence": {"type": "float"},
                "model_version": {"type": "keyword"},
                "timestamp": {"type": "date"},
                "description": {"type": "text"}
            }
        },
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        }
    }
    
    # Create index
    index_name = "weather-predictions"
    if es.indices.exists(index=index_name):
        print(f"Index {index_name} already exists, deleting...")
        es.indices.delete(index=index_name)
    
    es.indices.create(index=index_name, body=weather_mapping)
    print(f"✅ Created index: {index_name}")
    
    # Create historical data index
    historical_mapping = {
        "mappings": {
            "properties": {
                "date": {"type": "date"},
                "location": {"type": "geo_point"},
                "temperature_actual": {"type": "float"},
                "temperature_predicted": {"type": "float"},
                "accuracy": {"type": "float"},
                "weather_conditions": {"type": "keyword"},
                "satellite_data": {"type": "object"}
            }
        }
    }
    
    historical_index = "weather-historical"
    if es.indices.exists(index=historical_index):
        es.indices.delete(index=historical_index)
    
    es.indices.create(index=historical_index, body=historical_mapping)
    print(f"✅ Created index: {historical_index}")
    
    # Insert sample data for testing
    sample_predictions = [
        {
            "id": "2024-01-15-12",
            "date": "2024-01-15",
            "hour": 12,
            "temperature": 25.5,
            "feels_like": 27.2,
            "time_period": "afternoon",
            "location": {"lat": 40.7128, "lon": -74.0060},
            "prediction_confidence": 0.95,
            "timestamp": datetime.utcnow().isoformat(),
            "description": "Warm afternoon with clear skies"
        },
        {
            "id": "2024-01-15-18",
            "date": "2024-01-15",
            "hour": 18,
            "temperature": 22.1,
            "feels_like": 23.8,
            "time_period": "evening",
            "location": {"lat": 40.7128, "lon": -74.0060},
            "prediction_confidence": 0.92,
            "timestamp": datetime.utcnow().isoformat(),
            "description": "Pleasant evening temperature"
        }
    ]
    
    # Bulk insert sample data
    for doc in sample_predictions:
        es.index(index=index_name, id=doc['id'], body=doc)
    
    print(f"✅ Inserted {len(sample_predictions)} sample predictions")
    
    # Create search templates
    search_template = {
        "script": {
            "lang": "mustache",
            "source": {
                "query": {
                    "bool": {
                        "must": [
                            {"range": {"date": {"gte": "{{start_date}}", "lte": "{{end_date}}"}}},
                            {"match": {"description": "{{search_term}}"}}
                        ]
                    }
                },
                "sort": [{"timestamp": {"order": "desc"}}],
                "size": "{{size}}"
            }
        }
    }
    
    es.put_script(id="weather_search_template", body=search_template)
    print("✅ Created search template")
    
    return True

if __name__ == "__main__":
    print("🔍 Setting up Elasticsearch for NASA Weather App...")
    
    if setup_elasticsearch():
        print("🎉 Elasticsearch setup complete!")
        print("\nNext steps:")
        print("1. Update your Azure Function with Elasticsearch credentials")
        print("2. Deploy your functions to Azure")
        print("3. Test the search functionality")
    else:
        print("❌ Setup failed. Check your Elasticsearch connection.")