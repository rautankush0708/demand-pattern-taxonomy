## M3 · Low Volume
### 1. Definition
Predicts demand for SKUs in the 5th–25th percentile of portfolio demand volume, where low absolute quantities make percentage-based metrics unreliable and specialist low-volume methods are required to avoid overfitting and metric distortion.

### 2. Detailed Description
- **Applicable scenarios:** Long-tail variants, niche product lines, regional specialties, low-velocity B2B lines, specialty retail
- **Boundaries:**

| Granularity | Percentile | Absolute Guardrail | Rolling Window |
|---|---|---|---|
| Daily | 5th–25th percentile | 1–10 units/day | 90-day rolling mean |
| Weekly | 5th–25th percentile | 5–50 units/week | 26-week rolling mean |
| Monthly | 5th–25th percentile | 20–200 units/month | 6-month rolling mean |
| Quarterly | 5th–25th percentile | 60–600 units/quarter | 4-quarter rolling mean |
| Yearly | 5th–25th percentile | 240–2,400 units/year | 3-year rolling mean |

- **Key demand characteristics:** Low absolute volume; MAPE inflated by small actuals; overfitting risk is high with complex models; inventory policy often binary (stock vs no stock)
- **Differentiation from other models:** Unlike Medium Volume, MAPE/WMAPE unreliable — use MAE and MASE; unlike Ultra Low, demand is more than single-unit; simple models outperform complex ones

### 3. Business Impact
- **Primary risk (over-forecast):** Holding cost on low-value items; portfolio-level waste from many small overstock positions
- **Primary risk (under-forecast):** Long tail customers are disproportionately loyal; stockout damages relationship
- **Strategic importance:** Medium — individually low impact; collectively significant (long tail effect)

### 4. Priority Level
🟡 Tier 3 — Low individual priority; automation at scale is the key business requirement.

### 5. Model Strategy Overview

#### 5.1 Zero-Demand Handling (Hurdle)
- Active event threshold: P(demand > 0) > 0.70
- Classifier: Logistic Regression (simple — prevent overfitting on low data)
- Regressor: ETS or Theta — statistical methods outperform ML on low volume
- Fallback: Rolling mean (short window)

#### 5.2 Analogue / Similarity Logic
- Number of analogues: k = 5 (similar low-volume SKUs from same subcategory)
- Cross-SKU pooling: Group Low Volume SKUs into demand pools for shared model training
- Similarity: Subcategory, CV², ADI range, price tier

#### 5.3 Feature Engineering

| Granularity | Rolling Windows | Features | Notes |
|---|---|---|---|
| Daily | 7, 30, 90-day mean, std | Day of week, holiday flag, seasonal index | Minimal — prevent overfit |
| Weekly | 4, 8, 13-week mean, std | Week of year, holiday, seasonal index | Simple feature set |
| Monthly | 2, 3, 6, 12-month mean, std | Month of year, seasonal index, promo flag | Standard set |
| Quarterly | 1, 2, 4-quarter mean, std | Quarter of year, seasonal index | Minimal |
| Yearly | 1, 2, 3-year mean | Long-cycle index | Trend only |

- Feature count: 10–15 features maximum — regularisation critical

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM (heavily regularised)
- Configuration: Objective = reg:absoluteerror (MAE preferred); max_depth = 3; num_leaves = 15; min_data_in_leaf = 10; lambda_l1 = 1.0
- When to use: When portfolio large enough for cross-SKU learning (> 100 Low Volume SKUs)
- Cross-SKU learning: Train single LightGBM model across all Low Volume SKUs — SKU ID as feature

#### 6.2 Deep Learning (DL)
- Architectures: Not recommended — data too sparse for individual DL; cross-SKU DeepAR acceptable if > 500 Low Volume SKUs in portfolio
- When to use: Only if very large portfolio enables meaningful cross-learning

#### 6.3 Statistical / Time Series Models
- Architectures: Theta method (primary); ETS(A,N,A) or ETS(A,N,N)

| Granularity | Primary Model | Reason |
|---|---|---|
| Daily | Theta with period = 7 | Robust on low volume; handles noise better than SARIMA |
| Weekly | Theta or ETS(A,N,A) period = 52 | Simple seasonal capture |
| Monthly | Theta or ETS(A,N,A) period = 12 | Reliable on low volume monthly data |
| Quarterly | ETS(A,N,N) or 4-quarter moving average | Low complexity |
| Yearly | 3-year moving average | Minimal model |

**Theta Method Formula:**
```
Decompose series into two theta lines:
θ_0 line (θ=0): long-term trend = linear regression on d_t
θ_2 line (θ=2): short-term = 2 × d_t − θ_0_t

Forecast = α × θ_2_forecast + (1−α) × θ_0_forecast
α optimised on validation MAE
```

- When to use: Primary model for Low Volume — Theta consistently outperforms complex models on low-volume data

#### 6.4 Baseline / Fallback Model
- Fallback: 3-period moving average
- Logging & alerting: Alert if fallback rate > 25%

### 7. Ensemble & Weighting

#### 7.2 Dynamic Weight Schedule

| History Available | LightGBM (cross-SKU) | Theta | ETS |
|---|---|---|---|
| < 6 months | 0% | 60% | 40% |
| 6 months–1 year | 20% | 50% | 30% |
| 1–2 years | 30% | 45% | 25% |
| > 2 years | 40% | 40% | 20% |

### 8. Uncertainty Quantification
- Method: Bootstrap on historical residuals (simple; works on small samples)
- Output: [P10, P50, P90]
- Use case: Min/max stock policy — often binary (stock or not stock); P90 used for max stock level

**Min/Max Policy Formula:**
```
Min (reorder point) = Mean demand × Lead time + Safety stock
Max (order up to)   = Min + Order quantity
Safety stock        = z × σ_demand × √Lead_time   [if σ reliable]
                    = fixed buffer (1–2 units)      [if Ultra Low border]
```

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Rounding: Round to nearest whole unit — fractional units meaningless at low volume
- Minimum forecast consideration: Evaluate whether to stock at all (range rationalisation trigger)
- Manual overrides: Range review input; customer special order flag

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | Primary Metric | Secondary | Bias Alert |
|---|---|---|---|
| Daily | MAE (units) | Fill Rate | \|Bias\| > 20% |
| Weekly | MAE (units) | Fill Rate | \|Bias\| > 18% |
| Monthly | MASE | MAE | \|Bias\| > 15% |
| Quarterly | MASE | MAE | \|Bias\| > 12% |
| Yearly | MASE | MAE | \|Bias\| > 10% |

- **Note:** MAPE and WMAPE explicitly avoided for Low Volume — small denominators create misleading metrics

#### 10.2 Backtesting Protocol

| Granularity | Train | Test | Min History |
|---|---|---|---|
| Daily | 90 days | 30 days | 180 days |
| Weekly | 26 weeks | 13 weeks | 52 weeks |
| Monthly | 12 months | 6 months | 18 months |
| Quarterly | 4 quarters | 2 quarters | 6 quarters |
| Yearly | All available | 1 year | 2 years |

#### 10.3 Retraining

| Granularity | Cadence | Latency |
|---|---|---|
| Daily | Weekly (not daily — low priority) | T+4 hours |
| Weekly | Weekly | T+1 day |
| Monthly | Monthly | T+2 days |
| Quarterly | Quarterly | T+3 days |
| Yearly | Annually | T+7 days |

### 11. Exception Handling & Overrides
- Auto-detect: Volume rises above 25th percentile for 4 months → reclassify to Medium Volume
- Manual override: Range rationalisation trigger; special customer order flag
- Override expiration: Single cycle

### 12. Reclassification
- To Medium Volume: Percentile rises above 25th for 6 consecutive months
- To Ultra Low: Percentile drops below 5th for 6 consecutive months
- Soft blend over 4-period transition

### 13. Review Cadence
- Monthly automated portfolio-level dashboard; quarterly range rationalisation review; annual full re-evaluation

---
