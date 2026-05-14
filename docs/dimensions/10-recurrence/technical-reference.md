# PART 0 — FORMULA & THRESHOLD REFERENCE

## Dimension 10 · Recurrence Pattern

---

---

## 0.1 Core Segmentation Metrics

### A. Inter-Arrival Time (IAT) Statistics
> Measures intervals between consecutive demand events

```
IAT_i = t_i − t_{i-1}   (periods between consecutive non-zero demand events)

Mean IAT:  μ_IAT = (1/n) × Σ IAT_i
Std IAT:   σ_IAT = sqrt[(1/(n-1)) × Σ(IAT_i − μ_IAT)²]
CV_IAT:    CV_IAT = σ_IAT / μ_IAT

Regular:   CV_IAT < 0.20  (highly consistent intervals)
Irregular: 0.20 ≤ CV_IAT < 0.60  (variable but recurring)
One Time:  n = 1  (single demand event)
```

| Granularity | Regular Threshold | Irregular Range | Min Events for IAT |
|---|---|---|---|
| **Daily** | CV_IAT < 0.20 | 0.20–0.60 | ≥ 5 events |
| **Weekly** | CV_IAT < 0.20 | 0.20–0.60 | ≥ 5 events |
| **Monthly** | CV_IAT < 0.20 | 0.20–0.60 | ≥ 5 events |
| **Quarterly** | CV_IAT < 0.20 | 0.20–0.60 | ≥ 4 events |
| **Yearly** | CV_IAT < 0.20 | 0.20–0.60 | ≥ 3 events |

---

### B. Recurrence Rate Trend
> Measures whether demand frequency is increasing or decreasing over time

```
Recurrence Rate: RR(t) = demand events in rolling window / window length
Trend in RR:     Mann-Kendall test on RR(t) series

Declining Recurrence: Mann-Kendall p < 0.05; Z < 0
Growing Recurrence:   Mann-Kendall p < 0.05; Z > 0
Stable Recurrence:    Mann-Kendall p ≥ 0.10
```

| Granularity | Rolling Window for RR | Trend Window |
|---|---|---|
| **Daily** | 90-day | 180-day MK test |
| **Weekly** | 26-week | 52-week MK test |
| **Monthly** | 12-month | 24-month MK test |
| **Quarterly** | 4-quarter | 8-quarter MK test |
| **Yearly** | 3-year | 5-year MK test |

---

### C. Recurrence Probability
> Probability that demand will occur in the next period

```
P(recurrence in period t) = f(periods since last demand, season, external signals)

Estimated via Logistic Regression:
  logit[P(recurrence)] = α + β_1 × periods_since_last + β_2 × seasonal_index + β_3 × X(t)

Or via Survival model (hazard rate):
  h(t|s) = h_0(t) × exp(β × covariates(s))
  where s = periods since last demand event
  h_0(t) = baseline hazard empirically estimated from IAT distribution
```

---

## 0.2 Classification Decision Rules

```
STEP 1: Count demand events n in available history
  n = 0 → No demand history — use Lifecycle Cold Start
  n = 1 → ONE TIME (single event)
  n ≥ 2 → proceed to STEP 2

STEP 2: Compute CV_IAT from observed inter-arrival times
  CV_IAT < 0.20  → proceed to STEP 3 (Regular candidate)
  CV_IAT ≥ 0.60  → IRREGULAR (high variability)
  0.20 ≤ CV_IAT < 0.60 → IRREGULAR (moderate variability)

STEP 3: Compute RR(t) trend via Mann-Kendall
  p < 0.05; Z < 0 → DECLINING RECURRENCE
  p < 0.05; Z > 0 → GROWING RECURRENCE
  p ≥ 0.10        → REGULAR (stable, consistent intervals)
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
MAE     = (1/n) × Σ|Forecast_t − Actual_t|
MASE    = MAE_model / MAE_naive
Bias    = Σ(Forecast_t − Actual_t) / Σ Actual_t × 100

Recurrence-specific:
  Timing Accuracy   = % demand events predicted within ±1 period  (Regular: > 90%)
  Recurrence AUC    = AUC of P(recurrence) classifier  (Target > 0.70)
  False Positive Rate = Non-recurrence periods forecast > 0 / Total zero periods  (Target < 10%)
  RR Forecast Accuracy = |RR_predicted − RR_actual| / RR_actual × 100  (Target < 20%)
```

---

## 0.5 Retraining & Backtesting Reference

| Granularity | Retraining | Latency | Train | Test |
|---|---|---|---|---|
| **Daily** | Weekly | T+4 hours | 180 days | 30 days |
| **Weekly** | Weekly | T+1 day | 52 weeks | 13 weeks |
| **Monthly** | Monthly | T+2 days | 24 months | 6 months |
| **Quarterly** | Quarterly | T+3 days | 8 quarters | 2 quarters |
| **Yearly** | Annually | T+7 days | All available | 1 year |

---
