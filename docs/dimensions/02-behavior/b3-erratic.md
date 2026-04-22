## B3 · Erratic
### 1. Definition
Predicts demand for SKUs with high demand variance (CV² ≥ 0.49) and high demand frequency (ADI below granularity threshold), where demand occurs regularly but in highly unpredictable quantities.

### 2. Detailed Description
- **Applicable scenarios:** Promotional items, fashion/seasonal lines, weather-sensitive categories, volatile B2C demand
- **Boundaries:**

| Granularity | ADI Threshold | CV² Threshold |
|---|---|---|
| Daily | ADI < 1.10 | CV² ≥ 0.49 |
| Weekly | ADI < 1.32 | CV² ≥ 0.49 |
| Monthly | ADI < 1.25 | CV² ≥ 0.49 |
| Quarterly | ADI < 1.20 | CV² ≥ 0.49 |
| Yearly | ADI < 1.10 | CV² ≥ 0.49 |

- **Key demand characteristics:** Regular occurrence, high quantity variance, difficult to forecast quantity even when timing is known
- **Differentiation from other models:** Unlike Stable, CV² is high; unlike Lumpy, ADI is below threshold (demand occurs regularly); unlike Intermittent, demand is frequent

### 3. Business Impact
- **Primary risk (over-forecast):** Significant inventory when demand dips unexpectedly
- **Primary risk (under-forecast):** Stockouts during demand spikes — lost sales and poor service
- **Strategic importance:** High — erratic SKUs are often promotional or trend-driven with high revenue potential

### 4. Priority Level
🔴 Tier 1 — High frequency means high absolute volume impact; variance makes both over and under-forecast costly.

### 5. Model Strategy Overview

#### 5.1 Zero-Demand Handling (Hurdle)
- Active event threshold: P(demand > 0) > 0.70 — demand is frequent; focus on quantity not occurrence
- Classifier type: Rule-based — flag only when consecutive zeros appear
- Regressor type: LightGBM / CatBoost with variance-aware objective
- Fallback: Rolling mean with wide prediction intervals

#### 5.2 Analogue / Similarity Logic
- Number of analogues: k = 3 (erratic SKUs from same category at similar CV² level)
- Similarity criteria: Category, CV² range ±0.1, ADI range ±0.3, price tier
- Temporal decay: weight = exp(−age / half-life)

| Granularity | Half-Life |
|---|---|
| Daily | 14 days |
| Weekly | 4 weeks |
| Monthly | 2 months |
| Quarterly | 1 quarter |
| Yearly | 1 year |

#### 5.3 Feature Engineering

| Granularity | Rolling Windows | Additional Features |
|---|---|---|
| Daily | 7, 14, 30, 90-day mean, std, CV², max | Day of week, holiday, promo flag, weather index |
| Weekly | 4, 8, 13, 26-week mean, std, CV², max | Week of year, promo flag, competitor activity |
| Monthly | 2, 3, 6, 12-month mean, std, CV², max | Month of year, promo depth, price elasticity index |
| Quarterly | 1, 2, 3, 4-quarter mean, std, CV², max | Quarter, promo flag |
| Yearly | 1, 2, 3-year mean, std, CV², max | Long cycle, macro index |

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM / CatBoost
- Configuration: Objective = reg:squarederror with quantile outputs; Metric = WMAPE, Pinball loss
- Key features: Rolling means, rolling CV², rolling max, promo flag, holiday flag, day/week of year, price index
- When to use: Primary model — tabular features capture variance drivers well

#### 6.2 Deep Learning (DL)
- Architectures: TFT with quantile outputs

| Granularity | Lookback | Features | Output |
|---|---|---|---|
| Daily | 90 days | 15 | P10, P25, P50, P75, P90 |
| Weekly | 52 weeks | 12 | P10, P25, P50, P75, P90 |
| Monthly | 24 months | 10 | P10, P25, P50, P75, P90 |
| Quarterly | 8 quarters | 8 | P10, P25, P50, P75, P90 |
| Yearly | 5 years | 6 | P10, P25, P50, P75, P90 |

- Training: Loss = quantile loss (multiple quantiles); Adam lr = 0.001; Dropout = 0.2; Patience = 10
- When to use: When variance structure is complex and multi-quantile output is needed

#### 6.3 Statistical / Time Series Models
- Architectures: SARIMA with heteroscedastic errors; TBATS for dual seasonality at daily level
- When to use: Interpretability requirement; short history

#### 6.4 Baseline / Fallback Model
- Fallback triggers: Model convergence failure; missing external features
- Fallback model: Rolling mean (medium window) with ±1.5σ prediction interval
- Logging & alerting: Alert if fallback rate > 20%

### 7. Ensemble & Weighting

#### 7.1 Ensemble Scheme
- Combination: D̂_t = w_lgbm × LightGBM + w_tft × TFT + w_stat × SARIMA
- Weight determination: Error-inverse weighting on Pinball loss (P50) over 8-period rolling window

#### 7.2 Dynamic Weight Schedule

| History Length | LightGBM | TFT | SARIMA |
|---|---|---|---|
| Up to 6 months equiv. | 70% | 0% | 30% |
| 6–12 months equiv. | 60% | 30% | 10% |
| > 12 months equiv. | 50% | 40% | 10% |

### 8. Uncertainty Quantification
- Method: Quantile regression — full distribution output
- Output: [P10, P25, P50, P75, P90] — wider interval needed for erratic demand
- Use case: Safety stock at P75 or P90 depending on service level target

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Capping: min(forecast, 2 × rolling max over long window)
- Manual overrides: Promotional plan inputs; event uplift; competitor action flags
- Alignment: Forecast must be consistent with promotional calendar uplifts

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | WMAPE Target | Bias Alert | Pinball Coverage |
|---|---|---|---|
| Daily | < 35% | \|Bias\| > 15% | 80% P10–P90 |
| Weekly | < 30% | \|Bias\| > 12% | 80% P10–P90 |
| Monthly | < 25% | \|Bias\| > 10% | 80% P10–P90 |
| Quarterly | < 20% | \|Bias\| > 8% | 80% P10–P90 |
| Yearly | < 15% | \|Bias\| > 6% | 80% P10–P90 |

#### 10.2 Backtesting Protocol

| Granularity | Train | Test |
|---|---|---|
| Daily | 180 days | 30 days |
| Weekly | 52 weeks | 13 weeks |
| Monthly | 24 months | 6 months |
| Quarterly | 8 quarters | 2 quarters |
| Yearly | All available | 1 year |

### 11. Exception Handling & Overrides
- Automatic exception detection: Forecast > 3 × rolling max; CV² drops below 0.49 for 8 periods (→ Stable)
- Manual override: Commercial team promo/event input; reason logged

### 12. Reclassification / Model Selection

| Condition | Target Segment | Holding Period |
|---|---|---|
| CV² drops below 0.49 for 8 periods | Stable | 8 periods |
| ADI rises above threshold for 8 periods | Lumpy | 8 periods |
| Structural break detected | Step Change | Immediate |
| Volume drops below 5th percentile | Slow Mover | 8 periods |

### 13. Review Cadence
- Performance monitoring: Per cycle — Pinball loss and CV² drift monitored
- Model review meeting: Weekly for high-value erratic SKUs; bi-weekly otherwise
- Full model re-evaluation: Quarterly

---
