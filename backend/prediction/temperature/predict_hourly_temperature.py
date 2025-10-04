"""
Demo script for hourly "feels like" temperature prediction.
Shows how to predict temperature for any date and hour.
"""

import joblib
import sys
import os

# Import the model class
from temperature_prediction_model import TemperaturePredictionModel

def load_trained_model(model_path='../../data/Modis/temperature_model.pkl'):
    """Load the pre-trained model"""
    print(f"Loading model from {model_path}...")
    model = joblib.load(model_path)
    print("[OK] Model loaded successfully!\n")
    return model

def predict_hourly_temperatures(model, date, hours_to_predict=None):
    """
    Predict temperatures for multiple hours of a given date.

    Args:
        model: Trained TemperaturePredictionModel instance
        date: Date string in 'YYYY-MM-DD' format
        hours_to_predict: List of hours to predict (default: all 24 hours)
    """
    if hours_to_predict is None:
        hours_to_predict = range(24)  # All hours 0-23

    print("="*80)
    print(f"Hourly Temperature Predictions for {date}")
    print("="*80)

    results = []

    for hour in hours_to_predict:
        # You can provide actual satellite data here if available
        # For demo, we'll use default values which are estimated
        result = model.predict_feels_like_temperature(
            date_str=date,
            hour=hour,
            # Optional: Provide actual satellite readings if available
            # lst_day=288.0,  # Example: 15°C in Kelvin
            # lst_night=280.0,  # Example: 7°C in Kelvin
            # cloud_cover_day=0.8,
            # cloud_cover_night=0.9,
        )

        results.append(result)

        # Print formatted output
        print(f"\n{hour:02d}:00 - {result['time_period'].upper()}")
        print(f"  Predicted Temperature: {result['predicted_temperature']}°C")
        print(f"  Feels Like: {result['feels_like_temperature']}°C")
        print(f"  Condition: {result['description']}")
        print(f"  Day/Night Weight: {result['time_weight_day']:.1%} day, {result['time_weight_night']:.1%} night")

    return results

def predict_specific_time(model, date, hour, **kwargs):
    """
    Predict temperature for a specific date and hour with custom parameters.

    Args:
        model: Trained model
        date: Date string 'YYYY-MM-DD'
        hour: Hour (0-23)
        **kwargs: Optional satellite parameters (lst_day, lst_night, cloud_cover, etc.)
    """
    print("="*80)
    print(f"Temperature Prediction for {date} at {hour:02d}:00")
    print("="*80)

    result = model.predict_feels_like_temperature(
        date_str=date,
        hour=hour,
        **kwargs
    )

    print(f"\nTime Period: {result['time_period'].upper()}")
    print(f"Predicted Temperature: {result['predicted_temperature']}°C")
    print(f"Feels Like Temperature: {result['feels_like_temperature']}°C")
    print(f"Description: {result['description']}")
    print(f"\nDetails:")
    print(f"  - Day LST: {result['lst_day_celsius']}°C")
    print(f"  - Night LST: {result['lst_night_celsius']}°C")
    print(f"  - Cloud Cover (Day): {result['cloud_cover_day']:.2%}")
    print(f"  - Cloud Cover (Night): {result['cloud_cover_night']:.2%}")
    print(f"  - Day Weight: {result['time_weight_day']:.1%}")
    print(f"  - Night Weight: {result['time_weight_night']:.1%}")

    return result

def demo_predictions():
    """Run demonstration predictions"""
    # Load the trained model
    model = load_trained_model()

    print("\n" + "="*80)
    print("DEMO 1: Predict all 24 hours for a specific date")
    print("="*80)

    # Example 1: Predict all hours for January 15, 2024
    results_all_hours = predict_hourly_temperatures(
        model,
        date='2024-01-15',
        hours_to_predict=range(0, 24, 3)  # Every 3 hours for brevity
    )

    print("\n" + "="*80)
    print("DEMO 2: Predict specific time with custom parameters")
    print("="*80)

    # Example 2: Predict for a specific time with actual satellite data
    result_afternoon = predict_specific_time(
        model,
        date='2024-07-20',
        hour=14,  # 2 PM
        lst_day=303.15,  # 30°C in Kelvin (hot summer day)
        lst_night=293.15,  # 20°C in Kelvin
        cloud_cover_day=0.9,  # 90% clear (10% clouds)
        cloud_cover_night=0.8,  # 80% clear
        sur_refl_bands=[0.20, 0.25, 0.15, 0.20, 0.22, 0.15, 0.10]  # Reflectance values
    )

    print("\n" + "="*80)
    print("DEMO 3: Compare morning, afternoon, evening, and night")
    print("="*80)

    key_hours = [8, 14, 19, 23]  # Morning, afternoon, evening, night
    for h in key_hours:
        result = predict_specific_time(
            model,
            date='2024-03-15',
            hour=h,
            lst_day=285.15,  # 12°C
            lst_night=278.15,  # 5°C
            cloud_cover_day=0.6,  # 60% clear (40% clouds)
            cloud_cover_night=0.7
        )
        print()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Predict hourly "feels like" temperature')
    parser.add_argument('--date', type=str, help='Date in YYYY-MM-DD format')
    parser.add_argument('--hour', type=int, help='Hour (0-23)')
    parser.add_argument('--demo', action='store_true', help='Run demo predictions')

    args = parser.parse_args()

    if args.demo or (not args.date and not args.hour):
        # Run demo
        demo_predictions()
    else:
        # Load model
        model = load_trained_model()

        if args.date and args.hour is not None:
            # Predict specific time
            predict_specific_time(model, args.date, args.hour)
        elif args.date:
            # Predict all hours for date
            predict_hourly_temperatures(model, args.date)
        else:
            print("Please provide --date and optionally --hour, or use --demo")
