# Segment Model Template

## Dimension 9 · Leading

---

### 1. Definition
Predicts demand for SKUs where demand moves systematically ahead of an identifiable external trigger signal, enabling anticipatory forecasting by using leading indicators to predict demand before it materialises.

### 2. Detailed Description
- **Applicable scenarios:** Housing construction materials (leads permits), baby products (leads birth rate), school supplies (leads enrolment), B2B capital goods (leads equipment orders)
- **Boundaries:**

| Granularity | Detection Condition | Lead Time Range | Min History |
|---|---|---|---|
| Daily | Max CCF at k < 0; \|CCF\| > 2/√n | 3–30 days ahead | ≥ 180 days |
| Weekly | Max CCF at k < 0; \|CCF\| > 2/√n | 1–13 weeks ahead | ≥ 52 weeks |
| Monthly | Max CCF at k < 0; \|CCF\| > 2/√n | 1–6 months ahead | ≥ 24 months |
| Quarterly | Max CCF at k < 0; \|CCF\| > 2/√n | 1–4 quarters ahead | ≥ 8 quarters |
| Yearly | Max CCF at k < 0; \|CCF\| > 2/√n | 1–2 years ahead | ≥ 5 years |

- **Key demand characteristics:** Demand precedes observable external trigger; identifies future demand before conventional signals appear; requires leading indicator data pipeline
- **Differentiation from other models:** Unlike Lagging, demand moves before the trigger; unlike Coincident, there is a measurable negative lag; unlike standard models, the trigger signal is a future input not a past input

### 3. Business Impact
- **Primary risk (over-forecast):** Leading indicator false positive — demand anticipated but does not materialise
- **Primary risk (under-forecast):** Ignoring lead time — reactive rather than anticipatory; missing procurement window
- **Strategic importance:** High — leading indicators extend effective forecast horizon; competitive advantage in early procurement and capacity planning

### 4. Priority Level
🟠 **Tier 2** — High value when leading indicator data is available; requires external data pipeline investment.

### 5. Model Strategy Overview

#### 5.1 Zero-Demand Handling (Hurdle)
- Active event threshold: P(demand > 0) > 0.65
- Classifier type: Logistic Regression with leading indicator proximity features
- Regressor type: LightGBM with leading indicator at optimal lag k*
- Fallback: Standard behavior model without leading indicator

#### 5.2 Analogue / Similarity Logic
- Number of analogues: k = 3 (SKUs with similar CCF structure in same category)
- Similarity criteria: |CCF| strength ±0.10, lead time k* ±2 periods, category
- Temporal decay: weight = exp(−age / half-life)

| Granularity | Half-Life |
|---|---|
| Daily | 90 days |
| Weekly | 13 weeks |
| Monthly | 6 months |
| Quarterly | 3 quarters |
| Yearly | 2 years |

- Aggregation: Weighted mean of analogue CCF profiles

#### 5.3 Feature Engineering

**Leading Indicator Feature Construction:**
```
lead_indicator_k*(t) = trigger_signal(t + k*)   [future value at optimal lead]
CCF_strength         = |CCF(k*)|
lead_time_stability  = CV(k* across rolling windows)
lead_indicator_trend = slope of trigger signal over short window
```

| Granularity | Leading Indicator Features | Baseline Features |
|---|---|---|
| Daily | trigger(t+3 to t+30), k*, CCF strength, lead drift flag | 7/30/90-day rolling mean, seasonal index, holiday flag |
| Weekly | trigger(t+1 to t+13 weeks), k*, CCF strength | 4/8/13-week rolling mean, seasonal index |
| Monthly | trigger(t+1 to t+6 months), k*, CCF strength | 3/6/12-month rolling mean, seasonal index |
| Quarterly | trigger(t+1 to t+4 quarters), k* | 2/4-quarter rolling mean |
| Yearly | trigger(t+1 to t+2 years), k* | Annual rolling mean |

- External signals: Consumer confidence index, PMI, building permits, jobless claims, mobility index

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM with leading indicator features
- Configuration: Objective = reg:squarederror; Metric = WMAPE, Lead R²
- Key features: trigger(t+k*), CCF strength, lead time k*, baseline rolling mean, seasonal index, trend of trigger signal
- When to use: Primary model — when CCF > 0.40 and ≥ 3 historical trigger cycles available

#### 6.2 Deep Learning (DL)
- Architectures: TFT — leading indicators fed as **known future covariates** (unique advantage of TFT architecture)

| Granularity | Lookback | Future Covariate Horizon | Features | Output |
|---|---|---|---|---|
| Daily | 180 days | k* days ahead | 15 | P10, P50, P90 |
| Weekly | 52 weeks | k* weeks ahead | 12 | P10, P50, P90 |
| Monthly | 24 months | k* months ahead | 10 | P10, P50, P90 |
| Quarterly | 8 quarters | k* quarters ahead | 8 | P10, P50, P90 |
| Yearly | 5 years | k* years ahead | 6 | P10, P50, P90 |

- Training: Loss = quantile loss; Adam lr = 0.001; Dropout = 0.1; Patience = 10
- When to use: When leading indicator feed is available as forward-looking input — TFT leverages this natively

#### 6.3 Statistical / Time Series Models
- Architectures: ARIMAX with leading indicator at lag k* as exogenous variable

```
d(t) = α + β × trigger(t + k*) + Σγ × controls(t) + ARIMA(p,d,q) residual
β = leading indicator coefficient
k* = optimal lead time (estimated from CCF)
```

| Granularity | ARIMA Order | CCF Lag |
|---|---|---|
| Daily | (1,0,1) | k* days |
| Weekly | (1,0,1) | k* weeks |
| Monthly | (2,0,1) | k* months |
| Quarterly | (1,0,0) | k* quarters |
| Yearly | (1,0,0) | k* years |

- When to use: Interpretability requirement; β coefficient reporting for procurement planning

#### 6.4 Baseline / Fallback Model
- Fallback triggers: Leading indicator data feed unavailable; CCF drops below 0.25
- Fallback model: Standard behavior model (ignore timing dimension)
- Logging & alerting: Alert if leading indicator feed delayed > 1 period; alert if k* shifts > 2 periods between estimations

### 7. Ensemble & Weighting

#### 7.1 Ensemble Scheme
- Combination: D̂_t = w_lgbm × LightGBM + w_tft × TFT + w_arimax × ARIMAX
- Weight determination: Error-inverse weighting on rolling 8-period WMAPE

#### 7.2 Dynamic Weight Schedule

| CCF Strength | LightGBM | TFT | ARIMAX |
|---|---|---|---|
| \|CCF\| < 0.40 (weak) | 20% | 10% | 70% |
| \|CCF\| 0.40–0.60 (moderate) | 45% | 25% | 30% |
| \|CCF\| > 0.60 (strong) | 55% | 35% | 10% |

### 8. Uncertainty Quantification
- Method: Quantile regression on causal model residuals; wider intervals when CCF is weak
- Output: [P10, P50, P90]
- Use case: Procurement commitment at P75 when lead indicator strong; P50 when moderate; P25 when weak

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Lead time drift alert: If k* shifts > 2 periods between estimations → alert and re-estimate
- Capping: min(forecast, 2 × baseline rolling max)
- Data feed rule: If leading indicator unavailable → revert to standard behavior model; flag in dashboard
- Manual overrides: Macro economist input on leading indicator forecast; procurement team lead time adjustment

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | WMAPE Target | Lead R² Target | CCF Stability | Bias Alert |
|---|---|---|---|---|
| Daily | < 22% | > 0.25 | CV(k*) < 0.30 | \|Bias\| > 10% |
| Weekly | < 18% | > 0.25 | CV(k*) < 0.30 | \|Bias\| > 8% |
| Monthly | < 15% | > 0.20 | CV(k*) < 0.30 | \|Bias\| > 7% |
| Quarterly | < 12% | > 0.18 | CV(k*) < 0.30 | \|Bias\| > 6% |
| Yearly | < 10% | > 0.15 | CV(k*) < 0.30 | \|Bias\| > 5% |

#### 10.2 Backtesting Protocol

| Granularity | Method | Train | Test | Min History |
|---|---|---|---|---|
| Daily | Rolling window | 180 days | 30 days | 365 days |
| Weekly | Rolling window | 52 weeks | 13 weeks | 104 weeks |
| Monthly | Rolling window | 24 months | 6 months | 36 months |
| Quarterly | Rolling window | 8 quarters | 2 quarters | 12 quarters |
| Yearly | Expanding window | All available | 1 year | 5 years |

#### 10.3 Retraining & Data Freshness

| Granularity | Cadence | Trigger | Latency |
|---|---|---|---|
| Daily | Daily | Leading indicator feed update | T+4 hours |
| Weekly | Weekly | Weekly trigger data update | T+1 day |
| Monthly | Monthly | Monthly indicator release | T+2 days |
| Quarterly | Quarterly | Quarterly data release | T+3 days |
| Yearly | Annually | Annual data update | T+7 days |

### 11. Exception Handling & Overrides
- Automatic exception detection: Leading indicator feed failure → immediate fallback to standard model; k* shifts > 3 periods → re-estimate CCF; CCF drops below 0.20 → reclassify to Coincident
- Manual override process: Macroeconomist input on leading indicator outlook; procurement team lead time estimate input; dashboard approval with reason code
- Override expiration: Per forecast cycle

### 12. Reclassification / Model Selection

| Condition | Target Segment | Holding Period | Transition |
|---|---|---|---|
| Max CCF moves to k = 0 for 4 consecutive estimations | Coincident | 4 estimations | Soft blend |
| Max CCF moves to k > 0 for 4 estimations | Lagging | 4 estimations | Soft blend |
| \|CCF\| drops below 0.20 for 3 estimations | Coincident (no timing signal) | 3 estimations | Hard switch |
| dev_timing shifts to > +threshold for 3 estimations | Deferred | 3 estimations | Soft blend |

### 13. Review Cadence
- Performance monitoring: Per cycle — automated dashboard with k* drift monitor
- Model review meeting: Monthly CCF stability review; quarterly lead time recalibration
- Full model re-evaluation: Annually or on structural change in leading indicator relationship

---

---
