# Segment Model Template

## Dimension 12 · Distorted

---

### 1. Definition
Predicts demand for SKUs where observed demand is systematically inflated or deflated by external factors unrelated to true consumption (DI > 0.15 in > 20% of periods), requiring distortion identification, correction, and unconstrained demand reconstruction before any model is applied.

### 2. Detailed Description
- **Applicable scenarios:** Frequently out-of-stock SKUs (supply constrained demand), categories with high return rates, data reporting errors, double-counting in order management systems, demand inflation from cancelled orders
- **Boundaries:**

| Granularity | DI Threshold | Period Threshold | Distortion Sources |
|---|---|---|---|
| Daily | DI > 0.15 | > 20% of days | Stockout, returns, reporting error, cancellations |
| Weekly | DI > 0.15 | > 20% of weeks | Same |
| Monthly | DI > 0.15 | > 20% of months | Same |
| Quarterly | DI > 0.15 | > 20% of quarters | Same |
| Yearly | DI > 0.15 | > 20% of years | Same |

- **Key demand characteristics:** Observed demand ≠ true demand; systematic bias in the signal; unconstrained true demand must be reconstructed before modelling; distortion source must be identified and corrected
- **Differentiation from other models:** Unlike Noisy (random noise), Distorted has a systematic cause; unlike Amplified (supply chain amplification), Distorted is within the demand measurement itself; unlike Lagged Signal (timing offset), Distorted is a magnitude issue

### 3. Business Impact
- **Primary risk (over-forecast):** Modelling on inflated demand (returns, cancellations) — excess inventory
- **Primary risk (under-forecast):** Modelling on deflated demand (stockout) — chronic under-supply; perpetuating the stockout cycle
- **Strategic importance:** Critical — distorted demand silently corrupts all downstream forecasting; undetected distortion is the most common source of systematic bias

### 4. Priority Level
🔴 **Tier 1** — Must be corrected before any model is applied; distorted baselines corrupt all downstream decisions including safety stock, reorder points, and capacity planning.

### 5. Model Strategy Overview

#### 5.1 Distortion Correction Pipeline
```
STEP 1: Identify distortion source
  Types: Supply stockout | Returns inflation | Reporting errors
         Order cancellations | Double counting | System migration gaps

STEP 2: Estimate true demand per distortion type

  Type 1 — Supply Stockout:
    d_true(t) = d_observed(t) / Fill_Rate(t)
    Fill_Rate(t) = Units_Shipped / Units_Ordered  [if order data available]
    OR: d_true(t) = pre_stockout_rolling_mean(t)

  Type 2 — Returns Inflation:
    d_true(t) = d_gross(t) − returns(t)   [net demand]
    returns(t) = units returned to stock in period t

  Type 3 — Reporting Error:
    d_true(t) = interpolation between last_clean(t−) and next_clean(t+)
    Linear interpolation: d_true(t) = d(t−) + (d(t+) − d(t−)) × (t − t−) / (t+ − t−)

  Type 4 — Order Cancellations:
    d_true(t) = confirmed_net_orders(t)   [orders − cancellations]

  Type 5 — Double Counting:
    d_true(t) = deduplicated_transaction_count(t)

STEP 3: Replace distorted periods with d_true(t)

STEP 4: Apply standard behavior model to corrected series
```

#### 5.2 Analogue / Similarity Logic
- Per Behavior segment standard — applied after correction
- Additional: Use analogues from same category to validate d_true estimate (sanity check)

#### 5.3 Feature Engineering
- All features computed on **corrected demand d_true(t)** — not raw d_observed(t)
- Additional features:

| Feature | Description |
|---|---|
| distortion_flag(t) | 1 if period was distorted and corrected; 0 if clean |
| correction_magnitude(t) | d_true / d_observed ratio (scale of correction applied) |
| distortion_type | Categorical: stockout / returns / reporting / cancellation / double_count |
| fill_rate(t) | Fill rate if stockout distortion (from order management system) |
| correction_confidence | High / Medium / Low based on data quality of correction method |

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: Standard LightGBM per Behavior segment — applied to corrected series
- Additional features: distortion_flag, correction_magnitude, distortion_type
- Configuration: Same as standard Behavior segment model
- When to use: After correction — same model as would apply without distortion

#### 6.2 Deep Learning (DL)
- Standard TFT / N-BEATS per Behavior segment — applied to corrected series
- Additional covariate: distortion_flag as past observed covariate (flags corrected periods)

| Granularity | Lookback | Additional Covariate | Output |
|---|---|---|---|
| Daily | 180 days | distortion_flag(t) | P10, P50, P90 |
| Weekly | 52 weeks | distortion_flag(t) | P10, P50, P90 |
| Monthly | 24 months | distortion_flag(t) | P10, P50, P90 |
| Quarterly | 8 quarters | distortion_flag(t) | P10, P50, P90 |
| Yearly | 5 years | distortion_flag(t) | P10, P50, P90 |

#### 6.3 Statistical / Time Series Models
- Standard ETS / SARIMA per Behavior segment — applied to corrected series
- Outlier treatment: Use corrected d_true; mark distorted periods with low weight in estimation

#### 6.4 Baseline / Fallback Model
- Fallback: Category-level growth rate applied to last clean (non-distorted) observation
- Alert: If distortion source cannot be identified → escalate to data team; do not model until resolved

### 7. Ensemble & Weighting
- Standard ensemble per Behavior segment — applied to corrected series
- Correction confidence weighting: Periods with low correction_confidence → down-weight in model training

| Correction Confidence | Training Weight |
|---|---|
| High (fill rate data available) | 1.0× |
| Medium (interpolation used) | 0.6× |
| Low (proxy only) | 0.3× |

### 8. Uncertainty Quantification
- Method: Wider intervals during correction — additional uncertainty from correction assumptions
- Output: [P5, P50, P95] during high-distortion periods; [P10, P50, P90] post-correction validated
- Use case: Safety stock set higher than standard segment due to historical distortion risk

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, corrected forecast)
- Correction cap: d_true ≤ 3 × d_observed (prevent over-correction)
- Correction floor: d_true ≥ d_observed if distortion is downward inflation (stockout only goes up not down)
- History permanence: Corrected demand replaces raw demand permanently in training data — never revert to raw actuals
- Manual overrides: Supply chain team stockout root cause flag; data team reporting error confirmation; finance team cancellation rate input

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | Correction Accuracy | Post-Correction WMAPE | DI Post-Correction | Distortion Detection Rate | Bias Alert |
|---|---|---|---|---|---|
| Daily | DI < 0.10 after correction | Per Behavior std | < 0.10 | > 85% | \|Bias\| > 10% |
| Weekly | DI < 0.10 | Per Behavior std | < 0.10 | > 85% | \|Bias\| > 8% |
| Monthly | DI < 0.10 | Per Behavior std | < 0.10 | > 85% | \|Bias\| > 7% |
| Quarterly | DI < 0.10 | Per Behavior std | < 0.10 | > 80% | \|Bias\| > 6% |
| Yearly | DI < 0.10 | Per Behavior std | < 0.10 | > 80% | \|Bias\| > 5% |

#### 10.2 Backtesting Protocol
- Backtest on corrected series only — validate correction improves WMAPE vs raw
- Correction validation: If corrected WMAPE > raw WMAPE → review correction method

| Granularity | Train | Test |
|---|---|---|
| Daily | 180 days (corrected) | 30 days |
| Weekly | 52 weeks (corrected) | 13 weeks |
| Monthly | 24 months (corrected) | 6 months |
| Quarterly | 8 quarters (corrected) | 2 quarters |
| Yearly | All available (corrected) | 1 year |

#### 10.3 Retraining

| Granularity | Cadence | Distortion Feed Latency |
|---|---|---|
| Daily | Daily | Real-time inventory + returns feed |
| Weekly | Weekly | Daily inventory update |
| Monthly | Monthly | Weekly update |
| Quarterly | Quarterly | Monthly update |
| Yearly | Annually | Quarterly update |

### 11. Exception Handling & Overrides
- Auto-detect: DI rises above 0.20 in new period → immediate alert; correction ratio > 3× → cap and alert; distortion source unidentifiable → escalate to P1 data issue
- Manual override: Supply team stockout root cause; data team error correction; finance team cancellation data provision
- Override expiration: Until distortion source resolved and confirmed clean

### 12. Reclassification / Model Selection

| Condition | Target | Holding Period | Transition |
|---|---|---|---|
| DI < 0.10 for 6 consecutive months | Pure Signal | 6 months | Hard switch |
| SNR of corrected series < 1.0 | Noisy (secondary issue) | 2 estimations | Add noise correction layer |
| AR of corrected series > 1.5 | Amplified (secondary issue) | 2 estimations | Add de-amplification layer |

### 13. Review Cadence
- Daily distortion watchlist; weekly correction accuracy review; monthly distortion source audit; quarterly data pipeline review; annual full correction methodology reassessment

---

---
