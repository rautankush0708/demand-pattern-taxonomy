## B1 · Stable

### 1. Definition
Predicts demand for SKUs with low demand variance (CV² < 0.49) and high demand frequency (ADI below granularity threshold), where demand is consistent, well-behaved, and highly forecastable with standard time-series methods.

### 2. Detailed Description
- **Applicable scenarios:** Core FMCG lines, everyday essentials, high-frequency replenishment items, staple categories
- **Boundaries:**

| Granularity | ADI Threshold | CV² Threshold | Volume | Additional |
|---|---|---|---|---|
| Daily | ADI < 1.10 | CV² < 0.49 | > 5th pctile | No significant trend (p ≥ 0.10) |
| Weekly | ADI < 1.32 | CV² < 0.49 | > 5th pctile | No significant trend (p ≥ 0.10) |
| Monthly | ADI < 1.25 | CV² < 0.49 | > 5th pctile | No significant trend (p ≥ 0.10) |
| Quarterly | ADI < 1.20 | CV² < 0.49 | > 5th pctile | No significant trend (p ≥ 0.10) |
| Yearly | ADI < 1.10 | CV² < 0.49 | > 5th pctile | No significant trend (p ≥ 0.10) |

- **Key demand characteristics:** Low variance, high frequency, minimal zero periods, flat or mildly varying baseline
- **Differentiation from other models:** Unlike Volatile/Erratic, CV² is low; unlike Slow Mover, volume is above threshold; unlike Intermittent, ADI is below threshold; unlike Trending, no directional slope detected

### 3. Business Impact
- **Primary risk (over-forecast):** Excess working capital in inventory — low probability with good models
- **Primary risk (under-forecast):** Service level breaches on core revenue lines
- **Strategic importance:** Very high — Stable SKUs form the revenue backbone of most portfolios

### 4. Priority Level
🔴 Tier 1 — High volume, high frequency — even small percentage errors create large absolute inventory waste.

### 5. Model Strategy Overview

#### 5.1 Zero-Demand Handling (Hurdle)
- Active event threshold: P(demand > 0) > 0.90 — stable SKUs rarely go to zero
- Classifier type: Rule-based flag only — 2+ consecutive zero periods triggers alert
- Regressor type: LightGBM primary; ETS supplementary
- Fallback: Rolling mean over extended window

#### 5.2 Analogue / Similarity Logic
- Not applicable — sufficient own history; analogues not used for Stable SKUs

#### 5.3 Feature Engineering

| Granularity | Rolling Windows | Seasonal Features | External Signals |
|---|---|---|---|
| Daily | 7, 30, 90, 180, 365-day mean & std | Day of week, month index, holiday flag, annual cycle index | Promo calendar, price index |
| Weekly | 4, 8, 13, 26, 52-week mean & std | Week of year, quarter flag, holiday proximity | Promo calendar, price index |
| Monthly | 2, 3, 6, 12, 24-month mean & std | Month of year, quarter, half-year flag | Promo calendar, price index |
| Quarterly | 1, 2, 3, 4-quarter mean & std | Quarter of year, half-year | Promo flag |
| Yearly | 1, 2, 3, 4, 5-year mean & std | Long cycle index | Macro index |

- Categorical encoding: Target encoding with smoothing factor = 10

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM
- Configuration: Objective = reg:squarederror; Metric = WMAPE, RMSE
- Key features: All rolling means, seasonal index, promo flag, price index, holiday flag, period of year
- When to use: Primary model — rich feature set, well-understood demand

#### 6.2 Deep Learning (DL)
- Architectures: N-BEATS / TFT

| Granularity | Lookback | Features | Output |
|---|---|---|---|
| Daily | 365 days | 18 | P10, P50, P90 |
| Weekly | 52 weeks | 15 | P10, P50, P90 |
| Monthly | 24 months | 12 | P10, P50, P90 |
| Quarterly | 8 quarters | 10 | P10, P50, P90 |
| Yearly | 5 years | 8 | P10, P50, P90 |

- Training: Loss = MAE; Adam lr = 0.001; Dropout = 0.1; Early stopping patience = 15
- When to use: High-volume SKUs with complex seasonal patterns; history > 1 year equivalent

#### 6.3 Statistical / Time Series Models
- Architectures: ETS(A,N,A) — Holt-Winters additive seasonality

| Granularity | Seasonal Period | Model Variant |
|---|---|---|
| Daily | 7 (primary), 365 (secondary) | TBATS for dual seasonality |
| Weekly | 52 (primary), 13 (secondary) | ETS(A,N,A) with period = 52 |
| Monthly | 12 (primary), 3 (secondary) | SARIMA(p,0,q)(P,0,Q)_12 |
| Quarterly | 4 | ETS(A,N,A) with period = 4 |
| Yearly | None | ETS(A,N,N) — no seasonality |

- When to use: Interpretability requirement; prediction intervals needed; short history

#### 6.4 Baseline / Fallback Model
- Fallback triggers: Feature pipeline failure; model convergence issue
- Fallback model: Same period last year (naive seasonal)
- Logging & alerting: Alert if fallback rate > 10%

### 7. Ensemble & Weighting

#### 7.1 Ensemble Scheme
- Combination: D̂_t = w_lgbm × LightGBM + w_ets × ETS + w_dl × N-BEATS
- Weight determination: Error-inverse weighting on 8-period rolling WMAPE

#### 7.2 Dynamic Weight Schedule

| History Length | LightGBM | ETS | N-BEATS / TFT |
|---|---|---|---|
| Up to 1 year equivalent | 60% | 40% | 0% |
| > 1 year equivalent | 50% | 30% | 20% |

### 8. Uncertainty Quantification
- Method: Conformal prediction on residuals
- Output: [P10, P50, P90]
- Use case: Safety stock optimisation at target service level; P90 used for max stock bound

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Capping: min(forecast, 1.5 × full-year rolling max)
- Manual overrides: Range review decisions; promotional plan changes; known supply disruptions
- Alignment constraints: Forecast within ±20% of prior year same period unless justified with reason code

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | WMAPE Target | Bias Alert | Coverage Target |
|---|---|---|---|
| Daily | < 20% | \|Bias\| > 10% | 80% P10–P90 |
| Weekly | < 18% | \|Bias\| > 8% | 80% P10–P90 |
| Monthly | < 15% | \|Bias\| > 7% | 80% P10–P90 |
| Quarterly | < 12% | \|Bias\| > 6% | 80% P10–P90 |
| Yearly | < 10% | \|Bias\| > 5% | 80% P10–P90 |

#### 10.2 Backtesting Protocol

| Granularity | Method | Train | Test | Min History |
|---|---|---|---|---|
| Daily | Rolling window | 180 days | 30 days | 365 days |
| Weekly | Rolling window | 52 weeks | 13 weeks | 104 weeks |
| Monthly | Rolling window | 24 months | 6 months | 24 months |
| Quarterly | Rolling window | 8 quarters | 2 quarters | 8 quarters |
| Yearly | Expanding window | All available | 1 year | 3 years |

#### 10.3 Retraining & Data Freshness

| Granularity | Cadence | Incremental | Latency |
|---|---|---|---|
| Daily | Daily | No | T+4 hours |
| Weekly | Weekly | No | T+1 day |
| Monthly | Monthly | No | T+2 days |
| Quarterly | Quarterly | No | T+3 days |
| Yearly | Annually | No | T+7 days |

### 11. Exception Handling & Overrides
- Automatic exception detection: Forecast > 2 × historical max; 3+ consecutive zero actuals; bias drift > alert threshold for 4 periods
- Manual override process: Planner approval via dashboard; reason code required; logged with timestamp
- Override expiration: Single cycle unless permanent range change flagged

### 12. Reclassification / Model Selection

| Condition | Target Segment | Holding Period |
|---|---|---|
| CV² rises above 0.49 for 8 consecutive periods | Erratic or Volatile | 8 periods confirmation |
| ADI rises above threshold for 8 consecutive periods | Intermittent | 8 periods confirmation |
| Volume drops below 5th percentile for 8 periods | Slow Mover | 8 periods confirmation |
| Trend detected (Mann-Kendall p < 0.05) for 4 periods | Trending | 4 periods confirmation |
| Structural break detected | Step Change | Immediate |

- Switching logic: Soft blend over 4 periods for gradual transitions; hard switch for Step Change

### 13. Review Cadence
- Performance monitoring: Per cycle automated dashboard
- Model review meeting: Bi-weekly S&OP forecast review
- Full model re-evaluation: Quarterly

---

