# Segment Model Template

## Dimension 9 · Lagging

---

### 1. Definition
Predicts demand for SKUs where demand follows an identifiable external trigger signal with a consistent positive delay, enabling causal forecasting by detecting the trigger and projecting demand forward by the known lag.

### 2. Detailed Description
- **Applicable scenarios:** Aftermarket parts (follow equipment sales), consumables following capital equipment installation, re-order triggered by prior delivery cycle, categories driven by downstream production schedule
- **Boundaries:**

| Granularity | Detection Condition | Lag Time Range | Min History |
|---|---|---|---|
| Daily | Max CCF at k > 0; \|CCF\| > 2/√n | 3–30 days after trigger | ≥ 180 days |
| Weekly | Max CCF at k > 0; \|CCF\| > 2/√n | 1–13 weeks after | ≥ 52 weeks |
| Monthly | Max CCF at k > 0; \|CCF\| > 2/√n | 1–6 months after | ≥ 24 months |
| Quarterly | Max CCF at k > 0; \|CCF\| > 2/√n | 1–4 quarters after | ≥ 8 quarters |
| Yearly | Max CCF at k > 0; \|CCF\| > 2/√n | 1–2 years after | ≥ 5 years |

- **Key demand characteristics:** Demand follows trigger with consistent delay; trigger is observable before demand arrives; lag is the key planning parameter
- **Differentiation from other models:** Unlike Leading, demand follows the trigger not precedes it; unlike Coincident, there is a measurable positive lag; unlike Deferred, lag is structural not customer-decision-driven

### 3. Business Impact
- **Primary risk (over-forecast):** Over-ordering before trigger-driven demand arrives
- **Primary risk (under-forecast):** Not responding to trigger signal in time — stockout when lagged demand arrives
- **Strategic importance:** High — knowing the lag enables precise replenishment timing relative to the trigger event

### 4. Priority Level
🟠 **Tier 2** — High value in aftermarket and B2B contexts where trigger data is available.

### 5. Model Strategy Overview

#### 5.1 Zero-Demand Handling (Hurdle)
- Active event threshold: P(demand > 0) > 0.60
- Classifier type: Logistic Regression with lagged trigger features
- Regressor type: LightGBM with trigger at lag k*
- Fallback: Standard behavior model without lag structure

#### 5.2 Analogue / Similarity Logic
- Number of analogues: k = 3 (SKUs with similar lag structure in same category)
- Similarity criteria: Lag k* ±2 periods, |CCF| strength ±0.10, category, product type
- Temporal decay: weight = exp(−age / half-life)

| Granularity | Half-Life |
|---|---|
| Daily | 90 days |
| Weekly | 13 weeks |
| Monthly | 6 months |
| Quarterly | 3 quarters |
| Yearly | 2 years |

#### 5.3 Feature Engineering

**Lagged Trigger Feature Construction:**
```
lagged_trigger(t) = trigger(t − k*)   [past value at optimal lag]
CCF_strength      = |CCF(k*)|
lag_stability     = CV(k* across rolling windows)
trigger_trend     = slope of trigger series over rolling window
```

| Granularity | Lagged Features | Baseline Features |
|---|---|---|
| Daily | trigger(t−3 to t−30 days), k*, CCF strength, lag drift | 7/30/90-day rolling mean, seasonal index |
| Weekly | trigger(t−1 to t−13 weeks), k*, CCF | 4/8/13-week rolling mean, seasonal index |
| Monthly | trigger(t−1 to t−6 months), k*, CCF | 3/6/12-month rolling mean |
| Quarterly | trigger(t−1 to t−4 quarters), k* | 2/4-quarter rolling mean |
| Yearly | trigger(t−1 to t−2 years), k* | Annual rolling mean |

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM with lagged trigger features
- Configuration: Objective = reg:squarederror; Metric = WMAPE, Lag R²
- Key features: trigger(t−k*), CCF strength, lag k*, baseline rolling mean, seasonal index, trigger trend
- When to use: Primary model when CCF > 0.40 and ≥ 3 trigger-demand cycles in history

#### 6.2 Deep Learning (DL)
- Architectures: TFT — lagged triggers as past observed covariates

| Granularity | Lookback | Past Covariates | Output |
|---|---|---|---|
| Daily | 180 days | trigger(t−k* to t) | P10, P50, P90 |
| Weekly | 52 weeks | trigger(t−k* to t) | P10, P50, P90 |
| Monthly | 24 months | trigger(t−k* to t) | P10, P50, P90 |
| Quarterly | 8 quarters | trigger(t−k* to t) | P10, P50, P90 |
| Yearly | 5 years | trigger(t−k* to t) | P10, P50, P90 |

- Training: Loss = quantile loss; Adam lr = 0.001; Dropout = 0.1; Patience = 10

#### 6.3 Statistical / Time Series Models
- Architectures: ARIMAX with lagged exogenous variable

```
d(t) = α + β × trigger(t − k*) + ARIMA(p,d,q) residual
k* = argmax |CCF(k)| for k > 0
```

| Granularity | ARIMA Order |
|---|---|
| Daily | (1,0,1) |
| Weekly | (1,0,1) |
| Monthly | (2,0,1) |
| Quarterly | (1,0,0) |
| Yearly | (1,0,0) |

#### 6.4 Baseline / Fallback Model
- Fallback triggers: Trigger data unavailable; CCF < 0.25; lag k* unstable
- Fallback model: Standard behavior model
- Logging & alerting: Alert if trigger feed delayed; alert if k* shifts > 2 periods

### 7. Ensemble & Weighting

#### 7.1 Ensemble Scheme
- Combination: D̂_t = w_lgbm × LightGBM + w_tft × TFT + w_arimax × ARIMAX
- Weight determination: Error-inverse on rolling 8-period WMAPE

#### 7.2 Dynamic Weight Schedule

| CCF Strength | LightGBM | TFT | ARIMAX |
|---|---|---|---|
| \|CCF\| < 0.40 | 20% | 10% | 70% |
| \|CCF\| 0.40–0.60 | 45% | 25% | 30% |
| \|CCF\| > 0.60 | 55% | 35% | 10% |

### 8. Uncertainty Quantification
- Method: Quantile regression on lagged model residuals
- Output: [P10, P50, P90]
- Use case: Replenishment trigger at P50; safety stock buffer at P75

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Lag drift alert: If k* shifts > 2 periods → alert and re-estimate immediately
- Capping: min(forecast, 2 × baseline rolling max)
- Trigger monitoring: Real-time trigger signal monitoring; alert on trigger spike or collapse
- Manual overrides: Supply chain team lag estimate input; trigger signal quality flag

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | WMAPE Target | Lag R² Target | Lag Estimate Accuracy | Bias Alert |
|---|---|---|---|---|
| Daily | < 22% | > 0.25 | k* within ±2 days | \|Bias\| > 10% |
| Weekly | < 18% | > 0.25 | k* within ±1 week | \|Bias\| > 8% |
| Monthly | < 15% | > 0.20 | k* within ±1 month | \|Bias\| > 7% |
| Quarterly | < 12% | > 0.18 | k* within ±1 quarter | \|Bias\| > 6% |
| Yearly | < 10% | > 0.15 | k* within ±6 months | \|Bias\| > 5% |

#### 10.2 Backtesting Protocol

| Granularity | Train | Test | Min History |
|---|---|---|---|
| Daily | 180 days | 30 days | 365 days |
| Weekly | 52 weeks | 13 weeks | 104 weeks |
| Monthly | 24 months | 6 months | 36 months |
| Quarterly | 8 quarters | 2 quarters | 12 quarters |
| Yearly | All available | 1 year | 5 years |

#### 10.3 Retraining & Data Freshness

| Granularity | Cadence | Latency |
|---|---|---|
| Daily | Daily | T+4 hours |
| Weekly | Weekly | T+1 day |
| Monthly | Monthly | T+2 days |
| Quarterly | Quarterly | T+3 days |
| Yearly | Annually | T+7 days |

### 11. Exception Handling & Overrides
- Automatic exception detection: Trigger feed failure → fallback to standard model; k* shifts > 3 periods → immediate re-estimation; CCF drops below 0.20 → reclassify to Coincident
- Manual override process: Supply chain team lag adjustment; trigger signal correction input
- Override expiration: Per forecast cycle

### 12. Reclassification / Model Selection

| Condition | Target | Holding Period | Transition |
|---|---|---|---|
| Max CCF moves to k = 0 for 4 estimations | Coincident | 4 estimations | Soft blend |
| Max CCF moves to k < 0 for 4 estimations | Leading | 4 estimations | Soft blend |
| \|CCF\| < 0.20 for 3 estimations | Coincident | 3 estimations | Hard switch |
| Lag becomes customer-decision-driven | Deferred | 3 estimations | Soft blend |

### 13. Review Cadence
- Performance monitoring: Per cycle — k* drift monitor and trigger signal quality
- Model review meeting: Monthly lag stability review; quarterly CCF recalibration
- Full model re-evaluation: Annually or on structural change in trigger-demand relationship

---

---
