"""
UNIFIED WEATHER PREDICTION SYSTEM

Main prediction interface with:
1. predict_hourly(date, hour) - Get weather for specific hour
2. predict_daily_range(start_date, end_date) - Get daily averages for date range

Trained on full dataset and tuned against real 2025 data.

Usage:
    from predict import predict_hourly, predict_daily_range

    # Single hour
    weather = predict_hourly('2025-02-15', 14)
    print(weather)

    # Date range (daily averages)
    forecast = predict_daily_range('2025-02-15', '2025-02-20')
    print(forecast)

Author: Claude Code
Date: 2025-10-04
"""

import os
import pandas as pd
import numpy as np
import pickle
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Paths - handle both running from root and from prediction folder
if os.path.basename(os.getcwd()) == 'prediction':
    DATA_DIR = '../data'
else:
    DATA_DIR = 'backend/data'
MODELS_DIR = os.path.join(DATA_DIR, 'Modis')

# Global caches
_MODELS = None
_MODIS_DF = None
_WEIGHTS = None


def _load_resources():
    """Load models, MODIS data, and tuned weights (cached)"""
    global _MODELS, _MODIS_DF, _WEIGHTS

    first_load = _MODELS is None

    if _MODELS is None:
        if first_load:
            print("Loading models...")
        _MODELS = {}
        for name in ['temperature', 'precipitation', 'humidity', 'cloud', 'wind']:
            path = os.path.join(MODELS_DIR, f'{name}_model_full.pkl')
            with open(path, 'rb') as f:
                _MODELS[name] = pickle.load(f)

    if _MODIS_DF is None:
        if first_load:
            print("Loading MODIS data...")
        mod09ga = pd.read_csv(os.path.join(DATA_DIR, 'Modis', 'Chicago-MOD09GA.csv'))
        mod10a1 = pd.read_csv(os.path.join(DATA_DIR, 'Modis', 'Chicago-MOD10A1.csv'))
        mod11a1 = pd.read_csv(os.path.join(DATA_DIR, 'Modis', 'Chicago-MOD11A1.csv'))
        mod13a1 = pd.read_csv(os.path.join(DATA_DIR, 'Modis', 'Chicago-MOD13A1.csv'))
        mod16a2 = pd.read_csv(os.path.join(DATA_DIR, 'Modis', 'Chicago-MOD16A2.csv'))

        _MODIS_DF = mod09ga.merge(mod10a1, on='Date', how='outer', suffixes=('', '_d1'))
        _MODIS_DF = _MODIS_DF.merge(mod11a1, on='Date', how='outer', suffixes=('', '_d2'))
        _MODIS_DF = _MODIS_DF.merge(mod13a1, on='Date', how='outer', suffixes=('', '_d3'))
        _MODIS_DF = _MODIS_DF.merge(mod16a2, on='Date', how='outer', suffixes=('', '_d4'))
        _MODIS_DF = _MODIS_DF.loc[:, ~_MODIS_DF.columns.str.contains('_d[0-9]')]
        _MODIS_DF['Date'] = pd.to_datetime(_MODIS_DF['Date'])

    if _WEIGHTS is None:
        if first_load:
            print("Loading tuned weights...")
        weights_path = os.path.join(MODELS_DIR, 'tuned_weights.pkl')
        if os.path.exists(weights_path):
            with open(weights_path, 'rb') as f:
                _WEIGHTS = pickle.load(f)
        else:
            # Default weights if tuning hasn't been run
            _WEIGHTS = {
                'temp_morning_offset': -5.8419,
                'temp_afternoon_offset': -2.3419,
                'temp_evening_offset': -3.8419,
                'temp_night_offset': -6.3419,
                'temp_cloud_day_factor': -1.0,
                'temp_cloud_night_factor': 1.5,
                'precip_morning_mult': 1.15,
                'precip_afternoon_mult': 1.25,
                'precip_night_mult': 0.85,
                'humidity_vp_to_rh_factor': 16.4476,
                'cloud_baseline_offset': 32.5430,
                'wind_proxy_scale': 1.3176,
            }

    if first_load:
        print("[OK] All resources loaded")


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
            - temperature (float): Base temperature in °C
            - feels_like (float): Feels-like temperature in °C
            - precipitation (float): Precipitation in mm
            - humidity (float): Relative humidity in %
            - cloud_cover (float): Cloud cover in %
            - wind_speed (float): Wind speed in m/s
    """
    _load_resources()

    # Find closest MODIS data
    target_date = pd.to_datetime(date_str)
    _MODIS_DF['date_diff'] = abs((_MODIS_DF['Date'] - target_date).dt.days)

    if _MODIS_DF['date_diff'].min() > 60:
        raise ValueError(f"No MODIS data available within 60 days of {date_str}")

    modis_row = _MODIS_DF.loc[_MODIS_DF['date_diff'].idxmin()]

    # Build temporal features
    date_obj = pd.to_datetime(date_str)
    month = date_obj.month
    day_of_year = date_obj.dayofyear
    season = (month % 12 + 3) // 3

    def build_features(feature_names):
        features = {}
        for feat in feature_names:
            if feat == 'month':
                features[feat] = month
            elif feat == 'day_of_year':
                features[feat] = day_of_year
            elif feat == 'season':
                features[feat] = season
            else:
                features[feat] = modis_row.get(feat, 0)
        return pd.DataFrame([features])[feature_names]

    # ===== TEMPERATURE =====
    temp_X = build_features(_MODELS['temperature']['feature_names'])
    temp_X_scaled = _MODELS['temperature']['scaler'].transform(temp_X)
    base_temp = _MODELS['temperature']['model'].predict(temp_X_scaled)[0]

    # Time-based adjustments
    if 6 <= hour < 12:
        feels_like = base_temp + _WEIGHTS['temp_morning_offset']
    elif 12 <= hour < 18:
        feels_like = base_temp + _WEIGHTS['temp_afternoon_offset']
    elif 18 <= hour < 21:
        feels_like = base_temp + _WEIGHTS['temp_evening_offset']
    else:
        feels_like = base_temp + _WEIGHTS['temp_night_offset']

    # Cloud effects
    clear_cov = modis_row.get('MOD11A1_061_Clear_day_cov', 0.5)
    if 6 <= hour < 18:
        feels_like += (1 - clear_cov) * _WEIGHTS['temp_cloud_day_factor']
    else:
        feels_like += (1 - clear_cov) * _WEIGHTS['temp_cloud_night_factor']

    # ===== PRECIPITATION =====
    precip_X = build_features(_MODELS['precipitation']['feature_names'])
    precip_X_scaled = _MODELS['precipitation']['scaler'].transform(precip_X)
    base_precip = _MODELS['precipitation']['model'].predict(precip_X_scaled)[0]

    # Time multipliers
    if 5 <= hour <= 8:
        precip = base_precip * _WEIGHTS['precip_morning_mult']
    elif 15 <= hour <= 18:
        precip = base_precip * _WEIGHTS['precip_afternoon_mult']
    elif 21 <= hour or hour <= 3:
        precip = base_precip * _WEIGHTS['precip_night_mult']
    else:
        precip = base_precip
    precip = max(0, precip)

    # ===== HUMIDITY =====
    hum_X = build_features(_MODELS['humidity']['feature_names'])
    hum_X_scaled = _MODELS['humidity']['scaler'].transform(hum_X)
    vp = _MODELS['humidity']['model'].predict(hum_X_scaled)[0]
    humidity = min(100, max(0, vp / _WEIGHTS['humidity_vp_to_rh_factor']))

    # ===== CLOUD COVER =====
    cloud_X = build_features(_MODELS['cloud']['feature_names'])
    cloud_X_scaled = _MODELS['cloud']['scaler'].transform(cloud_X)
    cloud_pred = _MODELS['cloud']['model'].predict(cloud_X_scaled)[0]
    cloud = min(100, max(0, cloud_pred + _WEIGHTS['cloud_baseline_offset']))

    # ===== WIND =====
    wind_X = build_features(_MODELS['wind']['feature_names'])
    wind_X_scaled = _MODELS['wind']['scaler'].transform(wind_X)
    wind_proxy = _MODELS['wind']['model'].predict(wind_X_scaled)[0]
    wind = max(0, (wind_proxy - 330) * _WEIGHTS['wind_proxy_scale'])

    return {
        'date': date_str,
        'hour': hour,
        'temperature': round(base_temp, 2),
        'feels_like': round(feels_like, 2),
        'precipitation': round(precip, 2),
        'humidity': round(humidity, 1),
        'cloud_cover': round(cloud, 1),
        'wind_speed': round(wind, 2)
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
            - avg_temperature
            - avg_feels_like
            - total_precipitation
            - avg_humidity
            - avg_cloud_cover
            - avg_wind_speed
    """
    _load_resources()

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
            except:
                continue

        if hourly_predictions:
            # Calculate daily averages
            temps = [p['temperature'] for p in hourly_predictions]
            feels = [p['feels_like'] for p in hourly_predictions]
            precips = [p['precipitation'] for p in hourly_predictions]
            humids = [p['humidity'] for p in hourly_predictions]
            clouds = [p['cloud_cover'] for p in hourly_predictions]
            winds = [p['wind_speed'] for p in hourly_predictions]

            results.append({
                'date': date_str,
                'avg_temperature': round(np.mean(temps), 2),
                'avg_feels_like': round(np.mean(feels), 2),
                'total_precipitation': round(sum(precips), 2),
                'avg_humidity': round(np.mean(humids), 1),
                'avg_cloud_cover': round(np.mean(clouds), 1),
                'avg_wind_speed': round(np.mean(winds), 2)
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
    weather = predict_hourly('2025-02-15', 14)
    print(f"\nDate: {weather['date']}")
    print(f"Hour: {weather['hour']}:00")
    print(f"Temperature:    {weather['temperature']}°C")
    print(f"Feels Like:     {weather['feels_like']}°C")
    print(f"Precipitation:  {weather['precipitation']} mm")
    print(f"Humidity:       {weather['humidity']}%")
    print(f"Cloud Cover:    {weather['cloud_cover']}%")
    print(f"Wind Speed:     {weather['wind_speed']} m/s")

    # Daily range prediction
    print("\n\n2. DAILY RANGE PREDICTION")
    print("-"*70)
    forecast = predict_daily_range('2025-02-15', '2025-02-20')
    print("\n" + forecast.to_string(index=False))

    print("\n\n[OK] Demo complete")
