## L4 · Mature

### 1. Definition
Predicts demand for SKUs with stable, flat demand over an extended period where no statistically significant trend exists and demand is well understood; the primary workhorse forecasting segment representing the majority of portfolio volume.

### 2. Detailed Description
- **Applicable scenarios:** Core range SKUs, established products, high-volume stable lines
- **Boundaries:** History ≥ New Launch upper bound; Mann-Kendall p ≥ 0.10 (no significant trend)
- **Key demand characteristics:** Low CV², stable mean, possible seasonality, well-defined baseline
- **Differentiation from other models:** Unlike Growth/Decline, no directional slope; unlike Volatile/Erratic, variance is manageable with standard models

### 3. Business Impact
- **Primary risk (over-forecast):** Working capital tied up in excess inventory
- **Primary risk (under-forecast):** Stockouts on core lines — high customer dissatisfaction
- **Strategic importance:** Very high — Mature SKUs represent majority of revenue and volume

### 4. Priority Level
🔴 Tier 1 — Core revenue base; even small percentage errors create large absolute waste.

### 5. Model Strategy Overview

#### 5.1 Zero-Demand Handling (Hurdle)
- Active event threshold: P(demand > 0) > 0.85 — mature SKUs rarely go to zero
- Classifier type: Rule-based flag only — not primary concern
- Regressor type: LightGBM / ETS
- Fallback: Rolling mean over extended window

#### 5.2 Analogue / Similarity Logic
- Not applicable — sufficient own history; analogues not used for Mature SKUs

#### 5.3 Feature Engineering

| Granularity | Rolling Windows | Seasonal Features |
|---|---|---|
| Daily | 7, 30, 90, 180, 365-day rolling mean & std | Day of week, month index, holiday flag, annual cycle |
| Weekly | 4, 8, 13, 26, 52-week rolling mean & std | Week of year, quarter, holiday flag |
| Monthly | 2, 3, 6, 12, 24-month rolling mean & std | Month of year, quarter, half-year flag |
| Quarterly | 1, 2, 3, 4-quarter rolling mean & std | Quarter of year, half-year |
| Yearly | 1, 2, 3, 4, 5-year rolling mean & std | Long cycle index |

- Categorical encoding: Target encoding with smoothing = 10
- External signals: Promotional calendar, price changes, competitor activity index

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM
- Configuration: Objective = reg:squarederror; Metric = WMAPE, RMSE
- Key features: All rolling means, seasonal index, promo flag, price index, holiday flag
- When to use: Primary model — rich feature set available

#### 6.2 Deep Learning (DL)
- Architectures: N-BEATS / TFT

| Granularity | Lookback | Features |
|---|---|---|
| Daily | 365 days | 18 |
| Weekly | 52 weeks | 15 |
| Monthly | 24 months | 12 |
| Quarterly | 8 quarters | 10 |
| Yearly | 5 years | 8 |

- Training: Loss = MAE; Adam lr = 0.001; Dropout = 0.1; Early stopping patience = 15
- When to use: High-volume SKUs with complex seasonal patterns and long history (> 1 year equivalent)

#### 6.3 Statistical / Time Series Models
- Architectures: ETS(A,N,A) — Holt-Winters additive seasonality; SARIMA for complex seasonality

| Granularity | Primary Seasonal Period | Secondary |
|---|---|---|
| Daily | 7 (day of week) | 365 (annual) |
| Weekly | 52 (annual) | 13 (quarterly) |
| Monthly | 12 (annual) | 3 (quarterly) |
| Quarterly | 4 (annual) | — |
| Yearly | No seasonality | — |

- When to use: Interpretability requirement; prediction intervals needed

#### 6.4 Baseline / Fallback Model
- Fallback triggers: Feature pipeline failure; model convergence issue
- Fallback model: Same period last year (naive seasonal)
- Logging & alerting: Alert if fallback rate > 10%

### 7. Ensemble & Weighting

#### 7.1 Ensemble Scheme
- Combination: D̂_t = w_lgbm × LightGBM + w_ets × ETS + w_nbeats × N-BEATS
- Weight determination: Error-inverse weighting on 8-period rolling WMAPE

#### 7.2 Dynamic Weight Schedule

| History Length | LightGBM | ETS | N-BEATS |
|---|---|---|---|
| New Launch boundary to 1 year equiv. | 60% | 40% | 0% |
| > 1 year equivalent | 50% | 30% | 20% |

### 8. Uncertainty Quantification
- Method: Conformal prediction on residuals
- Output: [P10, P50, P90]
- Use case: Safety stock optimisation at target service level

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Capping: min(forecast, 1.5 × full-year rolling max)
- Manual overrides: Range review decisions; promotional plan changes
- Alignment constraints: Forecast within ±20% of prior year same period unless justified

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
- Manual override process: Planner approval via dashboard; reason code required
- Override expiration: Single cycle unless permanent range change flagged

### 12. Reclassification / Model Selection

| Granularity | To Growth | To Decline | Transition |
|---|---|---|---|
| Daily | Positive slope p < 0.05, 4 consecutive 90-day windows | Negative slope p < 0.05, 4 consecutive 90-day windows | Soft blend over 4 periods |
| Weekly | Positive slope p < 0.05, 4 consecutive 13-week windows | Negative slope p < 0.05, 4 consecutive 13-week windows | Soft blend over 4 weeks |
| Monthly | Positive slope p < 0.05, 4 consecutive 6-month windows | Negative slope p < 0.05, 4 consecutive 6-month windows | Soft blend over 4 months |
| Quarterly | Positive slope p < 0.05, 4 consecutive windows | Negative slope p < 0.05, 4 consecutive windows | Soft blend over 2 quarters |
| Yearly | Positive slope p < 0.05, 3 consecutive windows | Negative slope p < 0.05, 3 consecutive windows | Soft blend over 2 years |

### 13. Review Cadence
- Performance monitoring: Per cycle automated dashboard
- Model review meeting: Bi-weekly S&OP forecast review
- Full model re-evaluation: Quarterly

---

