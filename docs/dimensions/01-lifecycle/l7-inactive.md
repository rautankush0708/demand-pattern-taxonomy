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
