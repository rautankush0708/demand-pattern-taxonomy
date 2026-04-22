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
