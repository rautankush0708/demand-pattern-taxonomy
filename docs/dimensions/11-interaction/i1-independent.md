# Segment Model Template

## Dimension 11 · Independent

---

### 1. Definition
Predicts demand for SKUs with no statistically significant cross-SKU demand correlation (|r| < 0.20 with all portfolio SKUs), where standalone single-SKU models are optimal and portfolio-level effects can be safely ignored.

### 2. Detailed Description
- **Applicable scenarios:** Unique product categories, highly differentiated SKUs with no substitutes, SKUs serving distinct non-overlapping customer segments, diverse portfolio with no natural groupings
- **Boundaries:**

| Granularity | Condition | Min Portfolio SKUs Tested |
|---|---|---|
| Daily | \|r(A,B)\| < 0.20 for all B in portfolio | All active portfolio SKUs |
| Weekly | \|r(A,B)\| < 0.20 for all B | All active portfolio SKUs |
| Monthly | \|r(A,B)\| < 0.20 for all B | All active portfolio SKUs |
| Quarterly | \|r(A,B)\| < 0.20 for all B | All active portfolio SKUs |
| Yearly | \|r(A,B)\| < 0.20 for all B | All active portfolio SKUs |

- **Key demand characteristics:** Demand moves independently of all other SKUs; standard single-SKU models are sufficient; no portfolio-level adjustment needed
- **Differentiation from other models:** Unlike all other Interaction segments, no cross-SKU signal provides forecast value; adding portfolio features would introduce noise not signal

### 3. Business Impact
- **Primary risk (over-forecast):** Standard model risk only — no interaction amplification
- **Primary risk (under-forecast):** Standard model risk only
- **Strategic importance:** Medium — Independent classification confirms that standard models are appropriate; removes complexity justification

### 4. Priority Level
🟠 **Tier 2** — Standard model applied; primary value is confirming no cross-SKU modelling needed.

### 5. Model Strategy Overview

#### 5.1 Zero-Demand Handling (Hurdle)
- Active event threshold: Per Behavior segment standard
- Classifier: Per Behavior segment standard — no cross-SKU features
- Regressor: Per Behavior segment standard — standalone model

#### 5.2 Analogue / Similarity Logic
- Per Behavior segment standard — no cross-SKU analogues based on interaction

#### 5.3 Feature Engineering
- Standard features per Behavior × Lifecycle × Magnitude segment
- **Explicitly excluded:** Cross-SKU demand features, OOS flags of other SKUs, portfolio-level variables
- Interaction monitor feature: Cross-SKU r computed monthly as metadata — alert if any r exceeds 0.20

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Standard LightGBM per Behavior segment — no cross-SKU features
- When to use: Always — standard model

#### 6.2 Deep Learning (DL)
- Standard TFT / N-BEATS per Behavior segment — no shared model across SKUs

#### 6.3 Statistical / Time Series Models
- Standard ETS / ARIMA per Behavior segment

#### 6.4 Baseline / Fallback Model
- Standard per Behavior segment
- Logging & alerting: Monthly cross-SKU correlation check; alert if |r| rises above 0.20 with any SKU

### 7. Ensemble & Weighting
- Standard ensemble per Behavior segment — no interaction weighting
- Scenario planning: Maintain small (5%) weight on substitution scenario as contingency

### 8. Uncertainty Quantification
- Standard [P10, P50, P90] per Behavior segment
- No interaction-specific interval widening

### 9. Business Rules & Post-Processing
- Standard per Behavior segment
- No portfolio conservation adjustment needed — forecasts are additive
- Monthly interaction check: Re-run cross-SKU r test monthly; reclassify if threshold crossed

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | WMAPE Target | Bias Alert | Interaction Monitor | Portfolio Consistency |
|---|---|---|---|---|
| Daily | Per Behavior standard | Per Behavior standard | \|r\| < 0.20 all pairs | < 5% |
| Weekly | Per Behavior standard | Per Behavior standard | \|r\| < 0.20 | < 5% |
| Monthly | Per Behavior standard | Per Behavior standard | \|r\| < 0.20 | < 5% |
| Quarterly | Per Behavior standard | Per Behavior standard | \|r\| < 0.20 | < 5% |
| Yearly | Per Behavior standard | Per Behavior standard | \|r\| < 0.20 | < 5% |

#### 10.2 Backtesting Protocol
- Standard per Behavior segment
- Additional: Validate no cross-SKU feature improves WMAPE by > 5% (confirms Independence)

#### 10.3 Retraining
- Standard cadence per Behavior segment
- Additional trigger: Monthly interaction check; reclassify immediately if threshold crossed

### 11. Exception Handling & Overrides
- Auto-detect: |r| rises above 0.20 with any portfolio SKU for 3 consecutive estimations → run full interaction test; OOS event on related SKU causes demand spike on this SKU → investigate Substitution
- Manual override: Category manager interaction flag; portfolio restructuring input
- Override expiration: Per monthly interaction check

### 12. Reclassification / Model Selection

| Condition | Target | Holding Period | Transition |
|---|---|---|---|
| r > +0.20 with another SKU for 3 estimations | Run Granger test → Complementary or Halo | 3 estimations | Immediate test |
| r < −0.20 with another SKU for 3 estimations | Run sub/cannibalism test → Substitution or Cannibalistic | 3 estimations | Immediate test |
| sub_rate > 0.20 detected in OOS event | Substitution | 3 OOS events | Soft blend |

### 13. Review Cadence
- Monthly cross-SKU correlation monitor; quarterly portfolio interaction map refresh; annual full re-evaluation

---

---
