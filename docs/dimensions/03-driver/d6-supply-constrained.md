## D6 · Supply Constrained

### 1. Definition
Predicts true (unconstrained) demand for SKUs where historical observed demand is systematically below true demand due to supply stockouts, ensuring forecasts reflect genuine customer appetite rather than corrupted supply-limited actuals.

### 2. Detailed Description
- **Applicable scenarios:** Frequently out-of-stock SKUs, supply-limited launches, allocation periods, supply chain disrupted categories
- **Boundaries:**

| Granularity | Detection Condition | Window |
|---|---|---|
| Daily | Stockout days > 5 in rolling 90-day window | 90-day rolling |
| Weekly | Stockout weeks > 4 in rolling 52-week window | 52-week rolling |
| Monthly | Stockout months > 2 in rolling 12-month window | 12-month rolling |
| Quarterly | Stockout quarters > 1 in rolling 4-quarter window | 4-quarter rolling |
| Yearly | Stockout years > 1 in rolling 3-year window | 3-year rolling |

- **Key demand characteristics:** Observed demand systematically understates true demand; pent-up demand post-stockout; lost sales not captured in demand signal
- **Differentiation from other models:** Unlike all other segments, this is a **data correction driver** not a demand shape driver — the primary function is to reconstruct unconstrained demand before any other model is applied

### 3. Business Impact
- **Primary risk (over-forecast of unconstrained):** Safety stock set too high post-correction
- **Primary risk (under-correction):** Forecast trained on constrained demand perpetuates stockout cycle
- **Strategic importance:** Critical — supply-constrained forecasts trained on raw actuals are systematically biased downward; this corrupts safety stock, reorder points, and capacity planning

### 4. Priority Level
🔴 Tier 1 — Must be corrected before any other model is applied; uncorrected supply constraint silently corrupts all downstream forecasting.

### 5. Model Strategy Overview

#### 5.1 Lost Sales Reconstruction (Primary Step)
- Step 1: Flag all stockout periods using inventory on hand data
- Step 2: Estimate lost sales in each stockout period
- Step 3: Replace observed demand with unconstrained demand estimate
- Step 4: Apply standard behavior model on corrected demand series

**Lost Sales Estimation Methods:**

```
Method 1 — Fill Rate Adjustment (when order data available):
  d_unconstrained(t) = d_observed(t) / Fill_Rate(t)
  Fill_Rate(t) = Units_Shipped(t) / Units_Ordered(t)

Method 2 — Pre-Stockout Trend Extrapolation (when order data unavailable):
  d_unconstrained(t) = d_rolling_mean(t−1 to t−w, excl. stockout periods)
  where w = medium rolling window for granularity

Method 3 — Post-Stockout Pent-Up Demand (supplementary signal):
  Pent-up demand = Mean(d_{t+1} to d_{t+k}) − rolling mean, for k periods post-stockout
  Lost sales proxy = Pent-up demand × stockout duration ratio

Method 4 — Category Index (when no inventory data):
  d_unconstrained(t) = d_observed(t) × (Category_growth_rate_t / SKU_growth_rate_pre_stockout)
```

| Granularity | Preferred Method | Fallback Method |
|---|---|---|
| Daily | Fill Rate Adjustment (Method 1) | Pre-Stockout Extrapolation (Method 2) |
| Weekly | Fill Rate Adjustment (Method 1) | Pre-Stockout Extrapolation (Method 2) |
| Monthly | Fill Rate Adjustment (Method 1) | Post-Stockout Pent-Up (Method 3) |
| Quarterly | Category Index (Method 4) | Pre-Stockout Extrapolation (Method 2) |
| Yearly | Category Index (Method 4) | Pre-Stockout Extrapolation (Method 2) |

#### 5.2 Feature Engineering (Post-Correction)
- All features computed on **corrected unconstrained demand series**, not raw observed demand
- Stockout flag retained as feature in downstream model
- Stockout frequency feature: Number of stockout periods in rolling window
- Correction magnitude feature: d_unconstrained / d_observed ratio (signals correction scale)

### 6. Model Families

#### 6.1 ML: LightGBM on corrected demand series
- Additional feature: Stockout frequency, correction ratio, inventory policy flag
- When to use: After demand correction; same as standard behavior model

#### 6.2 DL: TFT on corrected demand series
- Additional covariate: Stockout flag as past observed covariate

#### 6.3 Statistical: Standard behavior model on corrected series
- Croston if intermittent; ETS if stable — applied to corrected demand

#### 6.4 Fallback: Category-level growth applied to last clean (non-stockout) demand observation

### 7. Ensemble & Weighting
- Same ensemble as underlying behavior segment applied to corrected demand
- Additional correction model weight: 10% weight to category index model as sanity check

### 8. Uncertainty Quantification
- Wider intervals during correction: [P5, P50, P95] — higher uncertainty from correction assumptions
- Standard intervals when correction validated: [P10, P50, P90]
- Use case: Safety stock set higher than standard segment due to stockout risk; reorder point elevated

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, corrected forecast)
- Correction cap: d_unconstrained ≤ 3 × d_observed (prevent over-correction)
- Correction floor: d_unconstrained ≥ d_observed (correction only upward; stockout never inflates downward)
- Manual overrides: Supply chain team stockout root cause flag; allocation policy input
- Alignment: Corrected forecast used for capacity and replenishment; observed demand used for actual sales reporting

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | Correction Accuracy | Post-Correction WMAPE | Stockout Rate Target | Bias Alert |
|---|---|---|---|---|
| Daily | Lost sales estimate within ±30% of fill-rate measure | < 25% | Stockout days < 3% | \|Bias\| > 15% |
| Weekly | Lost sales within ±25% | < 22% | Stockout weeks < 5% | \|Bias\| > 12% |
| Monthly | Lost sales within ±20% | < 18% | Stockout months < 8% | \|Bias\| > 10% |
| Quarterly | Lost sales within ±18% | < 15% | Stockout quarters < 10% | \|Bias\| > 8% |
| Yearly | Lost sales within ±15% | < 12% | Stockout years < 15% | \|Bias\| > 6% |

#### 10.2 Backtesting Protocol

| Granularity | Method | Notes |
|---|---|---|
| Daily | Rolling window on corrected series | Validate correction by comparing to fill-rate actuals where available |
| Weekly | Rolling window on corrected series | Same validation |
| Monthly | Rolling window | Same validation |
| Quarterly | Rolling window | Category index validation |
| Yearly | Expanding window | Category validation |

#### 10.3 Retraining & Data Freshness

| Granularity | Cadence | Stockout Flag Update | Latency |
|---|---|---|---|
| Daily | Daily | Real-time inventory feed | T+4 hours |
| Weekly | Weekly | Daily inventory update | T+1 day |
| Monthly | Monthly | Weekly inventory update | T+2 days |
| Quarterly | Quarterly | Monthly | T+3 days |
| Yearly | Annually | Quarterly | T+7 days |

### 11. Exception Handling & Overrides
- Automatic exception detection: Stockout rate > 20% in rolling window → escalate to supply chain; correction ratio > 3× → cap and alert; consecutive stockouts for 3+ periods → flag for root cause analysis
- Manual override: Supply team root cause and resolution timeline input; allocation policy flag; force unconstrained demand value from commercial intelligence
- Override expiration: Until stockout resolved and inventory replenished

### 12. Reclassification / Model Selection
- Remove Supply Constrained driver: Stockout rate < 2% for 6 consecutive periods — demand signal clean
- Retain flag: Even after stockout resolved, correct historical data permanently; do not revert to raw actuals
- Escalate: Chronic supply constraint (> 4 quarters) → escalate to supply strategy review

### 13. Review Cadence
- Performance monitoring: Daily stockout watchlist; weekly correction accuracy review
- Model review meeting: Weekly supply review with procurement and supply chain teams
- Full model re-evaluation: Quarterly; immediately on supply disruption resolution

---

*End of Dimension 3 · Driver Pattern*
*6 Segments Complete · D1 through D6*
