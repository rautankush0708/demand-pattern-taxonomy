# Dimension 1 · Lifecycle Pattern
## Demand Forecasting Model Templates

---

> **Segments:** 7 · Cold Start · New Launch · Growth · Mature · Decline · Phasing Out · Inactive
> **Granularities:** Daily · Weekly · Monthly · Quarterly · Yearly

---

# PART 0 — FORMULA & THRESHOLD REFERENCE
## Lifecycle Pattern Specific

---

## 0.1 Core Segmentation Metrics

### A. Demand Slope — Trend Detection
> Measures directional movement of demand over time

**General Formula:**
```
slope β = Σ[(t - t̄)(d_t - d̄)] / Σ[(t - t̄)²]
Assessed via Mann-Kendall test
Significant trend: p < 0.05
No trend:          p ≥ 0.10
Watch zone:        0.05 ≤ p < 0.10 → monitor 2 more periods
```

| Granularity | Rolling Window | Slope Unit | Significance |
|---|---|---|---|
| **Daily** | 90-day | Units/day | Mann-Kendall p < 0.05 |
| **Weekly** | 13-week | Units/week | Mann-Kendall p < 0.05 |
| **Monthly** | 6-month | Units/month | Mann-Kendall p < 0.05 |
| **Quarterly** | 4-quarter | Units/quarter | Mann-Kendall p < 0.05 |
| **Yearly** | 3-year | Units/year | Mann-Kendall p < 0.05 |

---

### B. % Zero Periods
> Proportion of periods with no demand — used to confirm Inactive status

**General Formula:**
```
%Zero = (Number of Zero Demand Periods / Total Periods in Window) × 100
```

| Granularity | Inactive Trigger | Formula |
|---|---|---|
| **Daily** | 0 demand ≥ 91 consecutive days | Count(demand = 0, consecutive) ≥ 91 |
| **Weekly** | 0 demand ≥ 13 consecutive weeks | Count(demand = 0, consecutive) ≥ 13 |
| **Monthly** | 0 demand ≥ 3 consecutive months | Count(demand = 0, consecutive) ≥ 3 |
| **Quarterly** | 0 demand ≥ 1 consecutive quarter | Count(demand = 0, consecutive) ≥ 1 |
| **Yearly** | 0 demand ≥ 1 consecutive year | Count(demand = 0, consecutive) ≥ 1 |

---

### C. Structural Break Detection
> Detects permanent level shifts — used before Lifecycle classification

| Granularity | Test | Window | Trigger |
|---|---|---|---|
| **Daily** | CUSUM | 30-day | CUSUM statistic > 5σ |
| **Weekly** | Chow Test + CUSUM | 8-week | p < 0.05 |
| **Monthly** | Chow Test | 4-month | p < 0.05 |
| **Quarterly** | Chow Test | 2-quarter | p < 0.05 |
| **Yearly** | Chow Test | 2-year | p < 0.05 |

---

## 0.2 Lifecycle Classification Thresholds

| Lifecycle Stage | Daily | Weekly | Monthly | Quarterly | Yearly |
|---|---|---|---|---|---|
| **Cold Start** | History < 56 days | History < 8 weeks | History < 2 months | History < 1 quarter | History < 1 year |
| **New Launch** | 56–112 days | 8–16 weeks | 2–4 months | 1–2 quarters | 1–2 years |
| **Growth** | Slope p < 0.05 (+), 90-day window | Slope p < 0.05 (+), 13-week window | Slope p < 0.05 (+), 6-month window | Slope p < 0.05 (+), 4-quarter window | Slope p < 0.05 (+), 3-year window |
| **Mature** | Slope p ≥ 0.10, 90-day window | Slope p ≥ 0.10, 13-week window | Slope p ≥ 0.10, 6-month window | Slope p ≥ 0.10, 4-quarter window | Slope p ≥ 0.10, 3-year window |
| **Decline** | Slope p < 0.05 (−), 90-day window | Slope p < 0.05 (−), 13-week window | Slope p < 0.05 (−), 6-month window | Slope p < 0.05 (−), 4-quarter window | Slope p < 0.05 (−), 3-year window |
| **Phasing Out** | Discontinuation flag set | Same | Same | Same | Same |
| **Inactive** | 0 demand ≥ 91 consecutive days | 0 demand ≥ 13 consecutive weeks | 0 demand ≥ 3 consecutive months | 0 demand ≥ 1 consecutive quarter | 0 demand ≥ 1 consecutive year |

---

## 0.3 Minimum History Requirements

| Requirement | Daily | Weekly | Monthly | Quarterly | Yearly |
|---|---|---|---|---|---|
| **Min for Trend Test** | ≥ 90 days | ≥ 13 weeks | ≥ 6 months | ≥ 4 quarters | ≥ 3 years |
| **Min for Seasonality** | ≥ 365 days (2 cycles) | ≥ 104 weeks (2 cycles) | ≥ 24 months (2 cycles) | ≥ 8 quarters (2 cycles) | ≥ 3 years |
| **Min for Growth/Decline** | ≥ 112 days | ≥ 16 weeks | ≥ 4 months | ≥ 2 quarters | ≥ 2 years |

---

## 0.4 Rolling Window Reference

| Window Name | Daily | Weekly | Monthly | Quarterly | Yearly |
|---|---|---|---|---|---|
| **Short** | 7 days | 4 weeks | 2 months | 1 quarter | 1 year |
| **Medium** | 30 days | 8 weeks | 3 months | 2 quarters | 2 years |
| **Long** | 90 days | 13 weeks | 6 months | 3 quarters | 3 years |
| **Extended** | 180 days | 26 weeks | 12 months | 4 quarters | 4 years |
| **Full Year** | 365 days | 52 weeks | 12 months | 4 quarters | 5 years |
| **DL Lookback** | 90 days | 52 weeks | 24 months | 8 quarters | 5 years |

**Rolling Statistic Formulas:**
```
Rolling Mean (window w):   μ_w(t) = (1/w) × Σ d_{t-i}   for i = 0 to w-1
Rolling Std  (window w):   σ_w(t) = sqrt[(1/w) × Σ (d_{t-i} − μ_w)²]
Rolling Slope (window w):  β_w(t) = Σ[(i − ī)(d_{t-i} − d̄)] / Σ[(i − ī)²]
Decay Weight:              w_i    = exp(−i / half_life) / Σ exp(−j / half_life)
```

---

## 0.5 Accuracy Metric Formulas

```
WMAPE  = Σ|Forecast_t − Actual_t| / Σ Actual_t × 100

Bias   = Σ(Forecast_t − Actual_t) / Σ Actual_t × 100

MAE    = (1/n) × Σ|Forecast_t − Actual_t|

MASE   = MAE_model / MAE_naive
         MAE_naive = (1/(n−m)) × Σ|Actual_t − Actual_{t−m}|
         m = seasonal period

Pinball(α,t) = α × (Actual_t − Q_α)     if Actual_t ≥ Q_α
             = (1−α) × (Q_α − Actual_t)  if Actual_t < Q_α

Coverage = (Actuals within [P10,P90]) / Total Periods × 100
           Target: 80% coverage
```

---

## 0.6 Lifecycle Classification Decision Tree

```
INPUT: SKU demand history at chosen granularity
  │
  ├── Zero demand ≥ Inactive threshold?       ──► L7: INACTIVE
  │
  ├── History < Cold Start upper bound?       ──► L1: COLD START
  │
  ├── History within New Launch range?        ──► L2: NEW LAUNCH
  │
  ├── Discontinuation flag set in system?     ──► L6: PHASING OUT
  │
  ├── Run Mann-Kendall on rolling window
  │     ├── Positive slope p < 0.05?          ──► L3: GROWTH
  │     ├── Negative slope p < 0.05?          ──► L5: DECLINE
  │     └── Slope p ≥ 0.10?                  ──► L4: MATURE
  │
  └── Watch zone (0.05 ≤ p < 0.10)           ──► Hold current; re-test next 2 periods
```

---

## 0.7 Strategic Overrides & Business Logic

> [!IMPORTANT]
> **New Product Launch Guardrail:** 
> For the first 30 days of a **Cold Start** SKU, the forecast must be aligned with the "Marketing Buy-in" quantity. Statistical models are only permitted to adjust the forecast *after* the initial 30-day signal is received.

> [!WARNING]
> **Phasing Out Protocol:**
> Once a SKU is flagged as **Phasing Out**, the automated replenishment logic must switch from MAE-optimization to **Clearance-optimization**. Safety stock should be set to zero to avoid terminal stock bloat.

---

# PART 1 — SEGMENT TEMPLATES

---

## L1 · Cold Start

### 1. Definition
Predicts demand for SKUs with insufficient history to detect any statistical pattern; applicable to all newly listed products regardless of category, where analogue-based or prior-informed forecasting is the only viable approach.

### 2. Detailed Description
- **Applicable scenarios:** First days/weeks post-listing, new SKU introduction, no meaningful demand history
- **Boundaries:**

| Granularity | Lower Bound | Upper Bound |
|---|---|---|
| Daily | 0 days | < 56 days |
| Weekly | 0 weeks | < 8 weeks |
| Monthly | 0 months | < 2 months |
| Quarterly | 0 quarters | < 1 quarter |
| Yearly | 0 years | < 1 year |

- **Key demand characteristics:** Near-zero or zero history, maximum uncertainty, no trend or seasonality detectable, sparse or zero observations
- **Differentiation from other models:** Unlike New Launch, no pattern has emerged — forecast is driven entirely by analogues or category priors, not the SKU's own signal

### 3. Business Impact
- **Primary risk (over-forecast):** Excess opening stock; write-offs if product fails to gain traction
- **Primary risk (under-forecast):** Missed launch velocity; out-of-stock in critical first periods; poor retailer relationships
- **Strategic importance:** High — first periods set ranging, reorder, and promotional decisions

### 4. Priority Level
🔴 Tier 1 — Launch success is disproportionately driven by availability in first periods; stockout during Cold Start is difficult to recover from.

### 5. Model Strategy Overview

#### 5.1 Zero-Demand Handling (Hurdle)
- Active event threshold: P(demand > 0) > 0.40
- Classifier type: Logistic Regression (low data — simple model preferred)
- Regressor type: Weighted analogue mean
- Fallback when disagree: Forecast = 0 if classifier < 0.40; ignore regressor output

#### 5.2 Analogue / Similarity Logic
- Number of analogues: k = 5
- Similarity criteria: Euclidean distance on category, subcategory, price tier, pack size, launch channel
- Temporal decay weight: weight = exp(−age / half-life)

| Granularity | Half-Life |
|---|---|
| Daily | 14 days |
| Weekly | 4 weeks |
| Monthly | 2 months |
| Quarterly | 1 quarter |
| Yearly | 1 year |

- Aggregation method: Weighted median (robust to outlier analogues)

#### 5.3 Feature Engineering
- Rolling statistics: Not applicable — use analogue rolling stats only; own SKU insufficient
- Categorical encoding: Target encoding with smoothing factor = 10
- Date/time features:

| Granularity | Features |
|---|---|
| Daily | Day of week, launch day index, holiday flag, days since listing |
| Weekly | Week of year, launch week index, holiday proximity flag |
| Monthly | Month of year, launch month index, seasonal category flag |
| Quarterly | Quarter index, launch quarter, fiscal period flag |
| Yearly | Launch year index, macro trend flag |

- External signals: Distribution coverage at launch, shelf placement tier, promotional support flag, competitor presence

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM (analogue features only)
- Configuration (classifier): Objective = binary:logistic; Metric = AUC
- Configuration (regressor): Objective = reg:absoluteerror; Metric = MAE
- Key features: Analogue demand periods 1–4, category median, price index, promo flag, channel type
- When to use: When ≥ 3 strong analogues available with full feature match

#### 6.2 Deep Learning (DL)
- Architectures: Not applicable — insufficient history for sequence models
- When to use: Not applicable at Cold Start stage

#### 6.3 Statistical / Time Series Models
- Architectures: Category median (naive prior); Croston initialisation from analogue mean
- Seasonality: Inherited from top analogues
- Trend: None — flat prior
- Zero-demand handling: Croston initialisation from analogue mean
- When to use: When fewer than 3 analogues exist; default safe fallback

#### 6.4 Baseline / Fallback Model
- Fallback triggers: No analogues found, missing category data, launch delay
- Fallback model: Category median demand for equivalent launch period
- Logging & alerting: Log every Cold Start fallback; alert if fallback rate > 30%

### 7. Ensemble & Weighting

#### 7.1 Ensemble Scheme
- Combination method: D̂_t = w_analogue × analogue_model + w_prior × category_prior
- Weight determination: Fixed schedule based on analogue count

#### 7.2 Dynamic Weight Schedule

| Analogues Available | Analogue Weight | Category Prior Weight |
|---|---|---|
| ≥ 5 strong analogues | 80% | 20% |
| 3–4 analogues | 65% | 35% |
| < 3 analogues | 20% | 80% |

### 8. Uncertainty Quantification
- Method: Quantile regression on analogue distribution
- Output: [P10, P50, P90] from analogue spread
- Use case: Safety stock sizing for new listing; P90 used for initial buy quantity

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Capping: min(forecast, 3 × top analogue period-1 demand)
- Manual overrides: Buyer input on expected velocity; marketing launch plan multiplier
- Alignment constraints: Forecast cannot exceed confirmed opening stock quantity

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | Primary Metric | Secondary | Bias Alert |
|---|---|---|---|
| Daily | MAE | Coverage P10–P90 | \|Bias\| > 15% |
| Weekly | MAE | Coverage P10–P90 | \|Bias\| > 15% |
| Monthly | MAE | Coverage P10–P90 | \|Bias\| > 12% |
| Quarterly | MAE | Coverage P10–P90 | \|Bias\| > 10% |
| Yearly | MAE | Coverage P10–P90 | \|Bias\| > 8% |

#### 10.2 Backtesting Protocol

| Granularity | Method | Train | Test | Min Analogues |
|---|---|---|---|---|
| Daily | Leave-one-out on analogue pool | History to day 0 | Days 1–56 | 5 completed launches |
| Weekly | Leave-one-out on analogue pool | History to week 0 | Weeks 1–8 | 5 completed launches |
| Monthly | Leave-one-out on analogue pool | History to month 0 | Months 1–2 | 5 completed launches |
| Quarterly | Leave-one-out on analogue pool | History to Q0 | Q1–Q2 | 5 completed launches |
| Yearly | Leave-one-out on analogue pool | History to year 0 | Years 1–2 | 5 completed launches |

#### 10.3 Retraining & Data Freshness

| Granularity | Cadence | Incremental | Latency |
|---|---|---|---|
| Daily | Daily | No | T+4 hours |
| Weekly | Weekly | No | T+1 day |
| Monthly | Monthly | No | T+2 days |
| Quarterly | Quarterly | No | T+3 days |
| Yearly | Annually | No | T+7 days |

### 11. Exception Handling & Overrides
- Automatic exception detection: Forecast > 5 × best analogue period-1 demand; missing category match; zero analogues found
- Manual override process: Dashboard approval by category manager; logged with timestamp and reason code
- Override expiration: Per forecast cycle — reviewed at each cycle

### 12. Reclassification / Model Selection

| Granularity | Graduate to New Launch at | Trigger |
|---|---|---|
| Daily | 56 days of history | Hard switch |
| Weekly | 8 weeks of history | Hard switch |
| Monthly | 2 months of history | Hard switch |
| Quarterly | 1 quarter of history | Hard switch |
| Yearly | 1 year of history | Hard switch |

- Switching logic: Hard switch — no blend; analogue weight handed over to New Launch model
- Holding period: Defined by upper bound — no early graduation

### 13. Review Cadence
- Performance monitoring: Per granularity cycle — automated dashboard
- Model review meeting: Per launch event review with commercial team
- Full model re-evaluation: After every 10 new launches to recalibrate analogue pool

---

## L2 · New Launch

### 1. Definition
Predicts demand for SKUs where an initial demand pattern is emerging but insufficient for full statistical modelling; hybrid of analogue and own-SKU signal, transitioning toward data-driven forecasting across 8–16 weeks of history.

### 2. Detailed Description
- **Applicable scenarios:** Post-launch ramp, early velocity signal available, first reorder decisions
- **Boundaries:**

| Granularity | Lower Bound | Upper Bound |
|---|---|---|
| Daily | 56 days | < 112 days |
| Weekly | 8 weeks | < 16 weeks |
| Monthly | 2 months | < 4 months |
| Quarterly | 1 quarter | < 2 quarters |
| Yearly | 1 year | < 2 years |

- **Key demand characteristics:** Low but growing history, potential upward trend not yet confirmed, high period-on-period variability, possible early promotional distortion
- **Differentiation from other models:** Unlike Cold Start, own SKU signal now contributes; unlike Growth, trend is not yet statistically confirmed

### 3. Business Impact
- **Primary risk (over-forecast):** Overcommit on second buy; excess inventory before demand curve confirmed
- **Primary risk (under-forecast):** Missed velocity window; competitors fill shelf space
- **Strategic importance:** High — ranging, distribution, and second buy decisions made in this window

### 4. Priority Level
🔴 Tier 1 — Second buy decision occurs here; error is costly and difficult to reverse.

### 5. Model Strategy Overview

#### 5.1 Zero-Demand Handling (Hurdle)
- Active event threshold: P(demand > 0) > 0.50
- Classifier type: Logistic Regression with own SKU + analogue features
- Regressor type: LightGBM — blended own + analogue features
- Fallback when disagree: Forecast = 0 if classifier < 0.50

#### 5.2 Analogue / Similarity Logic
- Number of analogues: k = 3 (weight reducing as own history grows)
- Similarity criteria: Category, price tier, launch channel, early period demand shape correlation
- Temporal decay weight: weight = exp(−age / half-life)

| Granularity | Half-Life |
|---|---|
| Daily | 21 days |
| Weekly | 6 weeks |
| Monthly | 3 months |
| Quarterly | 2 quarters |
| Yearly | 1.5 years |

- Aggregation method: Weighted mean blended with own SKU signal

#### 5.3 Feature Engineering
- Rolling statistics: Short window rolling mean and CV on own SKU

| Granularity | Min Non-Zero Obs | Rolling Windows Used |
|---|---|---|
| Daily | ≥ 10 non-zero days | 7-day, 14-day, 30-day |
| Weekly | ≥ 4 non-zero weeks | 4-week, 8-week |
| Monthly | ≥ 2 non-zero months | 2-month, 4-month |
| Quarterly | ≥ 1 non-zero quarter | 1-quarter, 2-quarter |
| Yearly | ≥ 1 non-zero year | 1-year |

- Categorical encoding: Target encoding with smoothing factor = 10
- Date/time features:

| Granularity | Features |
|---|---|
| Daily | Launch day index, day of week, holiday flag, days since listing |
| Weekly | Launch week index, week of year, holiday flag |
| Monthly | Launch month index, month of year, seasonal flag |
| Quarterly | Launch quarter index, quarter of year |
| Yearly | Launch year index |

- External signals: Distribution coverage growth, promotional depth, price index vs category

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM
- Configuration (classifier): Objective = binary:logistic; Metric = AUC
- Configuration (regressor): Objective = reg:absoluteerror; Metric = MAE
- Key features: Own rolling mean, analogue trajectory, promo flag, distribution coverage, category growth rate
- When to use: Primary model when ≥ 4 periods of own non-zero demand exist

#### 6.2 Deep Learning (DL)
- Architectures: Not recommended — history too short for sequence learning
- When to use: Not applicable

#### 6.3 Statistical / Time Series Models
- Architectures: ETS(A,A,N) — additive error, additive trend, no seasonality
- Trend: Additive — early ramp captured
- Zero-demand handling: Croston initialisation for first periods
- When to use: Supplementary model for ensemble; interpretability check

#### 6.4 Baseline / Fallback Model
- Fallback triggers: Own demand = 0 for 3+ consecutive periods post-launch
- Fallback model: Analogue-only weighted median
- Logging & alerting: Alert if fallback rate > 25%

### 7. Ensemble & Weighting

#### 7.1 Ensemble Scheme
- Combination: D̂_t = w_own × LightGBM + w_analogue × analogue_model
- Weight determination: Dynamic — own weight increases linearly with periods of history

#### 7.2 Dynamic Weight Schedule

| Granularity | Early Period | Mid Period | Late Period |
|---|---|---|---|
| Daily | Days 56–70: Own 40% / Analogue 60% | Days 71–90: Own 60% / Analogue 40% | Days 91–112: Own 80% / Analogue 20% |
| Weekly | Weeks 8–10: Own 40% / Analogue 60% | Weeks 11–13: Own 60% / Analogue 40% | Weeks 14–16: Own 80% / Analogue 20% |
| Monthly | Month 2: Own 40% / Analogue 60% | Month 3: Own 60% / Analogue 40% | Month 4: Own 80% / Analogue 20% |
| Quarterly | Q1: Own 40% / Analogue 60% | Q1.5: Own 60% / Analogue 40% | Q2: Own 80% / Analogue 20% |
| Yearly | Year 1: Own 40% / Analogue 60% | Year 1.5: Own 60% / Analogue 40% | Year 2: Own 80% / Analogue 20% |

### 8. Uncertainty Quantification
- Method: Quantile regression
- Output: [P10, P50, P90]
- Use case: Second buy quantity — P75 for safety stock; P50 for base order

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Capping: min(forecast, 2 × highest observed period demand so far)
- Manual overrides: Commercial team velocity adjustment; distribution rollout plan multiplier
- Alignment constraints: Forecast must align with confirmed distribution points

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | WMAPE Target | Bias Alert | Classification |
|---|---|---|---|
| Daily | < 30% | \|Bias\| > 20% | AUC > 0.65 |
| Weekly | < 25% | \|Bias\| > 20% | AUC > 0.65 |
| Monthly | < 20% | \|Bias\| > 15% | AUC > 0.65 |
| Quarterly | < 18% | \|Bias\| > 12% | AUC > 0.65 |
| Yearly | < 15% | \|Bias\| > 10% | AUC > 0.65 |

#### 10.2 Backtesting Protocol

| Granularity | Train | Test | Min Eval History |
|---|---|---|---|
| Daily | Days 1–56 | Days 57–112 | 8 completed launches |
| Weekly | Weeks 1–8 | Weeks 9–16 | 8 completed launches |
| Monthly | Months 1–2 | Months 3–4 | 8 completed launches |
| Quarterly | Q1 | Q2 | 8 completed launches |
| Yearly | Year 1 | Year 2 | 8 completed launches |

#### 10.3 Retraining & Data Freshness

| Granularity | Cadence | Incremental | Latency |
|---|---|---|---|
| Daily | Daily | No | T+4 hours |
| Weekly | Weekly | No | T+1 day |
| Monthly | Monthly | No | T+2 days |
| Quarterly | Quarterly | No | T+3 days |
| Yearly | Annually | No | T+7 days |

### 11. Exception Handling & Overrides
- Automatic exception detection: Zero demand for 3+ consecutive periods post-launch; forecast > 3 × period-peak demand to date
- Manual override process: Category manager approval; timestamp and reason code logged
- Override expiration: Single forecast cycle

### 12. Reclassification / Model Selection

| Granularity | Graduate at | Slope Determines |
|---|---|---|
| Daily | 112 days | Growth (p < 0.05+) vs Mature (p ≥ 0.10) |
| Weekly | 16 weeks | Growth (p < 0.05+) vs Mature (p ≥ 0.10) |
| Monthly | 4 months | Growth (p < 0.05+) vs Mature (p ≥ 0.10) |
| Quarterly | 2 quarters | Growth (p < 0.05+) vs Mature (p ≥ 0.10) |
| Yearly | 2 years | Growth (p < 0.05+) vs Mature (p ≥ 0.10) |

- Switching logic: Hard switch at upper bound; slope test determines next segment
- Holding period: No early graduation — must complete New Launch window

### 13. Review Cadence
- Performance monitoring: Weekly automated dashboard
- Model review meeting: Bi-weekly launch performance review
- Full model re-evaluation: Quarterly analogue pool refresh

---

## L3 · Growth

### 1. Definition
Predicts demand for SKUs with a statistically confirmed positive demand slope over a granularity-specific rolling window, where trend-aware models are required to avoid systematic under-forecasting.

### 2. Detailed Description
- **Applicable scenarios:** Post-launch acceleration, market expansion, distribution gains, category growth
- **Boundaries:** History ≥ New Launch upper bound; Mann-Kendall p < 0.05 positive slope
- **Key demand characteristics:** Consistent upward slope, increasing volume, low-to-moderate CV², possible seasonality layering onto trend
- **Differentiation from other models:** Unlike Mature, demand is not flat — static models will systematically under-forecast; unlike New Launch, trend is statistically confirmed

### 3. Business Impact
- **Primary risk (over-forecast):** Excess inventory if growth plateau arrives earlier than modelled
- **Primary risk (under-forecast):** Chronic stockouts; lost distribution gains; missed revenue targets
- **Strategic importance:** Very high — growth SKUs drive category share and revenue delivery

### 4. Priority Level
🔴 Tier 1 — Growth SKUs are actively managed by commercial teams; forecast accuracy directly impacts revenue.

### 5. Model Strategy Overview

#### 5.1 Zero-Demand Handling (Hurdle)
- Active event threshold: P(demand > 0) > 0.70 — growth SKUs rarely have zero periods
- Classifier type: Rule-based sanity check only — not primary concern
- Regressor type: LightGBM / TFT
- Fallback: Historical rolling mean if regressor fails

#### 5.2 Analogue / Similarity Logic
- Number of analogues: k = 2 (supplementary only — own signal dominates)
- Similarity criteria: Mature SKUs in same category at similar historical growth rate
- Temporal decay weight: weight = exp(−age / half-life)

| Granularity | Half-Life |
|---|---|
| Daily | 30 days |
| Weekly | 8 weeks |
| Monthly | 4 months |
| Quarterly | 2 quarters |
| Yearly | 2 years |

- Aggregation method: Weighted mean — low weight supplement only

#### 5.3 Feature Engineering

| Granularity | Rolling Windows | Slope Feature | Min Obs Required |
|---|---|---|---|
| Daily | 7, 30, 90, 180-day | β_90day rolling slope | ≥ 112 days |
| Weekly | 4, 8, 13, 26-week | β_13week rolling slope | ≥ 16 weeks |
| Monthly | 2, 3, 6, 12-month | β_6month rolling slope | ≥ 4 months |
| Quarterly | 1, 2, 3, 4-quarter | β_4quarter rolling slope | ≥ 2 quarters |
| Yearly | 1, 2, 3-year | β_3year rolling slope | ≥ 2 years |

- Categorical encoding: Target encoding with smoothing = 10
- External signals: Distribution point count, category growth index, promotional calendar

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM with trend features
- Configuration: Objective = reg:squarederror; Metric = RMSE, WMAPE
- Key features: Rolling means, slope coefficient, distribution coverage, category index, promo flag, period of year
- When to use: Primary model — moderate history with structured trend features

#### 6.2 Deep Learning (DL)
- Architectures: TFT (Temporal Fusion Transformer)

| Granularity | Lookback | Features | Output |
|---|---|---|---|
| Daily | 180 days | 15 | P10, P50, P90 |
| Weekly | 52 weeks | 12 | P10, P50, P90 |
| Monthly | 24 months | 10 | P10, P50, P90 |
| Quarterly | 8 quarters | 8 | P10, P50, P90 |
| Yearly | 5 years | 6 | P10, P50, P90 |

- Training: Loss = quantile loss; Optimizer = Adam lr = 0.001; Dropout = 0.1; Early stopping patience = 10
- When to use: History > 6 months equivalent; multi-horizon forecast required

#### 6.3 Statistical / Time Series Models
- Architectures: ETS(A,A,N) or ARIMA(p,1,q) with first differencing for trend stationarity
- Trend: Additive
- Seasonality: SARIMA if seasonal pattern detected on granularity periods (Section 0.8)
- When to use: Interpretability requirement; short history (just above New Launch boundary)

#### 6.4 Baseline / Fallback Model
- Fallback triggers: Model convergence failure; slope reversal detected mid-cycle
- Fallback model: Short rolling mean + 5% trend adjustment per period
- Logging & alerting: Alert if fallback rate > 15%

### 7. Ensemble & Weighting

#### 7.1 Ensemble Scheme
- Combination: D̂_t = w_lgbm × LightGBM + w_tft × TFT + w_ets × ETS
- Weight determination: Error-inverse weighting on rolling 4-period validation MAE

#### 7.2 Dynamic Weight Schedule

| History Length | LightGBM | TFT | ETS |
|---|---|---|---|
| New Launch boundary to 6 months equiv. | 70% | 0% | 30% |
| 6–12 months equivalent | 60% | 30% | 10% |
| > 12 months equivalent | 50% | 40% | 10% |

### 8. Uncertainty Quantification
- Method: Quantile regression + conformal prediction wrapper
- Output: [P10, P50, P90]
- Use case: Safety stock at P75; replenishment trigger at P50

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Capping: min(forecast, 2 × long-window rolling max)
- Manual overrides: Commercial team distribution gain inputs; trade plan uplift
- Alignment constraints: Forecast growth rate cannot exceed confirmed distribution point growth rate

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | WMAPE Target | Bias Alert | Pinball Loss |
|---|---|---|---|
| Daily | < 25% | Bias > +15% | Monitor P10–P90 |
| Weekly | < 20% | Bias > +15% | Monitor P10–P90 |
| Monthly | < 15% | Bias > +12% | Monitor P10–P90 |
| Quarterly | < 12% | Bias > +10% | Monitor P10–P90 |
| Yearly | < 10% | Bias > +8% | Monitor P10–P90 |

#### 10.2 Backtesting Protocol

| Granularity | Method | Train | Test |
|---|---|---|---|
| Daily | Rolling window | 180 days | 30 days |
| Weekly | Rolling window | 26 weeks | 4 weeks |
| Monthly | Rolling window | 12 months | 3 months |
| Quarterly | Rolling window | 4 quarters | 2 quarters |
| Yearly | Expanding window | All available | 1 year |

#### 10.3 Retraining & Data Freshness

| Granularity | Cadence | Incremental | Latency |
|---|---|---|---|
| Daily | Daily | No | T+4 hours |
| Weekly | Weekly | No | T+1 day |
| Monthly | Monthly | No | T+2 days |
| Quarterly | Quarterly | No | T+3 days |
| Yearly | Annually | No | T+7 days |

### 11. Exception Handling & Overrides
- Automatic exception detection: Slope reversal (positive to flat) for 3 consecutive periods; forecast > 2 × prior period actual
- Manual override process: Commercial sign-off required; distribution plan alignment checked
- Override expiration: Single cycle — reviewed each period

### 12. Reclassification / Model Selection

| Granularity | Reclassify to Mature when | Transition |
|---|---|---|
| Daily | Mann-Kendall p > 0.10 for 4 consecutive 90-day windows | Soft blend over 4 periods |
| Weekly | Mann-Kendall p > 0.10 for 4 consecutive 13-week windows | Soft blend over 4 weeks |
| Monthly | Mann-Kendall p > 0.10 for 4 consecutive 6-month windows | Soft blend over 4 months |
| Quarterly | Mann-Kendall p > 0.10 for 4 consecutive 4-quarter windows | Soft blend over 2 quarters |
| Yearly | Mann-Kendall p > 0.10 for 3 consecutive 3-year windows | Soft blend over 2 years |

### 13. Review Cadence
- Performance monitoring: Per granularity cycle — automated dashboard with slope monitor
- Model review meeting: Weekly commercial forecast review
- Full model re-evaluation: Quarterly or on distribution step-change event

---

## L4 · Mature

### 1. Definition
Predicts demand for SKUs with stable, flat demand over an extended period where no statistically significant trend exists and demand is well understood; the primary workhorse forecasting segment representing the majority of portfolio volume.

### 2. Detailed Description
- **Applicable scenarios:** Core range SKUs, established products, high-volume stable lines
- **Boundaries:** History ≥ New Launch upper bound; Mann-Kendall p ≥ 0.10 (no significant trend)
- **Key demand characteristics:** Low CV², stable mean, possible seasonality, well-defined baseline
- **Differentiation from other models:** Unlike Growth/Decline, no directional slope; unlike Volatile/Erratic, variance is manageable with standard models

### 3. Business Impact
- **Primary risk (over-forecast):** Working capital tied up in excess inventory
- **Primary risk (under-forecast):** Stockouts on core lines — high customer dissatisfaction
- **Strategic importance:** Very high — Mature SKUs represent majority of revenue and volume

### 4. Priority Level
🔴 Tier 1 — Core revenue base; even small percentage errors create large absolute waste.

### 5. Model Strategy Overview

#### 5.1 Zero-Demand Handling (Hurdle)
- Active event threshold: P(demand > 0) > 0.85 — mature SKUs rarely go to zero
- Classifier type: Rule-based flag only — not primary concern
- Regressor type: LightGBM / ETS
- Fallback: Rolling mean over extended window

#### 5.2 Analogue / Similarity Logic
- Not applicable — sufficient own history; analogues not used for Mature SKUs

#### 5.3 Feature Engineering

| Granularity | Rolling Windows | Seasonal Features |
|---|---|---|
| Daily | 7, 30, 90, 180, 365-day rolling mean & std | Day of week, month index, holiday flag, annual cycle |
| Weekly | 4, 8, 13, 26, 52-week rolling mean & std | Week of year, quarter, holiday flag |
| Monthly | 2, 3, 6, 12, 24-month rolling mean & std | Month of year, quarter, half-year flag |
| Quarterly | 1, 2, 3, 4-quarter rolling mean & std | Quarter of year, half-year |
| Yearly | 1, 2, 3, 4, 5-year rolling mean & std | Long cycle index |

- Categorical encoding: Target encoding with smoothing = 10
- External signals: Promotional calendar, price changes, competitor activity index

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM
- Configuration: Objective = reg:squarederror; Metric = WMAPE, RMSE
- Key features: All rolling means, seasonal index, promo flag, price index, holiday flag
- When to use: Primary model — rich feature set available

#### 6.2 Deep Learning (DL)
- Architectures: N-BEATS / TFT

| Granularity | Lookback | Features |
|---|---|---|
| Daily | 365 days | 18 |
| Weekly | 52 weeks | 15 |
| Monthly | 24 months | 12 |
| Quarterly | 8 quarters | 10 |
| Yearly | 5 years | 8 |

- Training: Loss = MAE; Adam lr = 0.001; Dropout = 0.1; Early stopping patience = 15
- When to use: High-volume SKUs with complex seasonal patterns and long history (> 1 year equivalent)

#### 6.3 Statistical / Time Series Models
- Architectures: ETS(A,N,A) — Holt-Winters additive seasonality; SARIMA for complex seasonality

| Granularity | Primary Seasonal Period | Secondary |
|---|---|---|
| Daily | 7 (day of week) | 365 (annual) |
| Weekly | 52 (annual) | 13 (quarterly) |
| Monthly | 12 (annual) | 3 (quarterly) |
| Quarterly | 4 (annual) | — |
| Yearly | No seasonality | — |

- When to use: Interpretability requirement; prediction intervals needed

#### 6.4 Baseline / Fallback Model
- Fallback triggers: Feature pipeline failure; model convergence issue
- Fallback model: Same period last year (naive seasonal)
- Logging & alerting: Alert if fallback rate > 10%

### 7. Ensemble & Weighting

#### 7.1 Ensemble Scheme
- Combination: D̂_t = w_lgbm × LightGBM + w_ets × ETS + w_nbeats × N-BEATS
- Weight determination: Error-inverse weighting on 8-period rolling WMAPE

#### 7.2 Dynamic Weight Schedule

| History Length | LightGBM | ETS | N-BEATS |
|---|---|---|---|
| New Launch boundary to 1 year equiv. | 60% | 40% | 0% |
| > 1 year equivalent | 50% | 30% | 20% |

### 8. Uncertainty Quantification
- Method: Conformal prediction on residuals
- Output: [P10, P50, P90]
- Use case: Safety stock optimisation at target service level

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Capping: min(forecast, 1.5 × full-year rolling max)
- Manual overrides: Range review decisions; promotional plan changes
- Alignment constraints: Forecast within ±20% of prior year same period unless justified

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | WMAPE Target | Bias Alert | Coverage Target |
|---|---|---|---|
| Daily | < 20% | \|Bias\| > 10% | 80% P10–P90 |
| Weekly | < 18% | \|Bias\| > 8% | 80% P10–P90 |
| Monthly | < 15% | \|Bias\| > 7% | 80% P10–P90 |
| Quarterly | < 12% | \|Bias\| > 6% | 80% P10–P90 |
| Yearly | < 10% | \|Bias\| > 5% | 80% P10–P90 |

#### 10.2 Backtesting Protocol

| Granularity | Method | Train | Test | Min History |
|---|---|---|---|---|
| Daily | Rolling window | 180 days | 30 days | 365 days |
| Weekly | Rolling window | 52 weeks | 13 weeks | 104 weeks |
| Monthly | Rolling window | 24 months | 6 months | 24 months |
| Quarterly | Rolling window | 8 quarters | 2 quarters | 8 quarters |
| Yearly | Expanding window | All available | 1 year | 3 years |

#### 10.3 Retraining & Data Freshness

| Granularity | Cadence | Incremental | Latency |
|---|---|---|---|
| Daily | Daily | No | T+4 hours |
| Weekly | Weekly | No | T+1 day |
| Monthly | Monthly | No | T+2 days |
| Quarterly | Quarterly | No | T+3 days |
| Yearly | Annually | No | T+7 days |

### 11. Exception Handling & Overrides
- Automatic exception detection: Forecast > 2 × historical max; 3+ consecutive zero actuals; bias drift > alert threshold for 4 periods
- Manual override process: Planner approval via dashboard; reason code required
- Override expiration: Single cycle unless permanent range change flagged

### 12. Reclassification / Model Selection

| Granularity | To Growth | To Decline | Transition |
|---|---|---|---|
| Daily | Positive slope p < 0.05, 4 consecutive 90-day windows | Negative slope p < 0.05, 4 consecutive 90-day windows | Soft blend over 4 periods |
| Weekly | Positive slope p < 0.05, 4 consecutive 13-week windows | Negative slope p < 0.05, 4 consecutive 13-week windows | Soft blend over 4 weeks |
| Monthly | Positive slope p < 0.05, 4 consecutive 6-month windows | Negative slope p < 0.05, 4 consecutive 6-month windows | Soft blend over 4 months |
| Quarterly | Positive slope p < 0.05, 4 consecutive windows | Negative slope p < 0.05, 4 consecutive windows | Soft blend over 2 quarters |
| Yearly | Positive slope p < 0.05, 3 consecutive windows | Negative slope p < 0.05, 3 consecutive windows | Soft blend over 2 years |

### 13. Review Cadence
- Performance monitoring: Per cycle automated dashboard
- Model review meeting: Bi-weekly S&OP forecast review
- Full model re-evaluation: Quarterly

---

## L5 · Decline

### 1. Definition
Predicts demand for SKUs with a statistically confirmed negative demand slope, requiring trend-aware models with downward bias controls to avoid systematic over-forecasting and inventory accumulation.

### 2. Detailed Description
- **Applicable scenarios:** Ageing products, distribution losses, category contraction, competitive displacement
- **Boundaries:** History ≥ New Launch upper bound; Mann-Kendall p < 0.05 negative slope
- **Key demand characteristics:** Consistent downward slope, shrinking volume, possibly rising CV² as volume drops
- **Differentiation from other models:** Unlike Phasing Out, decline is market-driven not supply-decision-driven; unlike Inactive, demand still exists

### 3. Business Impact
- **Primary risk (over-forecast):** Excess inventory accumulation — write-offs and obsolescence dominant risk
- **Primary risk (under-forecast):** Minimal concern — declining SKU stockouts are low priority
- **Strategic importance:** Medium — inventory risk and write-off prevention are primary objectives

### 4. Priority Level
🟠 Tier 2 — Over-forecast risk dominates; inventory write-off prevention is key business objective.

### 5. Model Strategy Overview

#### 5.1 Zero-Demand Handling (Hurdle)
- Active event threshold: P(demand > 0) > 0.50 — declining SKUs approach zero over time
- Classifier type: Logistic Regression with trend features
- Regressor type: LightGBM with negative slope features
- Fallback when disagree: Forecast = 0 if classifier < 0.50

#### 5.2 Analogue / Similarity Logic
- Number of analogues: k = 3 (declining SKUs from same category)
- Similarity criteria: Category, decline rate (weekly slope coefficient), volume at decline start
- Temporal decay weight: weight = exp(−age / half-life)

| Granularity | Half-Life |
|---|---|
| Daily | 21 days |
| Weekly | 6 weeks |
| Monthly | 3 months |
| Quarterly | 2 quarters |
| Yearly | 1.5 years |

- Aggregation method: Weighted mean of decline trajectories

#### 5.3 Feature Engineering

| Granularity | Slope Window | Key Features |
|---|---|---|
| Daily | β_90day | Periods since peak, rolling mean, distribution loss rate, competitor entry flag |
| Weekly | β_13week | Weeks since peak, rolling mean, distribution loss rate, category index |
| Monthly | β_6month | Months since peak, rolling mean, category index |
| Quarterly | β_4quarter | Quarters since peak, rolling mean |
| Yearly | β_3year | Years since peak |

- Categorical encoding: Target encoding smoothing = 10

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM with downward bias correction
- Configuration: Objective = reg:squarederror; Metric = WMAPE, MAE
- Key features: Slope coefficient, periods since peak, rolling mean, distribution loss rate, category index
- When to use: Primary model

#### 6.2 Deep Learning (DL)
- Architectures: Not recommended — complexity unwarranted for declining SKUs
- When to use: Not applicable

#### 6.3 Statistical / Time Series Models
- Architectures: ETS(A,A,N) with damped trend — prevents over-extrapolation of decline

| Granularity | Damping Factor (phi) |
|---|---|
| Daily | 0.90 |
| Weekly | 0.85 |
| Monthly | 0.80 |
| Quarterly | 0.75 |
| Yearly | 0.70 |

- When to use: When interpretability needed; damped trend prevents forecast crossing zero prematurely

#### 6.4 Baseline / Fallback Model
- Fallback triggers: Slope reversal for 3+ consecutive periods
- Fallback model: Short rolling mean — conservative hold
- Logging & alerting: Alert if fallback rate > 20%

### 7. Ensemble & Weighting

#### 7.1 Ensemble Scheme
- Combination: D̂_t = w_lgbm × LightGBM + w_ets × ETS(damped)
- Weight determination: Error-inverse weighting on 4-period rolling MAE

#### 7.2 Dynamic Weight Schedule

| Decline Stage | LightGBM | ETS Damped |
|---|---|---|
| Early decline (mild slope, CV² still low) | 70% | 30% |
| Late decline (steep slope, rising CV²) | 50% | 50% |

### 8. Uncertainty Quantification
- Method: Quantile regression
- Output: [P10, P50, P90]
- Use case: P10 for minimum buy; P50 for base; P90 for worst-case inventory cover

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Capping: min(forecast, prior period rolling mean) — prevent upward drift in forecast
- Manual overrides: Delisting date input; clearance promotion flags
- Alignment constraints: Forecast must not exceed current stock on hand + confirmed inbound

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | WMAPE Target | Over-Forecast Bias Alert | Train | Test |
|---|---|---|---|---|
| Daily | < 25% | Bias > +10% | 180 days | 30 days |
| Weekly | < 20% | Bias > +10% | 26 weeks | 4 weeks |
| Monthly | < 18% | Bias > +8% | 12 months | 3 months |
| Quarterly | < 15% | Bias > +6% | 4 quarters | 2 quarters |
| Yearly | < 12% | Bias > +5% | 3 years | 1 year |

#### 10.3 Retraining & Data Freshness

| Granularity | Cadence | Incremental | Latency |
|---|---|---|---|
| Daily | Daily | No | T+4 hours |
| Weekly | Weekly | No | T+1 day |
| Monthly | Monthly | No | T+2 days |
| Quarterly | Quarterly | No | T+3 days |
| Yearly | Annually | No | T+7 days |

### 11. Exception Handling & Overrides
- Automatic exception detection: Forecast > prior rolling mean; slope reversal for 3+ consecutive periods
- Manual override process: Supply chain planner sign-off; reason code logged
- Override expiration: Single cycle

### 12. Reclassification / Model Selection

| Granularity | To Inactive | To Mature | Transition |
|---|---|---|---|
| Daily | 0 demand ≥ 91 consecutive days | Slope reverses positive p < 0.05 for 4 windows | Inactive = hard; Mature = soft blend 4 periods |
| Weekly | 0 demand ≥ 13 consecutive weeks | Slope reverses positive p < 0.05 for 4 windows | Inactive = hard; Mature = soft blend 4 weeks |
| Monthly | 0 demand ≥ 3 consecutive months | Slope reverses positive p < 0.05 for 4 windows | Inactive = hard; Mature = soft blend 4 months |
| Quarterly | 0 demand ≥ 1 consecutive quarter | Slope reverses positive p < 0.05 for 3 windows | Inactive = hard; Mature = soft blend 2 quarters |
| Yearly | 0 demand ≥ 1 consecutive year | Slope reverses positive p < 0.05 for 2 windows | Inactive = hard; Mature = soft blend 2 years |

### 13. Review Cadence
- Performance monitoring: Per cycle — over-forecast alert primary watch item
- Model review meeting: Bi-weekly — focus on obsolescence risk
- Full model re-evaluation: Quarterly or on delisting decision

---

## L6 · Phasing Out

### 1. Definition
Predicts residual demand for SKUs with a confirmed planned discontinuation date, where the primary objective is inventory run-down optimisation rather than demand accuracy.

### 2. Detailed Description
- **Applicable scenarios:** Confirmed delisting, range rationalisation, product replacement, end-of-life
- **Boundaries:** Discontinuation flag set in system; remaining demand horizon is known and finite
- **Key demand characteristics:** Declining or flat residual demand, possible clearance spike, known hard stop date
- **Differentiation from other models:** Unlike Decline, the end date is known and supply-side decision-driven — not market-driven

### 3. Business Impact
- **Primary risk (over-forecast):** Residual stock at delisting — write-off cost
- **Primary risk (under-forecast):** Stockout before planned end date — customer complaints
- **Strategic importance:** Medium — clean exit minimises write-off and frees working capital

### 4. Priority Level
🟠 Tier 2 — Inventory write-off risk is primary concern; clean exit is the business objective.

### 5. Model Strategy Overview

#### 5.1 Zero-Demand Handling (Hurdle)
- Hard zero forecast after confirmed end date — no model override permitted
- Pre-end-date: Linear decay toward zero at end date
- Fallback: Flat short rolling mean until end date if decay underperforms

#### 5.2 Analogue / Similarity Logic
- Number of analogues: k = 3 (previously phased-out SKUs from same category)
- Similarity criteria:

| Granularity | Similarity Criteria |
|---|---|
| Daily | Category, days remaining to delist, volume at phase-out flag date |
| Weekly | Category, weeks remaining, volume at phase-out flag date |
| Monthly | Category, months remaining, volume at phase-out flag date |
| Quarterly | Category, quarters remaining |
| Yearly | Category, years remaining |

- Temporal decay weight: weight = exp(−age / half-life) with half-life = 4 periods
- Aggregation method: Weighted mean of historical phase-out trajectories

#### 5.3 Feature Engineering
- Rolling statistics: Short window rolling mean; periods remaining to end date
- Date/time features: Periods to delisting, holiday flag, clearance promotion flag
- External signals: Clearance price depth, successor SKU availability flag

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM (simple feature set)
- Key features: Periods to end date, rolling mean, clearance promo flag, successor availability
- When to use: When periods remaining > switch threshold (see 6.3)

#### 6.2 Deep Learning (DL)
- Architectures: Not applicable — horizon too short; end date known

#### 6.3 Statistical / Time Series Models
- Architectures: Linear decay model

```
Demand(t) = Demand(T0) × (Periods_Remaining(t) / Total_Periods_at_Flag)
```

| Granularity | Switch to Linear Decay at |
|---|---|
| Daily | < 30 days remaining |
| Weekly | < 8 weeks remaining |
| Monthly | < 3 months remaining |
| Quarterly | < 1 quarter remaining |
| Yearly | < 6 months remaining |

#### 6.4 Baseline / Fallback Model
- Fallback: Short rolling mean (conservative hold)
- Alert if forecast > current stock on hand at any point

### 7. Ensemble & Weighting

#### 7.1 Dynamic Weight Schedule

| Periods to End Date | Linear Decay | LightGBM |
|---|---|---|
| > 2× switch threshold | 40% | 60% |
| 1×–2× switch threshold | 70% | 30% |
| < 1× switch threshold | 90% | 10% |

### 8. Uncertainty Quantification
- Method: Quantile regression on phase-out analogue spread
- Output: [P10, P50, P90]
- Use case: P90 for stock cover planning; P10 for minimum hold; P50 for base run-down

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Hard zero on and after confirmed end date — no exceptions
- Capping: min(forecast, current stock on hand)
- Manual overrides: Clearance promotion uplift; successor delay extending phase-out period

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | Primary KPI | Over-Forecast Alert |
|---|---|---|
| Daily | MAE + Residual stock at exit date | Bias > +10% |
| Weekly | MAE + Residual stock at exit date | Bias > +10% |
| Monthly | MAE + Residual stock at exit date | Bias > +8% |
| Quarterly | Residual stock at exit date | Bias > +6% |
| Yearly | Residual stock at exit date | Bias > +5% |

#### 10.2 Backtesting Protocol

| Granularity | Method | Minimum Eval History |
|---|---|---|
| Daily | Historical phase-out events — forecast vs actual residual | 10 completed phase-outs |
| Weekly | Historical phase-out events | 10 completed phase-outs |
| Monthly | Historical phase-out events | 10 completed phase-outs |
| Quarterly | Historical phase-out events | 10 completed phase-outs |
| Yearly | Historical phase-out events | 10 completed phase-outs |

#### 10.3 Retraining & Data Freshness

| Granularity | Cadence | Latency |
|---|---|---|
| Daily | Daily until end date | T+4 hours |
| Weekly | Weekly until end date | T+1 day |
| Monthly | Monthly until end date | T+2 days |
| Quarterly | Quarterly until end date | T+3 days |
| Yearly | Annually until end date | T+7 days |

### 11. Exception Handling & Overrides
- Automatic exception detection: Forecast > stock on hand; end date change detected in system
- Manual override process: Supply chain planner sign-off required; reason logged
- Override expiration: Single cycle

### 12. Reclassification / Model Selection
- Reclassify to Inactive automatically on confirmed end date
- No holding period — hard switch on end date
- If end date is pushed back: Extend Phasing Out; recalibrate decay model

### 13. Review Cadence
- Performance monitoring: Per cycle until delisting with residual stock tracker
- Model review meeting: Weekly supply review until delisting
- Full model re-evaluation: After every 10 completed phase-outs

---

## L7 · Inactive

### 1. Definition
Assigns zero forecast to SKUs with zero demand beyond the inactive threshold while continuously monitoring for reactivation signals to enable rapid lifecycle graduation.

### 2. Detailed Description
- **Applicable scenarios:** Obsolete SKUs, delisted products, seasonal items in off-season, temporarily suspended lines
- **Boundaries:**

| Granularity | Inactive Threshold |
|---|---|
| Daily | Zero demand ≥ 91 consecutive days |
| Weekly | Zero demand ≥ 13 consecutive weeks |
| Monthly | Zero demand ≥ 3 consecutive months |
| Quarterly | Zero demand ≥ 1 consecutive quarter |
| Yearly | Zero demand ≥ 1 consecutive year |

- **Key demand characteristics:** Zero demand; possible future reactivation for seasonal or relaunched items
- **Differentiation from other models:** Unlike Phasing Out, no planned end date may exist — item may reactivate; unlike Cold Start, has prior demand history available

### 3. Business Impact
- **Primary risk (over-forecast):** Stock build for items with no demand — pure waste
- **Primary risk (under-forecast):** Missing reactivation signal — lost sales on relaunch
- **Strategic importance:** Low for pure obsoletes; high for seasonal items approaching active season

### 4. Priority Level
🟡 Tier 3 — Monitoring only; exception-driven rather than routine forecasting.

### 5. Model Strategy Overview

#### 5.1 Reactivation Classifier (Hurdle)
- Default forecast: 0 (no model runs unless reactivation triggered)
- Reactivation trigger: P(reactivation) > 0.60
- Classifier type: Logistic Regression

| Granularity | Monitoring Cadence | Key Input Signals |
|---|---|---|
| Daily | Daily scan | Prior year same day, seasonal index, category activity |
| Weekly | Weekly scan | Prior year same week, seasonal flag, category trend |
| Monthly | Monthly scan | Prior year same month, season start proximity |
| Quarterly | Quarterly scan | Prior year same quarter, long-cycle index |
| Yearly | Annual scan | Long-cycle demand pattern, macro index |

#### 5.2 Analogue / Similarity Logic
- Not applicable unless reactivation detected — graduate to Cold Start on trigger

#### 5.3 Feature Engineering
- Periods since last non-zero demand
- Prior year same-period demand (if available)
- Seasonal index for current period
- Category activity index (is category growing?)
- External: Relaunch flag in system, promotional calendar, season start proximity

### 6. Model Families

#### 6.1 Machine Learning
- Reactivation classifier only: Logistic Regression
- Features: Periods since last demand, prior year demand, seasonal flag, category trend index
- Metric: Sensitivity (recall) on reactivation events — minimise missed reactivations

#### 6.2 Deep Learning
- Not applicable — default zero forecast

#### 6.3 Statistical
- Not applicable — default zero forecast

#### 6.4 Baseline / Fallback
- Default: Zero forecast always
- Immediate alert on any non-zero demand observation

### 7. Ensemble & Weighting
- Not applicable — zero forecast by default; no ensemble

### 8. Uncertainty Quantification
- Binary probability: P(reactivation) reported weekly to planners
- Alert dashboard: SKUs with P(reactivation) > 0.40 flagged as watchlist

### 9. Business Rules & Post-Processing
- Forecast = 0 unless P(reactivation) > 0.60
- On trigger: Immediately graduate to Cold Start model — no blending
- Manual overrides: Relaunch plan input by commercial team — overrides classifier threshold

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | Primary KPI | Alert Trigger |
|---|---|---|
| Daily | Reactivation detection sensitivity | Any non-zero demand → immediate alert |
| Weekly | Reactivation detection sensitivity | Any non-zero demand → immediate alert |
| Monthly | Reactivation detection sensitivity | Any non-zero demand → immediate alert |
| Quarterly | Reactivation detection sensitivity | Any non-zero demand → immediate alert |
| Yearly | Reactivation detection sensitivity | Any non-zero demand → immediate alert |

- Secondary KPI: False positive rate (flagging items that don't reactivate — wastes planner time)
- Target: Sensitivity > 90%; False positive rate < 15%

#### 10.2 Backtesting Protocol

| Granularity | Method | Success Criteria |
|---|---|---|
| Daily | Historical reactivation events | Classifier detects within 3 days of first non-zero demand |
| Weekly | Historical reactivation events | Classifier detects within 1 week |
| Monthly | Historical reactivation events | Classifier detects within 1 month |
| Quarterly | Historical reactivation events | Classifier detects within 1 quarter |
| Yearly | Historical reactivation events | Classifier detects within 1 year |

#### 10.3 Retraining & Data Freshness

| Granularity | Cadence | Latency |
|---|---|---|
| Daily | Monthly (low priority) | T+4 hours |
| Weekly | Monthly | T+1 day |
| Monthly | Quarterly | T+2 days |
| Quarterly | Semi-annually | T+3 days |
| Yearly | Annually | T+7 days |

### 11. Exception Handling & Overrides
- Automatic exception detection: Any non-zero demand observation after inactive threshold — immediate system alert
- Manual override: Commercial team relaunch flag → graduate to Cold Start immediately, bypass classifier
- Override expiration: Permanent until reclassification completes

### 12. Reclassification / Model Selection

| Trigger | Target Segment | Switch Type |
|---|---|---|
| First non-zero demand observed | Cold Start | Immediate hard switch — no holding period |
| Seasonal pattern in prior year detected | Seasonal watchlist | Soft flag — monitor only |
| Commercial relaunch flag set | Cold Start | Immediate hard switch |

### 13. Review Cadence
- Performance monitoring: Per granularity cycle — reactivation watchlist dashboard
- Model review meeting: Monthly obsolescence and reactivation review
- Full model re-evaluation: Semi-annually

---

*End of Dimension 1 · Lifecycle Pattern*
*7 Segments Complete · L1 through L7*
