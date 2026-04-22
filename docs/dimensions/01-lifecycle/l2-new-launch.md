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

