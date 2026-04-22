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
