# Dimension 4 · Magnitude Pattern
## Demand Forecasting Model Templates

---

> **Segments:** 4 · High Volume · Medium Volume · Low Volume · Ultra Low
> **Granularities:** Daily · Weekly · Monthly · Quarterly · Yearly
> **Note:** Magnitude is a portfolio-relative classification — thresholds are percentile-based against the active SKU portfolio at the same granularity. Magnitude informs model complexity, error metric selection, and inventory policy — it does not replace Behavior classification.

---

# PART 0 — FORMULA & THRESHOLD REFERENCE
## Magnitude Pattern Specific

---

## 0.1 Core Segmentation Metrics

### A. Volume Percentile Formula
> Classifies absolute demand size relative to the active portfolio

**General Formula:**
```
Mean Demand(SKU, window) = Σ d_t(SKU) / Total Periods in Window

Volume Percentile(SKU) = [Rank of SKU Mean Demand in Portfolio / Total Active SKUs] × 100

Rank is ascending: lowest demand = rank 1, highest demand = rank N
```

| Segment | Percentile Range | Classification |
|---|---|---|
| **Ultra Low** | < 5th percentile | Near-zero volume — single unit or near-single unit demand |
| **Low Volume** | 5th–25th percentile | Below-average volume — slow but meaningful demand |
| **Medium Volume** | 25th–75th percentile | Average portfolio volume — core mid-range SKUs |
| **High Volume** | > 75th percentile | Above-average volume — top-quarter of portfolio by demand |

**Computation Rules:**
- Compute mean demand over rolling window (see Section 0.3)
- Rank against **active SKUs only** — exclude Inactive lifecycle SKUs from ranking pool
- Recompute percentile ranking **monthly** — portfolio composition changes over time
- Use same granularity for comparison — daily means vs daily means; weekly vs weekly

---

### B. Absolute Volume Thresholds
> Portfolio-relative thresholds anchored to granularity-specific absolute minimums

**Note:** Percentile thresholds are primary. Absolute thresholds below are guardrails to prevent misclassification in very small or very large portfolios.

| Granularity | Ultra Low (absolute) | Low Volume (absolute) | Medium Volume (absolute) | High Volume (absolute) |
|---|---|---|---|---|
| **Daily** | Mean daily demand < 1 unit | 1–10 units/day | 10–100 units/day | > 100 units/day |
| **Weekly** | Mean weekly demand < 5 units | 5–50 units/week | 50–500 units/week | > 500 units/week |
| **Monthly** | Mean monthly demand < 20 units | 20–200 units/month | 200–2,000 units/month | > 2,000 units/month |
| **Quarterly** | Mean quarterly demand < 60 units | 60–600 units/quarter | 600–6,000 units/quarter | > 6,000 units/quarter |
| **Yearly** | Mean yearly demand < 240 units | 240–2,400 units/year | 2,400–24,000 units/year | > 24,000 units/year |

**Override Rule:** If percentile and absolute thresholds disagree, use the **more conservative** classification (i.e. classify lower if in doubt).

---

### C. Coefficient of Variation of Mean Demand
> Measures stability of the volume classification over time

**Formula:**
```
CV_mean = σ(rolling_mean) / μ(rolling_mean)   over extended window

CV_mean < 0.20 → Volume classification stable — use current percentile
CV_mean 0.20–0.40 → Volume drifting — flag for review; use 6-month average percentile
CV_mean > 0.40 → Volume highly unstable — combine with Lifecycle/Behavior signals
```

---

### D. ABC Classification Alignment
> Maps Magnitude segments to standard ABC inventory classification

```
A Items (top 20% of SKUs driving ~80% of revenue):   typically High Volume
B Items (next 30% of SKUs):                           typically Medium Volume
C Items (bottom 50% of SKUs):                         typically Low Volume + Ultra Low

Note: ABC is revenue-weighted; Magnitude is volume-weighted
High-price Low-volume SKUs may be A items but Low Volume magnitude
```

| Magnitude | Typical ABC | Inventory Policy |
|---|---|---|
| High Volume | A | Continuous review; tight safety stock; frequent replenishment |
| Medium Volume | A/B | Periodic review; standard safety stock |
| Low Volume | B/C | Periodic review; min/max policy |
| Ultra Low | C | Reorder point = 1; review monthly; consider make-to-order |

---

## 0.2 Magnitude Classification Decision Rules

```
STEP 1: Compute mean demand over rolling window (Section 0.3)
STEP 2: Rank against active portfolio at same granularity
STEP 3: Compute percentile
STEP 4: Apply percentile threshold

  Percentile < 5%   → ULTRA LOW
  5% ≤ Percentile < 25% → LOW VOLUME
  25% ≤ Percentile < 75% → MEDIUM VOLUME
  Percentile ≥ 75%  → HIGH VOLUME

STEP 5: Check absolute threshold guardrail — override if needed
STEP 6: Check CV_mean — flag if unstable (CV_mean > 0.40)
STEP 7: Recheck monthly — portfolio composition changes affect percentile ranking
```

---

## 0.3 Rolling Window Reference

| Window Name | Daily | Weekly | Monthly | Quarterly | Yearly |
|---|---|---|---|---|---|
| **Percentile Window** | 90 days | 26 weeks | 6 months | 4 quarters | 3 years |
| **Short** | 7 days | 4 weeks | 2 months | 1 quarter | 1 year |
| **Medium** | 30 days | 8 weeks | 3 months | 2 quarters | 2 years |
| **Long** | 90 days | 13 weeks | 6 months | 3 quarters | 3 years |
| **Extended** | 180 days | 26 weeks | 12 months | 4 quarters | 4 years |
| **Full Year** | 365 days | 52 weeks | 12 months | 4 quarters | 5 years |
| **DL Lookback** | 90 days | 52 weeks | 24 months | 8 quarters | 5 years |

**Rolling Mean Formula:**
```
Rolling Mean (window w): μ_w(t) = (1/w) × Σ d_{t-i}  for i = 0 to w-1
Rolling Std  (window w): σ_w(t) = sqrt[(1/w) × Σ (d_{t-i} − μ_w)²]
CV_mean:                 CV_mean = σ_w(t) / μ_w(t)
```

---

## 0.4 Accuracy Metric Selection by Magnitude

> Metric selection is one of the primary reasons Magnitude classification exists — MAPE is unreliable at low volume; WMAPE at high volume understates tail errors.

```
High Volume:   WMAPE (primary) + RMSE (secondary) + Bias
               MAPE acceptable — denominator is large and stable
               Safety stock: σ_forecast_error × z_service_level

Medium Volume: WMAPE (primary) + MAE (secondary) + Bias
               MAPE acceptable with care — occasional small actuals inflate MAPE
               Safety stock: σ_forecast_error × z_service_level

Low Volume:    MAE (primary) + MASE (secondary) + Bias
               MAPE unreliable — small denominators inflate metric
               Safety stock: min/max policy preferred over σ-based

Ultra Low:     MAE (primary, in units) + Fill Rate (secondary) + Bias
               MAPE completely unreliable — avoid entirely
               Safety stock: fixed buffer (1–2 units); consider make-to-order
```

**MASE Formula (preferred for Low and Ultra Low):**
```
MASE = MAE_model / MAE_naive
MAE_naive = (1/(n−m)) × Σ|Actual_t − Actual_{t−m}|
m = seasonal period (see Section 0.6)
MASE < 1.0 → model beats naive seasonal benchmark
```

**Pinball Loss (for probabilistic forecasts):**
```
Pinball(α,t) = α × (Actual_t − Q_α)     if Actual_t ≥ Q_α
             = (1−α) × (Q_α − Actual_t)  if Actual_t < Q_α
Coverage = Actuals within [P10, P90] / n × 100  (Target: 80%)
```

---

## 0.5 WMAPE / Bias Targets by Magnitude and Granularity

| Segment | Daily WMAPE | Weekly WMAPE | Monthly WMAPE | Quarterly WMAPE | Yearly WMAPE |
|---|---|---|---|---|---|
| **High Volume** | < 15% | < 12% | < 10% | < 8% | < 6% |
| **Medium Volume** | < 22% | < 18% | < 15% | < 12% | < 10% |
| **Low Volume** | MAE primary | MAE primary | < 20% MASE | < 18% MASE | < 15% MASE |
| **Ultra Low** | MAE < 1 unit | MAE < 2 units | MAE < 5 units | MAE < 10 units | MAE < 20 units |

| Segment | Bias Alert Threshold |
|---|---|
| **High Volume** | \|Bias\| > 5% |
| **Medium Volume** | \|Bias\| > 8% |
| **Low Volume** | \|Bias\| > 12% |
| **Ultra Low** | \|Bias\| > 20% |

---

## 0.6 Seasonality Period Reference

| Granularity | Primary Period | Secondary Period | Detection |
|---|---|---|---|
| **Daily** | 7 (day of week) | 365 (annual) | FFT + ACF at lag 7, 365 |
| **Weekly** | 52 (annual) | 13 (quarterly) | ACF at lag 52, 13 |
| **Monthly** | 12 (annual) | 3 (quarterly) | ACF at lag 12, 3 |
| **Quarterly** | 4 (annual) | 2 (bi-annual) | ACF at lag 4, 2 |
| **Yearly** | — | — | Not applicable |

---

## 0.7 Retraining & Backtesting Reference

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

## M1 · High Volume

### 1. Definition
Predicts demand for SKUs in the top 75th percentile of portfolio demand volume at the relevant granularity, where high absolute quantities make even small percentage errors economically significant and justify investment in the most sophisticated forecasting methods.

### 2. Detailed Description
- **Applicable scenarios:** Category leaders, core FMCG lines, high-velocity retail items, strategic B2B accounts
- **Boundaries:**

| Granularity | Percentile | Absolute Guardrail | Rolling Window |
|---|---|---|---|
| Daily | > 75th percentile | > 100 units/day | 90-day rolling mean |
| Weekly | > 75th percentile | > 500 units/week | 26-week rolling mean |
| Monthly | > 75th percentile | > 2,000 units/month | 6-month rolling mean |
| Quarterly | > 75th percentile | > 6,000 units/quarter | 4-quarter rolling mean |
| Yearly | > 75th percentile | > 24,000 units/year | 3-year rolling mean |

- **Key demand characteristics:** High absolute volume, errors are large in absolute units even if small in percentage, inventory holding cost is high, stockout cost is very high
- **Differentiation from other models:** Unlike Medium Volume, justifies full ML + DL ensemble investment; unlike Low Volume, MAPE and WMAPE are reliable metrics; safety stock modelled using σ-based approach

### 3. Business Impact
- **Primary risk (over-forecast):** High absolute excess inventory — large working capital tied up; warehouse capacity consumed
- **Primary risk (under-forecast):** High absolute stockout — lost sales at scale; service level breach on most visible SKUs
- **Strategic importance:** Critical — High Volume SKUs typically represent 20% of portfolio but 60–80% of revenue and volume

### 4. Priority Level
🔴 Tier 1 — Highest investment justified; even 1% WMAPE improvement translates to significant inventory cost savings.

### 5. Model Strategy Overview

#### 5.1 Zero-Demand Handling (Hurdle)
- Active event threshold: P(demand > 0) > 0.95 — high volume SKUs almost never have zero demand
- Classifier: Rule-based flag only — consecutive zeros trigger immediate investigation
- Regressor: Full ensemble — LightGBM + TFT/N-BEATS + ETS
- Fallback: Same period last year × trend factor

#### 5.2 Analogue / Similarity Logic
- Not applicable — sufficient own history; volume too high to need analogues

#### 5.3 Feature Engineering

| Granularity | Rolling Windows | Seasonal Features | External Signals |
|---|---|---|---|
| Daily | 7, 14, 30, 60, 90, 180, 365-day mean, std, max, min, CV² | Day of week, week of year, month, quarter, holiday flag, days to/from peak | Promo calendar, price index, weather (if applicable), competitor index |
| Weekly | 4, 8, 13, 26, 52-week mean, std, max, min, CV² | Week of year, quarter flag, holiday week, seasonal index | Promo calendar, price index, category index |
| Monthly | 2, 3, 6, 12, 24-month mean, std, max, min, CV² | Month of year, quarter, half-year, seasonal index | Promo calendar, macro index |
| Quarterly | 1, 2, 3, 4, 6-quarter mean, std, max, CV² | Quarter of year, half-year, fiscal period | Macro index, category trend |
| Yearly | 1, 2, 3, 4, 5-year mean, std, max, CV² | Long-cycle index | Macro trend, market share index |

- Categorical encoding: Target encoding with smoothing factor = 10
- Feature count: Up to 50 features — high volume justifies full feature engineering

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM (primary) + CatBoost (secondary — handles categorical features natively)
- Configuration: Objective = reg:squarederror; Metric = WMAPE, RMSE
- Hyperparameter tuning: Optuna — 100 trials; 5-fold time series cross-validation
- Key features: All rolling statistics, full seasonal feature set, promotional features, price features, external signals
- When to use: Primary model — always applied for High Volume SKUs

#### 6.2 Deep Learning (DL)
- Architectures: TFT (primary DL) + N-BEATS (secondary DL)

| Granularity | Lookback | Features | Hidden Units | Attention Heads | Output |
|---|---|---|---|---|---|
| Daily | 365 days | 25 | 128 | 4 | P10, P50, P90 |
| Weekly | 104 weeks | 20 | 128 | 4 | P10, P50, P90 |
| Monthly | 36 months | 15 | 64 | 4 | P10, P50, P90 |
| Quarterly | 12 quarters | 12 | 64 | 2 | P10, P50, P90 |
| Yearly | 5 years | 8 | 32 | 2 | P10, P50, P90 |

- Training: Loss = quantile loss (P10, P50, P90); Optimizer = Adam lr = 0.001; Dropout = 0.1; Early stopping patience = 20; Batch size = 64
- When to use: Always applied — deep learning justified by volume importance

#### 6.3 Statistical / Time Series Models
- Architectures: ETS(A,N,A) or ETS(M,N,M); SARIMA; TBATS (daily dual seasonality)

| Granularity | Primary Statistical Model | Period |
|---|---|---|
| Daily | TBATS (dual seasonality) | 7 + 365 |
| Weekly | SARIMA(2,0,1)(1,1,0)_52 | 52 |
| Monthly | SARIMA(1,0,1)(1,1,0)_12 | 12 |
| Quarterly | ETS(A,N,A) | 4 |
| Yearly | ETS(A,A,N) | — |

- When to use: Always included in ensemble — statistical models provide stability and interpretability

#### 6.4 Baseline / Fallback Model
- Fallback triggers: Full ensemble failure (pipeline error)
- Fallback model: Same period last year × trend adjustment
- Logging & alerting: Alert if fallback triggered for High Volume SKU — P1 incident

### 7. Ensemble & Weighting

#### 7.1 Ensemble Scheme
- Combination: D̂_t = w_lgbm × LightGBM + w_catboost × CatBoost + w_tft × TFT + w_nbeats × N-BEATS + w_stat × Statistical
- Weight determination: Error-inverse weighting on rolling 8-period WMAPE; updated weekly

#### 7.2 Dynamic Weight Schedule

| History Available | LightGBM | CatBoost | TFT | N-BEATS | Statistical |
|---|---|---|---|---|---|
| 1–2 years | 40% | 10% | 0% | 0% | 50% |
| 2–3 years | 35% | 10% | 25% | 0% | 30% |
| > 3 years | 30% | 10% | 30% | 15% | 15% |

### 8. Uncertainty Quantification
- Method: Conformal prediction + quantile regression ensemble
- Output: [P10, P25, P50, P75, P90] — full distribution for high-value safety stock optimisation
- Use case: Safety stock = σ_error × z_service_level; z = 1.65 for 95% SL; z = 2.05 for 98% SL

**Safety Stock Formula:**
```
SS = z × σ_forecast_error × √(Lead_time + Review_period)
σ_forecast_error = RMSE over backtesting period
z = service level factor (1.28=90%, 1.65=95%, 2.05=98%, 2.33=99%)
```

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Capping: min(forecast, 1.5 × 52-week rolling max)
- Floor: max(forecast, 0.5 × 52-week rolling min) — prevent excessive down-forecast
- Manual overrides: S&OP consensus adjustment; commercial volume commitment; supply constraint flag
- Alignment: Forecast within ±15% of prior year same period; deviation requires documented justification
- Rounding: Round to nearest pallet/case quantity for operational feasibility

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | WMAPE Target | RMSE Target | Bias Alert | Coverage Target |
|---|---|---|---|---|
| Daily | < 15% | < 20% of mean | \|Bias\| > 5% | 80% P10–P90 |
| Weekly | < 12% | < 15% of mean | \|Bias\| > 5% | 80% P10–P90 |
| Monthly | < 10% | < 12% of mean | \|Bias\| > 4% | 80% P10–P90 |
| Quarterly | < 8% | < 10% of mean | \|Bias\| > 4% | 80% P10–P90 |
| Yearly | < 6% | < 8% of mean | \|Bias\| > 3% | 80% P10–P90 |

#### 10.2 Backtesting Protocol

| Granularity | Method | Train | Test | Min History |
|---|---|---|---|---|
| Daily | Rolling window | 365 days | 30 days | 730 days |
| Weekly | Rolling window | 104 weeks | 13 weeks | 156 weeks |
| Monthly | Rolling window | 36 months | 6 months | 36 months |
| Quarterly | Rolling window | 12 quarters | 2 quarters | 12 quarters |
| Yearly | Expanding window | All available | 1 year | 3 years |

#### 10.3 Retraining & Data Freshness

| Granularity | Cadence | Incremental | Latency |
|---|---|---|---|
| Daily | Daily | Yes — online gradient update | T+4 hours |
| Weekly | Weekly | No | T+1 day |
| Monthly | Monthly | No | T+2 days |
| Quarterly | Quarterly | No | T+3 days |
| Yearly | Annually | No | T+7 days |

### 11. Exception Handling & Overrides
- Automatic exception detection: Forecast > 2 × rolling max; forecast < 0.3 × rolling min; bias drift > 5% for 4 consecutive periods; model WMAPE degrades > 5% vs baseline
- Manual override process: S&OP sign-off required for > 20% override; documented with reason code; reviewed in next S&OP cycle
- Override expiration: Single cycle unless permanent change confirmed

### 12. Reclassification / Model Selection
- To Medium Volume: Percentile drops below 75th for 6 consecutive months — soft transition
- Switching logic: Gradual — blend High and Medium Volume models over 4 periods
- Holding period: 6 months before reclassification confirmed

### 13. Review Cadence
- Performance monitoring: Daily automated dashboard — High Volume SKUs have dedicated monitoring
- Model review meeting: Weekly S&OP review; bi-weekly model performance deep-dive
- Full model re-evaluation: Quarterly; after any major demand shock or structural break

---

## M2 · Medium Volume

### 1. Definition
Predicts demand for SKUs in the 25th–75th percentile of portfolio demand volume, representing the core middle tier of the portfolio where standard forecasting methods deliver reliable results with moderate feature complexity.

### 2. Detailed Description
- **Applicable scenarios:** Mainstream product variants, regional lines, standard B2B accounts, mid-tier category SKUs
- **Boundaries:**

| Granularity | Percentile | Absolute Guardrail | Rolling Window |
|---|---|---|---|
| Daily | 25th–75th percentile | 10–100 units/day | 90-day rolling mean |
| Weekly | 25th–75th percentile | 50–500 units/week | 26-week rolling mean |
| Monthly | 25th–75th percentile | 200–2,000 units/month | 6-month rolling mean |
| Quarterly | 25th–75th percentile | 600–6,000 units/quarter | 4-quarter rolling mean |
| Yearly | 25th–75th percentile | 2,400–24,000 units/year | 3-year rolling mean |

- **Key demand characteristics:** Moderate absolute volume; standard percentage metrics reliable; WMAPE-based safety stock appropriate; standard ensemble methods sufficient
- **Differentiation from other models:** Unlike High Volume, full DL ensemble not always justified by cost-benefit; unlike Low Volume, MAPE/WMAPE are reliable; standard feature set is appropriate

### 3. Business Impact
- **Primary risk (over-forecast):** Moderate excess inventory — manageable but cumulative across many Medium Volume SKUs
- **Primary risk (under-forecast):** Service level breaches on mainstream lines — customer satisfaction impact
- **Strategic importance:** High — Medium Volume SKUs are the breadth of the portfolio; collective accuracy matters

### 4. Priority Level
🟠 Tier 2 — High portfolio count; automation and standardisation are key; individual SKU attention lower than High Volume.

### 5. Model Strategy Overview

#### 5.1 Zero-Demand Handling (Hurdle)
- Active event threshold: P(demand > 0) > 0.85
- Classifier: Rule-based — 2+ consecutive zero periods triggers alert
- Regressor: LightGBM primary; ETS supplementary
- Fallback: Rolling mean (medium window)

#### 5.2 Analogue / Similarity Logic
- Not applicable — sufficient own history for most Medium Volume SKUs
- Exception: Use analogues if history < 6 months

#### 5.3 Feature Engineering

| Granularity | Rolling Windows | Seasonal Features | External Signals |
|---|---|---|---|
| Daily | 7, 30, 90, 180, 365-day mean, std, CV² | Day of week, month, holiday flag, seasonal index | Promo flag, price index |
| Weekly | 4, 8, 13, 26, 52-week mean, std, CV² | Week of year, quarter, holiday, seasonal index | Promo flag, price index |
| Monthly | 2, 3, 6, 12, 24-month mean, std, CV² | Month of year, quarter, seasonal index | Promo flag, macro index |
| Quarterly | 1, 2, 3, 4-quarter mean, std, CV² | Quarter of year, half-year | Promo flag |
| Yearly | 1, 2, 3, 4-year mean, std, CV² | Long-cycle index | Macro index |

- Feature count: 25–35 features — standard set, no hyperparameter-intensive tuning

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM
- Configuration: Objective = reg:squarederror; Metric = WMAPE, MAE
- Hyperparameter tuning: Optuna — 50 trials; 5-fold time series CV
- Key features: Rolling means (all windows), seasonal index, promo flag, price index, holiday flag
- When to use: Primary model — always applied

#### 6.2 Deep Learning (DL)
- Architectures: TFT (applied selectively — justified when history > 2 years)

| Granularity | Lookback | Features | Output |
|---|---|---|---|
| Daily | 180 days | 18 | P10, P50, P90 |
| Weekly | 52 weeks | 15 | P10, P50, P90 |
| Monthly | 24 months | 12 | P10, P50, P90 |
| Quarterly | 8 quarters | 10 | P10, P50, P90 |
| Yearly | 5 years | 8 | P10, P50, P90 |

- Training: Loss = MAE; Adam lr = 0.001; Dropout = 0.1; Patience = 15
- When to use: History > 2 years AND seasonal pattern detected — otherwise skip DL for Medium Volume

#### 6.3 Statistical / Time Series Models
- Architectures: ETS(A,N,A) primary; SARIMA for strong seasonal signal

| Granularity | Model | Period |
|---|---|---|
| Daily | ETS(A,N,A) | 7 (weekly seasonality) |
| Weekly | ETS(A,N,A) | 52 |
| Monthly | ETS(A,N,A) or SARIMA | 12 |
| Quarterly | ETS(A,N,A) | 4 |
| Yearly | ETS(A,N,N) | — |

- When to use: Always included — provides stability and interpretability

#### 6.4 Baseline / Fallback Model
- Fallback: Same period last year
- Logging & alerting: Alert if fallback rate > 15%

### 7. Ensemble & Weighting

#### 7.2 Dynamic Weight Schedule

| History Available | LightGBM | TFT | ETS / SARIMA |
|---|---|---|---|
| < 1 year | 50% | 0% | 50% |
| 1–2 years | 55% | 0% | 45% |
| 2–3 years | 55% | 20% | 25% |
| > 3 years | 50% | 25% | 25% |

- Weight determination: Error-inverse on rolling 8-period WMAPE

### 8. Uncertainty Quantification
- Method: Conformal prediction on residuals
- Output: [P10, P50, P90]
- Safety stock: SS = z × σ_error × √(LT + RP); z = service level factor

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Capping: min(forecast, 1.5 × 52-week rolling max)
- Alignment: ±20% of prior year same period — automated flag if breached
- Manual overrides: Planner approval via dashboard; reason code mandatory

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | WMAPE Target | MAE Target | Bias Alert | Coverage |
|---|---|---|---|---|
| Daily | < 22% | < 20% of mean | \|Bias\| > 8% | 80% P10–P90 |
| Weekly | < 18% | < 15% of mean | \|Bias\| > 8% | 80% P10–P90 |
| Monthly | < 15% | < 12% of mean | \|Bias\| > 7% | 80% P10–P90 |
| Quarterly | < 12% | < 10% of mean | \|Bias\| > 6% | 80% P10–P90 |
| Yearly | < 10% | < 8% of mean | \|Bias\| > 5% | 80% P10–P90 |

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
- Auto-detect: Forecast > 2 × rolling max; 3+ consecutive zero actuals; bias > 8% for 4 periods
- Manual override: Planner dashboard approval; reason code required
- Override expiration: Single cycle

### 12. Reclassification
- To High Volume: Percentile rises above 75th for 6 consecutive months
- To Low Volume: Percentile drops below 25th for 6 consecutive months
- Soft blend over 4-period transition for both directions

### 13. Review Cadence
- Weekly automated dashboard; bi-weekly S&OP review; quarterly full re-evaluation

---

## M3 · Low Volume

### 1. Definition
Predicts demand for SKUs in the 5th–25th percentile of portfolio demand volume, where low absolute quantities make percentage-based metrics unreliable and specialist low-volume methods are required to avoid overfitting and metric distortion.

### 2. Detailed Description
- **Applicable scenarios:** Long-tail variants, niche product lines, regional specialties, low-velocity B2B lines, specialty retail
- **Boundaries:**

| Granularity | Percentile | Absolute Guardrail | Rolling Window |
|---|---|---|---|
| Daily | 5th–25th percentile | 1–10 units/day | 90-day rolling mean |
| Weekly | 5th–25th percentile | 5–50 units/week | 26-week rolling mean |
| Monthly | 5th–25th percentile | 20–200 units/month | 6-month rolling mean |
| Quarterly | 5th–25th percentile | 60–600 units/quarter | 4-quarter rolling mean |
| Yearly | 5th–25th percentile | 240–2,400 units/year | 3-year rolling mean |

- **Key demand characteristics:** Low absolute volume; MAPE inflated by small actuals; overfitting risk is high with complex models; inventory policy often binary (stock vs no stock)
- **Differentiation from other models:** Unlike Medium Volume, MAPE/WMAPE unreliable — use MAE and MASE; unlike Ultra Low, demand is more than single-unit; simple models outperform complex ones

### 3. Business Impact
- **Primary risk (over-forecast):** Holding cost on low-value items; portfolio-level waste from many small overstock positions
- **Primary risk (under-forecast):** Long tail customers are disproportionately loyal; stockout damages relationship
- **Strategic importance:** Medium — individually low impact; collectively significant (long tail effect)

### 4. Priority Level
🟡 Tier 3 — Low individual priority; automation at scale is the key business requirement.

### 5. Model Strategy Overview

#### 5.1 Zero-Demand Handling (Hurdle)
- Active event threshold: P(demand > 0) > 0.70
- Classifier: Logistic Regression (simple — prevent overfitting on low data)
- Regressor: ETS or Theta — statistical methods outperform ML on low volume
- Fallback: Rolling mean (short window)

#### 5.2 Analogue / Similarity Logic
- Number of analogues: k = 5 (similar low-volume SKUs from same subcategory)
- Cross-SKU pooling: Group Low Volume SKUs into demand pools for shared model training
- Similarity: Subcategory, CV², ADI range, price tier

#### 5.3 Feature Engineering

| Granularity | Rolling Windows | Features | Notes |
|---|---|---|---|
| Daily | 7, 30, 90-day mean, std | Day of week, holiday flag, seasonal index | Minimal — prevent overfit |
| Weekly | 4, 8, 13-week mean, std | Week of year, holiday, seasonal index | Simple feature set |
| Monthly | 2, 3, 6, 12-month mean, std | Month of year, seasonal index, promo flag | Standard set |
| Quarterly | 1, 2, 4-quarter mean, std | Quarter of year, seasonal index | Minimal |
| Yearly | 1, 2, 3-year mean | Long-cycle index | Trend only |

- Feature count: 10–15 features maximum — regularisation critical

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM (heavily regularised)
- Configuration: Objective = reg:absoluteerror (MAE preferred); max_depth = 3; num_leaves = 15; min_data_in_leaf = 10; lambda_l1 = 1.0
- When to use: When portfolio large enough for cross-SKU learning (> 100 Low Volume SKUs)
- Cross-SKU learning: Train single LightGBM model across all Low Volume SKUs — SKU ID as feature

#### 6.2 Deep Learning (DL)
- Architectures: Not recommended — data too sparse for individual DL; cross-SKU DeepAR acceptable if > 500 Low Volume SKUs in portfolio
- When to use: Only if very large portfolio enables meaningful cross-learning

#### 6.3 Statistical / Time Series Models
- Architectures: Theta method (primary); ETS(A,N,A) or ETS(A,N,N)

| Granularity | Primary Model | Reason |
|---|---|---|
| Daily | Theta with period = 7 | Robust on low volume; handles noise better than SARIMA |
| Weekly | Theta or ETS(A,N,A) period = 52 | Simple seasonal capture |
| Monthly | Theta or ETS(A,N,A) period = 12 | Reliable on low volume monthly data |
| Quarterly | ETS(A,N,N) or 4-quarter moving average | Low complexity |
| Yearly | 3-year moving average | Minimal model |

**Theta Method Formula:**
```
Decompose series into two theta lines:
θ_0 line (θ=0): long-term trend = linear regression on d_t
θ_2 line (θ=2): short-term = 2 × d_t − θ_0_t

Forecast = α × θ_2_forecast + (1−α) × θ_0_forecast
α optimised on validation MAE
```

- When to use: Primary model for Low Volume — Theta consistently outperforms complex models on low-volume data

#### 6.4 Baseline / Fallback Model
- Fallback: 3-period moving average
- Logging & alerting: Alert if fallback rate > 25%

### 7. Ensemble & Weighting

#### 7.2 Dynamic Weight Schedule

| History Available | LightGBM (cross-SKU) | Theta | ETS |
|---|---|---|---|
| < 6 months | 0% | 60% | 40% |
| 6 months–1 year | 20% | 50% | 30% |
| 1–2 years | 30% | 45% | 25% |
| > 2 years | 40% | 40% | 20% |

### 8. Uncertainty Quantification
- Method: Bootstrap on historical residuals (simple; works on small samples)
- Output: [P10, P50, P90]
- Use case: Min/max stock policy — often binary (stock or not stock); P90 used for max stock level

**Min/Max Policy Formula:**
```
Min (reorder point) = Mean demand × Lead time + Safety stock
Max (order up to)   = Min + Order quantity
Safety stock        = z × σ_demand × √Lead_time   [if σ reliable]
                    = fixed buffer (1–2 units)      [if Ultra Low border]
```

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Rounding: Round to nearest whole unit — fractional units meaningless at low volume
- Minimum forecast consideration: Evaluate whether to stock at all (range rationalisation trigger)
- Manual overrides: Range review input; customer special order flag

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | Primary Metric | Secondary | Bias Alert |
|---|---|---|---|
| Daily | MAE (units) | Fill Rate | \|Bias\| > 20% |
| Weekly | MAE (units) | Fill Rate | \|Bias\| > 18% |
| Monthly | MASE | MAE | \|Bias\| > 15% |
| Quarterly | MASE | MAE | \|Bias\| > 12% |
| Yearly | MASE | MAE | \|Bias\| > 10% |

- **Note:** MAPE and WMAPE explicitly avoided for Low Volume — small denominators create misleading metrics

#### 10.2 Backtesting Protocol

| Granularity | Train | Test | Min History |
|---|---|---|---|
| Daily | 90 days | 30 days | 180 days |
| Weekly | 26 weeks | 13 weeks | 52 weeks |
| Monthly | 12 months | 6 months | 18 months |
| Quarterly | 4 quarters | 2 quarters | 6 quarters |
| Yearly | All available | 1 year | 2 years |

#### 10.3 Retraining

| Granularity | Cadence | Latency |
|---|---|---|
| Daily | Weekly (not daily — low priority) | T+4 hours |
| Weekly | Weekly | T+1 day |
| Monthly | Monthly | T+2 days |
| Quarterly | Quarterly | T+3 days |
| Yearly | Annually | T+7 days |

### 11. Exception Handling & Overrides
- Auto-detect: Volume rises above 25th percentile for 4 months → reclassify to Medium Volume
- Manual override: Range rationalisation trigger; special customer order flag
- Override expiration: Single cycle

### 12. Reclassification
- To Medium Volume: Percentile rises above 25th for 6 consecutive months
- To Ultra Low: Percentile drops below 5th for 6 consecutive months
- Soft blend over 4-period transition

### 13. Review Cadence
- Monthly automated portfolio-level dashboard; quarterly range rationalisation review; annual full re-evaluation

---

## M4 · Ultra Low

### 1. Definition
Predicts demand for SKUs in the bottom 5th percentile of portfolio demand volume where near-zero absolute quantities make statistical forecasting unreliable, and the primary decision is whether to stock at all rather than how much to forecast.

### 2. Detailed Description
- **Applicable scenarios:** Extreme long-tail variants, obsolescence-risk items, single-customer specialty products, very slow MRO items
- **Boundaries:**

| Granularity | Percentile | Absolute Guardrail | Rolling Window |
|---|---|---|---|
| Daily | < 5th percentile | < 1 unit/day | 90-day rolling mean |
| Weekly | < 5th percentile | < 5 units/week | 26-week rolling mean |
| Monthly | < 5th percentile | < 20 units/month | 6-month rolling mean |
| Quarterly | < 5th percentile | < 60 units/quarter | 4-quarter rolling mean |
| Yearly | < 5th percentile | < 240 units/year | 3-year rolling mean |

- **Key demand characteristics:** Near-zero volume; all percentage metrics meaningless; inventory decision is binary; make-to-order consideration; very high relative holding cost
- **Differentiation from other models:** Unlike Low Volume, even MAE in units may be near zero; primary question is stock vs no-stock not how much to forecast; demand often Poisson or near-Poisson distributed

### 3. Business Impact
- **Primary risk (over-forecast):** Any stock build is disproportionately costly relative to volume
- **Primary risk (under-forecast):** Single unit stockout may have outsized customer impact (niche loyalty)
- **Strategic importance:** Low individually; collectively represents range management risk

### 4. Priority Level
🟡 Tier 3 — Lowest individual priority; range rationalisation decision more impactful than forecast accuracy.

### 5. Model Strategy Overview

#### 5.1 Stock vs No-Stock Decision (Primary Model)
- Primary question: Should this SKU be stocked at all?
- Stocking trigger: P(demand > 0 in next period) > stocking threshold

| Granularity | Stocking Threshold |
|---|---|
| Daily | P(demand > 0) > 0.20 |
| Weekly | P(demand > 0) > 0.30 |
| Monthly | P(demand > 0) > 0.40 |
| Quarterly | P(demand > 0) > 0.50 |
| Yearly | P(demand > 0) > 0.60 |

- If P(demand > 0) < threshold → consider make-to-order or delist
- Classifier: Logistic Regression on minimal features (avoid overfitting)

#### 5.2 Quantity Forecast (Secondary — given stocking decision is yes)
- Method: Historical non-zero mean (simplest reliable estimate)
- Do not use ML or DL — insufficient data; models overfit

#### 5.3 Analogue / Similarity Logic
- Pool Ultra Low SKUs for shared Poisson model estimation
- k = 10 most similar Ultra Low SKUs (same subcategory, similar ADI, similar price tier)
- Pooled Poisson rate: λ = Σ demand_events_i / Σ total_periods_i across pool

#### 5.4 Feature Engineering
- Minimal: Periods since last demand, prior year same-period demand, seasonal flag, category demand trend
- No complex feature engineering — overfit risk is extreme at this volume

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: Not recommended — insufficient data for individual SKU ML
- Cross-SKU pooling: Group Ultra Low SKUs; train single pooled Logistic Regression for stocking trigger
- When to use: Stocking trigger classification only; not for quantity forecast

#### 6.2 Deep Learning (DL)
- Not applicable — data too sparse

#### 6.3 Statistical / Time Series Models
- Architectures: Poisson model (primary) — demand arrival rate λ

**Poisson Demand Model:**
```
Demand ~ Poisson(λ)
λ = Mean demand over rolling window (non-zero and zero periods included)
P(demand = k) = (λ^k × e^{−λ}) / k!
P(demand > 0) = 1 − e^{−λ}
Forecast = λ (expected value of Poisson)
Safety stock = z_SL × √λ   (Poisson variance = mean = λ)
```

| Granularity | λ Estimation Window | Update Frequency |
|---|---|---|
| Daily | 180-day rolling | Weekly |
| Weekly | 52-week rolling | Monthly |
| Monthly | 24-month rolling | Monthly |
| Quarterly | 8-quarter rolling | Quarterly |
| Yearly | 3-year rolling | Annually |

- When to use: Primary model — Poisson is the natural distribution for rare demand events

#### 6.4 Baseline / Fallback Model
- Fallback: Fixed forecast = 1 unit per period (minimum viable stock signal)
- Logging & alerting: Alert on any demand event (each event is significant at Ultra Low volume)

### 7. Ensemble & Weighting
- No ensemble — Poisson model is primary and sufficient
- Stocking trigger (Logistic Regression) × Quantity (Poisson mean) = Final forecast

### 8. Uncertainty Quantification
- Method: Poisson distribution — exact probability mass function
- Output: P(demand = 0), P(demand = 1), P(demand = 2), ... up to P(demand = 5)
- Use case: Stock 1 unit if P(demand ≥ 1) > stocking threshold; stock 2 units if P(demand ≥ 2) > secondary threshold

**Stocking Decision Matrix:**
```
P(demand ≥ 1) = 1 − e^{−λ}
P(demand ≥ 2) = 1 − e^{−λ} − λ × e^{−λ}
P(demand ≥ k) = 1 − Σ P(demand = j) for j = 0 to k-1

Stock k units if P(demand ≥ k) > threshold
Threshold = f(holding_cost, stockout_cost, service_level_target)
```

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Rounding: Always round to whole units — fractional units impossible
- Make-to-order trigger: If P(demand > 0) < stocking threshold AND lead time allows → switch to make-to-order
- Range rationalisation trigger: If no demand in 13 consecutive weeks → flag for delisting review
- Manual overrides: Commercial decision to maintain range; customer commitment to order

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | Primary Metric | Secondary | Stockout Alert |
|---|---|---|---|
| Daily | MAE in units (target < 0.5 units) | Fill Rate > 80% | Any stockout on active stocked item |
| Weekly | MAE in units (target < 1 unit) | Fill Rate > 80% | Any stockout on active stocked item |
| Monthly | MAE in units (target < 2 units) | Fill Rate > 75% | Any stockout |
| Quarterly | MAE in units (target < 5 units) | Fill Rate > 70% | Any stockout |
| Yearly | MAE in units (target < 10 units) | Fill Rate > 65% | Any stockout |

- **Note:** MAPE, WMAPE, MASE all explicitly avoided — meaningless at Ultra Low volume
- Primary KPI: Stock/no-stock decision accuracy (did we stock when demand arrived?)

#### 10.2 Backtesting Protocol

| Granularity | Method | Train | Test | Min Events |
|---|---|---|---|---|
| Daily | Leave-one-out on demand events | All events except last | Last event | 3 events |
| Weekly | Leave-one-out | All events except last | Last event | 3 events |
| Monthly | Leave-one-out | All events except last | Last event | 3 events |
| Quarterly | Leave-one-out | All events except last | Last event | 2 events |
| Yearly | Leave-one-out | All events except last | Last event | 2 events |

#### 10.3 Retraining

| Granularity | Cadence | Latency |
|---|---|---|
| Daily | Monthly (low priority) | T+4 hours |
| Weekly | Monthly | T+1 day |
| Monthly | Quarterly | T+2 days |
| Quarterly | Semi-annually | T+3 days |
| Yearly | Annually | T+7 days |

### 11. Exception Handling & Overrides
- Automatic exception: Any demand event → immediate alert; volume rises above 5th percentile for 3 months → reclassify to Low Volume; no demand for 13 consecutive weeks → delist flag
- Manual override: Commercial team range retention decision; customer special order flag
- Override expiration: Per review cycle

### 12. Reclassification
- To Low Volume: Percentile rises above 5th for 4 consecutive months
- To Inactive: Zero demand ≥ 13 consecutive weeks (Lifecycle reclassification triggered simultaneously)
- Hard switch for both directions — no blend needed at this volume level

### 13. Review Cadence
- Monthly automated Ultra Low watchlist; quarterly range rationalisation review; annual full portfolio long-tail assessment

---

*End of Dimension 4 · Magnitude Pattern*
*4 Segments Complete · M1 through M4*
