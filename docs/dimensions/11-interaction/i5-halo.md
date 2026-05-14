# Segment Model Template

## Dimension 11 · Halo

---

### 1. Definition
Predicts demand for SKUs where a hero SKU's demand performance systematically lifts demand for this follower SKU, with Granger causality confirmed from hero to follower, enabling hero-based leading forecast for the follower.

### 2. Detailed Description
- **Applicable scenarios:** Hero brand lifting private label, flagship product driving accessories, category leader lifting adjacent products, brand equity transfer across range
- **Boundaries:**

| Granularity | r Threshold | Granger Causality | Min Co-Active History |
|---|---|---|---|
| Daily | r > +0.40 | Hero → follower p < 0.05 (not reverse) | ≥ 90 co-active days |
| Weekly | r > +0.40 | Hero → follower p < 0.05 | ≥ 26 co-active weeks |
| Monthly | r > +0.40 | Hero → follower p < 0.05 | ≥ 12 co-active months |
| Quarterly | r > +0.35 | Hero → follower p < 0.05 | ≥ 4 co-active quarters |
| Yearly | r > +0.30 | Hero → follower p < 0.05 | ≥ 2 co-active years |

- **Key demand characteristics:** Hero SKU demand is a leading indicator for follower SKU; causal direction is one-way (hero drives follower); follower benefits from hero's promotional or volume uplift
- **Differentiation from other models:** Unlike Complementary, causal direction is clear (hero → follower not mutual); unlike Substitution, correlation is positive; unlike Cannibalistic, growth of hero lifts not depresses follower

### 3. Business Impact
- **Primary risk (over-forecast):** Over-reading hero signal — excess follower stock when hero spikes temporarily
- **Primary risk (under-forecast):** Not following hero signal — follower stockout when hero drives category growth
- **Strategic importance:** High — hero promotions should be planned jointly with follower; hero stockout also damages follower demand

### 4. Priority Level
🔴 **Tier 1** — Hero-follower dynamics are commercially significant; joint planning prevents follower stockout during hero promotional periods.

### 5. Model Strategy Overview

#### 5.1 Hero-Follower Causal Model
```
d_follower(t) = d_follower_baseline(t) × (1 + halo_factor × d_hero(t) / d_hero_mean)
halo_factor estimated from:
  d_follower(t) = α + β_halo × d_hero(t) + β_lag × d_hero(t−1) + controls + ε
  β_halo = halo elasticity (target: > 0; p < 0.05)

Halo elasticity: β_halo / mean(d_follower) = halo response per unit of hero demand

Granger causality verification (each quarter):
  H0: d_hero does NOT Granger-cause d_follower
  Reject H0 at p < 0.05 → confirmed hero → follower
  Verify reverse does NOT hold (follower does not Granger-cause hero)
```

#### 5.2 Analogue / Similarity Logic
- k = 3 (similar hero-follower pairs in same category with comparable halo elasticity)
- Similarity: β_halo ±0.05, r ±0.10, category

#### 5.3 Feature Engineering

**Hero-Follower Features:**
```
d_hero(t)      = hero SKU demand at time t
d_hero(t−1)    = hero lagged demand
hero_uplift(t) = d_hero(t) / d_hero_rolling_mean − 1   [hero excess demand above average]
halo_factor    = β_halo estimated from regression
hero_promo_flag = 1 if hero is on promotion; 0 otherwise
```

| Granularity | Hero Features | Follower Baseline Features |
|---|---|---|
| Daily | d_hero(t), d_hero(t−1), hero_uplift, hero_promo_flag, halo_factor | 7/30/90-day own rolling mean, seasonal index |
| Weekly | d_hero(t), d_hero(t−1), hero_uplift, hero_promo_flag | 4/8/13-week own rolling mean, seasonal index |
| Monthly | d_hero(t), d_hero(t−1), hero_uplift | 3/6/12-month own rolling mean |
| Quarterly | d_hero(t), hero_uplift | 2/4-quarter own rolling mean |
| Yearly | d_hero(t) | Annual own rolling mean |

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM with hero demand as primary feature for follower
- Configuration: Objective = reg:squarederror; Metric = WMAPE; improvement vs independent > 5%
- Key features: d_hero(t), d_hero(t−1), hero_uplift, halo_factor, hero_promo_flag, follower baseline rolling mean
- When to use: Primary model when Granger confirmed and ≥ 12 periods co-active history

#### 6.2 Deep Learning (DL)
- Architectures: Shared TFT across hero + follower; hero demand as known past covariate for follower

| Granularity | Follower Lookback | Hero Covariate | Output |
|---|---|---|---|
| Daily | 180 days | d_hero(t−90 to t) | P10, P50, P90 |
| Weekly | 52 weeks | d_hero(t−26 to t) | P10, P50, P90 |
| Monthly | 24 months | d_hero(t−12 to t) | P10, P50, P90 |
| Quarterly | 8 quarters | d_hero(t−4 to t) | P10, P50, P90 |
| Yearly | 5 years | d_hero(t−2 to t) | P10, P50, P90 |

- When to use: History > 2 years with consistent hero signal; r > 0.60

#### 6.3 Statistical / Time Series Models
- Architectures: Dynamic Regression — follower modelled as function of hero + ARIMA residual

**Dynamic Regression:**
```
d_follower(t) = α + β_halo × d_hero(t) + β_lag × d_hero(t−1) + ARIMA(p,d,q) residual
Estimate via GLS; confidence interval on β_halo for halo strength reporting
```

- When to use: Interpretability; β_halo coefficient reporting for commercial teams

#### 6.4 Baseline / Fallback Model
- Fallback: Independent model on follower (ignore hero signal) — if Granger fails to hold
- Alert if Granger p-value rises above 0.10 in quarterly re-test

### 7. Ensemble & Weighting

#### 7.2 Dynamic Weight Schedule

| Halo Strength (β_halo) | LightGBM | TFT | Dynamic Regression |
|---|---|---|---|
| β_halo < 0.20 (mild) | 45% | 20% | 35% |
| 0.20 ≤ β_halo < 0.40 (moderate) | 50% | 25% | 25% |
| β_halo ≥ 0.40 (strong) | 55% | 30% | 15% |

### 8. Uncertainty Quantification
- Method: Quantile regression on follower model residuals; hero signal uncertainty propagated
- Output: [P10, P50, P90] — wider when hero forecast itself has high uncertainty
- Use case: Follower safety stock at P75; joint hero + follower planning reviewed together

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Joint planning rule: Hero and follower promotional plans reviewed together — hero promo → automatic follower forecast uplift
- Hero stockout alert: If hero goes OOS → alert for follower demand impact; reduce follower forecast by halo_factor × expected_hero_demand_loss
- WMAPE improvement check: Joint model must outperform independent by > 5%; else revert
- Manual overrides: Category manager hero promotion plan input; halo elasticity challenge; hero discontinuation flag

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | Follower WMAPE | vs Independent | Granger p-value | β_halo Stability | Bias Alert |
|---|---|---|---|---|---|
| Daily | < 20% | > 5% improvement | < 0.05 quarterly | CV(β_halo) < 0.30 | \|Bias\| > 8% |
| Weekly | < 17% | > 5% improvement | < 0.05 quarterly | CV(β_halo) < 0.30 | \|Bias\| > 7% |
| Monthly | < 14% | > 5% improvement | < 0.05 quarterly | CV(β_halo) < 0.30 | \|Bias\| > 6% |
| Quarterly | < 11% | > 4% improvement | < 0.05 quarterly | CV(β_halo) < 0.30 | \|Bias\| > 5% |
| Yearly | < 9% | > 4% improvement | < 0.05 | CV(β_halo) < 0.30 | \|Bias\| > 4% |

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
- Auto-detect: Granger p-value rises above 0.10 in quarterly re-test → reclassify to Complementary or Independent; β_halo becomes negative → investigate cannibalism; hero discontinued → reclassify follower to Independent
- Manual override: Category manager halo elasticity revision; hero promotional plan input; hero discontinuation notification
- Override expiration: Per quarterly Granger re-test

### 12. Reclassification / Model Selection

| Condition | Target | Holding Period | Transition |
|---|---|---|---|
| Granger p > 0.10 for 2 consecutive quarterly tests | Complementary (mutual) or Independent | 2 tests | Re-test then soft blend |
| β_halo becomes negative | Cannibalistic (re-test) | 2 tests | Immediate re-test |
| Hero discontinued | Independent | Immediate | Hard switch |
| Reverse Granger also significant (mutual) | Complementary | 2 tests | Re-classify |

### 13. Review Cadence
- Monthly β_halo stability monitor; quarterly Granger causality re-test; annual portfolio interaction map refresh

---

*End of Dimension 11 · Interaction Pattern*
*5 Segments Complete · I1 through I5*

---
