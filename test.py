from backend.prediction.predict_simple import predict_daily_range as daily_range
from backend.prediction.predict_simple import predict_hourly as hourly

print("="*70)
print("TESTING WEATHER PREDICTIONS")
print("="*70)

print("\n1. HOURLY PREDICTION")
print("-"*70)
result = hourly("2025-10-04", 14)
print(result)

print("\n\n2. DAILY RANGE PREDICTION")
print("-"*70)
forecast = daily_range("2025-10-04", "2025-10-08")
print(forecast)

