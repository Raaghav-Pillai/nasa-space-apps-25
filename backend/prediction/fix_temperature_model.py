import sys
sys.path.insert(0, 'backend/prediction/temperature')

from temperature_prediction_model import TemperaturePredictionModel
import pickle

# Train model
model = TemperaturePredictionModel(data_dir='backend/data/Modis')
df = model.load_and_merge_data()
X, y, df_clean = model.prepare_features(df)

results = model.train_model(X, y)

# Save properly
data = {
    'model': model.model,
    'scaler': model.scaler,
    'feature_names': model.feature_names,
    'feature_importance': model.feature_importance
}

with open('backend/data/Modis/temperature_model_fixed.pkl', 'wb') as f:
    pickle.dump(data, f)

print("\n[OK] Temperature model saved to temperature_model_fixed.pkl")
