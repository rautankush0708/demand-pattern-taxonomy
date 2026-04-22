## B2 · Intermittent
### 1. Definition
Predicts demand for SKUs with low demand variance (CV² < 0.49) but low demand frequency (ADI ≥ granularity threshold), where demand occurs sporadically but in consistent quantities when it does occur; requires specialist intermittent demand methods.

### 2. Detailed Description
- **Applicable scenarios:** Spare parts, B2B specialty items, niche products, slow-moving lines with occasional orders
- **Boundaries:**

| Granularity | ADI Threshold | CV² Threshold | %Zero Range |
|---|---|---|---|
| Daily | ADI ≥ 1.10 | CV² < 0.49 | 50%–80% |
| Weekly | ADI ≥ 1.32 | CV² < 0.49 | 40%–70% |
| Monthly | ADI ≥ 1.25 | CV² < 0.49 | 30%–60% |
| Quarterly | ADI ≥ 1.20 | CV² < 0.49 | 25%–50% |
| Yearly | ADI ≥ 1.10 | CV² < 0.49 | 20%–40% |

- **Key demand characteristics:** Many zero periods, consistent non-zero quantity when demand occurs, Poisson-like arrival process
- **Differentiation from other models:** Unlike Lumpy, quantity is consistent (low CV²); unlike Sparse, ADI is moderate not extreme; unlike Pulsed, inter-arrival intervals are irregular

### 3. Business Impact
- **Primary risk (over-forecast):** Dead stock accumulation between demand events
- **Primary risk (under-forecast):** Stockout when demand arrives — often critical in aftermarket or MRO context
- **Strategic importance:** Medium-high for aftermarket and MRO; medium for niche retail

### 4. Priority Level
🟠 Tier 2 — Moderate volume but high service criticality in aftermarket and spare parts contexts.

### 5. Model Strategy Overview

#### 5.1 Zero-Demand Handling (Hurdle)
- Active event threshold: P(demand > 0) > 0.30 — many zero periods are expected and correct
- Classifier type: XGBoost on inter-arrival features
- Regressor type: Croston / SBA on non-zero demand only
- Fallback: Croston's method as primary statistical fallback

#### 5.2 Analogue / Similarity Logic
- Number of analogues: k = 3 from same part family or category
- Similarity criteria: ADI range ±0.5, CV² range ±0.1, category, price tier
- Temporal decay: weight = exp(−age / half-life)

| Granularity | Half-Life |
|---|---|
| Daily | 30 days |
| Weekly | 8 weeks |
| Monthly | 4 months |
| Quarterly | 2 quarters |
| Yearly | 2 years |

- Aggregation: Weighted mean on non-zero demand periods

#### 5.3 Feature Engineering

| Granularity | Key Features | Min Non-Zero Obs |
|---|---|---|
| Daily | Inter-arrival mean, inter-arrival std, CV_arrival, days since last demand, rolling non-zero mean (30-day) | ≥ 10 events |
| Weekly | Inter-arrival mean (weeks), CV_arrival, weeks since last demand, rolling non-zero mean (13-week) | ≥ 8 events |
| Monthly | Inter-arrival mean (months), CV_arrival, months since last demand, rolling non-zero mean (6-month) | ≥ 6 events |
| Quarterly | Inter-arrival mean (quarters), CV_arrival, quarters since last demand | ≥ 4 events |
| Yearly | Inter-arrival mean (years), years since last demand | ≥ 3 events |

- External signals: Equipment install base (MRO), order seasonality flag, contract renewal calendar

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: XGBoost (classifier) + XGBoost (regressor on non-zero periods)
- Classifier: Objective = binary:logistic; Metric = AUC, Precision/Recall at 0.30 threshold
- Regressor: Objective = reg:absoluteerror; Metric = MAE on non-zero periods only
- Key features: Inter-arrival time mean/std/CV, periods since last demand, rolling non-zero mean, category, price tier
- When to use: When ≥ 8 demand events in history

#### 6.2 Deep Learning (DL)
- Architectures: DeepAR (handles intermittent natively via negative binomial output distribution)

| Granularity | Lookback | Features | Output |
|---|---|---|---|
| Daily | 180 days | 8 | P10, P50, P90 |
| Weekly | 52 weeks | 8 | P10, P50, P90 |
| Monthly | 24 months | 6 | P10, P50, P90 |
| Quarterly | 8 quarters | 5 | P10, P50, P90 |
| Yearly | 5 years | 4 | P10, P50, P90 |

- Training: Loss = negative log-likelihood (NB distribution); Adam lr = 0.001; Dropout = 0.1; Patience = 10
- When to use: Large portfolio of intermittent SKUs — cross-learning across SKUs improves performance

#### 6.3 Statistical / Time Series Models
- Architectures: Croston's method (primary); SBA (Syntetos-Boylan Approximation) for bias correction

**Croston Formula:**
```
Demand size:    z_t = α × d_t + (1−α) × z_{t-1}   (update only on non-zero periods)
Inter-arrival:  p_t = α × q_t + (1−α) × p_{t-1}   (update only on non-zero periods)
Forecast:       F_t = z_t / p_t

SBA correction: F_SBA = (1 − α/2) × F_Croston
α = 0.1 to 0.3 (optimise on validation MAE)
```

| Granularity | Recommended α | Model |
|---|---|---|
| Daily | 0.10 | SBA |
| Weekly | 0.15 | SBA |
| Monthly | 0.20 | Croston / SBA |
| Quarterly | 0.20 | Croston |
| Yearly | 0.25 | Croston |

- When to use: Default statistical model for intermittent demand; always included in ensemble

#### 6.4 Baseline / Fallback Model
- Fallback triggers: Fewer than 5 demand events; XGBoost convergence failure
- Fallback model: Croston's method (always computable)
- Logging & alerting: Alert if fallback rate > 30%

### 7. Ensemble & Weighting

#### 7.1 Ensemble Scheme
- Combination: D̂_t = w_xgb × XGBoost + w_sba × SBA + w_dar × DeepAR
- Weight determination: Error-inverse weighting on non-zero period MAE

#### 7.2 Dynamic Weight Schedule

| Events in History | XGBoost | SBA | DeepAR |
|---|---|---|---|
| 5–10 events | 20% | 80% | 0% |
| 11–20 events | 50% | 50% | 0% |
| > 20 events | 50% | 30% | 20% |

### 8. Uncertainty Quantification
- Method: Negative binomial distribution fit; quantile regression on non-zero demand
- Output: [P10, P50, P90] on both demand occurrence and quantity separately
- Use case: Stock availability optimisation; spare parts service level

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Capping: min(forecast, 3 × historical max single demand event)
- Manual overrides: Known upcoming demand event (scheduled maintenance, contract renewal)
- Alignment: Forecast consistent with equipment install base count

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | Non-Zero MAE Target | Fill Rate Target | Bias Alert |
|---|---|---|---|
| Daily | MAE on non-zero days < 30% of mean | > 85% | \|Bias\| > 15% |
| Weekly | MAE on non-zero weeks < 25% of mean | > 85% | \|Bias\| > 15% |
| Monthly | MAE on non-zero months < 20% of mean | > 85% | \|Bias\| > 12% |
| Quarterly | MAE on non-zero quarters < 18% of mean | > 85% | \|Bias\| > 10% |
| Yearly | MAE on non-zero years < 15% of mean | > 80% | \|Bias\| > 8% |

#### 10.2 Backtesting Protocol

| Granularity | Method | Train | Test |
|---|---|---|---|
| Daily | Leave-one-out on demand events | Events 1 to n-3 | Last 3 events |
| Weekly | Leave-one-out on demand events | Events 1 to n-3 | Last 3 events |
| Monthly | Leave-one-out on demand events | Events 1 to n-3 | Last 3 events |
| Quarterly | Leave-one-out on demand events | Events 1 to n-2 | Last 2 events |
| Yearly | Leave-one-out on demand events | Events 1 to n-2 | Last 2 events |

#### 10.3 Retraining & Data Freshness

| Granularity | Cadence | Latency |
|---|---|---|
| Daily | Weekly | T+4 hours |
| Weekly | Weekly | T+1 day |
| Monthly | Monthly | T+2 days |
| Quarterly | Quarterly | T+3 days |
| Yearly | Annually | T+7 days |

### 11. Exception Handling & Overrides
- Automatic exception detection: Forecast > 0 for 8+ consecutive periods with zero actuals; demand event > 3 × historical max
- Manual override process: Planner input for known demand events; approval logged
- Override expiration: Single cycle

### 12. Reclassification / Model Selection

| Condition | Target Segment | Holding Period |
|---|---|---|
| CV² rises above 0.49 for 8 periods | Lumpy | 8 periods |
| ADI drops below threshold for 8 periods | Stable | 8 periods |
| %Zero exceeds Sparse threshold for 8 periods | Sparse sub-flag | 8 periods |
| Inter-arrival CV drops below 0.3 | Pulsed | 5 events |

### 13. Review Cadence
- Performance monitoring: Weekly automated — focus on non-zero period accuracy
- Model review meeting: Monthly intermittent demand review
- Full model re-evaluation: Quarterly or on install base change

---
