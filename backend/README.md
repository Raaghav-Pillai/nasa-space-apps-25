# Backend API

Flask backend for weather prediction and recommendations.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### POST /api/report
Generates weather report and recommendations based on location, profile, and dates.

**Request Body:**
```json
{
  "location": {
    "city": "Chicago",
    "region": "IL",
    "coordinates": { "lat": 41.8781, "lng": -87.6298 }
  },
  "profile": {
    "name": "Outdoor Enthusiast",
    "temperature": [60, 80],
    "precip": "Low",
    "windMaxMph": 15,
    "clouds": "Partly Cloudy",
    "minAQI": 50,
    "maxHumidity": 70
  },
  "dates": {
    "startDate": "2025-10-15",
    "endDate": "2025-10-20",
    "startTime": "08:00:00",
    "endTime": "18:00:00"
  }
}
```

**Response:**
```json
{
  "success": true,
  "weather": { ... },
  "recommendation": { ... },
  "message": "Report generated successfully"
}
```
