# Segment Model Template

## Dimension 12 · Noisy

---

### 1. Definition
Predicts demand for SKUs where the true demand signal is heavily masked by random variation (SNR < 1.0), requiring noise reduction pre-processing and conservative low-complexity models that resist overfitting to noise.

### 2. Detailed Description
- **Applicable scenarios:** Ultra-low volume SKUs with high relative noise, highly fragmented demand across many small customers, categories with large random variation in purchase size, demand series with many one-off anomalies
- **Boundaries:**

| Granularity | SNR Threshold | Min History for Detection |
|---|---|---|
| Daily | SNR < 1.0 (noise > 50% of total variance) | ≥ 90 days |
| Weekly | SNR < 1.0 | ≥ 52 weeks |
| Monthly | SNR < 1.0 | ≥ 12 months |
| Quarterly | SNR < 0.8 | ≥ 4 quarters |
| Yearly | SNR < 0.5 | ≥ 3 years |

- **Key demand characteristics:** High random variation relative to true signal; standard models overfit to noise; simple models outperform complex ones; smoothing is the primary tool
- **Differentiation from other models:** Unlike Distorted (systematic cause), Noisy is random; unlike Pure Signal, true underlying pattern is hidden; unlike Amplified (supply chain cause), noise is at the demand measurement level

### 3. Business Impact
- **Primary risk (over-forecast):** Complex models overfit noise — poor generalisation; erratic forecasts
- **Primary risk (under-forecast):** Suppressing all variation — missing genuine underlying trend or seasonality
- **Strategic importance:** Medium — primary challenge is finding the right level of smoothing; too much smoothing loses signal; too little overfits noise

### 4. Priority Level
🟠 **Tier 2** — Noise reduction is the primary pre-processing step; simple models outperform complex ones here.

### 5. Model Strategy Overview

#### 5.1 Noise Reduction Pipeline
```
STEP 1: STL decomposition
  d(t) = Trend(t) + Seasonal(t) + Remainder(t)
  SNR = Var(Trend + Seasonal) / Var(Remainder)

STEP 2: Apply noise reduction to Remainder
  Option A: HP Filter (smoothing based parameter λ)
  Option B: Kalman Filter (state space smoothing)
  Option C: Wavelet Denoising (threshold small wavelet coefficients)

STEP 3: Reconstruct cleaned series
  d_clean(t) = Trend(t) + Seasonal(t) + Smoothed_Remainder(t)

STEP 4: Apply model to d_clean(t)
  Prediction intervals widened to account for noise floor
```

#### 5.2 Analogue / Similarity Logic
- k = 5 (similar SNR level in same category — cross-pool learning important for noisy SKUs)
- Joint pooled model: Group Noisy SKUs for shared model training — cross-SKU learning reduces individual noise impact

#### 5.3 Feature Engineering
- Minimal feature set — prevent overfitting to noise

| Granularity | Features | Excluded Features | Notes |
|---|---|---|---|
| Daily | 7/30/90-day smoothed rolling mean, seasonal index, holiday flag | High-cardinality features, fine-grained lags | Prevent overfit |
| Weekly | 4/8/13-week smoothed rolling mean, seasonal index | Fine-grained price features | Simple set |
| Monthly | 3/6/12-month smoothed rolling mean, seasonal index | Interaction features | Conservative |
| Quarterly | 2/4-quarter smoothed rolling mean | All fine-grained features | Minimal |
| Yearly | 1/2/3-year smoothed rolling mean | — | Level only |

- Max features: 10–15 maximum — fewer features reduce overfit risk for noisy signal

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM on smoothed series — heavily regularised to prevent noise overfit
- Configuration: Objective = reg:absoluteerror (MAE — more robust to noise than MSE); max_depth = 3; num_leaves = 15; min_data_in_leaf = 10; lambda_l1 = 1.0; lambda_l2 = 1.0
- Feature count: ≤ 15 — strict limit; no interaction features
- Overfitting check: Validation WMAPE / Train WMAPE must be < 1.20
- When to use: Portfolio large enough for pooled cross-SKU training (> 50 Noisy SKUs)

#### 6.2 Deep Learning (DL)
- Architectures: Not recommended for individual SKU — insufficient signal; noise overwhelms DL
- Cross-portfolio: DeepAR with heavy dropout (p = 0.40) if > 500 Noisy SKUs in portfolio — cross-learning reduces individual noise impact
- When to use: Very large portfolio only; heavy regularisation mandatory

#### 6.3 Statistical / Time Series Models
- Architectures: Kalman filter structural time series (primary); Theta method (secondary)

**Kalman Filter for Noisy Demand:**
```
State equation:   α(t) = T × α(t-1) + R × η(t)   η ~ N(0, Q)
Observation:      d(t) = Z × α(t) + ε(t)          ε ~ N(0, H)

For Noisy signal: H >> Q (high observation noise relative to state noise)
  H / Q ratio calibrated from estimated SNR:
  H = (1/SNR) × total_variance
  Q = total_variance − H

Kalman smoother output = posterior estimate of true state α(t)
Use as d_clean(t) for downstream modelling
```

| Granularity | H/Q Ratio | Smoothing Strength |
|---|---|---|
| Daily (SNR 0.5–1.0) | H/Q = 2–4 | Moderate |
| Daily (SNR < 0.5) | H/Q = 5–10 | Strong |
| Weekly (SNR 0.5–1.0) | H/Q = 2–4 | Moderate |
| Monthly (SNR 0.5–1.0) | H/Q = 2–3 | Moderate |
| Quarterly (SNR < 0.8) | H/Q = 3–5 | Strong |
| Yearly (SNR < 0.5) | H/Q = 4–8 | Strong |

**Theta Method (secondary):**
```
Decompose into two Theta lines (θ=0, θ=2)
θ=0 captures long-run trend (noise-resistant)
θ=2 captures short-term (noise-susceptible)
Weight θ=0 more heavily for Noisy signal:
  Forecast = 0.70 × θ_0 + 0.30 × θ_2  (vs standard 0.50/0.50)
```

#### 6.4 Baseline / Fallback Model
- Fallback: Extended rolling mean (very long window — smooths out noise)
- Alert if fallback WMAPE is worse than smoothed model WMAPE (indicates noise too severe for any model)

### 7. Ensemble & Weighting

#### 7.2 Dynamic Weight Schedule

| SNR Level | LightGBM | Kalman Filter | Theta |
|---|---|---|---|
| SNR 0.5–1.0 | 30% | 40% | 30% |
| SNR 0.2–0.5 | 15% | 55% | 30% |
| SNR < 0.2 | 0% | 70% | 30% |

### 8. Uncertainty Quantification
- Method: Bootstrap on smoothed residuals (wider than standard — noise floor adds irreducible uncertainty)
- Output: [P10, P50, P90] — wider intervals than Pure Signal
- Irreducible noise floor: min_interval_width = 2 × std(noise_component)
- Use case: Safety stock must account for irreducible noise; consider make-to-order if SNR < 0.2

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Rounding: Round to nearest whole unit — avoid false precision on noisy signal
- Model complexity cap: Maximum model complexity inversely proportional to SNR level
- Make-to-order consideration: If SNR < 0.20 → evaluate make-to-order vs safety stock approach
- Manual overrides: Data team signal quality improvement plan input; aggregation level review (consider higher granularity forecasting)

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | WMAPE on Smoothed | SNR Post-Smoothing | Overfitting Check | Bias Alert |
|---|---|---|---|---|
| Daily | < 28% | SNR > 2.0 post-smooth | Val/Train WMAPE < 1.20 | \|Bias\| > 12% |
| Weekly | < 25% | SNR > 2.0 | Val/Train < 1.20 | \|Bias\| > 10% |
| Monthly | < 22% | SNR > 2.0 | Val/Train < 1.20 | \|Bias\| > 8% |
| Quarterly | < 18% | SNR > 1.5 | Val/Train < 1.20 | \|Bias\| > 6% |
| Yearly | < 15% | SNR > 1.0 | Val/Train < 1.20 | \|Bias\| > 5% |

#### 10.2 Backtesting Protocol

| Granularity | Method | Train | Test |
|---|---|---|---|
| Daily | Rolling window on smoothed series | 180 days | 30 days |
| Weekly | Rolling window on smoothed | 52 weeks | 13 weeks |
| Monthly | Rolling window on smoothed | 24 months | 6 months |
| Quarterly | Rolling window on smoothed | 8 quarters | 2 quarters |
| Yearly | Expanding window | All available | 1 year |

#### 10.3 Retraining

| Granularity | Cadence | Latency |
|---|---|---|
| Daily | Weekly (not daily — low ROI for daily retrain on noisy signal) | T+4 hours |
| Weekly | Weekly | T+1 day |
| Monthly | Monthly | T+2 days |
| Quarterly | Quarterly | T+3 days |
| Yearly | Annually | T+7 days |

### 11. Exception Handling & Overrides
- Auto-detect: SNR rises above 2.0 for 3 consecutive estimations → reclassify to Pure Signal; overfitting check fails (Val/Train > 1.30) → reduce model complexity; noise is actually distortion (DI > 0.15) → reclassify to Distorted
- Manual override: Data team aggregation level change (aggregate to less noisy level); portfolio team make-to-order consideration; range rationalisation for extreme noise SKUs
- Override expiration: Per quarterly SNR review

### 12. Reclassification / Model Selection

| Condition | Target | Holding Period | Transition |
|---|---|---|---|
| SNR rises above 4.0 for 3 estimations | Pure Signal | 3 estimations | Hard switch — remove smoothing |
| DI also > 0.15 detected | Distorted (primary) + Noisy (secondary) | Immediate | Address distortion first |
| AR also > 1.5 | Amplified + Noisy (both apply) | 2 estimations | De-amplify then denoise |

### 13. Review Cadence
- Monthly SNR monitor; quarterly smoothing parameter calibration; annual model complexity review

---

---
