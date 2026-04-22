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

