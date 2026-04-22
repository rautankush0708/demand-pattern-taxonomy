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
