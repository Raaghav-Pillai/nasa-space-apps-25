import pandas as pd

df = pd.read_csv('backend/data/Modis/validation_results_2025.csv')

print('Average predicted feels-like:', df['predicted_feels_like'].mean())
print('Average actual feels-like:', df['actual_feels_like'].mean())
print('Difference (actual - predicted):', df['actual_feels_like'].mean() - df['predicted_feels_like'].mean())

print('\nBy time period:')
for period in ['morning', 'afternoon', 'evening', 'night']:
    period_df = df[df['time_period'] == period]
    pred_mean = period_df['predicted_feels_like'].mean()
    actual_mean = period_df['actual_feels_like'].mean()
    diff = actual_mean - pred_mean
    print(f'{period}: predicted={pred_mean:.2f}, actual={actual_mean:.2f}, diff={diff:.2f}')
