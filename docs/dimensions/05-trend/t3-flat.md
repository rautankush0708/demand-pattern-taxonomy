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

