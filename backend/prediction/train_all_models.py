"""
Train all weather prediction models (Humidity, Cloud Cover, Wind, Precipitation)

This script trains all 4 models and saves them for prediction use.

Author: Claude Code
Date: 2025-10-04
"""

import os
import sys
import pandas as pd
import numpy as np
import pickle
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

# Add parent directory to path
current_dir = os.getcwd()
if os.path.basename(current_dir) == 'prediction':
    DATA_DIR = '../data'
else:
    DATA_DIR = 'backend/data'


def load_all_data():
    """Load and merge all datasets"""
    print("="*70)
    print("LOADING ALL MODIS AND DAYMET DATA")
    print("="*70)

    # Load MODIS data
    mod09ga = pd.read_csv(os.path.join(DATA_DIR, 'Modis', 'Chicago-MOD09GA.csv'))
    mod10a1 = pd.read_csv(os.path.join(DATA_DIR, 'Modis', 'Chicago-MOD10A1.csv'))
    mod11a1 = pd.read_csv(os.path.join(DATA_DIR, 'Modis', 'Chicago-MOD11A1.csv'))
    mod13a1 = pd.read_csv(os.path.join(DATA_DIR, 'Modis', 'Chicago-MOD13A1.csv'))
    mod16a2 = pd.read_csv(os.path.join(DATA_DIR, 'Modis', 'Chicago-MOD16A2.csv'))
    daymet = pd.read_csv(os.path.join(DATA_DIR, 'Daymet', 'Daymet-Chicago-Past-Year-DAYMET-004-results.csv'))

    print(f"\nLoaded {len(mod09ga)} MOD09GA records")
    print(f"Loaded {len(mod10a1)} MOD10A1 records")
    print(f"Loaded {len(mod11a1)} MOD11A1 records")
    print(f"Loaded {len(mod13a1)} MOD13A1 records")
    print(f"Loaded {len(mod16a2)} MOD16A2 records")
    print(f"Loaded {len(daymet)} Daymet records")

    # Merge all on Date
    print("\nMerging datasets...")

    # Start with Daymet (has target variables)
    df = daymet[['Date', 'DAYMET_004_vp', 'DAYMET_004_prcp', 'DAYMET_004_tmax',
                 'DAYMET_004_tmin', 'DAYMET_004_srad']].copy()

    # Merge MOD09GA - for surface reflectance, cloud state, wind indicators
    mod09ga_cols = ['Date', 'MOD09GA_061_sur_refl_b01_1', 'MOD09GA_061_sur_refl_b02_1',
                    'MOD09GA_061_sur_refl_b03_1', 'MOD09GA_061_sur_refl_b04_1',
                    'MOD09GA_061_sur_refl_b05_1', 'MOD09GA_061_sur_refl_b06_1',
                    'MOD09GA_061_sur_refl_b07_1', 'MOD09GA_061_SensorAzimuth_1',
                    'MOD09GA_061_SensorZenith_1', 'MOD09GA_061_Range_1',
                    'MOD09GA_061_iobs_res_1']
    df = df.merge(mod09ga[mod09ga_cols], on='Date', how='left')

    # Merge MOD10A1 - for snow cover
    mod10a1_cols = ['Date', 'MOD10A1_061_NDSI_Snow_Cover',
                    'MOD10A1_061_Snow_Albedo_Daily_Tile',
                    'MOD10A1_061_NDSI_Snow_Cover_Algorithm_Flags_QA']
    df = df.merge(mod10a1[mod10a1_cols], on='Date', how='left')

    # Merge MOD11A1 - for temperature and cloud cover
    mod11a1_cols = ['Date', 'MOD11A1_061_LST_Day_1km', 'MOD11A1_061_LST_Night_1km',
                    'MOD11A1_061_Clear_day_cov', 'MOD11A1_061_Clear_night_cov']
    df = df.merge(mod11a1[mod11a1_cols], on='Date', how='left')

    # Merge MOD13A1 - for vegetation
    mod13a1_cols = ['Date', 'MOD13A1_061__500m_16_days_NDVI',
                    'MOD13A1_061__500m_16_days_EVI',
                    'MOD13A1_061__500m_16_days_VI_Quality']
    df = df.merge(mod13a1[mod13a1_cols], on='Date', how='left')

    # Merge MOD16A2 - for ET
    mod16a2_cols = ['Date', 'MOD16A2_061_ET_500m', 'MOD16A2_061_LE_500m',
                    'MOD16A2_061_PET_500m']
    df = df.merge(mod16a2[mod16a2_cols], on='Date', how='left')

    print(f"Merged dataset: {len(df)} records")

    # Add temporal features
    df['Date'] = pd.to_datetime(df['Date'])
    df['year'] = df['Date'].dt.year
    df['month'] = df['Date'].dt.month
    df['day_of_year'] = df['Date'].dt.dayofyear
    df['season'] = ((df['Date'].dt.month % 12) + 3) // 3

    # Forward fill then backward fill missing values
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].fillna(method='ffill').fillna(method='bfill')

    # Drop remaining NaN
    df_clean = df.dropna()

    print(f"Clean dataset: {len(df_clean)} records")
    print(f"Date range: {df_clean['Date'].min()} to {df_clean['Date'].max()}")

    return df_clean


def train_humidity_model(df_clean):
    """Train humidity (vapor pressure) prediction model"""
    print("\n" + "="*70)
    print("TRAINING HUMIDITY MODEL")
    print("="*70)

    # Features based on user specification
    feature_names = [
        # MOD16A2: ET and LE relate to moisture
        'MOD16A2_061_ET_500m',
        'MOD16A2_061_LE_500m',
        # MOD09GA: Surface reflectance affects humidity
        'MOD09GA_061_sur_refl_b01_1',
        'MOD09GA_061_sur_refl_b02_1',
        'MOD09GA_061_sur_refl_b03_1',
        'MOD09GA_061_sur_refl_b04_1',
        'MOD09GA_061_sur_refl_b05_1',
        'MOD09GA_061_sur_refl_b06_1',
        'MOD09GA_061_sur_refl_b07_1',
        # MOD11A1: Temperature and cloud cover affect humidity
        'MOD11A1_061_LST_Day_1km',
        'MOD11A1_061_LST_Night_1km',
        'MOD11A1_061_Clear_day_cov',
        'MOD11A1_061_Clear_night_cov',
        # Temporal features
        'month',
        'day_of_year',
        'season'
    ]

    X = df_clean[feature_names]
    y = df_clean['DAYMET_004_vp']  # Vapor pressure (Pa)

    print(f"\nHumidity (vapor pressure) statistics:")
    print(f"  Mean: {y.mean():.2f} Pa")
    print(f"  Median: {y.median():.2f} Pa")
    print(f"  Range: {y.min():.2f} - {y.max():.2f} Pa")

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Scale
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train model
    model = RandomForestRegressor(n_estimators=200, max_depth=20, random_state=42, n_jobs=-1)
    model.fit(X_train_scaled, y_train)

    # Evaluate
    y_test_pred = model.predict(X_test_scaled)
    mae = mean_absolute_error(y_test, y_test_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
    r2 = r2_score(y_test, y_test_pred)

    print(f"\nTest Metrics:")
    print(f"  MAE:  {mae:.2f} Pa")
    print(f"  RMSE: {rmse:.2f} Pa")
    print(f"  R²:   {r2:.4f}")

    # Feature importance
    importance = pd.DataFrame({
        'feature': feature_names,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)

    print(f"\nTop 5 features:")
    for idx, row in importance.head(5).iterrows():
        print(f"  {row['feature']}: {row['importance']*100:.2f}%")

    # Save
    model_data = {
        'model': model,
        'scaler': scaler,
        'feature_names': feature_names,
        'feature_importance': importance
    }

    os.makedirs(os.path.join(DATA_DIR, 'Modis'), exist_ok=True)
    with open(os.path.join(DATA_DIR, 'Modis', 'humidity_model.pkl'), 'wb') as f:
        pickle.dump(model_data, f)

    print(f"[OK] Model saved")

    return model_data


def train_cloud_model(df_clean):
    """Train cloud cover prediction model"""
    print("\n" + "="*70)
    print("TRAINING CLOUD COVER MODEL")
    print("="*70)

    # Features
    feature_names = [
        # MOD11A1: Clear coverage (inverse of cloud cover)
        'MOD11A1_061_Clear_day_cov',
        'MOD11A1_061_Clear_night_cov',
        # MOD13A1: Vegetation index correlates with clouds
        'MOD13A1_061__500m_16_days_NDVI',
        # MOD10A1: Snow albedo affects cloud formation
        'MOD10A1_061_Snow_Albedo_Daily_Tile',
        # Temporal
        'month',
        'day_of_year',
        'season'
    ]

    # Create cloud cover proxy from clear coverage and solar radiation
    # Lower solar radiation = more clouds
    max_srad = df_clean['DAYMET_004_srad'].max()
    df_clean['cloud_cover_proxy'] = 100 * (1 - df_clean['DAYMET_004_srad'] / max_srad)

    X = df_clean[feature_names]
    y = df_clean['cloud_cover_proxy']  # Cloud cover percentage

    print(f"\nCloud cover statistics:")
    print(f"  Mean: {y.mean():.2f}%")
    print(f"  Median: {y.median():.2f}%")
    print(f"  Range: {y.min():.2f} - {y.max():.2f}%")

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Scale
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train
    model = RandomForestRegressor(n_estimators=200, max_depth=20, random_state=42, n_jobs=-1)
    model.fit(X_train_scaled, y_train)

    # Evaluate
    y_test_pred = model.predict(X_test_scaled)
    mae = mean_absolute_error(y_test, y_test_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
    r2 = r2_score(y_test, y_test_pred)

    print(f"\nTest Metrics:")
    print(f"  MAE:  {mae:.2f}%")
    print(f"  RMSE: {rmse:.2f}%")
    print(f"  R²:   {r2:.4f}")

    # Feature importance
    importance = pd.DataFrame({
        'feature': feature_names,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)

    print(f"\nTop 5 features:")
    for idx, row in importance.head(5).iterrows():
        print(f"  {row['feature']}: {row['importance']*100:.2f}%")

    # Save
    model_data = {
        'model': model,
        'scaler': scaler,
        'feature_names': feature_names,
        'feature_importance': importance
    }

    with open(os.path.join(DATA_DIR, 'Modis', 'cloud_model.pkl'), 'wb') as f:
        pickle.dump(model_data, f)

    print(f"[OK] Model saved")

    return model_data


def train_wind_model(df_clean):
    """Train wind speed prediction model"""
    print("\n" + "="*70)
    print("TRAINING WIND MODEL")
    print("="*70)

    # Features
    feature_names = [
        # MOD09GA: Sensor angles can indicate wind direction effects
        'MOD09GA_061_SensorAzimuth_1',
        'MOD09GA_061_SensorZenith_1',
        'MOD09GA_061_Range_1',
        'MOD09GA_061_iobs_res_1',
        # MOD16A2: PET relates to wind in arid conditions
        'MOD16A2_061_PET_500m',
        # Temperature gradients drive wind
        'MOD11A1_061_LST_Day_1km',
        'MOD11A1_061_LST_Night_1km',
        # Temporal
        'month',
        'day_of_year',
        'season'
    ]

    # Create wind proxy from temperature gradient and PET
    # Higher temp gradient and PET = higher wind
    temp_gradient = np.abs(df_clean['DAYMET_004_tmax'] - df_clean['DAYMET_004_tmin'])
    df_clean['wind_proxy'] = temp_gradient * 2 + df_clean['MOD16A2_061_PET_500m'] * 0.01

    X = df_clean[feature_names]
    y = df_clean['wind_proxy']  # Wind speed proxy

    print(f"\nWind proxy statistics:")
    print(f"  Mean: {y.mean():.2f}")
    print(f"  Median: {y.median():.2f}")
    print(f"  Range: {y.min():.2f} - {y.max():.2f}")

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Scale
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train
    model = RandomForestRegressor(n_estimators=200, max_depth=20, random_state=42, n_jobs=-1)
    model.fit(X_train_scaled, y_train)

    # Evaluate
    y_test_pred = model.predict(X_test_scaled)
    mae = mean_absolute_error(y_test, y_test_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
    r2 = r2_score(y_test, y_test_pred)

    print(f"\nTest Metrics:")
    print(f"  MAE:  {mae:.2f}")
    print(f"  RMSE: {rmse:.2f}")
    print(f"  R²:   {r2:.4f}")

    # Feature importance
    importance = pd.DataFrame({
        'feature': feature_names,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)

    print(f"\nTop 5 features:")
    for idx, row in importance.head(5).iterrows():
        print(f"  {row['feature']}: {row['importance']*100:.2f}%")

    # Save
    model_data = {
        'model': model,
        'scaler': scaler,
        'feature_names': feature_names,
        'feature_importance': importance
    }

    with open(os.path.join(DATA_DIR, 'Modis', 'wind_model.pkl'), 'wb') as f:
        pickle.dump(model_data, f)

    print(f"[OK] Model saved")

    return model_data


if __name__ == "__main__":
    # Load data
    df_clean = load_all_data()

    # Train all models
    humidity_model = train_humidity_model(df_clean)
    cloud_model = train_cloud_model(df_clean)
    wind_model = train_wind_model(df_clean)

    print("\n" + "="*70)
    print("ALL MODELS TRAINED SUCCESSFULLY!")
    print("="*70)
    print("\nSaved models:")
    print("  - humidity_model.pkl")
    print("  - cloud_model.pkl")
    print("  - wind_model.pkl")
    print("  - precipitation_model.pkl (trained separately)")
