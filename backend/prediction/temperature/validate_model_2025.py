"""
Validate the temperature prediction model against real 2025 weather data.
Uses Open-Meteo API to fetch actual historical weather data for Chicago.
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add path to import model
sys.path.append(os.path.join(os.path.dirname(__file__), 'prediction', 'temperature'))
from temperature_prediction_model import TemperaturePredictionModel
import joblib

def fetch_real_weather_data_2025(start_date='2025-01-01', end_date='2025-01-31'):
    """
    Fetch real weather data for Chicago in 2025 using Open-Meteo API.

    Args:
        start_date: Start date in 'YYYY-MM-DD' format
        end_date: End date in 'YYYY-MM-DD' format

    Returns:
        DataFrame with hourly weather data
    """
    print(f"Fetching real weather data for Chicago from {start_date} to {end_date}...")

    # Chicago coordinates
    latitude = 41.8781
    longitude = -87.6298

    # Open-Meteo API endpoint for historical/archive data
    url = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        'latitude': latitude,
        'longitude': longitude,
        'start_date': start_date,
        'end_date': end_date,
        'hourly': [
            'temperature_2m',
            'apparent_temperature',  # Feels like temperature
            'cloud_cover',
            'surface_pressure',
        ],
        'timezone': 'America/Chicago'
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Parse hourly data
        hourly = data.get('hourly', {})

        df = pd.DataFrame({
            'datetime': pd.to_datetime(hourly['time']),
            'temperature': hourly['temperature_2m'],
            'feels_like': hourly['apparent_temperature'],
            'cloud_cover': hourly['cloud_cover'],
        })

        # Add date and hour columns
        df['date'] = df['datetime'].dt.date
        df['hour'] = df['datetime'].dt.hour

        print(f"[OK] Fetched {len(df)} hourly records")
        print(f"  Temperature range: {df['temperature'].min():.1f}°C to {df['temperature'].max():.1f}°C")

        return df

    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return None

def get_modis_data_for_date(date_str, modis_data):
    """
    Get MODIS satellite data for a specific date.

    Args:
        date_str: Date in 'YYYY-MM-DD' format
        modis_data: DataFrame with MODIS data

    Returns:
        Dictionary with MODIS values for that date
    """
    # Filter for the date
    date_data = modis_data[modis_data['Date'] == date_str]

    if len(date_data) == 0:
        # Return None if no data available
        return None

    # Get the first row (should be only one for Chicago)
    row = date_data.iloc[0]

    return {
        'lst_day': row.get('MOD11A1_061_LST_Day_1km', 288.0),
        'lst_night': row.get('MOD11A1_061_LST_Night_1km', 280.0),
        'cloud_cover_day': row.get('MOD11A1_061_Clear_day_cov', 0.5),
        'cloud_cover_night': row.get('MOD11A1_061_Clear_night_cov', 0.5),
        'sur_refl_bands': [
            row.get('MOD09GA_061_sur_refl_b01_1', 0.15),
            row.get('MOD09GA_061_sur_refl_b02_1', 0.20),
            row.get('MOD09GA_061_sur_refl_b03_1', 0.10),
            row.get('MOD09GA_061_sur_refl_b04_1', 0.15),
            row.get('MOD09GA_061_sur_refl_b05_1', 0.18),
            row.get('MOD09GA_061_sur_refl_b06_1', 0.12),
            row.get('MOD09GA_061_sur_refl_b07_1', 0.08),
        ],
        'solar_azimuth': row.get('MOD09GA_061_SolarAzimuth_1', 180.0),
        'solar_zenith': row.get('MOD09GA_061_SolarZenith_1', 45.0),
        'emis_31': row.get('MOD11A1_061_Emis_31', 0.985),
        'emis_32': row.get('MOD11A1_061_Emis_32', 0.985),
    }

def validate_model_predictions(model, real_weather_df, modis_data):
    """
    Compare model predictions with real weather data.

    Args:
        model: Trained temperature prediction model
        real_weather_df: DataFrame with real weather data
        modis_data: DataFrame with MODIS satellite data

    Returns:
        DataFrame with comparison results
    """
    print("\nValidating model predictions against real 2025 data...")

    results = []

    for idx, row in real_weather_df.iterrows():
        date_str = str(row['date'])
        hour = row['hour']
        actual_temp = row['temperature']
        actual_feels_like = row['feels_like']

        # Get MODIS data for this date
        modis_values = get_modis_data_for_date(date_str, modis_data)

        if modis_values is None:
            # Use defaults if no MODIS data
            modis_values = {}

        # Make prediction
        try:
            prediction = model.predict_feels_like_temperature(
                date_str=date_str,
                hour=hour,
                **modis_values
            )

            results.append({
                'datetime': row['datetime'],
                'date': date_str,
                'hour': hour,
                'actual_temperature': actual_temp,
                'predicted_temperature': prediction['predicted_temperature'],
                'actual_feels_like': actual_feels_like,
                'predicted_feels_like': prediction['feels_like_temperature'],
                'time_period': prediction['time_period'],
                'error_temperature': abs(actual_temp - prediction['predicted_temperature']),
                'error_feels_like': abs(actual_feels_like - prediction['feels_like_temperature'])
            })
        except Exception as e:
            print(f"Error predicting for {date_str} {hour}:00 - {e}")
            continue

        # Progress indicator
        if (idx + 1) % 100 == 0:
            print(f"  Processed {idx + 1}/{len(real_weather_df)} records...")

    results_df = pd.DataFrame(results)

    # Calculate metrics
    print("\n" + "="*70)
    print("VALIDATION RESULTS")
    print("="*70)

    print(f"\nTotal predictions: {len(results_df)}")

    print("\nTemperature Prediction Metrics:")
    print(f"  MAE:  {results_df['error_temperature'].mean():.2f}°C")
    print(f"  RMSE: {np.sqrt((results_df['error_temperature']**2).mean()):.2f}°C")
    print(f"  Max Error: {results_df['error_temperature'].max():.2f}°C")

    print("\nFeels-Like Temperature Metrics:")
    print(f"  MAE:  {results_df['error_feels_like'].mean():.2f}°C")
    print(f"  RMSE: {np.sqrt((results_df['error_feels_like']**2).mean()):.2f}°C")
    print(f"  Max Error: {results_df['error_feels_like'].max():.2f}°C")

    # Breakdown by time period
    print("\nError by Time Period:")
    for period in ['morning', 'afternoon', 'evening', 'night']:
        period_data = results_df[results_df['time_period'] == period]
        if len(period_data) > 0:
            mae = period_data['error_feels_like'].mean()
            print(f"  {period.capitalize():10s}: MAE = {mae:.2f}°C ({len(period_data)} samples)")

    return results_df

def load_modis_data():
    """Load MODIS data for comparison"""
    print("\nLoading MODIS data...")

    try:
        # Try to load merged data
        mod09ga = pd.read_csv('backend/data/Modis/Chicago-MOD09GA.csv')
        mod11a1 = pd.read_csv('backend/data/Modis/Chicago-MOD11A1.csv')

        # Merge
        modis_df = pd.merge(
            mod09ga, mod11a1,
            on=['Date', 'Category', 'ID', 'Latitude', 'Longitude'],
            how='inner',
            suffixes=('_09GA', '_11A1')
        )

        print(f"[OK] Loaded {len(modis_df)} MODIS records")
        return modis_df

    except Exception as e:
        print(f"Warning: Could not load MODIS data: {e}")
        return pd.DataFrame()

def main():
    """Main validation function"""
    print("="*70)
    print("MODEL VALIDATION WITH REAL 2025 WEATHER DATA")
    print("="*70)

    # Load model
    print("\nLoading trained model...")
    try:
        model = joblib.load('backend/data/Modis/temperature_model.pkl')
        print("[OK] Model loaded")
    except FileNotFoundError:
        print("Error: Model file not found. Please train the model first.")
        return

    # Load MODIS data
    modis_data = load_modis_data()

    # Fetch real weather data (December 2024 - most recent available)
    real_weather = fetch_real_weather_data_2025(
        start_date='2024-12-01',
        end_date='2024-12-15'  # First 15 days of December 2024
    )

    if real_weather is None:
        print("Failed to fetch real weather data")
        return

    # Validate predictions
    results = validate_model_predictions(model, real_weather, modis_data)

    # Save results
    output_file = 'backend/data/Modis/validation_results_2025.csv'
    results.to_csv(output_file, index=False)
    print(f"\n[OK] Validation results saved to {output_file}")

    # Analyze if weights need adjustment
    mae_feels_like = results['error_feels_like'].mean()
    rmse_feels_like = np.sqrt((results['error_feels_like']**2).mean())

    print("\n" + "="*70)
    print("RECOMMENDATION")
    print("="*70)

    if mae_feels_like < 2.0:
        print("[OK] Model performance is EXCELLENT (MAE < 2°C)")
        print("  No weight adjustments needed.")
    elif mae_feels_like < 3.5:
        print("[OK] Model performance is GOOD (MAE < 3.5°C)")
        print("  Minor weight adjustments may improve accuracy.")
    else:
        print("[!] Model performance needs IMPROVEMENT (MAE > 3.5°C)")
        print("  Consider adjusting time period weights and cloud effects.")
        print("\nSuggested adjustments:")

        # Check which time periods have highest errors
        for period in ['morning', 'afternoon', 'evening', 'night']:
            period_data = results[results['time_period'] == period]
            if len(period_data) > 0:
                mae = period_data['error_feels_like'].mean()
                if mae > 4.0:
                    print(f"  - {period.capitalize()}: High error ({mae:.2f}°C) - adjust weights")

    return results

if __name__ == "__main__":
    results = main()
