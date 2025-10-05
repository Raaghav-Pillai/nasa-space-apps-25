"""
Validate models against ALL 2025 data (Jan 1 - Oct 1)
Uses predict.py to get predictions and compares with real weather data
All temperatures in FAHRENHEIT

Author: Kiro AI
Date: 2025-10-04
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from predict import predict_daily_range
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

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
                  'precipitation_sum'],
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
            'precipitation_mm': daily['precipitation_sum']
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

def get_model_predictions(start_date, end_date):
    """Get predictions from the model for date range"""
    print("\n" + "="*70)
    print("GETTING MODEL PREDICTIONS")
    print("="*70)
    
    try:
        predictions_df = predict_daily_range(start_date, end_date)
        
        # Convert to Fahrenheit
        predictions_df['avg_temperature_f'] = predictions_df['avg_temperature'].apply(celsius_to_fahrenheit)
        predictions_df['avg_feels_like_f'] = predictions_df['avg_feels_like'].apply(celsius_to_fahrenheit)
        
        print(f"\n✅ Generated {len(predictions_df)} daily predictions")
        print(f"\nPredicted Temperature Statistics (Fahrenheit):")
        print(f"  Mean: {predictions_df['avg_temperature_f'].mean():.1f}°F")
        print(f"  Min:  {predictions_df['avg_temperature_f'].min():.1f}°F")
        print(f"  Max:  {predictions_df['avg_temperature_f'].max():.1f}°F")
        
        return predictions_df
        
    except Exception as e:
        print(f"❌ Error getting predictions: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def compare_predictions(actual_df, predicted_df):
    """Compare actual vs predicted values"""
    print("\n" + "="*70)
    print("COMPARING PREDICTIONS WITH ACTUAL DATA")
    print("="*70)
    
    # Merge dataframes
    actual_df['date'] = actual_df['date'].dt.strftime('%Y-%m-%d')
    
    merged = actual_df.merge(predicted_df, on='date', how='inner')
    
    if len(merged) == 0:
        print("❌ No matching dates found between actual and predicted data")
        return None
    
    print(f"\n✅ Matched {len(merged)} days")
    
    # Calculate errors
    merged['error_temp_f'] = abs(merged['temp_mean_f'] - merged['avg_temperature_f'])
    merged['error_feels_like_f'] = abs(merged['feels_like_mean_f'] - merged['avg_feels_like_f'])
    merged['error_precipitation_mm'] = abs(merged['precipitation_mm'] - merged['total_precipitation'])
    
    return merged

def analyze_results(results_df):
    """Analyze and display results"""
    print("\n" + "="*70)
    print("📊 VALIDATION RESULTS")
    print("="*70)
    
    # Temperature metrics
    temp_mae = results_df['error_temp_f'].mean()
    temp_rmse = np.sqrt((results_df['error_temp_f']**2).mean())
    temp_max_error = results_df['error_temp_f'].max()
    
    # Feels-like metrics
    feels_mae = results_df['error_feels_like_f'].mean()
    feels_rmse = np.sqrt((results_df['error_feels_like_f']**2).mean())
    feels_max_error = results_df['error_feels_like_f'].max()
    
    # Precipitation metrics
    precip_mae = results_df['error_precipitation_mm'].mean()
    precip_rmse = np.sqrt((results_df['error_precipitation_mm']**2).mean())
    
    print("\n🌡️  TEMPERATURE METRICS (Fahrenheit):")
    print(f"  Mean Absolute Error (MAE):     {temp_mae:.2f}°F")
    print(f"  Root Mean Square Error (RMSE): {temp_rmse:.2f}°F")
    print(f"  Maximum Error:                 {temp_max_error:.2f}°F")
    
    print("\n🌡️  FEELS-LIKE TEMPERATURE METRICS (Fahrenheit):")
    print(f"  Mean Absolute Error (MAE):     {feels_mae:.2f}°F")
    print(f"  Root Mean Square Error (RMSE): {feels_rmse:.2f}°F")
    print(f"  Maximum Error:                 {feels_max_error:.2f}°F")
    
    print("\n🌧️  PRECIPITATION METRICS (mm):")
    print(f"  Mean Absolute Error (MAE):     {precip_mae:.2f} mm")
    print(f"  Root Mean Square Error (RMSE): {precip_rmse:.2f} mm")
    
    # Calculate R² scores
    from sklearn.metrics import r2_score
    temp_r2 = r2_score(results_df['temp_mean_f'], results_df['avg_temperature_f'])
    feels_r2 = r2_score(results_df['feels_like_mean_f'], results_df['avg_feels_like_f'])
    
    print(f"\n📈 R² SCORES:")
    print(f"  Temperature: {temp_r2:.4f}")
    print(f"  Feels-Like:  {feels_r2:.4f}")
    
    # Monthly breakdown
    results_df['month'] = pd.to_datetime(results_df['date']).dt.month
    monthly_stats = results_df.groupby('month').agg({
        'error_temp_f': 'mean',
        'error_feels_like_f': 'mean'
    }).round(2)
    
    month_names = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                   7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct'}
    monthly_stats.index = monthly_stats.index.map(month_names)
    
    print("\n📅 MONTHLY ERROR BREAKDOWN (°F):")
    print(monthly_stats.to_string())
    
    # Performance assessment
    print("\n" + "="*70)
    print("🎯 PERFORMANCE ASSESSMENT")
    print("="*70)
    
    if temp_mae < 5.0:
        print("✅ Temperature predictions: EXCELLENT (MAE < 5°F)")
        needs_fix = False
    elif temp_mae < 10.0:
        print("✅ Temperature predictions: GOOD (MAE < 10°F)")
        needs_fix = False
    elif temp_mae < 15.0:
        print("⚠️  Temperature predictions: ACCEPTABLE (MAE < 15°F)")
        needs_fix = True
    else:
        print("❌ Temperature predictions: NEEDS IMPROVEMENT (MAE >= 15°F)")
        needs_fix = True
    
    if feels_mae < 5.0:
        print("✅ Feels-like predictions: EXCELLENT (MAE < 5°F)")
    elif feels_mae < 10.0:
        print("✅ Feels-like predictions: GOOD (MAE < 10°F)")
    elif feels_mae < 15.0:
        print("⚠️  Feels-like predictions: ACCEPTABLE (MAE < 15°F)")
        needs_fix = True
    else:
        print("❌ Feels-like predictions: NEEDS IMPROVEMENT (MAE >= 15°F)")
        needs_fix = True
    
    # Save results
    output_path = '../data/Modis/validation_results_2025_complete.csv'
    results_df.to_csv(output_path, index=False)
    print(f"\n💾 Results saved to: {output_path}")
    
    return {
        'temp_mae': temp_mae,
        'temp_rmse': temp_rmse,
        'feels_mae': feels_mae,
        'feels_rmse': feels_rmse,
        'temp_r2': temp_r2,
        'feels_r2': feels_r2,
        'needs_fix': needs_fix
    }

def main():
    """Main execution"""
    print("\n" + "="*70)
    print("🌡️  MODEL VALIDATION - 2025 COMPLETE DATA")
    print("="*70)
    print("Testing Period: January 1 - October 1, 2025")
    print("Location: Chicago, IL")
    print("Units: Fahrenheit")
    print("="*70)
    
    # Step 1: Fetch real 2025 weather data
    actual_df = fetch_2025_weather_data()
    if actual_df is None:
        print("\n❌ Failed to fetch weather data. Exiting.")
        return None, None
    
    # Step 2: Get model predictions
    predicted_df = get_model_predictions('2025-01-01', '2025-10-01')
    if predicted_df is None:
        print("\n❌ Failed to get predictions. Exiting.")
        return None, None
    
    # Step 3: Compare predictions
    results_df = compare_predictions(actual_df, predicted_df)
    if results_df is None:
        print("\n❌ Failed to compare data. Exiting.")
        return None, None
    
    # Step 4: Analyze results
    metrics = analyze_results(results_df)
    
    # Step 5: Recommendations
    print("\n" + "="*70)
    print("🔧 NEXT STEPS")
    print("="*70)
    
    if metrics['needs_fix']:
        print("\n⚠️  Model performance needs improvement!")
        print("\nRecommended actions:")
        print("1. Run weight adjustment script to reduce bias")
        print("2. Apply seasonal correction factors")
        print("3. Fine-tune model parameters")
        print("\nI will now create a script to fix the model weights...")
    else:
        print("\n✅ Model performance is good!")
        print("No immediate action needed.")
        print("Model is ready for production use.")
    
    print("\n" + "="*70)
    print("✅ VALIDATION COMPLETE")
    print("="*70)
    
    return results_df, metrics

if __name__ == "__main__":
    results_df, metrics = main()
