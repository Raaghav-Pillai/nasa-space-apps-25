# Weather Trip Planner - Frontend

Beautiful, modern frontend for weather-based trip planning with ML-powered predictions.

## 🎨 Features

- **4-Step Wizard Interface**:
  1. 📍 Location Selection (with interactive map)
  2. 👤 Activity Profile Selection (6 preset profiles + custom)
  3. 📅 Date Selection (single date/time or date range)
  4. ✓ Confirmation & Weather Report

- **Complete Weather Data**:
  - Temperature & Feels-Like
  - Precipitation
  - Humidity
  - Cloud Cover
  - Wind Speed

- **Smart Suitability Scoring**:
  - Matches weather conditions to your activity preferences
  - Color-coded scores (Green = Excellent, Yellow = Good, Red = Poor)
  - Detailed explanations

## 🚀 Quick Start

### 1. Start the Backend Server

```bash
# From project root
python backend/api_server.py
```

The API will be available at `http://localhost:8000`

### 2. Open the Frontend

Simply open `index.html` in your browser:

```bash
# Windows
start frontend_new/index.html

# Mac
open frontend_new/index.html

# Linux
xdg-open frontend_new/index.html
```

Or use a local server:

```bash
cd frontend_new
python -m http.server 3000
# Then open http://localhost:3000
```

## 📋 How to Use

1. **Select Location**: 
   - Search for a US city
   - Or click/drag the map marker
   - Default: Chicago, IL

2. **Choose Activity**:
   - Beach Day (75-90°F, sunny)
   - Hiking (55-75°F, cloudy)
   - Skiing (20-40°F, cold)
   - Rain Dancing (60-75°F, rainy)
   - Sailing (65-80°F, windy)
   - Custom (create your own!)

3. **Pick Dates**:
   - Single date with specific time
   - Or date range for multi-day forecast

4. **Get Report**:
   - View detailed weather predictions
   - See suitability scores
   - Make informed decisions!

## 🎯 Activity Profiles

### Preset Profiles

Each profile has optimized weather preferences:

- **Beach Day**: Warm & sunny (75-90°F, clear skies, low wind)
- **Hiking**: Mild & comfortable (55-75°F, some clouds OK)
- **Skiing**: Cold conditions (20-40°F, any precipitation)
- **Rain Dancing**: Rainy weather (60-75°F, rain welcome)
- **Sailing**: Windy conditions (65-80°F, moderate wind)

### Custom Profile

Create your own with:
- Temperature range (0-110°F)
- Precipitation preference
- Max wind speed (0-50 mph)
- Cloud cover preference
- Max humidity (0-100%)

## 🔧 Technical Details

### Frontend Stack
- Pure HTML/CSS/JavaScript (no build step needed!)
- Leaflet.js for interactive maps
- Responsive design
- Modern CSS animations

### Backend Integration
- FastAPI server
- Fine-tuned ML models (1.72°F accuracy)
- Real-time predictions
- 5 weather parameters

### API Endpoints

**Single Prediction**:
```
POST /predict
{
  "date": "2025-10-04",
  "hour": 14
}
```

**Range Prediction**:
```
POST /predict-range
{
  "start_date": "2025-10-04",
  "end_date": "2025-10-08"
}
```

## 🎨 Design Features

- Clean, modern UI with golden/beige color scheme
- Smooth animations and transitions
- Mobile-responsive layout
- Intuitive step-by-step flow
- Visual weather icons
- Color-coded suitability scores

## 📊 Suitability Scoring

The app calculates how well the weather matches your preferences:

- **80-100%**: ✅ Excellent (Green)
- **60-79%**: 👍 Good (Yellow)
- **40-59%**: ⚠️ Fair (Orange)
- **0-39%**: ❌ Poor (Red)

Factors considered:
- Temperature match
- Precipitation levels
- Wind speed
- Humidity levels

## 🌐 Browser Support

Works on all modern browsers:
- Chrome/Edge (recommended)
- Firefox
- Safari
- Opera

## 📝 Notes

- Backend must be running for predictions to work
- Uses OpenStreetMap for location search
- All predictions use fine-tuned ML models
- Temperatures displayed in both Fahrenheit and Celsius

## 🎉 Ready to Use!

Your weather trip planner is ready! Just start the backend server and open the frontend in your browser.

Perfect for hackathon demos! 🚀
