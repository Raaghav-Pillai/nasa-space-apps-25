import sys
sys.path.insert(0, 'backend/prediction')
from predict_simple import predict_daily_range
from elasticsearch import Elasticsearch
import pandas as pd
from datetime import datetime, timedelta

# Elasticsearch configuration
ES_HOST = input("Enter Elasticsearch URL (e.g., https://your-deployment.es.io:9243): ")
ES_USERNAME = input("Enter Elasticsearch username (default: elastic): ") or "elastic"
ES_PASSWORD = input("Enter Elasticsearch password: ")

# Connect to Elasticsearch
es = Elasticsearch(
    [ES_HOST],
    basic_auth=(ES_USERNAME, ES_PASSWORD),
    verify_certs=True
)

print("Testing connection...")
if es.ping():
    print("âœ… Connected to Elasticsearch!")
else:
    print("âŒ Connection failed")
    exit(1)

# Create index
index_name = "weather-predictions"
mapping = {
    "mappings": {
        "properties": {
            "date": {"type": "date"},
            "location": {"type": "geo_point"},
            "avg_temperature_f": {"type": "float"},
            "avg_feels_like_f": {"type": "float"},
            "total_precipitation_mm": {"type": "float"},
            "avg_humidity_percent": {"type": "float"},
            "avg_cloud_cover_percent": {"type": "float"},
            "avg_wind_speed_mph": {"type": "float"},
            "timestamp": {"type": "date"}
        }
    }
}

if es.indices.exists(index=index_name):
    print(f"Deleting existing index: {index_name}")
    es.indices.delete(index=index_name)

es.indices.create(index=index_name, body=mapping)
print(f"âœ… Created index: {index_name}")

# Generate and index predictions
print("\nGenerating predictions for next 30 days...")
start_date = datetime.now().strftime('%Y-%m-%d')
end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')

df = predict_daily_range(start_date, end_date)

# Index data
for idx, row in df.iterrows():
    doc = {
        "date": row['date'],
        "location": {"lat": 41.8781, "lon": -87.6298},
        "avg_temperature_f": float(row['avg_temperature_f']),
        "avg_feels_like_f": float(row['avg_feels_like_f']),
        "total_precipitation_mm": float(row['total_precipitation_mm']),
        "avg_humidity_percent": float(row['avg_humidity_percent']),
        "avg_cloud_cover_percent": float(row['avg_cloud_cover_percent']),
        "avg_wind_speed_mph": float(row['avg_wind_speed_mph']),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    es.index(index=index_name, id=row['date'], body=doc)
    print(f"Indexed: {row['date']}")

print(f"\nâœ… Indexed {len(df)} predictions to Elasticsearch!")
print(f"\nYou can now search your data at: {ES_HOST}")
