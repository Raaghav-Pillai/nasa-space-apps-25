"""
Test trained models against ALL 2025 data (Jan 1 - Oct 1)
Fetch real weather data and validate predictions in Fahrenheit

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
import warnings
warnings.filterwarnings('ignore')

# Determine correct path based on where script is run from
if os.path.basename(os.getcwd()) == 'prediction':
    DATA_DIR = '../data/Modis'
else:
    DATA_DIR = 'backend/data/Modis'

def celsius_to_fahrenheit(celsius):
    """Convert Celsius to Fahrenheit"""
    return (celsius * 9/5) + 32

def fetch_2025_weather_data():
    """Fetch real 2025 weather data from Open-Meteo API"""
    print("="*70)
    print("FETCHING 2025 WEATHER DATA (Jan 1 - Oct 1)")
    print("="*70)
    
    # Chicago coordinates
    lat = 41.8781
    lon = -87.6298
    
    # Date range
    start_date = '2025-01-01'
    end_date = '2025-10-01'
    
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        'latitude': lat,
        'longitude': lon,
        'start_date': start_date,
        'end_date': end_date,
        'daily': ['temperature_2m_max', 'temperature_2m_min', 'temperature_2m_mean',
                  'apparent_temperature_max', 'apparent_temperature_min',
                  'precipitation_sum', 'rain_sum', 'snowfall_sum',
                  'wind_speed_10m_max', 'wind_gusts_10m_max'],
        'timezone': 'America/Chicago',
        'temperature_unit': 'fahrenheit'
    }
    
    print(f"\nFetching data from {start_date} to {end_date}...")
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Parse into DataFrame
        daily = data['daily']
        df = pd.DataFrame({
            'date': pd.to_datetime(daily['time']),
            'temp_max_f': daily['temperature_2m_max'],
            'temp_min_f': daily['temperature_2m_min'],
            'temp_mean_f': daily['temperature_2m_mean'],
            'feels_like_max_f': daily['apparent_temperature_max'],
            'feels_like_min_f': daily['apparent_temperature_min'],
            'precipitation_mm': daily['precipitation_sum'],
            'rain_mm': daily['rain_sum'],
            'snowfall_cm': daily['snowfall_sum'],
            'wind_speed_max_kmh': daily['wind_speed_10m_max'],
            'wind_gusts_kmh': daily['wind_gusts_10m_max']
        })
        
        # Calculate average feels-like temperature
        df['feels_like_mean_f'] = (df['feels_like_max_f'] + df['feels_like_min_f']) / 2
        
        print(f"\n✅ Successfully fetched {len(df)} days of data")
        print(f"\nTemperature Statistics (Fahrenheit):")
        print(f"  Mean: {df['temp_mean_f'].mean():.1f}°F")
        print(f"  Min:  {df['temp_min_f'].min():.1f}°F")
        print(f"  Max:  {df['temp_max_f'].max():.1f}°F")
        print(f"\nFeels Like Statistics (Fahrenheit):")
        print(f"  Mean: {df['feels_like_mean_f'].mean():.1f}°F")
        print(f"  Min:  {df['feels_like_min_f'].min():.1f}°F")
        print(f"  Max:  {df['feels_like_max_f'].max():.1f}°F")
        
        return df
        
    except Exception as e:
        print(f"❌ Error fetching data: {str(e)}")
        return None

def load_temperature_model():
    """Load the trained temperature model"""
    print("\n" + "="*70)
    print("LOADING TEMPERATURE MODEL")
    print("="*70)
    
    # Try the joblib model first (has predict_feels_like_temperature method)
    model_path = os.path.join(DATA_DIR, 'temperature_model.pkl')
    
    if not os.path.exists(model_path):
        print(f"❌ Model not found at {model_path}")
        print("Trying full model...")
        model_path = os.path.join(DATA_DIR, 'temperature_model_full.pkl')
    
    try:
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        print(f"✅ Model loaded from {model_path}")
        
        # Check if it's the old format (joblib) or new format (dict)
        if hasattr(model_data, 'predict_feels_like_temperature'):
            # Old format - it's the model object itself
            print("  Format: Model object")
            return {'model_object': model_data}
        else:
            # New format - dictionary with model, scaler, features
            print("  Format: Dictionary")
            print(f"  Features: {len(model_data.get('feature_names', []))}")
            return model_data
            
    except Exception as e:
        print(f"❌ Error loading model: {str(e)}")
        return None

def predict_temperatures_2025(weather_df, model_data):
    """Make predictions for all 2025 dates"""
    print("\n" + "="*70)
    print("MAKING PREDICTIONS FOR 2025 DATA")
    print("="*70)
    
    predictions = []
    
    # Check model format
    if 'model_object' in model_data:
        # Old format - use the model object's method
        model_obj = model_data['model_object']
        
        print("\nUsing model object's predict_feels_like_temperature method...")
        
        for idx, row in weather_df.iterrows():
            date_str = row['date'].strftime('%Y-%m-%d')
            
            # Predict for noon (hour 12)
            try:
                result = model_obj.predict_feels_like_temperature(
                    date_str=date_str,
                    hour=12
                )
                
                # Convert to Fahrenheit
                pred_temp_f = celsius_to_fahrenheit(result['predicted_temperature'])
                feels_like_f = celsius_to_fahrenheit(result['feels_like_temperature'])
                
                predictions.append({
                    'date': row['date'],
                    'actual_temp_f': row['temp_mean_f'],
                    'actual_feels_like_f': row['feels_like_mean_f'],
                    'predicted_temp_f': pred_temp_f,
                    'predicted_feels_like_f': feels_like_f,
                    'error_temp_f': abs(row['temp_mean_f'] - pred_temp_f),
                    'error_feels_like_f': abs(row['feels_like_mean_f'] - feels_like_f)
                })
                
            except Exception as e:
                print(f"  Error predicting for {date_str}: {str(e)}")
                continue
    
    else:
        # New format - use model, scaler, features
        print("\nUsing model dictionary format...")
        print("⚠️  This format requires MODIS satellite data for predictions")
        print("⚠️  Cannot make predictions without satellite features")
        return None
    
    if not predictions:
        print("❌ No predictions were made")
        return None
    
    results_df = pd.DataFrame(predictions)
    print(f"\n✅ Made {len(results_df)} predictions")
    
    return results_df

def analyze_results(results_df):
    """Analyze prediction results and calculate metrics"""
    print("\n" + "="*70)
    print("PREDICTION RESULTS ANALYSIS")
    print("="*70)
    
    # Temperature metrics
    temp_mae = results_df['error_temp_f'].mean()
    temp_rmse = np.sqrt((results_df['error_temp_f']**2).mean())
    temp_max_error = results_df['error_temp_f'].max()
    
    # Feels-like metrics
    feels_mae = results_df['error_feels_like_f'].mean()
    feels_rmse = np.sqrt((results_df['error_feels_like_f']**2).mean())
    feels_max_error = results_df['error_feels_like_f'].max()
    
    print("\n📊 TEMPERATURE PREDICTION METRICS (Fahrenheit):")
    print(f"  Mean Absolute Error (MAE):  {temp_mae:.2f}°F")
    print(f"  Root Mean Square Error (RMSE): {temp_rmse:.2f}°F")
    print(f"  Maximum Error: {temp_max_error:.2f}°F")
    
    print("\n📊 FEELS-LIKE TEMPERATURE METRICS (Fahrenheit):")
    print(f"  Mean Absolute Error (MAE):  {feels_mae:.2f}°F")
    print(f"  Root Mean Square Error (RMSE): {feels_rmse:.2f}°F")
    print(f"  Maximum Error: {feels_max_error:.2f}°F")
    
    # Calculate R² score
    from sklearn.metrics import r2_score
    temp_r2 = r2_score(results_df['actual_temp_f'], results_df['predicted_temp_f'])
    feels_r2 = r2_score(results_df['actual_feels_like_f'], results_df['predicted_feels_like_f'])
    
    print(f"\n📈 R² SCORES:")
    print(f"  Temperature: {temp_r2:.4f}")
    print(f"  Feels-Like:  {feels_r2:.4f}")
    
    # Monthly breakdown
    results_df['month'] = results_df['date'].dt.month
    monthly_stats = results_df.groupby('month').agg({
        'error_temp_f': 'mean',
        'error_feels_like_f': 'mean'
    }).round(2)
    
    print("\n📅 MONTHLY ERROR BREAKDOWN:")
    print(monthly_stats.to_string())
    
    # Performance assessment
    print("\n" + "="*70)
    print("PERFORMANCE ASSESSMENT")
    print("="*70)
    
    if temp_mae < 5.0:
        print("✅ Temperature predictions: EXCELLENT (MAE < 5°F)")
    elif temp_mae < 10.0:
        print("✅ Temperature predictions: GOOD (MAE < 10°F)")
    elif temp_mae < 15.0:
        print("⚠️  Temperature predictions: ACCEPTABLE (MAE < 15°F)")
    else:
        print("❌ Temperature predictions: NEEDS IMPROVEMENT (MAE >= 15°F)")
        print("   → Model weights need adjustment")
    
    if feels_mae < 5.0:
        print("✅ Feels-like predictions: EXCELLENT (MAE < 5°F)")
    elif feels_mae < 10.0:
        print("✅ Feels-like predictions: GOOD (MAE < 10°F)")
    elif feels_mae < 15.0:
        print("⚠️  Feels-like predictions: ACCEPTABLE (MAE < 15°F)")
    else:
        print("❌ Feels-like predictions: NEEDS IMPROVEMENT (MAE >= 15°F)")
        print("   → Model weights need adjustment")
    
    # Save results
    output_path = os.path.join(DATA_DIR, 'validation_results_2025_full.csv')
    results_df.to_csv(output_path, index=False)
    print(f"\n💾 Results saved to: {output_path}")
    
    return {
        'temp_mae': temp_mae,
        'temp_rmse': temp_rmse,
        'feels_mae': feels_mae,
        'feels_rmse': feels_rmse,
        'temp_r2': temp_r2,
        'feels_r2': feels_r2
    }

def main():
    """Main execution"""
    print("\n" + "="*70)
    print("🌡️  TEMPERATURE MODEL VALIDATION - 2025 DATA")
    print("="*70)
    print("Testing Period: January 1 - October 1, 2025")
    print("Location: Chicago, IL")
    print("Units: Fahrenheit")
    print("="*70)
    
    # Step 1: Fetch real 2025 weather data
    weather_df = fetch_2025_weather_data()
    if weather_df is None:
        print("\n❌ Failed to fetch weather data. Exiting.")
        return
    
    # Step 2: Load trained model
    model_data = load_temperature_model()
    if model_data is None:
        print("\n❌ Failed to load model. Exiting.")
        return
    
    # Step 3: Make predictions
    results_df = predict_temperatures_2025(weather_df, model_data)
    if results_df is None:
        print("\n❌ Failed to make predictions. Exiting.")
        return
    
    # Step 4: Analyze results
    metrics = analyze_results(results_df)
    
    # Step 5: Recommendations
    print("\n" + "="*70)
    print("🎯 NEXT STEPS")
    print("="*70)
    
    if metrics['temp_mae'] > 10.0 or metrics['feels_mae'] > 10.0:
        print("\n⚠️  Model performance needs improvement!")
        print("\nRecommended actions:")
        print("1. Adjust model weights to reduce bias")
        print("2. Retrain with more recent data")
        print("3. Add seasonal adjustment factors")
        print("\nRun: python backend/prediction/fix_model_weights.py")
    else:
        print("\n✅ Model performance is good!")
        print("No immediate action needed.")
    
    print("\n" + "="*70)
    print("VALIDATION COMPLETE")
    print("="*70)
    
    return results_df, metrics

if __name__ == "__main__":
    results_df, metrics = main()
