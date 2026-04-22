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

