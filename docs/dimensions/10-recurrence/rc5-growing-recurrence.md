# Segment Model Template

## Dimension 10 · Growing Recurrence

---

### 1. Definition
Predicts demand for SKUs where the frequency of demand events is increasing over time (Mann-Kendall on RR(t); p < 0.05; Z > 0), signalling growing customer adoption or expanding use cases that require recurrence-rate-adjusted upward forecasting.

### 2. Detailed Description
- **Applicable scenarios:** New product gaining customer traction, expanding B2B relationship, growing maintenance cycle needs, categories with increasing penetration, subscription adoption growing
- **Boundaries:**

| Granularity | Detection Condition | RR Window | Min History |
|---|---|---|---|
| Daily | MK p < 0.05; Z > 0 on RR(t); 180-day trend | 90-day rolling | ≥ 180 days with ≥ 5 events |
| Weekly | MK p < 0.05; Z > 0; 52-week trend | 26-week rolling | ≥ 52 weeks with ≥ 5 events |
| Monthly | MK p < 0.05; Z > 0; 24-month trend | 12-month rolling | ≥ 24 months with ≥ 5 events |
| Quarterly | MK p < 0.05; Z > 0; 8-quarter trend | 4-quarter rolling | ≥ 8 quarters with ≥ 4 events |
| Yearly | MK p < 0.05; Z > 0; 5-year trend | 3-year rolling | ≥ 5 years with ≥ 3 events |

- **Key demand characteristics:** Demand events becoming more frequent over time; RR is rising; approaching Regular recurrence pattern; under-forecast risk dominates
- **Differentiation from other models:** Unlike Growth Lifecycle (which captures volume slope), Growing Recurrence captures rising frequency; a SKU can have stable per-event quantity but growing recurrence rate

### 3. Business Impact
- **Primary risk (over-forecast):** Minimal — under-forecast dominates
- **Primary risk (under-forecast):** Systematic under-ordering as demand frequency rises — chronic stockout; missed growth opportunity
- **Strategic importance:** High — growing recurrence signals expanding customer adoption; under-serving creates competitor opportunity

### 4. Priority Level
🟠 **Tier 2** — Under-forecast prevention is primary; growing recurrence is a commercial opportunity signal.

### 5. Model Strategy Overview

#### 5.1 Growing Recurrence Rate Model
```
RR(t) = demand events in rolling window / window length
RR_forecast(t+h) = min(RR_max, RR(t) + β_RR × h)
where β_RR > 0 (growing rate slope)
      RR_max = 1.0 (demand every period — cannot exceed)

Forecast: F(t+h) = RR_forecast(t+h) × μ_quantity_per_event
```

#### 5.2 Analogue / Similarity Logic
- k = 3 (SKUs that previously showed similar growing recurrence — now Regular or Stable)
- Similarity: β_RR ±0.01, initial RR ±0.10, category

#### 5.3 Feature Engineering

| Granularity | RR Trend Features | Quantity Features | Context Features |
|---|---|---|---|
| Daily | RR(t), β_RR, periods of growing RR, RR vs 6-month-ago, distance to RR_max | Non-zero mean (90-day), quantity trend | Category growth index, customer acquisition rate |
| Weekly | RR(t), β_RR, weeks of growing RR, distance to RR_max | Non-zero mean (26-week) | Category index |
| Monthly | RR(t), β_RR, months of growing RR | Non-zero mean (12-month) | Market penetration index |
| Quarterly | RR(t), β_RR, distance to RR_max | Non-zero mean (4-quarter) | Category index |
| Yearly | RR(t), β_RR | Non-zero mean (3-year) | Macro index |

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM with RR growth trend features
- Configuration: Objective = reg:squarederror; Metric = WMAPE on occurrence-adjusted forecast
- Key features: RR(t), β_RR, distance to RR_max, non-zero mean, category growth index
- When to use: Primary model when ≥ 8 demand events in history

#### 6.2 Deep Learning (DL)
- Architectures: Not recommended during early growing phase — data too sparse
- When to use: Only after RR has stabilised near 0.50 (demand in ~half of periods)

#### 6.3 Statistical / Time Series Models
- Architectures: ETS(A,A,N) on RR(t) series with growth cap

**Growing RR Forecast:**
```
ETS on RR series:
  l_t = α × RR(t) + (1−α) × (l_{t-1} + b_{t-1})
  b_t = β × (l_t − l_{t-1}) + (1−β) × b_{t-1}
  RR_forecast(t+h) = min(1.0, l_t + h × b_t)  [cap at 1.0]
  D_forecast(t+h) = RR_forecast(t+h) × μ_quantity
α = 0.20; β = 0.10
```

| Granularity | α | β |
|---|---|---|
| Daily | 0.20 | 0.10 |
| Weekly | 0.20 | 0.10 |
| Monthly | 0.18 | 0.08 |
| Quarterly | 0.15 | 0.08 |
| Yearly | 0.12 | 0.06 |

#### 6.4 Baseline / Fallback Model
- Fallback: Current RR × non-zero mean (no growth extrapolation — conservative)
- Alert if under-forecast bias < −10%

### 7. Ensemble & Weighting

#### 7.2 Dynamic Weight Schedule

| Growth Stage | LightGBM | ETS on RR | Baseline RR |
|---|---|---|---|
| Mild growth (β_RR < 0.01) | 50% | 40% | 10% |
| Moderate growth (0.01 ≤ β_RR < 0.03) | 40% | 50% | 10% |
| Strong growth (β_RR ≥ 0.03) | 30% | 60% | 10% |

### 8. Uncertainty Quantification
- Method: Confidence interval on β_RR + quantile regression on quantity
- Output: [P10, P50, P90] — P90 used for safety stock; P50 for base
- Use case: Safety stock at P75; replenishment trigger at P50

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Growth rate cap: RR_forecast ≤ min(1.0, current_RR × 2) — prevent extreme extrapolation
- Anti-under-forecast: If under-forecast bias < −10% for 3 periods → apply additional β_RR × 0.5 correction
- Manual overrides: Commercial team adoption rate input; customer onboarding plan; distribution expansion plan

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | WMAPE | RR Forecast Accuracy | Under-Forecast Alert | Bias Alert |
|---|---|---|---|---|
| Daily | < 30% | RR within ±20% | Bias < −12% | Bias < −12% |
| Weekly | < 25% | RR within ±18% | Bias < −10% | Bias < −10% |
| Monthly | < 22% | RR within ±15% | Bias < −8% | Bias < −8% |
| Quarterly | < 18% | RR within ±12% | Bias < −6% | Bias < −6% |
| Yearly | < 15% | RR within ±10% | Bias < −5% | Bias < −5% |

#### 10.2 Backtesting Protocol

| Granularity | Train | Test |
|---|---|---|
| Daily | 180 days | 30 days |
| Weekly | 52 weeks | 13 weeks |
| Monthly | 24 months | 6 months |
| Quarterly | 8 quarters | 2 quarters |
| Yearly | All available | 1 year |

#### 10.3 Retraining

| Granularity | Cadence | Latency |
|---|---|---|
| Daily | Weekly | T+4 hours |
| Weekly | Weekly | T+1 day |
| Monthly | Monthly | T+2 days |
| Quarterly | Quarterly | T+3 days |
| Yearly | Annually | T+7 days |

### 11. Exception Handling & Overrides
- Auto-detect: RR plateaus (MK p ≥ 0.10 for 4 periods) → reclassify to Regular or Irregular; RR trend reverses negative → reclassify to Declining Recurrence
- Manual override: Sales team adoption rate revision; commercial plan update
- Override expiration: Per quarter review

### 12. Reclassification / Model Selection

| Condition | Target | Holding Period | Transition |
|---|---|---|---|
| RR stabilises (MK p ≥ 0.10) for 4 periods | Regular (if CV_IAT < 0.20) or Irregular | 4 periods | Soft blend |
| RR trend reverses (MK p < 0.05; Z < 0) | Declining Recurrence | 4 periods | Soft blend |
| RR approaches 1.0 (demand every period) | Lifecycle: Mature + Behavior: Stable | Graduation | Hard switch |

### 13. Review Cadence
- Monthly RR trend monitor with growth rate tracker; quarterly adoption rate review; annual full re-evaluation

---

*End of Dimension 10 · Recurrence Pattern*
*5 Segments Complete · RC1 through RC5*

---
