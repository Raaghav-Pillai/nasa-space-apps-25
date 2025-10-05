# Weather Prediction Models

Complete suite of weather prediction models using MODIS satellite data and Daymet weather observations.

## Models Included

1. **Temperature (Feels-Like)** - Predicts feels-like temperature based on time of day, cloud cover, and solar radiation
2. **Precipitation** - Predicts precipitation amount (mm) and probability
3. **Humidity** - Predicts relative humidity percentage
4. **Cloud Cover** - Predicts cloud cover percentage
5. **Wind Speed** - Predicts wind speed (m/s)

## Quick Start

### Single Weather Prediction

```python
from weather_predictor import WeatherPredictor

# Initialize predictor (loads all models)
predictor = WeatherPredictor()

# Get forecast for specific date and hour
forecast = predictor.predict('2024-12-15', hour=14)

# Output:
# Temperature:     -11.6°C (feels like)
# Precipitation:  6.4mm (93% probability)
# Humidity:       26%
# Cloud Cover:    80%
# Wind Speed:     2.6 m/s
```

### Multi-Day Forecast

```python
# Get 5-day forecast
df = predictor.predict_range('2024-12-15', '2024-12-19', hour=14)
print(df)
```

## Model Performance

### Temperature Model
- **MAE**: 5.44°C (feels-like temperature)
- **R²**: 0.9975 (base temperature)
- **Key Features**: LST_Day (80.7%), LST_Night (19.0%)

### Precipitation Model
- **MAE**: 5.40 mm/day
- **R²**: -0.50 (challenging variable)
- **Key Features**: day_of_year (47.6%), EVI (18.7%)

### Humidity Model
- **MAE**: 159.70 Pa (vapor pressure)
- **R²**: 0.8839
- **Key Features**: season (43.1%), day_of_year (42.1%)

### Cloud Cover Model
- **MAE**: 11.59%
- **R²**: 0.6522
- **Key Features**: day_of_year (34.6%), NDVI (22.1%), Clear_day_cov (20.5%)

### Wind Model
- **MAE**: 5.08 (wind proxy)
- **R²**: 0.3652
- **Key Features**: LST_Day (35.3%), LST_Night (21.8%)

## Individual Model Usage

### Temperature Only

```python
from temperature.temperature_prediction_model import TemperaturePredictionModel
import pickle

# Load model
with open('backend/data/Modis/temperature_model_fixed.pkl', 'rb') as f:
    model_data = pickle.load(f)

model = TemperaturePredictionModel()
model.model = model_data['model']
model.scaler = model_data['scaler']
model.feature_names = model_data['feature_names']

# Predict
result = model.predict_feels_like_temperature(
    date_str='2024-12-15',
    hour=14,
    lst_day=273.0,
    lst_night=265.0,
    cloud_cover_day=0.7,
    cloud_cover_night=0.6
)

print(f"Feels like: {result['feels_like_temperature']}°C")
```

### Precipitation Only

```python
import pickle

# Load model
with open('backend/data/Modis/precipitation_model.pkl', 'rb') as f:
    precip_model = pickle.load(f)

# Make prediction (requires building feature vector)
# See weather_predictor.py for full implementation
```

## Data Sources

### MODIS Satellite Data
- **MOD09GA**: Surface reflectance, solar angles
- **MOD10A1**: Snow cover and albedo
- **MOD11A1**: Land surface temperature, cloud cover
- **MOD13A1**: Vegetation indices (NDVI, EVI)
- **MOD16A2**: Evapotranspiration

### Daymet Weather Data
- Daily precipitation (mm)
- Temperature (min/max)
- Vapor pressure (humidity indicator)
- Solar radiation

## Model Training

To retrain models:

```bash
# Train temperature model
cd backend/prediction/temperature
python temperature_prediction_model.py

# Train precipitation model
cd backend/prediction/precipitation
python precipitation_prediction_model.py

# Train humidity, cloud, and wind models
cd backend/prediction
python train_all_models.py
```

## Validation

Validate all models against real 2025 weather data:

```bash
cd backend/prediction
python validate_all_models_2025.py
```

This fetches real weather data from Open-Meteo API and compares predictions.

## File Structure

```
backend/prediction/
├── weather_predictor.py          # Unified prediction interface
├── train_all_models.py            # Train humidity, cloud, wind models
├── validate_all_models_2025.py   # Validation script
├── temperature/
│   ├── temperature_prediction_model.py
│   └── validate_model_2025.py
└── precipitation/
    └── precipitation_prediction_model.py
```

## Model Files

All trained models are saved in `backend/data/Modis/`:
- `temperature_model_fixed.pkl` - Temperature prediction model
- `precipitation_model.pkl` - Precipitation prediction model
- `humidity_model.pkl` - Humidity prediction model
- `cloud_model.pkl` - Cloud cover prediction model
- `wind_model.pkl` - Wind speed prediction model

## Weight Adjustments

### Temperature (Feels-Like)
Weights have been tuned based on real 2025 data validation:

- **Afternoon**: +2.5°C adjustment (strongest solar heating)
- **Morning**: -1.0°C adjustment (cooling from night)
- **Evening**: +0.8°C adjustment (residual heat)
- **Night**: -1.5°C adjustment (coldest period)

Cloud effects:
- Daytime: Up to -0.5°C per cloud factor
- Nighttime: Up to +1.0°C (clouds trap heat)

### Precipitation
Time-of-day factors:
- Morning (5-8am): 1.1x multiplier
- Afternoon (3-6pm): 1.2x multiplier (storm peak)
- Night (9pm-3am): 0.9x multiplier

### Other Models
Humidity, cloud cover, and wind use default model predictions with minimal post-processing.

## Limitations

1. **Missing MODIS Data**: Some dates lack satellite coverage, leading to higher errors
2. **Proxy Variables**: Wind and precipitation use proxy calculations rather than direct measurements
3. **Limited Training Data**: Only ~367 days of overlapping MODIS+Daymet data
4. **Geographic Specificity**: Models trained on Chicago data only

## Future Improvements

1. Incorporate actual wind speed measurements from weather stations
2. Add more training data (multiple years, multiple locations)
3. Include additional features (pressure, dew point)
4. Ensemble methods combining multiple models
5. Real-time satellite data integration

## API Reference

### WeatherPredictor

#### `__init__(models_dir=None)`
Initialize the unified weather predictor.

#### `predict(date_str, hour=12, verbose=True)`
Predict all weather variables for a specific date and hour.

**Parameters:**
- `date_str` (str): Date in 'YYYY-MM-DD' format
- `hour` (int): Hour of day (0-23)
- `verbose` (bool): Print detailed output

**Returns:**
- dict with keys: date, hour, temperature_c, feels_like_c, precipitation_mm, precipitation_probability_pct, humidity_pct, cloud_cover_pct, wind_speed_ms

#### `predict_range(start_date, end_date, hour=12)`
Predict for a range of dates.

**Returns:**
- pandas DataFrame with predictions for each date

## License

Created for NASA Space Apps Challenge 2025.

## Authors

Claude Code - AI Assistant
