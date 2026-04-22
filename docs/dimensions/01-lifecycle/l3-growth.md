## L3 · Growth
### 1. Definition
Predicts demand for SKUs with a statistically confirmed positive demand slope over a granularity-specific rolling window, where trend-aware models are required to avoid systematic under-forecasting.

### 2. Detailed Description
- **Applicable scenarios:** Post-launch acceleration, market expansion, distribution gains, category growth
- **Boundaries:** History ≥ New Launch upper bound; Mann-Kendall p < 0.05 positive slope
- **Key demand characteristics:** Consistent upward slope, increasing volume, low-to-moderate CV², possible seasonality layering onto trend
- **Differentiation from other models:** Unlike Mature, demand is not flat — static models will systematically under-forecast; unlike New Launch, trend is statistically confirmed

### 3. Business Impact
- **Primary risk (over-forecast):** Excess inventory if growth plateau arrives earlier than modelled
- **Primary risk (under-forecast):** Chronic stockouts; lost distribution gains; missed revenue targets
- **Strategic importance:** Very high — growth SKUs drive category share and revenue delivery

### 4. Priority Level
🔴 Tier 1 — Growth SKUs are actively managed by commercial teams; forecast accuracy directly impacts revenue.

### 5. Model Strategy Overview

#### 5.1 Zero-Demand Handling (Hurdle)
- Active event threshold: P(demand > 0) > 0.70 — growth SKUs rarely have zero periods
- Classifier type: Rule-based sanity check only — not primary concern
- Regressor type: LightGBM / TFT
- Fallback: Historical rolling mean if regressor fails

#### 5.2 Analogue / Similarity Logic
- Number of analogues: k = 2 (supplementary only — own signal dominates)
- Similarity criteria: Mature SKUs in same category at similar historical growth rate
- Temporal decay weight: weight = exp(−age / half-life)

| Granularity | Half-Life |
|---|---|
| Daily | 30 days |
| Weekly | 8 weeks |
| Monthly | 4 months |
| Quarterly | 2 quarters |
| Yearly | 2 years |

- Aggregation method: Weighted mean — low weight supplement only

#### 5.3 Feature Engineering

| Granularity | Rolling Windows | Slope Feature | Min Obs Required |
|---|---|---|---|
| Daily | 7, 30, 90, 180-day | β_90day rolling slope | ≥ 112 days |
| Weekly | 4, 8, 13, 26-week | β_13week rolling slope | ≥ 16 weeks |
| Monthly | 2, 3, 6, 12-month | β_6month rolling slope | ≥ 4 months |
| Quarterly | 1, 2, 3, 4-quarter | β_4quarter rolling slope | ≥ 2 quarters |
| Yearly | 1, 2, 3-year | β_3year rolling slope | ≥ 2 years |

- Categorical encoding: Target encoding with smoothing = 10
- External signals: Distribution point count, category growth index, promotional calendar

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM with trend features
- Configuration: Objective = reg:squarederror; Metric = RMSE, WMAPE
- Key features: Rolling means, slope coefficient, distribution coverage, category index, promo flag, period of year
- When to use: Primary model — moderate history with structured trend features

#### 6.2 Deep Learning (DL)
- Architectures: TFT (Temporal Fusion Transformer)

| Granularity | Lookback | Features | Output |
|---|---|---|---|
| Daily | 180 days | 15 | P10, P50, P90 |
| Weekly | 52 weeks | 12 | P10, P50, P90 |
| Monthly | 24 months | 10 | P10, P50, P90 |
| Quarterly | 8 quarters | 8 | P10, P50, P90 |
| Yearly | 5 years | 6 | P10, P50, P90 |

- Training: Loss = quantile loss; Optimizer = Adam lr = 0.001; Dropout = 0.1; Early stopping patience = 10
- When to use: History > 6 months equivalent; multi-horizon forecast required

#### 6.3 Statistical / Time Series Models
- Architectures: ETS(A,A,N) or ARIMA(p,1,q) with first differencing for trend stationarity
- Trend: Additive
- Seasonality: SARIMA if seasonal pattern detected on granularity periods (Section 0.8)
- When to use: Interpretability requirement; short history (just above New Launch boundary)

#### 6.4 Baseline / Fallback Model
- Fallback triggers: Model convergence failure; slope reversal detected mid-cycle
- Fallback model: Short rolling mean + 5% trend adjustment per period
- Logging & alerting: Alert if fallback rate > 15%

### 7. Ensemble & Weighting

#### 7.1 Ensemble Scheme
- Combination: D̂_t = w_lgbm × LightGBM + w_tft × TFT + w_ets × ETS
- Weight determination: Error-inverse weighting on rolling 4-period validation MAE

#### 7.2 Dynamic Weight Schedule

| History Length | LightGBM | TFT | ETS |
|---|---|---|---|
| New Launch boundary to 6 months equiv. | 70% | 0% | 30% |
| 6–12 months equivalent | 60% | 30% | 10% |
| > 12 months equivalent | 50% | 40% | 10% |

### 8. Uncertainty Quantification
- Method: Quantile regression + conformal prediction wrapper
- Output: [P10, P50, P90]
- Use case: Safety stock at P75; replenishment trigger at P50

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Capping: min(forecast, 2 × long-window rolling max)
- Manual overrides: Commercial team distribution gain inputs; trade plan uplift
- Alignment constraints: Forecast growth rate cannot exceed confirmed distribution point growth rate

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | WMAPE Target | Bias Alert | Pinball Loss |
|---|---|---|---|
| Daily | < 25% | Bias > +15% | Monitor P10–P90 |
| Weekly | < 20% | Bias > +15% | Monitor P10–P90 |
| Monthly | < 15% | Bias > +12% | Monitor P10–P90 |
| Quarterly | < 12% | Bias > +10% | Monitor P10–P90 |
| Yearly | < 10% | Bias > +8% | Monitor P10–P90 |

#### 10.2 Backtesting Protocol

| Granularity | Method | Train | Test |
|---|---|---|---|
| Daily | Rolling window | 180 days | 30 days |
| Weekly | Rolling window | 26 weeks | 4 weeks |
| Monthly | Rolling window | 12 months | 3 months |
| Quarterly | Rolling window | 4 quarters | 2 quarters |
| Yearly | Expanding window | All available | 1 year |

#### 10.3 Retraining & Data Freshness

| Granularity | Cadence | Incremental | Latency |
|---|---|---|---|
| Daily | Daily | No | T+4 hours |
| Weekly | Weekly | No | T+1 day |
| Monthly | Monthly | No | T+2 days |
| Quarterly | Quarterly | No | T+3 days |
| Yearly | Annually | No | T+7 days |

### 11. Exception Handling & Overrides
- Automatic exception detection: Slope reversal (positive to flat) for 3 consecutive periods; forecast > 2 × prior period actual
- Manual override process: Commercial sign-off required; distribution plan alignment checked
- Override expiration: Single cycle — reviewed each period

### 12. Reclassification / Model Selection

| Granularity | Reclassify to Mature when | Transition |
|---|---|---|
| Daily | Mann-Kendall p > 0.10 for 4 consecutive 90-day windows | Soft blend over 4 periods |
| Weekly | Mann-Kendall p > 0.10 for 4 consecutive 13-week windows | Soft blend over 4 weeks |
| Monthly | Mann-Kendall p > 0.10 for 4 consecutive 6-month windows | Soft blend over 4 months |
| Quarterly | Mann-Kendall p > 0.10 for 4 consecutive 4-quarter windows | Soft blend over 2 quarters |
| Yearly | Mann-Kendall p > 0.10 for 3 consecutive 3-year windows | Soft blend over 2 years |

### 13. Review Cadence
- Performance monitoring: Per granularity cycle — automated dashboard with slope monitor
- Model review meeting: Weekly commercial forecast review
- Full model re-evaluation: Quarterly or on distribution step-change event

---
