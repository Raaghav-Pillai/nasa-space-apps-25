"""
Validate models against 2025 data and auto-tune weights

Fetches real 2025 weather data and iteratively adjusts weight parameters
until predictions are within acceptable error ranges.

Author: Claude Code
Date: 2025-10-04
"""

import os
import pandas as pd
import numpy as np
import pickle
import requests
from sklearn.metrics import mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

DATA_DIR = 'backend/data'


# ========== TUNABLE WEIGHT PARAMETERS ==========
WEIGHTS = {
    # Temperature feels-like adjustments by time period
    'temp_morning_offset': -0.5,
    'temp_afternoon_offset': 3.0,
    'temp_evening_offset': 1.5,
    'temp_night_offset': -1.0,
    'temp_cloud_day_factor': -1.0,
    'temp_cloud_night_factor': 1.5,

    # Precipitation time-of-day multipliers
    'precip_morning_mult': 1.15,
    'precip_afternoon_mult': 1.25,
    'precip_night_mult': 0.85,

    # Humidity conversion (vapor pressure to RH)
    'humidity_vp_to_rh_factor': 25.0,  # Simplified conversion

    # Cloud cover adjustment
    'cloud_clear_to_cover_factor': -1.0,  # -1 means inverse relationship
    'cloud_baseline_offset': 50.0,

    # Wind speed conversion
    'wind_proxy_offset': -330,
    'wind_proxy_scale': 0.5,
}


def fetch_2025_weather_data(start_date='2025-01-01', end_date='2025-01-07'):
    """Fetch real 2025 weather data from Open-Meteo (1 week for speed)"""
    print(f"\nFetching real 2025 weather data ({start_date} to {end_date})...")

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        'latitude': 41.8781,
        'longitude': -87.6298,
        'start_date': start_date,
        'end_date': end_date,
        'hourly': ['temperature_2m', 'relative_humidity_2m', 'precipitation',
                   'cloud_cover', 'wind_speed_10m', 'apparent_temperature'],
        'timezone': 'America/Chicago'
    }

    response = requests.get(url, params=params)
    data = response.json()

    hourly = data['hourly']
    df = pd.DataFrame({
        'datetime': pd.to_datetime(hourly['time']),
        'temperature': hourly['temperature_2m'],
        'feels_like': hourly['apparent_temperature'],
        'humidity': hourly['relative_humidity_2m'],
        'precipitation': hourly['precipitation'],
        'cloud_cover': hourly['cloud_cover'],
        'wind_speed': hourly['wind_speed_10m']
    })

    print(f"[OK] Fetched {len(df)} hourly records")
    return df


def load_modis_data():
    """Load MODIS data for predictions"""
    mod09ga = pd.read_csv(os.path.join(DATA_DIR, 'Modis', 'Chicago-MOD09GA.csv'))
    mod10a1 = pd.read_csv(os.path.join(DATA_DIR, 'Modis', 'Chicago-MOD10A1.csv'))
    mod11a1 = pd.read_csv(os.path.join(DATA_DIR, 'Modis', 'Chicago-MOD11A1.csv'))
    mod13a1 = pd.read_csv(os.path.join(DATA_DIR, 'Modis', 'Chicago-MOD13A1.csv'))
    mod16a2 = pd.read_csv(os.path.join(DATA_DIR, 'Modis', 'Chicago-MOD16A2.csv'))

    df = mod09ga.merge(mod10a1, on='Date', how='outer', suffixes=('', '_drop'))
    df = df.merge(mod11a1, on='Date', how='outer', suffixes=('', '_drop'))
    df = df.merge(mod13a1, on='Date', how='outer', suffixes=('', '_drop'))
    df = df.merge(mod16a2, on='Date', how='outer', suffixes=('', '_drop'))
    df = df.loc[:, ~df.columns.str.endswith('_drop')]
    df['Date'] = pd.to_datetime(df['Date'])

    return df


def load_models():
    """Load all trained models"""
    models = {}

    for name in ['temperature', 'precipitation', 'humidity', 'cloud', 'wind']:
        path = os.path.join(DATA_DIR, 'Modis', f'{name}_model_full.pkl')
        with open(path, 'rb') as f:
            models[name] = pickle.load(f)

    return models


def predict_with_weights(models, modis_df, date_str, hour, weights):
    """Make predictions with current weight parameters"""

    # Find MODIS data for this date
    target_date = pd.to_datetime(date_str)
    modis_df['date_diff'] = abs((modis_df['Date'] - target_date).dt.days)

    if modis_df['date_diff'].min() > 30:  # No data within 30 days
        return None

    modis_row = modis_df.loc[modis_df['date_diff'].idxmin()]

    # Build feature vectors
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

    # 1. TEMPERATURE
    temp_X = build_features(models['temperature']['feature_names'])
    temp_X_scaled = models['temperature']['scaler'].transform(temp_X)
    base_temp = models['temperature']['model'].predict(temp_X_scaled)[0]

    # Apply time-based adjustments
    if 6 <= hour < 12:
        feels_like = base_temp + weights['temp_morning_offset']
    elif 12 <= hour < 18:
        feels_like = base_temp + weights['temp_afternoon_offset']
    elif 18 <= hour < 21:
        feels_like = base_temp + weights['temp_evening_offset']
    else:
        feels_like = base_temp + weights['temp_night_offset']

    # Cloud effects
    clear_cov = modis_row.get('MOD11A1_061_Clear_day_cov', 0.5)
    if hour >= 6 and hour < 18:
        feels_like += (1 - clear_cov) * weights['temp_cloud_day_factor']
    else:
        feels_like += (1 - clear_cov) * weights['temp_cloud_night_factor']

    # 2. PRECIPITATION
    precip_X = build_features(models['precipitation']['feature_names'])
    precip_X_scaled = models['precipitation']['scaler'].transform(precip_X)
    base_precip = models['precipitation']['model'].predict(precip_X_scaled)[0]

    # Time multipliers
    if 5 <= hour <= 8:
        precip = base_precip * weights['precip_morning_mult']
    elif 15 <= hour <= 18:
        precip = base_precip * weights['precip_afternoon_mult']
    elif 21 <= hour or hour <= 3:
        precip = base_precip * weights['precip_night_mult']
    else:
        precip = base_precip
    precip = max(0, precip)

    # 3. HUMIDITY
    hum_X = build_features(models['humidity']['feature_names'])
    hum_X_scaled = models['humidity']['scaler'].transform(hum_X)
    vp = models['humidity']['model'].predict(hum_X_scaled)[0]

    # Convert vapor pressure to RH (simplified)
    humidity = min(100, max(0, vp / weights['humidity_vp_to_rh_factor']))

    # 4. CLOUD COVER
    cloud_X = build_features(models['cloud']['feature_names'])
    cloud_X_scaled = models['cloud']['scaler'].transform(cloud_X)
    cloud_pred = models['cloud']['model'].predict(cloud_X_scaled)[0]

    # Adjust with clear coverage
    cloud = min(100, max(0, cloud_pred + weights['cloud_baseline_offset']))

    # 5. WIND
    wind_X = build_features(models['wind']['feature_names'])
    wind_X_scaled = models['wind']['scaler'].transform(wind_X)
    wind_proxy = models['wind']['model'].predict(wind_X_scaled)[0]

    # Convert to m/s
    wind = max(0, (wind_proxy + weights['wind_proxy_offset']) * weights['wind_proxy_scale'])

    return {
        'temperature': base_temp,
        'feels_like': feels_like,
        'precipitation': precip,
        'humidity': humidity,
        'cloud_cover': cloud,
        'wind_speed': wind
    }


def validate_and_tune(max_iterations=3):
    """Validate against 2025 data and auto-tune weights"""
    print("="*70)
    print("VALIDATING AND TUNING AGAINST 2025 DATA")
    print("="*70)

    # Fetch 2025 data
    weather_df = fetch_2025_weather_data()

    # Load MODIS and models
    print("\nLoading MODIS data and models...")
    modis_df = load_modis_data()
    models = load_models()
    print("[OK] Loaded")

    best_weights = WEIGHTS.copy()
    best_total_error = float('inf')

    for iteration in range(max_iterations):
        print(f"\n{'='*70}")
        print(f"ITERATION {iteration + 1}/{max_iterations}")
        print(f"{'='*70}")

        # Predict for sampled hours (every 6 hours for speed)
        predictions = []
        actuals = []

        for idx, row in weather_df[::6].iterrows():
            dt = row['datetime']
            date_str = dt.strftime('%Y-%m-%d')

            pred = predict_with_weights(models, modis_df, date_str, dt.hour, best_weights)

            if pred is None:
                continue

            predictions.append(pred)
            actuals.append(row.to_dict())

        # Calculate errors
        pred_df = pd.DataFrame(predictions)
        actual_df = pd.DataFrame(actuals)

        temp_mae = mean_absolute_error(actual_df['feels_like'], pred_df['feels_like'])
        precip_mae = mean_absolute_error(actual_df['precipitation'], pred_df['precipitation'])
        humidity_mae = mean_absolute_error(actual_df['humidity'], pred_df['humidity'])
        cloud_mae = mean_absolute_error(actual_df['cloud_cover'], pred_df['cloud_cover'])
        wind_mae = mean_absolute_error(actual_df['wind_speed'], pred_df['wind_speed'])

        # Total error (weighted)
        total_error = (temp_mae * 2 + humidity_mae * 0.5 + cloud_mae * 0.5 +
                      wind_mae * 1 + precip_mae * 2)

        print(f"\nErrors:")
        print(f"  Temperature (feels-like): {temp_mae:.2f}°C")
        print(f"  Precipitation:            {precip_mae:.2f} mm")
        print(f"  Humidity:                 {humidity_mae:.2f}%")
        print(f"  Cloud Cover:              {cloud_mae:.2f}%")
        print(f"  Wind Speed:               {wind_mae:.2f} m/s")
        print(f"  Total weighted error:     {total_error:.2f}")

        # Check if improved
        if total_error < best_total_error:
            best_total_error = total_error
            print(f"\n[OK] Improved! New best error: {best_total_error:.2f}")
        else:
            print(f"\n[!] No improvement")
            break  # Stop if not improving

        # Auto-adjust weights based on errors
        if iteration < max_iterations - 1:
            # Adjust temperature offsets
            temp_bias = (actual_df['feels_like'] - pred_df['feels_like']).mean()
            if abs(temp_bias) > 1.0:
                best_weights['temp_morning_offset'] += temp_bias * 0.3
                best_weights['temp_afternoon_offset'] += temp_bias * 0.3
                best_weights['temp_evening_offset'] += temp_bias * 0.3
                best_weights['temp_night_offset'] += temp_bias * 0.3

            # Adjust humidity factor
            hum_bias = (actual_df['humidity'] - pred_df['humidity']).mean()
            if abs(hum_bias) > 5.0:
                best_weights['humidity_vp_to_rh_factor'] *= (1 - hum_bias / 200)

            # Adjust cloud baseline
            cloud_bias = (actual_df['cloud_cover'] - pred_df['cloud_cover']).mean()
            if abs(cloud_bias) > 5.0:
                best_weights['cloud_baseline_offset'] += cloud_bias * 0.3

            # Adjust wind scale
            wind_bias = (actual_df['wind_speed'] - pred_df['wind_speed']).mean()
            if abs(wind_bias) > 1.0:
                best_weights['wind_proxy_scale'] *= (1 + wind_bias / 20)

    # Save tuned weights
    print(f"\n{'='*70}")
    print("FINAL TUNED WEIGHTS")
    print(f"{'='*70}")
    for key, value in best_weights.items():
        print(f"  {key}: {value:.4f}")

    with open(os.path.join(DATA_DIR, 'Modis', 'tuned_weights.pkl'), 'wb') as f:
        pickle.dump(best_weights, f)

    print(f"\n[OK] Weights saved to tuned_weights.pkl")
    print(f"\nFinal errors:")
    print(f"  Temperature: {temp_mae:.2f}°C")
    print(f"  Humidity:    {humidity_mae:.2f}%")
    print(f"  Cloud Cover: {cloud_mae:.2f}%")
    print(f"  Wind:        {wind_mae:.2f} m/s")
    print(f"  Precip:      {precip_mae:.2f} mm")

    return best_weights


if __name__ == "__main__":
    tuned_weights = validate_and_tune(max_iterations=3)
