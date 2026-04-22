## B8 · Slow Mover

### 1. Definition
Predicts demand for SKUs with regular demand frequency and low variance (same CV²-ADI quadrant as Stable) but with absolute volume below the 5th portfolio percentile, where low volume creates amplified percentage error and specialist treatment improves inventory efficiency.

### 2. Detailed Description
- **Applicable scenarios:** Long-tail SKUs, niche variants, regional specialties, low-volume B2B lines
- **Boundaries:**

| Granularity | ADI Threshold | CV² Threshold | Volume |
|---|---|---|---|
| Daily | ADI < 1.10 | CV² < 0.49 | < 5th percentile of portfolio daily means |
| Weekly | ADI < 1.32 | CV² < 0.49 | < 5th percentile of portfolio weekly means |
| Monthly | ADI < 1.25 | CV² < 0.49 | < 5th percentile of portfolio monthly means |
| Quarterly | ADI < 1.20 | CV² < 0.49 | < 5th percentile of portfolio quarterly means |
| Yearly | ADI < 1.10 | CV² < 0.49 | < 5th percentile of portfolio yearly means |

- **Key demand characteristics:** Regular but very low volume, stable pattern, high MAPE due to low absolute values
- **Differentiation:** Unlike Stable, volume is very low — MAPE is unreliable; unlike Intermittent, frequency is high; like Stable in behavior but different in volume tier

### 3. Business Impact
- **Primary risk (over-forecast):** Small absolute overstock but high relative cost — write-off on low-value lines
- **Primary risk (under-forecast):** Stockout on niche lines — long tail customers are disproportionately loyal
- **Strategic importance:** Low-medium — individually small but collectively significant (long tail effect)

### 4. Priority Level
🟡 Tier 3 — Low individual impact but high portfolio count — automation is key.

### 5. Model Strategy Overview

#### 5.1 Hurdle
- Threshold: P(demand > 0) > 0.80 — slow movers demand regularly but in small quantities
- Regressor: Simple statistical models preferred — ML overfits on low-volume data

#### 5.2 Analogue Logic
- k = 5 (similar low-volume SKUs from same subcategory)
- Pool analogues for cross-learning — critical for sparse data

#### 5.3 Feature Engineering

| Granularity | Features | Notes |
|---|---|---|
| Daily | 7, 30, 90-day rolling mean, holiday flag, day of week | Minimal features — prevent overfitting |
| Weekly | 4, 8, 13-week rolling mean, holiday flag | Simple feature set |
| Monthly | 2, 3, 6-month rolling mean, seasonal flag | Seasonal index important |
| Quarterly | 1, 2, 4-quarter rolling mean | Minimal |
| Yearly | 1, 2-year rolling mean | Long-cycle only |

### 6. Model Families

#### 6.1 ML: LightGBM (simple, regularised heavily to prevent overfit)
- Objective: reg:absoluteerror (MAE preferred over RMSE for low volume)
- Max depth: 3; num_leaves: 15; min_data_in_leaf: 5 (prevent overfit)
- When to use: When portfolio is large enough for cross-SKU learning

#### 6.2 DL: Not recommended — insufficient signal for deep learning

#### 6.3 Statistical: ETS(A,N,A) or Theta method

| Granularity | Model | Reason |
|---|---|---|
| Daily | Theta with period = 7 | Handles low volume well |
| Weekly | ETS(A,N,A) period = 52 | Captures annual seasonality |
| Monthly | Theta or ETS(A,N,A) period = 12 | Reliable on low volume |
| Quarterly | ETS(A,N,N) | No seasonality at quarterly |
| Yearly | Simple moving average (3-year) | Minimal complexity |

#### 6.4 Fallback: 3-period moving average; alert if fallback > 20%

### 7. Ensemble

| History | LightGBM | ETS / Theta |
|---|---|---|
| Up to 1 year equiv. | 30% | 70% |
| > 1 year equiv. | 50% | 50% |

### 8. Uncertainty Quantification
- Method: Bootstrap on historical residuals (simple, works on small samples)
- Output: [P10, P50, P90]
- Use case: Min/max stock policy — often binary (stock or not stock decision)

### 9. Business Rules
- Non-negativity: max(0, forecast)
- Minimum forecast: Consider rounding to nearest whole unit
- Stockout cost vs holding cost assessment: For very low volume, safety stock = 1 unit may suffice
- Manual overrides: Range rationalisation decisions; customer-specific demand alerts

### 10. Evaluation

| Granularity | Primary Metric | WMAPE Note | Bias Alert |
|---|---|---|---|
| Daily | MAE (not WMAPE — too noisy) | WMAPE unreliable at low volume | \|Bias\| > 20% |
| Weekly | MAE | WMAPE unreliable | \|Bias\| > 20% |
| Monthly | MAE + MASE | MASE reliable here | \|Bias\| > 15% |
| Quarterly | MAE + MASE | MASE reliable | \|Bias\| > 12% |
| Yearly | MAE + MASE | MASE reliable | \|Bias\| > 10% |

- **Note:** MASE preferred over MAPE/WMAPE for slow movers — MAPE inflates on near-zero actuals

### 11. Exception Handling
- Alert: Volume rises above 5th percentile for 8 periods → reclassify to Stable

### 12. Reclassification

| Condition | Target | Holding Period |
|---|---|---|
| Volume rises above 5th percentile for 8 periods | Stable | 8 periods |
| ADI rises above threshold for 8 periods | Intermittent | 8 periods |
| CV² rises above 0.49 for 8 periods | Erratic | 8 periods |

### 13. Review Cadence
- Monthly automated — low individual priority; quarterly portfolio-level slow mover review; annual range rationalisation input

---

*End of Dimension 2 · Behavior Pattern*
*8 Segments Complete · B1 through B8*
