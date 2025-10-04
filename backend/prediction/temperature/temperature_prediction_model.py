import pandas as pd
import numpy as np
import os
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge, Lasso
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

class TemperaturePredictionModel:
    """
    Temperature prediction model using MODIS satellite data.
    Predicts temperature using various surface and atmospheric variables.
    """

    def __init__(self, data_dir='../../data/Modis'):
        self.data_dir = data_dir
        self.model = None
        self.scaler = StandardScaler()
        self.feature_importance = None
        self.feature_names = None

    def load_and_merge_data(self):
        """Load and merge MOD09GA and MOD11A1 datasets"""
        print("Loading MODIS data...")

        # Load datasets
        mod09ga_path = os.path.join(self.data_dir, 'Chicago-MOD09GA.csv')
        mod11a1_path = os.path.join(self.data_dir, 'Chicago-MOD11A1.csv')

        df_09ga = pd.read_csv(mod09ga_path)
        df_11a1 = pd.read_csv(mod11a1_path)

        print(f"MOD09GA shape: {df_09ga.shape}")
        print(f"MOD11A1 shape: {df_11a1.shape}")

        # Merge on Date
        df = pd.merge(df_09ga, df_11a1, on=['Date', 'Category', 'ID', 'Latitude', 'Longitude'],
                      how='inner', suffixes=('_09GA', '_11A1'))

        print(f"Merged data shape: {df.shape}")

        return df

    def prepare_features(self, df):
        """
        Prepare feature set with selected variables for temperature prediction.

        Features:
        - Surface reflectance bands (sur_refl_b01_1 to sur_refl_b07_1)
        - Land surface temperature (LST_Day_1km, LST_Night_1km)
        - Solar angles (SolarAzimuth_1, SolarZenith_1)
        - Emissivity (Emis_31, Emis_32)
        - Cloud cover (Clear_day_cov, Clear_night_cov)
        """
        print("\nPreparing features...")

        # Convert Date to datetime
        df['Date'] = pd.to_datetime(df['Date'])

        # Add temporal features
        df['year'] = df['Date'].dt.year
        df['month'] = df['Date'].dt.month
        df['day_of_year'] = df['Date'].dt.dayofyear
        df['season'] = (df['month'] % 12 + 3) // 3  # 1: Winter, 2: Spring, 3: Summer, 4: Fall

        # Selected feature columns
        feature_cols = [
            # Surface reflectance (MOD09GA)
            'MOD09GA_061_sur_refl_b01_1',
            'MOD09GA_061_sur_refl_b02_1',
            'MOD09GA_061_sur_refl_b03_1',
            'MOD09GA_061_sur_refl_b04_1',
            'MOD09GA_061_sur_refl_b05_1',
            'MOD09GA_061_sur_refl_b06_1',
            'MOD09GA_061_sur_refl_b07_1',
            # Solar angles (MOD09GA)
            'MOD09GA_061_SolarAzimuth_1',
            'MOD09GA_061_SolarZenith_1',
            # Land Surface Temperature (MOD11A1)
            'MOD11A1_061_LST_Day_1km',
            'MOD11A1_061_LST_Night_1km',
            # Emissivity (MOD11A1)
            'MOD11A1_061_Emis_31',
            'MOD11A1_061_Emis_32',
            # Cloud cover (MOD11A1)
            'MOD11A1_061_Clear_day_cov',
            'MOD11A1_061_Clear_night_cov',
            # Temporal features
            'month',
            'day_of_year',
            'season'
        ]

        # Check which columns exist
        available_features = [col for col in feature_cols if col in df.columns]
        missing_features = [col for col in feature_cols if col not in df.columns]

        if missing_features:
            print(f"Warning: Missing features: {missing_features}")

        print(f"Using {len(available_features)} features")

        # Create feature matrix
        X = df[available_features].copy()

        # Convert LST from Kelvin to Celsius (target variable)
        # We'll use the average of day and night LST as the target
        df['Temperature_C'] = ((df['MOD11A1_061_LST_Day_1km'] + df['MOD11A1_061_LST_Night_1km']) / 2) - 273.15

        y = df['Temperature_C']

        # Handle missing values
        X = X.fillna(X.median())

        # Remove outliers (temperatures outside reasonable range)
        valid_mask = (y >= -50) & (y <= 50)  # Reasonable temperature range
        X = X[valid_mask]
        y = y[valid_mask]
        df_clean = df[valid_mask].copy()

        print(f"Final dataset shape: {X.shape}")
        print(f"Temperature range: {y.min():.2f}°C to {y.max():.2f}°C")

        self.feature_names = available_features

        return X, y, df_clean

    def train_model(self, X, y, test_size=0.2, model_type='random_forest'):
        """
        Train the temperature prediction model.

        Args:
            X: Feature matrix
            y: Target variable (temperature)
            test_size: Proportion of data for testing
            model_type: 'random_forest', 'gradient_boosting', 'ridge', or 'lasso'
        """
        print(f"\nTraining {model_type} model...")

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, shuffle=True
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
        elif model_type == 'ridge':
            self.model = Ridge(alpha=1.0)
        elif model_type == 'lasso':
            self.model = Lasso(alpha=1.0)
        else:
            raise ValueError(f"Unknown model type: {model_type}")

        # Train model
        self.model.fit(X_train_scaled, y_train)

        # Predictions
        y_train_pred = self.model.predict(X_train_scaled)
        y_test_pred = self.model.predict(X_test_scaled)

        # Evaluation
        train_metrics = self._calculate_metrics(y_train, y_train_pred, "Training")
        test_metrics = self._calculate_metrics(y_test, y_test_pred, "Testing")

        # Feature importance
        if hasattr(self.model, 'feature_importances_'):
            self.feature_importance = pd.DataFrame({
                'feature': self.feature_names,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)

        return {
            'train_metrics': train_metrics,
            'test_metrics': test_metrics,
            'y_test': y_test,
            'y_test_pred': y_test_pred,
            'X_test': X_test
        }

    def _calculate_metrics(self, y_true, y_pred, dataset_name):
        """Calculate evaluation metrics"""
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)

        print(f"\n{dataset_name} Set Metrics:")
        print(f"  RMSE: {rmse:.4f}°C")
        print(f"  MAE:  {mae:.4f}°C")
        print(f"  R²:   {r2:.4f}")

        return {'rmse': rmse, 'mae': mae, 'r2': r2}

    def predict_2025(self, df_clean):
        """Test model on 2025 data"""
        print("\n" + "="*70)
        print("Testing on 2025 Data")
        print("="*70)

        # Filter 2025 data
        df_2025 = df_clean[df_clean['year'] == 2025].copy()

        if len(df_2025) == 0:
            print("No 2025 data available in the dataset")
            return None

        print(f"Found {len(df_2025)} records from 2025")

        # Prepare features
        X_2025 = df_2025[self.feature_names]
        y_2025_true = df_2025['Temperature_C']

        # Scale and predict
        X_2025_scaled = self.scaler.transform(X_2025)
        y_2025_pred = self.model.predict(X_2025_scaled)

        # Metrics
        metrics_2025 = self._calculate_metrics(y_2025_true, y_2025_pred, "2025")

        return {
            'predictions': y_2025_pred,
            'actual': y_2025_true,
            'dates': df_2025['Date'],
            'metrics': metrics_2025
        }

    def predict_feels_like_temperature(self, date_str, hour, lst_day=None, lst_night=None,
                                       cloud_cover_day=None, cloud_cover_night=None,
                                       sur_refl_bands=None, solar_azimuth=None, solar_zenith=None,
                                       emis_31=None, emis_32=None):
        """
        Predict "feels like" temperature for a specific date and hour.

        Args:
            date_str: Date in 'YYYY-MM-DD' format
            hour: Hour of day (0-23)
            lst_day: Land Surface Temperature Day (Kelvin)
            lst_night: Land Surface Temperature Night (Kelvin)
            cloud_cover_day: Clear day coverage (0-1)
            cloud_cover_night: Clear night coverage (0-1)
            sur_refl_bands: List of 7 surface reflectance values [b01-b07]
            solar_azimuth: Solar azimuth angle
            solar_zenith: Solar zenith angle
            emis_31: Emissivity band 31
            emis_32: Emissivity band 32

        Returns:
            Dictionary with predicted feels-like temperature and details
        """
        if self.model is None:
            raise ValueError("Model not trained yet. Please train the model first.")

        # Parse date
        date_obj = pd.to_datetime(date_str)
        month = date_obj.month
        day_of_year = date_obj.dayofyear
        season = (month % 12 + 3) // 3

        # Determine time of day period
        if 6 <= hour < 12:
            time_period = "morning"
            time_weight_day = 0.7
            time_weight_night = 0.3
        elif 12 <= hour < 18:
            time_period = "afternoon"
            time_weight_day = 1.0
            time_weight_night = 0.0
        elif 18 <= hour < 21:
            time_period = "evening"
            time_weight_day = 0.4
            time_weight_night = 0.6
        else:  # 21-6
            time_period = "night"
            time_weight_day = 0.0
            time_weight_night = 1.0

        # Use defaults if values not provided (median from training data)
        if lst_day is None:
            lst_day = 288.0  # ~15°C
        if lst_night is None:
            lst_night = 280.0  # ~7°C
        if cloud_cover_day is None:
            cloud_cover_day = 0.5
        if cloud_cover_night is None:
            cloud_cover_night = 0.5
        if sur_refl_bands is None:
            sur_refl_bands = [0.15, 0.20, 0.10, 0.15, 0.18, 0.12, 0.08]
        if solar_azimuth is None:
            solar_azimuth = 180.0
        if solar_zenith is None:
            solar_zenith = 45.0
        if emis_31 is None:
            emis_31 = 0.985
        if emis_32 is None:
            emis_32 = 0.985

        # Create feature vector
        features = {
            'MOD09GA_061_sur_refl_b01_1': sur_refl_bands[0],
            'MOD09GA_061_sur_refl_b02_1': sur_refl_bands[1],
            'MOD09GA_061_sur_refl_b03_1': sur_refl_bands[2],
            'MOD09GA_061_sur_refl_b04_1': sur_refl_bands[3],
            'MOD09GA_061_sur_refl_b05_1': sur_refl_bands[4],
            'MOD09GA_061_sur_refl_b06_1': sur_refl_bands[5],
            'MOD09GA_061_sur_refl_b07_1': sur_refl_bands[6],
            'MOD09GA_061_SolarAzimuth_1': solar_azimuth,
            'MOD09GA_061_SolarZenith_1': solar_zenith,
            'MOD11A1_061_LST_Day_1km': lst_day,
            'MOD11A1_061_LST_Night_1km': lst_night,
            'MOD11A1_061_Emis_31': emis_31,
            'MOD11A1_061_Emis_32': emis_32,
            'MOD11A1_061_Clear_day_cov': cloud_cover_day,
            'MOD11A1_061_Clear_night_cov': cloud_cover_night,
            'month': month,
            'day_of_year': day_of_year,
            'season': season
        }

        # Create DataFrame with features in correct order
        X_pred = pd.DataFrame([features])[self.feature_names]

        # Scale features
        X_pred_scaled = self.scaler.transform(X_pred)

        # Get base prediction (already in Celsius)
        base_temp = self.model.predict(X_pred_scaled)[0]

        # Convert LST to Celsius for reference
        lst_day_c = lst_day - 273.15
        lst_night_c = lst_night - 273.15

        # Use base temperature as starting point for feels-like
        # Then adjust based on time of day and cloud cover
        if time_period == "afternoon":
            # Afternoon: stronger solar radiation effect
            # More clouds (lower clear_cov) = feels cooler
            cloud_factor = cloud_cover_day  # 1.0 = clear, 0.0 = cloudy
            feels_like = base_temp - (1 - cloud_factor) * 0.5  # Reduced cloud cooling effect
            # Add solar heating effect
            feels_like += 2.5  # Afternoon feels warmer due to direct sun
        elif time_period == "morning":
            # Morning: transitioning from night, less solar heating
            cloud_factor = cloud_cover_day
            feels_like = base_temp - (1 - cloud_factor) * 1.5
            # Morning feels cooler
            feels_like -= 1.0
        elif time_period == "evening":
            # Evening: cooling down but some residual heat
            cloud_factor = cloud_cover_night
            feels_like = base_temp + (1 - cloud_factor) * 1.0
            # Slight warmth from day
            feels_like += 0.8
        else:  # night
            # Nighttime: clouds trap heat
            # More clouds (lower clear_cov) = feels warmer
            cloud_factor = cloud_cover_night
            feels_like = base_temp + (1 - cloud_factor) * 1.0
            # Night feels colder
            feels_like -= 1.5

        result = {
            'date': date_str,
            'hour': hour,
            'time_period': time_period,
            'predicted_temperature': round(base_temp, 2),
            'feels_like_temperature': round(feels_like, 2),
            'lst_day_celsius': round(lst_day_c, 2),
            'lst_night_celsius': round(lst_night_c, 2),
            'cloud_cover_day': cloud_cover_day,
            'cloud_cover_night': cloud_cover_night,
            'time_weight_day': time_weight_day,
            'time_weight_night': time_weight_night,
            'description': self._get_temperature_description(feels_like, time_period)
        }

        return result

    def _get_temperature_description(self, temp, time_period):
        """Get human-readable temperature description"""
        if temp < 0:
            feel = "Freezing"
        elif temp < 10:
            feel = "Cold"
        elif temp < 20:
            feel = "Cool"
        elif temp < 25:
            feel = "Comfortable"
        elif temp < 30:
            feel = "Warm"
        else:
            feel = "Hot"

        return f"{feel} {time_period}"

    def plot_results(self, results, output_dir='backend/data/Modis'):
        """Generate visualization plots"""
        print("\nGenerating plots...")
        os.makedirs(output_dir, exist_ok=True)

        # 1. Actual vs Predicted
        plt.figure(figsize=(10, 6))
        plt.scatter(results['y_test'], results['y_test_pred'], alpha=0.5)
        plt.plot([results['y_test'].min(), results['y_test'].max()],
                 [results['y_test'].min(), results['y_test'].max()],
                 'r--', lw=2)
        plt.xlabel('Actual Temperature (°C)', fontsize=12)
        plt.ylabel('Predicted Temperature (°C)', fontsize=12)
        plt.title('Temperature Prediction: Actual vs Predicted', fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.savefig(os.path.join(output_dir, 'actual_vs_predicted.png'), dpi=300, bbox_inches='tight')
        plt.close()

        # 2. Feature Importance
        if self.feature_importance is not None:
            plt.figure(figsize=(12, 8))
            top_features = self.feature_importance.head(15)
            plt.barh(range(len(top_features)), top_features['importance'])
            plt.yticks(range(len(top_features)), top_features['feature'])
            plt.xlabel('Importance', fontsize=12)
            plt.title('Top 15 Feature Importance', fontsize=14)
            plt.grid(True, alpha=0.3, axis='x')
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'feature_importance.png'), dpi=300, bbox_inches='tight')
            plt.close()

            # Save feature importance to CSV
            self.feature_importance.to_csv(
                os.path.join(output_dir, 'feature_importance.csv'),
                index=False
            )

        print(f"Plots saved to {output_dir}")

def main():
    """Main execution function"""
    print("="*70)
    print("MODIS Temperature Prediction Model")
    print("="*70)

    # Initialize model
    model = TemperaturePredictionModel()

    # Load data
    df = model.load_and_merge_data()

    # Prepare features
    X, y, df_clean = model.prepare_features(df)

    # Train model
    results = model.train_model(X, y, model_type='random_forest')

    # Test on 2025 data
    results_2025 = model.predict_2025(df_clean)

    # Generate plots
    model.plot_results(results)

    print("\n" + "="*70)
    print("Model Training Complete!")
    print("="*70)
    print(f"\nModel saved as: temperature_model.pkl (ready for deployment)")
    print(f"Feature importance saved to: backend/data/Modis/feature_importance.csv")

    # Save model
    import joblib
    joblib.dump(model, 'backend/data/Modis/temperature_model.pkl')

    return model, results, results_2025

if __name__ == "__main__":
    model, results, results_2025 = main()
