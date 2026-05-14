# Segment Model Template

## Dimension 9 · Coincident

---

### 1. Definition
Predicts demand for SKUs where demand moves simultaneously with an identifiable external trigger signal (max CCF at k = 0), requiring real-time external signal integration for contemporaneous demand forecasting.

### 2. Detailed Description
- **Applicable scenarios:** Weather-sensitive same-day demand (temperature = same-day cold drink sales), real-time event demand, POS-driven replenishment categories, same-day consumption-purchase patterns
- **Boundaries:**

| Granularity | Detection Condition | Min History |
|---|---|---|
| Daily | Max \|CCF\| at k = 0; \|CCF(0)\| > 2/√n | ≥ 180 days |
| Weekly | Max \|CCF\| at k = 0; \|CCF(0)\| > 2/√n | ≥ 52 weeks |
| Monthly | Max \|CCF\| at k = 0; \|CCF(0)\| > 2/√n | ≥ 24 months |
| Quarterly | Max \|CCF\| at k = 0; \|CCF(0)\| > 2/√n | ≥ 8 quarters |
| Yearly | Max \|CCF\| at k = 0; \|CCF(0)\| > 2/√n | ≥ 5 years |

- **Key demand characteristics:** Contemporaneous correlation between demand and trigger; same-period signal is the primary forecast driver; real-time data pipeline is critical
- **Differentiation from other models:** Unlike Leading/Lagging, trigger and demand move together with no systematic delay; unlike standard models, trigger enriches the current-period forecast

### 3. Business Impact
- **Primary risk (over-forecast):** Trigger signal overstates demand in current period
- **Primary risk (under-forecast):** Missing trigger signal — forecast reverts to baseline; stockout in high-trigger periods
- **Strategic importance:** High — contemporaneous signals (weather, mobility, events) are the most immediately actionable driver inputs

### 4. Priority Level
🟠 **Tier 2** — High accuracy gain when real-time signal feed is available; requires low-latency data pipeline.

### 5. Model Strategy Overview

#### 5.1 Zero-Demand Handling (Hurdle)
- Active event threshold: P(demand > 0) > 0.70
- Classifier: Logistic Regression with contemporaneous trigger level
- Regressor: LightGBM with same-period trigger
- Fallback: Seasonal baseline (ignore trigger)

#### 5.2 Analogue / Similarity Logic
- Number of analogues: k = 3 (similar CCF(0) strength in same category)
- Similarity criteria: \|CCF(0)\| ±0.10, category, trigger type

#### 5.3 Feature Engineering

**Contemporaneous Feature Construction:**
```
contemporaneous_trigger(t) = trigger(t)  [same-period value]
CCF_0 = CCF(k=0) — contemporaneous correlation strength
trigger_deviation(t) = (trigger(t) − trigger_rolling_mean) / trigger_rolling_std
```

| Granularity | Contemporaneous Features | Baseline Features |
|---|---|---|
| Daily | Same-day temperature, mobility index, event flag, POS feed | 7/30/90-day rolling mean, seasonal index, holiday flag |
| Weekly | Same-week weather index, event flag, same-week POS | 4/8/13-week rolling mean, seasonal index |
| Monthly | Same-month economic index, category trend | 3/6/12-month rolling mean |
| Quarterly | Same-quarter GDP component, category trend | 2/4-quarter rolling mean |
| Yearly | Same-year macro indicator, demographic index | Annual rolling mean |

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM with contemporaneous trigger
- Configuration: Objective = reg:squarederror; Metric = WMAPE, Trigger R²
- Key features: trigger(t), trigger_deviation(t), CCF(0) strength, rolling baseline mean, seasonal index
- When to use: Primary model — CCF(0) > 0.35 and trigger data available in real-time

#### 6.2 Deep Learning (DL)
- Architectures: TFT with contemporaneous trigger as time-varying observed covariate

| Granularity | Lookback | Covariate | Output |
|---|---|---|---|
| Daily | 180 days | Same-day trigger | P10, P50, P90 |
| Weekly | 52 weeks | Same-week trigger | P10, P50, P90 |
| Monthly | 24 months | Same-month trigger | P10, P50, P90 |
| Quarterly | 8 quarters | Same-quarter trigger | P10, P50, P90 |
| Yearly | 5 years | Same-year trigger | P10, P50, P90 |

#### 6.3 Statistical / Time Series Models
- Architectures: ARIMAX with contemporaneous exogenous variable (k=0)

```
d(t) = α + β × trigger(t) + ARIMA(p,d,q) residual
β = contemporaneous effect coefficient
```

#### 6.4 Baseline / Fallback Model
- Fallback triggers: Trigger data unavailable for current period; CCF(0) < 0.20
- Fallback model: Standard behavior seasonal model
- Logging & alerting: Alert if real-time trigger feed fails; alert if CCF(0) drops below 0.20

### 7. Ensemble & Weighting

#### 7.2 Dynamic Weight Schedule

| CCF(0) Strength | LightGBM | TFT | ARIMAX |
|---|---|---|---|
| \|CCF(0)\| < 0.35 | 20% | 10% | 70% |
| \|CCF(0)\| 0.35–0.55 | 50% | 25% | 25% |
| \|CCF(0)\| > 0.55 | 55% | 35% | 10% |

### 8. Uncertainty Quantification
- Method: Quantile regression on contemporaneous model residuals
- Output: [P10, P50, P90]
- Use case: Real-time replenishment decisions; intra-day safety stock adjustment

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Real-time feed rule: Trigger must be available within latency threshold; revert to fallback if delayed
- Capping: min(forecast, 2 × baseline rolling max during high-trigger periods)
- Manual overrides: Operations team trigger quality flag; event data correction

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | WMAPE Target | Trigger R² | CCF(0) Monitor | Bias Alert |
|---|---|---|---|---|
| Daily | < 20% | > 0.30 | Alert if CCF(0) < 0.20 | \|Bias\| > 8% |
| Weekly | < 17% | > 0.25 | Alert if CCF(0) < 0.20 | \|Bias\| > 7% |
| Monthly | < 14% | > 0.20 | Alert if CCF(0) < 0.18 | \|Bias\| > 6% |
| Quarterly | < 11% | > 0.18 | Alert if CCF(0) < 0.15 | \|Bias\| > 5% |
| Yearly | < 9% | > 0.15 | Alert if CCF(0) < 0.12 | \|Bias\| > 4% |

#### 10.2 Backtesting Protocol

| Granularity | Train | Test |
|---|---|---|
| Daily | 180 days | 30 days |
| Weekly | 52 weeks | 13 weeks |
| Monthly | 24 months | 6 months |
| Quarterly | 8 quarters | 2 quarters |
| Yearly | All available | 1 year |

#### 10.3 Retraining

| Granularity | Cadence | Latency |
|---|---|---|
| Daily | Daily | T+4 hours |
| Weekly | Weekly | T+1 day |
| Monthly | Monthly | T+2 days |
| Quarterly | Quarterly | T+3 days |
| Yearly | Annually | T+7 days |

### 11. Exception Handling & Overrides
- Auto-detect: Trigger feed failure → immediate fallback; CCF(0) drops below 0.15 → reclassify; lag shift detected (k* ≠ 0 for 3 estimations) → reclassify to Leading or Lagging
- Manual override: Operations team trigger quality correction; intra-period reforecast trigger
- Override expiration: Per period

### 12. Reclassification / Model Selection

| Condition | Target | Holding Period |
|---|---|---|
| Max CCF shifts to k < 0 for 4 estimations | Leading | 4 estimations |
| Max CCF shifts to k > 0 for 4 estimations | Lagging | 4 estimations |
| \|CCF(0)\| < 0.15 for 3 estimations | No timing signal — standard model | Hard switch |

### 13. Review Cadence
- Per cycle real-time trigger quality monitor; monthly CCF(0) stability check; quarterly full re-evaluation

---

---
