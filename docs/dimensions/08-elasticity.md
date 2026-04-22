# Dimension 8 · Elasticity Pattern
## Demand Forecasting Model Templates

---

> **Segments:** 4 · Elastic · Inelastic · Threshold · Saturation
> **Granularities:** Daily · Weekly · Monthly · Quarterly · Yearly
> **Note:** Elasticity Pattern describes how demand **responds to external stimuli** — primarily price changes, promotional depth, and marketing spend. It is a pure demand-side classification measuring sensitivity of demand quantity to stimulus magnitude. Elasticity is estimated from historical stimulus-response data and used to calibrate causal forecasting models and promotional planning inputs.

---

# PART 0 — FORMULA & THRESHOLD REFERENCE
## Elasticity Pattern Specific

---

## 0.1 Core Segmentation Metrics

### A. Price Elasticity of Demand (PED)
> Measures percentage change in demand for a 1% change in price

**General Formula:**
```
PED = % Change in Quantity Demanded / % Change in Price
    = (ΔQ / Q) / (ΔP / P)
    = (dQ/dP) × (P/Q)

PED < 0 always (inverse relationship — higher price → lower demand)
|PED| < 1 → Inelastic (demand changes less than price)
|PED| = 1 → Unit elastic
|PED| > 1 → Elastic (demand changes more than price)
|PED| > 2 → Highly elastic
```

**Log-Log Regression Estimation:**
```
ln(Q_t) = α + β × ln(P_t) + γ × X_t + ε_t
where β = PED (directly estimated)
      X_t = control variables (seasonality, promotions, distribution)
      β < −1 → Elastic
      −1 < β < 0 → Inelastic
```

| Granularity | Estimation Window | Min Price Changes Required | Method |
|---|---|---|---|
| **Daily** | 180-day rolling | ≥ 10 price change events | Log-log OLS with controls |
| **Weekly** | 52-week rolling | ≥ 8 price change events | Log-log OLS with controls |
| **Monthly** | 24-month rolling | ≥ 6 price change events | Log-log OLS with controls |
| **Quarterly** | 8-quarter rolling | ≥ 4 price change events | Log-log OLS with controls |
| **Yearly** | 3-year rolling | ≥ 3 price change events | Log-log OLS with controls |

---

### B. Promotional Elasticity
> Measures demand response to promotional discount depth

**General Formula:**
```
Promo Elasticity = % Change in Demand / % Change in Price (during promotion)
                = ln(Q_promo / Q_baseline) / ln(P_promo / P_regular)

Uplift Factor = Q_promo / Q_baseline − 1   [expressed as % uplift per % discount]
```

**Estimation:**
```
Q_promo(t) = Q_baseline(t) × exp(β_promo × depth(t) + β_type × promo_type(t))
where depth(t) = (P_regular − P_promo) / P_regular × 100   [% discount]
      β_promo = promotional elasticity coefficient
      β_type = promotion type multiplier {price_cut, multibuy, display, TPR}
```

| Granularity | Min Promotions Required | Controls |
|---|---|---|
| **Daily** | ≥ 8 promotion events | Season, baseline trend, distribution |
| **Weekly** | ≥ 6 promotion events | Season, baseline trend |
| **Monthly** | ≥ 5 promotion events | Season, trend |
| **Quarterly** | ≥ 4 promotion events | Trend |
| **Yearly** | ≥ 3 promotion events | Trend |

---

### C. Threshold Detection
> Identifies non-linear demand response with a stimulus activation threshold

**General Formula:**
```
Demand response is non-linear:
  d(t) = d_baseline(t)                           if stimulus(t) < threshold
  d(t) = d_baseline(t) × response_factor(t)     if stimulus(t) ≥ threshold

Threshold estimation:
  Fit piecewise regression with unknown breakpoint T*:
  Q(t) = α + β_1 × stimulus(t) × I(stimulus < T*) + β_2 × stimulus(t) × I(stimulus ≥ T*)
  Estimate T* via grid search: minimise RSS across candidate threshold values T* ∈ [5%, 50%]

Threshold confirmed: RSS reduction > 20% vs linear model AND p < 0.05 for β_2 − β_1
```

| Granularity | Grid Search Range | Step Size | Min Events Above Threshold |
|---|---|---|---|
| **Daily** | 5%–50% discount depth | 2.5% | ≥ 5 events |
| **Weekly** | 5%–50% discount depth | 2.5% | ≥ 5 events |
| **Monthly** | 5%–50% discount depth | 5% | ≥ 4 events |
| **Quarterly** | 5%–50% discount depth | 5% | ≥ 3 events |
| **Yearly** | 5%–50% discount depth | 10% | ≥ 3 events |

---

### D. Saturation Detection
> Identifies maximum demand ceiling beyond which additional stimulus generates no further response

**General Formula:**
```
Saturation model:
  Q(t) = Q_max × [1 − e^{−λ × stimulus(t)}]   [Logistic saturation curve]
  where Q_max = demand ceiling (estimated via NLS)
        λ = rate of saturation

Saturation confirmed:
  (1) Q_max estimated and statistically significant (p < 0.05)
  (2) Current observed demand at stimulus peak ≥ 0.90 × Q_max
  (3) Marginal response at high stimulus < 10% of marginal response at low stimulus

Alternative: Adstock diminishing returns model:
  Response(t) = β_1 × stimulus(t)^β_2   where β_2 < 1 → diminishing returns
  β_2 < 0.50 → strong saturation signal
```

| Granularity | NLS Estimation Window | Saturation Threshold |
|---|---|---|
| **Daily** | 365-day rolling | Observed demand ≥ 0.90 × Q_max |
| **Weekly** | 104-week rolling | Observed demand ≥ 0.90 × Q_max |
| **Monthly** | 36-month rolling | Observed demand ≥ 0.90 × Q_max |
| **Quarterly** | 12-quarter rolling | Observed demand ≥ 0.90 × Q_max |
| **Yearly** | 5-year rolling | Observed demand ≥ 0.90 × Q_max |

---

## 0.2 Elasticity Classification Decision Rules

```
STEP 1: Estimate PED via log-log regression (Section 0.1A)
  Sufficient price variation detected?
    YES → proceed with PED estimate
    NO  → use Promotional Elasticity as proxy (Section 0.1B)

STEP 2: Test for non-linearity
  Run Threshold detection (Section 0.1C)
  Threshold confirmed? → THRESHOLD segment

  Run Saturation detection (Section 0.1D)
  Saturation confirmed? → SATURATION segment

STEP 3: Apply linear elasticity classification (if no non-linearity)
  |PED| > 1.0 OR Promo Elasticity β_promo > 0.015/% → ELASTIC
  |PED| < 1.0 AND Promo Elasticity β_promo < 0.008/% → INELASTIC

Confidence rules:
  < minimum price changes required → provisional estimate; flag as low confidence
  Conflicting PED and Promo Elasticity signals → use Promo Elasticity (more data)
  Coefficient of variation of PED estimates > 0.50 → flag as unstable elasticity
```

---

## 0.3 Elasticity Coefficient Reference Table

| Segment | PED Range | Promo Uplift per 10% Discount | Behaviour |
|---|---|---|---|
| **Elastic** | PED < −1.0 | > 15% uplift | Large demand response to small price/promo change |
| **Inelastic** | −1.0 < PED < 0 | < 8% uplift | Small demand response to large price/promo change |
| **Threshold** | Non-linear (PED varies by stimulus level) | < 5% below T*; > 20% above T* | No response below threshold; large response above |
| **Saturation** | Diminishing (PED → 0 at high stimulus) | > 20% at low stimulus; < 5% at high stimulus | Strong early response; caps at ceiling |

---

## 0.4 Rolling Window Reference

| Window Name | Daily | Weekly | Monthly | Quarterly | Yearly |
|---|---|---|---|---|---|
| **Short** | 7 days | 4 weeks | 2 months | 1 quarter | 1 year |
| **Medium** | 30 days | 8 weeks | 3 months | 2 quarters | 2 years |
| **Long** | 90 days | 13 weeks | 6 months | 3 quarters | 3 years |
| **Estimation** | 180 days | 52 weeks | 24 months | 8 quarters | 3 years |
| **DL Lookback** | 180 days | 52 weeks | 24 months | 8 quarters | 5 years |

---

## 0.5 Accuracy Metric Formulas

```
Standard metrics:
  WMAPE = Σ|Forecast_t − Actual_t| / Σ Actual_t × 100
  Bias  = Σ(Forecast_t − Actual_t) / Σ Actual_t × 100

Elasticity-specific metrics:
  Uplift Accuracy = |Predicted Uplift − Actual Uplift| / Actual Uplift × 100
  Elasticity Stability = CV(PED estimates over rolling windows)  (Target < 0.30)
  Price Response R² = R² of log-log regression (Target > 0.30)
  Promotion Forecast Lift = WMAPE improvement vs no-promo model (Target > 10%)

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

## E2 · Inelastic

### 1. Definition
Predicts demand for SKUs where demand quantity responds less than proportionally to price or promotional stimulus changes (|PED| < 1.0), where causal features add minimal forecast value and standard time-series methods are more reliable than causal models.

### 2. Detailed Description
- **Applicable scenarios:** Essential staples, habitual purchases, medically/nutritionally necessary products, utility-like demand, high switching-cost categories, brand-loyal categories with low substitutability
- **Boundaries:**

| Granularity | PED Range | Promo Uplift Threshold | Min Events | Confidence |
|---|---|---|---|---|
| Daily | −1.0 < PED < 0 | < 8% per 10% discount | ≥ 8 events | R² < 0.20 |
| Weekly | −1.0 < PED < 0 | < 8% per 10% discount | ≥ 6 events | R² < 0.20 |
| Monthly | −1.0 < PED < 0 | < 8% per 10% discount | ≥ 5 events | R² < 0.20 |
| Quarterly | −1.0 < PED < 0 | < 8% per 10% discount | ≥ 4 events | R² < 0.15 |
| Yearly | −1.0 < PED < 0 | < 8% per 10% discount | ≥ 3 events | R² < 0.15 |

- **Key demand characteristics:** Demand relatively stable regardless of price changes; promotional uplifts small and often not economically justifiable; brand loyalty or necessity drives purchase; price changes have limited demand impact
- **Differentiation from other models:** Unlike Elastic, promotional ROI is low — price/promo features add noise not signal; unlike Threshold, response is consistently weak across all stimulus levels; standard time-series models outperform causal models for Inelastic SKUs

### 3. Business Impact
- **Primary risk (over-forecast):** Standard model risk only — price features not required
- **Primary risk (under-forecast):** Standard model risk only
- **Strategic importance:** High revenue stability — inelastic SKUs provide reliable baseline revenue; promotional investment here delivers low ROI

### 4. Priority Level
🟠 Tier 2 — Lower forecast complexity; primary business value is identifying where NOT to invest promotional spend.

### 5. Model Strategy Overview

#### 5.1 Causal Feature Suppression
- Explicitly suppress price and promo features — they add noise for Inelastic SKUs
- Standard time-series model applied; causal model only used for strategic analysis (not operational forecasting)
- Elasticity estimate retained as metadata for pricing team reporting

#### 5.2 Analogue / Similarity Logic
- Not applicable — sufficient own history; inelastic demand is stable and reliable

#### 5.3 Feature Engineering

| Granularity | Included Features | Explicitly Excluded Features |
|---|---|---|
| Daily | 7/30/90/180/365-day rolling mean, std, CV²; day of week; holiday flag; seasonal index | Price features, promo depth, promo type, discount features, competitor price |
| Weekly | 4/8/13/26/52-week rolling mean, std; week of year; holiday; seasonal index | All price and promo features |
| Monthly | 2/3/6/12/24-month rolling mean, std; month of year; seasonal index | All price and promo features |
| Quarterly | 1/2/3/4-quarter rolling mean, std; quarter of year | All price and promo features |
| Yearly | 1/2/3/4-year rolling mean, std | All price and promo features |

- Note: Promo flag retained as binary (yes/no) — not as depth or type; used only for outlier detection during promo periods, not as a causal driver

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM (standard — no causal features)
- Configuration: Objective = reg:squarederror; Metric = WMAPE, RMSE
- Key features: Rolling means, seasonal index, holiday flag, promo binary flag (for outlier control only)
- When to use: Primary model — same as standard Stable behavior segment

#### 6.2 Deep Learning (DL)
- Architectures: N-BEATS (no causal external inputs)

| Granularity | Lookback | Features | Output |
|---|---|---|---|
| Daily | 365 days | 12 | P10, P50, P90 |
| Weekly | 52 weeks | 10 | P10, P50, P90 |
| Monthly | 24 months | 8 | P10, P50, P90 |
| Quarterly | 8 quarters | 6 | P10, P50, P90 |
| Yearly | 5 years | 5 | P10, P50, P90 |

- When to use: History > 2 years; seasonal pattern present

#### 6.3 Statistical / Time Series Models
- Architectures: ETS(A,N,A) — standard; SARIMA for complex seasonality

| Granularity | Model | Period |
|---|---|---|
| Daily | ETS(A,N,A) or TBATS | 7, 365 |
| Weekly | ETS(A,N,A) | 52 |
| Monthly | ETS(A,N,A) or SARIMA | 12 |
| Quarterly | ETS(A,N,A) | 4 |
| Yearly | ETS(A,N,N) | — |

- When to use: Always included — no causal model needed

#### 6.4 Baseline / Fallback Model
- Fallback: Same period last year
- Alert if fallback rate > 10%

### 7. Ensemble & Weighting

#### 7.2 Dynamic Weight Schedule

| History Length | LightGBM | N-BEATS | ETS |
|---|---|---|---|
| Up to 1 year | 55% | 0% | 45% |
| 1–2 years | 55% | 0% | 45% |
| > 2 years | 50% | 20% | 30% |

### 8. Uncertainty Quantification
- Method: Conformal prediction on residuals
- Output: [P10, P50, P90] — symmetric intervals expected for inelastic demand
- Use case: Standard safety stock from σ_residual × z_service_level; no promo-specific buffer needed

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Capping: min(forecast, 1.5 × full-year rolling max)
- Promotional override rule: If large promo planned (> 30% discount) on Inelastic SKU → flag for commercial review; ROI likely negative; do not increase forecast significantly
- Manual overrides: Standard S&OP consensus; supply constraint flag
- Alignment: ±20% of prior year same period

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | WMAPE Target | Bias Alert | Elasticity Monitor | Coverage |
|---|---|---|---|---|
| Daily | < 18% | \|Bias\| > 8% | Alert if PED < −1.0 (reclassify) | 80% P10–P90 |
| Weekly | < 15% | \|Bias\| > 7% | Alert if PED < −1.0 | 80% P10–P90 |
| Monthly | < 12% | \|Bias\| > 6% | Alert if PED < −1.0 | 80% P10–P90 |
| Quarterly | < 10% | \|Bias\| > 5% | Alert if PED < −1.0 | 80% P10–P90 |
| Yearly | < 8% | \|Bias\| > 4% | Alert if PED < −1.0 | 80% P10–P90 |

#### 10.2 Backtesting Protocol

| Granularity | Train | Test | Min History |
|---|---|---|---|
| Daily | 180 days | 30 days | 365 days |
| Weekly | 52 weeks | 13 weeks | 104 weeks |
| Monthly | 24 months | 6 months | 24 months |
| Quarterly | 8 quarters | 2 quarters | 8 quarters |
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
- Auto-detect: PED drops below −1.0 for 3 consecutive estimates → reclassify to Elastic; large promo uplift detected (> 15%) → flag for re-estimation
- Manual override: Pricing team major price change input (even if inelastic, very large changes may have some impact); supply constraint flag
- Override expiration: Single cycle

### 12. Reclassification

| Condition | Target Segment | Holding Period |
|---|---|---|
| PED drops below −1.0 for 3 estimates | Elastic | 3 estimates |
| Threshold behaviour detected | Threshold | 2 estimates |
| Saturation detected | Saturation | 2 estimates |

### 13. Review Cadence
- Monthly PED monitor; quarterly full elasticity re-estimation; annual pricing strategy alignment

---

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

## E4 · Saturation

### 1. Definition
Predicts demand for SKUs where demand response to stimulus follows a diminishing returns curve, reaching a maximum ceiling beyond which additional stimulus generates negligible incremental demand, requiring non-linear causal models and saturation-aware promotional investment optimisation.

### 2. Detailed Description
- **Applicable scenarios:** Market-penetration-limited categories, loyalty-capped demand, population-constrained categories, categories where all reachable customers have already responded, high-frequency-purchase categories where stockpiling is limited
- **Boundaries:**

| Granularity | Detection Condition | Q_max Confidence | Min Events |
|---|---|---|---|
| Daily | Q ≥ 0.90 × Q_max at peak stimulus AND β₂ < 0.50 in Adstock model | p < 0.05 for Q_max | ≥ 10 events across stimulus range |
| Weekly | Q ≥ 0.90 × Q_max AND β₂ < 0.50 | p < 0.05 | ≥ 8 events |
| Monthly | Q ≥ 0.90 × Q_max AND β₂ < 0.50 | p < 0.05 | ≥ 6 events |
| Quarterly | Q ≥ 0.90 × Q_max AND β₂ < 0.50 | p < 0.05 | ≥ 4 events |
| Yearly | Q ≥ 0.90 × Q_max AND β₂ < 0.50 | p < 0.05 | ≥ 3 events |

- **Key demand characteristics:** Strong response at low stimulus levels; diminishing returns as stimulus increases; demand ceiling (Q_max) that cannot be breached regardless of promotional depth; promotional ROI falls sharply as ceiling is approached
- **Differentiation from other models:** Unlike Elastic, response is not proportional — it decelerates with stimulus; unlike Threshold, response starts immediately (no dead zone); unlike Inelastic, there IS a strong response — just with a ceiling

### 3. Business Impact
- **Primary risk (over-forecast):** Over-estimating ceiling — deploying excessive promotional spend beyond saturation point
- **Primary risk (under-forecast):** Under-deploying promotion below saturation — leaving demand unrealised
- **Strategic importance:** High — Q_max defines the revenue ceiling for promotional investment; optimal promotional depth is the inflection point of ROI curve

### 4. Priority Level
🟠 Tier 2 — Non-linear model required; primary business value is defining optimal promotional depth and ROI ceiling.

### 5. Model Strategy Overview

#### 5.1 Saturation Curve Model
```
Logistic saturation model:
  Q(t) = Q_max / (1 + e^{−λ × (stimulus(t) − T_mid)})
  where Q_max = demand ceiling
        λ = steepness of saturation curve
        T_mid = stimulus level at 50% of Q_max (inflection point)

Power saturation (Adstock) model:
  Q(t) = baseline(t) × (1 + α × stimulus(t)^β)
  where β < 1 → diminishing returns (β = 0.50 → square root diminishing returns)
        α = initial response rate

Optimal promotional depth (ROI maximisation):
  Marginal response = dQ/dstimulus = 0.5 × Q_max × λ × e^{−λ×(s−T_mid)} / (1 + e^{−λ×(s−T_mid)})²
  ROI = (Margin × ΔQ − Promo_cost) / Promo_cost
  Optimal stimulus: s* = argmax ROI(s)
```

#### 5.2 Feature Engineering

| Granularity | Saturation Features | Stimulus Features | Baseline Features |
|---|---|---|---|
| Daily | Stimulus level, stimulus^0.5 (square root — captures diminishing returns), stimulus^2 (quadratic), distance from Q_max, saturation ratio (Q/Q_max) | Promo depth, promo type, display flag, distribution on promo | 7/30/90-day non-promo rolling mean, seasonal index |
| Weekly | Stimulus level, stimulus^0.5, distance from Q_max, saturation ratio | Promo depth, promo type | 4/8/13-week baseline, seasonal index |
| Monthly | Stimulus level, stimulus^0.5, saturation ratio | Promo depth, promo type | 3/6/12-month baseline |
| Quarterly | Stimulus level, stimulus^0.5, saturation ratio | Promo depth | 2/4-quarter baseline |
| Yearly | Annual stimulus level, saturation ratio | Annual promo intensity | Annual baseline |

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM with non-linear stimulus features (stimulus^0.5, stimulus^2, saturation ratio)
- Configuration: Objective = reg:squarederror; Metric = WMAPE, Uplift Accuracy
- Key features: Stimulus^0.5 (primary non-linear feature), saturation ratio, baseline rolling mean, seasonal index, promo type
- When to use: Primary model — non-linear features enable tree models to learn saturation curve

#### 6.2 Deep Learning (DL)
- Architectures: TFT with non-linear stimulus encoding as known future covariate

| Granularity | Lookback | Future Covariates | Output |
|---|---|---|---|
| Daily | 180 days | Promo plan 30 days ahead (with depth encoding) | P10, P50, P90 |
| Weekly | 52 weeks | Promo plan 8 weeks ahead | P10, P50, P90 |
| Monthly | 24 months | Promo plan 3 months ahead | P10, P50, P90 |
| Quarterly | 8 quarters | Promo plan 1 quarter ahead | P10, P50, P90 |
| Yearly | 5 years | Annual promo plan | P10, P50, P90 |

#### 6.3 Statistical / Time Series Models
- Architectures: Non-linear least squares (NLS) — logistic saturation curve

**NLS Saturation Fitting:**
```
Q(t) = Q_max × [1 − e^{−λ × stimulus(t)}] + ε(t)
Estimate: Q_max, λ via NLS minimising Σε²
Confidence interval for Q_max: Delta method or bootstrap
Starting values: Q_max_0 = 1.5 × max(Q_observed); λ_0 = 0.05
```

- When to use: Interpretability; Q_max reporting; ROI curve generation for trade planning

#### 6.4 Baseline / Fallback Model
- Fallback: Baseline × min(saturation_factor, 2.0) where saturation_factor based on historical mean uplift at current stimulus level
- Alert if Q_max estimate changes > 20% between estimations

### 7. Ensemble & Weighting

| Stimulus Level | LightGBM | TFT | NLS Saturation |
|---|---|---|---|
| Low (< 50% of saturation point) | 40% | 20% | 40% |
| Medium (50–90% of saturation point) | 50% | 25% | 25% |
| High (> 90% of saturation point — near ceiling) | 30% | 20% | 50% |

### 8. Uncertainty Quantification
- Method: Q_max bootstrap CI + quantile regression on residuals
- Output: [P10, P50, P90] — P90 capped at Q_max upper confidence bound
- Key output: Q_max estimate + 90% CI for trade planning

**ROI Curve Output:**
```
For each stimulus level s ∈ {0%, 5%, 10%, ..., 50%}:
  Expected uplift: ΔQ(s) = F_saturation(s) − baseline
  Marginal uplift: MΔQ(s) = ΔQ(s) − ΔQ(s − 5%)
  Marginal ROI(s) = (Margin × MΔQ(s)) / Marginal_promo_cost(s)
  Optimal s* = argmax ROI(s) [where marginal ROI = 1.0]
```

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Ceiling enforcement: max(forecast, 0); min(forecast, Q_max × 1.05) — hard ceiling with 5% buffer
- Over-promotion flag: If planned stimulus > optimal s* → alert trade team; ROI negative beyond s*
- Q_max advisory: Communicate Q_max and optimal promotional depth to trade team each cycle
- Manual overrides: Trade team ceiling challenge; market research on unrealised potential

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | Baseline WMAPE | Near-Ceiling WMAPE | Q_max Accuracy | ROI Curve Accuracy | Bias Alert |
|---|---|---|---|---|---|
| Daily | < 18% | < 25% | Q_max within ±15% | ROI peak within ±10% | \|Bias\| > 10% |
| Weekly | < 15% | < 22% | Q_max within ±12% | ROI peak within ±8% | \|Bias\| > 8% |
| Monthly | < 12% | < 20% | Q_max within ±10% | ROI peak within ±7% | \|Bias\| > 7% |
| Quarterly | < 10% | < 18% | Q_max within ±8% | ROI peak within ±6% | \|Bias\| > 6% |
| Yearly | < 8% | < 15% | Q_max within ±6% | ROI peak within ±5% | \|Bias\| > 5% |

#### 10.2 Backtesting Protocol
- Validate Q_max estimate on held-out near-ceiling promotional events
- Leave-one-out on events at different stimulus levels
- Min events: ≥ 3 events at stimulus levels > 80% of saturation point

#### 10.3 Retraining
- Standard cadence per granularity
- Re-estimate Q_max quarterly — saturation ceiling may shift with distribution or market size changes

### 11. Exception Handling & Overrides
- Auto-detect: Q_max rises significantly (> 20%) → market expansion detected; re-evaluate saturation model; β₂ rises above 0.80 → diminishing returns weakening → reclassify to Elastic; Q_max approaches zero (category collapse) → Lifecycle: Decline
- Manual override: Market expansion plan (new distribution, new geography) that raises effective Q_max; trade team ceiling challenge
- Override expiration: Per quarterly re-estimation

### 12. Reclassification

| Condition | Target | Holding Period |
|---|---|---|
| β₂ rises above 0.80 for 3 estimates | Elastic | 3 estimates |
| Non-linear piecewise threshold detected | Threshold | 2 estimates |
| Q_max shrinks to near-baseline | Inelastic | 3 estimates |
| New distribution expands Q_max significantly | Elastic (temporarily) | Until new Q_max estimated |

### 13. Review Cadence
- Monthly saturation ratio monitor; quarterly Q_max re-estimation and ROI curve refresh; annual trade strategy alignment

---

*End of Dimension 8 · Elasticity Pattern*
*4 Segments Complete · E1 through E4*
