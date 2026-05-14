# Segment Model Template

## Dimension 12 · Lagged Signal

---

### 1. Definition
Predicts demand for SKUs where the observed demand signal consistently lags true consumption by a known duration, requiring lag correction to align the demand signal with actual consumption timing before any model is applied.

### 2. Detailed Description
- **Applicable scenarios:** Wholesale ordering that lags retail consumption, distributor orders that lag end-consumer purchases, B2B procurement lags, long pipeline categories (fashion, seasonal with pre-orders)
- **Boundaries:**

| Granularity | Signal Lag Threshold | Estimation Method |
|---|---|---|
| Daily | L > 3 days | CCF vs POS or supply chain pipeline |
| Weekly | L > 1 week | CCF vs POS; or pipeline |
| Monthly | L > 1 month | CCF vs consumption data; or pipeline |
| Quarterly | L > 1 quarter | Pipeline estimation |
| Yearly | L > 6 months | Pipeline estimation |

- **Key demand characteristics:** Observed orders arrive after true consumption has occurred; modelling on raw orders introduces systematic future-bias; consumption data (POS, usage data) is the preferred signal when available
- **Differentiation from other models:** Unlike Timing Dimension (Lagging), which describes demand arriving after a trigger, Signal Lagging describes the observation mechanism — orders are recorded after consumption; unlike Distorted, the total demand is correct — only timing is offset

### 3. Business Impact
- **Primary risk (over-forecast):** Using lagged signal as if it were contemporaneous — model sees "future" demand as current; biased inventory decisions
- **Primary risk (under-forecast):** Not recognising that current orders reflect past consumption — missing true current demand
- **Strategic importance:** High in multi-tier supply chains — lag correction enables true demand sensing; transforms order-based planning to consumption-based planning

### 4. Priority Level
🟠 **Tier 2** — Lag correction is a data pipeline issue; high value when consumption data is available; medium complexity.

### 5. Model Strategy Overview

#### 5.1 Signal Lag Correction
```
Correction approaches (in priority order):

Priority 1 — Use consumption/POS data directly:
  d_true(t) = d_POS(t)   [point-of-sale or consumption data at time t]
  This eliminates lag entirely — consumption = true demand at time t

Priority 2 — Shift observed signal back by L:
  d_corrected(t) = d_observed(t + L)
  Equivalently: d_true(t) = d_observed(t − L)
  Requires L periods of forward-looking data → use with caution

Priority 3 — Model the lag explicitly:
  d_true(t) = α + β × d_observed(t − L) + ARIMA residual
  Estimate L from CCF(d_observed, d_POS) or pipeline analysis

Forecast at time t for horizon h:
  F_true(t+h) = Model(d_corrected_history)
  F_observed(t+h) = F_true(t + h + L)   [shift forecast forward by lag]
```

#### 5.2 Analogue / Similarity Logic
- Per Behavior segment — applied after lag correction
- Additional: Analogues from same supply chain tier to validate L estimate

#### 5.3 Feature Engineering
- All features computed on **lag-corrected series** — not raw observed orders
- Additional features:

| Feature | Description |
|---|---|
| lag_L | Estimated signal lag (periods) |
| lag_confidence | High / Medium / Low based on CCF strength or pipeline data quality |
| correction_method | POS_direct / shift / modelled |
| pipeline_visibility | % of pipeline with confirmed consumption data |

| Granularity | Lag Features | Corrected Baseline Features |
|---|---|---|
| Daily | lag_L, correction_method, pipeline_visibility | 7/30/90-day corrected rolling mean, seasonal index |
| Weekly | lag_L, correction_method | 4/8/13-week corrected rolling mean, seasonal index |
| Monthly | lag_L, correction_method | 3/6/12-month corrected rolling mean |
| Quarterly | lag_L | 2/4-quarter corrected rolling mean |
| Yearly | lag_L | Annual corrected rolling mean |

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: Standard LightGBM per Behavior segment — applied to lag-corrected series
- When to use: After lag correction — same model as standard

#### 6.2 Deep Learning (DL)
- Architectures: TFT with lag correction applied to input series
- Note: TFT lookback window extended by L to cover equivalent consumption history

| Granularity | Extended Lookback | Output |
|---|---|---|
| Daily | Standard + L days | P10, P50, P90 |
| Weekly | Standard + L weeks | P10, P50, P90 |
| Monthly | Standard + L months | P10, P50, P90 |
| Quarterly | Standard + L quarters | P10, P50, P90 |
| Yearly | Standard + L years | P10, P50, P90 |

#### 6.3 Statistical / Time Series Models
- Standard ETS / ARIMA per Behavior segment applied to corrected series
- ARIMAX option: Use raw orders as exogenous variable with lag L: d_true(t) ~ d_obs(t−L)

#### 6.4 Baseline / Fallback Model
- Fallback: Shift raw orders back by estimated L — simple lag correction without model
- Alert if lag estimate changes > 1 period between estimations

### 7. Ensemble & Weighting

| Correction Method | LightGBM | Standard Stat | Lag-ARIMAX |
|---|---|---|---|
| POS direct (Priority 1) | 55% | 35% | 10% |
| Shift correction (Priority 2) | 45% | 35% | 20% |
| Modelled lag (Priority 3) | 30% | 30% | 40% |

### 8. Uncertainty Quantification
- Method: Standard per Behavior segment on corrected series; additional uncertainty for lag estimate error
- Output: [P10, P50, P90] — interval widened by lag uncertainty (σ_L × slope of demand)
- Use case: Safety stock accounts for lag uncertainty in addition to standard demand uncertainty

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, corrected forecast)
- POS priority rule: If POS or consumption data becomes available → immediately switch to Priority 1; discard order-based correction
- Lag drift monitor: Alert if L changes > 1 period — indicates supply chain structure change
- Manual overrides: Supply chain team pipeline structure change input; new POS data feed activation; lag L expert estimate input

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | Lag Estimate Accuracy | Post-Correction WMAPE | Downstream Alignment | Bias Alert |
|---|---|---|---|---|
| Daily | k* within ±2 days | Per Behavior std | r(corrected, POS) > 0.70 | \|Bias\| > 8% |
| Weekly | k* within ±1 week | Per Behavior std | r > 0.70 | \|Bias\| > 7% |
| Monthly | k* within ±1 month | Per Behavior std | r > 0.65 | \|Bias\| > 6% |
| Quarterly | k* within ±1 quarter | Per Behavior std | r > 0.65 | \|Bias\| > 5% |
| Yearly | k* within ±6 months | Per Behavior std | r > 0.60 | \|Bias\| > 4% |

#### 10.2 Backtesting Protocol

| Granularity | Train | Test |
|---|---|---|
| Daily | 180 days (corrected) | 30 days |
| Weekly | 52 weeks (corrected) | 13 weeks |
| Monthly | 24 months (corrected) | 6 months |
| Quarterly | 8 quarters (corrected) | 2 quarters |
| Yearly | All available | 1 year |

#### 10.3 Retraining

| Granularity | Cadence | Data Feed | Latency |
|---|---|---|---|
| Daily | Daily | POS daily; or order daily | T+4 hours |
| Weekly | Weekly | POS weekly | T+1 day |
| Monthly | Monthly | POS monthly | T+2 days |
| Quarterly | Quarterly | Consumption quarterly | T+3 days |
| Yearly | Annually | — | T+7 days |

### 11. Exception Handling & Overrides
- Auto-detect: POS data feed activated → immediately upgrade to Priority 1 (no correction needed); L shifts > 2 periods → supply chain structure change; r(corrected, POS) drops below 0.50 → lag estimate wrong
- Manual override: Supply chain restructuring (new distribution tier changes L); POS data newly available
- Override expiration: Per monthly lag stability check

### 12. Reclassification / Model Selection

| Condition | Target | Holding Period | Transition |
|---|---|---|---|
| POS data available and L → 0 | Pure Signal | Immediate | Hard switch to POS-based model |
| L drops below granularity threshold | Pure Signal | 3 estimations | Soft blend |
| Distortion detected on top of lag | Distorted + Lagged | Immediate | Apply both corrections |

### 13. Review Cadence
- Monthly lag stability monitor; quarterly pipeline structure review; annual full signal correction methodology reassessment

---

---
