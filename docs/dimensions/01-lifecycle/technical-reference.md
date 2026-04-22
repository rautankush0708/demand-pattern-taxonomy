# PART 0 — FORMULA & THRESHOLD REFERENCE
## Lifecycle Pattern Specific

---

## 0.1 Core Segmentation Metrics

### A. Demand Slope — Trend Detection
> Measures directional movement of demand over time

**General Formula:**
```
slope β = Σ[(t - t̄)(d_t - d̄)] / Σ[(t - t̄)²]
Assessed via Mann-Kendall test
Significant trend: p < 0.05
No trend:          p ≥ 0.10
Watch zone:        0.05 ≤ p < 0.10 → monitor 2 more periods
```

| Granularity | Rolling Window | Slope Unit | Significance |
|---|---|---|---|
| **Daily** | 90-day | Units/day | Mann-Kendall p < 0.05 |
| **Weekly** | 13-week | Units/week | Mann-Kendall p < 0.05 |
| **Monthly** | 6-month | Units/month | Mann-Kendall p < 0.05 |
| **Quarterly** | 4-quarter | Units/quarter | Mann-Kendall p < 0.05 |
| **Yearly** | 3-year | Units/year | Mann-Kendall p < 0.05 |

---

### B. % Zero Periods
> Proportion of periods with no demand — used to confirm Inactive status

**General Formula:**
```
%Zero = (Number of Zero Demand Periods / Total Periods in Window) × 100
```

| Granularity | Inactive Trigger | Formula |
|---|---|---|
| **Daily** | 0 demand ≥ 91 consecutive days | Count(demand = 0, consecutive) ≥ 91 |
| **Weekly** | 0 demand ≥ 13 consecutive weeks | Count(demand = 0, consecutive) ≥ 13 |
| **Monthly** | 0 demand ≥ 3 consecutive months | Count(demand = 0, consecutive) ≥ 3 |
| **Quarterly** | 0 demand ≥ 1 consecutive quarter | Count(demand = 0, consecutive) ≥ 1 |
| **Yearly** | 0 demand ≥ 1 consecutive year | Count(demand = 0, consecutive) ≥ 1 |

---

### C. Structural Break Detection
> Detects permanent level shifts — used before Lifecycle classification

| Granularity | Test | Window | Trigger |
|---|---|---|---|
| **Daily** | CUSUM | 30-day | CUSUM statistic > 5σ |
| **Weekly** | Chow Test + CUSUM | 8-week | p < 0.05 |
| **Monthly** | Chow Test | 4-month | p < 0.05 |
| **Quarterly** | Chow Test | 2-quarter | p < 0.05 |
| **Yearly** | Chow Test | 2-year | p < 0.05 |

---

## 0.2 Lifecycle Classification Thresholds

| Lifecycle Stage | Daily | Weekly | Monthly | Quarterly | Yearly |
|---|---|---|---|---|---|
| **Cold Start** | History < 56 days | History < 8 weeks | History < 2 months | History < 1 quarter | History < 1 year |
| **New Launch** | 56–112 days | 8–16 weeks | 2–4 months | 1–2 quarters | 1–2 years |
| **Growth** | Slope p < 0.05 (+), 90-day window | Slope p < 0.05 (+), 13-week window | Slope p < 0.05 (+), 6-month window | Slope p < 0.05 (+), 4-quarter window | Slope p < 0.05 (+), 3-year window |
| **Mature** | Slope p ≥ 0.10, 90-day window | Slope p ≥ 0.10, 13-week window | Slope p ≥ 0.10, 6-month window | Slope p ≥ 0.10, 4-quarter window | Slope p ≥ 0.10, 3-year window |
| **Decline** | Slope p < 0.05 (−), 90-day window | Slope p < 0.05 (−), 13-week window | Slope p < 0.05 (−), 6-month window | Slope p < 0.05 (−), 4-quarter window | Slope p < 0.05 (−), 3-year window |
| **Phasing Out** | Discontinuation flag set | Same | Same | Same | Same |
| **Inactive** | 0 demand ≥ 91 consecutive days | 0 demand ≥ 13 consecutive weeks | 0 demand ≥ 3 consecutive months | 0 demand ≥ 1 consecutive quarter | 0 demand ≥ 1 consecutive year |

---

## 0.3 Minimum History Requirements

| Requirement | Daily | Weekly | Monthly | Quarterly | Yearly |
|---|---|---|---|---|---|
| **Min for Trend Test** | ≥ 90 days | ≥ 13 weeks | ≥ 6 months | ≥ 4 quarters | ≥ 3 years |
| **Min for Seasonality** | ≥ 365 days (2 cycles) | ≥ 104 weeks (2 cycles) | ≥ 24 months (2 cycles) | ≥ 8 quarters (2 cycles) | ≥ 3 years |
| **Min for Growth/Decline** | ≥ 112 days | ≥ 16 weeks | ≥ 4 months | ≥ 2 quarters | ≥ 2 years |

---

## 0.4 Rolling Window Reference

| Window Name | Daily | Weekly | Monthly | Quarterly | Yearly |
|---|---|---|---|---|---|
| **Short** | 7 days | 4 weeks | 2 months | 1 quarter | 1 year |
| **Medium** | 30 days | 8 weeks | 3 months | 2 quarters | 2 years |
| **Long** | 90 days | 13 weeks | 6 months | 3 quarters | 3 years |
| **Extended** | 180 days | 26 weeks | 12 months | 4 quarters | 4 years |
| **Full Year** | 365 days | 52 weeks | 12 months | 4 quarters | 5 years |
| **DL Lookback** | 90 days | 52 weeks | 24 months | 8 quarters | 5 years |

**Rolling Statistic Formulas:**
```
Rolling Mean (window w):   μ_w(t) = (1/w) × Σ d_{t-i}   for i = 0 to w-1
Rolling Std  (window w):   σ_w(t) = sqrt[(1/w) × Σ (d_{t-i} − μ_w)²]
Rolling Slope (window w):  β_w(t) = Σ[(i − ī)(d_{t-i} − d̄)] / Σ[(i − ī)²]
Decay Weight:              w_i    = exp(−i / half_life) / Σ exp(−j / half_life)
```

---

## 0.5 Accuracy Metric Formulas

```
WMAPE  = Σ|Forecast_t − Actual_t| / Σ Actual_t × 100

Bias   = Σ(Forecast_t − Actual_t) / Σ Actual_t × 100

MAE    = (1/n) × Σ|Forecast_t − Actual_t|

MASE   = MAE_model / MAE_naive
         MAE_naive = (1/(n−m)) × Σ|Actual_t − Actual_{t−m}|
         m = seasonal period

Pinball(α,t) = α × (Actual_t − Q_α)     if Actual_t ≥ Q_α
             = (1−α) × (Q_α − Actual_t)  if Actual_t < Q_α

Coverage = (Actuals within [P10,P90]) / Total Periods × 100
           Target: 80% coverage
```

---

## 0.6 Lifecycle Classification Decision Tree

```
INPUT: SKU demand history at chosen granularity
  │
  ├── Zero demand ≥ Inactive threshold?       ──► L7: INACTIVE
  │
  ├── History < Cold Start upper bound?       ──► L1: COLD START
  │
  ├── History within New Launch range?        ──► L2: NEW LAUNCH
  │
  ├── Discontinuation flag set in system?     ──► L6: PHASING OUT
  │
  ├── Run Mann-Kendall on rolling window
  │     ├── Positive slope p < 0.05?          ──► L3: GROWTH
  │     ├── Negative slope p < 0.05?          ──► L5: DECLINE
  │     └── Slope p ≥ 0.10?                  ──► L4: MATURE
  │
  └── Watch zone (0.05 ≤ p < 0.10)           ──► Hold current; re-test next 2 periods
```

---

# PART 1 — SEGMENT TEMPLATES

---

---

# PART 1 — SEGMENT TEMPLATES

