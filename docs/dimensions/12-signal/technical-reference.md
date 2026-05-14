# PART 0 — FORMULA & THRESHOLD REFERENCE

## Dimension 12 · Signal Pattern

---

---

## 0.1 Core Segmentation Metrics

### A. Signal-to-Noise Ratio (SNR)
> Measures how much of demand variance is true signal vs random noise

```
STL decomposition:
  d(t) = Trend(t) + Seasonal(t) + Remainder(t)

Signal component: Signal(t) = Trend(t) + Seasonal(t)
Noise component:  Noise(t) = Remainder(t)

SNR = Var(Signal) / Var(Noise)

SNR > 4.0 → Pure Signal  (noise < 20% of total variance)
SNR 1.0–4.0 → Moderate noise
SNR < 1.0 → Noisy  (noise > 50% of total variance)
```

| Granularity | STL Window | Min History for STL | Pure Signal | Noisy |
|---|---|---|---|---|
| **Daily** | Seasonal period = 7 or 365 | ≥ 365 days | SNR > 4.0 | SNR < 1.0 |
| **Weekly** | Seasonal period = 52 | ≥ 104 weeks | SNR > 4.0 | SNR < 1.0 |
| **Monthly** | Seasonal period = 12 | ≥ 24 months | SNR > 4.0 | SNR < 1.0 |
| **Quarterly** | Seasonal period = 4 | ≥ 8 quarters | SNR > 3.0 | SNR < 0.8 |
| **Yearly** | No seasonal | ≥ 5 years | SNR > 2.0 | SNR < 0.5 |

---

### B. Distortion Index (DI)
> Measures systematic difference between observed and true demand

```
Distortion Index:
  DI(t) = |d_observed(t) − d_true_estimate(t)| / d_true_estimate(t)

d_true_estimate options:
  1. Fill rate adjustment: d_true = d_observed / Fill_Rate(t)
  2. Pre-distortion rolling mean (if distortion dates known)
  3. Category index proxy: d_true = d_observed × (Category_growth / SKU_growth_pre_distortion)

Distorted: DI > 0.15 in > 20% of periods
Pure:      DI < 0.10 in > 90% of periods
```

| Granularity | Distortion Threshold | Pure Threshold | Computation Window |
|---|---|---|---|
| **Daily** | DI > 0.15 in > 20% of days | DI < 0.10 in > 90% of days | 90-day rolling |
| **Weekly** | DI > 0.15 in > 20% of weeks | DI < 0.10 in > 90% of weeks | 52-week rolling |
| **Monthly** | DI > 0.15 in > 20% of months | DI < 0.10 in > 90% of months | 24-month rolling |
| **Quarterly** | DI > 0.15 in > 20% of quarters | DI < 0.10 in > 90% of quarters | 8-quarter rolling |
| **Yearly** | DI > 0.15 in > 20% of years | DI < 0.10 in > 90% of years | 3-year rolling |

---

### C. Bullwhip Amplification Ratio (AR)
> Measures how much upstream order variance exceeds downstream demand variance

```
Amplification Ratio:
  AR = Var(Orders_upstream) / Var(d_downstream)

AR > 1.5 → Amplified signal (upstream orders much more variable than true demand)
AR 1.2–1.5 → Mild amplification
AR < 1.2 → Clean signal (minimal amplification)

De-amplification smoothing factor:
  α_deamp = 2 / (AR + 1)   [derived from AR]
  Higher AR → lower α → more smoothing required
```

| Granularity | AR Estimation Window | Amplified Threshold | Clean Threshold |
|---|---|---|---|
| **Daily** | 90-day rolling | AR > 1.5 | AR < 1.2 |
| **Weekly** | 52-week rolling | AR > 1.5 | AR < 1.2 |
| **Monthly** | 24-month rolling | AR > 1.5 | AR < 1.2 |
| **Quarterly** | 8-quarter rolling | AR > 1.5 | AR < 1.2 |
| **Yearly** | 3-year rolling | AR > 1.5 | AR < 1.2 |

---

### D. Signal Lag
> Measures systematic delay between observed orders and true consumption

```
Signal lag estimation:
  L = argmax CCF(d_observed, d_consumption)   for k = 0 to H
  where d_consumption = POS/consumption data (if available)

Signal lag confirmed: L > granularity threshold AND |CCF(L)| > 2/√n

Alternative (no consumption data):
  Estimate L from order-to-shipment-to-consumption pipeline:
  L = order_lead_time + transit_time + customer_hold_time
```

| Granularity | Lagged Signal Threshold | Estimation Method |
|---|---|---|
| **Daily** | L > 3 days | CCF vs POS; or supply chain pipeline L |
| **Weekly** | L > 1 week | CCF vs POS; or pipeline L |
| **Monthly** | L > 1 month | CCF vs consumption data; or pipeline |
| **Quarterly** | L > 1 quarter | Pipeline estimation |
| **Yearly** | L > 6 months | Pipeline estimation |

---

## 0.2 Signal Classification Decision Rules

```
STEP 1: Check for supply constraint or reporting issues
  Stockout events > threshold → FLAG as Distorted (supply constraint)
  Returns > 10% of gross demand → FLAG as Distorted (returns)
  Reporting gaps > 5% of periods → FLAG as Distorted (data quality)

STEP 2: Compute SNR via STL decomposition
  SNR > 4.0 → Pure Signal candidate (proceed to STEP 3)
  SNR < 1.0 → Noisy

STEP 3: Compute DI (if distortion suspected)
  DI > 0.15 in > 20% periods → Distorted
  DI < 0.10 in > 90% periods → Pure Signal confirmed

STEP 4: Compute AR (if upstream order data available)
  AR > 1.5 → Amplified

STEP 5: Estimate signal lag L (if POS or consumption data available)
  L > granularity threshold → Lagged Signal

STEP 6: Default
  No issues detected → Pure Signal
```

---

## 0.3 Noise Reduction Methods

```
Hodrick-Prescott (HP) Filter:
  min_τ Σ(d_t − τ_t)² + λ × Σ(Δ²τ_t)²
  Daily: λ = 1,600 | Weekly: λ = 6,760 | Monthly: λ = 1,600
  Quarterly: λ = 1,600 | Yearly: λ = 6.25

Kalman Filter State Space:
  State:       α(t) = T × α(t-1) + R × η(t)   η ~ N(0,Q)
  Observation: d(t) = Z × α(t) + ε(t)          ε ~ N(0,H)
  H >> Q → noisy observations; smooth state estimated from noisy signal

Wavelet Denoising:
  Decompose d(t) into wavelet coefficients
  Threshold small coefficients (noise)
  Reconstruct from thresholded coefficients
```

---

## 0.4 Rolling Window Reference

| Window | Daily | Weekly | Monthly | Quarterly | Yearly |
|---|---|---|---|---|---|
| Short | 7 days | 4 weeks | 2 months | 1 quarter | 1 year |
| Medium | 30 days | 8 weeks | 3 months | 2 quarters | 2 years |
| Long | 90 days | 13 weeks | 6 months | 3 quarters | 3 years |
| Extended | 180 days | 26 weeks | 12 months | 4 quarters | 4 years |
| DL Lookback | 180 days | 52 weeks | 24 months | 8 quarters | 5 years |

---

## 0.5 Accuracy Metrics

```
WMAPE   = Σ|Forecast_t − Actual_t| / Σ Actual_t × 100
Bias    = Σ(Forecast_t − Actual_t) / Σ Actual_t × 100
MAE     = (1/n) × Σ|Forecast_t − Actual_t|

Signal-specific metrics:
  SNR Post-Correction   (Target > 2.0 after noise reduction)
  DI Post-Correction    (Target < 0.10 after distortion removal)
  AR Post-De-amplification (Target < 1.2 after de-amplification)
  Downstream Alignment  = r(corrected_forecast, POS_actuals)  (Target > 0.70)
  Overfitting Check     = Validation WMAPE / Train WMAPE  (Target < 1.20)
```

---

## 0.6 Retraining & Backtesting Reference

| Granularity | Retraining | Latency | Train | Test |
|---|---|---|---|---|
| **Daily** | Daily | T+4 hours | 180 days | 30 days |
| **Weekly** | Weekly | T+1 day | 52 weeks | 13 weeks |
| **Monthly** | Monthly | T+2 days | 24 months | 6 months |
| **Quarterly** | Quarterly | T+3 days | 8 quarters | 2 quarters |
| **Yearly** | Annually | T+7 days | All available | 1 year |

---
