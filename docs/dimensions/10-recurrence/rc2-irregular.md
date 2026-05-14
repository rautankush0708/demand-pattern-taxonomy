# Segment Model Template

## Dimension 10 · Irregular

---

### 1. Definition
Predicts demand for SKUs that recur across time but with inconsistent timing (0.20 ≤ CV_IAT < 0.60), requiring probabilistic occurrence modelling rather than deterministic interval forecasting.

### 2. Detailed Description
- **Applicable scenarios:** Project-based demand with variable timelines, opportunistic purchasing, variable-cycle MRO, demand driven by unpredictable customer triggers, B2B spot orders
- **Boundaries:**

| Granularity | CV_IAT Range | Min Events | RR Trend |
|---|---|---|---|
| Daily | 0.20 ≤ CV_IAT < 0.60 | ≥ 5 events | Any |
| Weekly | 0.20 ≤ CV_IAT < 0.60 | ≥ 5 events | Any |
| Monthly | 0.20 ≤ CV_IAT < 0.60 | ≥ 5 events | Any |
| Quarterly | 0.20 ≤ CV_IAT < 0.60 | ≥ 4 events | Any |
| Yearly | 0.20 ≤ CV_IAT < 0.60 | ≥ 3 events | Any |

- **Key demand characteristics:** Demand occurs periodically but timing is not predictable; intervals vary significantly; probabilistic timing model outperforms deterministic interval approach
- **Differentiation from other models:** Unlike Regular, timing is not predictable enough for deterministic forecasting; unlike One Time, demand does recur; unlike Declining/Growing Recurrence, rate is stable (MK p ≥ 0.10)

### 3. Business Impact
- **Primary risk (over-forecast):** Ordering in non-demand periods — stock held waiting for irregular demand arrival
- **Primary risk (under-forecast):** Missing demand event timing — stockout when irregular demand arrives
- **Strategic importance:** Medium-high — irregular demand is common in B2B and MRO; missed events damage relationships

### 4. Priority Level
🟠 **Tier 2** — Probabilistic timing model required; standard time-series methods fail on irregular recurrence.

### 5. Model Strategy Overview

#### 5.1 Zero-Demand Handling (Hurdle)
- Active event threshold: P(demand > 0) > 0.35 — irregular demand is often sparse
- Classifier type: Logistic Regression / XGBoost on inter-arrival features
- Regressor type: Rolling non-zero mean or Croston on non-zero quantity
- Fallback: Historical occurrence rate × historical non-zero mean

#### 5.2 Analogue / Similarity Logic
- Number of analogues: k = 5 (similar IAT distribution shape in same category)
- Similarity criteria: μ_IAT ±2 periods, CV_IAT ±0.10, category, customer type
- Aggregation: Weighted mean of analogue occurrence rate and quantity

#### 5.3 Feature Engineering

**Survival Model Features:**
```
periods_since_last(t) = t − t_last_demand
hazard_rate(t)        = P(demand occurs at t | no demand since t_last)
                      = h_0(t−t_last) × exp(β × seasonal_flag + γ × external_trigger)
cumulative_hazard(t)  = Σ h_0(s) for s = 1 to (t − t_last)
```

| Granularity | Timing Features | Quantity Features |
|---|---|---|
| Daily | Days since last, hazard rate, cumulative hazard, seasonal flag, day of week | Non-zero mean (90-day), quantity trend |
| Weekly | Weeks since last, hazard rate, seasonal index, week of year | Non-zero mean (26-week) |
| Monthly | Months since last, hazard rate, seasonal index | Non-zero mean (12-month) |
| Quarterly | Quarters since last, hazard rate | Non-zero mean (4-quarter) |
| Yearly | Years since last, hazard rate | Non-zero mean (3-year) |

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: XGBoost (timing classifier) + XGBoost (quantity regressor on non-zero)
- Timing classifier: Objective = binary:logistic; Metric = AUC, Precision/Recall
- Quantity regressor: Objective = reg:absoluteerror; Metric = MAE on non-zero periods only
- Key features: Periods since last demand, hazard rate, cumulative hazard, seasonal index, category, customer type
- When to use: Primary model when ≥ 8 demand events available

#### 6.2 Deep Learning (DL)
- Architectures: DeepAR (handles irregular intermittent patterns via negative binomial distribution)

| Granularity | Lookback | Features | Output |
|---|---|---|---|
| Daily | 180 days | 10 | P10, P50, P90 |
| Weekly | 52 weeks | 10 | P10, P50, P90 |
| Monthly | 24 months | 8 | P10, P50, P90 |
| Quarterly | 8 quarters | 6 | P10, P50, P90 |
| Yearly | 5 years | 5 | P10, P50, P90 |

- When to use: Large portfolio of irregular SKUs — cross-learning across portfolio improves sparse-data problem

#### 6.3 Statistical / Time Series Models
- Architectures: Croston / SBA (Syntetos-Boylan Approximation) with moderate α

**Croston for Irregular:**
```
Demand size:    z_t = α_z × d_t + (1−α_z) × z_{t-1}   α_z = 0.10–0.20
Inter-arrival:  p_t = α_p × q_t + (1−α_p) × p_{t-1}   α_p = 0.10–0.20
Forecast:       F_t = z_t / p_t (Croston)
SBA correction: F_SBA = (1 − α_p/2) × F_Croston   [bias correction]
```

| Granularity | α_z | α_p | Model |
|---|---|---|---|
| Daily | 0.15 | 0.12 | SBA |
| Weekly | 0.15 | 0.12 | SBA |
| Monthly | 0.18 | 0.15 | SBA |
| Quarterly | 0.20 | 0.15 | Croston |
| Yearly | 0.20 | 0.18 | Croston |

- Survival model: Cox proportional hazard for timing; OLS for quantity — used for interpretability

#### 6.4 Baseline / Fallback Model
- Fallback triggers: Event count < 5; survival model convergence failure
- Fallback model: Historical occurrence rate × historical non-zero mean
- Logging & alerting: Alert if fallback rate > 35%

### 7. Ensemble & Weighting

#### 7.1 Ensemble Scheme
- Timing: XGBoost classifier (probability) used as gating function
- Quantity: Weighted average of quantity models on non-zero periods
- Final: D̂_t = P(demand > 0) × D̂_quantity

#### 7.2 Dynamic Weight Schedule

| Events in History | XGBoost | Croston/SBA | DeepAR |
|---|---|---|---|
| 5–8 events | 15% | 85% | 0% |
| 9–20 events | 45% | 55% | 0% |
| > 20 events | 50% | 30% | 20% |

### 8. Uncertainty Quantification
- Method: Negative binomial distribution fit to demand events; quantile regression on non-zero quantity
- Output: [P10, P50, P90] on both occurrence and quantity
- Use case: Safety stock at P75 of quantity; stock policy driven by P(demand > 0) threshold

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Capping: min(forecast, 3 × historical max single demand event)
- Customer signal integration: If known customer trigger approaching → increase P(demand) manually
- Manual overrides: Known upcoming demand event (tender, project milestone, maintenance schedule)

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | Timing AUC | Quantity MAE | False Positive Rate | Bias Alert |
|---|---|---|---|---|
| Daily | > 0.70 | < 20% of non-zero mean | < 10% | \|Bias\| > 12% |
| Weekly | > 0.70 | < 18% | < 10% | \|Bias\| > 10% |
| Monthly | > 0.68 | < 15% | < 10% | \|Bias\| > 8% |
| Quarterly | > 0.65 | < 12% | < 8% | \|Bias\| > 6% |
| Yearly | > 0.65 | < 10% | < 8% | \|Bias\| > 5% |

#### 10.2 Backtesting Protocol

| Granularity | Method | Train | Test |
|---|---|---|---|
| Daily | Leave-one-event-out | Events 1 to n-3 | Last 3 events |
| Weekly | Leave-one-event-out | Events 1 to n-3 | Last 3 events |
| Monthly | Leave-one-event-out | Events 1 to n-3 | Last 3 events |
| Quarterly | Leave-one-event-out | Events 1 to n-2 | Last 2 events |
| Yearly | Leave-one-event-out | Events 1 to n-2 | Last 2 events |

#### 10.3 Retraining & Data Freshness

| Granularity | Cadence | Latency |
|---|---|---|
| Daily | Weekly | T+4 hours |
| Weekly | Weekly | T+1 day |
| Monthly | Monthly | T+2 days |
| Quarterly | Quarterly | T+3 days |
| Yearly | Annually | T+7 days |

### 11. Exception Handling & Overrides
- Automatic exception detection: CV_IAT drops below 0.20 for 5 events → reclassify to Regular; CV_IAT rises above 0.60 → flag as highly irregular; RR trend becomes significant → reclassify to Declining or Growing
- Manual override process: Known demand event input; customer signal flag; approval logged with reason
- Override expiration: Per demand event

### 12. Reclassification / Model Selection

| Condition | Target | Holding Period | Transition |
|---|---|---|---|
| CV_IAT drops below 0.20 for 5 events | Regular | 5 events | Soft blend |
| CV_IAT rises above 0.60 for 5 events | Irregular (extreme) — monitor | 5 events | Flag |
| RR declining (MK p < 0.05; Z < 0) | Declining Recurrence | 4 periods | Soft blend |
| RR growing (MK p < 0.05; Z > 0) | Growing Recurrence | 4 periods | Soft blend |
| Single event remains for > 2 years | One Time | 2 years | Hard switch |

### 13. Review Cadence
- Monthly IAT stability check; quarterly survival model recalibration; annual full re-evaluation

---

---
