"""
Complete Elasticsearch Setup
1. Creates indices
2. Indexes all weather predictions
3. Enables search functionality

Run this after signing up for Elastic Cloud at https://cloud.elastic.co
"""

import sys
sys.path.insert(0, 'backend/prediction')

from predict_simple import predict_daily_range
from elasticsearch import Elasticsearch
import pandas as pd
from datetime import datetime, timedelta
import json

print("="*70)
print("ELASTICSEARCH SETUP FOR WEATHER APP")
print("="*70)

# Get Elasticsearch credentials
print("\nSign up at https://cloud.elastic.co for a free 14-day trial")
print("After creating a deployment, you'll get connection details\n")

ES_HOST = input("Enter Elasticsearch Cloud ID or URL: ").strip()
ES_USERNAME = input("Enter username (default: elastic): ").strip() or "elastic"
ES_PASSWORD = input("Enter password: ").strip()

# Connect
print("\nConnecting to Elasticsearch...")

if "cloud.es.io" in ES_HOST or ":" not in ES_HOST:
    # Cloud ID format
    es = Elasticsearch(
        cloud_id=ES_HOST,
        basic_auth=(ES_USERNAME, ES_PASSWORD)
    )
else:
    # URL format
    es = Elasticsearch(
        [ES_HOST],
        basic_auth=(ES_USERNAME, ES_PASSWORD),
        verify_certs=True
    )

if not es.ping():
    print("❌ Connection failed! Check your credentials.")
    exit(1)

print("✅ Connected to Elasticsearch!")

# Create index
index_name = "weather-predictions"

mapping = {
    "mappings": {
        "properties": {
            "date": {"type": "date", "format": "yyyy-MM-dd"},
            "location_name": {"type": "text"},
            "location": {"type": "geo_point"},
            "avg_temperature_f": {"type": "float"},
            "avg_temperature_c": {"type": "float"},
            "avg_feels_like_f": {"type": "float"},
            "avg_feels_like_c": {"type": "float"},
            "total_precipitation_mm": {"type": "float"},
            "total_precipitation_inches": {"type": "float"},
            "avg_humidity_percent": {"type": "float"},
            "avg_cloud_cover_percent": {"type": "float"},
            "avg_wind_speed_mph": {"type": "float"},
            "avg_wind_speed_ms": {"type": "float"},
            "min_temp_f": {"type": "float"},
            "max_temp_f": {"type": "float"},
            "timestamp": {"type": "date"}
        }
    },
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 1
    }
}

print(f"\nCreating index: {index_name}")

if es.indices.exists(index=index_name):
    print(f"Index already exists. Deleting...")
    es.indices.delete(index=index_name)

es.indices.create(index=index_name, body=mapping)
print(f"✅ Index created!")

# Generate predictions for next 90 days
print("\nGenerating weather predictions...")
start_date = datetime.now().strftime('%Y-%m-%d')
end_date = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')

print(f"Date range: {start_date} to {end_date}")

df = predict_daily_range(start_date, end_date)

print(f"✅ Generated {len(df)} predictions")

# Index to Elasticsearch
print("\nIndexing to Elasticsearch...")

indexed_count = 0
for idx, row in df.iterrows():
    doc = {
        "date": row['date'],
        "location_name": "Chicago, IL",
        "location": {"lat": 41.8781, "lon": -87.6298},
        "avg_temperature_f": float(row['avg_temperature_f']),
        "avg_temperature_c": float(row['avg_temperature_c']),
        "avg_feels_like_f": float(row['avg_feels_like_f']),
        "avg_feels_like_c": float(row['avg_feels_like_c']),
        "total_precipitation_mm": float(row['total_precipitation_mm']),
        "total_precipitation_inches": float(row['total_precipitation_inches']),
        "avg_humidity_percent": float(row['avg_humidity_percent']),
        "avg_cloud_cover_percent": float(row['avg_cloud_cover_percent']),
        "avg_wind_speed_mph": float(row['avg_wind_speed_mph']),
        "avg_wind_speed_ms": float(row['avg_wind_speed_ms']),
        "min_temp_f": float(row['min_temp_f']),
        "max_temp_f": float(row['max_temp_f']),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    es.index(index=index_name, id=row['date'], document=doc)
    indexed_count += 1
    
    if indexed_count % 10 == 0:
        print(f"  Indexed {indexed_count}/{len(df)} documents...")

print(f"\n✅ Successfully indexed {indexed_count} predictions!")

# Create a search template
print("\nCreating search template...")

search_template = {
    "script": {
        "lang": "mustache",
        "source": json.dumps({
            "query": {
                "bool": {
                    "must": [
                        {"range": {"date": {"gte": "{{start_date}}", "lte": "{{end_date}}"}}},
                        {"range": {"avg_temperature_f": {"gte": "{{min_temp}}", "lte": "{{max_temp}}"}}}
                    ]
                }
            },
            "sort": [{"date": {"order": "asc"}}],
            "size": 100
        })
    }
}

es.put_script(id="weather_search", body=search_template)
print("✅ Search template created!")

# Test search
print("\nTesting search...")
test_query = {
    "query": {
        "range": {
            "avg_temperature_f": {"gte": 60, "lte": 80}
        }
    },
    "size": 5
}

results = es.search(index=index_name, body=test_query)
print(f"✅ Found {results['hits']['total']['value']} days with temperature 60-80°F")

print("\n" + "="*70)
print("ELASTICSEARCH SETUP COMPLETE!")
print("="*70)

print(f"\nYour data is now in Elasticsearch!")
print(f"Index: {index_name}")
print(f"Documents: {indexed_count}")
print(f"\nYou can now:")
print("1. Search weather data by date range")
print("2. Filter by temperature, precipitation, etc.")
print("3. Visualize in Kibana")
print("4. Use in your application")

# Save connection info
config = {
    "elasticsearch_host": ES_HOST,
    "index_name": index_name,
    "documents_indexed": indexed_count,
    "date_range": f"{start_date} to {end_date}"
}

with open('elasticsearch_config.json', 'w') as f:
    json.dump(config, f, indent=2)

print("\n💾 Configuration saved to elasticsearch_config.json")
print("\n🎉 All done! Your weather data is in Elasticsearch!")
