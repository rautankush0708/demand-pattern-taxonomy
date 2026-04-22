# Dimension 2 · Behavior Pattern
## Demand Forecasting Model Templates

---

> **Segments:** 8 · Stable · Intermittent · Erratic · Lumpy · Trending · Step Change · Pulsed · Slow Mover
> **Granularities:** Daily · Weekly · Monthly · Quarterly · Yearly

---

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

## B1 · Stable

### 1. Definition
Predicts demand for SKUs with low demand variance (CV² < 0.49) and high demand frequency (ADI below granularity threshold), where demand is consistent, well-behaved, and highly forecastable with standard time-series methods.

### 2. Detailed Description
- **Applicable scenarios:** Core FMCG lines, everyday essentials, high-frequency replenishment items, staple categories
- **Boundaries:**

| Granularity | ADI Threshold | CV² Threshold | Volume | Additional |
|---|---|---|---|---|
| Daily | ADI < 1.10 | CV² < 0.49 | > 5th pctile | No significant trend (p ≥ 0.10) |
| Weekly | ADI < 1.32 | CV² < 0.49 | > 5th pctile | No significant trend (p ≥ 0.10) |
| Monthly | ADI < 1.25 | CV² < 0.49 | > 5th pctile | No significant trend (p ≥ 0.10) |
| Quarterly | ADI < 1.20 | CV² < 0.49 | > 5th pctile | No significant trend (p ≥ 0.10) |
| Yearly | ADI < 1.10 | CV² < 0.49 | > 5th pctile | No significant trend (p ≥ 0.10) |

- **Key demand characteristics:** Low variance, high frequency, minimal zero periods, flat or mildly varying baseline
- **Differentiation from other models:** Unlike Volatile/Erratic, CV² is low; unlike Slow Mover, volume is above threshold; unlike Intermittent, ADI is below threshold; unlike Trending, no directional slope detected

### 3. Business Impact
- **Primary risk (over-forecast):** Excess working capital in inventory — low probability with good models
- **Primary risk (under-forecast):** Service level breaches on core revenue lines
- **Strategic importance:** Very high — Stable SKUs form the revenue backbone of most portfolios

### 4. Priority Level
🔴 Tier 1 — High volume, high frequency — even small percentage errors create large absolute inventory waste.

### 5. Model Strategy Overview

#### 5.1 Zero-Demand Handling (Hurdle)
- Active event threshold: P(demand > 0) > 0.90 — stable SKUs rarely go to zero
- Classifier type: Rule-based flag only — 2+ consecutive zero periods triggers alert
- Regressor type: LightGBM primary; ETS supplementary
- Fallback: Rolling mean over extended window

#### 5.2 Analogue / Similarity Logic
- Not applicable — sufficient own history; analogues not used for Stable SKUs

#### 5.3 Feature Engineering

| Granularity | Rolling Windows | Seasonal Features | External Signals |
|---|---|---|---|
| Daily | 7, 30, 90, 180, 365-day mean & std | Day of week, month index, holiday flag, annual cycle index | Promo calendar, price index |
| Weekly | 4, 8, 13, 26, 52-week mean & std | Week of year, quarter flag, holiday proximity | Promo calendar, price index |
| Monthly | 2, 3, 6, 12, 24-month mean & std | Month of year, quarter, half-year flag | Promo calendar, price index |
| Quarterly | 1, 2, 3, 4-quarter mean & std | Quarter of year, half-year | Promo flag |
| Yearly | 1, 2, 3, 4, 5-year mean & std | Long cycle index | Macro index |

- Categorical encoding: Target encoding with smoothing factor = 10

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM
- Configuration: Objective = reg:squarederror; Metric = WMAPE, RMSE
- Key features: All rolling means, seasonal index, promo flag, price index, holiday flag, period of year
- When to use: Primary model — rich feature set, well-understood demand

#### 6.2 Deep Learning (DL)
- Architectures: N-BEATS / TFT

| Granularity | Lookback | Features | Output |
|---|---|---|---|
| Daily | 365 days | 18 | P10, P50, P90 |
| Weekly | 52 weeks | 15 | P10, P50, P90 |
| Monthly | 24 months | 12 | P10, P50, P90 |
| Quarterly | 8 quarters | 10 | P10, P50, P90 |
| Yearly | 5 years | 8 | P10, P50, P90 |

- Training: Loss = MAE; Adam lr = 0.001; Dropout = 0.1; Early stopping patience = 15
- When to use: High-volume SKUs with complex seasonal patterns; history > 1 year equivalent

#### 6.3 Statistical / Time Series Models
- Architectures: ETS(A,N,A) — Holt-Winters additive seasonality

| Granularity | Seasonal Period | Model Variant |
|---|---|---|
| Daily | 7 (primary), 365 (secondary) | TBATS for dual seasonality |
| Weekly | 52 (primary), 13 (secondary) | ETS(A,N,A) with period = 52 |
| Monthly | 12 (primary), 3 (secondary) | SARIMA(p,0,q)(P,0,Q)_12 |
| Quarterly | 4 | ETS(A,N,A) with period = 4 |
| Yearly | None | ETS(A,N,N) — no seasonality |

- When to use: Interpretability requirement; prediction intervals needed; short history

#### 6.4 Baseline / Fallback Model
- Fallback triggers: Feature pipeline failure; model convergence issue
- Fallback model: Same period last year (naive seasonal)
- Logging & alerting: Alert if fallback rate > 10%

### 7. Ensemble & Weighting

#### 7.1 Ensemble Scheme
- Combination: D̂_t = w_lgbm × LightGBM + w_ets × ETS + w_dl × N-BEATS
- Weight determination: Error-inverse weighting on 8-period rolling WMAPE

#### 7.2 Dynamic Weight Schedule

| History Length | LightGBM | ETS | N-BEATS / TFT |
|---|---|---|---|
| Up to 1 year equivalent | 60% | 40% | 0% |
| > 1 year equivalent | 50% | 30% | 20% |

### 8. Uncertainty Quantification
- Method: Conformal prediction on residuals
- Output: [P10, P50, P90]
- Use case: Safety stock optimisation at target service level; P90 used for max stock bound

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Capping: min(forecast, 1.5 × full-year rolling max)
- Manual overrides: Range review decisions; promotional plan changes; known supply disruptions
- Alignment constraints: Forecast within ±20% of prior year same period unless justified with reason code

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | WMAPE Target | Bias Alert | Coverage Target |
|---|---|---|---|
| Daily | < 20% | \|Bias\| > 10% | 80% P10–P90 |
| Weekly | < 18% | \|Bias\| > 8% | 80% P10–P90 |
| Monthly | < 15% | \|Bias\| > 7% | 80% P10–P90 |
| Quarterly | < 12% | \|Bias\| > 6% | 80% P10–P90 |
| Yearly | < 10% | \|Bias\| > 5% | 80% P10–P90 |

#### 10.2 Backtesting Protocol

| Granularity | Method | Train | Test | Min History |
|---|---|---|---|---|
| Daily | Rolling window | 180 days | 30 days | 365 days |
| Weekly | Rolling window | 52 weeks | 13 weeks | 104 weeks |
| Monthly | Rolling window | 24 months | 6 months | 24 months |
| Quarterly | Rolling window | 8 quarters | 2 quarters | 8 quarters |
| Yearly | Expanding window | All available | 1 year | 3 years |

#### 10.3 Retraining & Data Freshness

| Granularity | Cadence | Incremental | Latency |
|---|---|---|---|
| Daily | Daily | No | T+4 hours |
| Weekly | Weekly | No | T+1 day |
| Monthly | Monthly | No | T+2 days |
| Quarterly | Quarterly | No | T+3 days |
| Yearly | Annually | No | T+7 days |

### 11. Exception Handling & Overrides
- Automatic exception detection: Forecast > 2 × historical max; 3+ consecutive zero actuals; bias drift > alert threshold for 4 periods
- Manual override process: Planner approval via dashboard; reason code required; logged with timestamp
- Override expiration: Single cycle unless permanent range change flagged

### 12. Reclassification / Model Selection

| Condition | Target Segment | Holding Period |
|---|---|---|
| CV² rises above 0.49 for 8 consecutive periods | Erratic or Volatile | 8 periods confirmation |
| ADI rises above threshold for 8 consecutive periods | Intermittent | 8 periods confirmation |
| Volume drops below 5th percentile for 8 periods | Slow Mover | 8 periods confirmation |
| Trend detected (Mann-Kendall p < 0.05) for 4 periods | Trending | 4 periods confirmation |
| Structural break detected | Step Change | Immediate |

- Switching logic: Soft blend over 4 periods for gradual transitions; hard switch for Step Change

### 13. Review Cadence
- Performance monitoring: Per cycle automated dashboard
- Model review meeting: Bi-weekly S&OP forecast review
- Full model re-evaluation: Quarterly

---

## B2 · Intermittent

### 1. Definition
Predicts demand for SKUs with low demand variance (CV² < 0.49) but low demand frequency (ADI ≥ granularity threshold), where demand occurs sporadically but in consistent quantities when it does occur; requires specialist intermittent demand methods.

### 2. Detailed Description
- **Applicable scenarios:** Spare parts, B2B specialty items, niche products, slow-moving lines with occasional orders
- **Boundaries:**

| Granularity | ADI Threshold | CV² Threshold | %Zero Range |
|---|---|---|---|
| Daily | ADI ≥ 1.10 | CV² < 0.49 | 50%–80% |
| Weekly | ADI ≥ 1.32 | CV² < 0.49 | 40%–70% |
| Monthly | ADI ≥ 1.25 | CV² < 0.49 | 30%–60% |
| Quarterly | ADI ≥ 1.20 | CV² < 0.49 | 25%–50% |
| Yearly | ADI ≥ 1.10 | CV² < 0.49 | 20%–40% |

- **Key demand characteristics:** Many zero periods, consistent non-zero quantity when demand occurs, Poisson-like arrival process
- **Differentiation from other models:** Unlike Lumpy, quantity is consistent (low CV²); unlike Sparse, ADI is moderate not extreme; unlike Pulsed, inter-arrival intervals are irregular

### 3. Business Impact
- **Primary risk (over-forecast):** Dead stock accumulation between demand events
- **Primary risk (under-forecast):** Stockout when demand arrives — often critical in aftermarket or MRO context
- **Strategic importance:** Medium-high for aftermarket and MRO; medium for niche retail

### 4. Priority Level
🟠 Tier 2 — Moderate volume but high service criticality in aftermarket and spare parts contexts.

### 5. Model Strategy Overview

#### 5.1 Zero-Demand Handling (Hurdle)
- Active event threshold: P(demand > 0) > 0.30 — many zero periods are expected and correct
- Classifier type: XGBoost on inter-arrival features
- Regressor type: Croston / SBA on non-zero demand only
- Fallback: Croston's method as primary statistical fallback

#### 5.2 Analogue / Similarity Logic
- Number of analogues: k = 3 from same part family or category
- Similarity criteria: ADI range ±0.5, CV² range ±0.1, category, price tier
- Temporal decay: weight = exp(−age / half-life)

| Granularity | Half-Life |
|---|---|
| Daily | 30 days |
| Weekly | 8 weeks |
| Monthly | 4 months |
| Quarterly | 2 quarters |
| Yearly | 2 years |

- Aggregation: Weighted mean on non-zero demand periods

#### 5.3 Feature Engineering

| Granularity | Key Features | Min Non-Zero Obs |
|---|---|---|
| Daily | Inter-arrival mean, inter-arrival std, CV_arrival, days since last demand, rolling non-zero mean (30-day) | ≥ 10 events |
| Weekly | Inter-arrival mean (weeks), CV_arrival, weeks since last demand, rolling non-zero mean (13-week) | ≥ 8 events |
| Monthly | Inter-arrival mean (months), CV_arrival, months since last demand, rolling non-zero mean (6-month) | ≥ 6 events |
| Quarterly | Inter-arrival mean (quarters), CV_arrival, quarters since last demand | ≥ 4 events |
| Yearly | Inter-arrival mean (years), years since last demand | ≥ 3 events |

- External signals: Equipment install base (MRO), order seasonality flag, contract renewal calendar

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: XGBoost (classifier) + XGBoost (regressor on non-zero periods)
- Classifier: Objective = binary:logistic; Metric = AUC, Precision/Recall at 0.30 threshold
- Regressor: Objective = reg:absoluteerror; Metric = MAE on non-zero periods only
- Key features: Inter-arrival time mean/std/CV, periods since last demand, rolling non-zero mean, category, price tier
- When to use: When ≥ 8 demand events in history

#### 6.2 Deep Learning (DL)
- Architectures: DeepAR (handles intermittent natively via negative binomial output distribution)

| Granularity | Lookback | Features | Output |
|---|---|---|---|
| Daily | 180 days | 8 | P10, P50, P90 |
| Weekly | 52 weeks | 8 | P10, P50, P90 |
| Monthly | 24 months | 6 | P10, P50, P90 |
| Quarterly | 8 quarters | 5 | P10, P50, P90 |
| Yearly | 5 years | 4 | P10, P50, P90 |

- Training: Loss = negative log-likelihood (NB distribution); Adam lr = 0.001; Dropout = 0.1; Patience = 10
- When to use: Large portfolio of intermittent SKUs — cross-learning across SKUs improves performance

#### 6.3 Statistical / Time Series Models
- Architectures: Croston's method (primary); SBA (Syntetos-Boylan Approximation) for bias correction

**Croston Formula:**
```
Demand size:    z_t = α × d_t + (1−α) × z_{t-1}   (update only on non-zero periods)
Inter-arrival:  p_t = α × q_t + (1−α) × p_{t-1}   (update only on non-zero periods)
Forecast:       F_t = z_t / p_t

SBA correction: F_SBA = (1 − α/2) × F_Croston
α = 0.1 to 0.3 (optimise on validation MAE)
```

| Granularity | Recommended α | Model |
|---|---|---|
| Daily | 0.10 | SBA |
| Weekly | 0.15 | SBA |
| Monthly | 0.20 | Croston / SBA |
| Quarterly | 0.20 | Croston |
| Yearly | 0.25 | Croston |

- When to use: Default statistical model for intermittent demand; always included in ensemble

#### 6.4 Baseline / Fallback Model
- Fallback triggers: Fewer than 5 demand events; XGBoost convergence failure
- Fallback model: Croston's method (always computable)
- Logging & alerting: Alert if fallback rate > 30%

### 7. Ensemble & Weighting

#### 7.1 Ensemble Scheme
- Combination: D̂_t = w_xgb × XGBoost + w_sba × SBA + w_dar × DeepAR
- Weight determination: Error-inverse weighting on non-zero period MAE

#### 7.2 Dynamic Weight Schedule

| Events in History | XGBoost | SBA | DeepAR |
|---|---|---|---|
| 5–10 events | 20% | 80% | 0% |
| 11–20 events | 50% | 50% | 0% |
| > 20 events | 50% | 30% | 20% |

### 8. Uncertainty Quantification
- Method: Negative binomial distribution fit; quantile regression on non-zero demand
- Output: [P10, P50, P90] on both demand occurrence and quantity separately
- Use case: Stock availability optimisation; spare parts service level

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Capping: min(forecast, 3 × historical max single demand event)
- Manual overrides: Known upcoming demand event (scheduled maintenance, contract renewal)
- Alignment: Forecast consistent with equipment install base count

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | Non-Zero MAE Target | Fill Rate Target | Bias Alert |
|---|---|---|---|
| Daily | MAE on non-zero days < 30% of mean | > 85% | \|Bias\| > 15% |
| Weekly | MAE on non-zero weeks < 25% of mean | > 85% | \|Bias\| > 15% |
| Monthly | MAE on non-zero months < 20% of mean | > 85% | \|Bias\| > 12% |
| Quarterly | MAE on non-zero quarters < 18% of mean | > 85% | \|Bias\| > 10% |
| Yearly | MAE on non-zero years < 15% of mean | > 80% | \|Bias\| > 8% |

#### 10.2 Backtesting Protocol

| Granularity | Method | Train | Test |
|---|---|---|---|
| Daily | Leave-one-out on demand events | Events 1 to n-3 | Last 3 events |
| Weekly | Leave-one-out on demand events | Events 1 to n-3 | Last 3 events |
| Monthly | Leave-one-out on demand events | Events 1 to n-3 | Last 3 events |
| Quarterly | Leave-one-out on demand events | Events 1 to n-2 | Last 2 events |
| Yearly | Leave-one-out on demand events | Events 1 to n-2 | Last 2 events |

#### 10.3 Retraining & Data Freshness

| Granularity | Cadence | Latency |
|---|---|---|
| Daily | Weekly | T+4 hours |
| Weekly | Weekly | T+1 day |
| Monthly | Monthly | T+2 days |
| Quarterly | Quarterly | T+3 days |
| Yearly | Annually | T+7 days |

### 11. Exception Handling & Overrides
- Automatic exception detection: Forecast > 0 for 8+ consecutive periods with zero actuals; demand event > 3 × historical max
- Manual override process: Planner input for known demand events; approval logged
- Override expiration: Single cycle

### 12. Reclassification / Model Selection

| Condition | Target Segment | Holding Period |
|---|---|---|
| CV² rises above 0.49 for 8 periods | Lumpy | 8 periods |
| ADI drops below threshold for 8 periods | Stable | 8 periods |
| %Zero exceeds Sparse threshold for 8 periods | Sparse sub-flag | 8 periods |
| Inter-arrival CV drops below 0.3 | Pulsed | 5 events |

### 13. Review Cadence
- Performance monitoring: Weekly automated — focus on non-zero period accuracy
- Model review meeting: Monthly intermittent demand review
- Full model re-evaluation: Quarterly or on install base change

---

## B3 · Erratic

### 1. Definition
Predicts demand for SKUs with high demand variance (CV² ≥ 0.49) and high demand frequency (ADI below granularity threshold), where demand occurs regularly but in highly unpredictable quantities.

### 2. Detailed Description
- **Applicable scenarios:** Promotional items, fashion/seasonal lines, weather-sensitive categories, volatile B2C demand
- **Boundaries:**

| Granularity | ADI Threshold | CV² Threshold |
|---|---|---|
| Daily | ADI < 1.10 | CV² ≥ 0.49 |
| Weekly | ADI < 1.32 | CV² ≥ 0.49 |
| Monthly | ADI < 1.25 | CV² ≥ 0.49 |
| Quarterly | ADI < 1.20 | CV² ≥ 0.49 |
| Yearly | ADI < 1.10 | CV² ≥ 0.49 |

- **Key demand characteristics:** Regular occurrence, high quantity variance, difficult to forecast quantity even when timing is known
- **Differentiation from other models:** Unlike Stable, CV² is high; unlike Lumpy, ADI is below threshold (demand occurs regularly); unlike Intermittent, demand is frequent

### 3. Business Impact
- **Primary risk (over-forecast):** Significant inventory when demand dips unexpectedly
- **Primary risk (under-forecast):** Stockouts during demand spikes — lost sales and poor service
- **Strategic importance:** High — erratic SKUs are often promotional or trend-driven with high revenue potential

### 4. Priority Level
🔴 Tier 1 — High frequency means high absolute volume impact; variance makes both over and under-forecast costly.

### 5. Model Strategy Overview

#### 5.1 Zero-Demand Handling (Hurdle)
- Active event threshold: P(demand > 0) > 0.70 — demand is frequent; focus on quantity not occurrence
- Classifier type: Rule-based — flag only when consecutive zeros appear
- Regressor type: LightGBM / CatBoost with variance-aware objective
- Fallback: Rolling mean with wide prediction intervals

#### 5.2 Analogue / Similarity Logic
- Number of analogues: k = 3 (erratic SKUs from same category at similar CV² level)
- Similarity criteria: Category, CV² range ±0.1, ADI range ±0.3, price tier
- Temporal decay: weight = exp(−age / half-life)

| Granularity | Half-Life |
|---|---|
| Daily | 14 days |
| Weekly | 4 weeks |
| Monthly | 2 months |
| Quarterly | 1 quarter |
| Yearly | 1 year |

#### 5.3 Feature Engineering

| Granularity | Rolling Windows | Additional Features |
|---|---|---|
| Daily | 7, 14, 30, 90-day mean, std, CV², max | Day of week, holiday, promo flag, weather index |
| Weekly | 4, 8, 13, 26-week mean, std, CV², max | Week of year, promo flag, competitor activity |
| Monthly | 2, 3, 6, 12-month mean, std, CV², max | Month of year, promo depth, price elasticity index |
| Quarterly | 1, 2, 3, 4-quarter mean, std, CV², max | Quarter, promo flag |
| Yearly | 1, 2, 3-year mean, std, CV², max | Long cycle, macro index |

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM / CatBoost
- Configuration: Objective = reg:squarederror with quantile outputs; Metric = WMAPE, Pinball loss
- Key features: Rolling means, rolling CV², rolling max, promo flag, holiday flag, day/week of year, price index
- When to use: Primary model — tabular features capture variance drivers well

#### 6.2 Deep Learning (DL)
- Architectures: TFT with quantile outputs

| Granularity | Lookback | Features | Output |
|---|---|---|---|
| Daily | 90 days | 15 | P10, P25, P50, P75, P90 |
| Weekly | 52 weeks | 12 | P10, P25, P50, P75, P90 |
| Monthly | 24 months | 10 | P10, P25, P50, P75, P90 |
| Quarterly | 8 quarters | 8 | P10, P25, P50, P75, P90 |
| Yearly | 5 years | 6 | P10, P25, P50, P75, P90 |

- Training: Loss = quantile loss (multiple quantiles); Adam lr = 0.001; Dropout = 0.2; Patience = 10
- When to use: When variance structure is complex and multi-quantile output is needed

#### 6.3 Statistical / Time Series Models
- Architectures: SARIMA with heteroscedastic errors; TBATS for dual seasonality at daily level
- When to use: Interpretability requirement; short history

#### 6.4 Baseline / Fallback Model
- Fallback triggers: Model convergence failure; missing external features
- Fallback model: Rolling mean (medium window) with ±1.5σ prediction interval
- Logging & alerting: Alert if fallback rate > 20%

### 7. Ensemble & Weighting

#### 7.1 Ensemble Scheme
- Combination: D̂_t = w_lgbm × LightGBM + w_tft × TFT + w_stat × SARIMA
- Weight determination: Error-inverse weighting on Pinball loss (P50) over 8-period rolling window

#### 7.2 Dynamic Weight Schedule

| History Length | LightGBM | TFT | SARIMA |
|---|---|---|---|
| Up to 6 months equiv. | 70% | 0% | 30% |
| 6–12 months equiv. | 60% | 30% | 10% |
| > 12 months equiv. | 50% | 40% | 10% |

### 8. Uncertainty Quantification
- Method: Quantile regression — full distribution output
- Output: [P10, P25, P50, P75, P90] — wider interval needed for erratic demand
- Use case: Safety stock at P75 or P90 depending on service level target

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Capping: min(forecast, 2 × rolling max over long window)
- Manual overrides: Promotional plan inputs; event uplift; competitor action flags
- Alignment: Forecast must be consistent with promotional calendar uplifts

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | WMAPE Target | Bias Alert | Pinball Coverage |
|---|---|---|---|
| Daily | < 35% | \|Bias\| > 15% | 80% P10–P90 |
| Weekly | < 30% | \|Bias\| > 12% | 80% P10–P90 |
| Monthly | < 25% | \|Bias\| > 10% | 80% P10–P90 |
| Quarterly | < 20% | \|Bias\| > 8% | 80% P10–P90 |
| Yearly | < 15% | \|Bias\| > 6% | 80% P10–P90 |

#### 10.2 Backtesting Protocol

| Granularity | Train | Test |
|---|---|---|
| Daily | 180 days | 30 days |
| Weekly | 52 weeks | 13 weeks |
| Monthly | 24 months | 6 months |
| Quarterly | 8 quarters | 2 quarters |
| Yearly | All available | 1 year |

### 11. Exception Handling & Overrides
- Automatic exception detection: Forecast > 3 × rolling max; CV² drops below 0.49 for 8 periods (→ Stable)
- Manual override: Commercial team promo/event input; reason logged

### 12. Reclassification / Model Selection

| Condition | Target Segment | Holding Period |
|---|---|---|
| CV² drops below 0.49 for 8 periods | Stable | 8 periods |
| ADI rises above threshold for 8 periods | Lumpy | 8 periods |
| Structural break detected | Step Change | Immediate |
| Volume drops below 5th percentile | Slow Mover | 8 periods |

### 13. Review Cadence
- Performance monitoring: Per cycle — Pinball loss and CV² drift monitored
- Model review meeting: Weekly for high-value erratic SKUs; bi-weekly otherwise
- Full model re-evaluation: Quarterly

---

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

## B5 · Trending

### 1. Definition
Predicts demand for SKUs with a statistically confirmed directional slope (either positive or negative) that sits within the Stable/Slow Mover CV²-ADI quadrant, requiring trend-aware models to avoid systematic directional bias.

### 2. Detailed Description
- **Applicable scenarios:** Gradually growing or declining product lines without discrete lifecycle reclassification trigger, slow burn trends, gradual market share shifts
- **Boundaries:**

| Granularity | ADI | CV² | Trend Condition |
|---|---|---|---|
| Daily | < 1.10 | < 0.49 | Mann-Kendall p < 0.05 on 90-day window |
| Weekly | < 1.32 | < 0.49 | Mann-Kendall p < 0.05 on 13-week window |
| Monthly | < 1.25 | < 0.49 | Mann-Kendall p < 0.05 on 6-month window |
| Quarterly | < 1.20 | < 0.49 | Mann-Kendall p < 0.05 on 4-quarter window |
| Yearly | < 1.10 | < 0.49 | Mann-Kendall p < 0.05 on 3-year window |

- **Key demand characteristics:** Consistent directional movement, low variance around the trend, regular demand occurrence
- **Differentiation:** Unlike Stable, a trend exists; unlike Growth/Decline Lifecycle, this is behavioral — the Lifecycle segment may be Mature but demand still has a trend component

### 3. Business Impact
- **Primary risk (over-forecast):** Over-forecast on downward trending SKUs — inventory build
- **Primary risk (under-forecast):** Under-forecast on upward trending SKUs — stockouts
- **Strategic importance:** Medium-high — trend direction determines inventory strategy

### 4. Priority Level
🟠 Tier 2 — Trend models prevent systematic directional bias; medium complexity.

### 5. Model Strategy Overview

#### 5.1 Hurdle
- Threshold: P(demand > 0) > 0.75 — trending SKUs are regularly demanded
- Regressor: LightGBM / ETS with trend component

#### 5.2 Feature Engineering

| Granularity | Rolling Windows | Trend Features |
|---|---|---|
| Daily | 7, 30, 90, 180-day | β_90day slope, slope direction flag, periods of consistent direction |
| Weekly | 4, 8, 13, 26-week | β_13week slope, slope direction flag |
| Monthly | 2, 3, 6, 12-month | β_6month slope |
| Quarterly | 1, 2, 4-quarter | β_4quarter slope |
| Yearly | 1, 2, 3-year | β_3year slope |

### 6. Model Families

#### 6.1 ML: LightGBM with slope and direction features
- Regressor: reg:squarederror | WMAPE, RMSE

#### 6.2 DL: TFT — captures trend via attention mechanism

| Granularity | Lookback | Features |
|---|---|---|
| Daily | 180 days | 12 |
| Weekly | 52 weeks | 10 |
| Monthly | 24 months | 8 |
| Quarterly | 8 quarters | 6 |
| Yearly | 5 years | 5 |

#### 6.3 Statistical: ETS(A,A,N) — additive trend; damped if downward (phi = 0.85)

#### 6.4 Fallback: Rolling mean + slope extrapolation; alert if fallback > 15%

### 7. Ensemble

| History | LightGBM | TFT | ETS |
|---|---|---|---|
| Up to 6 months equiv. | 70% | 0% | 30% |
| 6–12 months equiv. | 60% | 30% | 10% |
| > 12 months equiv. | 50% | 40% | 10% |

### 8. Uncertainty Quantification
- Quantile regression: [P10, P50, P90]
- Upward trend: P75 for safety stock; downward trend: P50 for base (conservative)

### 9. Business Rules
- Capping: Upward — min(forecast, 2 × rolling max); Downward — max(forecast, 0) with decay cap
- Manual overrides: Commercial confirmation of trend continuation/reversal

### 10. Evaluation

| Granularity | WMAPE Target | Bias Alert (directional) |
|---|---|---|
| Daily | < 25% | Directional Bias > 12% |
| Weekly | < 20% | Directional Bias > 10% |
| Monthly | < 18% | Directional Bias > 8% |
| Quarterly | < 15% | Directional Bias > 6% |
| Yearly | < 12% | Directional Bias > 5% |

### 11. Exception Handling
- Alert: Trend reversal for 3 consecutive periods → evaluate reclassification to Stable

### 12. Reclassification

| Condition | Target | Holding Period |
|---|---|---|
| Trend p > 0.10 for 4 periods | Stable | 4 periods |
| CV² rises above 0.49 | Erratic | 8 periods |
| ADI rises above threshold | Lumpy or Intermittent | 8 periods |

### 13. Review Cadence
- Per cycle with slope monitor; bi-weekly review; quarterly full re-evaluation

---

## B6 · Step Change

### 1. Definition
Predicts demand for SKUs where a structural break has caused a permanent shift in the demand level, requiring rebaselining before any pattern model is applied; the pre-processing segment that protects other segments from corrupted baselines.

### 2. Detailed Description
- **Applicable scenarios:** Permanent distribution gain/loss, major competitor entry/exit, regulatory change, pricing restructure
- **Boundaries:** Structural break test significant (see Section 0.1E) regardless of CV²/ADI values
- **Key demand characteristics:** Two distinct demand regimes separated by a breakpoint; model trained on pre-break data is invalid
- **Differentiation:** Unlike Trending, change is sudden and permanent — not gradual; unlike Volatile/Erratic, variance within each regime may be low; the break itself creates the misclassification risk

### 3. Business Impact
- **Primary risk (over-forecast):** Using pre-break high baseline after downward step — chronic overstock
- **Primary risk (under-forecast):** Using pre-break low baseline after upward step — chronic stockout
- **Strategic importance:** Very high — forecasting on wrong baseline makes all models fail

### 4. Priority Level
🔴 Tier 1 — Corrupted baseline contaminates all downstream forecasting; must be detected and corrected first.

### 5. Model Strategy Overview

#### 5.1 Break Detection (Hurdle)
- Run structural break test at each retraining cycle (Section 0.1E)
- On break detection: Flag SKU; truncate training data to post-break period only
- Re-run behavior classification on post-break data to assign correct sub-segment

#### 5.2 Post-Break Rebaselining

| Granularity | Post-Break Warm-Up Period | Min Data for Reclassification |
|---|---|---|
| Daily | 30 days post-break | 56 days post-break |
| Weekly | 8 weeks post-break | 8 weeks post-break |
| Monthly | 3 months post-break | 2 months post-break |
| Quarterly | 1 quarter post-break | 1 quarter post-break |
| Yearly | 1 year post-break | 1 year post-break |

- During warm-up: Use Cold Start / New Launch model on post-break data
- After warm-up: Reclassify using post-break data only

#### 5.3 Feature Engineering
- Break point date as feature
- Periods since break as feature
- Pre-break level vs post-break level ratio
- Cause of break flag (if known): distribution, pricing, competitor, regulatory

### 6. Model Families

#### 6.1 ML: LightGBM trained on post-break data only after warm-up
#### 6.2 DL: Not applicable during warm-up; TFT after sufficient post-break history
#### 6.3 Statistical: Piecewise regression on pre/post-break periods for detection; ETS on post-break data for forecasting

**Break Point Detection Formula (Chow Test):**
```
F = [(RSS_total − RSS_1 − RSS_2) / k] / [(RSS_1 + RSS_2) / (n − 2k)]
where RSS = residual sum of squares
      k = number of parameters
      n = total observations
F > F_critical (p < 0.05) → structural break confirmed
```

#### 6.4 Fallback: Post-break rolling mean during warm-up period

### 7. Ensemble
- During warm-up: Analogue-only (similar to Cold Start)
- Post warm-up: Standard ensemble for reclassified behavior segment

### 8. Uncertainty Quantification
- Wider intervals during warm-up: [P5, P50, P95]
- Standard intervals post reclassification: [P10, P50, P90]

### 9. Business Rules
- Non-negativity: max(0, forecast)
- Training data hard cutoff: Only post-break data used after break confirmed
- Manual overrides: Cause of break input by commercial team; expected new level input

### 10. Evaluation

| Granularity | Break Detection Lag Target | Post-Break WMAPE |
|---|---|---|
| Daily | Detect within 14 days | < 30% during warm-up |
| Weekly | Detect within 3 weeks | < 25% during warm-up |
| Monthly | Detect within 2 months | < 20% during warm-up |
| Quarterly | Detect within 1 quarter | < 18% during warm-up |
| Yearly | Detect within 1 year | < 15% during warm-up |

### 11. Exception Handling
- Alert: Break detected → immediate planner notification with pre/post level comparison
- False positive monitoring: Track break detections that revert — tune test sensitivity

### 12. Reclassification
- After warm-up: Automatic reclassification to appropriate behavior segment using post-break data
- No holding period — reclassification is the exit from Step Change

### 13. Review Cadence
- Daily break scan on all SKUs; immediate alert on detection; monthly false-positive review

---

## B7 · Pulsed

### 1. Definition
Predicts demand for SKUs with regular inter-arrival intervals and consistent quantities, where demand arrives in predictable bulk pulses — typically driven by periodic ordering behavior rather than underlying consumption patterns.

### 2. Detailed Description
- **Applicable scenarios:** B2B periodic procurement, regular bulk orders, contract call-offs, distributor stocking orders
- **Boundaries:**

| Granularity | ADI Threshold | CV² Threshold | Inter-Arrival CV |
|---|---|---|---|
| Daily | ADI ≥ 1.10 | CV² < 0.49 | CV_arrival < 0.30 |
| Weekly | ADI ≥ 1.32 | CV² < 0.49 | CV_arrival < 0.30 |
| Monthly | ADI ≥ 1.25 | CV² < 0.49 | CV_arrival < 0.30 |
| Quarterly | ADI ≥ 1.20 | CV² < 0.49 | CV_arrival < 0.30 |
| Yearly | ADI ≥ 1.10 | CV² < 0.49 | CV_arrival < 0.30 |

- **Key demand characteristics:** Regular timing, consistent quantity, predictable bulk arrivals, gaps between orders are expected
- **Differentiation:** Unlike Intermittent, inter-arrival intervals are regular (CV_arrival < 0.30); unlike Stable, demand does not occur every period; unlike Lumpy, quantity variance is low

### 3. Business Impact
- **Primary risk (over-forecast):** Stock build between pulse events
- **Primary risk (under-forecast):** Shortage when pulse arrives — often large quantity impact
- **Strategic importance:** High in B2B — pulse timing is the critical forecast dimension

### 4. Priority Level
🟠 Tier 2 — Timing accuracy is more important than quantity accuracy for this segment.

### 5. Model Strategy Overview

#### 5.1 Hurdle (Timing Model)
- Primary task: Predict when next pulse will occur
- Threshold: P(pulse in period t) > 0.50
- Classifier: Logistic Regression on inter-arrival time features
- Quantity model: Rolling non-zero mean (quantity is stable — low CV²)

#### 5.2 Analogue Logic
- k = 3 (pulsed SKUs from same customer or category)
- Similarity: Inter-arrival mean ±1 period, CV² ±0.1, customer type

#### 5.3 Feature Engineering

| Granularity | Timing Features | Quantity Features |
|---|---|---|
| Daily | Days since last pulse, mean inter-arrival (days), CV_arrival, day of week of pulses | Non-zero mean (90-day), quantity trend |
| Weekly | Weeks since last pulse, mean inter-arrival (weeks), CV_arrival, week of month pattern | Non-zero mean (13-week) |
| Monthly | Months since last pulse, mean inter-arrival (months), contract renewal flag | Non-zero mean (6-month) |
| Quarterly | Quarters since last pulse, mean inter-arrival | Non-zero mean |
| Yearly | Years since last pulse | Non-zero mean |

### 6. Model Families

#### 6.1 ML: Two-stage — Logistic Regression (timing) + Rolling Mean (quantity)
#### 6.2 DL: DeepAR — handles periodic patterns with zero inflation

| Granularity | Lookback | Features |
|---|---|---|
| Daily | 180 days | 8 |
| Weekly | 52 weeks | 8 |
| Monthly | 24 months | 6 |
| Quarterly | 8 quarters | 5 |
| Yearly | 5 years | 4 |

#### 6.3 Statistical: Croston with low α (stable inter-arrival exploitation)

| Granularity | α_z | α_p |
|---|---|---|
| Daily | 0.05 | 0.05 |
| Weekly | 0.05 | 0.05 |
| Monthly | 0.10 | 0.10 |
| Quarterly | 0.10 | 0.10 |
| Yearly | 0.15 | 0.15 |

#### 6.4 Fallback: Historical occurrence rate × historical non-zero mean

### 7. Ensemble

| Events in History | Logistic+Mean | Croston | DeepAR |
|---|---|---|---|
| < 8 events | 20% | 80% | 0% |
| 8–20 events | 60% | 40% | 0% |
| > 20 events | 50% | 25% | 25% |

### 8. Uncertainty Quantification
- [P10, P50, P90] — narrower than Intermittent due to regular timing
- Primary uncertainty: Timing of pulse (±1–2 periods); quantity uncertainty is low

### 9. Business Rules
- Forecast = 0 outside predicted pulse window (P(pulse) < 0.50)
- Pulse window: Center on predicted timing ± half inter-arrival std

### 10. Evaluation

| Granularity | Timing Accuracy Target | Quantity MAE | Bias Alert |
|---|---|---|---|
| Daily | Pulse predicted within ±3 days | < 15% of non-zero mean | \|Bias\| > 10% |
| Weekly | Pulse predicted within ±1 week | < 15% | \|Bias\| > 10% |
| Monthly | Pulse predicted within ±1 month | < 12% | \|Bias\| > 8% |
| Quarterly | Pulse predicted within ±1 quarter | < 12% | \|Bias\| > 8% |
| Yearly | Pulse predicted within ±1 year | < 10% | \|Bias\| > 6% |

### 11. Exception Handling
- Alert: Pulse expected but not arrived within 2× mean inter-arrival — check supply and customer status
- Alert: Inter-arrival CV rises above 0.30 for 5 events → reclassify to Intermittent

### 12. Reclassification

| Condition | Target | Holding Period |
|---|---|---|
| CV_arrival rises above 0.30 for 5 events | Intermittent | 5 events |
| CV² rises above 0.49 | Lumpy | 8 periods |
| ADI drops below threshold for 8 periods | Stable | 8 periods |

### 13. Review Cadence
- Per pulse event review; monthly pulsed portfolio review; quarterly full re-evaluation

---

## B8 · Slow Mover

### 1. Definition
Predicts demand for SKUs with regular demand frequency and low variance (same CV²-ADI quadrant as Stable) but with absolute volume below the 5th portfolio percentile, where low volume creates amplified percentage error and specialist treatment improves inventory efficiency.

### 2. Detailed Description
- **Applicable scenarios:** Long-tail SKUs, niche variants, regional specialties, low-volume B2B lines
- **Boundaries:**

| Granularity | ADI Threshold | CV² Threshold | Volume |
|---|---|---|---|
| Daily | ADI < 1.10 | CV² < 0.49 | < 5th percentile of portfolio daily means |
| Weekly | ADI < 1.32 | CV² < 0.49 | < 5th percentile of portfolio weekly means |
| Monthly | ADI < 1.25 | CV² < 0.49 | < 5th percentile of portfolio monthly means |
| Quarterly | ADI < 1.20 | CV² < 0.49 | < 5th percentile of portfolio quarterly means |
| Yearly | ADI < 1.10 | CV² < 0.49 | < 5th percentile of portfolio yearly means |

- **Key demand characteristics:** Regular but very low volume, stable pattern, high MAPE due to low absolute values
- **Differentiation:** Unlike Stable, volume is very low — MAPE is unreliable; unlike Intermittent, frequency is high; like Stable in behavior but different in volume tier

### 3. Business Impact
- **Primary risk (over-forecast):** Small absolute overstock but high relative cost — write-off on low-value lines
- **Primary risk (under-forecast):** Stockout on niche lines — long tail customers are disproportionately loyal
- **Strategic importance:** Low-medium — individually small but collectively significant (long tail effect)

### 4. Priority Level
🟡 Tier 3 — Low individual impact but high portfolio count — automation is key.

### 5. Model Strategy Overview

#### 5.1 Hurdle
- Threshold: P(demand > 0) > 0.80 — slow movers demand regularly but in small quantities
- Regressor: Simple statistical models preferred — ML overfits on low-volume data

#### 5.2 Analogue Logic
- k = 5 (similar low-volume SKUs from same subcategory)
- Pool analogues for cross-learning — critical for sparse data

#### 5.3 Feature Engineering

| Granularity | Features | Notes |
|---|---|---|
| Daily | 7, 30, 90-day rolling mean, holiday flag, day of week | Minimal features — prevent overfitting |
| Weekly | 4, 8, 13-week rolling mean, holiday flag | Simple feature set |
| Monthly | 2, 3, 6-month rolling mean, seasonal flag | Seasonal index important |
| Quarterly | 1, 2, 4-quarter rolling mean | Minimal |
| Yearly | 1, 2-year rolling mean | Long-cycle only |

### 6. Model Families

#### 6.1 ML: LightGBM (simple, regularised heavily to prevent overfit)
- Objective: reg:absoluteerror (MAE preferred over RMSE for low volume)
- Max depth: 3; num_leaves: 15; min_data_in_leaf: 5 (prevent overfit)
- When to use: When portfolio is large enough for cross-SKU learning

#### 6.2 DL: Not recommended — insufficient signal for deep learning

#### 6.3 Statistical: ETS(A,N,A) or Theta method

| Granularity | Model | Reason |
|---|---|---|
| Daily | Theta with period = 7 | Handles low volume well |
| Weekly | ETS(A,N,A) period = 52 | Captures annual seasonality |
| Monthly | Theta or ETS(A,N,A) period = 12 | Reliable on low volume |
| Quarterly | ETS(A,N,N) | No seasonality at quarterly |
| Yearly | Simple moving average (3-year) | Minimal complexity |

#### 6.4 Fallback: 3-period moving average; alert if fallback > 20%

### 7. Ensemble

| History | LightGBM | ETS / Theta |
|---|---|---|
| Up to 1 year equiv. | 30% | 70% |
| > 1 year equiv. | 50% | 50% |

### 8. Uncertainty Quantification
- Method: Bootstrap on historical residuals (simple, works on small samples)
- Output: [P10, P50, P90]
- Use case: Min/max stock policy — often binary (stock or not stock decision)

### 9. Business Rules
- Non-negativity: max(0, forecast)
- Minimum forecast: Consider rounding to nearest whole unit
- Stockout cost vs holding cost assessment: For very low volume, safety stock = 1 unit may suffice
- Manual overrides: Range rationalisation decisions; customer-specific demand alerts

### 10. Evaluation

| Granularity | Primary Metric | WMAPE Note | Bias Alert |
|---|---|---|---|
| Daily | MAE (not WMAPE — too noisy) | WMAPE unreliable at low volume | \|Bias\| > 20% |
| Weekly | MAE | WMAPE unreliable | \|Bias\| > 20% |
| Monthly | MAE + MASE | MASE reliable here | \|Bias\| > 15% |
| Quarterly | MAE + MASE | MASE reliable | \|Bias\| > 12% |
| Yearly | MAE + MASE | MASE reliable | \|Bias\| > 10% |

- **Note:** MASE preferred over MAPE/WMAPE for slow movers — MAPE inflates on near-zero actuals

### 11. Exception Handling
- Alert: Volume rises above 5th percentile for 8 periods → reclassify to Stable

### 12. Reclassification

| Condition | Target | Holding Period |
|---|---|---|
| Volume rises above 5th percentile for 8 periods | Stable | 8 periods |
| ADI rises above threshold for 8 periods | Intermittent | 8 periods |
| CV² rises above 0.49 for 8 periods | Erratic | 8 periods |

### 13. Review Cadence
- Monthly automated — low individual priority; quarterly portfolio-level slow mover review; annual range rationalisation input

---

*End of Dimension 2 · Behavior Pattern*
*8 Segments Complete · B1 through B8*
