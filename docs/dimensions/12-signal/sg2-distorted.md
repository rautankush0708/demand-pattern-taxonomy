## SG2 · Distorted

### 1. Definition
Predicts demand for SKUs where observed demand is systematically inflated or deflated by external factors unrelated to true consumption (DI > 0.15 in > 20% of periods), requiring distortion identification, correction, and unconstrained demand reconstruction before modelling.

### 5. Model Strategy

#### 5.1 Distortion Correction Pipeline
```
STEP 1: Identify distortion source
  Sources: Supply stockouts, returns inflation, reporting errors, order cancellations, double-counting

STEP 2: Estimate distortion magnitude
  d_true(t) = d_observed(t) / distortion_factor(t)
  distortion_factor(t) = 1 + (distortion_magnitude × distortion_indicator(t))

STEP 3: Replace distorted periods
  Use corrected demand d_true(t) for all model training and feature computation

STEP 4: Apply standard behavior model to corrected series
```

| Distortion Type | Correction Method |
|---|---|
| Supply stockout | Fill rate adjustment |
| Returns inflation | Subtract gross returns from gross demand |
| Reporting error | Replace with interpolated adjacent periods |
| Order cancellation | Adjust with confirmed net demand |
| Double counting | Identify and remove duplicate transactions |

### 6. Model Families
- Post-correction: Standard behavior model per segment
- Pre-correction: Distortion detection model (anomaly detection — Isolation Forest or CUSUM)

### Evaluation

| Granularity | Distortion Detection Rate | Post-Correction WMAPE | Correction Accuracy | Bias Alert |
|---|---|---|---|---|
| Daily | > 85% | Per behavior standard | DI < 0.10 post-correction | |Bias| > 10% |
| Weekly | > 85% | Per behavior standard | DI < 0.10 | |Bias| > 8% |
| Monthly | > 85% | Per behavior standard | DI < 0.10 | |Bias| > 7% |
| Quarterly | > 80% | Per behavior standard | DI < 0.10 | |Bias| > 6% |
| Yearly | > 80% | Per behavior standard | DI < 0.10 | |Bias| > 5% |

---

