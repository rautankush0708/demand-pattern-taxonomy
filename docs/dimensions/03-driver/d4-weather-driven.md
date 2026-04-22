## D4 · Weather Driven

### 1. Definition
Predicts demand for SKUs where meteorological variables explain a statistically significant portion of demand variance, requiring weather data integration and weather-conditioned forecasting.

### 2. Detailed Description
- **Applicable scenarios:** Beverages (temperature-driven), apparel (temperature/rainfall), energy (heating/cooling), outdoor leisure, agriculture, ice cream, umbrellas, cold/flu remedies
- **Boundaries:**

| Granularity | Detection Condition | Weather Variables |
|---|---|---|
| Daily | \|Pearson r\| > 0.30 with temperature or rainfall; p < 0.05 | Temperature, rainfall, humidity, UV |
| Weekly | \|Pearson r\| > 0.30 with weekly mean temperature or rainfall; p < 0.05 | Weekly mean temp, total rainfall |
| Monthly | \|Pearson r\| > 0.30 with monthly mean temperature; p < 0.05 | Monthly mean temp, rainfall, sunshine |
| Quarterly | \|Pearson r\| > 0.30 with seasonal temperature deviation; p < 0.05 | Seasonal deviation from norm |
| Yearly | \|Pearson r\| > 0.30 with annual temperature anomaly; p < 0.05 | Annual anomaly |

- **Key demand characteristics:** Demand correlated with weather conditions, often with a lag; weather-driven spikes and troughs layered on top of seasonal pattern; forecast uncertainty driven by weather forecast uncertainty
- **Differentiation from other models:** Unlike Seasonal, correlation is with weather variable values not calendar position; unlike Event Driven, weather effect is continuous not discrete

### 3. Business Impact
- **Primary risk (over-forecast):** Overstock during unexpected cold/wet summer (e.g. ice cream, beer)
- **Primary risk (under-forecast):** Stockout during unexpected heat wave (e.g. cold drinks, fans)
- **Strategic importance:** High — weather uncertainty compounds demand uncertainty; responsive supply chain critical

### 4. Priority Level
🟠 Tier 2 — High value when weather forecasts are integrated; requires external data pipeline.

### 5. Model Strategy Overview

#### 5.1 Zero-Demand Handling (Hurdle)
- Active event threshold: P(demand > 0) > 0.70 in peak weather conditions; may drop in adverse weather
- Classifier: Logistic Regression with weather threshold features
- Regressor: LightGBM with weather variables as primary features

#### 5.2 Analogue / Similarity Logic
- Analogues: Prior periods with similar weather conditions (not similar SKUs)
- k = 10 most similar weather periods in history
- Similarity: Euclidean distance on normalised weather variables (temperature, rainfall) over window

#### 5.3 Feature Engineering

**Weather Feature Construction:**
```
Temperature deviation:  temp_t − temp_seasonal_norm_t
Rainfall deviation:     rain_t − rain_seasonal_norm_t
Heat index:             Combined temperature + humidity index
Extreme weather flag:   1 if temperature > seasonal norm + 2σ
Cold snap flag:         1 if temperature < seasonal norm − 2σ
Weather forecast:       Predicted temperature/rainfall T+1 to T+H ahead
Weather lag features:   temp_{t−1}, temp_{t−2}, rain_{t−1}, rain_{t−2}
```

| Granularity | Weather Features | Lag Range | Forecast Horizon |
|---|---|---|---|
| Daily | Daily temperature, rainfall, humidity, UV, extreme flags | lag 0–3 days | 7-day weather forecast |
| Weekly | Weekly mean temp, total rainfall, frost days, heat wave flag | lag 0–2 weeks | 2-week weather forecast |
| Monthly | Monthly mean temp, total rainfall, sunshine hours, deviation from norm | lag 0–1 month | 1-month outlook |
| Quarterly | Seasonal mean temp, seasonal rainfall total, deviation | lag 0–1 quarter | Seasonal outlook |
| Yearly | Annual temp anomaly, El Niño/La Niña index | lag 0 | Annual climate forecast |

- External signals: Weather forecast API (14-day horizon), climate outlook (seasonal), historical weather database

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM with weather variables as primary features
- Configuration: Objective = reg:squarederror; Metric = WMAPE, RMSE
- Key features: Temperature (observed and forecast), rainfall, weather deviation from norm, extreme flags, seasonal index, rolling baseline mean
- When to use: Primary model — weather variables as tabular features work well with LightGBM

#### 6.2 Deep Learning (DL)
- Architectures: TFT with weather forecast as known future covariate

| Granularity | Lookback | Future Covariates | Output |
|---|---|---|---|
| Daily | 365 days | 7-day weather forecast | P10, P50, P90 |
| Weekly | 104 weeks | 2-week weather forecast | P10, P50, P90 |
| Monthly | 36 months | 1-month outlook | P10, P50, P90 |
| Quarterly | 8 quarters | Seasonal outlook | P10, P50, P90 |
| Yearly | 5 years | Annual climate forecast | P10, P50, P90 |

- Training: Loss = quantile loss; Adam lr = 0.001; Dropout = 0.1; Patience = 10
- When to use: When weather forecast feed is available as future input — critical advantage

#### 6.3 Statistical / Time Series Models
- Architectures: Dynamic Regression (ARIMAX) with weather as exogenous variable

**ARIMAX Formula:**
```
d_t = β_0 + β_temp × temp_t + β_rain × rain_t + β_extreme × extreme_t + η_t
η_t = ARIMA(p,d,q) residual
β coefficients estimated via maximum likelihood
```

- When to use: Interpretability required; coefficient quantification for weather sensitivity reporting

#### 6.4 Baseline / Fallback Model
- Fallback triggers: Weather forecast API unavailable; model convergence failure
- Fallback model: Seasonal model (ignore weather component) — conservative approach
- Logging & alerting: Alert if weather feed unavailable; alert if temperature deviation > 3σ from norm

### 7. Ensemble & Weighting

#### 7.2 Dynamic Weight Schedule

| Weather Correlation Strength | LightGBM | TFT | ARIMAX |
|---|---|---|---|
| \|r\| 0.30–0.50 | 50% | 20% | 30% |
| \|r\| 0.50–0.70 | 55% | 30% | 15% |
| \|r\| > 0.70 | 60% | 35% | 5% |

### 8. Uncertainty Quantification
- Method: Scenario quantiles — cold scenario (P10), normal scenario (P50), hot scenario (P90)
- Output: [P10, P50, P90] based on weather forecast uncertainty cone
- Use case: Safety stock = P75 in high weather-sensitivity season; P50 in low-sensitivity periods

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Extreme weather cap: min(forecast, 2 × rolling max) during heat waves
- Weather revision: Reforecast triggered automatically when 7-day weather forecast updates significantly (> 3°C deviation)
- Manual overrides: Supply chain team response to extreme weather forecast; buying team weather hedging decision

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | WMAPE Target | Weather Sensitivity R² | Bias Alert |
|---|---|---|---|
| Daily | < 22% | R² > 0.15 vs no-weather model | \|Bias\| > 10% |
| Weekly | < 20% | R² > 0.15 | \|Bias\| > 8% |
| Monthly | < 18% | R² > 0.12 | \|Bias\| > 7% |
| Quarterly | < 15% | R² > 0.10 | \|Bias\| > 6% |
| Yearly | < 12% | R² > 0.08 | \|Bias\| > 5% |

- Secondary KPI: WMAPE improvement vs seasonal-only model (must be > 5% better to justify weather data cost)

#### 10.2 Backtesting Protocol

| Granularity | Method | Train | Test |
|---|---|---|---|
| Daily | Rolling window | 365 days | 30 days |
| Weekly | Rolling window | 104 weeks | 13 weeks |
| Monthly | Rolling window | 36 months | 6 months |
| Quarterly | Rolling window | 8 quarters | 2 quarters |
| Yearly | Expanding window | All available | 1 year |

#### 10.3 Retraining & Data Freshness

| Granularity | Cadence | Weather Feed Update | Latency |
|---|---|---|---|
| Daily | Daily + weather forecast update | Every 6 hours | T+4 hours |
| Weekly | Weekly + weekly forecast update | Daily | T+1 day |
| Monthly | Monthly + monthly outlook | Weekly | T+2 days |
| Quarterly | Quarterly + seasonal outlook | Monthly | T+3 days |
| Yearly | Annually | Annually | T+7 days |

### 11. Exception Handling & Overrides
- Automatic exception detection: Weather API feed failure → fallback to seasonal model; temperature deviation > 3σ → trigger reforecast; demand deviation > 2σ from weather-adjusted forecast → investigate supply constraint
- Manual override: Buyer weather hedging decision; contingency stock for extreme weather

### 12. Reclassification / Model Selection
- Remove Weather Driven driver: If \|r\| drops below 0.20 for 2 consecutive years
- Add Seasonal driver: Weather driver often co-exists with seasonality — test both simultaneously
- Add Event Driven driver: Extreme weather events (floods, droughts) treated as events

### 13. Review Cadence
- Performance monitoring: Daily in peak weather-sensitive season; weekly otherwise
- Model review meeting: Monthly weather sensitivity review; seasonal outlook briefing
- Full model re-evaluation: Annually at season start; after any climate anomaly year

---

