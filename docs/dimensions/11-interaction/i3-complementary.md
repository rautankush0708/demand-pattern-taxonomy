# Segment Model Template

## Dimension 11 · Complementary

---

### 1. Definition
Predicts demand for SKUs that move in demand synchrony with a correlated partner SKU (r > 0.50), enabling cross-SKU signal sharing to improve forecast accuracy for both SKUs simultaneously through joint modelling.

### 2. Detailed Description
- **Applicable scenarios:** Product bundles, accessories and main products, categories purchased together (coffee + milk), complementary service items, coordinated fashion items
- **Boundaries:**

| Granularity | r Threshold | Granger Causality | Min Co-Active History |
|---|---|---|---|
| Daily | r > +0.50 | Mutual or neither direction dominant | ≥ 90 co-active days |
| Weekly | r > +0.50 | Mutual or neither | ≥ 26 co-active weeks |
| Monthly | r > +0.50 | Mutual or neither | ≥ 12 co-active months |
| Quarterly | r > +0.40 | Mutual or neither | ≥ 4 co-active quarters |
| Yearly | r > +0.35 | Mutual or neither | ≥ 2 co-active years |

- **Key demand characteristics:** Positive demand co-movement; one SKU's demand provides a leading or contemporaneous signal for the other; joint modelling reduces forecast error for both
- **Differentiation from other models:** Unlike Halo, relationship is mutual — neither SKU clearly drives the other; unlike Substitution, correlation is positive (demand rises together); unlike Independent, cross-SKU features significantly improve forecast accuracy

### 3. Business Impact
- **Primary risk (over-forecast):** Over-reading complementary signal — ordering excess when partner SKU spikes temporarily
- **Primary risk (under-forecast):** Ignoring partner signal — missing demand synchrony; service level breach on both SKUs
- **Strategic importance:** High — complementary SKUs should be planned jointly; separate forecasting loses the cross-signal value

### 4. Priority Level
🟠 **Tier 2** — Joint modelling provides measurable forecast improvement; medium complexity.

### 5. Model Strategy Overview

#### 5.1 Cross-SKU Signal Sharing
```
d_A(t) = f(d_A_history, d_B_history, shared_features)
d_B(t) = f(d_B_history, d_A_history, shared_features)

Cross-SKU feature: d_B(t−1), d_B(t−2) as lagged inputs for d_A model
                   d_A(t−1), d_A(t−2) as lagged inputs for d_B model
Cross-SKU feature weight ∝ |r(A,B)|
```

#### 5.2 Analogue / Similarity Logic
- Joint portfolio: Model A and B together; analogues are other Complementary pairs in same category
- k = 3 complementary pairs with r > 0.50 in same category

#### 5.3 Feature Engineering

**Cross-SKU Features:**
```
d_B_lag1(t) = d_B(t−1)   [partner SKU lagged demand]
d_B_lag2(t) = d_B(t−2)
r_AB        = Pearson r between A and B (rolling estimate)
joint_trend = slope of d_A + d_B combined series
```

| Granularity | Cross-SKU Features | Own Features |
|---|---|---|
| Daily | d_B(t−1), d_B(t−2), r_AB, joint_trend | 7/30/90-day own rolling mean, seasonal index, promo flag |
| Weekly | d_B(t−1 week), d_B(t−2 weeks), r_AB | 4/8/13-week own rolling mean, seasonal index |
| Monthly | d_B(t−1 month), d_B(t−2 months), r_AB | 3/6/12-month own rolling mean |
| Quarterly | d_B(t−1 quarter), r_AB | 2/4-quarter own rolling mean |
| Yearly | d_B(t−1 year), r_AB | Annual own rolling mean |

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM — trained with cross-SKU lagged features
- Configuration: Objective = reg:squarederror; Metric = WMAPE; improvement vs Independent model > 5%
- Key features: Partner lagged demand, r_AB, own rolling means, seasonal index
- When to use: Primary model when r > 0.50 confirmed and ≥ 26 weeks co-active history

#### 6.2 Deep Learning (DL)
- Architectures: DeepAR or TFT trained jointly across complementary SKU pairs (shared model)

| Granularity | Joint Lookback | Shared Features | Output |
|---|---|---|---|
| Daily | 180 days (both SKUs) | 12 per SKU | P10, P50, P90 (both) |
| Weekly | 52 weeks (both) | 10 per SKU | P10, P50, P90 |
| Monthly | 24 months (both) | 8 per SKU | P10, P50, P90 |
| Quarterly | 8 quarters (both) | 6 per SKU | P10, P50, P90 |
| Yearly | 5 years (both) | 5 per SKU | P10, P50, P90 |

- When to use: When history > 2 years and r > 0.60 — joint model exploits full cross-SKU signal

#### 6.3 Statistical / Time Series Models
- Architectures: VAR (Vector AutoRegression) for pairs with r > 0.70

**VAR(1) for Complementary Pairs:**
```
[d_A(t)]   [c_A]   [A_11 A_12] [d_A(t-1)]   [ε_A(t)]
[d_B(t)] = [c_B] + [A_21 A_22] [d_B(t-1)] + [ε_B(t)]

A_12 > 0 → B Granger-causes A (useful cross-SKU feature)
A_21 > 0 → A Granger-causes B
Estimate jointly via OLS or MLE
```

- When to use: r > 0.70 AND Granger causality confirmed in at least one direction

#### 6.4 Baseline / Fallback Model
- Fallback: Independent model (ignore cross-SKU features)
- Alert if WMAPE improvement from joint model drops below 3% — cross-SKU signal weakening

### 7. Ensemble & Weighting

#### 7.2 Dynamic Weight Schedule

| r Strength | LightGBM | TFT/DeepAR | VAR |
|---|---|---|---|
| 0.50 ≤ r < 0.65 | 55% | 30% | 15% |
| 0.65 ≤ r < 0.80 | 45% | 35% | 20% |
| r ≥ 0.80 | 35% | 35% | 30% |

### 8. Uncertainty Quantification
- Method: Conformal prediction on joint model residuals
- Output: [P10, P50, P90] for each SKU in the complementary pair
- Use case: Joint safety stock planning; coordinated replenishment timing

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- WMAPE improvement check: If joint model WMAPE < independent WMAPE − 5% → use joint; else revert to independent
- Joint planning rule: Complementary pairs should be reviewed together in S&OP; trigger joint reforecast if either SKU has significant demand change
- Manual overrides: Category manager signal; promotional plan applying to one but not both

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | Joint WMAPE | WMAPE vs Independent | r Stability | Portfolio Consistency | Bias Alert |
|---|---|---|---|---|---|
| Daily | Per behavior std − 5% | > 5% improvement | CV(r) < 0.20 | < 5% | \|Bias\| > 8% |
| Weekly | Per behavior std − 5% | > 5% improvement | CV(r) < 0.20 | < 5% | \|Bias\| > 7% |
| Monthly | Per behavior std − 5% | > 5% improvement | CV(r) < 0.20 | < 5% | \|Bias\| > 6% |
| Quarterly | Per behavior std − 5% | > 5% improvement | CV(r) < 0.20 | < 5% | \|Bias\| > 5% |
| Yearly | Per behavior std − 4% | > 4% improvement | CV(r) < 0.20 | < 5% | \|Bias\| > 4% |

#### 10.2 Backtesting Protocol

| Granularity | Train | Test |
|---|---|---|
| Daily | 180 days | 30 days |
| Weekly | 52 weeks | 13 weeks |
| Monthly | 24 months | 6 months |
| Quarterly | 8 quarters | 2 quarters |
| Yearly | All available | 1 year |

#### 10.3 Retraining

| Granularity | Cadence | Latency |
|---|---|---|
| Daily | Daily | T+4 hours |
| Weekly | Weekly | T+1 day |
| Monthly | Monthly | T+2 days |
| Quarterly | Quarterly | T+3 days |
| Yearly | Annually | T+7 days |

### 11. Exception Handling & Overrides
- Auto-detect: r drops below 0.30 for 4 estimations → reclassify to Independent; Granger causality becomes one-directional (p < 0.05 in one direction only) → reclassify to Halo; WMAPE improvement drops below 3% → revert to independent model
- Manual override: Category restructuring; one SKU discontinued; promotional decoupling
- Override expiration: Per monthly r check

### 12. Reclassification / Model Selection

| Condition | Target | Holding Period | Transition |
|---|---|---|---|
| r drops below 0.25 for 4 estimations | Independent | 4 estimations | Soft blend |
| r turns negative (< −0.20) | Substitution or Cannibalistic (re-test) | 3 estimations | Re-test |
| Granger one-directional at p < 0.05 | Halo (causal direction confirmed) | 4 estimations | Re-classify |

### 13. Review Cadence
- Monthly r stability monitor; quarterly VAR recalibration; annual portfolio interaction map refresh

---

---
