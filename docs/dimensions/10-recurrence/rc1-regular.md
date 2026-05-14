# Segment Model Template

## Dimension 10 · Regular

---

### 1. Definition
Predicts demand for SKUs with highly consistent inter-arrival intervals (CV_IAT < 0.20), where timing predictability enables interval-based deterministic forecasting rather than probabilistic occurrence modelling.

### 2. Detailed Description
- **Applicable scenarios:** B2B scheduled replenishment, subscription-like ordering, fixed maintenance cycles, contracted delivery schedules, weekly standing orders
- **Boundaries:**

| Granularity | CV_IAT | Mean IAT Range | Min Events | RR Trend |
|---|---|---|---|---|
| Daily | < 0.20 | Any | ≥ 5 events | p ≥ 0.10 (stable) |
| Weekly | < 0.20 | Any | ≥ 5 events | p ≥ 0.10 |
| Monthly | < 0.20 | Any | ≥ 5 events | p ≥ 0.10 |
| Quarterly | < 0.20 | Any | ≥ 4 events | p ≥ 0.10 |
| Yearly | < 0.20 | Any | ≥ 3 events | p ≥ 0.10 |

- **Key demand characteristics:** Highly consistent intervals between demand events; timing is nearly deterministic; quantity may vary but arrival is predictable
- **Differentiation from other models:** Unlike Irregular, timing is predictable; unlike Pulsed (Behavior B7), Regular focuses on recurrence consistency across the full history not just inter-arrival CV; like Pulsed but at the recurrence level, not just behavior level

### 3. Business Impact
- **Primary risk (over-forecast):** Ordering between expected demand events — unnecessary inventory
- **Primary risk (under-forecast):** Missing expected demand event — stockout on a known recurring order
- **Strategic importance:** High in B2B — scheduled orders are plannable; timing accuracy is the primary commercial requirement

### 4. Priority Level
🟠 **Tier 2** — Relatively easy to forecast given timing predictability; primary challenge is quantity accuracy not timing.

### 5. Model Strategy Overview

#### 5.1 Zero-Demand Handling (Hurdle)
- Active event threshold: Deterministic — P(demand > 0) = 1 in expected demand period; = 0 outside
- Classifier type: Interval-based rule — next demand at t_last + μ_IAT (±σ_IAT confidence window)
- Regressor type: Rolling non-zero mean for quantity; ETS for quantity trend
- Fallback: Historical non-zero mean × expected demand flag

#### 5.2 Analogue / Similarity Logic
- Number of analogues: k = 3 (similar IAT structure in same category or customer)
- Similarity criteria: μ_IAT ±1 period, CV_IAT ±0.05, category, customer type
- Use: Cross-validate own IAT estimate when event count is low (< 8 events)

#### 5.3 Feature Engineering

**Interval-Based Features:**
```
periods_since_last_demand(t) = t − t_last_demand
expected_next_demand(t)      = t_last_demand + μ_IAT
in_demand_window(t)          = 1 if |t − expected_next_demand| ≤ σ_IAT
days_to_expected(t)          = expected_next_demand(t) − t
```

| Granularity | IAT Features | Quantity Features |
|---|---|---|
| Daily | Days since last demand, expected next demand date, in-window flag, CV_IAT | Non-zero mean (90-day), 7/30-day rolling non-zero mean |
| Weekly | Weeks since last demand, expected next week, in-window flag | Non-zero mean (26-week), 4/13-week rolling non-zero mean |
| Monthly | Months since last demand, expected next month, in-window flag | Non-zero mean (12-month), 3/6-month rolling |
| Quarterly | Quarters since last, expected next quarter | Non-zero mean (4-quarter) |
| Yearly | Years since last, expected next year | Non-zero mean (3-year) |

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM with IAT features — timing model (classifier) + quantity model (regressor)
- Timing classifier: Objective = binary:logistic; Metric = AUC, Precision at demand window
- Quantity regressor: Objective = reg:absoluteerror; Metric = MAE on non-zero periods
- When to use: When ≥ 8 demand events available and quantity shows some variability

#### 6.2 Deep Learning (DL)
- Architectures: Not primary — deterministic timing makes DL unnecessary for timing; DeepAR acceptable for quantity only if history long enough

| Granularity | Lookback | Output |
|---|---|---|
| Daily | 180 days | P10, P50, P90 (quantity only) |
| Weekly | 52 weeks | P10, P50, P90 (quantity only) |
| Monthly | 24 months | P10, P50, P90 (quantity only) |
| Quarterly | 8 quarters | P10, P50, P90 (quantity only) |
| Yearly | 5 years | P10, P50, P90 (quantity only) |

- When to use: History > 2 years AND quantity variability is moderate (CV_qty > 0.20)

#### 6.3 Statistical / Time Series Models
- Architectures: Croston with very low α (exploits high IAT regularity)

**Croston for Regular Demand:**
```
Demand size:    z_t = α_z × d_t + (1−α_z) × z_{t-1}   (update on non-zero only)
Inter-arrival:  p_t = α_p × q_t + (1−α_p) × p_{t-1}   (update on non-zero only)
Forecast:       F_t = z_t / p_t

For Regular: α_z = 0.05; α_p = 0.05  (very low — exploit regularity)
Low α preserves stable interval estimate; high stability = low α optimal
```

| Granularity | α_z | α_p |
|---|---|---|
| Daily | 0.05 | 0.05 |
| Weekly | 0.05 | 0.05 |
| Monthly | 0.08 | 0.05 |
| Quarterly | 0.10 | 0.05 |
| Yearly | 0.10 | 0.08 |

- When to use: Default statistical model — always included in ensemble

#### 6.4 Baseline / Fallback Model
- Fallback triggers: Event count < 5; IAT distribution insufficient for estimation
- Fallback model: Historical non-zero mean × demand_window_flag (1 in expected period; 0 otherwise)
- Logging & alerting: Alert if expected demand event missed (t > expected_next + 2σ_IAT)

### 7. Ensemble & Weighting

#### 7.1 Ensemble Scheme
- Timing: Deterministic interval rule (primary) — not ensemble-weighted
- Quantity: D̂_quantity = w_lgbm × LightGBM + w_croston × Croston + w_dl × DeepAR
- Weight determination: Error-inverse on non-zero period MAE

#### 7.2 Dynamic Weight Schedule

| Events in History | LightGBM | Croston | DeepAR |
|---|---|---|---|
| 5–8 events | 10% | 90% | 0% |
| 9–20 events | 40% | 60% | 0% |
| > 20 events | 50% | 30% | 20% |

### 8. Uncertainty Quantification
- Method: Empirical distribution of IAT and non-zero quantity
- Output: [P10, P50, P90] — narrow timing interval (±σ_IAT); moderate quantity interval
- Use case: Safety stock = P75 of quantity; timing buffer = +1σ_IAT on expected date

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Timing enforcement: Forecast = 0 outside demand window (t < expected − σ_IAT or t > expected + σ_IAT)
- Missed event alert: If demand does not arrive within expected window → alert planner immediately
- Manual overrides: Customer schedule change; contract amendment; holiday adjustment to expected date

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | Timing Accuracy | Quantity MAE | False Positive Rate | Bias Alert |
|---|---|---|---|---|
| Daily | > 95% (±1 day) | < 10% of mean | < 5% | \|Bias\| > 8% |
| Weekly | > 90% (±1 week) | < 10% of mean | < 5% | \|Bias\| > 8% |
| Monthly | > 90% (±1 month) | < 8% of mean | < 5% | \|Bias\| > 6% |
| Quarterly | > 85% (±1 quarter) | < 8% of mean | < 5% | \|Bias\| > 6% |
| Yearly | > 85% (±1 year) | < 6% of mean | < 5% | \|Bias\| > 5% |

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
- Automatic exception detection: CV_IAT rises above 0.30 for 5 consecutive events → reclassify to Irregular; expected demand missed by > 2σ_IAT → missed event alert; RR trend becomes significant (p < 0.05) → reclassify to Declining or Growing Recurrence
- Manual override process: Customer schedule change; contract end flag; holiday rescheduling; planner approval via dashboard
- Override expiration: Per demand cycle

### 12. Reclassification / Model Selection

| Condition | Target Segment | Holding Period | Transition |
|---|---|---|---|
| CV_IAT rises above 0.30 for 5 events | Irregular | 5 events | Soft blend |
| RR declining (MK p < 0.05; Z < 0) | Declining Recurrence | 4 periods | Soft blend |
| RR growing (MK p < 0.05; Z > 0) | Growing Recurrence | 4 periods | Soft blend |
| Demand ceases for > inactive threshold | Lifecycle: Inactive | Immediate | Hard switch |

### 13. Review Cadence
- Per demand event review; monthly IAT stability check; quarterly full re-evaluation

---

---
