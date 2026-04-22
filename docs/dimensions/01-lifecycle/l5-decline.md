## L5 · Decline
### 1. Definition
Predicts demand for SKUs with a statistically confirmed negative demand slope, requiring trend-aware models with downward bias controls to avoid systematic over-forecasting and inventory accumulation.

### 2. Detailed Description
- **Applicable scenarios:** Ageing products, distribution losses, category contraction, competitive displacement
- **Boundaries:** History ≥ New Launch upper bound; Mann-Kendall p < 0.05 negative slope
- **Key demand characteristics:** Consistent downward slope, shrinking volume, possibly rising CV² as volume drops
- **Differentiation from other models:** Unlike Phasing Out, decline is market-driven not supply-decision-driven; unlike Inactive, demand still exists

### 3. Business Impact
- **Primary risk (over-forecast):** Excess inventory accumulation — write-offs and obsolescence dominant risk
- **Primary risk (under-forecast):** Minimal concern — declining SKU stockouts are low priority
- **Strategic importance:** Medium — inventory risk and write-off prevention are primary objectives

### 4. Priority Level
🟠 Tier 2 — Over-forecast risk dominates; inventory write-off prevention is key business objective.

### 5. Model Strategy Overview

#### 5.1 Zero-Demand Handling (Hurdle)
- Active event threshold: P(demand > 0) > 0.50 — declining SKUs approach zero over time
- Classifier type: Logistic Regression with trend features
- Regressor type: LightGBM with negative slope features
- Fallback when disagree: Forecast = 0 if classifier < 0.50

#### 5.2 Analogue / Similarity Logic
- Number of analogues: k = 3 (declining SKUs from same category)
- Similarity criteria: Category, decline rate (weekly slope coefficient), volume at decline start
- Temporal decay weight: weight = exp(−age / half-life)

| Granularity | Half-Life |
|---|---|
| Daily | 21 days |
| Weekly | 6 weeks |
| Monthly | 3 months |
| Quarterly | 2 quarters |
| Yearly | 1.5 years |

- Aggregation method: Weighted mean of decline trajectories

#### 5.3 Feature Engineering

| Granularity | Slope Window | Key Features |
|---|---|---|
| Daily | β_90day | Periods since peak, rolling mean, distribution loss rate, competitor entry flag |
| Weekly | β_13week | Weeks since peak, rolling mean, distribution loss rate, category index |
| Monthly | β_6month | Months since peak, rolling mean, category index |
| Quarterly | β_4quarter | Quarters since peak, rolling mean |
| Yearly | β_3year | Years since peak |

- Categorical encoding: Target encoding smoothing = 10

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM with downward bias correction
- Configuration: Objective = reg:squarederror; Metric = WMAPE, MAE
- Key features: Slope coefficient, periods since peak, rolling mean, distribution loss rate, category index
- When to use: Primary model

#### 6.2 Deep Learning (DL)
- Architectures: Not recommended — complexity unwarranted for declining SKUs
- When to use: Not applicable

#### 6.3 Statistical / Time Series Models
- Architectures: ETS(A,A,N) with damped trend — prevents over-extrapolation of decline

| Granularity | Damping Factor (phi) |
|---|---|
| Daily | 0.90 |
| Weekly | 0.85 |
| Monthly | 0.80 |
| Quarterly | 0.75 |
| Yearly | 0.70 |

- When to use: When interpretability needed; damped trend prevents forecast crossing zero prematurely

#### 6.4 Baseline / Fallback Model
- Fallback triggers: Slope reversal for 3+ consecutive periods
- Fallback model: Short rolling mean — conservative hold
- Logging & alerting: Alert if fallback rate > 20%

### 7. Ensemble & Weighting

#### 7.1 Ensemble Scheme
- Combination: D̂_t = w_lgbm × LightGBM + w_ets × ETS(damped)
- Weight determination: Error-inverse weighting on 4-period rolling MAE

#### 7.2 Dynamic Weight Schedule

| Decline Stage | LightGBM | ETS Damped |
|---|---|---|
| Early decline (mild slope, CV² still low) | 70% | 30% |
| Late decline (steep slope, rising CV²) | 50% | 50% |

### 8. Uncertainty Quantification
- Method: Quantile regression
- Output: [P10, P50, P90]
- Use case: P10 for minimum buy; P50 for base; P90 for worst-case inventory cover

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Capping: min(forecast, prior period rolling mean) — prevent upward drift in forecast
- Manual overrides: Delisting date input; clearance promotion flags
- Alignment constraints: Forecast must not exceed current stock on hand + confirmed inbound

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | WMAPE Target | Over-Forecast Bias Alert | Train | Test |
|---|---|---|---|---|
| Daily | < 25% | Bias > +10% | 180 days | 30 days |
| Weekly | < 20% | Bias > +10% | 26 weeks | 4 weeks |
| Monthly | < 18% | Bias > +8% | 12 months | 3 months |
| Quarterly | < 15% | Bias > +6% | 4 quarters | 2 quarters |
| Yearly | < 12% | Bias > +5% | 3 years | 1 year |

#### 10.3 Retraining & Data Freshness

| Granularity | Cadence | Incremental | Latency |
|---|---|---|---|
| Daily | Daily | No | T+4 hours |
| Weekly | Weekly | No | T+1 day |
| Monthly | Monthly | No | T+2 days |
| Quarterly | Quarterly | No | T+3 days |
| Yearly | Annually | No | T+7 days |

### 11. Exception Handling & Overrides
- Automatic exception detection: Forecast > prior rolling mean; slope reversal for 3+ consecutive periods
- Manual override process: Supply chain planner sign-off; reason code logged
- Override expiration: Single cycle

### 12. Reclassification / Model Selection

| Granularity | To Inactive | To Mature | Transition |
|---|---|---|---|
| Daily | 0 demand ≥ 91 consecutive days | Slope reverses positive p < 0.05 for 4 windows | Inactive = hard; Mature = soft blend 4 periods |
| Weekly | 0 demand ≥ 13 consecutive weeks | Slope reverses positive p < 0.05 for 4 windows | Inactive = hard; Mature = soft blend 4 weeks |
| Monthly | 0 demand ≥ 3 consecutive months | Slope reverses positive p < 0.05 for 4 windows | Inactive = hard; Mature = soft blend 4 months |
| Quarterly | 0 demand ≥ 1 consecutive quarter | Slope reverses positive p < 0.05 for 3 windows | Inactive = hard; Mature = soft blend 2 quarters |
| Yearly | 0 demand ≥ 1 consecutive year | Slope reverses positive p < 0.05 for 2 windows | Inactive = hard; Mature = soft blend 2 years |

### 13. Review Cadence
- Performance monitoring: Per cycle — over-forecast alert primary watch item
- Model review meeting: Bi-weekly — focus on obsolescence risk
- Full model re-evaluation: Quarterly or on delisting decision

---
