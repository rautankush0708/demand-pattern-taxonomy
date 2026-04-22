## D3 · Promotional

### 1. Definition
Predicts demand for SKUs where internal pricing and trade promotion activities cause statistically significant demand uplifts, requiring promotion calendar integration, uplift modelling, and post-promotion dip correction.

### 2. Detailed Description
- **Applicable scenarios:** Price promotions, multi-buy offers, display/feature promotions, trade deal periods, loyalty reward events, clearance sales
- **Boundaries:**

| Granularity | Detection Condition | Promo Window |
|---|---|---|
| Daily | Uplift > 15% during promotion; p < 0.05 | Duration of promotion |
| Weekly | Uplift > 15% during promotion; p < 0.05 | Duration of promotion |
| Monthly | Uplift > 15% during promotion; p < 0.05 | Duration of promotion |
| Quarterly | Uplift > 15% during promotion; p < 0.05 | Duration of promotion |
| Yearly | Uplift > 15% during promotion; p < 0.05 | Duration of promotion |

- **Key demand characteristics:** Demand spike during promotion; post-promotion dip (demand pull-forward); baseline demand between promotions; promotion frequency and depth are key drivers
- **Differentiation from other models:** Unlike Event Driven, promotions are internally controlled and planned; unlike Seasonal, timing is commercially set not calendar-driven; post-promo dip is a distinct Promotional characteristic

### 3. Business Impact
- **Primary risk (over-forecast):** Excess promotional stock left after promotion ends; post-promo inventory overhang
- **Primary risk (under-forecast):** Out-of-stock during promotion — lost sales at promoted price; retailer penalty
- **Strategic importance:** Very high — promotional ROI is directly linked to forecast accuracy

### 4. Priority Level
🔴 Tier 1 — Promotional forecast errors have immediate P&L impact; over-stock post-promo forces clearance at further discount.

### 5. Model Strategy Overview

#### 5.1 Zero-Demand Handling (Hurdle)
- Active event threshold: P(demand > 0) > 0.85 during promotion; standard threshold in baseline
- Classifier: Rule-based — promotional period always active
- Regressor: LightGBM with promotion depth and type features

#### 5.2 Analogue / Similarity Logic
- Number of analogues: k = 5 (prior promotions of same type on same or similar SKU)
- Similarity criteria: Promotion type (price/multi-buy/display), discount depth ±5%, category, season
- Temporal decay: weight = exp(−age / half-life)

| Granularity | Half-Life |
|---|---|
| Daily | 90 days |
| Weekly | 13 weeks |
| Monthly | 6 months |
| Quarterly | 3 quarters |
| Yearly | 2 years |

- Aggregation: Weighted mean of promotion uplift profiles

#### 5.3 Feature Engineering

**Promotional Feature Construction:**
```
Promo flag:         1 if period is promotional; 0 otherwise
Promo depth:        (Regular price − Promo price) / Regular price
Promo type:         One-hot encoded {price_cut, multibuy, display, TPR, clearance}
Promo duration:     Number of periods promotion is active
Days into promo:    t_current − t_promo_start
Days left in promo: t_promo_end − t_current
Post-promo flag:    1 if within post-promo dip window; 0 otherwise
Post-promo day:     t_current − t_promo_end (for dip modelling)
Baseline demand:    Rolling mean on non-promo periods (deseasonalised)
Uplift factor:      Estimated = f(promo_depth, promo_type, category_elasticity)
```

| Granularity | Promo Features | Baseline Features |
|---|---|---|
| Daily | Promo flag, depth, type, days into/left in promo, post-promo flag, post-promo day, distribution on promotion | 7/30/90-day non-promo rolling mean, seasonal index, day of week |
| Weekly | Promo flag, depth, type, week of promo, post-promo flag, distribution coverage | 4/8/13-week non-promo rolling mean, seasonal index |
| Monthly | Promo flag, depth, type, month of promo, post-promo dip flag | 3/6/12-month non-promo rolling mean, seasonal index |
| Quarterly | Promo flag, depth, type, post-promo flag | 2/4-quarter non-promo rolling mean |
| Yearly | Annual promo count, average depth | Annual non-promo baseline |

- External signals: Promotion calendar feed, retailer feature/display confirmation, distribution on promotion, competitor promotional activity

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM — separate models for promotional and baseline periods
- Configuration (promo model): Objective = reg:squarederror; Metric = WMAPE, Uplift Accuracy
- Configuration (baseline model): Objective = reg:squarederror; Metric = WMAPE
- Key features: All promotional features, price elasticity index, category promotional intensity, competitive promo flag
- When to use: Primary model when ≥ 5 prior promotions in history

#### 6.2 Deep Learning (DL)
- Architectures: TFT with promotion calendar as known future covariate

| Granularity | Lookback | Future Covariates | Output |
|---|---|---|---|
| Daily | 180 days | Promo calendar 30 days ahead | P10, P50, P90 |
| Weekly | 52 weeks | Promo calendar 8 weeks ahead | P10, P50, P90 |
| Monthly | 24 months | Promo calendar 3 months ahead | P10, P50, P90 |
| Quarterly | 8 quarters | Promo calendar 1 quarter ahead | P10, P50, P90 |
| Yearly | 5 years | Annual promo plan | P10, P50, P90 |

- Training: Loss = quantile loss; Adam lr = 0.001; Dropout = 0.15; Patience = 10
- When to use: When promo calendar available as future input; complex promo patterns

#### 6.3 Statistical / Time Series Models
- Architectures: RegARIMA with promotion dummy variables + post-promo dip correction

**Promotional Uplift Model:**
```
d_promo(t) = d_baseline(t) × (1 + β_uplift × promo_depth(t) × promo_type_factor)
d_postpromo(t) = d_baseline(t) × (1 + β_dip × post_promo_day(t))

β_uplift estimated from historical promotions via OLS
β_dip estimated from post-promo periods via OLS
promo_type_factor = {price_cut: 1.0, multibuy: 0.8, display: 0.6, TPR: 0.9}
```

- When to use: Interpretability required; uplift coefficients needed for trade planning

#### 6.4 Baseline / Fallback Model
- Fallback triggers: No prior promotions; promotion calendar missing
- Fallback model: Baseline forecast × category average uplift factor for promotion type
- Logging & alerting: Alert if promo period detected without model coverage; alert if post-promo dip not modelled

### 7. Ensemble & Weighting

#### 7.1 Ensemble Scheme
- Combination: D̂_t = w_lgbm × LightGBM + w_tft × TFT + w_stat × RegARIMA
- Weight determination: Error-inverse on promotional period WMAPE

#### 7.2 Dynamic Weight Schedule

| Prior Promotions in History | LightGBM | TFT | RegARIMA |
|---|---|---|---|
| < 5 promotions | 20% | 30% | 50% |
| 5–10 promotions | 50% | 20% | 30% |
| > 10 promotions | 60% | 30% | 10% |

### 8. Uncertainty Quantification
- Method: Quantile regression on promotional residuals
- Output: [P10, P50, P90] — wider during promotion; narrower in baseline
- Use case: Promotional stock buy = P75; post-promo rundown = P25 for residual stock

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Promo cap: min(forecast, 3 × baseline rolling mean)
- Post-promo dip: max(forecast_postpromo, 0.5 × baseline) — prevent over-correction
- Manual overrides: Trade team promotional depth confirmation; display confirmation; retailer acceptance
- Alignment: Promotional forecast must align with confirmed promotional stock commitment

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | Promo WMAPE Target | Baseline WMAPE | Post-Promo Dip Accuracy | Bias Alert |
|---|---|---|---|---|
| Daily | < 25% | < 20% | Dip within ±20% of actual | \|Bias\| > 12% |
| Weekly | < 22% | < 18% | Dip within ±18% | \|Bias\| > 10% |
| Monthly | < 20% | < 15% | Dip within ±15% | \|Bias\| > 8% |
| Quarterly | < 18% | < 12% | Dip within ±12% | \|Bias\| > 6% |
| Yearly | < 15% | < 10% | — | \|Bias\| > 5% |

#### 10.2 Backtesting Protocol

| Granularity | Method | Train | Test |
|---|---|---|---|
| Daily | Leave-one-promo-out | All promos except last | Last promotion |
| Weekly | Leave-one-promo-out | All promos except last | Last promotion |
| Monthly | Leave-one-promo-out | All promos except last | Last promotion |
| Quarterly | Leave-one-promo-out | All promos except last | Last promotion |
| Yearly | Leave-one-promo-out | All promos except last | Last promotion |

#### 10.3 Retraining & Data Freshness

| Granularity | Cadence | Event Trigger | Latency |
|---|---|---|---|
| Daily | Daily | On promo calendar update | T+4 hours |
| Weekly | Weekly | On promo calendar update | T+1 day |
| Monthly | Monthly | On promo calendar update | T+2 days |
| Quarterly | Quarterly | On promo plan update | T+3 days |
| Yearly | Annually | On annual plan | T+7 days |

### 11. Exception Handling & Overrides
- Automatic exception detection: Promo period demand < baseline (promotion had no effect → flag for review); post-promo demand > promo demand (demand timing anomaly); forecast > 3 × baseline during non-promo period
- Manual override process: Trade manager promo depth confirmation; display uplift manual input; logistics team stock availability confirmation
- Override expiration: Per promotion occurrence

### 12. Reclassification / Model Selection
- Remove Promotional driver: If uplift consistently < 10% across last 5 promotions (promotion-insensitive)
- Promote to Event Driven: If promotions are discrete, non-recurring events rather than regular trade activity
- Add Seasonal driver: If promotional calendar aligns with seasonal peaks

### 13. Review Cadence
- Performance monitoring: Per promotion debrief within 1 week post-promotion end
- Model review meeting: Monthly promotional planning review with trade/commercial team
- Full model re-evaluation: Quarterly or after major promotional strategy change

---

