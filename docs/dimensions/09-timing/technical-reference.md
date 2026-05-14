# PART 0 — FORMULA & THRESHOLD REFERENCE

## Dimension 9 · Timing Pattern

---

---

## 0.1 Core Segmentation Metrics

### A. Cross-Correlation Function (CCF)
> Measures lead-lag relationship between demand and trigger signal

```
CCF(k) = Σ[(d_t − d̄)(trigger_{t−k} − trigger̄)] / [n × σ_d × σ_trigger]

Leading:    Max |CCF| at k < 0  (demand moves before trigger)
Lagging:    Max |CCF| at k > 0  (demand moves after trigger)
Coincident: Max |CCF| at k = 0  (demand moves with trigger)

Significant: |CCF(k)| > 2/√n
```

| Granularity | Lag Range Tested | Trigger Variables |
|---|---|---|
| **Daily** | k = −30 to +30 days | Competitor price, weather, mobility index, news sentiment |
| **Weekly** | k = −13 to +13 weeks | Category trend, promotional activity, macro index |
| **Monthly** | k = −6 to +6 months | GDP, industrial output, consumer confidence |
| **Quarterly** | k = −4 to +4 quarters | GDP growth, capital expenditure |
| **Yearly** | k = −2 to +2 years | Macro cycle, population growth |

---

### B. Timing Deviation
> Measures how far demand arrival deviates from expected timing

```
dev_timing = t_actual − t_expected  (periods)

Leading:     Mean(dev_timing) < −1 period
Lagging:     Mean(dev_timing) > +1 period
Coincident:  |Mean(dev_timing)| ≤ 1 period
Deferred:    Mean(dev_timing) > granularity threshold
Accelerated: Mean(dev_timing) < −granularity threshold
```

| Granularity | Deferred Threshold | Accelerated Threshold |
|---|---|---|
| **Daily** | dev > +7 days | dev < −7 days |
| **Weekly** | dev > +3 weeks | dev < −3 weeks |
| **Monthly** | dev > +2 months | dev < −2 months |
| **Quarterly** | dev > +1 quarter | dev < −1 quarter |
| **Yearly** | dev > +1 year | dev < −1 year |

---

## 0.2 Classification Decision Rules

```
STEP 1: Compute CCF across full lag range
STEP 2: Identify lag k* = argmax |CCF(k)|

  k* < 0 AND dev_timing < −1 period   → LEADING
  k* > 0 AND dev_timing > +1 period   → LAGGING
  k* = 0 AND |dev_timing| ≤ 1 period  → COINCIDENT
  dev_timing > granularity threshold   → DEFERRED
  dev_timing < −granularity threshold  → ACCELERATED

Significance check: |CCF(k*)| > 2/√n required for all classifications
```

---

## 0.3 Rolling Window Reference

| Window | Daily | Weekly | Monthly | Quarterly | Yearly |
|---|---|---|---|---|---|
| Short | 7 days | 4 weeks | 2 months | 1 quarter | 1 year |
| Medium | 30 days | 8 weeks | 3 months | 2 quarters | 2 years |
| Long | 90 days | 13 weeks | 6 months | 3 quarters | 3 years |
| Extended | 180 days | 26 weeks | 12 months | 4 quarters | 4 years |
| DL Lookback | 180 days | 52 weeks | 24 months | 8 quarters | 5 years |

---

## 0.4 Accuracy Metrics

```
WMAPE   = Σ|Forecast_t − Actual_t| / Σ Actual_t × 100
Bias    = Σ(Forecast_t − Actual_t) / Σ Actual_t × 100
MAE     = (1/n) × Σ|Forecast_t − Actual_t|
Pinball(α,t) = α × (Actual_t − Q_α)_+ + (1−α) × (Q_α − Actual_t)_+
Coverage = P(Actual ∈ [P10, P90])  Target: 80%

Timing-specific:
  Lead Indicator R²  = R² of trigger regression  (Target > 0.25)
  CCF Stability      = CV(k*) across rolling windows  (Target < 0.30)
  Lag Estimate Accuracy = |k*_estimated − k*_true|  (Target < 2 periods)
```

---

## 0.5 Retraining & Backtesting Reference

| Granularity | Retraining | Latency | Train | Test |
|---|---|---|---|---|
| **Daily** | Daily | T+4 hours | 180 days | 30 days |
| **Weekly** | Weekly | T+1 day | 52 weeks | 13 weeks |
| **Monthly** | Monthly | T+2 days | 24 months | 6 months |
| **Quarterly** | Quarterly | T+3 days | 8 quarters | 2 quarters |
| **Yearly** | Annually | T+7 days | All available | 1 year |

---
