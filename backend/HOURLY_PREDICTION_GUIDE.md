# Hourly "Feels Like" Temperature Prediction Guide

## Overview
The temperature prediction model can predict "feels like" temperature for any date and hour (0-23), accounting for:
- Time of day (morning, afternoon, evening, night)
- Cloud cover conditions
- Day/night temperature variations
- Solar positioning

## Quick Start

### Option 1: Run Demo
```bash
cd backend/prediction/temperature
python predict_hourly_temperature.py --demo
```

### Option 2: Predict for Specific Date
```bash
cd backend/prediction/temperature
python predict_hourly_temperature.py --date 2024-07-15
```

### Option 3: Predict for Specific Date and Hour
```bash
cd backend/prediction/temperature
python predict_hourly_temperature.py --date 2024-07-15 --hour 14
```

## Using in Your Code

```python
import joblib

# Load the trained model
model = joblib.load('backend/data/Modis/temperature_model.pkl')

# Predict for a specific hour
result = model.predict_feels_like_temperature(
    date_str='2024-07-15',
    hour=14,  # 2 PM
    # Optional: Provide actual satellite data
    lst_day=303.15,  # 30°C in Kelvin
    lst_night=293.15,  # 20°C in Kelvin
    cloud_cover_day=0.9,  # 90% clear (10% clouds)
    cloud_cover_night=0.8
)

print(f"Feels Like: {result['feels_like_temperature']}°C")
print(f"Description: {result['description']}")
```

## Time Periods and Weights

The model adjusts predictions based on time of day:

| Hours | Period | Day Weight | Night Weight |
|-------|--------|------------|--------------|
| 06-12 | Morning | 70% | 30% |
| 12-18 | Afternoon | 100% | 0% |
| 18-21 | Evening | 40% | 60% |
| 21-06 | Night | 0% | 100% |

## Input Parameters

### Required:
- `date_str`: Date in 'YYYY-MM-DD' format
- `hour`: Hour of day (0-23)

### Optional (uses defaults if not provided):
- `lst_day`: Land Surface Temperature Day (Kelvin) - default: 288.0K (15°C)
- `lst_night`: Land Surface Temperature Night (Kelvin) - default: 280.0K (7°C)
- `cloud_cover_day`: Clear day coverage 0-1 - default: 0.5
- `cloud_cover_night`: Clear night coverage 0-1 - default: 0.5
- `sur_refl_bands`: List of 7 surface reflectance values
- `solar_azimuth`: Solar azimuth angle
- `solar_zenith`: Solar zenith angle
- `emis_31`: Emissivity band 31
- `emis_32`: Emissivity band 32

## Output

The function returns a dictionary with:
- `date`: Input date
- `hour`: Input hour
- `time_period`: morning/afternoon/evening/night
- `predicted_temperature`: Base temperature prediction (°C)
- `feels_like_temperature`: Adjusted "feels like" temperature (°C)
- `lst_day_celsius`: Day temperature in Celsius
- `lst_night_celsius`: Night temperature in Celsius
- `cloud_cover_day`: Day cloud cover
- `cloud_cover_night`: Night cloud cover
- `time_weight_day`: Weight given to day temperature
- `time_weight_night`: Weight given to night temperature
- `description`: Human-readable description (e.g., "Warm afternoon")

## Example Output

```
Time Period: AFTERNOON
Predicted Temperature: 25.13°C
Feels Like Temperature: 29.94°C
Description: Warm afternoon

Details:
  - Day LST: 30.0°C
  - Night LST: 20.0°C
  - Cloud Cover (Day): 90.00%
  - Cloud Cover (Night): 80.00%
  - Day Weight: 100.0%
  - Night Weight: 0.0%
```

## Temperature Descriptions

| Temperature Range | Description |
|-------------------|-------------|
| < 0°C | Freezing |
| 0-10°C | Cold |
| 10-20°C | Cool |
| 20-25°C | Comfortable |
| 25-30°C | Warm |
| > 30°C | Hot |

## Model Performance

- **RMSE**: 0.57°C
- **MAE**: 0.33°C
- **R²**: 0.9975 (99.75% accuracy)

## Files

- **Model**: `backend/data/Modis/temperature_model.pkl`
- **Training Script**: `backend/prediction/temperature/temperature_prediction_model.py`
- **Prediction Script**: `backend/prediction/temperature/predict_hourly_temperature.py`
- **Feature Importance**: `backend/data/Modis/feature_importance.csv`
