"""
Quick validation using existing model with synthetic MODIS features
Tests temperature predictions against real 2025 data

Author: Kiro AI
Date: 2025-10-04
"""

import os
import sys
import pandas as pd
import numpy as np
import pickle
import requests
from datetime import datetime, timedelta
from sklearn.metrics import mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

# Determine correct path
if os.path.basename(os.getcwd()) == 'prediction':
    DATA_DIR = '../data/Modis'
else:
    DATA_DIR = 'backend/data/Modis'

def celsius_to_fahrenheit(celsius):
    """Convert Celsius to Fahrenheit"""
    return (celsius * 9/5) + 32

def fahrenheit_to_celsius(fahrenheit):
    """Convert Fahrenheit to Celsius"""
    return (fahrenheit - 32) * 5/9

def fetch_2025_weather_data():
    """Fetch real 2025 weather data"""
    print("="*70)
    print("FETCHING 2025 WEATHER DATA (Jan 1 - Oct 1)")
    print("="*70)
    
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        'latitude': 41.8781,
        'longitude': -87.6298,
        'start_date': '2025-01-01',
        'end_date': '2025-10-01',
        'daily': ['temperature_2m_max', 'temperature_2m_min', 'temperature_2m_mean',
                  'apparent_temperature_max', 'apparent_temperature_min'],
        'timezone': 'America/Chicago',
        'temperature_unit': 'fahrenheit'
    }
    
    print(f"\nFetching data...")
    response = requests.get(url, params=params, timeout=30)
    data = response.json()
    
    daily = data['daily']
    df = pd.DataFrame({
        'date': pd.to_datetime(daily['time']),
        'temp_max_f': daily['temperature_2m_max'],
        'temp_min_f': daily['temperature_2m_min'],
        'temp_mean_f': daily['temperature_2m_mean'],
        'feels_like_max_f': daily['apparent_temperature_max'],
        'feels_like_min_f': daily['apparent_temperature_min']
    })
    
    df['feels_like_mean_f'] = (df['feels_like_max_f'] + df['feels_like_min_f']) / 2
    
    print(f"✅ Fetched {len(df)} days")
    print(f"Temperature range: {df['temp_min_f'].min():.1f}°F to {df['temp_max_f'].max():.1f}°F")
    
    return df

def load_model():
    """Load temperature model"""
    print("\n" + "="*70)
    print("LOADING MODEL")
    print("="*70)
    
    model_path = os.path.join(DATA_DIR, 'temperature_model_full.pkl')
    with open(model_path, 'rb') as f:
        model_data = pickle.load(f)
    
    print(f"✅ Model loaded")
    print(f"Features: {len(model_data['feature_names'])}")
    
    return model_data

def generate_synthetic_features(date, model_data):
    """Generate synthetic MODIS features based on date"""
    date_obj = pd.to_datetime(date)
    month = date_obj.month
    day_of_year = date_obj.dayofyear
    season = (month % 12 + 3) // 3
    
    # Seasonal patterns for Chicago
    # Winter (Dec-Feb): cold, low LST
    # Spring (Mar-May): warming
    # Summer (Jun-Aug): hot, high LST
    # Fall (Sep-Nov): cooling
    
    # Base LST values (Kelvin) - seasonal variation
    if season == 1:  # Winter
        lst_day_base = 273.15 - 5  # ~-5°C
        lst_night_base = 273.15 - 10  # ~-10°C
        clear_cov = 0.4  # More clouds in winter
    elif season == 2:  # Spring
        lst_day_base = 273.15 + 10  # ~10°C
        lst_night_base = 273.15 + 5  # ~5°C
        clear_cov = 0.6
    elif season == 3:  # Summer
        lst_day_base = 273.15 + 25  # ~25°C
        lst_night_base = 273.15 + 18  # ~18°C
        clear_cov = 0.7  # Clearer in summer
    else:  # Fall
        lst_day_base = 273.15 + 12  # ~12°C
        lst_night_base = 273.15 + 7  # ~7°C
        clear_cov = 0.5
    
    # Add daily variation
    daily_var = np.sin(2 * np.pi * day_of_year / 365) * 5
    lst_day = lst_day_base + daily_var
    lst_night = lst_night_base + daily_var
    
    # Solar angles - approximate for Chicago
    solar_zenith = 45 + 20 * np.cos(2 * np.pi * day_of_year / 365)
    solar_azimuth = 180
    
    # Surface reflectance - typical values
    sur_refl = [0.15, 0.20, 0.10, 0.15, 0.18, 0.12, 0.08]
    
    # Emissivity
    emis = [0.985, 0.985]
    
    # Build feature dict
    features = {
        'MOD09GA_061_sur_refl_b01_1': sur_refl[0],
        'MOD09GA_061_sur_refl_b02_1': sur_refl[1],
        'MOD09GA_061_sur_refl_b03_1': sur_refl[2],
        'MOD09GA_061_sur_refl_b04_1': sur_refl[3],
        'MOD09GA_061_sur_refl_b05_1': sur_refl[4],
        'MOD09GA_061_sur_refl_b06_1': sur_refl[5],
        'MOD09GA_061_sur_refl_b07_1': sur_refl[6],
        'MOD09GA_061_SolarAzimuth_1': solar_azimuth,
        'MOD09GA_061_SolarZenith_1': solar_zenith,
        'MOD11A1_061_LST_Day_1km': lst_day,
        'MOD11A1_061_LST_Night_1km': lst_night,
        'MOD11A1_061_Emis_31': emis[0],
        'MOD11A1_061_Emis_32': emis[1],
        'MOD11A1_061_Clear_day_cov': clear_cov,
        'MOD11A1_061_Clear_night_cov': clear_cov,
        'month': month,
        'day_of_year': day_of_year,
        'season': season
    }
    
    return pd.DataFrame([features])[model_data['feature_names']]

def predict_for_date_range(weather_df, model_data):
    """Make predictions for all dates"""
    print("\n" + "="*70)
    print("MAKING PREDICTIONS")
    print("="*70)
    
    predictions = []
    
    for idx, row in weather_df.iterrows():
        date_str = row['date'].strftime('%Y-%m-%d')
        
        try:
            # Generate features
            X = generate_synthetic_features(date_str, model_data)
            
            # Scale and predict
            X_scaled = model_data['scaler'].transform(X)
            temp_c = model_data['model'].predict(X_scaled)[0]
            temp_f = celsius_to_fahrenheit(temp_c)
            
            # Simple feels-like adjustment
            feels_like_f = temp_f + 2.5  # Rough approximation
            
            predictions.append({
                'date': row['date'],
                'predicted_temp_f': temp_f,
                'predicted_feels_like_f': feels_like_f,
                'actual_temp_f': row['temp_mean_f'],
                'actual_feels_like_f': row['feels_like_mean_f']
            })
            
        except Exception as e:
            print(f"Error for {date_str}: {e}")
            continue
        
        if (idx + 1) % 50 == 0:
            print(f"Processed {idx + 1}/{len(weather_df)} days...")
    
    results_df = pd.DataFrame(predictions)
    print(f"\n✅ Generated {len(results_df)} predictions")
    
    return results_df

def analyze_results(results_df):
    """Analyze prediction accuracy"""
    print("\n" + "="*70)
    print("📊 RESULTS ANALYSIS")
    print("="*70)
    
    # Calculate errors
    results_df['error_temp_f'] = abs(results_df['actual_temp_f'] - results_df['predicted_temp_f'])
    results_df['error_feels_like_f'] = abs(results_df['actual_feels_like_f'] - results_df['predicted_feels_like_f'])
    
    # Metrics
    temp_mae = results_df['error_temp_f'].mean()
    temp_rmse = np.sqrt((results_df['error_temp_f']**2).mean())
    temp_r2 = r2_score(results_df['actual_temp_f'], results_df['predicted_temp_f'])
    
    feels_mae = results_df['error_feels_like_f'].mean()
    feels_rmse = np.sqrt((results_df['error_feels_like_f']**2).mean())
    feels_r2 = r2_score(results_df['actual_feels_like_f'], results_df['predicted_feels_like_f'])
    
    print("\n🌡️  TEMPERATURE METRICS (Fahrenheit):")
    print(f"  MAE:  {temp_mae:.2f}°F")
    print(f"  RMSE: {temp_rmse:.2f}°F")
    print(f"  R²:   {temp_r2:.4f}")
    
    print("\n🌡️  FEELS-LIKE METRICS (Fahrenheit):")
    print(f"  MAE:  {feels_mae:.2f}°F")
    print(f"  RMSE: {feels_rmse:.2f}°F")
    print(f"  R²:   {feels_r2:.4f}")
    
    # Monthly breakdown
    results_df['month'] = results_df['date'].dt.month
    monthly = results_df.groupby('month')['error_temp_f'].mean()
    
    print("\n📅 MONTHLY ERRORS (°F):")
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct']
    for month, error in monthly.items():
        print(f"  {month_names[month-1]}: {error:.2f}°F")
    
    # Assessment
    print("\n" + "="*70)
    print("🎯 ASSESSMENT")
    print("="*70)
    
    if temp_mae < 10:
        print("✅ Temperature: GOOD performance")
        needs_fix = False
    elif temp_mae < 15:
        print("⚠️  Temperature: ACCEPTABLE, could be improved")
        needs_fix = True
    else:
        print("❌ Temperature: NEEDS IMPROVEMENT")
        needs_fix = True
    
    # Save results
    output_path = os.path.join(DATA_DIR, 'validation_2025_quick.csv')
    results_df.to_csv(output_path, index=False)
    print(f"\n💾 Saved to: {output_path}")
    
    return {
        'temp_mae': temp_mae,
        'temp_rmse': temp_rmse,
        'temp_r2': temp_r2,
        'feels_mae': feels_mae,
        'feels_rmse': feels_rmse,
        'feels_r2': feels_r2,
        'needs_fix': needs_fix
    }

def main():
    print("\n" + "="*70)
    print("🌡️  QUICK MODEL VALIDATION - 2025")
    print("="*70)
    
    # Fetch data
    weather_df = fetch_2025_weather_data()
    
    # Load model
    model_data = load_model()
    
    # Make predictions
    results_df = predict_for_date_range(weather_df, model_data)
    
    # Analyze
    metrics = analyze_results(results_df)
    
    print("\n" + "="*70)
    print("✅ VALIDATION COMPLETE")
    print("="*70)
    
    if metrics['needs_fix']:
        print("\n⚠️  Model needs weight adjustment")
        print("Creating fix script...")
    else:
        print("\n✅ Model performance is acceptable")
    
    return results_df, metrics

if __name__ == "__main__":
    results_df, metrics = main()
