# PART 0 — FORMULA & THRESHOLD REFERENCE
## Trend Pattern Specific

---

## 0.1 Core Segmentation Metrics

### A. Linear Slope — OLS Regression
> Measures the average directional change in demand per period

**General Formula:**
```
slope β₁ = Σ[(t − t̄)(d_t − d̄)] / Σ[(t − t̄)²]
intercept β₀ = d̄ − β₁ × t̄

t = time index (1, 2, 3, ... n)
d_t = demand at time t
d̄ = mean demand over window
t̄ = mean time index over window

Trend line: D̂(t) = β₀ + β₁ × t
β₁ > 0 → upward trend
β₁ < 0 → downward trend
β₁ ≈ 0 → flat (no trend)
```

| Granularity | Rolling Window | Slope Unit | Min Obs |
|---|---|---|---|
| **Daily** | 90-day | Units/day | ≥ 56 days |
| **Weekly** | 13-week | Units/week | ≥ 8 weeks |
| **Monthly** | 6-month | Units/month | ≥ 4 months |
| **Quarterly** | 4-quarter | Units/quarter | ≥ 2 quarters |
| **Yearly** | 3-year | Units/year | ≥ 2 years |

---

### B. Mann-Kendall Trend Test
> Non-parametric test for monotonic trend — robust to outliers and non-normality

**General Formula:**
```
S = Σ_{j>i} sign(d_j − d_i)
where sign(x) = +1 if x > 0; 0 if x = 0; −1 if x < 0

Variance: Var(S) = n(n−1)(2n+5) / 18
Z-statistic: Z = (S−1)/√Var(S) if S > 0
             Z = 0             if S = 0
             Z = (S+1)/√Var(S) if S < 0

p-value from standard normal distribution
Significant trend: p < 0.05
No trend:          p ≥ 0.10
Watch zone:        0.05 ≤ p < 0.10 → monitor 2 more periods
```

| Granularity | Rolling Window | Significance | Direction |
|---|---|---|---|
| **Daily** | 90-day | p < 0.05 | Z > 0 → Up; Z < 0 → Down |
| **Weekly** | 13-week | p < 0.05 | Z > 0 → Up; Z < 0 → Down |
| **Monthly** | 6-month | p < 0.05 | Z > 0 → Up; Z < 0 → Down |
| **Quarterly** | 4-quarter | p < 0.05 | Z > 0 → Up; Z < 0 → Down |
| **Yearly** | 3-year | p < 0.05 | Z > 0 → Up; Z < 0 → Down |

---

### C. Slope Magnitude Classification
> Classifies trend strength relative to mean demand level

**Formula:**
```
Relative Slope = |β₁| / μ_demand × 100   (% change per period)

Mild trend:     Relative Slope < 2% per period
Moderate trend: 2% ≤ Relative Slope < 5% per period
Strong trend:   Relative Slope ≥ 5% per period
```

| Granularity | Mild | Moderate | Strong |
|---|---|---|---|
| **Daily** | < 2%/day | 2–5%/day | > 5%/day |
| **Weekly** | < 2%/week | 2–5%/week | > 5%/week |
| **Monthly** | < 2%/month | 2–5%/month | > 5%/month |
| **Quarterly** | < 2%/quarter | 2–5%/quarter | > 5%/quarter |
| **Yearly** | < 2%/year | 2–5%/year | > 5%/year |

---

### D. Cyclical Trend Detection
> Identifies long-wave cycles beyond seasonal frequency

**Formula:**
```
Deseasonalised series: d_adj(t) = d(t) / SI(period_t)
Detrended series:      d_dt(t) = d_adj(t) − (β₀ + β₁ × t)
Cycle detection:       FFT on d_dt(t) — look for peaks at periods > 2 × seasonal period
Cycle period:          T_cycle = 1 / f_peak (from FFT)
Significant cycle:     Amplitude > 10% of mean demand AND T_cycle > 2 × primary seasonal period

Cyclical trend condition: Significant cycle detected on detrended, deseasonalised series
```

| Granularity | Min Cycle Period | Max Cycle Period | Min Obs for Detection |
|---|---|---|---|
| **Daily** | > 14 days | < 3 years | ≥ 2 full cycles |
| **Weekly** | > 8 weeks | < 3 years | ≥ 2 full cycles |
| **Monthly** | > 6 months | < 5 years | ≥ 2 full cycles |
| **Quarterly** | > 2 quarters | < 5 years | ≥ 2 full cycles |
| **Yearly** | > 2 years | < 10 years | ≥ 2 full cycles |

---

### E. Mean Reversion Detection
> Identifies demand series that deviate then return to a stable long-run mean

**Formula:**
```
Long-run mean:  μ_LR = mean over extended window (full available history)
Deviation:      dev(t) = d(t) − μ_LR
Reversion test: Augmented Dickey-Fuller (ADF) test on dev(t)
                ADF p < 0.05 → stationary (mean-reverting)
                ADF p ≥ 0.05 → non-stationary (not mean-reverting)

Half-life of reversion:
  Regress Δdev(t) = α × dev(t−1) + ε(t)
  Half-life = −ln(2) / α   (α must be negative for reversion)
```

| Granularity | Extended Window | ADF Threshold | Min Obs |
|---|---|---|---|
| **Daily** | 365 days | p < 0.05 | ≥ 180 days |
| **Weekly** | 52 weeks | p < 0.05 | ≥ 52 weeks |
| **Monthly** | 24 months | p < 0.05 | ≥ 24 months |
| **Quarterly** | 8 quarters | p < 0.05 | ≥ 8 quarters |
| **Yearly** | 5 years | p < 0.05 | ≥ 5 years |

---

## 0.2 Trend Classification Decision Rules

```
STEP 1: Deseasonalise the series (remove seasonal component if Seasonal driver detected)
STEP 2: Run Mann-Kendall test on rolling window (granularity-specific)
STEP 3: Apply classification rules

  Mann-Kendall p < 0.05 AND Z > 0 → Upward Trend
  Mann-Kendall p < 0.05 AND Z < 0 → Downward Trend
  Mann-Kendall p ≥ 0.10            → proceed to STEP 4

STEP 4 (flat or ambiguous): Run ADF test for mean reversion
  ADF p < 0.05 → Reverting
  ADF p ≥ 0.05 → proceed to STEP 5

STEP 5 (not reverting): Run FFT on detrended, deseasonalised series
  Significant cycle detected → Cyclical Trend
  No cycle detected         → Flat

Watch zone (0.05 ≤ p < 0.10): Hold current classification; re-test next 2 periods
```

---

## 0.3 Damping Factor Reference (for Downward Trend)

| Granularity | Mild Downward | Moderate Downward | Strong Downward |
|---|---|---|---|
| **Daily** | phi = 0.95 | phi = 0.90 | phi = 0.85 |
| **Weekly** | phi = 0.90 | phi = 0.85 | phi = 0.80 |
| **Monthly** | phi = 0.85 | phi = 0.80 | phi = 0.75 |
| **Quarterly** | phi = 0.80 | phi = 0.75 | phi = 0.70 |
| **Yearly** | phi = 0.75 | phi = 0.70 | phi = 0.65 |

**Damped Trend Formula:**
```
F(t+h) = l_t + (phi + phi² + ... + phi^h) × b_t
where l_t = level; b_t = trend; phi = damping factor
phi = 1.0 → no damping (pure trend extrapolation)
phi < 1.0 → trend fades over horizon; phi = 0 → pure level forecast
```

---

## 0.4 Rolling Window Reference

| Window Name | Daily | Weekly | Monthly | Quarterly | Yearly |
|---|---|---|---|---|---|
| **Short** | 7 days | 4 weeks | 2 months | 1 quarter | 1 year |
| **Medium** | 30 days | 8 weeks | 3 months | 2 quarters | 2 years |
| **Long** | 90 days | 13 weeks | 6 months | 3 quarters | 3 years |
| **Extended** | 180 days | 26 weeks | 12 months | 4 quarters | 4 years |
| **Full Year** | 365 days | 52 weeks | 12 months | 4 quarters | 5 years |
| **DL Lookback** | 180 days | 52 weeks | 24 months | 8 quarters | 5 years |

---

## 0.5 Accuracy Metric Formulas

```
WMAPE   = Σ|Forecast_t − Actual_t| / Σ Actual_t × 100
Bias    = Σ(Forecast_t − Actual_t) / Σ Actual_t × 100
MAE     = (1/n) × Σ|Forecast_t − Actual_t|
RMSE    = sqrt[(1/n) × Σ(Forecast_t − Actual_t)²]

Directional Bias (critical for trend segments):
  Upward trend: Bias < 0 (under-forecast) is the primary risk → alert if Bias < −10%
  Downward trend: Bias > 0 (over-forecast) is the primary risk → alert if Bias > +10%

Trend Tracking Signal:
  TS(t) = Σ(Forecast_t − Actual_t) / MAE
  |TS| > 4 → forecast systematically biased → reforecast required

Pinball Loss:
  Pinball(α,t) = α × (Actual_t − Q_α)     if Actual_t ≥ Q_α
               = (1−α) × (Q_α − Actual_t)  if Actual_t < Q_α
Coverage = Actuals within [P10, P90] / n × 100  (Target: 80%)
```

---

## 0.6 Retraining & Backtesting Reference

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

