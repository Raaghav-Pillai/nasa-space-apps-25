"""
Precipitation Prediction Model using MODIS Satellite Data

This model predicts precipitation using:
- MOD10A1: Snow cover and quality data
- MOD16A2: Evapotranspiration and latent heat flux
- MOD13A1: Vegetation indices (EVI, VI Quality)

Author: Claude Code
Date: 2025-10-04
"""

import os
import sys
import pandas as pd
import numpy as np
import pickle
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge, Lasso
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')


class PrecipitationPredictionModel:
    """Precipitation prediction using MODIS satellite data"""

    def __init__(self, data_dir='backend/data/Modis'):
        """Initialize the model"""
        # Handle running from different directories
        current_dir = os.getcwd()
        if os.path.basename(current_dir) == 'backend':
            self.data_dir = 'data/Modis'
        elif os.path.basename(current_dir) == 'precipitation':
            self.data_dir = '../../data/Modis'
        else:
            self.data_dir = data_dir

        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.feature_importance = None

    def load_and_merge_data(self):
        """Load and merge all MODIS datasets with Daymet precipitation data"""
        print("\n" + "="*70)
        print("Loading MODIS Data for Precipitation Prediction")
        print("="*70)

        # Determine Daymet path
        if os.path.basename(self.data_dir) == 'Modis':
            daymet_path = os.path.join(os.path.dirname(self.data_dir), 'Daymet',
                                       'Daymet-Chicago-Past-Year-DAYMET-004-results.csv')
        else:
            daymet_path = 'backend/data/Daymet/Daymet-Chicago-Past-Year-DAYMET-004-results.csv'

        # Load datasets
        print("\nLoading datasets...")
        mod10a1 = pd.read_csv(os.path.join(self.data_dir, 'Chicago-MOD10A1.csv'))
        mod16a2 = pd.read_csv(os.path.join(self.data_dir, 'Chicago-MOD16A2.csv'))
        mod13a1 = pd.read_csv(os.path.join(self.data_dir, 'Chicago-MOD13A1.csv'))
        daymet = pd.read_csv(daymet_path)

        print(f"  MOD10A1 (Snow): {len(mod10a1)} records")
        print(f"  MOD16A2 (Evapotranspiration): {len(mod16a2)} records")
        print(f"  MOD13A1 (Vegetation): {len(mod13a1)} records")
        print(f"  Daymet (Weather): {len(daymet)} records")

        # Select relevant columns
        mod10a1_cols = ['Date', 'MOD10A1_061_NDSI_Snow_Cover',
                        'MOD10A1_061_NDSI_Snow_Cover_Algorithm_Flags_QA']
        mod16a2_cols = ['Date', 'MOD16A2_061_ET_500m', 'MOD16A2_061_LE_500m']
        mod13a1_cols = ['Date', 'MOD13A1_061__500m_16_days_EVI',
                        'MOD13A1_061__500m_16_days_VI_Quality']
        daymet_cols = ['Date', 'DAYMET_004_prcp']  # Precipitation in mm/day

        # Merge datasets on Date
        print("\nMerging datasets...")
        df = mod10a1[mod10a1_cols].copy()
        df = df.merge(mod16a2[mod16a2_cols], on='Date', how='outer')
        df = df.merge(mod13a1[mod13a1_cols], on='Date', how='outer')
        df = df.merge(daymet[daymet_cols], on='Date', how='inner')  # Inner join for precipitation

        print(f"  Merged dataset: {len(df)} records")

        return df

    def prepare_features(self, df):
        """Prepare features for training"""
        print("\nPreparing features...")

        # Convert date
        df['Date'] = pd.to_datetime(df['Date'])
        df['year'] = df['Date'].dt.year
        df['month'] = df['Date'].dt.month
        df['day_of_year'] = df['Date'].dt.dayofyear
        df['season'] = ((df['month'] % 12) + 3) // 3

        # Handle missing values - use forward fill then backward fill
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = df[numeric_cols].fillna(method='ffill').fillna(method='bfill')

        # Remove any remaining NaN rows
        df_clean = df.dropna()

        print(f"  Clean dataset: {len(df_clean)} records")
        print(f"  Date range: {df_clean['Date'].min()} to {df_clean['Date'].max()}")

        return df_clean

    def train(self, df_clean, model_type='random_forest', test_size=0.2):
        """Train the precipitation prediction model"""
        print("\n" + "="*70)
        print("Training Precipitation Prediction Model")
        print("="*70)

        # Use actual precipitation data from Daymet
        # DAYMET_004_prcp is in mm/day

        # Define features
        self.feature_names = [
            'MOD10A1_061_NDSI_Snow_Cover',
            'MOD10A1_061_NDSI_Snow_Cover_Algorithm_Flags_QA',
            'MOD16A2_061_ET_500m',
            'MOD16A2_061_LE_500m',
            'MOD13A1_061__500m_16_days_EVI',
            'MOD13A1_061__500m_16_days_VI_Quality',
            'month',
            'day_of_year',
            'season'
        ]

        # Prepare X and y
        X = df_clean[self.feature_names]
        y = df_clean['DAYMET_004_prcp']  # Actual precipitation in mm/day

        print(f"\nPrecipitation statistics (mm/day):")
        print(f"  Mean: {y.mean():.2f}")
        print(f"  Median: {y.median():.2f}")
        print(f"  Max: {y.max():.2f}")
        print(f"  Days with rain (>0mm): {(y > 0).sum()} ({(y > 0).sum() / len(y) * 100:.1f}%)")

        print(f"\nFeatures: {len(self.feature_names)}")
        print(f"Training samples: {len(X)}")

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Initialize model
        if model_type == 'random_forest':
            self.model = RandomForestRegressor(
                n_estimators=200,
                max_depth=20,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
        elif model_type == 'gradient_boosting':
            self.model = GradientBoostingRegressor(
                n_estimators=200,
                max_depth=10,
                learning_rate=0.1,
                random_state=42
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")

        # Train model
        print(f"\nTraining {model_type} model...")
        self.model.fit(X_train_scaled, y_train)

        # Predictions
        y_train_pred = self.model.predict(X_train_scaled)
        y_test_pred = self.model.predict(X_test_scaled)

        # Evaluation
        train_metrics = self._calculate_metrics(y_train, y_train_pred, "Training", " mm/day")
        test_metrics = self._calculate_metrics(y_test, y_test_pred, "Testing", " mm/day")

        # Feature importance
        if hasattr(self.model, 'feature_importances_'):
            self.feature_importance = pd.DataFrame({
                'feature': self.feature_names,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)

            print("\nTop 5 Most Important Features:")
            for idx, row in self.feature_importance.head(5).iterrows():
                print(f"  {row['feature']}: {row['importance']*100:.2f}%")

        return {
            'train_metrics': train_metrics,
            'test_metrics': test_metrics,
            'y_test': y_test,
            'y_test_pred': y_test_pred,
            'X_test': X_test,
            'df_clean': df_clean
        }

    def _calculate_metrics(self, y_true, y_pred, dataset_name, unit=""):
        """Calculate evaluation metrics"""
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)

        print(f"\n{dataset_name} Set Metrics:")
        print(f"  RMSE: {rmse:.4f}{unit}")
        print(f"  MAE:  {mae:.4f}{unit}")
        print(f"  R²:   {r2:.4f}")

        return {'rmse': rmse, 'mae': mae, 'r2': r2}

    def predict_hourly_precipitation(self, date_str, hour,
                                     ndsi_snow_cover=None, snow_qa=None,
                                     et_500m=None, le_500m=None,
                                     evi=None, vi_quality=None):
        """
        Predict precipitation probability for a specific date and hour.

        Args:
            date_str: Date in 'YYYY-MM-DD' format
            hour: Hour of day (0-23)
            ndsi_snow_cover: Snow cover index (0-100)
            snow_qa: Snow cover quality assurance flags
            et_500m: Evapotranspiration at 500m resolution
            le_500m: Latent heat flux at 500m resolution
            evi: Enhanced Vegetation Index
            vi_quality: Vegetation index quality

        Returns:
            Dictionary with predicted precipitation and details
        """
        if self.model is None:
            raise ValueError("Model not trained yet. Please train the model first.")

        # Parse date
        date_obj = pd.to_datetime(date_str)
        month = date_obj.month
        day_of_year = date_obj.dayofyear
        season = (month % 12 + 3) // 3

        # Use defaults if values not provided
        if ndsi_snow_cover is None:
            ndsi_snow_cover = 0.0
        if snow_qa is None:
            snow_qa = 0
        if et_500m is None:
            et_500m = 50.0
        if le_500m is None:
            le_500m = 100.0
        if evi is None:
            evi = 0.3
        if vi_quality is None:
            vi_quality = 0

        # Create feature vector
        features = {
            'MOD10A1_061_NDSI_Snow_Cover': ndsi_snow_cover,
            'MOD10A1_061_NDSI_Snow_Cover_Algorithm_Flags_QA': snow_qa,
            'MOD16A2_061_ET_500m': et_500m,
            'MOD16A2_061_LE_500m': le_500m,
            'MOD13A1_061__500m_16_days_EVI': evi,
            'MOD13A1_061__500m_16_days_VI_Quality': vi_quality,
            'month': month,
            'day_of_year': day_of_year,
            'season': season
        }

        # Create DataFrame
        X_pred = pd.DataFrame([features])[self.feature_names]

        # Scale features
        X_pred_scaled = self.scaler.transform(X_pred)

        # Get base prediction (mm/day)
        base_precip = self.model.predict(X_pred_scaled)[0]

        # Adjust based on time of day (precipitation patterns vary)
        # Early morning and late afternoon tend to have higher precipitation
        if 5 <= hour <= 8:
            time_factor = 1.1  # Morning increase
        elif 15 <= hour <= 18:
            time_factor = 1.2  # Afternoon storms
        elif 21 <= hour or hour <= 3:
            time_factor = 0.9  # Night decrease
        else:
            time_factor = 1.0

        adjusted_precip = base_precip * time_factor

        # Ensure non-negative
        adjusted_precip = max(0, adjusted_precip)

        # Convert to probability (0-100%)
        # Based on precipitation amount: >2.5mm = high, >5mm = very high
        if adjusted_precip < 0.1:
            precip_probability = 0
        elif adjusted_precip < 1.0:
            precip_probability = min(30, adjusted_precip * 30)
        elif adjusted_precip < 2.5:
            precip_probability = 30 + min(40, (adjusted_precip - 1.0) * 26.67)
        else:
            precip_probability = 70 + min(30, (adjusted_precip - 2.5) * 6)

        result = {
            'date': date_str,
            'hour': hour,
            'predicted_precipitation_mm': round(base_precip, 2),
            'adjusted_precipitation_mm': round(adjusted_precip, 2),
            'precipitation_probability_percent': round(precip_probability, 1),
            'time_factor': time_factor,
            'description': self._get_precipitation_description(precip_probability, adjusted_precip)
        }

        return result

    def _get_precipitation_description(self, prob, amount_mm):
        """Get human-readable precipitation description"""
        if prob < 10:
            return f"Clear - Very low chance of precipitation"
        elif prob < 30:
            return f"Mostly clear - Low chance of light rain ({amount_mm:.1f}mm)"
        elif prob < 50:
            return f"Partly cloudy - Moderate chance of rain ({amount_mm:.1f}mm)"
        elif prob < 70:
            return f"Cloudy - High chance of rain ({amount_mm:.1f}mm)"
        else:
            return f"Storm conditions - Heavy rain expected ({amount_mm:.1f}mm)"

    def save_model(self, filepath='precipitation_model.pkl'):
        """Save trained model"""
        if not os.path.isabs(filepath):
            filepath = os.path.join(self.data_dir, filepath)

        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'feature_importance': self.feature_importance
        }

        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)

        print(f"\n[OK] Model saved to {filepath}")

    def load_model(self, filepath='precipitation_model.pkl'):
        """Load trained model"""
        if not os.path.isabs(filepath):
            filepath = os.path.join(self.data_dir, filepath)

        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)

        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        self.feature_importance = model_data['feature_importance']

        print(f"[OK] Model loaded from {filepath}")


if __name__ == "__main__":
    # Create and train model
    model = PrecipitationPredictionModel()

    # Load data
    df = model.load_and_merge_data()
    df_clean = model.prepare_features(df)

    # Train model
    results = model.train(df_clean)

    # Save model
    model.save_model()

    # Demo prediction
    print("\n" + "="*70)
    print("Demo Prediction")
    print("="*70)

    demo_result = model.predict_hourly_precipitation(
        date_str='2024-12-15',
        hour=14,
        et_500m=75.0,
        le_500m=150.0,
        evi=0.4
    )

    print(f"\nDate: {demo_result['date']}")
    print(f"Hour: {demo_result['hour']}:00")
    print(f"Precipitation Probability: {demo_result['precipitation_probability_percent']}%")
    print(f"Description: {demo_result['description']}")
