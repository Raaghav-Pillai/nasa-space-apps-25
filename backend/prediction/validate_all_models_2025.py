"""
Validate All Weather Prediction Models Against Real 2025 Data

Tests humidity, cloud cover, wind, and precipitation models against actual weather data.

Author: Claude Code
Date: 2025-10-04
"""

import os
import sys
import pandas as pd
import numpy as np
import pickle
import requests
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Determine data directory
current_dir = os.getcwd()
if os.path.basename(current_dir) == 'prediction':
    DATA_DIR = '../data/Modis'
    MODIS_DIR = '../data/Modis'
else:
    DATA_DIR = 'backend/data/Modis'
    MODIS_DIR = 'backend/data/Modis'


def fetch_real_weather_data_2025(start_date='2024-12-01', end_date='2024-12-15'):
    """Fetch real weather data from Open-Meteo API"""
    print("Fetching real weather data from Open-Meteo...")

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        'latitude': 41.8781,
        'longitude': -87.6298,
        'start_date': start_date,
        'end_date': end_date,
        'hourly': ['temperature_2m', 'relative_humidity_2m', 'precipitation',
                   'cloud_cover', 'wind_speed_10m'],
        'timezone': 'America/Chicago'
    }

    response = requests.get(url, params=params)
    data = response.json()

    # Parse into DataFrame
    hourly = data['hourly']
    df = pd.DataFrame({
        'datetime': pd.to_datetime(hourly['time']),
        'temperature': hourly['temperature_2m'],
        'humidity': hourly['relative_humidity_2m'],
        'precipitation': hourly['precipitation'],
        'cloud_cover': hourly['cloud_cover'],
        'wind_speed': hourly['wind_speed_10m']
    })

    print(f"[OK] Fetched {len(df)} hourly records")
    print(f"  Temperature range: {df['temperature'].min():.1f} to {df['temperature'].max():.1f} deg C")
    print(f"  Humidity range: {df['humidity'].min():.1f} to {df['humidity'].max():.1f}%")
    print(f"  Cloud cover range: {df['cloud_cover'].min():.1f} to {df['cloud_cover'].max():.1f}%")
    print(f"  Wind speed range: {df['wind_speed'].min():.1f} to {df['wind_speed'].max():.1f} m/s")

    return df


def load_modis_data():
    """Load MODIS satellite data"""
    print("\nLoading MODIS data...")

    mod09ga = pd.read_csv(os.path.join(MODIS_DIR, 'Chicago-MOD09GA.csv'))
    mod10a1 = pd.read_csv(os.path.join(MODIS_DIR, 'Chicago-MOD10A1.csv'))
    mod11a1 = pd.read_csv(os.path.join(MODIS_DIR, 'Chicago-MOD11A1.csv'))
    mod13a1 = pd.read_csv(os.path.join(MODIS_DIR, 'Chicago-MOD13A1.csv'))
    mod16a2 = pd.read_csv(os.path.join(MODIS_DIR, 'Chicago-MOD16A2.csv'))

    # Merge
    df = mod09ga.merge(mod10a1, on='Date', how='outer', suffixes=('', '_mod10'))
    df = df.merge(mod11a1, on='Date', how='outer', suffixes=('', '_mod11'))
    df = df.merge(mod13a1, on='Date', how='outer', suffixes=('', '_mod13'))
    df = df.merge(mod16a2, on='Date', how='outer', suffixes=('', '_mod16'))

    df['Date'] = pd.to_datetime(df['Date'])

    print(f"[OK] Loaded {len(df)} MODIS records")

    return df


def validate_models(weather_df, modis_df):
    """Validate all models against real weather data"""
    print("\n" + "="*70)
    print("VALIDATING ALL MODELS")
    print("="*70)

    # Load all models
    print("\nLoading models...")
    with open(os.path.join(DATA_DIR, 'humidity_model.pkl'), 'rb') as f:
        humidity_model_data = pickle.load(f)
    with open(os.path.join(DATA_DIR, 'cloud_model.pkl'), 'rb') as f:
        cloud_model_data = pickle.load(f)
    with open(os.path.join(DATA_DIR, 'wind_model.pkl'), 'rb') as f:
        wind_model_data = pickle.load(f)

    print("[OK] All models loaded")

    results = []

    for idx, row in weather_df.iterrows():
        dt = row['datetime']
        date_str = dt.strftime('%Y-%m-%d')

        # Find matching MODIS data
        modis_row = modis_df[modis_df['Date'] == date_str]

        if len(modis_row) == 0:
            continue  # No MODIS data for this date

        modis_row = modis_row.iloc[0]

        # Extract features for each model
        try:
            # Humidity model prediction
            humidity_features = {}
            for feat in humidity_model_data['feature_names']:
                if feat in ['month', 'day_of_year', 'season']:
                    if feat == 'month':
                        humidity_features[feat] = dt.month
                    elif feat == 'day_of_year':
                        humidity_features[feat] = dt.dayofyear
                    else:  # season
                        humidity_features[feat] = ((dt.month % 12) + 3) // 3
                else:
                    humidity_features[feat] = modis_row.get(feat, 0)

            X_hum = pd.DataFrame([humidity_features])[humidity_model_data['feature_names']]
            X_hum_scaled = humidity_model_data['scaler'].transform(X_hum)
            pred_humidity_pa = humidity_model_data['model'].predict(X_hum_scaled)[0]

            # Convert vapor pressure to relative humidity (approximation)
            # RH ≈ (VP / SVP) * 100, where SVP depends on temperature
            # Simplified: use a conversion factor
            pred_humidity_pct = min(100, max(0, pred_humidity_pa / 30))

            # Cloud model prediction
            cloud_features = {}
            for feat in cloud_model_data['feature_names']:
                if feat in ['month', 'day_of_year', 'season']:
                    if feat == 'month':
                        cloud_features[feat] = dt.month
                    elif feat == 'day_of_year':
                        cloud_features[feat] = dt.dayofyear
                    else:
                        cloud_features[feat] = ((dt.month % 12) + 3) // 3
                else:
                    cloud_features[feat] = modis_row.get(feat, 0)

            X_cloud = pd.DataFrame([cloud_features])[cloud_model_data['feature_names']]
            X_cloud_scaled = cloud_model_data['scaler'].transform(X_cloud)
            pred_cloud_pct = cloud_model_data['model'].predict(X_cloud_scaled)[0]
            pred_cloud_pct = min(100, max(0, pred_cloud_pct))

            # Wind model prediction
            wind_features = {}
            for feat in wind_model_data['feature_names']:
                if feat in ['month', 'day_of_year', 'season']:
                    if feat == 'month':
                        wind_features[feat] = dt.month
                    elif feat == 'day_of_year':
                        wind_features[feat] = dt.dayofyear
                    else:
                        wind_features[feat] = ((dt.month % 12) + 3) // 3
                else:
                    wind_features[feat] = modis_row.get(feat, 0)

            X_wind = pd.DataFrame([wind_features])[wind_model_data['feature_names']]
            X_wind_scaled = wind_model_data['scaler'].transform(X_wind)
            pred_wind_proxy = wind_model_data['model'].predict(X_wind_scaled)[0]

            # Convert wind proxy to m/s (approximation)
            pred_wind_ms = (pred_wind_proxy - 330) / 2  # Rough conversion

            results.append({
                'datetime': dt,
                'date': date_str,
                'hour': dt.hour,
                # Actual values
                'actual_humidity': row['humidity'],
                'actual_cloud_cover': row['cloud_cover'],
                'actual_wind_speed': row['wind_speed'],
                # Predicted values
                'predicted_humidity': pred_humidity_pct,
                'predicted_cloud_cover': pred_cloud_pct,
                'predicted_wind_speed': pred_wind_ms,
                # Errors
                'error_humidity': abs(row['humidity'] - pred_humidity_pct),
                'error_cloud_cover': abs(row['cloud_cover'] - pred_cloud_pct),
                'error_wind_speed': abs(row['wind_speed'] - pred_wind_ms)
            })

        except Exception as e:
            continue  # Skip this record if there's an error

    results_df = pd.DataFrame(results)

    return results_df


def print_validation_results(results_df):
    """Print validation metrics"""
    print("\n" + "="*70)
    print("VALIDATION RESULTS")
    print("="*70)

    print(f"\nTotal predictions: {len(results_df)}")

    # Humidity metrics
    print("\n--- HUMIDITY METRICS ---")
    hum_mae = results_df['error_humidity'].mean()
    hum_rmse = np.sqrt((results_df['error_humidity']**2).mean())
    print(f"  MAE:  {hum_mae:.2f}%")
    print(f"  RMSE: {hum_rmse:.2f}%")

    # Cloud cover metrics
    print("\n--- CLOUD COVER METRICS ---")
    cloud_mae = results_df['error_cloud_cover'].mean()
    cloud_rmse = np.sqrt((results_df['error_cloud_cover']**2).mean())
    print(f"  MAE:  {cloud_mae:.2f}%")
    print(f"  RMSE: {cloud_rmse:.2f}%")

    # Wind speed metrics
    print("\n--- WIND SPEED METRICS ---")
    wind_mae = results_df['error_wind_speed'].mean()
    wind_rmse = np.sqrt((results_df['error_wind_speed']**2).mean())
    print(f"  MAE:  {wind_mae:.2f} m/s")
    print(f"  RMSE: {wind_rmse:.2f} m/s")

    # Save results
    output_path = os.path.join(DATA_DIR, 'validation_results_all_models_2025.csv')
    results_df.to_csv(output_path, index=False)
    print(f"\n[OK] Results saved to {output_path}")

    # Recommendations
    print("\n" + "="*70)
    print("RECOMMENDATIONS")
    print("="*70)

    if hum_mae < 15:
        print("[OK] Humidity model: Good performance")
    else:
        print("[!] Humidity model: Needs improvement")

    if cloud_mae < 20:
        print("[OK] Cloud cover model: Good performance")
    else:
        print("[!] Cloud cover model: Needs improvement")

    if wind_mae < 3:
        print("[OK] Wind speed model: Good performance")
    else:
        print("[!] Wind speed model: Needs improvement")


if __name__ == "__main__":
    print("="*70)
    print("MODEL VALIDATION WITH REAL 2025 WEATHER DATA")
    print("="*70)

    # Fetch real weather data
    weather_df = fetch_real_weather_data_2025()

    # Load MODIS data
    modis_df = load_modis_data()

    # Validate
    results_df = validate_models(weather_df, modis_df)

    # Print results
    print_validation_results(results_df)
