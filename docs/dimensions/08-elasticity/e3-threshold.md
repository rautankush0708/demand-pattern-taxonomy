## E3 · Threshold
### 1. Definition
Predicts demand for SKUs where demand shows no meaningful response to stimulus below a critical activation threshold but responds strongly above it, requiring piecewise causal modelling with explicit threshold detection and non-linear response functions.

### 2. Detailed Description
- **Applicable scenarios:** Categories with psychological price points (e.g. "nothing below 20% discount moves"), volume-deal trigger thresholds (e.g. bulk buy triggers at specific quantity), promotional activation thresholds in B2B
- **Boundaries:**

| Granularity | Detection Condition | Min Events Below T* | Min Events Above T* |
|---|---|---|---|
| Daily | RSS reduction > 20% vs linear AND p < 0.05 for β₂ − β₁ | ≥ 5 events | ≥ 5 events |
| Weekly | RSS reduction > 20% AND p < 0.05 | ≥ 5 events | ≥ 5 events |
| Monthly | RSS reduction > 20% AND p < 0.05 | ≥ 4 events | ≥ 4 events |
| Quarterly | RSS reduction > 20% AND p < 0.05 | ≥ 3 events | ≥ 3 events |
| Yearly | RSS reduction > 20% AND p < 0.05 | ≥ 3 events | ≥ 3 events |

- **Key demand characteristics:** Binary-like response to stimulus; below-threshold behaviour similar to Inelastic; above-threshold behaviour similar to Elastic; threshold value is a critical business planning input
- **Differentiation from other models:** Unlike Elastic, response is not proportional — there is a dead zone below the threshold; unlike Inelastic, large response does exist — just not at all stimulus levels; unlike Saturation, ceiling effect is not the primary feature — activation is

### 3. Business Impact
- **Primary risk (over-forecast):** Planning promotions below threshold — zero uplift; wasted promotional spend
- **Primary risk (under-forecast):** Not deploying above-threshold stimulus when needed — missing demand surge opportunity
- **Strategic importance:** High — threshold knowledge directly determines promotional effectiveness and ROI; knowing the activation point transforms trade planning

### 4. Priority Level
🔴 Tier 1 — Threshold value is a critical commercial input; incorrect threshold assumption wastes entire promotional budget or misses demand surge opportunity.

### 5. Model Strategy Overview

#### 5.1 Piecewise Causal Model
```
Below-threshold model (stimulus < T*):
  F_below(t) = baseline(t) × (1 + β_below × stimulus(t))
  β_below ≈ 0 (minimal response below threshold)

Above-threshold model (stimulus ≥ T*):
  F_above(t) = baseline(t) × (1 + β_above × (stimulus(t) − T*))
  β_above >> β_below (strong response above threshold)

Combined piecewise model:
  F(t) = F_below(t) × I(stimulus < T*) + F_above(t) × I(stimulus ≥ T*)

Threshold T* estimation:
  Grid search over candidate values: T* ∈ {5%, 10%, 15%, 20%, 25%, 30%, 35%, 40%, 45%, 50%}
  Select T* = argmin RSS(piecewise model)
  Confidence interval for T*: Bootstrap 95% CI
```

#### 5.2 Feature Engineering

| Granularity | Threshold Features | Below-Threshold Features | Above-Threshold Features |
|---|---|---|---|
| Daily | Stimulus level (%), above-threshold flag (I(stimulus ≥ T*)), excess above threshold (stimulus − T*)_+, threshold proximity | Baseline rolling mean (non-stimulus periods), seasonal index | Excess above threshold, above-threshold duration, promo type flag, distribution on promo |
| Weekly | Same structure at weekly level | 4/8/13-week baseline rolling mean | Excess above T*, promo type, display flag |
| Monthly | Same structure at monthly level | 3/6/12-month baseline rolling mean | Excess above T*, promo type |
| Quarterly | Same structure | 2/4-quarter baseline mean | Excess above T* |
| Yearly | Same structure | Annual baseline | Excess above T* |

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM with piecewise features (above-threshold indicator and excess features)
- Configuration: Objective = reg:squarederror; Metric = WMAPE, Uplift Accuracy above threshold
- Key features: Above-threshold flag, excess above T*, stimulus level, promo type, baseline rolling mean, seasonal index
- Interaction: above_threshold_flag × stimulus_level × promo_type — captures differential response
- When to use: Primary model — tree-based models naturally learn threshold-like splits

#### 6.2 Deep Learning (DL)
- Architectures: TFT with stimulus level as known future covariate
- When to use: When promotional plan is available as future input; history > 2 years with varied stimulus levels

#### 6.3 Statistical / Time Series Models
- Architectures: Piecewise regression (threshold regression) + ARIMA residuals

**Threshold Regression Formula:**
```
ln(Q_t) = α + β_below × stimulus_t × I(stimulus_t < T*)
         + β_above × (stimulus_t − T*)_+ × I(stimulus_t ≥ T*)
         + Σ γ_k × control_k(t) + ARIMA residual
(stimulus_t − T*)_+ = max(0, stimulus_t − T*)   [excess above threshold]
```

- When to use: Interpretability; threshold value reporting; trade planning

#### 6.4 Baseline / Fallback Model
- Below threshold: Baseline rolling mean (no uplift applied)
- Above threshold: Baseline × category average elastic uplift
- Alert if promotional plan does not specify whether stimulus is above or below T*

### 7. Ensemble & Weighting

| State | LightGBM | TFT | Piecewise Regression |
|---|---|---|---|
| Below threshold | 30% | 10% | 60% |
| Above threshold | 55% | 25% | 20% |
| Threshold vicinity (±5% of T*) | 40% | 20% | 40% |

### 8. Uncertainty Quantification
- Method: Scenario analysis — below threshold, at threshold, above threshold
- Output:

| Scenario | Description | Probability |
|---|---|---|
| Stimulus below T* | No uplift; baseline forecast | Based on planned promo depth |
| Stimulus at T* | Partial uplift; transitional | Transition zone ±5% of T* |
| Stimulus above T* | Full uplift; strong response | Based on planned promo depth |

- Bootstrap CI for T*: [T*_lower, T*_upper] — uncertainty in threshold value itself

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Threshold enforcement rule: If planned promo depth < T* → apply baseline forecast (no uplift); alert trade team
- Above-threshold cap: min(above_threshold_forecast, 3 × baseline rolling mean)
- Threshold advisory: Automatically communicate T* to trade planning team for all promotional planning cycles
- Manual overrides: Trade team above/below threshold confirmation; threshold value challenge input

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | Baseline WMAPE | Above-T* WMAPE | Threshold Accuracy | Bias Alert |
|---|---|---|---|---|
| Daily | < 18% | < 28% | T* estimate within ±5% of true | \|Bias\| > 10% |
| Weekly | < 15% | < 25% | T* within ±5% | \|Bias\| > 8% |
| Monthly | < 12% | < 22% | T* within ±5% | \|Bias\| > 7% |
| Quarterly | < 10% | < 20% | T* within ±5% | \|Bias\| > 6% |
| Yearly | < 8% | < 18% | T* within ±5% | \|Bias\| > 5% |

#### 10.2 Backtesting Protocol
- Separate backtesting for below-threshold and above-threshold periods
- Leave-one-above-threshold-event-out for above-threshold model validation
- Min events: ≥ 5 above-threshold and ≥ 5 below-threshold events

#### 10.3 Retraining
- Standard cadence per granularity
- Additional trigger: Re-estimate T* on each promotional cycle completion — threshold may shift with market conditions

### 11. Exception Handling & Overrides
- Auto-detect: T* estimate shifts > 10% between estimations → alert and re-estimate; above-threshold response weakens (β_above drops) → reclassify to Elastic (if still responsive) or Saturation (if ceiling reached); below-threshold response grows → reclassify toward Elastic
- Manual override: Trade team threshold challenge; market research input on psychological price points
- Override expiration: Per promotional cycle

### 12. Reclassification

| Condition | Target | Holding Period |
|---|---|---|
| Piecewise model advantage disappears (RSS reduction < 10%) | Elastic or Inelastic | 3 estimates |
| Saturation confirmed above threshold | Saturation | 2 estimates |
| Threshold T* approaches 0% (always above threshold) | Elastic | 2 estimates |
| Threshold T* approaches 50% (rarely above threshold) | Inelastic | 2 estimates |

### 13. Review Cadence
- Monthly T* stability check; quarterly threshold re-estimation; annual trade planning alignment

---
