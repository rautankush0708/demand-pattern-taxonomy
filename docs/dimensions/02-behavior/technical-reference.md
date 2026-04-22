# PART 0 — FORMULA & THRESHOLD REFERENCE
## Behavior Pattern Specific

---

## 0.1 Core Segmentation Metrics

### A. ADI — Average Demand Interval
> Measures demand **frequency** — how often demand occurs

**General Formula:**
```
ADI = Total Periods in Window / Number of Non-Zero Demand Periods
```

| Granularity | Formula | ADI Threshold | Interpretation |
|---|---|---|---|
| **Daily** | Total Days / Days with Demand > 0 | 1.10 | ADI < 1.10 = Regular; ≥ 1.10 = Intermittent |
| **Weekly** | Total Weeks / Weeks with Demand > 0 | 1.32 | ADI < 1.32 = Regular; ≥ 1.32 = Intermittent |
| **Monthly** | Total Months / Months with Demand > 0 | 1.25 | ADI < 1.25 = Regular; ≥ 1.25 = Intermittent |
| **Quarterly** | Total Quarters / Quarters with Demand > 0 | 1.20 | ADI < 1.20 = Regular; ≥ 1.20 = Intermittent |
| **Yearly** | Total Years / Years with Demand > 0 | 1.10 | ADI < 1.10 = Regular; ≥ 1.10 = Intermittent |

**Computation Rules:**
- Use rolling window (see Section 0.4)
- A period is **active** if demand > 0 in that period
- Exclude structural zeros (supply stockouts, system downtime) from denominator
- ADI = 1.0 → demand every period; ADI = 4.0 → demand every 4th period

---

### B. CV² — Squared Coefficient of Variation
> Measures demand **quantity variability** across active periods

**General Formula:**
```
CV² = (σ_nz / μ_nz)²
where σ_nz = std dev of non-zero demand periods
      μ_nz = mean of non-zero demand periods
CV² Threshold = 0.49 at all granularities
```

| Granularity | Formula | Example | Classification |
|---|---|---|---|
| **Daily** | (σ non-zero daily / μ non-zero daily)² | μ=10, σ=7 → CV²=0.49 | < 0.49 = Smooth; ≥ 0.49 = Variable |
| **Weekly** | (σ non-zero weekly / μ non-zero weekly)² | μ=100, σ=60 → CV²=0.36 | < 0.49 = Smooth; ≥ 0.49 = Variable |
| **Monthly** | (σ non-zero monthly / μ non-zero monthly)² | μ=400, σ=280 → CV²=0.49 | < 0.49 = Smooth; ≥ 0.49 = Variable |
| **Quarterly** | (σ non-zero quarterly / μ non-zero quarterly)² | μ=1200, σ=900 → CV²=0.5625 | < 0.49 = Smooth; ≥ 0.49 = Variable |
| **Yearly** | (σ non-zero yearly / μ non-zero yearly)² | μ=5000, σ=4000 → CV²=0.64 | < 0.49 = Smooth; ≥ 0.49 = Variable |

**Computation Rules:**
- Always compute on **non-zero periods only**
- Minimum non-zero observations required (see Section 0.3)
- If insufficient non-zero obs → flag; use category-level CV² as proxy

---

### C. % Zero Periods
> Proportion of periods with zero demand — used for Sparse sub-classification

**General Formula:**
```
%Zero = (Zero Demand Periods / Total Periods in Window) × 100
```

| Granularity | Sparse Threshold | Intermittent Threshold |
|---|---|---|
| **Daily** | %Zero > 80% | 50% < %Zero ≤ 80% |
| **Weekly** | %Zero > 70% | 40% < %Zero ≤ 70% |
| **Monthly** | %Zero > 60% | 30% < %Zero ≤ 60% |
| **Quarterly** | %Zero > 50% | 25% < %Zero ≤ 50% |
| **Yearly** | %Zero > 40% | 20% < %Zero ≤ 40% |

---

### D. Inter-Arrival Time CV — Pulsed Detection
> Measures regularity of intervals between demand events

**General Formula:**
```
Inter-arrival time = Number of periods between consecutive non-zero demand events
CV_arrival = σ_arrival / μ_arrival
CV_arrival < 0.3 → Pulsed (regular intervals)
CV_arrival ≥ 0.3 → Intermittent (irregular intervals)
```

| Granularity | Pulsed Threshold | Example Pattern |
|---|---|---|
| **Daily** | CV_arrival < 0.3 | Demand every 7 days ±1 day |
| **Weekly** | CV_arrival < 0.3 | Demand every 4 weeks ±0.5 weeks |
| **Monthly** | CV_arrival < 0.3 | Demand every 3 months ±0.5 months |
| **Quarterly** | CV_arrival < 0.3 | Demand every 2 quarters ±0.2 quarters |
| **Yearly** | CV_arrival < 0.3 | Demand every 2 years ±0.3 years |

---

### E. Structural Break Detection — Step Change
> Detects permanent level shifts in demand

| Granularity | Test | Window | Trigger |
|---|---|---|---|
| **Daily** | CUSUM | 30-day | CUSUM statistic > 5σ |
| **Weekly** | Chow Test + CUSUM | 8-week | Chow p < 0.05 |
| **Monthly** | Chow Test | 4-month | Chow p < 0.05 |
| **Quarterly** | Chow Test | 2-quarter | Chow p < 0.05 |
| **Yearly** | Chow Test | 2-year | Chow p < 0.05 |

---

### F. Volume Percentile — Slow Mover Detection
> Classifies absolute demand size relative to portfolio

**General Formula:**
```
Volume Percentile = rank(SKU mean demand) / total SKUs × 100
Slow Mover: Volume < 5th percentile of portfolio at same granularity
```

| Granularity | Slow Mover Threshold |
|---|---|
| **Daily** | Mean daily demand < 5th percentile of portfolio daily means |
| **Weekly** | Mean weekly demand < 5th percentile of portfolio weekly means |
| **Monthly** | Mean monthly demand < 5th percentile of portfolio monthly means |
| **Quarterly** | Mean quarterly demand < 5th percentile of portfolio quarterly means |
| **Yearly** | Mean yearly demand < 5th percentile of portfolio yearly means |

---

### G. Trend Detection — Trending Behavior
> Detects systematic directional demand movement within Behavior classification

**General Formula:**
```
Mann-Kendall test on rolling window
Trending: p < 0.05 (either direction)
Stable: p ≥ 0.10
```

| Granularity | Rolling Window | Min Obs |
|---|---|---|
| **Daily** | 90-day | ≥ 56 days |
| **Weekly** | 13-week | ≥ 8 weeks |
| **Monthly** | 6-month | ≥ 4 months |
| **Quarterly** | 4-quarter | ≥ 2 quarters |
| **Yearly** | 3-year | ≥ 2 years |

---

## 0.2 Behavior Classification Decision Matrix

```
STEP 1: Run structural break test (Section 0.1E)
  └── Significant break detected? → B6: STEP CHANGE

STEP 2: Compute ADI and CV² using granularity-specific thresholds

STEP 3: Apply CV² × ADI matrix

                        ADI
                 < Threshold    ≥ Threshold
               ┌─────────────┬───────────────┐
CV²  < 0.49   │             │               │
               │  ─ Volume < 5th pctile?     │
               │    → B8: SLOW MOVER         │
               │  ─ Trend detected?           │
               │    → B5: TRENDING           │
               │  ─ Default: B1: STABLE      │ B2: INTERMITTENT
               │             │               │
               │             │  ─ Inter-arrival CV < 0.3?
               │             │    → B7: PULSED
               │             │  ─ Default: B2: INTERMITTENT
               ├─────────────┼───────────────┤
CV²  ≥ 0.49   │ B3: ERRATIC │  B4: LUMPY    │
               └─────────────┴───────────────┘
```

---

## 0.3 Minimum History Requirements

| Requirement | Daily | Weekly | Monthly | Quarterly | Yearly |
|---|---|---|---|---|---|
| **Min total periods for ADI** | ≥ 30 days | ≥ 13 weeks | ≥ 6 months | ≥ 4 quarters | ≥ 3 years |
| **Min non-zero obs for CV²** | ≥ 10 days | ≥ 8 weeks | ≥ 6 months | ≥ 4 quarters | ≥ 3 years |
| **Min for Trend (Trending)** | ≥ 56 days | ≥ 8 weeks | ≥ 4 months | ≥ 2 quarters | ≥ 2 years |
| **Min for Step Change** | ≥ 30 days | ≥ 8 weeks | ≥ 4 months | ≥ 2 quarters | ≥ 2 years |
| **Min for Pulsed** | ≥ 5 events | ≥ 5 events | ≥ 5 events | ≥ 5 events | ≥ 5 events |

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
Rolling Mean (window w):      μ_w(t) = (1/w) × Σ d_{t-i}   for i = 0 to w-1
Rolling Std  (window w):      σ_w(t) = sqrt[(1/w) × Σ (d_{t-i} − μ_w)²]
Rolling CV²  (window w):      CV²_w(t) = [σ_w(t) / μ_w(t)]²  (non-zero only)
Rolling Slope (window w):     β_w(t) = Σ[(i − ī)(d_{t-i} − d̄)] / Σ[(i − ī)²]
Decay Weight:                 w_i = exp(−i / half_life) / Σ exp(−j / half_life)
```

---

## 0.5 Accuracy Metric Formulas

```
WMAPE   = Σ|Forecast_t − Actual_t| / Σ Actual_t × 100

Bias    = Σ(Forecast_t − Actual_t) / Σ Actual_t × 100

MAE     = (1/n) × Σ|Forecast_t − Actual_t|

MASE    = MAE_model / MAE_naive
          MAE_naive = (1/(n−m)) × Σ|Actual_t − Actual_{t−m}|  (m = seasonal period)
          MASE < 1.0 → model beats naive benchmark

Fill Rate (Intermittent) = Periods with correct zero forecast / Total zero periods × 100

Pinball(α,t) = α × (Actual_t − Q_α)     if Actual_t ≥ Q_α
             = (1−α) × (Q_α − Actual_t)  if Actual_t < Q_α

Coverage = Actuals within [P10, P90] / Total Periods × 100  (Target: 80%)
```

---

## 0.6 Seasonality Period Reference

| Granularity | Primary Period | Secondary Period | Detection Method |
|---|---|---|---|
| **Daily** | 7 (day of week) | 365 (annual) | FFT + ACF at lag 7, 365 |
| **Weekly** | 52 (annual) | 13 (quarterly) | FFT + ACF at lag 52, 13 |
| **Monthly** | 12 (annual) | 3 (quarterly) | ACF at lag 12, 3 |
| **Quarterly** | 4 (annual) | 2 (bi-annual) | ACF at lag 4, 2 |
| **Yearly** | — | — | No intra-year seasonality |

```
Seasonal Index: SI(p) = μ_p / μ_overall
ACF(lag) > 2/√n → Significant seasonality
Minimum 2 full cycles required for detection
```

---

## 0.7 Retraining & Backtesting Reference

| Granularity | Retraining | Latency | Backtest Train | Backtest Test |
|---|---|---|---|---|
| **Daily** | Daily | T+4 hours | 180 days | 30 days |
| **Weekly** | Weekly | T+1 day | 52 weeks | 13 weeks |
| **Monthly** | Monthly | T+2 days | 24 months | 6 months |
| **Quarterly** | Quarterly | T+3 days | 8 quarters | 2 quarters |
| **Yearly** | Annually | T+7 days | All available | 1 year |

---

# PART 1 — SEGMENT TEMPLATES

---

