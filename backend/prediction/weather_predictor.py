"""
Unified Weather Prediction Interface

Provides predictions for:
- Temperature (feels-like)
- Precipitation
- Humidity
- Cloud Cover
- Wind Speed

Usage:
    from weather_predictor import WeatherPredictor

    predictor = WeatherPredictor()
    forecast = predictor.predict('2024-12-15', hour=14)
    print(forecast)

Author: Claude Code
Date: 2025-10-04
"""

import os
import sys
import pandas as pd
import numpy as np
import pickle
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Add temperature model to path
current_dir = os.path.dirname(__file__)
if current_dir:
    sys.path.insert(0, os.path.join(current_dir, 'temperature'))
else:
    sys.path.insert(0, 'backend/prediction/temperature')

from temperature_prediction_model import TemperaturePredictionModel


class WeatherPredictor:
    """Unified interface for all weather predictions"""

    def __init__(self, models_dir=None):
        """Initialize all weather prediction models"""
        if models_dir is None:
            # Determine models directory
            if os.path.basename(os.getcwd()) == 'prediction':
                self.models_dir = '../data/Modis'
                self.modis_dir = '../data/Modis'
            else:
                self.models_dir = 'backend/data/Modis'
                self.modis_dir = 'backend/data/Modis'
        else:
            self.models_dir = models_dir
            self.modis_dir = models_dir

        # Load MODIS data once (for feature extraction)
        self._load_modis_data()

        # Load all models
        self._load_models()

    def _load_modis_data(self):
        """Load MODIS satellite data for feature extraction"""
        print("Loading MODIS data...")

        try:
            mod09ga = pd.read_csv(os.path.join(self.modis_dir, 'Chicago-MOD09GA.csv'))
            mod10a1 = pd.read_csv(os.path.join(self.modis_dir, 'Chicago-MOD10A1.csv'))
            mod11a1 = pd.read_csv(os.path.join(self.modis_dir, 'Chicago-MOD11A1.csv'))
            mod13a1 = pd.read_csv(os.path.join(self.modis_dir, 'Chicago-MOD13A1.csv'))
            mod16a2 = pd.read_csv(os.path.join(self.modis_dir, 'Chicago-MOD16A2.csv'))

            # Merge all
            self.modis_df = mod09ga.merge(mod10a1, on='Date', how='outer', suffixes=('', '_drop'))
            self.modis_df = self.modis_df.merge(mod11a1, on='Date', how='outer', suffixes=('', '_drop'))
            self.modis_df = self.modis_df.merge(mod13a1, on='Date', how='outer', suffixes=('', '_drop'))
            self.modis_df = self.modis_df.merge(mod16a2, on='Date', how='outer', suffixes=('', '_drop'))

            # Drop duplicate columns
            self.modis_df = self.modis_df.loc[:, ~self.modis_df.columns.str.endswith('_drop')]

            self.modis_df['Date'] = pd.to_datetime(self.modis_df['Date'])

            print(f"[OK] Loaded {len(self.modis_df)} MODIS records")

        except Exception as e:
            print(f"[!] Warning: Could not load MODIS data: {e}")
            print("    Predictions will use default values")
            self.modis_df = None

    def _load_models(self):
        """Load all prediction models"""
        print("Loading prediction models...")

        # Temperature model - load the fixed pickle
        temp_model_path = os.path.join(self.models_dir, 'temperature_model_fixed.pkl')

        with open(temp_model_path, 'rb') as f:
            temp_data = pickle.load(f)

        # Reconstruct temperature model
        self.temp_model = TemperaturePredictionModel()
        self.temp_model.model = temp_data['model']
        self.temp_model.scaler = temp_data['scaler']
        self.temp_model.feature_names = temp_data['feature_names']
        self.temp_model.feature_importance = temp_data.get('feature_importance')

        # Precipitation model
        with open(os.path.join(self.models_dir, 'precipitation_model.pkl'), 'rb') as f:
            self.precip_model = pickle.load(f)

        # Humidity model
        with open(os.path.join(self.models_dir, 'humidity_model.pkl'), 'rb') as f:
            self.humidity_model = pickle.load(f)

        # Cloud cover model
        with open(os.path.join(self.models_dir, 'cloud_model.pkl'), 'rb') as f:
            self.cloud_model = pickle.load(f)

        # Wind model
        with open(os.path.join(self.models_dir, 'wind_model.pkl'), 'rb') as f:
            self.wind_model = pickle.load(f)

        print("[OK] All models loaded")

    def _get_modis_features(self, date_str):
        """Extract MODIS features for a given date"""
        if self.modis_df is None:
            return None

        # Find closest date
        target_date = pd.to_datetime(date_str)
        self.modis_df['date_diff'] = abs((self.modis_df['Date'] - target_date).dt.days)
        closest = self.modis_df.loc[self.modis_df['date_diff'].idxmin()]

        return closest

    def predict(self, date_str, hour=12, verbose=True):
        """
        Predict all weather variables for a specific date and hour

        Args:
            date_str: Date in 'YYYY-MM-DD' format
            hour: Hour of day (0-23)
            verbose: Print detailed output

        Returns:
            Dictionary with all weather predictions
        """
        if verbose:
            print(f"\n{'='*70}")
            print(f"WEATHER FORECAST FOR {date_str} at {hour}:00")
            print(f"{'='*70}")

        # Get MODIS features for this date
        modis_features = self._get_modis_features(date_str)

        # Extract features (use defaults if not available)
        if modis_features is not None:
            lst_day = modis_features.get('MOD11A1_061_LST_Day_1km', 288.0)
            lst_night = modis_features.get('MOD11A1_061_LST_Night_1km', 280.0)
            clear_day = modis_features.get('MOD11A1_061_Clear_day_cov', 0.5)
            clear_night = modis_features.get('MOD11A1_061_Clear_night_cov', 0.5)
            et_500m = modis_features.get('MOD16A2_061_ET_500m', 50.0)
            le_500m = modis_features.get('MOD16A2_061_LE_500m', 100.0)
            snow_cover = modis_features.get('MOD10A1_061_NDSI_Snow_Cover', 0.0)
            evi = modis_features.get('MOD13A1_061__500m_16_days_EVI', 0.3)
        else:
            # Use defaults
            lst_day, lst_night = 288.0, 280.0
            clear_day, clear_night = 0.5, 0.5
            et_500m, le_500m = 50.0, 100.0
            snow_cover, evi = 0.0, 0.3

        # 1. Temperature prediction
        temp_result = self.temp_model.predict_feels_like_temperature(
            date_str, hour,
            lst_day=lst_day,
            lst_night=lst_night,
            cloud_cover_day=clear_day,
            cloud_cover_night=clear_night
        )

        # 2. Precipitation prediction
        precip_features = self._build_features(date_str, self.precip_model['feature_names'], modis_features)
        X_precip = self.precip_model['scaler'].transform(precip_features)
        precip_mm = self.precip_model['model'].predict(X_precip)[0]

        # Adjust for time of day
        if 5 <= hour <= 8:
            precip_mm *= 1.1
        elif 15 <= hour <= 18:
            precip_mm *= 1.2
        elif 21 <= hour or hour <= 3:
            precip_mm *= 0.9

        precip_mm = max(0, precip_mm)

        # Convert to probability
        if precip_mm < 0.1:
            precip_prob = 0
        elif precip_mm < 1.0:
            precip_prob = min(30, precip_mm * 30)
        elif precip_mm < 2.5:
            precip_prob = 30 + min(40, (precip_mm - 1.0) * 26.67)
        else:
            precip_prob = 70 + min(30, (precip_mm - 2.5) * 6)

        # 3. Humidity prediction
        humidity_features = self._build_features(date_str, self.humidity_model['feature_names'], modis_features)
        X_humidity = self.humidity_model['scaler'].transform(humidity_features)
        humidity_pa = self.humidity_model['model'].predict(X_humidity)[0]
        humidity_pct = min(100, max(0, humidity_pa / 30))  # Convert to percentage

        # 4. Cloud cover prediction
        cloud_features = self._build_features(date_str, self.cloud_model['feature_names'], modis_features)
        X_cloud = self.cloud_model['scaler'].transform(cloud_features)
        cloud_pct = self.cloud_model['model'].predict(X_cloud)[0]
        cloud_pct = min(100, max(0, cloud_pct))

        # 5. Wind speed prediction
        wind_features = self._build_features(date_str, self.wind_model['feature_names'], modis_features)
        X_wind = self.wind_model['scaler'].transform(wind_features)
        wind_proxy = self.wind_model['model'].predict(X_wind)[0]
        wind_ms = (wind_proxy - 330) / 2  # Convert to m/s

        # Compile results
        forecast = {
            'date': date_str,
            'hour': hour,
            'temperature_c': temp_result['predicted_temperature'],
            'feels_like_c': temp_result['feels_like_temperature'],
            'precipitation_mm': round(precip_mm, 2),
            'precipitation_probability_pct': round(precip_prob, 1),
            'humidity_pct': round(humidity_pct, 1),
            'cloud_cover_pct': round(cloud_pct, 1),
            'wind_speed_ms': round(max(0, wind_ms), 1)
        }

        if verbose:
            print(f"\n Temperature:     {forecast['feels_like_c']:.1f}°C (feels like)")
            print(f" Precipitation:  {forecast['precipitation_mm']:.1f}mm ({forecast['precipitation_probability_pct']:.0f}% probability)")
            print(f" Humidity:       {forecast['humidity_pct']:.0f}%")
            print(f" Cloud Cover:    {forecast['cloud_cover_pct']:.0f}%")
            print(f" Wind Speed:     {forecast['wind_speed_ms']:.1f} m/s")

            # Weather summary
            print(f"\n Summary: ", end="")
            if cloud_pct > 70:
                print("Cloudy", end="")
            elif cloud_pct > 40:
                print("Partly cloudy", end="")
            else:
                print("Clear", end="")

            if precip_prob > 50:
                print(f" with rain likely ({precip_mm:.1f}mm expected)")
            elif precip_prob > 20:
                print(f" with possible light rain")
            else:
                print("")

        return forecast

    def _build_features(self, date_str, feature_names, modis_features):
        """Build feature vector for prediction"""
        date_obj = pd.to_datetime(date_str)

        features = {}
        for feat in feature_names:
            if feat == 'month':
                features[feat] = date_obj.month
            elif feat == 'day_of_year':
                features[feat] = date_obj.dayofyear
            elif feat == 'season':
                features[feat] = ((date_obj.month % 12) + 3) // 3
            elif modis_features is not None:
                features[feat] = modis_features.get(feat, 0)
            else:
                features[feat] = 0

        return pd.DataFrame([features])[feature_names]

    def predict_range(self, start_date, end_date, hour=12):
        """Predict for a range of dates"""
        results = []

        current = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)

        while current <= end:
            date_str = current.strftime('%Y-%m-%d')
            forecast = self.predict(date_str, hour=hour, verbose=False)
            results.append(forecast)
            current += pd.Timedelta(days=1)

        return pd.DataFrame(results)


if __name__ == "__main__":
    # Demo
    predictor = WeatherPredictor()

    # Single prediction
    forecast = predictor.predict('2024-12-15', hour=14)

    # Range prediction (silent)
    print(f"\n\n{'='*70}")
    print("5-DAY FORECAST")
    print(f"{'='*70}\n")

    df = predictor.predict_range('2024-12-15', '2024-12-19', hour=14)
    print(df[['date', 'feels_like_c', 'precipitation_mm', 'humidity_pct',
             'cloud_cover_pct', 'wind_speed_ms']].to_string(index=False))
