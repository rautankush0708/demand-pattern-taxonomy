# PART 0 — FORMULA & THRESHOLD REFERENCE
## Magnitude Pattern Specific

---

## 0.1 Core Segmentation Metrics

### A. Volume Percentile Formula
> Classifies absolute demand size relative to the active portfolio

**General Formula:**
```
Mean Demand(SKU, window) = Σ d_t(SKU) / Total Periods in Window

Volume Percentile(SKU) = [Rank of SKU Mean Demand in Portfolio / Total Active SKUs] × 100

Rank is ascending: lowest demand = rank 1, highest demand = rank N
```

| Segment | Percentile Range | Classification |
|---|---|---|
| **Ultra Low** | < 5th percentile | Near-zero volume — single unit or near-single unit demand |
| **Low Volume** | 5th–25th percentile | Below-average volume — slow but meaningful demand |
| **Medium Volume** | 25th–75th percentile | Average portfolio volume — core mid-range SKUs |
| **High Volume** | > 75th percentile | Above-average volume — top-quarter of portfolio by demand |

**Computation Rules:**
- Compute mean demand over rolling window (see Section 0.3)
- Rank against **active SKUs only** — exclude Inactive lifecycle SKUs from ranking pool
- Recompute percentile ranking **monthly** — portfolio composition changes over time
- Use same granularity for comparison — daily means vs daily means; weekly vs weekly

---

### B. Absolute Volume Thresholds
> Portfolio-relative thresholds anchored to granularity-specific absolute minimums

**Note:** Percentile thresholds are primary. Absolute thresholds below are guardrails to prevent misclassification in very small or very large portfolios.

| Granularity | Ultra Low (absolute) | Low Volume (absolute) | Medium Volume (absolute) | High Volume (absolute) |
|---|---|---|---|---|
| **Daily** | Mean daily demand < 1 unit | 1–10 units/day | 10–100 units/day | > 100 units/day |
| **Weekly** | Mean weekly demand < 5 units | 5–50 units/week | 50–500 units/week | > 500 units/week |
| **Monthly** | Mean monthly demand < 20 units | 20–200 units/month | 200–2,000 units/month | > 2,000 units/month |
| **Quarterly** | Mean quarterly demand < 60 units | 60–600 units/quarter | 600–6,000 units/quarter | > 6,000 units/quarter |
| **Yearly** | Mean yearly demand < 240 units | 240–2,400 units/year | 2,400–24,000 units/year | > 24,000 units/year |

**Override Rule:** If percentile and absolute thresholds disagree, use the **more conservative** classification (i.e. classify lower if in doubt).

---

### C. Coefficient of Variation of Mean Demand
> Measures stability of the volume classification over time

**Formula:**
```
CV_mean = σ(rolling_mean) / μ(rolling_mean)   over extended window

CV_mean < 0.20 → Volume classification stable — use current percentile
CV_mean 0.20–0.40 → Volume drifting — flag for review; use 6-month average percentile
CV_mean > 0.40 → Volume highly unstable — combine with Lifecycle/Behavior signals
```

---

### D. ABC Classification Alignment
> Maps Magnitude segments to standard ABC inventory classification

```
A Items (top 20% of SKUs driving ~80% of revenue):   typically High Volume
B Items (next 30% of SKUs):                           typically Medium Volume
C Items (bottom 50% of SKUs):                         typically Low Volume + Ultra Low

Note: ABC is revenue-weighted; Magnitude is volume-weighted
High-price Low-volume SKUs may be A items but Low Volume magnitude
```

| Magnitude | Typical ABC | Inventory Policy |
|---|---|---|
| High Volume | A | Continuous review; tight safety stock; frequent replenishment |
| Medium Volume | A/B | Periodic review; standard safety stock |
| Low Volume | B/C | Periodic review; min/max policy |
| Ultra Low | C | Reorder point = 1; review monthly; consider make-to-order |

---

## 0.2 Magnitude Classification Decision Rules

```
STEP 1: Compute mean demand over rolling window (Section 0.3)
STEP 2: Rank against active portfolio at same granularity
STEP 3: Compute percentile
STEP 4: Apply percentile threshold

  Percentile < 5%   → ULTRA LOW
  5% ≤ Percentile < 25% → LOW VOLUME
  25% ≤ Percentile < 75% → MEDIUM VOLUME
  Percentile ≥ 75%  → HIGH VOLUME

STEP 5: Check absolute threshold guardrail — override if needed
STEP 6: Check CV_mean — flag if unstable (CV_mean > 0.40)
STEP 7: Recheck monthly — portfolio composition changes affect percentile ranking
```

---

## 0.3 Rolling Window Reference

| Window Name | Daily | Weekly | Monthly | Quarterly | Yearly |
|---|---|---|---|---|---|
| **Percentile Window** | 90 days | 26 weeks | 6 months | 4 quarters | 3 years |
| **Short** | 7 days | 4 weeks | 2 months | 1 quarter | 1 year |
| **Medium** | 30 days | 8 weeks | 3 months | 2 quarters | 2 years |
| **Long** | 90 days | 13 weeks | 6 months | 3 quarters | 3 years |
| **Extended** | 180 days | 26 weeks | 12 months | 4 quarters | 4 years |
| **Full Year** | 365 days | 52 weeks | 12 months | 4 quarters | 5 years |
| **DL Lookback** | 90 days | 52 weeks | 24 months | 8 quarters | 5 years |

**Rolling Mean Formula:**
```
Rolling Mean (window w): μ_w(t) = (1/w) × Σ d_{t-i}  for i = 0 to w-1
Rolling Std  (window w): σ_w(t) = sqrt[(1/w) × Σ (d_{t-i} − μ_w)²]
CV_mean:                 CV_mean = σ_w(t) / μ_w(t)
```

---

## 0.4 Accuracy Metric Selection by Magnitude

> Metric selection is one of the primary reasons Magnitude classification exists — MAPE is unreliable at low volume; WMAPE at high volume understates tail errors.

```
High Volume:   WMAPE (primary) + RMSE (secondary) + Bias
               MAPE acceptable — denominator is large and stable
               Safety stock: σ_forecast_error × z_service_level

Medium Volume: WMAPE (primary) + MAE (secondary) + Bias
               MAPE acceptable with care — occasional small actuals inflate MAPE
               Safety stock: σ_forecast_error × z_service_level

Low Volume:    MAE (primary) + MASE (secondary) + Bias
               MAPE unreliable — small denominators inflate metric
               Safety stock: min/max policy preferred over σ-based

Ultra Low:     MAE (primary, in units) + Fill Rate (secondary) + Bias
               MAPE completely unreliable — avoid entirely
               Safety stock: fixed buffer (1–2 units); consider make-to-order
```

**MASE Formula (preferred for Low and Ultra Low):**
```
MASE = MAE_model / MAE_naive
MAE_naive = (1/(n−m)) × Σ|Actual_t − Actual_{t−m}|
m = seasonal period (see Section 0.6)
MASE < 1.0 → model beats naive seasonal benchmark
```

**Pinball Loss (for probabilistic forecasts):**
```
Pinball(α,t) = α × (Actual_t − Q_α)     if Actual_t ≥ Q_α
             = (1−α) × (Q_α − Actual_t)  if Actual_t < Q_α
Coverage = Actuals within [P10, P90] / n × 100  (Target: 80%)
```

---

## 0.5 WMAPE / Bias Targets by Magnitude and Granularity

| Segment | Daily WMAPE | Weekly WMAPE | Monthly WMAPE | Quarterly WMAPE | Yearly WMAPE |
|---|---|---|---|---|---|
| **High Volume** | < 15% | < 12% | < 10% | < 8% | < 6% |
| **Medium Volume** | < 22% | < 18% | < 15% | < 12% | < 10% |
| **Low Volume** | MAE primary | MAE primary | < 20% MASE | < 18% MASE | < 15% MASE |
| **Ultra Low** | MAE < 1 unit | MAE < 2 units | MAE < 5 units | MAE < 10 units | MAE < 20 units |

| Segment | Bias Alert Threshold |
|---|---|
| **High Volume** | \|Bias\| > 5% |
| **Medium Volume** | \|Bias\| > 8% |
| **Low Volume** | \|Bias\| > 12% |
| **Ultra Low** | \|Bias\| > 20% |

---

## 0.6 Seasonality Period Reference

| Granularity | Primary Period | Secondary Period | Detection |
|---|---|---|---|
| **Daily** | 7 (day of week) | 365 (annual) | FFT + ACF at lag 7, 365 |
| **Weekly** | 52 (annual) | 13 (quarterly) | ACF at lag 52, 13 |
| **Monthly** | 12 (annual) | 3 (quarterly) | ACF at lag 12, 3 |
| **Quarterly** | 4 (annual) | 2 (bi-annual) | ACF at lag 4, 2 |
| **Yearly** | — | — | Not applicable |

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

---

# PART 1 — SEGMENT TEMPLATES

