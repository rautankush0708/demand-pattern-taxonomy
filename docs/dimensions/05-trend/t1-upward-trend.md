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
