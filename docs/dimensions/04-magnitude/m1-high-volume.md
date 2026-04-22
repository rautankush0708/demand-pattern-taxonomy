## M1 · High Volume
### 1. Definition
Predicts demand for SKUs in the top 75th percentile of portfolio demand volume at the relevant granularity, where high absolute quantities make even small percentage errors economically significant and justify investment in the most sophisticated forecasting methods.

### 2. Detailed Description
- **Applicable scenarios:** Category leaders, core FMCG lines, high-velocity retail items, strategic B2B accounts
- **Boundaries:**

| Granularity | Percentile | Absolute Guardrail | Rolling Window |
|---|---|---|---|
| Daily | > 75th percentile | > 100 units/day | 90-day rolling mean |
| Weekly | > 75th percentile | > 500 units/week | 26-week rolling mean |
| Monthly | > 75th percentile | > 2,000 units/month | 6-month rolling mean |
| Quarterly | > 75th percentile | > 6,000 units/quarter | 4-quarter rolling mean |
| Yearly | > 75th percentile | > 24,000 units/year | 3-year rolling mean |

- **Key demand characteristics:** High absolute volume, errors are large in absolute units even if small in percentage, inventory holding cost is high, stockout cost is very high
- **Differentiation from other models:** Unlike Medium Volume, justifies full ML + DL ensemble investment; unlike Low Volume, MAPE and WMAPE are reliable metrics; safety stock modelled using σ-based approach

### 3. Business Impact
- **Primary risk (over-forecast):** High absolute excess inventory — large working capital tied up; warehouse capacity consumed
- **Primary risk (under-forecast):** High absolute stockout — lost sales at scale; service level breach on most visible SKUs
- **Strategic importance:** Critical — High Volume SKUs typically represent 20% of portfolio but 60–80% of revenue and volume

### 4. Priority Level
🔴 Tier 1 — Highest investment justified; even 1% WMAPE improvement translates to significant inventory cost savings.

### 5. Model Strategy Overview

#### 5.1 Zero-Demand Handling (Hurdle)
- Active event threshold: P(demand > 0) > 0.95 — high volume SKUs almost never have zero demand
- Classifier: Rule-based flag only — consecutive zeros trigger immediate investigation
- Regressor: Full ensemble — LightGBM + TFT/N-BEATS + ETS
- Fallback: Same period last year × trend factor

#### 5.2 Analogue / Similarity Logic
- Not applicable — sufficient own history; volume too high to need analogues

#### 5.3 Feature Engineering

| Granularity | Rolling Windows | Seasonal Features | External Signals |
|---|---|---|---|
| Daily | 7, 14, 30, 60, 90, 180, 365-day mean, std, max, min, CV² | Day of week, week of year, month, quarter, holiday flag, days to/from peak | Promo calendar, price index, weather (if applicable), competitor index |
| Weekly | 4, 8, 13, 26, 52-week mean, std, max, min, CV² | Week of year, quarter flag, holiday week, seasonal index | Promo calendar, price index, category index |
| Monthly | 2, 3, 6, 12, 24-month mean, std, max, min, CV² | Month of year, quarter, half-year, seasonal index | Promo calendar, macro index |
| Quarterly | 1, 2, 3, 4, 6-quarter mean, std, max, CV² | Quarter of year, half-year, fiscal period | Macro index, category trend |
| Yearly | 1, 2, 3, 4, 5-year mean, std, max, CV² | Long-cycle index | Macro trend, market share index |

- Categorical encoding: Target encoding with smoothing factor = 10
- Feature count: Up to 50 features — high volume justifies full feature engineering

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM (primary) + CatBoost (secondary — handles categorical features natively)
- Configuration: Objective = reg:squarederror; Metric = WMAPE, RMSE
- Hyperparameter tuning: Optuna — 100 trials; 5-fold time series cross-validation
- Key features: All rolling statistics, full seasonal feature set, promotional features, price features, external signals
- When to use: Primary model — always applied for High Volume SKUs

#### 6.2 Deep Learning (DL)
- Architectures: TFT (primary DL) + N-BEATS (secondary DL)

| Granularity | Lookback | Features | Hidden Units | Attention Heads | Output |
|---|---|---|---|---|---|
| Daily | 365 days | 25 | 128 | 4 | P10, P50, P90 |
| Weekly | 104 weeks | 20 | 128 | 4 | P10, P50, P90 |
| Monthly | 36 months | 15 | 64 | 4 | P10, P50, P90 |
| Quarterly | 12 quarters | 12 | 64 | 2 | P10, P50, P90 |
| Yearly | 5 years | 8 | 32 | 2 | P10, P50, P90 |

- Training: Loss = quantile loss (P10, P50, P90); Optimizer = Adam lr = 0.001; Dropout = 0.1; Early stopping patience = 20; Batch size = 64
- When to use: Always applied — deep learning justified by volume importance

#### 6.3 Statistical / Time Series Models
- Architectures: ETS(A,N,A) or ETS(M,N,M); SARIMA; TBATS (daily dual seasonality)

| Granularity | Primary Statistical Model | Period |
|---|---|---|
| Daily | TBATS (dual seasonality) | 7 + 365 |
| Weekly | SARIMA(2,0,1)(1,1,0)_52 | 52 |
| Monthly | SARIMA(1,0,1)(1,1,0)_12 | 12 |
| Quarterly | ETS(A,N,A) | 4 |
| Yearly | ETS(A,A,N) | — |

- When to use: Always included in ensemble — statistical models provide stability and interpretability

#### 6.4 Baseline / Fallback Model
- Fallback triggers: Full ensemble failure (pipeline error)
- Fallback model: Same period last year × trend adjustment
- Logging & alerting: Alert if fallback triggered for High Volume SKU — P1 incident

### 7. Ensemble & Weighting

#### 7.1 Ensemble Scheme
- Combination: D̂_t = w_lgbm × LightGBM + w_catboost × CatBoost + w_tft × TFT + w_nbeats × N-BEATS + w_stat × Statistical
- Weight determination: Error-inverse weighting on rolling 8-period WMAPE; updated weekly

#### 7.2 Dynamic Weight Schedule

| History Available | LightGBM | CatBoost | TFT | N-BEATS | Statistical |
|---|---|---|---|---|---|
| 1–2 years | 40% | 10% | 0% | 0% | 50% |
| 2–3 years | 35% | 10% | 25% | 0% | 30% |
| > 3 years | 30% | 10% | 30% | 15% | 15% |

### 8. Uncertainty Quantification
- Method: Conformal prediction + quantile regression ensemble
- Output: [P10, P25, P50, P75, P90] — full distribution for high-value safety stock optimisation
- Use case: Safety stock = σ_error × z_service_level; z = 1.65 for 95% SL; z = 2.05 for 98% SL

**Safety Stock Formula:**
```
SS = z × σ_forecast_error × √(Lead_time + Review_period)
σ_forecast_error = RMSE over backtesting period
z = service level factor (1.28=90%, 1.65=95%, 2.05=98%, 2.33=99%)
```

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Capping: min(forecast, 1.5 × 52-week rolling max)
- Floor: max(forecast, 0.5 × 52-week rolling min) — prevent excessive down-forecast
- Manual overrides: S&OP consensus adjustment; commercial volume commitment; supply constraint flag
- Alignment: Forecast within ±15% of prior year same period; deviation requires documented justification
- Rounding: Round to nearest pallet/case quantity for operational feasibility

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | WMAPE Target | RMSE Target | Bias Alert | Coverage Target |
|---|---|---|---|---|
| Daily | < 15% | < 20% of mean | \|Bias\| > 5% | 80% P10–P90 |
| Weekly | < 12% | < 15% of mean | \|Bias\| > 5% | 80% P10–P90 |
| Monthly | < 10% | < 12% of mean | \|Bias\| > 4% | 80% P10–P90 |
| Quarterly | < 8% | < 10% of mean | \|Bias\| > 4% | 80% P10–P90 |
| Yearly | < 6% | < 8% of mean | \|Bias\| > 3% | 80% P10–P90 |

#### 10.2 Backtesting Protocol

| Granularity | Method | Train | Test | Min History |
|---|---|---|---|---|
| Daily | Rolling window | 365 days | 30 days | 730 days |
| Weekly | Rolling window | 104 weeks | 13 weeks | 156 weeks |
| Monthly | Rolling window | 36 months | 6 months | 36 months |
| Quarterly | Rolling window | 12 quarters | 2 quarters | 12 quarters |
| Yearly | Expanding window | All available | 1 year | 3 years |

#### 10.3 Retraining & Data Freshness

| Granularity | Cadence | Incremental | Latency |
|---|---|---|---|
| Daily | Daily | Yes — online gradient update | T+4 hours |
| Weekly | Weekly | No | T+1 day |
| Monthly | Monthly | No | T+2 days |
| Quarterly | Quarterly | No | T+3 days |
| Yearly | Annually | No | T+7 days |

### 11. Exception Handling & Overrides
- Automatic exception detection: Forecast > 2 × rolling max; forecast < 0.3 × rolling min; bias drift > 5% for 4 consecutive periods; model WMAPE degrades > 5% vs baseline
- Manual override process: S&OP sign-off required for > 20% override; documented with reason code; reviewed in next S&OP cycle
- Override expiration: Single cycle unless permanent change confirmed

### 12. Reclassification / Model Selection
- To Medium Volume: Percentile drops below 75th for 6 consecutive months — soft transition
- Switching logic: Gradual — blend High and Medium Volume models over 4 periods
- Holding period: 6 months before reclassification confirmed

### 13. Review Cadence
- Performance monitoring: Daily automated dashboard — High Volume SKUs have dedicated monitoring
- Model review meeting: Weekly S&OP review; bi-weekly model performance deep-dive
- Full model re-evaluation: Quarterly; after any major demand shock or structural break

---
