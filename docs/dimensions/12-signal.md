# Dimension 12 · Signal Pattern
## Demand Forecasting Model Templates

---

> **Segments:** 5 · Pure Signal · Distorted · Noisy · Lagged · Amplified
> **Granularities:** Daily · Weekly · Monthly · Quarterly · Yearly

---

## 0.4 Signal Pattern Metrics

### A. Signal Noise Ratio
```
Signal-to-Noise Ratio (SNR):
  Signal component: Trend + Seasonal = fitted values from STL decomposition
  Noise component:  Residual from STL decomposition

  SNR = Var(Signal) / Var(Noise)
  SNR > 4.0 → Pure Signal (noise < 20% of total variance)
  SNR 1.0–4.0 → Moderate noise
  SNR < 1.0 → Noisy (noise > 50% of total variance)
```

### B. Distortion Detection
```
Distortion factors: Supply constraints, returns, order cancellations, reporting errors
Distortion index: DI = |d_observed(t) − d_true_estimate(t)| / d_true_estimate(t)

Distorted: DI > 0.15 in > 20% of periods
Pure: DI < 0.10 in > 90% of periods

d_true_estimate(t) = unconstrained demand
```

### C. Bullwhip Amplification
```
Bullwhip effect: Order variance amplifies upstream from retail to distributor to manufacturer

Amplification ratio: AR = Var(Orders_upstream) / Var(Orders_downstream)
AR > 1.5 → Amplified signal (upstream orders more variable than downstream demand)
AR < 1.2 → Clean signal (minimal amplification)
```

### D. Lag Between Signal and Consumption
```
Signal lag: L = t_order − t_consumption (periods between order and actual use)

Lagged Signal: Mean(L) > granularity threshold
  Daily: L > 3 days
  Weekly: L > 1 week
  Monthly: L > 1 month
  Quarterly: L > 1 quarter
  Yearly: L > 6 months
```

---

# PART 1 — SEGMENT TEMPLATES

## SG1 · Pure Signal

### 1. Definition
Predicts demand for SKUs where the observed demand series accurately reflects true underlying consumption (SNR > 4.0; DI < 0.10), enabling direct application of statistical and ML models without pre-processing corrections.

### 5. Model Strategy
- Standard behavior model per segment — no signal correction required
- Signal quality monitoring: Monthly SNR check; alert if SNR drops below 2.0

### Evaluation — Standard per Behavior segment; add SNR as monitoring metric

---

## SG2 · Distorted

### 1. Definition
Predicts demand for SKUs where observed demand is systematically inflated or deflated by external factors unrelated to true consumption (DI > 0.15 in > 20% of periods), requiring distortion identification, correction, and unconstrained demand reconstruction before modelling.

### 5. Model Strategy

#### 5.1 Distortion Correction Pipeline
```
STEP 1: Identify distortion source
  Sources: Supply stockouts, returns inflation, reporting errors, order cancellations, double-counting

STEP 2: Estimate distortion magnitude
  d_true(t) = d_observed(t) / distortion_factor(t)
  distortion_factor(t) = 1 + (distortion_magnitude × distortion_indicator(t))

STEP 3: Replace distorted periods
  Use corrected demand d_true(t) for all model training and feature computation

STEP 4: Apply standard behavior model to corrected series
```

| Distortion Type | Correction Method |
|---|---|
| Supply stockout | Fill rate adjustment |
| Returns inflation | Subtract gross returns from gross demand |
| Reporting error | Replace with interpolated adjacent periods |
| Order cancellation | Adjust with confirmed net demand |
| Double counting | Identify and remove duplicate transactions |

### 6. Model Families
- Post-correction: Standard behavior model per segment
- Pre-correction: Distortion detection model (anomaly detection — Isolation Forest or CUSUM)

### Evaluation

| Granularity | Distortion Detection Rate | Post-Correction WMAPE | Correction Accuracy | Bias Alert |
|---|---|---|---|---|
| Daily | > 85% | Per behavior standard | DI < 0.10 post-correction | |Bias| > 10% |
| Weekly | > 85% | Per behavior standard | DI < 0.10 | |Bias| > 8% |
| Monthly | > 85% | Per behavior standard | DI < 0.10 | |Bias| > 7% |
| Quarterly | > 80% | Per behavior standard | DI < 0.10 | |Bias| > 6% |
| Yearly | > 80% | Per behavior standard | DI < 0.10 | |Bias| > 5% |

---

## SG3 · Noisy

### 1. Definition
Predicts demand for SKUs where true demand signal is heavily masked by random variation (SNR < 1.0), requiring noise reduction pre-processing and robust low-sensitivity models that do not overfit to noise.

### 5. Model Strategy

#### 5.1 Noise Reduction Pipeline
```
STEP 1: Decompose series via STL (Seasonal and Trend decomposition using Loess)
  d(t) = Trend(t) + Seasonal(t) + Remainder(t)
  Remainder = noise component

STEP 2: Apply smoothing to remainder
  Options: Hodrick-Prescott filter, Wavelet denoising, Kalman filter

STEP 3: Reconstruct cleaned series
  d_clean(t) = Trend(t) + Seasonal(t) + Smoothed_Remainder(t)

STEP 4: Apply model to d_clean(t); prediction intervals widen to account for noise
```

**HP Filter:**
```
min_τ Σ(d_t − τ_t)² + λ × Σ(Δ²τ_t)²
λ controls smoothness:
  Daily:     λ = 1,600
  Weekly:    λ = 6,760
  Monthly:   λ = 1,600
  Quarterly: λ = 1,600
  Yearly:    λ = 6.25
```

### 6. Model Families

#### 6.1 ML: LightGBM on smoothed series; max_depth = 3 (prevent overfitting noise)
#### 6.2 DL: Not recommended — DL overfits to noise easily; use only with heavy dropout
#### 6.3 Statistical: Structural time series (Kalman filter) — naturally handles noisy signals

**Kalman Filter State Space Model:**
```
State equation:   α(t) = T × α(t-1) + R × η(t)   η ~ N(0, Q)
Observation:      d(t) = Z × α(t) + ε(t)          ε ~ N(0, H)
H >> Q → noisy observations; state estimated smoothly from noisy signal
```

### Evaluation

| Granularity | WMAPE (on smoothed) | SNR Post-Smoothing | Overfitting Check | Bias Alert |
|---|---|---|---|---|
| Daily | < 25% | SNR > 2.0 | Validation WMAPE < Train × 1.20 | |Bias| > 12% |
| Weekly | < 22% | SNR > 2.0 | Validation < Train × 1.20 | |Bias| > 10% |
| Monthly | < 18% | SNR > 2.0 | Validation < Train × 1.20 | |Bias| > 8% |
| Quarterly | < 15% | SNR > 2.0 | Validation < Train × 1.20 | |Bias| > 6% |
| Yearly | < 12% | SNR > 2.0 | Validation < Train × 1.20 | |Bias| > 5% |

---

## SG4 · Lagged Signal

### 1. Definition
Predicts demand for SKUs where the observed demand signal consistently lags true consumption by a known duration (L > granularity threshold), requiring lag correction to align the demand signal with actual consumption timing before modelling.

### 5. Model Strategy

#### 5.1 Signal Lag Correction
```
d_corrected(t) = d_observed(t + L)   [shift observed signal back by lag L]
OR equivalently:
d_true(t) = d_observed(t − L)   [true consumption at t = observed orders at t+L]

Forecast at t for horizon h:
  F_true(t+h) = Model(d_corrected history)
  F_observed(t+h) = F_true(t + h + L)   [shift forecast forward by lag]
```

| Granularity | Lag Estimation | Min Lag Observations |
|---|---|---|
| Daily | Cross-correlation of orders vs POS; Mean(L) estimated | ≥ 30 paired observations |
| Weekly | Order-to-POS lag; Mean(L) in weeks | ≥ 20 paired observations |
| Monthly | Order-to-consumption lag | ≥ 12 paired observations |
| Quarterly | Order-to-use lag | ≥ 8 paired observations |
| Yearly | Long-cycle lag | ≥ 3 paired observations |

### 6. Model Families

#### 6.1 ML: LightGBM on lag-corrected series + lag features
#### 6.2 Statistical: Standard model on corrected series; ARIMAX with lag structure

### Evaluation

| Granularity | Lag Estimate Accuracy | WMAPE on Corrected | Bias Alert |
|---|---|---|---|
| Daily | Lag within ±2 days | Per behavior standard | |Bias| > 8% |
| Weekly | Lag within ±1 week | Per behavior standard | |Bias| > 7% |
| Monthly | Lag within ±1 month | Per behavior standard | |Bias| > 6% |
| Quarterly | Lag within ±1 quarter | Per behavior standard | |Bias| > 5% |
| Yearly | Lag within ±6 months | Per behavior standard | |Bias| > 4% |

---

## SG5 · Amplified

### 1. Definition
Predicts demand for SKUs where the observed upstream order signal is amplified relative to true end-consumer demand due to the bullwhip effect (AR > 1.5), requiring demand sensing correction and end-to-end signal reconstruction to recover true consumption signal.

### 2. Detailed Description
- **Applicable scenarios:** Multi-tier supply chains where distributor or wholesaler ordering amplifies variability; categories with large distributor safety stocks and batch ordering behaviour

### 5. Model Strategy

#### 5.1 Bullwhip De-amplification
```
Amplification Ratio: AR = Var(Orders_upstream) / Var(d_downstream)

De-amplification:
  d_true(t) = d_upstream(t) / AR + (1 − 1/AR) × d_downstream_estimate(t)

If downstream (POS/consumption) data available:
  Use d_downstream directly — highest fidelity signal

If only upstream order data available:
  Apply exponential smoothing to orders: d_smoothed(t) = α × d(t) + (1−α) × d(t-1)
  α = 2 / (AR + 1)   [de-amplification smoothing factor derived from AR]
```

| Granularity | AR Estimation Window | De-amplification Method |
|---|---|---|
| Daily | 90-day rolling | Exponential smoothing + POS comparison |
| Weekly | 52-week rolling | ETS smoothing on orders + POS if available |
| Monthly | 24-month rolling | ARIMA fitted on downstream; orders smoothed |
| Quarterly | 8-quarter rolling | Moving average de-amplification |
| Yearly | 3-year rolling | Long-run average de-amplification |

### 6. Model Families

#### 6.1 ML: LightGBM on de-amplified demand series
#### 6.2 DL: TFT with both upstream and downstream signals (if available)
#### 6.3 Statistical: State space model — observes upstream orders; estimates downstream state

### Evaluation

| Granularity | AR Estimate Accuracy | De-amplified WMAPE | Downstream Alignment | Bias Alert |
|---|---|---|---|---|
| Daily | AR within ±0.3 | < 25% | r(deamplified, POS) > 0.70 | |Bias| > 12% |
| Weekly | AR within ±0.3 | < 22% | r > 0.70 | |Bias| > 10% |
| Monthly | AR within ±0.2 | < 18% | r > 0.65 | |Bias| > 8% |
| Quarterly | AR within ±0.2 | < 15% | r > 0.65 | |Bias| > 6% |
| Yearly | AR within ±0.2 | < 12% | r > 0.60 | |Bias| > 5% |
