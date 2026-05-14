# Segment Model Template

## Dimension 10 · Declining Recurrence

---

### 1. Definition
Predicts demand for SKUs where the frequency of demand events is decreasing over time (Mann-Kendall on RR(t); p < 0.05; Z < 0), signalling a category or customer relationship in structural decline that requires recurrence-rate-adjusted forecasting.

### 2. Detailed Description
- **Applicable scenarios:** Ageing customer relationships, gradually obsoleting product lines, categories losing relevance, B2B accounts reducing order frequency, technology-displaced categories
- **Boundaries:**

| Granularity | Detection Condition | RR Window | Min History |
|---|---|---|---|
| Daily | MK p < 0.05; Z < 0 on RR(t); 180-day trend | 90-day rolling | ≥ 180 days with ≥ 5 events |
| Weekly | MK p < 0.05; Z < 0; 52-week trend | 26-week rolling | ≥ 52 weeks with ≥ 5 events |
| Monthly | MK p < 0.05; Z < 0; 24-month trend | 12-month rolling | ≥ 24 months with ≥ 5 events |
| Quarterly | MK p < 0.05; Z < 0; 8-quarter trend | 4-quarter rolling | ≥ 8 quarters with ≥ 4 events |
| Yearly | MK p < 0.05; Z < 0; 5-year trend | 3-year rolling | ≥ 5 years with ≥ 3 events |

- **Key demand characteristics:** Demand events becoming less frequent over time; RR is falling; quantity per event may remain stable even as frequency declines; approaching One Time or Inactive
- **Differentiation from other models:** Unlike Decline Lifecycle (which captures volume slope), Declining Recurrence captures falling frequency; a SKU can have stable per-event quantity but declining recurrence rate

### 3. Business Impact
- **Primary risk (over-forecast):** Applying historical occurrence rate to future periods — excess inventory as frequency drops
- **Primary risk (under-forecast):** Minimal — over-forecast dominates for declining recurrence
- **Strategic importance:** Medium — early signal of customer churn or product obsolescence; triggers range review

### 4. Priority Level
🟠 **Tier 2** — Over-forecast prevention is primary; declining recurrence signals commercial risk.

### 5. Model Strategy Overview

#### 5.1 Recurrence Rate Trend Model
```
RR(t) = demand events in rolling window / window length
RR_forecast(t+h) = RR(t) + β_RR × h
where β_RR < 0 (declining rate slope from MK test)

Floor: RR_min = 0 (cannot go below zero frequency)
Forecast: F(t+h) = RR_forecast(t+h) × μ_quantity_per_event
```

#### 5.2 Analogue / Similarity Logic
- k = 3 (SKUs that previously showed similar declining recurrence — now Inactive or One Time)
- Similarity: β_RR ±0.01, initial RR ±0.10, category

#### 5.3 Feature Engineering

| Granularity | RR Trend Features | Quantity Features | Context Features |
|---|---|---|---|
| Daily | RR(t), β_RR, periods of declining RR, RR vs 6-month-ago | Non-zero mean (90-day), quantity trend | Category RR trend, customer churn score |
| Weekly | RR(t), β_RR, weeks of declining RR | Non-zero mean (26-week) | Category index |
| Monthly | RR(t), β_RR, months of declining RR | Non-zero mean (12-month) | Market share index |
| Quarterly | RR(t), β_RR | Non-zero mean (4-quarter) | Category index |
| Yearly | RR(t), β_RR | Non-zero mean (3-year) | Macro index |

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM with RR trend features
- Configuration: Objective = reg:squarederror; Metric = WMAPE on occurrence-adjusted forecast
- Key features: RR(t), β_RR, periods of declining RR, non-zero mean, category RR trend
- When to use: Primary model when ≥ 8 demand events in history

#### 6.2 Deep Learning (DL)
- Architectures: Not recommended — declining recurrence reduces data density; DL overfits
- When to use: Not applicable

#### 6.3 Statistical / Time Series Models
- Architectures: ETS(A,A,N) on RR(t) series — additive trend (negative) for recurrence rate

**Declining RR Forecast:**
```
ETS on RR series:
  l_t = α × RR(t) + (1−α) × (l_{t-1} + b_{t-1})
  b_t = β × (l_t − l_{t-1}) + (1−β) × b_{t-1}
  RR_forecast(t+h) = max(0, l_t + h × b_t)  [floor at 0]
  D_forecast(t+h) = RR_forecast(t+h) × μ_quantity
α = 0.20; β = 0.10 (moderate adaptation; captures declining trend)
```

| Granularity | α | β |
|---|---|---|
| Daily | 0.20 | 0.10 |
| Weekly | 0.20 | 0.10 |
| Monthly | 0.18 | 0.08 |
| Quarterly | 0.15 | 0.08 |
| Yearly | 0.12 | 0.06 |

#### 6.4 Baseline / Fallback Model
- Fallback: Current RR × non-zero mean (no trend extrapolation — conservative)
- Alert if over-forecast bias > 10%

### 7. Ensemble & Weighting

#### 7.2 Dynamic Weight Schedule

| Decline Stage | LightGBM | ETS on RR | Baseline RR |
|---|---|---|---|
| Mild decline (β_RR > −0.01) | 50% | 40% | 10% |
| Moderate decline (−0.03 < β_RR ≤ −0.01) | 40% | 50% | 10% |
| Steep decline (β_RR ≤ −0.03) | 25% | 65% | 10% |

### 8. Uncertainty Quantification
- Method: Confidence interval on β_RR estimate + quantile regression on quantity
- Output: [P10, P50, P90] — P10 for minimum expected demand; P50 for base
- Use case: P10 for conservative inventory; P50 for base replenishment

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Ceiling: min(forecast, prior period rolling mean) — prevent upward drift
- Anti-accumulation: If over-forecast bias > 10% for 3 periods → apply additional β_RR × 0.5 correction
- Manual overrides: Account manager customer churn flag; commercial decision to defend vs exit
- Range review trigger: If projected RR drops below 0.10 within 6 months → flag for range rationalisation

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | WMAPE | RR Forecast Accuracy | Over-Forecast Alert | Bias Alert |
|---|---|---|---|---|
| Daily | < 30% | RR within ±20% | Bias > +12% | Bias > +12% |
| Weekly | < 25% | RR within ±18% | Bias > +10% | Bias > +10% |
| Monthly | < 22% | RR within ±15% | Bias > +8% | Bias > +8% |
| Quarterly | < 18% | RR within ±12% | Bias > +6% | Bias > +6% |
| Yearly | < 15% | RR within ±10% | Bias > +5% | Bias > +5% |

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
- Auto-detect: RR drops to zero for 3 periods → reclassify to One Time or Inactive; RR trend reverses (Z > 0 for 4 periods) → reclassify to Regular or Growing Recurrence
- Manual override: Commercial decision to defend customer / product; account manager intervention
- Override expiration: Per quarter review

### 12. Reclassification / Model Selection

| Condition | Target | Holding Period | Transition |
|---|---|---|---|
| RR stabilises (MK p ≥ 0.10) for 4 periods | Regular or Irregular | 4 periods | Soft blend |
| RR trend reverses (MK p < 0.05; Z > 0) | Growing Recurrence | 4 periods | Soft blend |
| RR drops to 0 events in last 13 weeks | Lifecycle: Inactive | Immediate | Hard switch |
| Only 1 event in last 2 years | One Time | Immediate | Hard switch |

### 13. Review Cadence
- Monthly RR trend monitor; quarterly range rationalisation input; annual full re-evaluation

---

---
