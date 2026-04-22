## B6 · Step Change

### 1. Definition
Predicts demand for SKUs where a structural break has caused a permanent shift in the demand level, requiring rebaselining before any pattern model is applied; the pre-processing segment that protects other segments from corrupted baselines.

### 2. Detailed Description
- **Applicable scenarios:** Permanent distribution gain/loss, major competitor entry/exit, regulatory change, pricing restructure
- **Boundaries:** Structural break test significant (see Section 0.1E) regardless of CV²/ADI values
- **Key demand characteristics:** Two distinct demand regimes separated by a breakpoint; model trained on pre-break data is invalid
- **Differentiation:** Unlike Trending, change is sudden and permanent — not gradual; unlike Volatile/Erratic, variance within each regime may be low; the break itself creates the misclassification risk

### 3. Business Impact
- **Primary risk (over-forecast):** Using pre-break high baseline after downward step — chronic overstock
- **Primary risk (under-forecast):** Using pre-break low baseline after upward step — chronic stockout
- **Strategic importance:** Very high — forecasting on wrong baseline makes all models fail

### 4. Priority Level
🔴 Tier 1 — Corrupted baseline contaminates all downstream forecasting; must be detected and corrected first.

### 5. Model Strategy Overview

#### 5.1 Break Detection (Hurdle)
- Run structural break test at each retraining cycle (Section 0.1E)
- On break detection: Flag SKU; truncate training data to post-break period only
- Re-run behavior classification on post-break data to assign correct sub-segment

#### 5.2 Post-Break Rebaselining

| Granularity | Post-Break Warm-Up Period | Min Data for Reclassification |
|---|---|---|
| Daily | 30 days post-break | 56 days post-break |
| Weekly | 8 weeks post-break | 8 weeks post-break |
| Monthly | 3 months post-break | 2 months post-break |
| Quarterly | 1 quarter post-break | 1 quarter post-break |
| Yearly | 1 year post-break | 1 year post-break |

- During warm-up: Use Cold Start / New Launch model on post-break data
- After warm-up: Reclassify using post-break data only

#### 5.3 Feature Engineering
- Break point date as feature
- Periods since break as feature
- Pre-break level vs post-break level ratio
- Cause of break flag (if known): distribution, pricing, competitor, regulatory

### 6. Model Families

#### 6.1 ML: LightGBM trained on post-break data only after warm-up
#### 6.2 DL: Not applicable during warm-up; TFT after sufficient post-break history
#### 6.3 Statistical: Piecewise regression on pre/post-break periods for detection; ETS on post-break data for forecasting

**Break Point Detection Formula (Chow Test):**
```
F = [(RSS_total − RSS_1 − RSS_2) / k] / [(RSS_1 + RSS_2) / (n − 2k)]
where RSS = residual sum of squares
      k = number of parameters
      n = total observations
F > F_critical (p < 0.05) → structural break confirmed
```

#### 6.4 Fallback: Post-break rolling mean during warm-up period

### 7. Ensemble
- During warm-up: Analogue-only (similar to Cold Start)
- Post warm-up: Standard ensemble for reclassified behavior segment

### 8. Uncertainty Quantification
- Wider intervals during warm-up: [P5, P50, P95]
- Standard intervals post reclassification: [P10, P50, P90]

### 9. Business Rules
- Non-negativity: max(0, forecast)
- Training data hard cutoff: Only post-break data used after break confirmed
- Manual overrides: Cause of break input by commercial team; expected new level input

### 10. Evaluation

| Granularity | Break Detection Lag Target | Post-Break WMAPE |
|---|---|---|
| Daily | Detect within 14 days | < 30% during warm-up |
| Weekly | Detect within 3 weeks | < 25% during warm-up |
| Monthly | Detect within 2 months | < 20% during warm-up |
| Quarterly | Detect within 1 quarter | < 18% during warm-up |
| Yearly | Detect within 1 year | < 15% during warm-up |

### 11. Exception Handling
- Alert: Break detected → immediate planner notification with pre/post level comparison
- False positive monitoring: Track break detections that revert — tune test sensitivity

### 12. Reclassification
- After warm-up: Automatic reclassification to appropriate behavior segment using post-break data
- No holding period — reclassification is the exit from Step Change

### 13. Review Cadence
- Daily break scan on all SKUs; immediate alert on detection; monthly false-positive review

---

