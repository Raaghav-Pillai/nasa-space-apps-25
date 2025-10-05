"""
SIMPLIFIED WEATHER PREDICTION SYSTEM
Works without MODIS CSV files by using synthetic features

Usage:
    from backend.prediction.predict_simple import predict_hourly, predict_daily_range

    # Single hour
    weather = predict_hourly('2025-02-15', 14)
    print(weather)

    # Date range (daily averages)
    forecast = predict_daily_range('2025-02-15', '2025-02-20')
    print(forecast)

Author: Kiro AI
Date: 2025-10-04
"""

import os
import pandas as pd
import numpy as np
import pickle
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Paths
if os.path.basename(os.getcwd()) == 'prediction':
    DATA_DIR = '../data'
else:
    DATA_DIR = 'backend/data'
MODELS_DIR = os.path.join(DATA_DIR, 'Modis')

# Global cache
_MODELS = None

def celsius_to_fahrenheit(c):
    """Convert Celsius to Fahrenheit"""
    return (c * 9/5) + 32

def _load_models():
    """Load all weather prediction models (cached)"""
    global _MODELS
    
    if _MODELS is None:
        print("Loading all weather models...")
        _MODELS = {}
        
        # Load all models
        model_names = ['temperature', 'precipitation', 'humidity', 'cloud', 'wind']
        
        for name in model_names:
            # Try fine-tuned first for temperature
            if name == 'temperature':
                model_path = os.path.join(MODELS_DIR, 'temperature_model_finetuned.pkl')
                if not os.path.exists(model_path):
                    model_path = os.path.join(MODELS_DIR, 'temperature_model_full.pkl')
            else:
                model_path = os.path.join(MODELS_DIR, f'{name}_model_full.pkl')
            
            try:
                with open(model_path, 'rb') as f:
                    _MODELS[name] = pickle.load(f)
                print(f"  ✅ {name.capitalize()} model loaded")
            except Exception as e:
                print(f"  ⚠️  {name.capitalize()} model not found: {e}")
                _MODELS[name] = None
        
        print(f"✅ Loaded {len([m for m in _MODELS.values() if m is not None])} models")
    
    return _MODELS

def _generate_features(date_str, feature_names):
    """Generate synthetic MODIS features based on date"""
    date_obj = pd.to_datetime(date_str)
    month = date_obj.month
    day_of_year = date_obj.dayofyear
    season = (month % 12 + 3) // 3
    
    # Seasonal patterns for Chicago
    if season == 1:  # Winter (Dec-Feb)
        lst_day_base = 273.15 - 5
        lst_night_base = 273.15 - 10
        clear_cov = 0.4
        snow_cover = 0.3
        et = 50
        le = 100
        evi = 0.2
        ndvi = 0.3
        pet = 80
    elif season == 2:  # Spring (Mar-May)
        lst_day_base = 273.15 + 10
        lst_night_base = 273.15 + 5
        clear_cov = 0.6
        snow_cover = 0.05
        et = 150
        le = 300
        evi = 0.5
        ndvi = 0.6
        pet = 200
    elif season == 3:  # Summer (Jun-Aug)
        lst_day_base = 273.15 + 25
        lst_night_base = 273.15 + 18
        clear_cov = 0.7
        snow_cover = 0.0
        et = 250
        le = 500
        evi = 0.7
        ndvi = 0.8
        pet = 350
    else:  # Fall (Sep-Nov)
        lst_day_base = 273.15 + 12
        lst_night_base = 273.15 + 7
        clear_cov = 0.5
        snow_cover = 0.1
        et = 100
        le = 200
        evi = 0.4
        ndvi = 0.5
        pet = 150
    
    # Add daily variation
    daily_var = np.sin(2 * np.pi * day_of_year / 365) * 5
    lst_day = lst_day_base + daily_var
    lst_night = lst_night_base + daily_var
    
    # Solar angles
    solar_zenith = 45 + 20 * np.cos(2 * np.pi * day_of_year / 365)
    solar_azimuth = 180
    sensor_azimuth = 180
    sensor_zenith = 45
    
    # Surface reflectance
    sur_refl = [0.15, 0.20, 0.10, 0.15, 0.18, 0.12, 0.08]
    
    # Emissivity
    emis = [0.985, 0.985]
    
    # Snow albedo
    snow_albedo = snow_cover * 0.8
    
    # Build comprehensive feature dict
    features = {
        # MOD09GA features
        'MOD09GA_061_sur_refl_b01_1': sur_refl[0],
        'MOD09GA_061_sur_refl_b02_1': sur_refl[1],
        'MOD09GA_061_sur_refl_b03_1': sur_refl[2],
        'MOD09GA_061_sur_refl_b04_1': sur_refl[3],
        'MOD09GA_061_sur_refl_b05_1': sur_refl[4],
        'MOD09GA_061_sur_refl_b06_1': sur_refl[5],
        'MOD09GA_061_sur_refl_b07_1': sur_refl[6],
        'MOD09GA_061_SolarAzimuth_1': solar_azimuth,
        'MOD09GA_061_SolarZenith_1': solar_zenith,
        'MOD09GA_061_SensorAzimuth_1': sensor_azimuth,
        'MOD09GA_061_SensorZenith_1': sensor_zenith,
        'MOD09GA_061_Range_1': 1000,
        'MOD09GA_061_iobs_res_1': 500,
        
        # MOD11A1 features
        'MOD11A1_061_LST_Day_1km': lst_day,
        'MOD11A1_061_LST_Night_1km': lst_night,
        'MOD11A1_061_Emis_31': emis[0],
        'MOD11A1_061_Emis_32': emis[1],
        'MOD11A1_061_Clear_day_cov': clear_cov,
        'MOD11A1_061_Clear_night_cov': clear_cov,
        
        # MOD10A1 features (snow)
        'MOD10A1_061_NDSI_Snow_Cover': snow_cover,
        'MOD10A1_061_Snow_Albedo_Daily_Tile': snow_albedo,
        'MOD10A1_061_NDSI_Snow_Cover_Algorithm_Flags_QA': 0,
        
        # MOD13A1 features (vegetation)
        'MOD13A1_061__500m_16_days_NDVI': ndvi,
        'MOD13A1_061__500m_16_days_EVI': evi,
        'MOD13A1_061__500m_16_days_VI_Quality': 0,
        
        # MOD16A2 features (evapotranspiration)
        'MOD16A2_061_ET_500m': et,
        'MOD16A2_061_LE_500m': le,
        'MOD16A2_061_PET_500m': pet,
        
        # Temporal features
        'month': month,
        'day_of_year': day_of_year,
        'season': season
    }
    
    # Return only the features needed by this model
    return pd.DataFrame([features])[[f for f in feature_names if f in features]]

def predict_hourly(date_str, hour):
    """
    Predict weather for a specific date and hour.

    Args:
        date_str (str): Date in 'YYYY-MM-DD' format
        hour (int): Hour of day (0-23)

    Returns:
        dict: Weather predictions with keys:
            - date (str)
            - hour (int)
            - temperature_f (float): Temperature in Fahrenheit
            - feels_like_f (float): Feels-like temperature in Fahrenheit
            - temperature_c (float): Temperature in Celsius
            - feels_like_c (float): Feels-like temperature in Celsius
            - precipitation_mm (float): Precipitation in mm
            - precipitation_inches (float): Precipitation in inches
            - humidity_percent (float): Relative humidity %
            - cloud_cover_percent (float): Cloud cover %
            - wind_speed_mph (float): Wind speed in mph
            - wind_speed_ms (float): Wind speed in m/s
            - time_period (str): morning/afternoon/evening/night
            - description (str): Human-readable description
    """
    models = _load_models()
    
    # ===== TEMPERATURE =====
    temp_model = models['temperature']
    X_temp = _generate_features(date_str, temp_model['feature_names'])
    X_temp_scaled = temp_model['scaler'].transform(X_temp)
    temp_c = temp_model['model'].predict(X_temp_scaled)[0]
    temp_f = celsius_to_fahrenheit(temp_c)
    
    # Time-based feels-like adjustment
    if 6 <= hour < 12:
        time_period = "morning"
        feels_like_adjustment = -1.0
    elif 12 <= hour < 18:
        time_period = "afternoon"
        feels_like_adjustment = 3.0
    elif 18 <= hour < 21:
        time_period = "evening"
        feels_like_adjustment = 1.0
    else:
        time_period = "night"
        feels_like_adjustment = -2.0
    
    feels_like_f = temp_f + feels_like_adjustment
    feels_like_c = (feels_like_f - 32) * 5/9
    
    # ===== PRECIPITATION =====
    precip_mm = 0.0
    if models['precipitation']:
        precip_model = models['precipitation']
        X_precip = _generate_features(date_str, precip_model['feature_names'])
        X_precip_scaled = precip_model['scaler'].transform(X_precip)
        precip_mm = max(0, precip_model['model'].predict(X_precip_scaled)[0])
        
        # Time-based adjustment (more rain in afternoon/evening)
        if 15 <= hour <= 18:
            precip_mm *= 1.3
        elif 5 <= hour <= 8:
            precip_mm *= 1.1
        elif 21 <= hour or hour <= 3:
            precip_mm *= 0.8
    
    precip_inches = precip_mm / 25.4
    
    # ===== HUMIDITY =====
    humidity_percent = 50.0  # Default
    if models['humidity']:
        hum_model = models['humidity']
        X_hum = _generate_features(date_str, hum_model['feature_names'])
        X_hum_scaled = hum_model['scaler'].transform(X_hum)
        vapor_pressure = hum_model['model'].predict(X_hum_scaled)[0]
        
        # Convert vapor pressure to relative humidity (approximation)
        humidity_percent = min(100, max(0, vapor_pressure / 16.5))
        
        # Adjust by time of day (higher in morning/night)
        if 5 <= hour <= 9:
            humidity_percent = min(100, humidity_percent * 1.15)
        elif 21 <= hour or hour <= 5:
            humidity_percent = min(100, humidity_percent * 1.1)
        elif 13 <= hour <= 17:
            humidity_percent = max(20, humidity_percent * 0.9)
    
    # ===== CLOUD COVER =====
    cloud_cover_percent = 50.0  # Default
    if models['cloud']:
        cloud_model = models['cloud']
        X_cloud = _generate_features(date_str, cloud_model['feature_names'])
        X_cloud_scaled = cloud_model['scaler'].transform(X_cloud)
        cloud_cover_percent = cloud_model['model'].predict(X_cloud_scaled)[0]
        cloud_cover_percent = min(100, max(0, cloud_cover_percent + 32.5))
    
    # ===== WIND SPEED =====
    wind_speed_ms = 3.0  # Default ~7 mph
    if models['wind']:
        wind_model = models['wind']
        X_wind = _generate_features(date_str, wind_model['feature_names'])
        X_wind_scaled = wind_model['scaler'].transform(X_wind)
        wind_proxy = wind_model['model'].predict(X_wind_scaled)[0]
        wind_speed_ms = max(0, (wind_proxy - 330) * 1.3)
        
        # Adjust by time of day (windier in afternoon)
        if 12 <= hour <= 17:
            wind_speed_ms *= 1.2
        elif 21 <= hour or hour <= 5:
            wind_speed_ms *= 0.8
    
    wind_speed_mph = wind_speed_ms * 2.237
    
    # Description
    if feels_like_f < 32:
        feel = "Freezing"
    elif feels_like_f < 50:
        feel = "Cold"
    elif feels_like_f < 65:
        feel = "Cool"
    elif feels_like_f < 75:
        feel = "Comfortable"
    elif feels_like_f < 85:
        feel = "Warm"
    else:
        feel = "Hot"
    
    # Add weather conditions to description
    conditions = []
    if precip_mm > 5:
        conditions.append("rainy")
    elif precip_mm > 1:
        conditions.append("light rain")
    
    if cloud_cover_percent > 75:
        conditions.append("cloudy")
    elif cloud_cover_percent > 50:
        conditions.append("partly cloudy")
    elif cloud_cover_percent < 25:
        conditions.append("clear")
    
    if wind_speed_mph > 20:
        conditions.append("windy")
    
    condition_str = ", ".join(conditions) if conditions else ""
    description = f"{feel} {time_period}" + (f" - {condition_str}" if condition_str else "")
    
    return {
        'date': date_str,
        'hour': hour,
        'temperature_f': round(temp_f, 1),
        'feels_like_f': round(feels_like_f, 1),
        'temperature_c': round(temp_c, 1),
        'feels_like_c': round(feels_like_c, 1),
        'precipitation_mm': round(precip_mm, 2),
        'precipitation_inches': round(precip_inches, 3),
        'humidity_percent': round(humidity_percent, 1),
        'cloud_cover_percent': round(cloud_cover_percent, 1),
        'wind_speed_mph': round(wind_speed_mph, 1),
        'wind_speed_ms': round(wind_speed_ms, 1),
        'time_period': time_period,
        'description': description
    }

def predict_daily_range(start_date, end_date):
    """
    Predict daily average weather for a date range.

    Args:
        start_date (str): Start date in 'YYYY-MM-DD' format
        end_date (str): End date in 'YYYY-MM-DD' format

    Returns:
        pandas.DataFrame: Daily averages with columns:
            - date
            - avg_temperature_f, avg_feels_like_f
            - avg_temperature_c, avg_feels_like_c
            - total_precipitation_mm, total_precipitation_inches
            - avg_humidity_percent
            - avg_cloud_cover_percent
            - avg_wind_speed_mph, avg_wind_speed_ms
            - min_temp_f, max_temp_f
    """
    models = _load_models()
    
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    
    if (end - start).days > 365:
        raise ValueError("Date range cannot exceed 365 days")
    
    results = []
    
    current = start
    while current <= end:
        date_str = current.strftime('%Y-%m-%d')
        
        # Predict for representative hours (0, 6, 12, 18)
        hourly_predictions = []
        for hour in [0, 6, 12, 18]:
            try:
                pred = predict_hourly(date_str, hour)
                hourly_predictions.append(pred)
            except Exception as e:
                print(f"Error predicting {date_str} hour {hour}: {e}")
                continue
        
        if hourly_predictions:
            # Calculate daily averages and totals
            temps_f = [p['temperature_f'] for p in hourly_predictions]
            feels_f = [p['feels_like_f'] for p in hourly_predictions]
            temps_c = [p['temperature_c'] for p in hourly_predictions]
            feels_c = [p['feels_like_c'] for p in hourly_predictions]
            precip_mm = [p['precipitation_mm'] for p in hourly_predictions]
            precip_in = [p['precipitation_inches'] for p in hourly_predictions]
            humidity = [p['humidity_percent'] for p in hourly_predictions]
            clouds = [p['cloud_cover_percent'] for p in hourly_predictions]
            wind_mph = [p['wind_speed_mph'] for p in hourly_predictions]
            wind_ms = [p['wind_speed_ms'] for p in hourly_predictions]
            
            results.append({
                'date': date_str,
                'avg_temperature_f': round(np.mean(temps_f), 1),
                'avg_feels_like_f': round(np.mean(feels_f), 1),
                'avg_temperature_c': round(np.mean(temps_c), 1),
                'avg_feels_like_c': round(np.mean(feels_c), 1),
                'total_precipitation_mm': round(sum(precip_mm), 2),
                'total_precipitation_inches': round(sum(precip_in), 3),
                'avg_humidity_percent': round(np.mean(humidity), 1),
                'avg_cloud_cover_percent': round(np.mean(clouds), 1),
                'avg_wind_speed_mph': round(np.mean(wind_mph), 1),
                'avg_wind_speed_ms': round(np.mean(wind_ms), 1),
                'min_temp_f': round(min(temps_f), 1),
                'max_temp_f': round(max(temps_f), 1)
            })
        
        current += timedelta(days=1)
    
    return pd.DataFrame(results)

if __name__ == "__main__":
    # Demo
    print("="*70)
    print("WEATHER PREDICTION SYSTEM - DEMO")
    print("="*70)
    
    # Single hour prediction
    print("\n1. HOURLY PREDICTION")
    print("-"*70)
    weather = predict_hourly('2025-10-04', 14)
    print(f"\nDate: {weather['date']}")
    print(f"Hour: {weather['hour']}:00")
    print(f"Temperature:    {weather['temperature_f']}°F ({weather['temperature_c']}°C)")
    print(f"Feels Like:     {weather['feels_like_f']}°F ({weather['feels_like_c']}°C)")
    print(f"Precipitation:  {weather['precipitation_mm']} mm ({weather['precipitation_inches']} in)")
    print(f"Humidity:       {weather['humidity_percent']}%")
    print(f"Cloud Cover:    {weather['cloud_cover_percent']}%")
    print(f"Wind Speed:     {weather['wind_speed_mph']} mph ({weather['wind_speed_ms']} m/s)")
    print(f"Time Period:    {weather['time_period']}")
    print(f"Description:    {weather['description']}")
    
    # Daily range prediction
    print("\n\n2. DAILY RANGE PREDICTION")
    print("-"*70)
    forecast = predict_daily_range('2025-10-04', '2025-10-08')
    print("\n" + forecast.to_string(index=False))
    
    print("\n\n✅ Demo complete")
