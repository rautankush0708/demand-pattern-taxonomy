## E1 · Elastic
### 1. Definition
Predicts demand for SKUs where demand quantity responds more than proportionally to price or promotional stimulus changes (|PED| > 1.0), requiring causal forecasting models that explicitly capture stimulus-response dynamics and promotional planning integration.

### 2. Detailed Description
- **Applicable scenarios:** Discretionary categories, branded FMCG with strong promotional response, price-sensitive consumer electronics, fashion, commoditised categories with easy substitution
- **Boundaries:**

| Granularity | PED Threshold | Promo Uplift Threshold | Min Events | Confidence |
|---|---|---|---|---|
| Daily | PED < −1.0 | > 15% per 10% discount | ≥ 10 price/promo events | R² > 0.30 |
| Weekly | PED < −1.0 | > 15% per 10% discount | ≥ 8 events | R² > 0.30 |
| Monthly | PED < −1.0 | > 15% per 10% discount | ≥ 6 events | R² > 0.30 |
| Quarterly | PED < −1.0 | > 15% per 10% discount | ≥ 4 events | R² > 0.25 |
| Yearly | PED < −1.0 | > 15% per 10% discount | ≥ 3 events | R² > 0.20 |

- **Key demand characteristics:** Strong price-demand relationship; promotional events drive large uplifts; demand highly sensitive to competitor pricing; price reduction creates volume; price increase destroys volume more than proportionally
- **Differentiation from other models:** Unlike Inelastic, demand responds strongly to stimulus; unlike Threshold, response is linear and proportional (not step-change); unlike Saturation, no ceiling effect

### 3. Business Impact
- **Primary risk (over-forecast):** Over-estimating promotional uplift — excess promotional stock
- **Primary risk (under-forecast):** Under-estimating promotional uplift — stockout during promotion; missing the price-driven demand surge
- **Strategic importance:** Very high — elastic SKUs are the primary vehicle for revenue growth through promotional investment; ROI is directly tied to forecast accuracy

### 4. Priority Level
🔴 Tier 1 — Promotional ROI depends entirely on accurate uplift forecasting; elastic SKUs are the promotional workhorses of most FMCG and retail portfolios.

### 5. Model Strategy Overview

#### 5.1 Causal Model Architecture
```
Total demand decomposition:
  d(t) = d_baseline(t) × price_response(t) × promo_response(t) × seasonal_index(t)

Price response:
  price_response(t) = (P_t / P_regular)^PED
  where PED < −1.0 (estimated via log-log regression)

Promotional response:
  promo_response(t) = exp(β_promo × depth(t) + β_type × promo_type(t))
  where depth(t) = discount % from regular price

Combined causal forecast:
  F(t) = baseline(t) × (P_t/P_ref)^β_price × exp(β_promo × depth(t)) × SI(t)
```

#### 5.2 Analogue / Similarity Logic
- Number of analogues: k = 3 (similar elastic SKUs from same category at similar PED)
- Similarity criteria: |PED| range ±0.3, category, price tier, substitutability index
- Use: Supplement own elasticity estimate when own price variation is limited

#### 5.3 Feature Engineering

| Granularity | Price Features | Promo Features | Baseline Features |
|---|---|---|---|
| Daily | Price index (P_t/P_ref), price change flag, log(price), price vs competitor, days since last price change | Promo flag, discount depth (%), promo type, display flag, distribution on promo, days into promo, post-promo dip flag | 7/30/90-day non-promo rolling mean, seasonal index, holiday flag |
| Weekly | Price index, log(price), price change flag, competitor price index | Promo flag, depth, type, week of promo, display flag | 4/8/13-week non-promo rolling mean, seasonal index |
| Monthly | Price index, log(price), price vs category average | Promo flag, depth, promo type, months on promotion | 3/6/12-month non-promo rolling mean, seasonal index |
| Quarterly | Price index, log(price), price position vs market | Promo depth, promo type | 2/4-quarter non-promo rolling mean |
| Yearly | Price index, log(price), long-run price trend | Annual promo intensity | Annual non-promo baseline |

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM with causal price and promo features
- Configuration: Objective = reg:squarederror; Metric = WMAPE, Uplift Accuracy
- Key features: Log price, price index, promo depth, promo type, promo interaction terms (depth × type), post-promo dip, baseline rolling mean, seasonal index, competitor price index
- Interaction terms: price × promo_flag (capture combined price-promo effect); price × season (seasonal price sensitivity variation)
- When to use: Primary model — causal features make LightGBM very effective for elastic demand

#### 6.2 Deep Learning (DL)
- Architectures: TFT with price and promo calendar as known future covariates

| Granularity | Lookback | Future Covariates | Output |
|---|---|---|---|
| Daily | 180 days | Price plan 30 days ahead, promo calendar | P10, P50, P90 |
| Weekly | 52 weeks | Price plan 8 weeks ahead, promo calendar | P10, P50, P90 |
| Monthly | 24 months | Price plan 3 months ahead, promo calendar | P10, P50, P90 |
| Quarterly | 8 quarters | Price plan 1 quarter ahead | P10, P50, P90 |
| Yearly | 5 years | Annual price plan | P10, P50, P90 |

- Training: Loss = quantile loss; Adam lr = 0.001; Dropout = 0.15; Patience = 10
- When to use: When price and promo plans are available as future inputs — significant advantage

#### 6.3 Statistical / Time Series Models
- Architectures: ARIMAX / RegARIMA with price and promo as exogenous variables

**Log-Log ARIMAX:**
```
ln(Q_t) = α + β_price × ln(P_t) + β_promo × depth(t) + β_type × type(t)
         + Σ β_season × SI(t) + ARIMA(p,d,q) residual
β_price = PED (target: < −1.0 for Elastic)
β_promo = uplift per unit of discount depth
```

- When to use: Interpretability requirement; price elasticity reporting; regulatory / trade planning

#### 6.4 Baseline / Fallback Model
- Fallback triggers: Price/promo features missing; insufficient price variation for elasticity estimation
- Fallback model: Baseline rolling mean × category average uplift for promo type
- Logging & alerting: Alert if promo period without causal model coverage; alert if PED estimate reverses sign

### 7. Ensemble & Weighting

#### 7.1 Ensemble Scheme
- Combination: D̂_t = w_lgbm × LightGBM + w_tft × TFT + w_arimax × ARIMAX
- Weight determination: Error-inverse on promotional period WMAPE

#### 7.2 Dynamic Weight Schedule

| Promo Events in History | LightGBM | TFT | ARIMAX |
|---|---|---|---|
| < 6 events | 20% | 20% | 60% |
| 6–12 events | 50% | 20% | 30% |
| > 12 events | 55% | 30% | 15% |

### 8. Uncertainty Quantification
- Method: Quantile regression on causal model residuals
- Output: [P10, P50, P90] — wider during promotional periods (higher uncertainty)
- Use case: Promotional stock buy = P75; post-promo run-down = P25 for residual stock

**Promotional Stock Calculation:**
```
Promo stock needed = F_promo(P75) × promo_duration_periods
                   − existing_stock_on_hand
Post-promo dip duration = HRT_postpromo   [estimate from historical dip patterns]
Post-promo forecast = baseline × (1 − dip_factor × e^{−λ_dip × h})
```

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Promo cap: min(promo_forecast, 3 × baseline rolling mean)
- Post-promo dip correction: max(postpromo_forecast, 0.5 × baseline) — prevent over-correction
- Price increase rule: If price rise > 5% → automatically reduce forecast by |PED| × price_change_%
- Manual overrides: Trade team promo depth confirmation; display confirmation; competitor price response flag
- Alignment: Promotional forecast must align with confirmed promotional stock commitment and distribution

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | Baseline WMAPE | Promo WMAPE | Uplift Accuracy | Elasticity Stability | Bias Alert |
|---|---|---|---|---|---|
| Daily | < 18% | < 25% | < 20% error | CV(PED) < 0.30 | \|Bias\| > 10% |
| Weekly | < 15% | < 22% | < 18% error | CV(PED) < 0.30 | \|Bias\| > 8% |
| Monthly | < 12% | < 20% | < 15% error | CV(PED) < 0.30 | \|Bias\| > 7% |
| Quarterly | < 10% | < 18% | < 12% error | CV(PED) < 0.30 | \|Bias\| > 6% |
| Yearly | < 8% | < 15% | < 10% error | CV(PED) < 0.30 | \|Bias\| > 5% |

#### 10.2 Backtesting Protocol

| Granularity | Method | Train | Test |
|---|---|---|---|
| Daily | Leave-one-promo-out | All promos except last | Last promotion |
| Weekly | Leave-one-promo-out | All promos except last | Last promotion |
| Monthly | Leave-one-promo-out | All promos except last | Last promotion |
| Quarterly | Leave-one-promo-out | All promos except last | Last promotion |
| Yearly | Leave-one-promo-out | All promos except last | Last promotion |

#### 10.3 Retraining

| Granularity | Cadence | Trigger | Latency |
|---|---|---|---|
| Daily | Daily | On price/promo calendar update | T+4 hours |
| Weekly | Weekly | On price/promo update | T+1 day |
| Monthly | Monthly | On monthly price review | T+2 days |
| Quarterly | Quarterly | On quarterly price review | T+3 days |
| Yearly | Annually | On annual pricing strategy | T+7 days |

### 11. Exception Handling & Overrides
- Auto-detect: PED estimate becomes > −0.5 for 3 consecutive estimations → reclassify to Inelastic; uplift consistently < 8% → reclassify; price response R² drops below 0.15 → flag low confidence
- Manual override: Trade manager promo depth confirmation; pricing team price change input; competitor response flag
- Override expiration: Per price/promo event

### 12. Reclassification

| Condition | Target Segment | Holding Period |
|---|---|---|
| PED moves to −0.5 to 0 for 4 consecutive estimates | Inelastic | 4 estimates |
| Non-linear threshold detected (RSS reduction > 20%) | Threshold | 2 estimates |
| Saturation confirmed (Q ≥ 0.90 × Q_max) | Saturation | 2 estimates |

### 13. Review Cadence
- Weekly during active promotional periods; monthly PED stability check; quarterly full elasticity re-estimation; annual pricing strategy alignment

---
