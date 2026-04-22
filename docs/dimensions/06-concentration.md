# Dimension 6 · Concentration Pattern
## Demand Forecasting Model Templates

---

> **Segments:** 5 · Uniform · Peaked · Bi-Modal · Multi-Modal · Skewed
> **Granularities:** Daily · Weekly · Monthly · Quarterly · Yearly
> **Note:** Concentration Pattern describes how demand is **distributed across time periods within a cycle**. It is distinct from Behavior (which captures frequency and variability) and Trend (which captures direction). A Stable Behavior SKU can have a Peaked Concentration if most of its demand clusters in a few periods per cycle.

---

# PART 0 — FORMULA & THRESHOLD REFERENCE
## Concentration Pattern Specific

---

## 0.1 Core Segmentation Metrics

### A. Demand Concentration Index (DCI)
> Measures how unevenly demand is distributed across periods in a cycle

**General Formula:**
```
DCI = Σ [d_p / Σ d_p × (d_p / Σ d_p)]   = Σ s_p²
where s_p = share of period p in total cycle demand
DCI = Σ s_p²

DCI range: 1/n (perfectly uniform) to 1.0 (all demand in one period)
n = number of periods in cycle

Normalised DCI: DCI_norm = (DCI − 1/n) / (1 − 1/n)
DCI_norm = 0 → perfectly uniform
DCI_norm = 1 → all demand in one period
```

| Granularity | Cycle Length (n) | Uniform DCI | Peaked DCI | Formula |
|---|---|---|---|---|
| **Daily** | 7 (weekly cycle) | DCI_norm < 0.15 | DCI_norm > 0.40 | Σ(d_day / Σ d_week)² |
| **Weekly** | 52 (annual cycle) | DCI_norm < 0.10 | DCI_norm > 0.30 | Σ(d_week / Σ d_year)² |
| **Monthly** | 12 (annual cycle) | DCI_norm < 0.10 | DCI_norm > 0.30 | Σ(d_month / Σ d_year)² |
| **Quarterly** | 4 (annual cycle) | DCI_norm < 0.15 | DCI_norm > 0.40 | Σ(d_quarter / Σ d_year)² |
| **Yearly** | Available history | DCI_norm < 0.15 | DCI_norm > 0.40 | Σ(d_year / Σ d_total)² |

---

### B. Gini Coefficient of Demand Distribution
> Alternative concentration measure — more sensitive to inequality across the full distribution

**General Formula:**
```
Gini = 1 − 2 × Σ [F(d_p) × (d_p / Σ d_p)]
where F(d_p) = cumulative frequency up to period p (sorted ascending)

Gini = 0 → perfect equality (uniform demand)
Gini = 1 → perfect inequality (all demand in one period)

Uniform:   Gini < 0.20
Moderate:  0.20 ≤ Gini < 0.50
Peaked:    Gini ≥ 0.50
```

| Granularity | Uniform | Moderate | Peaked |
|---|---|---|---|
| **Daily** | Gini < 0.20 | 0.20–0.50 | > 0.50 |
| **Weekly** | Gini < 0.15 | 0.15–0.40 | > 0.40 |
| **Monthly** | Gini < 0.15 | 0.15–0.40 | > 0.40 |
| **Quarterly** | Gini < 0.20 | 0.20–0.50 | > 0.50 |
| **Yearly** | Gini < 0.20 | 0.20–0.50 | > 0.50 |

---

### C. Modality Detection
> Identifies number of distinct demand peaks within a cycle

**General Formula:**
```
Demand distribution histogram over cycle periods:
  Peak = local maximum where d_p > d_{p-1} AND d_p > d_{p+1}
  Peak is significant if d_p > mean_demand × 1.5

Modes:
  0–1 peaks → Uniform or single-peaked → classify further by DCI
  1 peak    → Peaked
  2 peaks   → Bi-Modal
  3+ peaks  → Multi-Modal

Skewness test (additional check for Skewed classification):
  Pearson skewness = 3 × (mean − median) / std
  |skewness| > 0.5 → demand distribution is skewed
  skewness > 0     → right-skewed (demand concentrated early in cycle)
  skewness < 0     → left-skewed (demand concentrated late in cycle)
```

| Granularity | Significant Peak Threshold | Bi-Modal Gap Requirement |
|---|---|---|
| **Daily** | d_p > μ_daily × 1.5 | Peaks separated by ≥ 2 days |
| **Weekly** | d_p > μ_weekly × 1.5 | Peaks separated by ≥ 4 weeks |
| **Monthly** | d_p > μ_monthly × 1.5 | Peaks separated by ≥ 3 months |
| **Quarterly** | d_p > μ_quarterly × 1.5 | Peaks separated by ≥ 1 quarter |
| **Yearly** | d_p > μ_yearly × 1.5 | Peaks separated by ≥ 1 year |

---

### D. Seasonal Index Dispersion
> Measures how spread the seasonal indices are — high dispersion = concentrated demand

**Formula:**
```
SI(p) = μ_period_p / μ_overall   [multiplicative seasonal index]
SI_dispersion = std(SI) / mean(SI) = CV of seasonal indices

Low dispersion:  SI_dispersion < 0.20 → Uniform
High dispersion: SI_dispersion > 0.50 → Peaked / Multi-Modal
```

| Granularity | Uniform Threshold | Concentrated Threshold |
|---|---|---|
| **Daily** | SI_dispersion < 0.20 | SI_dispersion > 0.50 |
| **Weekly** | SI_dispersion < 0.15 | SI_dispersion > 0.40 |
| **Monthly** | SI_dispersion < 0.15 | SI_dispersion > 0.40 |
| **Quarterly** | SI_dispersion < 0.20 | SI_dispersion > 0.50 |
| **Yearly** | SI_dispersion < 0.20 | SI_dispersion > 0.50 |

---

## 0.2 Concentration Classification Decision Rules

```
STEP 1: Compute DCI_norm and Gini over most recent full cycle
STEP 2: Detect number of significant peaks (modality)
STEP 3: Compute skewness of demand distribution

Classification rules:

  DCI_norm < threshold AND Gini < threshold → UNIFORM
  DCI_norm > threshold AND 1 significant peak → PEAKED
  DCI_norm > threshold AND 2 significant peaks → BI-MODAL
  DCI_norm > threshold AND 3+ significant peaks → MULTI-MODAL
  DCI_norm moderate AND |skewness| > 0.5 → SKEWED

Note: Must use ≥ 2 full cycles to compute reliable DCI and Gini
      Single-cycle estimates are noisy — flag as provisional
```

---

## 0.3 Seasonal Index Formulas

```
Multiplicative SI: SI(p) = μ_period_p / μ_overall
Additive SI:       SI(p) = μ_period_p − μ_overall

Deseasonalised demand: d_adj(t) = d(t) / SI(period_of_t)   [multiplicative]

Seasonal index update (exponential smoothing):
  SI_new(p) = γ × (d(t) / l_t) + (1−γ) × SI_old(p)
  γ ∈ [0.05, 0.20] — low γ preserves stable seasonal pattern

ACF(lag) > 2/√n → Significant seasonality at that lag
Minimum 2 full cycles for reliable SI estimation
```

---

## 0.4 Rolling Window Reference

| Window Name | Daily | Weekly | Monthly | Quarterly | Yearly |
|---|---|---|---|---|---|
| **Short** | 7 days | 4 weeks | 2 months | 1 quarter | 1 year |
| **Medium** | 30 days | 8 weeks | 3 months | 2 quarters | 2 years |
| **Long** | 90 days | 13 weeks | 6 months | 3 quarters | 3 years |
| **Extended** | 180 days | 26 weeks | 12 months | 4 quarters | 4 years |
| **Full Cycle** | 365 days | 52 weeks | 12 months | 4 quarters | Varies |
| **DL Lookback** | 365 days | 104 weeks | 36 months | 12 quarters | 5 years |

---

## 0.5 Accuracy Metric Formulas

```
WMAPE   = Σ|Forecast_t − Actual_t| / Σ Actual_t × 100
Bias    = Σ(Forecast_t − Actual_t) / Σ Actual_t × 100
MAE     = (1/n) × Σ|Forecast_t − Actual_t|

Peak Period WMAPE (critical for Peaked / Bi-Modal / Multi-Modal):
  Peak_WMAPE = Σ_{peak periods}|Forecast_t − Actual_t| / Σ_{peak periods} Actual_t × 100
  Target: Peak_WMAPE < 1.5 × overall WMAPE target

Trough Period WMAPE:
  Trough_WMAPE = Σ_{trough periods}|Forecast_t − Actual_t| / Σ_{trough periods} Actual_t × 100

Pinball(α,t) = α × (Actual_t − Q_α)     if Actual_t ≥ Q_α
             = (1−α) × (Q_α − Actual_t)  if Actual_t < Q_α
Coverage = Actuals within [P10, P90] / n × 100  (Target: 80%)
```

---

## 0.6 Retraining & Backtesting Reference

| Granularity | Retraining | Latency | Backtest Train | Backtest Test |
|---|---|---|---|---|
| **Daily** | Daily | T+4 hours | 365 days (full cycle) | 30 days |
| **Weekly** | Weekly | T+1 day | 104 weeks (2 cycles) | 13 weeks |
| **Monthly** | Monthly | T+2 days | 36 months (3 cycles) | 6 months |
| **Quarterly** | Quarterly | T+3 days | 12 quarters (3 cycles) | 2 quarters |
| **Yearly** | Annually | T+7 days | All available | 1 year |

---

# PART 1 — SEGMENT TEMPLATES

---

## C1 · Uniform

### 1. Definition
Predicts demand for SKUs where demand is distributed evenly across all periods within a cycle, requiring no period-specific adjustment and permitting the simplest forecasting approaches without seasonal index complexity.

### 2. Detailed Description
- **Applicable scenarios:** Essential staples, commodity replenishment, utility-driven demand, subscription-like purchasing patterns
- **Boundaries:**

| Granularity | DCI_norm Threshold | Gini Threshold | SI Dispersion | Min Cycles |
|---|---|---|---|---|
| Daily | DCI_norm < 0.15 | Gini < 0.20 | SI_disp < 0.20 | ≥ 2 weekly cycles |
| Weekly | DCI_norm < 0.10 | Gini < 0.15 | SI_disp < 0.15 | ≥ 2 annual cycles |
| Monthly | DCI_norm < 0.10 | Gini < 0.15 | SI_disp < 0.15 | ≥ 2 annual cycles |
| Quarterly | DCI_norm < 0.15 | Gini < 0.20 | SI_disp < 0.20 | ≥ 2 annual cycles |
| Yearly | DCI_norm < 0.15 | Gini < 0.20 | SI_disp < 0.20 | ≥ 3 years |

- **Key demand characteristics:** Flat intra-cycle distribution; all periods contribute roughly equally to cycle total; seasonal index ≈ 1.0 for all periods; demand driven by steady consumption not calendar events
- **Differentiation from other models:** Unlike Peaked, no dominant period; unlike Skewed, distribution is symmetric; seasonal component adds minimal forecast improvement — level model is sufficient

### 3. Business Impact
- **Primary risk (over-forecast):** Consistent slight over-forecast across all periods — slow inventory build
- **Primary risk (under-forecast):** Consistent slight under-forecast — gradual service level erosion
- **Strategic importance:** Medium-high — uniform demand SKUs are the easiest to manage; focus is on accuracy of the level estimate

### 4. Priority Level
🟠 Tier 2 — Relatively easy to forecast well; primary challenge is maintaining accurate level estimate rather than capturing seasonal shape.

### 5. Model Strategy Overview

#### 5.1 Zero-Demand Handling (Hurdle)
- Active event threshold: P(demand > 0) > 0.90 — uniform demand means consistently active
- Classifier: Rule-based flag only
- Regressor: LightGBM (level features only); ETS(A,N,N) simple smoothing
- Fallback: Rolling mean (extended window)

#### 5.2 Analogue / Similarity Logic
- Not applicable — sufficient own history; uniform demand is stable and reliable

#### 5.3 Feature Engineering

| Granularity | Key Features | Excluded Features | Notes |
|---|---|---|---|
| Daily | 7, 30, 90, 180, 365-day rolling mean, std; day of week flag (low weight); holiday flag | Seasonal index, peak indicators, period-specific dummies | Seasonal features add noise not signal for Uniform |
| Weekly | 4, 8, 13, 26, 52-week rolling mean, std; holiday flag | Week of year index, seasonal index | Same — suppress seasonal |
| Monthly | 2, 3, 6, 12, 24-month rolling mean, std; holiday flag | Month of year index, seasonal index | Same |
| Quarterly | 1, 2, 3, 4-quarter rolling mean, std | Quarter index | Same |
| Yearly | 1, 2, 3, 4-year rolling mean, std | — | Level features only |

- Note: Seasonal index features **explicitly excluded** — including them introduces spurious seasonal adjustment on flat distribution

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM (level-focused; minimal feature set)
- Configuration: Objective = reg:squarederror; Metric = WMAPE, RMSE; max_depth = 4 (prevent overfit on seasonal noise)
- Key features: Rolling means (all windows), rolling std, holiday flag, promo flag
- When to use: Primary model

#### 6.2 Deep Learning (DL)
- Architectures: N-BEATS (generic block — no seasonal block to avoid spurious seasonal injection)

| Granularity | Lookback | Features | Output |
|---|---|---|---|
| Daily | 90 days | 8 | P10, P50, P90 |
| Weekly | 26 weeks | 6 | P10, P50, P90 |
| Monthly | 12 months | 5 | P10, P50, P90 |
| Quarterly | 4 quarters | 4 | P10, P50, P90 |
| Yearly | 3 years | 4 | P10, P50, P90 |

- When to use: History > 2 years; applied selectively — simple models often sufficient for Uniform

#### 6.3 Statistical / Time Series Models
- Architectures: ETS(A,N,N) — simple exponential smoothing (no trend, no seasonality)

**Simple Exponential Smoothing:**
```
l_t = α × d_t + (1−α) × l_{t-1}
F(t+h) = l_t   (flat forecast for all horizons)
α ∈ [0.10, 0.30] — optimised on validation WMAPE
Low α preferred for uniform demand — preserves stable level estimate
```

| Granularity | α Range | Recommended α |
|---|---|---|
| Daily | 0.10–0.25 | 0.15 |
| Weekly | 0.10–0.25 | 0.12 |
| Monthly | 0.08–0.20 | 0.10 |
| Quarterly | 0.08–0.20 | 0.10 |
| Yearly | 0.05–0.15 | 0.08 |

- When to use: Always included — simple smoothing is the natural model for uniform demand

#### 6.4 Baseline / Fallback Model
- Fallback: Rolling mean (extended window) — equivalent to ETS with very low α
- Logging & alerting: Alert if fallback rate > 10%

### 7. Ensemble & Weighting

#### 7.2 Dynamic Weight Schedule

| History Length | LightGBM | ETS(A,N,N) | N-BEATS |
|---|---|---|---|
| Up to 1 year | 40% | 60% | 0% |
| 1–2 years | 50% | 50% | 0% |
| > 2 years | 45% | 40% | 15% |

- Weight determination: Error-inverse on rolling 8-period WMAPE

### 8. Uncertainty Quantification
- Method: Conformal prediction on residuals — symmetric intervals expected for uniform demand
- Output: [P10, P50, P90]
- Use case: Safety stock from σ_residual × z_service_level; symmetric intervals appropriate

**Safety Stock Formula:**
```
SS = z × σ_residual × √(Lead_time + Review_period)
σ_residual = std(Forecast_t − Actual_t) over backtesting period
z = 1.65 for 95% service level
Expected: σ_residual / μ_demand < 0.20 for well-performing Uniform segment
```

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Capping: min(forecast, 1.3 × extended rolling max) — tight cap appropriate for uniform demand
- Floor: max(forecast, 0.7 × extended rolling min) — symmetric floor
- Alignment: ±15% of prior year same period — tighter than other segments due to predictability
- Manual overrides: Level change events only (pricing restructure, distribution change); no seasonal adjustments needed

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | WMAPE Target | Bias Alert | Coverage Target | Period Variance Check |
|---|---|---|---|---|
| Daily | < 15% | \|Bias\| > 6% | 80% P10–P90 | CV of period forecasts < 0.10 |
| Weekly | < 12% | \|Bias\| > 5% | 80% P10–P90 | CV of period forecasts < 0.10 |
| Monthly | < 10% | \|Bias\| > 5% | 80% P10–P90 | CV of period forecasts < 0.10 |
| Quarterly | < 8% | \|Bias\| > 4% | 80% P10–P90 | CV of period forecasts < 0.10 |
| Yearly | < 6% | \|Bias\| > 3% | 80% P10–P90 | CV of period forecasts < 0.08 |

- Period Variance Check: Forecast CV across periods in a cycle should be < 0.10 — confirms uniform pattern maintained in forecast output

#### 10.2 Backtesting Protocol

| Granularity | Train | Test | Min History |
|---|---|---|---|
| Daily | 180 days | 30 days | 365 days |
| Weekly | 52 weeks | 13 weeks | 104 weeks |
| Monthly | 24 months | 6 months | 36 months |
| Quarterly | 8 quarters | 2 quarters | 12 quarters |
| Yearly | All available | 1 year | 3 years |

#### 10.3 Retraining

| Granularity | Cadence | Latency |
|---|---|---|
| Daily | Daily | T+4 hours |
| Weekly | Weekly | T+1 day |
| Monthly | Monthly | T+2 days |
| Quarterly | Quarterly | T+3 days |
| Yearly | Annually | T+7 days |

### 11. Exception Handling & Overrides
- Auto-detect: DCI_norm rises above 0.20 for 2 consecutive cycles → reclassify to Peaked or Skewed; period variance in forecast rises above 0.15 → model introducing spurious seasonal pattern — check feature set
- Manual override: Level change event only — seasonal pattern adjustment not applicable
- Override expiration: Single cycle

### 12. Reclassification

| Condition | Target Segment | Holding Period |
|---|---|---|
| DCI_norm rises above 0.30 for 2 cycles; 1 significant peak | Peaked | 2 cycles |
| DCI_norm rises above 0.30 for 2 cycles; |skewness| > 0.5 | Skewed | 2 cycles |
| DCI_norm rises above 0.30; 2 significant peaks | Bi-Modal | 2 cycles |
| Gini rises above 0.40 for 2 cycles | Peaked or Skewed | 2 cycles |

### 13. Review Cadence
- Weekly automated dashboard; monthly DCI and Gini monitor; quarterly full re-evaluation

---

## C2 · Peaked

### 1. Definition
Predicts demand for SKUs where demand is concentrated in one dominant period within the cycle, requiring period-specific uplift modelling and asymmetric safety stock policies to capture the peak accurately while avoiding excess inventory in non-peak periods.

### 2. Detailed Description
- **Applicable scenarios:** Holiday gift categories, summer peak products, back-to-school, Q4 budget flush categories, single-holiday driven demand
- **Boundaries:**

| Granularity | DCI_norm Threshold | Gini Threshold | Modality | Min Cycles |
|---|---|---|---|---|
| Daily | DCI_norm > 0.40 | Gini > 0.50 | 1 significant peak | ≥ 2 weekly cycles |
| Weekly | DCI_norm > 0.30 | Gini > 0.40 | 1 significant peak | ≥ 2 annual cycles |
| Monthly | DCI_norm > 0.30 | Gini > 0.40 | 1 significant peak | ≥ 2 annual cycles |
| Quarterly | DCI_norm > 0.40 | Gini > 0.50 | 1 significant peak | ≥ 2 annual cycles |
| Yearly | DCI_norm > 0.40 | Gini > 0.50 | 1 significant peak | ≥ 3 years |

- **Key demand characteristics:** One dominant demand period per cycle; remaining periods are troughs; strong seasonal index contrast between peak and non-peak; peak timing is predictable
- **Differentiation from other models:** Unlike Bi-Modal, only one significant peak; unlike Uniform, strong period concentration; unlike Skewed, the concentrated demand is at a specific known point not asymmetrically distributed

### 3. Business Impact
- **Primary risk (over-forecast):** Post-peak overstock — acute markdown pressure after single peak
- **Primary risk (under-forecast):** Stockout during the single peak — no recovery opportunity; peak is the season
- **Strategic importance:** Very high — the peak period often represents 40–70% of annual revenue for this segment

### 4. Priority Level
🔴 Tier 1 — Peak accuracy is mission-critical; one peak per cycle means one chance per year; error is unrecoverable.

### 5. Model Strategy Overview

#### 5.1 Dual-Model Approach
- **Peak model:** Applied during peak window (±n periods around peak); high-complexity model
- **Trough model:** Applied outside peak window; simpler level model
- Peak window definition:

| Granularity | Peak Window |
|---|---|
| Daily | ±3 days around peak day |
| Weekly | ±3 weeks around peak week |
| Monthly | ±1 month around peak month |
| Quarterly | Peak quarter only |
| Yearly | Peak year segment only |

#### 5.2 Analogue / Similarity Logic
- Number of analogues: k = 5 (same SKU prior years + similar category SKUs)
- Similarity criteria: Peak timing (same period ±1), peak SI magnitude ±0.2, category
- Temporal decay: weight = exp(−age / half-life)

| Granularity | Half-Life |
|---|---|
| Daily | 365 days (align to annual cycle) |
| Weekly | 52 weeks |
| Monthly | 12 months |
| Quarterly | 4 quarters |
| Yearly | 3 years |

#### 5.3 Feature Engineering

**Peak Index Features:**
```
peak_proximity(t) = exp(−|t − t_peak| / peak_half_width)
days_to_peak(t) = t_peak − t
days_since_peak(t) = t − t_peak
in_peak_window(t) = 1 if |t − t_peak| ≤ peak_window; else 0
peak_SI(period) = SI(peak_period) — the seasonal index of the peak period
trough_SI(period) = SI(trough_period)
SI_contrast = peak_SI / trough_SI  (ratio of peak to average trough)
```

| Granularity | Peak Features | Trough Features | Shared Features |
|---|---|---|---|
| Daily | Peak proximity, days to/from peak, in-peak flag, peak SI, day-of-peak pattern | Trough rolling mean (excl. peak), trough SI | Rolling mean (deseasonalised), holiday flag, promo flag |
| Weekly | Peak proximity (weeks), weeks to/from peak, in-peak flag, peak SI, week-of-peak pattern | Trough rolling mean | Rolling mean, seasonal index, promo flag |
| Monthly | Peak proximity (months), months to/from peak, in-peak flag, peak SI | Trough rolling mean | Rolling mean, seasonal index |
| Quarterly | In-peak-quarter flag, peak SI, quarters to peak | Trough rolling mean | Rolling mean |
| Yearly | In-peak-year flag, years to peak | — | Rolling mean |

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM — separate models for peak and trough periods
- Peak model: Objective = reg:squarederror; emphasis on peak period accuracy; higher weight on peak observations in training
- Trough model: Objective = reg:squarederror; emphasis on flat trough prediction
- When to use: Primary model — always applied; peak/trough split is key architectural decision

#### 6.2 Deep Learning (DL)
- Architectures: TFT with seasonal decomposition; N-BEATS with seasonality block (captures peak shape)

| Granularity | Lookback | Key Advantage | Output |
|---|---|---|---|
| Daily | 365 days (full annual cycle) | Captures day-level peak shape | P10, P50, P90 |
| Weekly | 104 weeks (2 cycles) | Learns peak week pattern | P10, P50, P90 |
| Monthly | 36 months (3 cycles) | Learns peak month profile | P10, P50, P90 |
| Quarterly | 12 quarters (3 cycles) | Learns peak quarter | P10, P50, P90 |
| Yearly | 5 years | Learns inter-year peak variation | P10, P50, P90 |

- Training: Loss = quantile loss with peak-period upweighting (×3 weight on peak periods); Adam lr = 0.001; Dropout = 0.1; Patience = 15

#### 6.3 Statistical / Time Series Models
- Architectures: ETS(A,N,A) or ETS(M,N,M) with strong seasonal component

**Seasonal Index for Peaked Demand:**
```
SI(peak_period) >> 1.0  (typically 2.0–5.0 for strongly peaked demand)
SI(trough_period) << 1.0 (typically 0.1–0.5)

Update seasonal index with low γ to preserve stable peak pattern:
  SI_new(p) = γ × (d(t) / l_t) + (1−γ) × SI_old(p)
  γ = 0.05–0.10 (lower than standard — peak SI should be stable year-on-year)

Forecast: F(t+h) = l_t × SI(period of t+h)
```

| Granularity | Seasonal Period | γ | Model |
|---|---|---|---|
| Daily | 7 (weekly peak) or 365 (annual peak) | 0.05 | TBATS or ETS(A,N,A) |
| Weekly | 52 (annual peak) | 0.07 | ETS(M,N,M) |
| Monthly | 12 (annual peak) | 0.07 | ETS(M,N,M) or SARIMA |
| Quarterly | 4 (annual peak) | 0.08 | ETS(A,N,A) |
| Yearly | — | — | Trend + SI pattern only |

- When to use: Always included — ETS seasonal models naturally capture single-peak patterns

#### 6.4 Baseline / Fallback Model
- Fallback: Prior year same period × trend adjustment factor
- Peak period fallback: Prior year peak × (1 + trend_rate) — simple and robust
- Logging & alerting: Alert if fallback deployed during peak window — P1 incident for Peaked SKUs

### 7. Ensemble & Weighting

#### 7.1 Ensemble Scheme
- Combination: D̂_t = w_lgbm × LightGBM + w_dl × TFT/NBEATS + w_ets × ETS
- Separate weights for peak vs trough periods

#### 7.2 Dynamic Weight Schedule

| Period | History | LightGBM | TFT / N-BEATS | ETS |
|---|---|---|---|---|
| Peak periods | < 3 cycles | 30% | 0% | 70% |
| Peak periods | 3–5 cycles | 40% | 30% | 30% |
| Peak periods | > 5 cycles | 40% | 35% | 25% |
| Trough periods | All | 50% | 20% | 30% |

### 8. Uncertainty Quantification
- Method: Quantile regression with asymmetric intervals (wider at peak — higher uncertainty)
- Output: [P10, P50, P90] — peak period intervals wider than trough

**Asymmetric Uncertainty:**
```
Peak period:   P90 − P50 > P50 − P10 (right-skewed uncertainty — upside risk of missed peak)
Trough period: Symmetric [P10, P90]
Pre-season buy: Use P75 for peak period stock commitment
```

- Use case: Pre-season buy = P75 of peak period forecast; post-peak run-down using P25

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Peak cap: min(peak_forecast, 3 × trough_mean × peak_SI)
- Trough floor: max(trough_forecast, 0) — allow near-zero in deep trough
- Pre-season lock: Peak period forecast locked 6–8 weeks before peak for procurement; in-season revisions to trough only
- Manual overrides: Buyer peak quantity input; early/late peak timing adjustment (±1 period)
- Alignment: Peak forecast within ±30% of prior year peak actual (wider than standard — peak variability is higher)

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | Overall WMAPE | Peak WMAPE | Trough WMAPE | Bias Alert | Peak Coverage |
|---|---|---|---|---|---|
| Daily | < 25% | < 30% | < 20% | \|Bias\| > 12% | 75% P10–P90 |
| Weekly | < 20% | < 25% | < 15% | \|Bias\| > 10% | 75% P10–P90 |
| Monthly | < 18% | < 22% | < 12% | \|Bias\| > 8% | 80% P10–P90 |
| Quarterly | < 15% | < 20% | < 10% | \|Bias\| > 6% | 80% P10–P90 |
| Yearly | < 12% | < 18% | < 8% | \|Bias\| > 5% | 80% P10–P90 |

#### 10.2 Backtesting Protocol

| Granularity | Train | Test | Peak Backtest Rule |
|---|---|---|---|
| Daily | 2 full cycles | 1 full cycle | Must include ≥ 1 full peak period |
| Weekly | 2 full cycles | 1 full cycle | Must include ≥ 1 full peak period |
| Monthly | 2 full cycles | 1 full cycle | Must include ≥ 1 full peak period |
| Quarterly | 2 full cycles | 1 full cycle | Must include ≥ 1 full peak period |
| Yearly | All available | 1 year | Must include ≥ 1 full peak |

#### 10.3 Retraining

| Granularity | Cadence | Pre-Peak Trigger | Latency |
|---|---|---|---|
| Daily | Daily | Retrain 2 weeks before peak window | T+4 hours |
| Weekly | Weekly | Retrain 4 weeks before peak window | T+1 day |
| Monthly | Monthly | Retrain 2 months before peak window | T+2 days |
| Quarterly | Quarterly | Retrain 1 quarter before peak | T+3 days |
| Yearly | Annually | Pre-season retrain | T+7 days |

### 11. Exception Handling & Overrides
- Auto-detect: Peak timing shifts > 1 period vs prior year → alert and adjust peak window; peak SI changes > 25% vs prior year → flag for buyer review; forecast misses peak by > 30% → P1 incident review
- Manual override: Buyer peak timing adjustment; early/late season call; peak magnitude input from commercial intelligence
- Override expiration: Per peak occurrence

### 12. Reclassification

| Condition | Target Segment | Holding Period |
|---|---|---|
| Second significant peak emerges for 2 cycles | Bi-Modal | 2 cycles |
| DCI_norm drops below 0.15 for 2 cycles | Uniform | 2 cycles |
| 3+ significant peaks detected | Multi-Modal | 2 cycles |
| |skewness| > 0.5 with no clear single peak | Skewed | 2 cycles |

### 13. Review Cadence
- Pre-peak review (6–8 weeks before peak); post-peak debrief within 2 weeks; annual SI calibration; quarterly monitoring

---

## C3 · Bi-Modal

### 1. Definition
Predicts demand for SKUs with two distinct significant demand peaks per cycle, requiring dual-peak modelling and separate peak-specific inventory policies for each of the two demand surges.

### 2. Detailed Description
- **Applicable scenarios:** Summer and winter peaks (apparel, beverages), back-to-school + holiday (stationery, toys), Q1 and Q3 budget cycles, dual-season sports categories
- **Boundaries:**

| Granularity | DCI_norm | Gini | Modality | Peak Separation | Min Cycles |
|---|---|---|---|---|---|
| Daily | DCI_norm > 0.30 | Gini > 0.40 | Exactly 2 significant peaks | ≥ 2 days between peaks | ≥ 2 weekly cycles |
| Weekly | DCI_norm > 0.25 | Gini > 0.35 | Exactly 2 significant peaks | ≥ 4 weeks between peaks | ≥ 2 annual cycles |
| Monthly | DCI_norm > 0.25 | Gini > 0.35 | Exactly 2 significant peaks | ≥ 3 months between peaks | ≥ 2 annual cycles |
| Quarterly | DCI_norm > 0.30 | Gini > 0.40 | Exactly 2 significant peaks | ≥ 1 quarter between peaks | ≥ 2 annual cycles |
| Yearly | DCI_norm > 0.30 | Gini > 0.40 | Exactly 2 significant peaks | ≥ 1 year between peaks | ≥ 4 years |

- **Key demand characteristics:** Two clearly separated demand surges per cycle; each peak has its own magnitude and timing; trough periods between peaks; each peak may have different drivers
- **Differentiation from other models:** Unlike Peaked, two peaks exist — managing them separately is required; unlike Multi-Modal, exactly two peaks; unlike Seasonal (which handles regular multi-peak), the two peaks may have different magnitudes and drivers

### 3. Business Impact
- **Primary risk (over-forecast):** Post-first-peak overstock carried into second peak; combined inventory burden
- **Primary risk (under-forecast):** Stockout at either peak — two windows of high commercial risk per cycle
- **Strategic importance:** High — managing both peaks correctly doubles the commercial opportunity vs single-peak

### 4. Priority Level
🔴 Tier 1 — Two independent peak events per cycle; each is individually high-stakes; combined error impact is significant.

### 5. Model Strategy Overview

#### 5.1 Dual-Peak Decomposition
```
Decompose demand into three components:
  Peak 1 component: Demand attributable to first peak (timed around t_peak1)
  Peak 2 component: Demand attributable to second peak (timed around t_peak2)
  Baseline component: Demand in trough periods between and outside peaks

Peak 1 SI: SI_1(p) = peak 1 period mean / overall mean
Peak 2 SI: SI_2(p) = peak 2 period mean / overall mean
Dual seasonal model: F(t) = baseline × SI_1(period_of_t) × SI_2(period_of_t)
```

#### 5.2 Feature Engineering

| Granularity | Peak 1 Features | Peak 2 Features | Baseline Features |
|---|---|---|---|
| Daily | Peak1 proximity, days to/from peak1, in-peak1 flag, SI_1 | Peak2 proximity, days to/from peak2, in-peak2 flag, SI_2 | 7/30/90-day rolling mean (excl. both peaks), holiday flag |
| Weekly | Weeks to/from peak1, in-peak1 flag, SI_1 | Weeks to/from peak2, in-peak2 flag, SI_2 | 4/8/13-week rolling mean (excl. peaks), promo flag |
| Monthly | Months to/from peak1, SI_1 | Months to/from peak2, SI_2 | 3/6/12-month rolling mean |
| Quarterly | In-peak1-quarter flag, SI_1 | In-peak2-quarter flag, SI_2 | 2/4-quarter rolling mean |
| Yearly | Years to peak1, SI_1 | Years to peak2, SI_2 | Annual baseline |

### 6. Model Families

#### 6.1 ML: LightGBM — three-way split model (peak1 / peak2 / baseline)
- Peak models: Higher complexity; peak-period upweighting in training
- Baseline model: Simpler; level-focused

#### 6.2 DL: TFT with dual seasonal decomposition; TBATS for daily (handles multiple seasonal periods natively)

**TBATS for Bi-Modal:**
```
TBATS(p, {m_1, m_2}, φ, {α, β}, {γ_1, γ_2})
p = number of ARMA components
m_1 = period of seasonal component 1 (distance between peaks)
m_2 = period of seasonal component 2 (full cycle)
Example monthly: TBATS with m_1 = 6 (6-month peak gap), m_2 = 12 (annual)
```

| Granularity | TBATS Configuration |
|---|---|
| Daily | m_1 = days between peaks; m_2 = 365 |
| Weekly | m_1 = weeks between peaks; m_2 = 52 |
| Monthly | m_1 = months between peaks; m_2 = 12 |
| Quarterly | m_1 = quarters between peaks; m_2 = 4 |
| Yearly | BSTS with dual seasonal components |

#### 6.3 Statistical: TBATS (primary for bi-modal) — handles dual seasonality natively

#### 6.4 Fallback: Prior year same period × trend adjustment; separate fallback for each peak

### 7. Ensemble

| Period | LightGBM | TFT/TBATS | ETS |
|---|---|---|---|
| Peak 1 window | 40% | 40% | 20% |
| Peak 2 window | 40% | 40% | 20% |
| Trough periods | 50% | 20% | 30% |

### 8. Uncertainty Quantification
- Output: [P10, P50, P90] — separate intervals for each peak
- Peak 1 buy: P75 of peak1 forecast
- Peak 2 buy: P75 of peak2 forecast (adjusted for unsold Peak1 stock remaining)
- Use case: Dual pre-season buy; inter-peak inventory run-down plan

### 9. Business Rules
- Non-negativity: max(0, forecast)
- Inter-peak run-down rule: Forecast for trough between peaks ≤ remaining peak1 stock / expected trough periods (prevents over-ordering for peak2 when peak1 stock remains)
- Separate peak locks: Peak1 forecast locked separately from Peak2 forecast
- Manual overrides: Independent buyer adjustments for each peak timing and magnitude

### 10. Evaluation

#### 10.1 Key Metrics

| Granularity | Overall WMAPE | Peak1 WMAPE | Peak2 WMAPE | Trough WMAPE | Bias Alert |
|---|---|---|---|---|---|
| Daily | < 28% | < 32% | < 32% | < 18% | \|Bias\| > 12% |
| Weekly | < 22% | < 28% | < 28% | < 15% | \|Bias\| > 10% |
| Monthly | < 20% | < 25% | < 25% | < 12% | \|Bias\| > 8% |
| Quarterly | < 18% | < 22% | < 22% | < 10% | \|Bias\| > 6% |
| Yearly | < 15% | < 20% | < 20% | < 8% | \|Bias\| > 5% |

#### 10.2 Backtesting — must include both peaks in test period; minimum 2 full cycles in train

#### 10.3 Retraining — pre-peak1 retrain + pre-peak2 retrain + standard cadence

### 11. Exception Handling
- Alert: Peak timing shifts > 1 period for either peak; peak magnitude changes > 25%; one peak disappears for 1 cycle → reclassify to Peaked

### 12. Reclassification

| Condition | Target | Holding Period |
|---|---|---|
| One peak disappears for 2 cycles | Peaked | 2 cycles |
| DCI_norm drops below threshold for 2 cycles | Uniform | 2 cycles |
| 3+ peaks emerge for 2 cycles | Multi-Modal | 2 cycles |

### 13. Review Cadence
- Pre-peak1 review; pre-peak2 review; post-cycle debrief; annual full re-evaluation

---

## C4 · Multi-Modal

### 1. Definition
Predicts demand for SKUs with three or more distinct significant demand peaks per cycle, requiring decomposition-based modelling and period-specific inventory policies across multiple demand surges within the same cycle.

### 2. Detailed Description
- **Applicable scenarios:** Weekly promotions creating multiple monthly peaks, quarterly + mid-quarter peaks, multiple holiday categories, product lines with 3+ seasonal occasions
- **Boundaries:**

| Granularity | DCI_norm | Gini | Modality | Min Cycles |
|---|---|---|---|---|
| Daily | DCI_norm > 0.25 | Gini > 0.35 | ≥ 3 significant peaks | ≥ 2 weekly cycles |
| Weekly | DCI_norm > 0.20 | Gini > 0.30 | ≥ 3 significant peaks | ≥ 2 annual cycles |
| Monthly | DCI_norm > 0.20 | Gini > 0.30 | ≥ 3 significant peaks | ≥ 2 annual cycles |
| Quarterly | DCI_norm > 0.25 | Gini > 0.35 | ≥ 3 significant peaks | ≥ 3 annual cycles |
| Yearly | DCI_norm > 0.25 | Gini > 0.35 | ≥ 3 significant peaks | ≥ 5 years |

- **Key demand characteristics:** Multiple demand surges; complex intra-cycle pattern; individual peak accuracy is critical; standard seasonal models underfit
- **Differentiation from other models:** Unlike Bi-Modal, three or more peaks; unlike Peaked, demand is distributed across multiple occasions; most complex Concentration segment

### 3. Business Impact
- **Primary risk (over-forecast):** Simultaneous overstock across multiple peaks — compounding inventory burden
- **Primary risk (under-forecast):** Stockout across multiple occasions — compounding lost sales
- **Strategic importance:** High — complex demand management challenge; model sophistication directly translates to commercial value

### 4. Priority Level
🔴 Tier 1 — Multiple peak management is complex; error at any peak is commercially significant.

### 5. Model Strategy Overview

#### 5.1 Full Decomposition Approach
```
Demand Decomposition:
  d(t) = Baseline(t) + Σ Peak_k(t)   for k = 1 to K peaks

For each peak k:
  Peak_k(t) = A_k × proximity_k(t)
  proximity_k(t) = exp(−|t − t_peak_k| / half_width_k)
  A_k = peak amplitude (estimated from historical data)
  half_width_k = half-width of peak k (periods to decay to 50% of amplitude)

Reconstruct: F(t) = Baseline(t) + Σ A_k × proximity_k(t)
```

#### 5.2 Feature Engineering

| Granularity | Features per Peak (×K peaks) | Baseline Features |
|---|---|---|
| Daily | Proximity_k, days to/from peak_k, in-peak_k flag, SI_k; for k=1 to K | 7/30/90-day rolling mean (excl. all peaks), holiday flag |
| Weekly | Weeks to/from peak_k, in-peak_k flag, SI_k; for k=1 to K | 4/8/13-week rolling mean, promo flag |
| Monthly | Months to/from peak_k, in-peak_k flag, SI_k; for k=1 to K | 3/6/12-month rolling mean |
| Quarterly | In-peak_k flag, SI_k; for k=1 to K | 2/4-quarter rolling mean |
| Yearly | Years to peak_k, SI_k; for k=1 to K | Annual baseline |

### 6. Model Families

#### 6.1 ML: LightGBM with full peak decomposition features; one model per period type (each peak + baseline)

#### 6.2 DL: TBATS (handles multiple seasonal frequencies natively) + TFT with full seasonal decomposition

**TBATS Multi-Modal Configuration:**
```
TBATS(p, {m_1, m_2, ..., m_K}, φ, {α, β}, {γ_1, ..., γ_K})
m_k = period of k-th seasonal component
Optimise m_k via FFT peak detection on detrended series
```

| Granularity | TBATS Components |
|---|---|
| Daily | Up to 3 seasonal components: day-of-week (7), monthly (30), annual (365) |
| Weekly | Up to 3: monthly (4), quarterly (13), annual (52) |
| Monthly | Up to 3: quarterly (3), bi-annual (6), annual (12) |
| Quarterly | Up to 2: bi-annual (2), annual (4) |
| Yearly | BSTS with K seasonal components |

#### 6.3 Statistical: TBATS as primary — designed for multi-seasonal demand

#### 6.4 Fallback: Prior year same period × trend; separate fallback per peak

### 7. Ensemble

| Period Type | LightGBM | TBATS / TFT | Naive Prior Year |
|---|---|---|---|
| Peak periods | 40% | 45% | 15% |
| Trough periods | 50% | 30% | 20% |

### 8. Uncertainty Quantification
- [P10, P50, P90] — separate intervals per peak
- Use case: Individual peak stock buy per peak; consolidated safety stock across all peaks

### 9. Business Rules
- Separate peak locks: Each peak period locked independently for procurement
- Peak priority rule: If stock limited → prioritise highest-revenue peak by SI × expected volume
- Manual overrides: Independent adjustments per peak; peak cancellation flag for any individual peak

### 10. Evaluation

#### 10.1 Key Metrics

| Granularity | Overall WMAPE | Per-Peak WMAPE | Trough WMAPE | Bias Alert |
|---|---|---|---|---|
| Daily | < 30% | < 35% per peak | < 20% | \|Bias\| > 15% |
| Weekly | < 25% | < 30% per peak | < 18% | \|Bias\| > 12% |
| Monthly | < 22% | < 28% per peak | < 15% | \|Bias\| > 10% |
| Quarterly | < 20% | < 25% per peak | < 12% | \|Bias\| > 8% |
| Yearly | < 18% | < 22% per peak | < 10% | \|Bias\| > 6% |

#### 10.2 Backtesting — rolling seasonal window covering full cycle; ≥ 3 cycles in train

#### 10.3 Retraining — pre-each-peak retrain triggered + standard cadence

### 11. Exception Handling
- Alert: Number of peaks changes vs prior cycle → reclassify; any peak amplitude changes > 30%; peak timing shifts > 1 period

### 12. Reclassification

| Condition | Target | Holding Period |
|---|---|---|
| Reduces to 2 peaks for 2 cycles | Bi-Modal | 2 cycles |
| Reduces to 1 peak for 2 cycles | Peaked | 2 cycles |
| DCI_norm drops below threshold | Uniform | 2 cycles |

### 13. Review Cadence
- Pre-each-peak review; post-cycle full debrief; annual TBATS frequency re-calibration

---

## C5 · Skewed

### 1. Definition
Predicts demand for SKUs where demand within a cycle is asymmetrically distributed — concentrated earlier or later in the cycle — requiring asymmetric seasonal indices and lead-time-aware inventory positioning to capture directional demand concentration.

### 2. Detailed Description
- **Applicable scenarios:** Budget-front-loaded categories (spend early in fiscal year), end-of-period purchasing (budget flush), early adopter purchase patterns, product ramp-up within cycle
- **Boundaries:**

| Granularity | Skewness Threshold | DCI_norm | Gini | Min Cycles |
|---|---|---|---|---|
| Daily | \|Pearson skewness\| > 0.5 | 0.15–0.40 | 0.20–0.50 | ≥ 2 weekly cycles |
| Weekly | \|Pearson skewness\| > 0.5 | 0.10–0.30 | 0.15–0.40 | ≥ 2 annual cycles |
| Monthly | \|Pearson skewness\| > 0.5 | 0.10–0.30 | 0.15–0.40 | ≥ 2 annual cycles |
| Quarterly | \|Pearson skewness\| > 0.5 | 0.15–0.40 | 0.20–0.50 | ≥ 2 annual cycles |
| Yearly | \|Pearson skewness\| > 0.5 | 0.15–0.40 | 0.20–0.50 | ≥ 3 years |

**Skewness Direction:**
```
Pearson skewness = 3 × (mean − median) / std

Positive skewness (> 0.5): Right-skewed → demand concentrated EARLY in cycle
  Example: Heavy January demand, tapering through the year (budget front-loading)

Negative skewness (< −0.5): Left-skewed → demand concentrated LATE in cycle
  Example: Low start-of-year demand, heavy December (budget flush, gift buying)
```

- **Key demand characteristics:** Asymmetric within-cycle distribution; demand trails off or builds across the cycle; not a single sharp peak but a gradual concentration at one end
- **Differentiation from other models:** Unlike Peaked, no single dominant period — concentration is gradual; unlike Uniform, distribution is clearly asymmetric; unlike Bi-Modal/Multi-Modal, concentration is at one end of the cycle not in distinct peaks

### 3. Business Impact
- **Primary risk (over-forecast for positive skew):** Over-ordering early; stock depletes quickly then demand falls away leaving no excess — lower risk
- **Primary risk (negative skew over-forecast):** Carrying excess early-cycle stock before late-cycle demand arrives — highest risk for left-skewed categories
- **Strategic importance:** Medium-high — correct timing of stock build relative to skew direction is the key operational challenge

### 4. Priority Level
🟠 Tier 2 — Skew direction determines inventory positioning strategy; medium complexity once direction confirmed.

### 5. Model Strategy Overview

#### 5.1 Skew-Aware Seasonal Index
```
Construct period-specific seasonal indices reflecting asymmetric pattern:

Right-skewed (front-loaded):
  SI(early periods) > 1.0 (demand above average)
  SI(late periods) < 1.0 (demand below average)
  Gradient: Seasonal index decreases monotonically across cycle

Left-skewed (end-loaded):
  SI(early periods) < 1.0
  SI(late periods) > 1.0
  Gradient: Seasonal index increases monotonically across cycle

Compute SI(p) = μ_period_p / μ_overall for each period in cycle
Verify skewness direction: skewness(SI values) confirms direction
```

#### 5.2 Feature Engineering

| Granularity | Skew Direction Features | Cycle Position Features | Rolling Features |
|---|---|---|---|
| Daily | Skewness flag (positive/negative), day in cycle (1 to n), cycle position ratio (day/n), cumulative cycle demand, SI gradient | Day of week, holiday flag, days to cycle end | 7/30-day rolling mean, SI |
| Weekly | Skewness flag, week in cycle, cycle position ratio, cumulative cycle demand, SI gradient | Week of year, promo flag | 4/8-week rolling mean, SI |
| Monthly | Skewness flag, month in cycle, cycle position ratio, SI gradient | Month of year, fiscal period flag | 3/6-month rolling mean, SI |
| Quarterly | Skewness flag, quarter in cycle, cycle position ratio | Fiscal year quarter, budget cycle flag | 2/4-quarter rolling mean, SI |
| Yearly | Skewness flag, year in sequence, cycle position | Budget year flag | Annual rolling mean |

### 6. Model Families

#### 6.1 ML: LightGBM with cycle position and skew direction features
- Objective: reg:squarederror; Metric: WMAPE
- Cycle position ratio is the primary feature — captures gradual within-cycle concentration

#### 6.2 DL: TFT — attention mechanism naturally captures within-cycle asymmetric patterns

| Granularity | Lookback | Key Feature |
|---|---|---|
| Daily | 365 days | Day-in-cycle index |
| Weekly | 104 weeks | Week-in-cycle index |
| Monthly | 36 months | Month-in-cycle index |
| Quarterly | 12 quarters | Quarter-in-cycle index |
| Yearly | 5 years | Year-in-cycle index |

#### 6.3 Statistical: ETS(A,N,A) with asymmetric seasonal indices

**Asymmetric Seasonal Index Update:**
```
For right-skewed (front-loaded): Apply higher weight to early-cycle observations in SI estimation
  γ_early = 0.15 (faster update — early cycle SI more variable)
  γ_late = 0.05 (slower update — late cycle SI stable at low level)

For left-skewed (end-loaded): Reverse — faster update for late periods
  γ_late = 0.15; γ_early = 0.05
```

#### 6.4 Fallback: Prior year same period × (1 + trend_rate); maintains skew pattern from prior year

### 7. Ensemble

| Skew Strength | LightGBM | TFT | ETS(A,N,A) |
|---|---|---|---|
| Mild (\|skewness\| 0.5–1.0) | 45% | 20% | 35% |
| Moderate (\|skewness\| 1.0–2.0) | 50% | 25% | 25% |
| Strong (\|skewness\| > 2.0) | 55% | 30% | 15% |

### 8. Uncertainty Quantification
- Method: Quantile regression with cycle-position-conditioned intervals
- Output: [P10, P50, P90] — asymmetric across cycle (wider early for right-skew; wider late for left-skew)
- Use case:
  - Right-skew: Stock early at P75; reduce to P25 for later periods
  - Left-skew: Conservative early stock at P25; build to P75 approach to cycle end

### 9. Business Rules
- Non-negativity: max(0, forecast)
- Inventory build timing rule: Right-skew → front-load inventory; Left-skew → hold stock, build toward cycle end
- Alignment: SI gradient direction must match historical skew direction — alert if reversed
- Manual overrides: Budget cycle change (fiscal year shift); pricing structure change affecting skew direction

### 10. Evaluation

#### 10.1 Key Metrics

| Granularity | WMAPE Target | Early-Cycle WMAPE | Late-Cycle WMAPE | Bias Alert | Skew Direction Accuracy |
|---|---|---|---|---|---|
| Daily | < 22% | < 25% | < 20% | \|Bias\| > 10% | Direction correct > 90% of cycles |
| Weekly | < 18% | < 22% | < 18% | \|Bias\| > 8% | Direction correct > 90% |
| Monthly | < 15% | < 18% | < 15% | \|Bias\| > 7% | Direction correct > 90% |
| Quarterly | < 12% | < 15% | < 12% | \|Bias\| > 6% | Direction correct > 90% |
| Yearly | < 10% | < 12% | < 10% | \|Bias\| > 5% | Direction correct > 90% |

#### 10.2 Backtesting — rolling seasonal window ≥ 2 full cycles; evaluate early and late cycle separately

#### 10.3 Retraining — standard cadence + triggered on fiscal year / budget cycle change

### 11. Exception Handling
- Alert: Skew direction reverses vs prior cycle → investigate structural change; |skewness| drops below 0.3 for 2 cycles → reclassify to Uniform or Peaked

### 12. Reclassification

| Condition | Target | Holding Period |
|---|---|---|
| |skewness| drops below 0.3 for 2 cycles; DCI_norm below threshold | Uniform | 2 cycles |
| Single clear peak emerges for 2 cycles | Peaked | 2 cycles |
| |skewness| drops below 0.3; single peak remains high | Peaked | 2 cycles |
| Two peaks emerge at opposite ends of skew for 2 cycles | Bi-Modal | 2 cycles |

### 13. Review Cadence
- Quarterly skewness monitor; annual skew direction confirmation; full re-evaluation on any fiscal/budget cycle change

---

*End of Dimension 6 · Concentration Pattern*
*5 Segments Complete · C1 through C5*
