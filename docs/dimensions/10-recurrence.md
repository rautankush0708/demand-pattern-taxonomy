# Dimension 10 · Recurrence Pattern
## Demand Forecasting Model Templates

---

> **Segments:** 5 · Regular · Irregular · One Time · Declining Recurrence · Growing Recurrence
> **Granularities:** Daily · Weekly · Monthly · Quarterly · Yearly

---

## 0.2 Recurrence Pattern Metrics

### A. Inter-Arrival Time Statistics
```
Inter-arrival time: IAT_i = t_i − t_{i-1} (periods between consecutive demand events)
Mean IAT: μ_IAT = (1/n) × Σ IAT_i
Std IAT:  σ_IAT = sqrt[(1/(n-1)) × Σ(IAT_i − μ_IAT)²]
CV_IAT:   CV_IAT = σ_IAT / μ_IAT

Regular:   CV_IAT < 0.20 (highly consistent intervals)
Irregular: 0.20 ≤ CV_IAT < 0.60 (variable but recurring)
One Time:  n = 1 (single demand event observed)
```

### B. Recurrence Rate Trend
```
Recurrence rate at time t: RR(t) = demand events in rolling window / window length
Trend in RR: Mann-Kendall test on RR(t) series

Declining Recurrence: Mann-Kendall p < 0.05; Z < 0 (demand frequency decreasing)
Growing Recurrence:   Mann-Kendall p < 0.05; Z > 0 (demand frequency increasing)
```

| Granularity | Rolling Window for RR | Trend Window |
|---|---|---|
| **Daily** | 90-day | 180-day MK test |
| **Weekly** | 26-week | 52-week MK test |
| **Monthly** | 12-month | 24-month MK test |
| **Quarterly** | 4-quarter | 8-quarter MK test |
| **Yearly** | 3-year | 5-year MK test |

---

# PART 1 — SEGMENT TEMPLATES

## RC1 · Regular

### 1. Definition
Predicts demand for SKUs with highly consistent inter-arrival intervals (CV_IAT < 0.20), where timing predictability enables interval-based forecasting models.

### 2. Detailed Description
- **Applicable scenarios:** B2B scheduled replenishment, subscription-like ordering, fixed maintenance cycles, contracted delivery schedules

### 5. Model Strategy

#### 5.1 Interval-Based Forecasting
```
Next demand period = t_last + μ_IAT   (deterministic prediction)
Confidence window: t_next ± 1σ_IAT   (narrow for regular)
Quantity forecast: Historical non-zero mean with ETS smoothing
```

| Granularity | Mean IAT | IAT Features |
|---|---|---|
| Daily | 7/30/90-day mean IAT | Days since last demand, expected next demand date, CV_IAT |
| Weekly | Mean IAT in weeks | Weeks since last demand, next expected week |
| Monthly | Mean IAT in months | Months since last demand, next expected month |
| Quarterly | Mean IAT in quarters | Quarters since last demand |
| Yearly | Mean IAT in years | Years since last demand |

### 6. Model Families

#### 6.1 ML: LightGBM with IAT features — Pulsed behaviour model (B7 template extended)
#### 6.2 Statistical: Croston (very low α = 0.05 — exploit high regularity)
```
Croston with α = 0.05:
  z_t = 0.05 × d_t + 0.95 × z_{t-1}   [very stable quantity estimate]
  p_t = 0.05 × q_t + 0.95 × p_{t-1}   [very stable interval estimate]
  F_t = z_t / p_t
```

### Evaluation

| Granularity | Timing Accuracy (±1 period) | Quantity MAE | Bias Alert |
|---|---|---|---|
| Daily | > 95% | < 10% of mean | |Bias| > 8% |
| Weekly | > 90% | < 10% of mean | |Bias| > 8% |
| Monthly | > 90% | < 8% | |Bias| > 6% |
| Quarterly | > 85% | < 8% | |Bias| > 6% |
| Yearly | > 85% | < 6% | |Bias| > 5% |

---

## RC2 · Irregular

### 1. Definition
Predicts demand for SKUs that recur but with inconsistent timing (0.20 ≤ CV_IAT < 0.60), requiring probabilistic timing models rather than deterministic interval forecasting.

### 2. Detailed Description
- **Applicable scenarios:** Project-based demand, opportunistic purchasing, variable-cycle MRO, demand driven by unpredictable triggers

### 5. Model Strategy

#### 5.1 Probabilistic Timing Model
```
P(demand in period t) = f(periods since last demand, season, trigger signals)
Estimate via Logistic Regression or Survival model:
  Hazard function: h(t|s) = h_0(t) × e^{β × covariates(s)}
  where s = periods since last demand event
  h_0(t) = baseline hazard (empirically estimated from IAT distribution)
```

### 6. Model Families

#### 6.1 ML: XGBoost (timing classifier) + rolling non-zero mean (quantity)
#### 6.2 Statistical: Croston/SBA (α = 0.10–0.20)
#### 6.3 Survival model: Cox proportional hazard for timing; OLS for quantity

### Evaluation

| Granularity | Timing AUC | Quantity MAE | Bias Alert |
|---|---|---|---|
| Daily | > 0.70 | < 20% of mean | |Bias| > 12% |
| Weekly | > 0.70 | < 18% | |Bias| > 10% |
| Monthly | > 0.68 | < 15% | |Bias| > 8% |
| Quarterly | > 0.65 | < 12% | |Bias| > 6% |
| Yearly | > 0.65 | < 10% | |Bias| > 5% |

---

## RC3 · One Time

### 1. Definition
Predicts demand for SKUs with a single observed demand event and no recurrence expectation, where the primary decision is whether future demand will occur at all.

### 2. Detailed Description
- **Applicable scenarios:** Project-specific custom items, one-off procurement, trial orders, unique event-specific demand

### 5. Model Strategy

#### 5.1 Recurrence Probability Model
```
P(recurrence) = Logistic Regression on:
  - Category recurrence base rate
  - Customer tenure and order history
  - Time since first order
  - Product type (standard vs custom)
  - Market context signals

If P(recurrence) > 0.50 → Maintain in Cold Start lifecycle; monitor for second demand
If P(recurrence) < 0.20 → Flag for potential Inactive lifecycle
```

### 6. Model Families
- Not applicable for quantity forecast — single event only
- Recurrence classifier: Logistic Regression (simple; prevent overfit)
- Quantity estimate: First order quantity (only data point available)

### Evaluation
- Primary KPI: Recurrence detection within 2 periods of second demand event
- Secondary KPI: False positive rate (flagging non-recurring as recurring)

---

## RC4 · Declining Recurrence

### 1. Definition
Predicts demand for SKUs where the frequency of demand events is decreasing over time (Mann-Kendall on RR(t); p < 0.05; Z < 0), indicating a category or customer relationship in decline.

### 5. Model Strategy

#### 5.1 Recurrence Rate Trend Model
```
RR(t) = demand events in rolling window / window length
Forecast recurrence rate: RR_forecast(t+h) = RR(t) × (1 + β_RR × h)
where β_RR < 0 (declining rate slope)
Quantity per event: Historical non-zero mean (stable)
Demand forecast: RR_forecast(t+h) × quantity_per_event
```

### 6. Model Families

#### 6.1 ML: LightGBM with RR trend features + time index
#### 6.2 Statistical: ETS on RR(t) series with additive negative trend

### Evaluation

| Granularity | RR Forecast Accuracy | WMAPE | Over-Forecast Alert |
|---|---|---|---|
| Daily | RR within ±20% | < 30% | Bias > +12% |
| Weekly | RR within ±18% | < 25% | Bias > +10% |
| Monthly | RR within ±15% | < 22% | Bias > +8% |
| Quarterly | RR within ±12% | < 18% | Bias > +6% |
| Yearly | RR within ±10% | < 15% | Bias > +5% |

---

## RC5 · Growing Recurrence

### 1. Definition
Predicts demand for SKUs where the frequency of demand events is increasing over time (Mann-Kendall on RR(t); p < 0.05; Z > 0), indicating growing customer adoption or expanding use cases.

### 5. Model Strategy

#### 5.1 Growing Recurrence Rate Model
```
RR_forecast(t+h) = RR(t) × (1 + β_RR × h)
where β_RR > 0 (growing rate slope)
Cap: RR_max = 1.0 (demand every period — cannot exceed)
```

### 6. Model Families

#### 6.1 ML: LightGBM with RR trend features
#### 6.2 Statistical: ETS(A,A,N) on RR(t) with growth cap

### Evaluation

| Granularity | RR Forecast Accuracy | WMAPE | Under-Forecast Alert |
|---|---|---|---|
| Daily | RR within ±20% | < 30% | Bias < −12% |
| Weekly | RR within ±18% | < 25% | Bias < −10% |
| Monthly | RR within ±15% | < 22% | Bias < −8% |
| Quarterly | RR within ±12% | < 18% | Bias < −6% |
| Yearly | RR within ±10% | < 15% | Bias < −5% |
