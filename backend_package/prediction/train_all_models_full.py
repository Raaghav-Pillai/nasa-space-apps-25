"""
Train ALL models on FULL dataset (no train/test split)
Then validate against real 2025 data

Author: Claude Code
Date: 2025-10-04
"""

import os
import pandas as pd
import numpy as np
import pickle
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

DATA_DIR = 'backend/data'


def load_all_data():
    """Load and merge all datasets"""
    print("="*70)
    print("LOADING ALL DATA")
    print("="*70)

    # Load MODIS
    mod09ga = pd.read_csv(os.path.join(DATA_DIR, 'Modis', 'Chicago-MOD09GA.csv'))
    mod10a1 = pd.read_csv(os.path.join(DATA_DIR, 'Modis', 'Chicago-MOD10A1.csv'))
    mod11a1 = pd.read_csv(os.path.join(DATA_DIR, 'Modis', 'Chicago-MOD11A1.csv'))
    mod13a1 = pd.read_csv(os.path.join(DATA_DIR, 'Modis', 'Chicago-MOD13A1.csv'))
    mod16a2 = pd.read_csv(os.path.join(DATA_DIR, 'Modis', 'Chicago-MOD16A2.csv'))
    daymet = pd.read_csv(os.path.join(DATA_DIR, 'Daymet', 'Daymet-Chicago-Past-Year-DAYMET-004-results.csv'))

    print(f"\nDataset sizes:")
    print(f"  MOD09GA: {len(mod09ga)}")
    print(f"  MOD10A1: {len(mod10a1)}")
    print(f"  MOD11A1: {len(mod11a1)}")
    print(f"  MOD13A1: {len(mod13a1)}")
    print(f"  MOD16A2: {len(mod16a2)}")
    print(f"  Daymet:  {len(daymet)}")

    # Merge all
    df = daymet[['Date', 'DAYMET_004_vp', 'DAYMET_004_prcp', 'DAYMET_004_tmax',
                 'DAYMET_004_tmin', 'DAYMET_004_srad']].copy()

    # MOD09GA
    mod09ga_cols = ['Date', 'MOD09GA_061_sur_refl_b01_1', 'MOD09GA_061_sur_refl_b02_1',
                    'MOD09GA_061_sur_refl_b03_1', 'MOD09GA_061_sur_refl_b04_1',
                    'MOD09GA_061_sur_refl_b05_1', 'MOD09GA_061_sur_refl_b06_1',
                    'MOD09GA_061_sur_refl_b07_1', 'MOD09GA_061_SolarAzimuth_1',
                    'MOD09GA_061_SolarZenith_1', 'MOD09GA_061_SensorAzimuth_1',
                    'MOD09GA_061_SensorZenith_1', 'MOD09GA_061_Range_1',
                    'MOD09GA_061_iobs_res_1']
    df = df.merge(mod09ga[mod09ga_cols], on='Date', how='left')

    # MOD10A1
    mod10a1_cols = ['Date', 'MOD10A1_061_NDSI_Snow_Cover',
                    'MOD10A1_061_Snow_Albedo_Daily_Tile',
                    'MOD10A1_061_NDSI_Snow_Cover_Algorithm_Flags_QA']
    df = df.merge(mod10a1[mod10a1_cols], on='Date', how='left')

    # MOD11A1
    mod11a1_cols = ['Date', 'MOD11A1_061_LST_Day_1km', 'MOD11A1_061_LST_Night_1km',
                    'MOD11A1_061_Clear_day_cov', 'MOD11A1_061_Clear_night_cov',
                    'MOD11A1_061_Emis_31', 'MOD11A1_061_Emis_32']
    df = df.merge(mod11a1[mod11a1_cols], on='Date', how='left')

    # MOD13A1
    mod13a1_cols = ['Date', 'MOD13A1_061__500m_16_days_NDVI',
                    'MOD13A1_061__500m_16_days_EVI',
                    'MOD13A1_061__500m_16_days_VI_Quality']
    df = df.merge(mod13a1[mod13a1_cols], on='Date', how='left')

    # MOD16A2
    mod16a2_cols = ['Date', 'MOD16A2_061_ET_500m', 'MOD16A2_061_LE_500m',
                    'MOD16A2_061_PET_500m']
    df = df.merge(mod16a2[mod16a2_cols], on='Date', how='left')

    # Temporal features
    df['Date'] = pd.to_datetime(df['Date'])
    df['year'] = df['Date'].dt.year
    df['month'] = df['Date'].dt.month
    df['day_of_year'] = df['Date'].dt.dayofyear
    df['season'] = ((df['Date'].dt.month % 12) + 3) // 3

    # Fill missing
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].fillna(method='ffill').fillna(method='bfill')
    df = df.dropna()

    print(f"\nFinal merged dataset: {len(df)} records")
    print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")

    return df


def train_temperature_model(df):
    """Train temperature model on FULL dataset"""
    print("\n" + "="*70)
    print("TRAINING TEMPERATURE MODEL (FULL DATA)")
    print("="*70)

    features = [
        'MOD09GA_061_sur_refl_b01_1', 'MOD09GA_061_sur_refl_b02_1',
        'MOD09GA_061_sur_refl_b03_1', 'MOD09GA_061_sur_refl_b04_1',
        'MOD09GA_061_sur_refl_b05_1', 'MOD09GA_061_sur_refl_b06_1',
        'MOD09GA_061_sur_refl_b07_1', 'MOD09GA_061_SolarAzimuth_1',
        'MOD09GA_061_SolarZenith_1', 'MOD11A1_061_LST_Day_1km',
        'MOD11A1_061_LST_Night_1km', 'MOD11A1_061_Emis_31',
        'MOD11A1_061_Emis_32', 'MOD11A1_061_Clear_day_cov',
        'MOD11A1_061_Clear_night_cov', 'month', 'day_of_year', 'season'
    ]

    X = df[features]
    y = ((df['DAYMET_004_tmax'] + df['DAYMET_004_tmin']) / 2)  # Average temp

    print(f"Training samples: {len(X)}")
    print(f"Temperature range: {y.min():.1f}°C to {y.max():.1f}°C")

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = RandomForestRegressor(n_estimators=300, max_depth=25, random_state=42, n_jobs=-1)
    model.fit(X_scaled, y)

    # Training metrics
    y_pred = model.predict(X_scaled)
    mae = mean_absolute_error(y, y_pred)
    r2 = r2_score(y, y_pred)

    print(f"\nTraining Metrics:")
    print(f"  MAE: {mae:.2f}°C")
    print(f"  R²:  {r2:.4f}")

    model_data = {'model': model, 'scaler': scaler, 'feature_names': features}
    with open(os.path.join(DATA_DIR, 'Modis', 'temperature_model_full.pkl'), 'wb') as f:
        pickle.dump(model_data, f)

    print("[OK] Model saved")
    return model_data


def train_precipitation_model(df):
    """Train precipitation model on FULL dataset"""
    print("\n" + "="*70)
    print("TRAINING PRECIPITATION MODEL (FULL DATA)")
    print("="*70)

    features = [
        'MOD10A1_061_NDSI_Snow_Cover',
        'MOD10A1_061_NDSI_Snow_Cover_Algorithm_Flags_QA',
        'MOD16A2_061_ET_500m', 'MOD16A2_061_LE_500m',
        'MOD13A1_061__500m_16_days_EVI',
        'MOD13A1_061__500m_16_days_VI_Quality',
        'month', 'day_of_year', 'season'
    ]

    X = df[features]
    y = df['DAYMET_004_prcp']

    print(f"Training samples: {len(X)}")
    print(f"Precipitation - Mean: {y.mean():.2f} mm, Max: {y.max():.2f} mm")

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = RandomForestRegressor(n_estimators=300, max_depth=25, random_state=42, n_jobs=-1)
    model.fit(X_scaled, y)

    y_pred = model.predict(X_scaled)
    mae = mean_absolute_error(y, y_pred)
    r2 = r2_score(y, y_pred)

    print(f"\nTraining Metrics:")
    print(f"  MAE: {mae:.2f} mm")
    print(f"  R²:  {r2:.4f}")

    model_data = {'model': model, 'scaler': scaler, 'feature_names': features}
    with open(os.path.join(DATA_DIR, 'Modis', 'precipitation_model_full.pkl'), 'wb') as f:
        pickle.dump(model_data, f)

    print("[OK] Model saved")
    return model_data


def train_humidity_model(df):
    """Train humidity model on FULL dataset"""
    print("\n" + "="*70)
    print("TRAINING HUMIDITY MODEL (FULL DATA)")
    print("="*70)

    features = [
        'MOD16A2_061_ET_500m', 'MOD16A2_061_LE_500m',
        'MOD09GA_061_sur_refl_b01_1', 'MOD09GA_061_sur_refl_b02_1',
        'MOD09GA_061_sur_refl_b03_1', 'MOD09GA_061_sur_refl_b04_1',
        'MOD09GA_061_sur_refl_b05_1', 'MOD09GA_061_sur_refl_b06_1',
        'MOD09GA_061_sur_refl_b07_1', 'MOD11A1_061_LST_Day_1km',
        'MOD11A1_061_LST_Night_1km', 'MOD11A1_061_Clear_day_cov',
        'MOD11A1_061_Clear_night_cov', 'month', 'day_of_year', 'season'
    ]

    X = df[features]
    y = df['DAYMET_004_vp']

    print(f"Training samples: {len(X)}")
    print(f"Vapor pressure - Mean: {y.mean():.0f} Pa, Range: {y.min():.0f}-{y.max():.0f} Pa")

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = RandomForestRegressor(n_estimators=300, max_depth=25, random_state=42, n_jobs=-1)
    model.fit(X_scaled, y)

    y_pred = model.predict(X_scaled)
    mae = mean_absolute_error(y, y_pred)
    r2 = r2_score(y, y_pred)

    print(f"\nTraining Metrics:")
    print(f"  MAE: {mae:.0f} Pa")
    print(f"  R²:  {r2:.4f}")

    model_data = {'model': model, 'scaler': scaler, 'feature_names': features}
    with open(os.path.join(DATA_DIR, 'Modis', 'humidity_model_full.pkl'), 'wb') as f:
        pickle.dump(model_data, f)

    print("[OK] Model saved")
    return model_data


def train_cloud_model(df):
    """Train cloud cover model on FULL dataset"""
    print("\n" + "="*70)
    print("TRAINING CLOUD COVER MODEL (FULL DATA)")
    print("="*70)

    features = [
        'MOD11A1_061_Clear_day_cov', 'MOD11A1_061_Clear_night_cov',
        'MOD13A1_061__500m_16_days_NDVI',
        'MOD10A1_061_Snow_Albedo_Daily_Tile',
        'month', 'day_of_year', 'season'
    ]

    # Cloud cover from solar radiation
    max_srad = df['DAYMET_004_srad'].max()
    df['cloud_cover'] = 100 * (1 - df['DAYMET_004_srad'] / max_srad)

    X = df[features]
    y = df['cloud_cover']

    print(f"Training samples: {len(X)}")
    print(f"Cloud cover - Mean: {y.mean():.1f}%, Range: {y.min():.1f}-{y.max():.1f}%")

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = RandomForestRegressor(n_estimators=300, max_depth=25, random_state=42, n_jobs=-1)
    model.fit(X_scaled, y)

    y_pred = model.predict(X_scaled)
    mae = mean_absolute_error(y, y_pred)
    r2 = r2_score(y, y_pred)

    print(f"\nTraining Metrics:")
    print(f"  MAE: {mae:.1f}%")
    print(f"  R²:  {r2:.4f}")

    model_data = {'model': model, 'scaler': scaler, 'feature_names': features}
    with open(os.path.join(DATA_DIR, 'Modis', 'cloud_model_full.pkl'), 'wb') as f:
        pickle.dump(model_data, f)

    print("[OK] Model saved")
    return model_data


def train_wind_model(df):
    """Train wind model on FULL dataset"""
    print("\n" + "="*70)
    print("TRAINING WIND MODEL (FULL DATA)")
    print("="*70)

    features = [
        'MOD09GA_061_SensorAzimuth_1', 'MOD09GA_061_SensorZenith_1',
        'MOD09GA_061_Range_1', 'MOD09GA_061_iobs_res_1',
        'MOD16A2_061_PET_500m', 'MOD11A1_061_LST_Day_1km',
        'MOD11A1_061_LST_Night_1km', 'month', 'day_of_year', 'season'
    ]

    # Wind proxy
    temp_gradient = np.abs(df['DAYMET_004_tmax'] - df['DAYMET_004_tmin'])
    df['wind_proxy'] = temp_gradient * 2 + df['MOD16A2_061_PET_500m'] * 0.01

    X = df[features]
    y = df['wind_proxy']

    print(f"Training samples: {len(X)}")
    print(f"Wind proxy - Mean: {y.mean():.1f}, Range: {y.min():.1f}-{y.max():.1f}")

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = RandomForestRegressor(n_estimators=300, max_depth=25, random_state=42, n_jobs=-1)
    model.fit(X_scaled, y)

    y_pred = model.predict(X_scaled)
    mae = mean_absolute_error(y, y_pred)
    r2 = r2_score(y, y_pred)

    print(f"\nTraining Metrics:")
    print(f"  MAE: {mae:.1f}")
    print(f"  R²:  {r2:.4f}")

    model_data = {'model': model, 'scaler': scaler, 'feature_names': features}
    with open(os.path.join(DATA_DIR, 'Modis', 'wind_model_full.pkl'), 'wb') as f:
        pickle.dump(model_data, f)

    print("[OK] Model saved")
    return model_data


if __name__ == "__main__":
    # Load all data
    df = load_all_data()

    # Train all models on FULL dataset
    temp_model = train_temperature_model(df)
    precip_model = train_precipitation_model(df)
    humidity_model = train_humidity_model(df)
    cloud_model = train_cloud_model(df)
    wind_model = train_wind_model(df)

    print("\n" + "="*70)
    print("ALL MODELS TRAINED ON FULL DATASET!")
    print("="*70)
    print("\nNext step: Validate against 2025 data")
