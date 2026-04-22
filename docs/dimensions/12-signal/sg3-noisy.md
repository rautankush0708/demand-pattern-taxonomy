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
| Daily | < 25% | SNR > 2.0 | Validation WMAPE < Train × 1.20 | \|Bias\| > 12% |
| Weekly | < 22% | SNR > 2.0 | Validation < Train × 1.20 | \|Bias\| > 10% |
| Monthly | < 18% | SNR > 2.0 | Validation < Train × 1.20 | \|Bias\| > 8% |
| Quarterly | < 15% | SNR > 2.0 | Validation < Train × 1.20 | \|Bias\| > 6% |
| Yearly | < 12% | SNR > 2.0 | Validation < Train × 1.20 | \|Bias\| > 5% |

---
