# Dimension 5 · Trend Pattern
## Demand Forecasting Model Templates

---

> **Segments:** 5 · Upward Trend · Downward Trend · Flat · Cyclical Trend · Reverting
> **Granularities:** Daily · Weekly · Monthly · Quarterly · Yearly
> **Note:** Trend Pattern describes the **directional movement** of demand over time. It is distinct from Lifecycle (which captures commercial stage) and Behavior (which captures statistical shape). A Mature Lifecycle SKU can still have a Trending demand pattern; a Growth Lifecycle SKU will typically show an Upward Trend pattern.

---

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

## T1 · Upward Trend

### 1. Definition
Predicts demand for SKUs with a statistically confirmed positive demand slope, where trend-aware models are required to avoid systematic under-forecasting and chronic stockout in rising demand environments.

### 2. Detailed Description
- **Applicable scenarios:** Growing categories, distribution expansion, market share gains, post-launch ramp, price-driven volume growth
- **Boundaries:**

| Granularity | Detection Condition | Slope Magnitude | Min History |
|---|---|---|---|
| Daily | Mann-Kendall p < 0.05; Z > 0; 90-day window | β₁ > 0 | ≥ 56 days |
| Weekly | Mann-Kendall p < 0.05; Z > 0; 13-week window | β₁ > 0 | ≥ 8 weeks |
| Monthly | Mann-Kendall p < 0.05; Z > 0; 6-month window | β₁ > 0 | ≥ 4 months |
| Quarterly | Mann-Kendall p < 0.05; Z > 0; 4-quarter window | β₁ > 0 | ≥ 2 quarters |
| Yearly | Mann-Kendall p < 0.05; Z > 0; 3-year window | β₁ > 0 | ≥ 2 years |

- **Key demand characteristics:** Rising mean demand, positive slope coefficient, possibly increasing variance as volume grows, trend may be mild/moderate/strong
- **Differentiation from other models:** Unlike Flat, slope is statistically confirmed positive; unlike Cyclical Trend, movement is monotonically upward not cyclical; unlike Reverting, demand is not returning to a historical mean but reaching new highs

### 3. Business Impact
- **Primary risk (over-forecast):** Excess inventory if trend flattens or reverses unexpectedly
- **Primary risk (under-forecast):** Systematic chronic stockout as demand outpaces static forecasts — the dominant risk for this segment
- **Strategic importance:** Very high — upward trend SKUs are the growth engine; stockout during growth is a compounding loss

### 4. Priority Level
🔴 Tier 1 — Under-forecast risk dominates; chronic stockout during upward trend is commercially damaging and self-reinforcing (lost sales reduce observed demand, further suppressing forecast).

### 5. Model Strategy Overview

#### 5.1 Zero-Demand Handling (Hurdle)
- Active event threshold: P(demand > 0) > 0.75 — rising demand means fewer zero periods over time
- Classifier: Rule-based — monitor for unexpected zero periods as anomaly signal
- Regressor: LightGBM with trend slope features; TFT for multi-horizon trend projection
- Fallback: Rolling mean + slope extrapolation (β₀ + β₁ × t_forecast)

#### 5.2 Analogue / Similarity Logic
- Number of analogues: k = 3 (SKUs that previously showed similar upward trend — now Mature)
- Similarity criteria: Category, slope magnitude relative to mean (%/period), starting volume level
- Temporal decay: weight = exp(−age / half-life)

| Granularity | Half-Life |
|---|---|
| Daily | 90 days |
| Weekly | 13 weeks |
| Monthly | 6 months |
| Quarterly | 3 quarters |
| Yearly | 2 years |

- Aggregation: Weighted mean of analogues' trend trajectory post-peak

#### 5.3 Feature Engineering

| Granularity | Trend Features | Rolling Features | External Features |
|---|---|---|---|
| Daily | β₁_90day, relative slope (%/day), slope direction consistency (% of 30 positive days in 90-day window), acceleration (Δβ₁) | 7, 30, 90, 180, 365-day mean, std | Promo calendar, distribution coverage, category growth index |
| Weekly | β₁_13week, relative slope (%/week), slope consistency (% positive weeks), acceleration | 4, 8, 13, 26, 52-week mean, std | Promo calendar, distribution points, category index |
| Monthly | β₁_6month, relative slope (%/month), slope consistency, acceleration | 2, 3, 6, 12, 24-month mean, std | Distribution coverage, category index |
| Quarterly | β₁_4quarter, relative slope (%/quarter), acceleration | 1, 2, 4, 6-quarter mean, std | Category trend index |
| Yearly | β₁_3year, relative slope (%/year), acceleration | 1, 2, 3, 4-year mean, std | Market share index, macro index |

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM with trend-aware features
- Configuration: Objective = reg:squarederror; Metric = WMAPE, RMSE; directional bias penalty applied
- Key features: Slope coefficient, relative slope, slope acceleration, rolling means (all windows), distribution coverage growth, category growth index
- Bias correction: Apply +β₁ × h adjustment to forecast for horizon h (trend extrapolation correction)
- When to use: Primary model — always applied

#### 6.2 Deep Learning (DL)
- Architectures: TFT (captures trend via attention) + N-BEATS (explicit trend block)

| Granularity | Lookback | Features | Output |
|---|---|---|---|
| Daily | 180 days | 18 | P10, P50, P90 |
| Weekly | 52 weeks | 15 | P10, P50, P90 |
| Monthly | 24 months | 12 | P10, P50, P90 |
| Quarterly | 8 quarters | 10 | P10, P50, P90 |
| Yearly | 5 years | 8 | P10, P50, P90 |

- Training: Loss = quantile loss; Adam lr = 0.001; Dropout = 0.1; Patience = 10
- When to use: History > 1 year equivalent; multi-horizon forecast required

#### 6.3 Statistical / Time Series Models
- Architectures: ETS(A,A,N) — additive error, additive trend, no seasonality (or ETS(A,A,A) if seasonal)
- Trend: Additive — no damping applied (upward trend expected to continue)
- Seasonality: ETS(A,A,A) if Seasonal driver also present; SARIMA(p,1,q) for non-stationary with trend

**Holt's Linear Trend Model:**
```
Level:   l_t = α × d_t + (1−α)(l_{t-1} + b_{t-1})
Trend:   b_t = β × (l_t − l_{t-1}) + (1−β) × b_{t-1}
Forecast: F(t+h) = l_t + h × b_t
α ∈ [0.1, 0.5]; β ∈ [0.05, 0.3] — optimised on validation MAE
```

| Granularity | α Range | β Range |
|---|---|---|
| Daily | 0.2–0.5 | 0.05–0.2 |
| Weekly | 0.15–0.4 | 0.05–0.2 |
| Monthly | 0.1–0.3 | 0.05–0.15 |
| Quarterly | 0.1–0.3 | 0.05–0.15 |
| Yearly | 0.1–0.25 | 0.05–0.10 |

- When to use: Always included in ensemble; interpretability and trend coefficient reporting

#### 6.4 Baseline / Fallback Model
- Fallback triggers: Model convergence failure; slope reversal detected
- Fallback model: Rolling mean + β₁ × forecast_horizon (simple trend extrapolation)
- Logging & alerting: Alert if fallback rate > 15%

### 7. Ensemble & Weighting

#### 7.1 Ensemble Scheme
- Combination: D̂_t = w_lgbm × LightGBM + w_tft × TFT + w_nbeats × N-BEATS + w_ets × ETS(A,A,N)
- Weight determination: Error-inverse on directional bias-adjusted WMAPE (penalise under-forecast more heavily)

#### 7.2 Dynamic Weight Schedule

| History Length | LightGBM | TFT | N-BEATS | ETS(A,A,N) |
|---|---|---|---|---|
| Up to 6 months equiv. | 60% | 0% | 0% | 40% |
| 6–12 months equiv. | 55% | 25% | 0% | 20% |
| 12–24 months equiv. | 45% | 30% | 10% | 15% |
| > 24 months equiv. | 40% | 30% | 20% | 10% |

### 8. Uncertainty Quantification
- Method: Quantile regression + conformal prediction
- Output: [P10, P50, P90] — P90 used for safety stock; P50 for base replenishment
- Use case: Safety stock calibrated to P75 (lean upward); replenishment trigger at P50

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Trend cap: Forecast growth rate per period ≤ 2 × historical maximum growth rate observed
- Anti-stockout rule: If bias tracking signal TS > 4 → automatically increase forecast by β₁ × 2 periods
- Manual overrides: Commercial distribution gain plan; promotional acceleration input
- Alignment: Forecast growth rate must not exceed confirmed distribution coverage growth rate

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | WMAPE Target | Under-Forecast Bias Alert | Tracking Signal Alert | Coverage |
|---|---|---|---|---|
| Daily | < 25% | Bias < −10% | \|TS\| > 4 | 80% P10–P90 |
| Weekly | < 20% | Bias < −10% | \|TS\| > 4 | 80% P10–P90 |
| Monthly | < 18% | Bias < −8% | \|TS\| > 4 | 80% P10–P90 |
| Quarterly | < 15% | Bias < −6% | \|TS\| > 4 | 80% P10–P90 |
| Yearly | < 12% | Bias < −5% | \|TS\| > 4 | 80% P10–P90 |

#### 10.2 Backtesting Protocol

| Granularity | Train | Test | Direction Bias Check |
|---|---|---|---|
| Daily | 180 days | 30 days | Confirm no systematic under-forecast |
| Weekly | 52 weeks | 13 weeks | Confirm no systematic under-forecast |
| Monthly | 24 months | 6 months | Confirm no systematic under-forecast |
| Quarterly | 8 quarters | 2 quarters | Confirm no systematic under-forecast |
| Yearly | All available | 1 year | Confirm no systematic under-forecast |

#### 10.3 Retraining

| Granularity | Cadence | Latency |
|---|---|---|
| Daily | Daily | T+4 hours |
| Weekly | Weekly | T+1 day |
| Monthly | Monthly | T+2 days |
| Quarterly | Quarterly | T+3 days |
| Yearly | Annually | T+7 days |

### 11. Exception Handling & Overrides
- Auto-detect: Slope reversal (Z changes sign) for 3 consecutive periods → reclassification trigger; forecast > 3 × rolling max → cap and alert; tracking signal |TS| > 6 → automatic upward adjustment
- Manual override: Commercial confirmation of trend continuation; supply expansion plan alignment
- Override expiration: Single cycle — reviewed each period given trend sensitivity

### 12. Reclassification / Model Selection

| Condition | Target Segment | Holding Period | Transition |
|---|---|---|---|
| Mann-Kendall p > 0.10 for 4 consecutive periods | Flat | 4 periods | Soft blend |
| Mann-Kendall p < 0.05; Z < 0 for 3 periods | Downward Trend | 3 periods | Soft blend |
| ADF p < 0.05 (mean-reverting confirmed) | Reverting | 4 periods | Soft blend |

### 13. Review Cadence
- Per cycle automated dashboard with slope monitor and tracking signal; weekly commercial review; quarterly full re-evaluation

---

## T2 · Downward Trend

### 1. Definition
Predicts demand for SKUs with a statistically confirmed negative demand slope, where damped trend-aware models are required to prevent systematic over-forecasting and inventory accumulation in declining demand environments.

### 2. Detailed Description
- **Applicable scenarios:** Declining categories, distribution losses, market share erosion, ageing products, price-driven volume decline
- **Boundaries:**

| Granularity | Detection Condition | Slope | Min History |
|---|---|---|---|
| Daily | Mann-Kendall p < 0.05; Z < 0; 90-day window | β₁ < 0 | ≥ 56 days |
| Weekly | Mann-Kendall p < 0.05; Z < 0; 13-week window | β₁ < 0 | ≥ 8 weeks |
| Monthly | Mann-Kendall p < 0.05; Z < 0; 6-month window | β₁ < 0 | ≥ 4 months |
| Quarterly | Mann-Kendall p < 0.05; Z < 0; 4-quarter window | β₁ < 0 | ≥ 2 quarters |
| Yearly | Mann-Kendall p < 0.05; Z < 0; 3-year window | β₁ < 0 | ≥ 2 years |

- **Key demand characteristics:** Falling mean demand, negative slope, possibly rising CV² as volume shrinks, approaching zero asymptotically (damped model) or rapidly (steep decline)
- **Differentiation from other models:** Unlike Flat, slope is confirmed negative; unlike Reverting, demand is not bouncing back to a long-run mean but continuing downward; unlike Phasing Out lifecycle, decline is market-driven not supply-side-decided

### 3. Business Impact
- **Primary risk (over-forecast):** Systematic inventory accumulation — the dominant risk; write-off and obsolescence
- **Primary risk (under-forecast):** Minimal — over-forecast risk dominates entirely for this segment
- **Strategic importance:** Medium — primary goal is inventory run-down management, not service level optimisation

### 4. Priority Level
🟠 Tier 2 — Over-forecast prevention dominates; damped models and conservative forecasting are the primary tools.

### 5. Model Strategy Overview

#### 5.1 Zero-Demand Handling (Hurdle)
- Active event threshold: P(demand > 0) > 0.50 — declining SKUs approach zero over time
- Classifier: Logistic Regression with trend and time-to-zero features
- Regressor: LightGBM with negative slope features + damped ETS
- Fallback: Flat rolling mean (conservative — prevents over-extrapolation of decline)

#### 5.2 Analogue / Similarity Logic
- Number of analogues: k = 3 (SKUs that previously showed similar downward trend — now Inactive or Phasing Out)
- Similarity criteria: Category, slope magnitude (%/period), volume at decline start
- Temporal decay: weight = exp(−age / half-life)

| Granularity | Half-Life |
|---|---|
| Daily | 60 days |
| Weekly | 8 weeks |
| Monthly | 4 months |
| Quarterly | 2 quarters |
| Yearly | 1.5 years |

#### 5.3 Feature Engineering

| Granularity | Trend Features | Rolling Features | Decline Context Features |
|---|---|---|---|
| Daily | β₁_90day (negative), relative slope, periods since peak demand, slope acceleration (Δβ₁) | 7, 30, 90-day mean, std | Distribution loss rate, competitor gain flag, price increase flag |
| Weekly | β₁_13week (negative), relative slope, weeks since peak | 4, 8, 13, 26-week mean, std | Distribution point loss, category decline index |
| Monthly | β₁_6month (negative), relative slope, months since peak | 2, 3, 6, 12-month mean, std | Category decline index |
| Quarterly | β₁_4quarter (negative), relative slope, quarters since peak | 1, 2, 4-quarter mean, std | Category index |
| Yearly | β₁_3year (negative), relative slope, years since peak | 1, 2, 3-year mean, std | Market share index |

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM with downward bias correction
- Configuration: Objective = reg:squarederror; Metric = WMAPE, MAE; over-forecast penalty applied
- Over-forecast correction: If bias > 0 for 3 consecutive periods → apply −β₁ × 1.5 × h correction
- When to use: Primary model

#### 6.2 Deep Learning (DL)
- Architectures: TFT (attention captures declining trend)
- Not recommended for steep decline SKUs — model complexity unjustified as volume approaches zero
- When to use: Only if history > 1 year AND decline is mild (relative slope < 2%/period)

#### 6.3 Statistical / Time Series Models
- Architectures: ETS(A,A,N) with **damped trend** — critical for downward trend to prevent forecast crossing zero

**Damped Holt's Linear Trend:**
```
Level:    l_t = α × d_t + (1−α)(l_{t-1} + phi × b_{t-1})
Trend:    b_t = β × (l_t − l_{t-1}) + (1−β) × phi × b_{t-1}
Forecast: F(t+h) = l_t + (phi + phi² + ... + phi^h) × b_t
phi < 1 → trend fades over horizon (prevents forecast going negative)
```

| Granularity | Mild Slope phi | Moderate Slope phi | Strong Slope phi |
|---|---|---|---|
| Daily | 0.95 | 0.90 | 0.85 |
| Weekly | 0.90 | 0.85 | 0.80 |
| Monthly | 0.85 | 0.80 | 0.75 |
| Quarterly | 0.80 | 0.75 | 0.70 |
| Yearly | 0.75 | 0.70 | 0.65 |

- When to use: Always included — damped trend is essential safety model for decline

#### 6.4 Baseline / Fallback Model
- Fallback triggers: Slope reversal detected (reclassification triggered)
- Fallback model: Rolling mean (conservative hold — no trend extrapolation)
- Logging & alerting: Alert if fallback triggered AND over-forecast bias > 10%

### 7. Ensemble & Weighting

#### 7.2 Dynamic Weight Schedule

| Decline Stage (Relative Slope) | LightGBM | ETS(damped) | TFT |
|---|---|---|---|
| Mild (< 2%/period) | 55% | 30% | 15% |
| Moderate (2–5%/period) | 50% | 45% | 5% |
| Strong (> 5%/period) | 40% | 60% | 0% |

- Weight determination: Error-inverse on over-forecast-penalised WMAPE

### 8. Uncertainty Quantification
- Method: Quantile regression
- Output: [P10, P50, P90] — P10 for minimum buy; P50 for base; P90 for maximum exposure
- Use case: Inventory run-down planning using P10; obsolescence risk using P90

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Decline cap: max(forecast, 0) — damped model prevents negative; hard floor at zero
- Ceiling: min(forecast, prior rolling mean) — forecast must not drift upward
- Anti-accumulation rule: If bias > +10% for 3 periods → apply additional −β₁ × 0.5 × h correction
- Manual overrides: Delisting date; clearance promotion; distribution reinstatement plan
- Alignment: Forecast cannot exceed current stock on hand + confirmed inbound

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | WMAPE Target | Over-Forecast Bias Alert | Tracking Signal Alert | Coverage |
|---|---|---|---|---|
| Daily | < 28% | Bias > +10% | TS > +4 | 80% P10–P90 |
| Weekly | < 22% | Bias > +10% | TS > +4 | 80% P10–P90 |
| Monthly | < 18% | Bias > +8% | TS > +4 | 80% P10–P90 |
| Quarterly | < 15% | Bias > +6% | TS > +4 | 80% P10–P90 |
| Yearly | < 12% | Bias > +5% | TS > +4 | 80% P10–P90 |

#### 10.2 Backtesting Protocol

| Granularity | Train | Test | Over-Forecast Check |
|---|---|---|---|
| Daily | 180 days | 30 days | Confirm no systematic over-forecast |
| Weekly | 52 weeks | 13 weeks | Confirm no systematic over-forecast |
| Monthly | 24 months | 6 months | Confirm no systematic over-forecast |
| Quarterly | 8 quarters | 2 quarters | Confirm no systematic over-forecast |
| Yearly | All available | 1 year | Confirm no systematic over-forecast |

#### 10.3 Retraining

| Granularity | Cadence | Latency |
|---|---|---|
| Daily | Daily | T+4 hours |
| Weekly | Weekly | T+1 day |
| Monthly | Monthly | T+2 days |
| Quarterly | Quarterly | T+3 days |
| Yearly | Annually | T+7 days |

### 11. Exception Handling & Overrides
- Auto-detect: Slope reversal (Z positive) for 3 consecutive periods → reclassification trigger; forecast > prior rolling mean → immediate over-forecast alert; demand reaches zero for 3+ consecutive periods → Inactive reclassification trigger
- Manual override: Commercial decision to reinvest; distribution plan reversal
- Override expiration: Single cycle

### 12. Reclassification

| Condition | Target Segment | Holding Period | Transition |
|---|---|---|---|
| Mann-Kendall p > 0.10 for 4 periods | Flat | 4 periods | Soft blend |
| Mann-Kendall p < 0.05; Z > 0 for 3 periods | Upward Trend | 3 periods | Soft blend |
| Zero demand ≥ Inactive threshold | Flat → Lifecycle: Inactive | Immediate | Hard switch |

### 13. Review Cadence
- Per cycle automated dashboard with over-forecast alert; bi-weekly obsolescence review; quarterly full re-evaluation

---

## T3 · Flat

### 1. Definition
Predicts demand for SKUs where no statistically significant directional trend exists, where standard level-based forecasting methods are optimal and trend components should be suppressed to avoid spurious drift.

### 2. Detailed Description
- **Applicable scenarios:** Established core products, mature market SKUs, staple categories, commodity lines
- **Boundaries:**

| Granularity | Detection Condition | Min History |
|---|---|---|
| Daily | Mann-Kendall p ≥ 0.10; ADF p < 0.05 (stationary); 90-day window | ≥ 56 days |
| Weekly | Mann-Kendall p ≥ 0.10; ADF p < 0.05; 13-week window | ≥ 8 weeks |
| Monthly | Mann-Kendall p ≥ 0.10; ADF p < 0.05; 6-month window | ≥ 4 months |
| Quarterly | Mann-Kendall p ≥ 0.10; ADF p < 0.05; 4-quarter window | ≥ 2 quarters |
| Yearly | Mann-Kendall p ≥ 0.10; 3-year window | ≥ 2 years |

- **Key demand characteristics:** Stable mean, no directional movement, possibly seasonal fluctuations around flat baseline, mean-stationary series
- **Differentiation from other models:** Unlike Upward/Downward Trend, no slope confirmed; unlike Reverting, demand is not deviating and returning — it is consistently near the mean; unlike Cyclical, no long-wave cycle detected

### 3. Business Impact
- **Primary risk (over-forecast):** Gradual inventory accumulation from small consistent positive bias
- **Primary risk (under-forecast):** Gradual service level erosion from small consistent negative bias
- **Strategic importance:** Very high — Flat trend SKUs are the bulk of mature portfolios; accuracy is paramount

### 4. Priority Level
🔴 Tier 1 — Flat trend is the most common segment; even small systematic bias creates significant cumulative inventory impact across the portfolio.

### 5. Model Strategy Overview

#### 5.1 Zero-Demand Handling (Hurdle)
- Active event threshold: P(demand > 0) > 0.85 — flat demand means consistently active
- Classifier: Rule-based flag only
- Regressor: LightGBM + ETS — no trend component
- Fallback: Rolling mean (extended window)

#### 5.2 Analogue / Similarity Logic
- Not applicable — sufficient own history; flat trend means signal is stable and reliable

#### 5.3 Feature Engineering

| Granularity | Trend Features | Rolling Features | External Features |
|---|---|---|---|
| Daily | No slope features — explicitly excluded; stationarity flag | 7, 30, 90, 180, 365-day mean, std, CV² | Holiday flag, promo flag, day of week, seasonal index |
| Weekly | No slope features; stationarity flag | 4, 8, 13, 26, 52-week mean, std, CV² | Holiday, promo flag, week of year, seasonal index |
| Monthly | No slope features; stationarity flag | 2, 3, 6, 12, 24-month mean, std, CV² | Month of year, promo flag, seasonal index |
| Quarterly | No slope features; stationarity flag | 1, 2, 3, 4-quarter mean, std | Quarter, seasonal index |
| Yearly | No slope features | 1, 2, 3, 4-year mean, std | Macro index |

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM (no trend features — suppress trend component explicitly)
- Configuration: Objective = reg:squarederror; Metric = WMAPE, RMSE
- Key features: Rolling means (all windows), seasonal index, promo flag, holiday flag, period of year
- Explicit exclusion: Slope features, trend index — adding these introduces spurious trend

#### 6.2 Deep Learning (DL)
- Architectures: N-BEATS (generic block — no explicit trend block to avoid trend injection)

| Granularity | Lookback | Features | Output |
|---|---|---|---|
| Daily | 365 days | 15 | P10, P50, P90 |
| Weekly | 52 weeks | 12 | P10, P50, P90 |
| Monthly | 24 months | 10 | P10, P50, P90 |
| Quarterly | 8 quarters | 8 | P10, P50, P90 |
| Yearly | 5 years | 6 | P10, P50, P90 |

- When to use: History > 2 years; seasonal pattern present

#### 6.3 Statistical / Time Series Models
- Architectures: ETS(A,N,A) — additive error, **no trend**, additive seasonality

**Holt-Winters No-Trend (Flat):**
```
Level:    l_t = α × d_t + (1−α) × l_{t-1}          [no trend component]
Seasonal: s_t = γ × (d_t − l_t) + (1−γ) × s_{t−m}
Forecast: F(t+h) = l_t + s_{t+h−m}
α ∈ [0.1, 0.4]; γ ∈ [0.05, 0.3] — optimised on validation WMAPE
```

| Granularity | Period (m) | Model |
|---|---|---|
| Daily | 7 (+ 365 if enough history) | TBATS or ETS(A,N,A) |
| Weekly | 52 | ETS(A,N,A) |
| Monthly | 12 | ETS(A,N,A) or SARIMA(p,0,q)(P,0,Q)_12 |
| Quarterly | 4 | ETS(A,N,A) |
| Yearly | — | ETS(A,N,N) simple smoothing |

- When to use: Always included — no trend ETS is the natural model for flat demand

#### 6.4 Baseline / Fallback Model
- Fallback: Same period last year
- Logging & alerting: Alert if fallback rate > 10%

### 7. Ensemble & Weighting

#### 7.2 Dynamic Weight Schedule

| History Length | LightGBM | N-BEATS | ETS(A,N,A) |
|---|---|---|---|
| Up to 1 year | 55% | 0% | 45% |
| 1–2 years | 55% | 0% | 45% |
| > 2 years | 50% | 20% | 30% |

### 8. Uncertainty Quantification
- Method: Conformal prediction on residuals
- Output: [P10, P50, P90]
- Use case: Safety stock at target service level; symmetric intervals expected for flat demand

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Capping: min(forecast, 1.5 × full-year rolling max)
- Floor: max(forecast, 0.5 × full-year rolling min)
- Alignment: ±20% of prior year same period; automated flag if breached
- Manual overrides: S&OP consensus; known upcoming change (distribution, pricing, promo)

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | WMAPE Target | Bias Alert | Tracking Signal | Coverage |
|---|---|---|---|---|
| Daily | < 18% | \|Bias\| > 8% | \|TS\| > 4 | 80% P10–P90 |
| Weekly | < 15% | \|Bias\| > 7% | \|TS\| > 4 | 80% P10–P90 |
| Monthly | < 12% | \|Bias\| > 6% | \|TS\| > 4 | 80% P10–P90 |
| Quarterly | < 10% | \|Bias\| > 5% | \|TS\| > 4 | 80% P10–P90 |
| Yearly | < 8% | \|Bias\| > 4% | \|TS\| > 4 | 80% P10–P90 |

#### 10.2 Backtesting Protocol

| Granularity | Train | Test | Stationarity Check |
|---|---|---|---|
| Daily | 365 days | 30 days | ADF p < 0.05 confirmed |
| Weekly | 104 weeks | 13 weeks | ADF p < 0.05 confirmed |
| Monthly | 36 months | 6 months | ADF p < 0.05 confirmed |
| Quarterly | 12 quarters | 2 quarters | ADF p < 0.05 confirmed |
| Yearly | All available | 1 year | Visual inspection |

#### 10.3 Retraining

| Granularity | Cadence | Latency |
|---|---|---|
| Daily | Daily | T+4 hours |
| Weekly | Weekly | T+1 day |
| Monthly | Monthly | T+2 days |
| Quarterly | Quarterly | T+3 days |
| Yearly | Annually | T+7 days |

### 11. Exception Handling & Overrides
- Auto-detect: Mann-Kendall p < 0.05 for 4 periods → reclassify to Upward or Downward Trend; tracking signal |TS| > 6 → reforecast triggered
- Manual override: S&OP consensus adjustment; known structural change input
- Override expiration: Single cycle unless permanent change confirmed

### 12. Reclassification

| Condition | Target Segment | Holding Period | Transition |
|---|---|---|---|
| Mann-Kendall p < 0.05; Z > 0 for 4 periods | Upward Trend | 4 periods | Soft blend |
| Mann-Kendall p < 0.05; Z < 0 for 4 periods | Downward Trend | 4 periods | Soft blend |
| ADF p ≥ 0.05 AND FFT cycle detected | Cyclical Trend | 4 periods | Soft blend |
| ADF p < 0.05 AND deviations detected | Reverting | 4 periods | Soft blend |

### 13. Review Cadence
- Per cycle automated dashboard with stationarity monitor; bi-weekly S&OP; quarterly full re-evaluation

---

## T4 · Cyclical Trend

### 1. Definition
Predicts demand for SKUs exhibiting long-wave demand cycles beyond the primary seasonal frequency, where standard seasonal models underfit and multi-period cycle-aware models are required to capture boom-bust or long-cycle patterns.

### 2. Detailed Description
- **Applicable scenarios:** Business cycle-sensitive categories, commodities, capital goods, construction materials, economic-cycle-driven categories, fashion macro-cycles
- **Boundaries:**

| Granularity | Detection Condition | Cycle Period Range | Min Obs |
|---|---|---|---|
| Daily | FFT peak on detrended/deseasonalised series; amplitude > 10% of mean; cycle period > 14 days | 14 days to 3 years | ≥ 2 full cycles |
| Weekly | FFT peak; amplitude > 10%; cycle period > 8 weeks | 8 weeks to 3 years | ≥ 2 full cycles |
| Monthly | FFT peak; amplitude > 10%; cycle period > 6 months | 6 months to 5 years | ≥ 2 full cycles |
| Quarterly | FFT peak; amplitude > 10%; cycle period > 2 quarters | 2 quarters to 5 years | ≥ 2 full cycles |
| Yearly | FFT peak; amplitude > 10%; cycle period > 2 years | 2 years to 10 years | ≥ 2 full cycles |

- **Key demand characteristics:** Long-wave oscillation beyond primary seasonality; demand rises and falls in multi-period cycles; standard seasonal models treat troughs as anomalies
- **Differentiation from other models:** Unlike Seasonal (short calendar cycle), cycles are longer; unlike Upward/Downward Trend, direction reverses cyclically; unlike Reverting, deviations are not random but structured

### 3. Business Impact
- **Primary risk (over-forecast):** Inventory build at cycle peak — missed trough
- **Primary risk (under-forecast):** Stockout at cycle trough recovery — missed upturn
- **Strategic importance:** High for capital goods, industrial, and economic-cycle-sensitive categories

### 4. Priority Level
🟠 Tier 2 — Complex modelling required; data pipeline for macro indicators needed; medium-high implementation effort.

### 5. Model Strategy Overview

#### 5.1 Cycle Decomposition (Primary Pre-Processing Step)
```
STEP 1: Remove seasonal component → d_adj(t) = d(t) / SI(t)
STEP 2: Remove linear trend → d_dt(t) = d_adj(t) − (β₀ + β₁ × t)
STEP 3: Identify cycle via FFT → cycle period T_c = 1 / f_peak
STEP 4: Fit sinusoidal cycle → C(t) = A × sin(2π × t / T_c + φ)
         A = amplitude (estimated via OLS); φ = phase offset
STEP 5: Reconstruct forecast → F(t) = Trend(t) + Seasonal(t) + Cycle(t) + ε(t)
```

#### 5.2 Feature Engineering

| Granularity | Cycle Features | Macro Features | Rolling Features |
|---|---|---|---|
| Daily | Cycle phase (t mod T_c / T_c), cycle position index, days to cycle peak/trough | Consumer confidence, industrial output index | 7, 30, 90-day mean, std |
| Weekly | Cycle phase, weeks to cycle peak/trough, cycle amplitude index | PMI, GDP growth rate, industry index | 4, 8, 13, 26-week mean, std |
| Monthly | Cycle phase (month in cycle), months to peak/trough | GDP growth, industry output, commodity price | 2, 3, 6, 12-month mean, std |
| Quarterly | Cycle phase (quarter in cycle), quarters to peak/trough | GDP growth, capital expenditure index | 1, 2, 4-quarter mean, std |
| Yearly | Cycle phase (year in cycle), years to peak/trough | GDP, macro cycle indicator | 1, 2, 3-year mean, std |

### 6. Model Families

#### 6.1 ML: LightGBM with cycle phase features + macro economic indicators
- Objective: reg:squarederror | Metric: WMAPE, RMSE
- Key features: Cycle phase, cycle amplitude, macro index, rolling means, seasonal index

#### 6.2 DL: TFT with long lookback (captures full cycle)

| Granularity | Lookback (covers ≥ 2 cycles) | Features |
|---|---|---|
| Daily | 2 × T_c (days) | 18 |
| Weekly | 2 × T_c (weeks) | 15 |
| Monthly | 2 × T_c (months) | 12 |
| Quarterly | 2 × T_c (quarters) | 10 |
| Yearly | 2 × T_c (years) | 8 |

#### 6.3 Statistical: BSTS (Bayesian Structural Time Series) with cycle component

**BSTS Cycle Component:**
```
Cycle(t) = ρ × cos(λ) × Cycle(t-1) + ρ × sin(λ) × Cycle*(t-1) + ε_c(t)
Cycle*(t) = −ρ × sin(λ) × Cycle(t-1) + ρ × cos(λ) × Cycle*(t-1) + ε_c*(t)
where λ = 2π / T_c (cycle frequency); ρ ∈ (0,1) = damping factor
```

| Granularity | λ Computation | ρ |
|---|---|---|
| Daily | 2π / T_c_days | 0.90 |
| Weekly | 2π / T_c_weeks | 0.90 |
| Monthly | 2π / T_c_months | 0.85 |
| Quarterly | 2π / T_c_quarters | 0.85 |
| Yearly | 2π / T_c_years | 0.80 |

#### 6.4 Fallback: Seasonal model (treats cycle as long-season); alert if cycle missed

### 7. Ensemble

| History (Full Cycles) | LightGBM | TFT | BSTS |
|---|---|---|---|
| 2 cycles | 40% | 0% | 60% |
| 3 cycles | 45% | 25% | 30% |
| ≥ 4 cycles | 40% | 35% | 25% |

### 8. Uncertainty Quantification
- Method: Scenario analysis — early cycle, mid-cycle, late cycle scenarios
- Output: [P10, P50, P90] conditioned on cycle position
- Use case: Strategic inventory positioning at cycle trough; run-down at cycle peak

### 9. Business Rules
- Non-negativity: max(0, forecast)
- Cycle position flag: Attach cycle phase label (early expansion / late expansion / early contraction / late contraction) to all forecasts for planner context
- Manual overrides: Macro economist input on cycle turning point; commodity price signal

### 10. Evaluation

| Granularity | WMAPE Target | Cycle Phase WMAPE | Bias Alert |
|---|---|---|---|
| Daily | < 25% | Peak/trough < 30% | \|Bias\| > 12% |
| Weekly | < 22% | Peak/trough < 28% | \|Bias\| > 10% |
| Monthly | < 20% | Peak/trough < 25% | \|Bias\| > 8% |
| Quarterly | < 18% | Peak/trough < 22% | \|Bias\| > 6% |
| Yearly | < 15% | Peak/trough < 20% | \|Bias\| > 5% |

### 11. Exception Handling
- Alert: Cycle period changes significantly (> 20%) between detections → re-detect cycle; macro shock → evaluate permanent cycle disruption

### 12. Reclassification

| Condition | Target | Holding Period |
|---|---|---|
| FFT cycle no longer significant for 2 full cycles | Flat or Reverting | 2 cycles |
| Mann-Kendall p < 0.05 confirms monotonic direction | Upward or Downward Trend | 4 periods |

### 13. Review Cadence
- Quarterly cycle position update; semi-annual macro review; annual full re-evaluation

---

## T5 · Reverting

### 1. Definition
Predicts demand for SKUs that systematically deviate from a stable long-run mean and return to it, where mean-reversion models outperform trend extrapolation and prevent over-reaction to temporary deviations.

### 2. Detailed Description
- **Applicable scenarios:** Commodity-like demand, budget-constrained categories (spend reverts to annual budget), weather-normalised categories, post-shock recovery demand
- **Boundaries:**

| Granularity | Detection Condition | Half-Life Range | Min History |
|---|---|---|---|
| Daily | ADF p < 0.05 (stationary); reversion half-life estimated | 3–90 days | ≥ 180 days |
| Weekly | ADF p < 0.05; half-life estimable | 2–26 weeks | ≥ 52 weeks |
| Monthly | ADF p < 0.05; half-life estimable | 1–12 months | ≥ 24 months |
| Quarterly | ADF p < 0.05; half-life estimable | 1–4 quarters | ≥ 8 quarters |
| Yearly | ADF p < 0.05; half-life estimable | 1–3 years | ≥ 5 years |

- **Key demand characteristics:** Demand deviates above or below long-run mean; strong pull back toward mean; deviation magnitude decays exponentially at reversion half-life rate
- **Differentiation from other models:** Unlike Flat, demand does deviate noticeably; unlike Upward/Downward, deviation reverses direction; unlike Cyclical, reversion is probabilistic not structural

### 3. Business Impact
- **Primary risk (over-forecast):** Over-reacting to temporary upswing — building stock that isn't needed as demand reverts
- **Primary risk (under-forecast):** Under-reacting to temporary dip — cutting stock before demand recovers
- **Strategic importance:** Medium — primary value is avoiding over-reaction to noise

### 4. Priority Level
🟠 Tier 2 — Mean-reversion models prevent costly over-reactions; medium complexity.

### 5. Model Strategy Overview

#### 5.1 Mean Reversion Model (Primary)
```
Long-run mean: μ_LR = mean over extended window
Current deviation: dev(t) = d(t) − μ_LR
Reversion speed: α = estimated from regression Δdev(t) = α × dev(t-1) + ε(t)
                 α must be negative (−1 < α < 0) for reversion
Half-life: HL = −ln(2) / α

Forecast h periods ahead:
  dev_forecast(t+h) = dev(t) × (1+α)^h
  d_forecast(t+h) = μ_LR + dev_forecast(t+h)
  = μ_LR + (d(t) − μ_LR) × (1+α)^h
```

| Granularity | Long-Run Mean Window | Reversion Estimation Window |
|---|---|---|
| Daily | 365 days | 90-day rolling regression |
| Weekly | 52 weeks | 26-week rolling regression |
| Monthly | 24 months | 12-month rolling regression |
| Quarterly | 8 quarters | 4-quarter rolling regression |
| Yearly | 5 years | 3-year rolling regression |

#### 5.2 Feature Engineering

| Granularity | Reversion Features | Rolling Features |
|---|---|---|
| Daily | Current deviation (d(t) − μ_LR), deviation normalised by σ, half-life (days), reversion speed α, periods since last mean crossing | 7, 30, 90-day mean, std |
| Weekly | Current deviation, normalised deviation, half-life (weeks), α, weeks since last mean crossing | 4, 8, 13, 26-week mean, std |
| Monthly | Current deviation, normalised deviation, half-life (months), α | 2, 3, 6, 12-month mean, std |
| Quarterly | Current deviation, normalised deviation, half-life (quarters), α | 1, 2, 4-quarter mean, std |
| Yearly | Current deviation, normalised deviation, half-life (years), α | 1, 2, 3-year mean, std |

### 6. Model Families

#### 6.1 ML: LightGBM with deviation and reversion features
- Objective: reg:squarederror | Metric: WMAPE, RMSE

#### 6.2 DL: Not primary — mean reversion is well captured statistically

#### 6.3 Statistical: Ornstein-Uhlenbeck (OU) process — the natural model for mean-reverting demand

**OU Process:**
```
d(t+dt) = θ × (μ_LR − d(t)) × dt + σ × dW(t)
where θ = speed of reversion (θ > 0)
      μ_LR = long-run mean
      σ = volatility
      dW = Wiener process increment

Discrete-time equivalent:
d(t+1) = μ_LR + e^{−θ} × (d(t) − μ_LR) + σ × √[(1 − e^{−2θ}) / 2θ] × ε(t)
ε(t) ~ N(0,1)

θ = −ln(1+α)  where α = reversion speed from regression
Half-life HL = ln(2) / θ
```

| Granularity | θ Estimation | Typical HL Range |
|---|---|---|
| Daily | Daily regression on 90-day window | 7–30 days |
| Weekly | Weekly regression on 26-week window | 2–8 weeks |
| Monthly | Monthly regression on 12-month window | 1–4 months |
| Quarterly | Quarterly regression on 4-quarter window | 1–2 quarters |
| Yearly | Annual regression on 3-year window | 1–2 years |

#### 6.4 Fallback: Long-run mean as flat forecast (maximum reversion assumption)

### 7. Ensemble

| History | LightGBM | OU Process | ETS(A,N,N) |
|---|---|---|---|
| Up to 1 year | 20% | 50% | 30% |
| 1–2 years | 35% | 45% | 20% |
| > 2 years | 45% | 40% | 15% |

### 8. Uncertainty Quantification
- Method: OU analytical distribution — exact probability distribution available
- Output: [P10, P50, P90] from OU distribution conditioned on current deviation
- Use case: Deviation from mean triggers safety stock adjustment; large deviations trigger investigation

### 9. Business Rules
- Non-negativity: max(0, forecast)
- Mean anchor: Forecast must converge toward μ_LR as horizon increases
- Deviation alert: If |dev(t)| > 2σ → flag for planner review (unusual deviation)

### 10. Evaluation

| Granularity | WMAPE Target | Mean Convergence Check | Bias Alert |
|---|---|---|---|
| Daily | < 22% | Forecast approaches μ_LR at horizon ≥ 2×HL | \|Bias\| > 10% |
| Weekly | < 18% | Same | \|Bias\| > 8% |
| Monthly | < 15% | Same | \|Bias\| > 7% |
| Quarterly | < 12% | Same | \|Bias\| > 6% |
| Yearly | < 10% | Same | \|Bias\| > 5% |

### 11. Exception Handling
- Alert: ADF p rises above 0.10 (non-stationary → reclassify); half-life estimate > extended window (too slow to confirm reversion); mean level shift detected (structural break → Step Change behavior)

### 12. Reclassification

| Condition | Target | Holding Period |
|---|---|---|
| ADF p ≥ 0.10 for 4 periods | Flat (if no trend) or Upward/Downward Trend | 4 periods |
| FFT cycle detected on residuals | Cyclical Trend | 2 cycles |
| Structural break detected | Step Change (Behavior) | Immediate |

### 13. Review Cadence
- Monthly automated stationarity check; quarterly reversion speed calibration; annual full re-evaluation

---

*End of Dimension 5 · Trend Pattern*
*5 Segments Complete · T1 through T5*
