# Model Validation Results vs Real 2025 Data

Validation period: **December 1-15, 2024** (360 hourly predictions)
Location: **Chicago, IL** (41.88°N, 87.63°W)
Data source: Open-Meteo Archive API

---

## Overall Performance Summary

| Model | MAE | RMSE | Status |
|-------|-----|------|--------|
| **Temperature (Feels-Like)** | 5.44°C | 6.88°C | ⚠️ Needs Improvement |
| **Temperature (Base)** | 6.21°C | 8.21°C | ⚠️ Needs Improvement |
| **Humidity** | 45.16% | 47.68% | ❌ Poor |
| **Cloud Cover** | 38.28% | 43.78% | ❌ Poor |
| **Wind Speed** | 9.42 m/s | 10.96 m/s | ❌ Poor |
| **Precipitation** | Not validated | - | - |

---

## 1. Temperature Model (Feels-Like)

### Error Metrics
- **Mean Absolute Error (MAE)**: 5.44°C
- **Root Mean Square Error (RMSE)**: 6.88°C
- **Max Error**: 20.06°C
- **Overall Bias**: +0.03°C (nearly zero - well calibrated!)

### Error by Time of Day
| Time Period | MAE | Samples | Performance |
|-------------|-----|---------|-------------|
| **Morning** (6am-12pm) | 6.16°C | 90 | Moderate |
| **Afternoon** (12pm-6pm) | 5.26°C | 90 | Moderate |
| **Evening** (6pm-9pm) | 4.57°C | 45 | ✅ Best |
| **Night** (9pm-6am) | 5.36°C | 135 | Moderate |

### Bias Analysis (Actual - Predicted)
- **Morning**: -0.07°C (nearly perfect)
- **Afternoon**: +0.16°C (excellent)
- **Evening**: +0.15°C (excellent)
- **Night**: -0.03°C (nearly perfect)

### Example Predictions vs Actual

| Date/Time | Actual Feels-Like | Predicted | Error |
|-----------|-------------------|-----------|-------|
| 2024-12-01 00:00 | -13.0°C | -7.15°C | 5.85°C |
| 2024-12-01 12:00 | -11.6°C | -2.24°C | 9.36°C |
| 2024-12-01 18:00 | -10.0°C | -4.85°C | 5.15°C |
| 2024-12-02 00:00 | -13.1°C | -9.22°C | 3.88°C |

### Key Issues
1. **Underestimating cold**: Model predicts warmer than actual, especially in early December
2. **Missing MODIS data**: Dec 10-15 had 15-20°C errors due to missing/poor satellite data
3. **Wind chill not modeled**: Actual feels-like includes wind chill effects we don't account for

---

## 2. Humidity Model

### Error Metrics
- **Mean Absolute Error (MAE)**: 45.16%
- **Root Mean Square Error (RMSE)**: 47.68%
- **Max Error**: ~80%

### Example Predictions vs Actual

| Date/Time | Actual Humidity | Predicted | Error |
|-----------|-----------------|-----------|-------|
| 2024-12-01 00:00 | 48% | 16.4% | 31.6% |
| 2024-12-01 08:00 | 64% | 16.4% | 47.6% |
| 2024-12-01 12:00 | 47% | 16.4% | 30.6% |
| 2024-12-01 18:00 | 47% | 16.4% | 30.6% |

### Key Issues
1. **Severe underprediction**: Predicting ~16% when actual is 40-60%
2. **No variation**: Model predictions barely change throughout the day
3. **Conversion error**: Vapor pressure → relative humidity conversion is too simplified
4. **Missing features**: Need actual temperature for proper RH calculation (RH depends on temp)

### Root Cause
The model predicts vapor pressure (Pa), but the conversion to relative humidity % is incorrect:
```python
# Current (WRONG):
pred_humidity_pct = min(100, max(0, pred_humidity_pa / 30))

# Should use proper formula:
# RH = (VP / SVP(T)) × 100
# where SVP depends on temperature
```

---

## 3. Cloud Cover Model

### Error Metrics
- **Mean Absolute Error (MAE)**: 38.28%
- **Root Mean Square Error (RMSE)**: 43.78%

### Example Predictions vs Actual

| Date/Time | Actual Cloud Cover | Predicted | Error |
|-----------|-------------------|-----------|-------|
| 2024-12-01 00:00 | 0% | 50.8% | 50.8% |
| 2024-12-01 08:00 | 20% | 50.8% | 30.8% |
| 2024-12-01 12:00 | 0% | 50.8% | 50.8% |
| 2024-12-01 18:00 | 0% | 50.8% | 50.8% |

### Key Issues
1. **Constant prediction**: Model predicts ~50% cloud cover regardless of conditions
2. **Clear sky bias**: Dec 1 was mostly clear (0% clouds) but model predicted 50%
3. **Proxy limitation**: Using solar radiation to infer clouds is indirect

### Root Cause
Cloud cover proxy based on solar radiation:
```python
cloud_cover_proxy = 100 * (1 - srad / max_srad)
```
This doesn't account for seasonal variations in solar angle/intensity.

---

## 4. Wind Speed Model

### Error Metrics
- **Mean Absolute Error (MAE)**: 9.42 m/s
- **Root Mean Square Error (RMSE)**: 10.96 m/s

### Example Predictions vs Actual

| Date/Time | Actual Wind Speed | Predicted | Error |
|-----------|------------------|-----------|-------|
| 2024-12-01 00:00 | 15.8 m/s | 6.1 m/s | 9.7 m/s |
| 2024-12-01 08:00 | 13.1 m/s | 6.1 m/s | 7.0 m/s |
| 2024-12-01 12:00 | 11.3 m/s | 6.1 m/s | 5.2 m/s |
| 2024-12-01 18:00 | 9.7 m/s | 6.1 m/s | 3.6 m/s |

### Key Issues
1. **Severe underprediction**: Predicting ~6 m/s when actual is 10-16 m/s
2. **No variation**: Predictions remain constant
3. **Weak proxy**: Temperature gradient doesn't correlate well with wind speed

### Root Cause
Wind proxy based on temperature gradient is too weak:
```python
wind_proxy = temp_gradient * 2 + PET * 0.01
# Then converted: wind_ms = (wind_proxy - 330) / 2
```
This oversimplifies complex atmospheric dynamics.

---

## Why Temperature Performs Best

The temperature model performs significantly better because:

1. **Direct measurement**: LST (Land Surface Temperature) from satellites directly relates to air temperature
2. **Strong features**: LST_Day and LST_Night explain 99.76% of variance
3. **Physical relationship**: Clear physics linking surface temp to air temp
4. **Good calibration**: Bias corrections based on validation work well

In contrast:
- **Humidity**: Indirect (vapor pressure) + wrong conversion
- **Cloud Cover**: Proxy from solar radiation (indirect)
- **Wind**: Very weak proxy from temperature gradient
- **Precipitation**: Highly variable and hard to predict from satellite data alone

---

## Recommendations for Improvement

### Immediate Fixes

1. **Humidity Model**
   ```python
   # Fix the RH calculation
   def vapor_pressure_to_rh(vp_pa, temp_c):
       # Saturation vapor pressure (Magnus formula)
       svp = 610.7 * 10**(7.5 * temp_c / (237.3 + temp_c))
       rh = (vp_pa / svp) * 100
       return min(100, max(0, rh))
   ```

2. **Cloud Cover Model**
   - Use MOD11A1 Clear_day_cov and Clear_night_cov directly (inverse)
   - Add seasonal adjustments for solar angle
   - Incorporate more cloud-related features

3. **Wind Model**
   - Collect actual wind speed data for training (not proxy)
   - Add pressure gradient features if available
   - Use weather station data for ground truth

### Long-Term Improvements

1. **More Training Data**
   - Current: Only 367 days of overlap between MODIS and Daymet
   - Target: Multiple years (1000+ days)
   - Multiple locations for generalization

2. **Additional Features**
   - Atmospheric pressure
   - Dew point temperature
   - Weather station measurements
   - Previous hour's values (temporal features)

3. **Ensemble Methods**
   - Combine satellite data with numerical weather models
   - Use multiple ML algorithms (random forest + neural network)
   - Weighted averaging based on conditions

4. **Real-Time Data**
   - Integrate live satellite feeds
   - Update predictions as new data arrives
   - Continuous model retraining

---

## Conclusion

**Temperature (feels-like)**: ✅ **Acceptable** (5.44°C MAE, minimal bias)
- Ready for use with understanding of limitations
- Best performance in evening hours
- Some outliers when MODIS data is missing

**Humidity, Cloud, Wind**: ❌ **Not Production-Ready**
- Large systematic errors (30-50% for humidity/cloud, 9 m/s for wind)
- Need fundamental improvements to conversion formulas and proxies
- Consider collecting actual measurements instead of using proxies

**Next Steps**:
1. Fix humidity conversion formula immediately
2. Retrain cloud model with direct features (not proxy)
3. Replace wind proxy with actual measurements if available
4. Expand training dataset to multiple years
5. Add weather station data for ground truth validation
