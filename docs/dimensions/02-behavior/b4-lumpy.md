## B4 · Lumpy
### 1. Definition
Predicts demand for SKUs with high demand variance (CV² ≥ 0.49) and low demand frequency (ADI ≥ granularity threshold), the hardest-to-forecast segment combining sporadic occurrence with large unpredictable quantity spikes.

### 2. Detailed Description
- **Applicable scenarios:** Capital goods, project-based demand, large batch orders, tender-driven categories
- **Boundaries:**

| Granularity | ADI Threshold | CV² Threshold |
|---|---|---|
| Daily | ADI ≥ 1.10 | CV² ≥ 0.49 |
| Weekly | ADI ≥ 1.32 | CV² ≥ 0.49 |
| Monthly | ADI ≥ 1.25 | CV² ≥ 0.49 |
| Quarterly | ADI ≥ 1.20 | CV² ≥ 0.49 |
| Yearly | ADI ≥ 1.10 | CV² ≥ 0.49 |

- **Key demand characteristics:** Infrequent demand, massive quantity variance, extreme spikes when active, long zero stretches
- **Differentiation from other models:** Unlike Erratic, ADI is above threshold (infrequent); unlike Intermittent, CV² is high (large quantity variance when demand occurs); this is the hardest behavioral segment to forecast

### 3. Business Impact
- **Primary risk (over-forecast):** Severe dead stock — lumpy over-forecast creates large idle inventory
- **Primary risk (under-forecast):** Catastrophic stockout when a large order arrives unexpectedly
- **Strategic importance:** High for capital goods, MRO, and B2B; inventory cost of error is extreme

### 4. Priority Level
🔴 Tier 1 — Error magnitude per event is very large; both directions of error are extremely costly.

### 5. Model Strategy Overview

#### 5.1 Zero-Demand Handling (Hurdle)
- Active event threshold: P(demand > 0) > 0.25 — infrequent demand is the norm
- Classifier type: XGBoost (occurrence model — when will demand happen?)
- Regressor type: XGBoost / CatBoost (quantity model — how much when it does?)
- Two-stage prediction: Stage 1 = occurrence probability; Stage 2 = quantity given occurrence
- Fallback: Stage 1 = historical occurrence rate; Stage 2 = historical non-zero median

#### 5.2 Analogue / Similarity Logic
- Number of analogues: k = 5 (more analogues needed — own data sparse)
- Similarity criteria: Category, CV² range ±0.15, ADI range ±0.5, price tier, customer type
- Temporal decay: weight = exp(−age / half-life)

| Granularity | Half-Life |
|---|---|
| Daily | 60 days |
| Weekly | 13 weeks |
| Monthly | 6 months |
| Quarterly | 3 quarters |
| Yearly | 3 years |

- Aggregation: Weighted median (robust to extreme analogue outliers)

#### 5.3 Feature Engineering

| Granularity | Occurrence Features | Quantity Features |
|---|---|---|
| Daily | Days since last demand, 90-day occurrence rate, seasonal occurrence flag | Non-zero mean (90-day), non-zero max, CV², customer order flag |
| Weekly | Weeks since last demand, 13-week occurrence rate, seasonal flag | Non-zero mean (13-week), non-zero max, CV², order flag |
| Monthly | Months since last demand, 6-month occurrence rate | Non-zero mean (6-month), non-zero max, CV² |
| Quarterly | Quarters since last demand, occurrence rate | Non-zero mean, CV² |
| Yearly | Years since last demand, occurrence rate | Non-zero mean, CV² |

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: Two-stage XGBoost (occurrence classifier + quantity regressor)
- Occurrence classifier: Objective = binary:logistic; Metric = AUC, Recall
- Quantity regressor: Objective = reg:absoluteerror (robust to extreme values); Metric = MAE
- Final forecast: D̂_t = P(occurrence_t) × Ê(quantity_t | occurrence)
- When to use: Primary model when ≥ 8 demand events in history

#### 6.2 Deep Learning (DL)
- Architectures: DeepAR with negative binomial output (handles lumpiness natively)

| Granularity | Lookback | Features |
|---|---|---|
| Daily | 180 days | 10 |
| Weekly | 52 weeks | 10 |
| Monthly | 24 months | 8 |
| Quarterly | 8 quarters | 6 |
| Yearly | 5 years | 5 |

- When to use: Large portfolio of lumpy SKUs — cross-SKU learning improves sparse data problem

#### 6.3 Statistical / Time Series Models
- Architectures: Croston's method (occurrence + quantity separately)

**Croston for Lumpy:**
```
Demand size (non-zero):    z_t = α_z × d_t + (1−α_z) × z_{t-1}   α_z = 0.1–0.2
Inter-arrival:             p_t = α_p × q_t + (1−α_p) × p_{t-1}   α_p = 0.1–0.2
Forecast:                  F_t = z_t / p_t
Note: For lumpy, z_t has high variance — wide prediction intervals required
```

| Granularity | α_z | α_p |
|---|---|---|
| Daily | 0.10 | 0.10 |
| Weekly | 0.10 | 0.10 |
| Monthly | 0.15 | 0.15 |
| Quarterly | 0.15 | 0.15 |
| Yearly | 0.20 | 0.20 |

#### 6.4 Baseline / Fallback Model
- Fallback triggers: Fewer than 5 demand events; model convergence failure
- Fallback model: Historical occurrence rate × historical non-zero median
- Logging & alerting: Alert if fallback rate > 40%

### 7. Ensemble & Weighting

#### 7.2 Dynamic Weight Schedule

| Events in History | XGBoost 2-Stage | Croston | DeepAR |
|---|---|---|---|
| < 8 events | 10% | 90% | 0% |
| 8–20 events | 50% | 50% | 0% |
| > 20 events | 50% | 25% | 25% |

### 8. Uncertainty Quantification
- Method: Full distribution — negative binomial fit to demand events
- Output: [P10, P50, P90] — very wide intervals expected for lumpy demand
- Use case: Inventory policy decision — cycle stock vs safety stock split

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Capping: min(forecast, 2 × largest historical single demand event)
- Manual overrides: Known large order event; tender win notification
- Alignment: Cross-reference with customer order pipeline / CRM for known future events

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | MAE Target | Bias Alert | Fill Rate |
|---|---|---|---|
| Daily | MAE < 50% of non-zero mean | \|Bias\| > 20% | > 80% |
| Weekly | MAE < 40% of non-zero mean | \|Bias\| > 18% | > 80% |
| Monthly | MAE < 35% of non-zero mean | \|Bias\| > 15% | > 80% |
| Quarterly | MAE < 30% of non-zero mean | \|Bias\| > 12% | > 80% |
| Yearly | MAE < 25% of non-zero mean | \|Bias\| > 10% | > 75% |

#### 10.2 Backtesting Protocol

| Granularity | Method | Train | Test |
|---|---|---|---|
| Daily | Leave-one-out on demand events | Events 1 to n-3 | Last 3 events |
| Weekly | Leave-one-out on demand events | Events 1 to n-3 | Last 3 events |
| Monthly | Leave-one-out | Events 1 to n-2 | Last 2 events |
| Quarterly | Leave-one-out | Events 1 to n-2 | Last 2 events |
| Yearly | Leave-one-out | Events 1 to n-2 | Last 2 events |

### 11. Exception Handling
- Alert: Demand event > 3 × historical max; forecast > 2 × historical max for 3+ periods

### 12. Reclassification

| Condition | Target Segment | Holding Period |
|---|---|---|
| CV² drops below 0.49 for 8 periods | Intermittent | 8 periods |
| ADI drops below threshold for 8 periods | Erratic | 8 periods |
| Both CV² low and ADI low | Stable | 8 periods |

### 13. Review Cadence
- Per cycle automated; monthly lumpy demand review; quarterly full re-evaluation

---
