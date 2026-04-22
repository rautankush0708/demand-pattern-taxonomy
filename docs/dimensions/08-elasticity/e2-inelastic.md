## E2 · Inelastic
### 1. Definition
Predicts demand for SKUs where demand quantity responds less than proportionally to price or promotional stimulus changes (|PED| < 1.0), where causal features add minimal forecast value and standard time-series methods are more reliable than causal models.

### 2. Detailed Description
- **Applicable scenarios:** Essential staples, habitual purchases, medically/nutritionally necessary products, utility-like demand, high switching-cost categories, brand-loyal categories with low substitutability
- **Boundaries:**

| Granularity | PED Range | Promo Uplift Threshold | Min Events | Confidence |
|---|---|---|---|---|
| Daily | −1.0 < PED < 0 | < 8% per 10% discount | ≥ 8 events | R² < 0.20 |
| Weekly | −1.0 < PED < 0 | < 8% per 10% discount | ≥ 6 events | R² < 0.20 |
| Monthly | −1.0 < PED < 0 | < 8% per 10% discount | ≥ 5 events | R² < 0.20 |
| Quarterly | −1.0 < PED < 0 | < 8% per 10% discount | ≥ 4 events | R² < 0.15 |
| Yearly | −1.0 < PED < 0 | < 8% per 10% discount | ≥ 3 events | R² < 0.15 |

- **Key demand characteristics:** Demand relatively stable regardless of price changes; promotional uplifts small and often not economically justifiable; brand loyalty or necessity drives purchase; price changes have limited demand impact
- **Differentiation from other models:** Unlike Elastic, promotional ROI is low — price/promo features add noise not signal; unlike Threshold, response is consistently weak across all stimulus levels; standard time-series models outperform causal models for Inelastic SKUs

### 3. Business Impact
- **Primary risk (over-forecast):** Standard model risk only — price features not required
- **Primary risk (under-forecast):** Standard model risk only
- **Strategic importance:** High revenue stability — inelastic SKUs provide reliable baseline revenue; promotional investment here delivers low ROI

### 4. Priority Level
🟠 Tier 2 — Lower forecast complexity; primary business value is identifying where NOT to invest promotional spend.

### 5. Model Strategy Overview

#### 5.1 Causal Feature Suppression
- Explicitly suppress price and promo features — they add noise for Inelastic SKUs
- Standard time-series model applied; causal model only used for strategic analysis (not operational forecasting)
- Elasticity estimate retained as metadata for pricing team reporting

#### 5.2 Analogue / Similarity Logic
- Not applicable — sufficient own history; inelastic demand is stable and reliable

#### 5.3 Feature Engineering

| Granularity | Included Features | Explicitly Excluded Features |
|---|---|---|
| Daily | 7/30/90/180/365-day rolling mean, std, CV²; day of week; holiday flag; seasonal index | Price features, promo depth, promo type, discount features, competitor price |
| Weekly | 4/8/13/26/52-week rolling mean, std; week of year; holiday; seasonal index | All price and promo features |
| Monthly | 2/3/6/12/24-month rolling mean, std; month of year; seasonal index | All price and promo features |
| Quarterly | 1/2/3/4-quarter rolling mean, std; quarter of year | All price and promo features |
| Yearly | 1/2/3/4-year rolling mean, std | All price and promo features |

- Note: Promo flag retained as binary (yes/no) — not as depth or type; used only for outlier detection during promo periods, not as a causal driver

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM (standard — no causal features)
- Configuration: Objective = reg:squarederror; Metric = WMAPE, RMSE
- Key features: Rolling means, seasonal index, holiday flag, promo binary flag (for outlier control only)
- When to use: Primary model — same as standard Stable behavior segment

#### 6.2 Deep Learning (DL)
- Architectures: N-BEATS (no causal external inputs)

| Granularity | Lookback | Features | Output |
|---|---|---|---|
| Daily | 365 days | 12 | P10, P50, P90 |
| Weekly | 52 weeks | 10 | P10, P50, P90 |
| Monthly | 24 months | 8 | P10, P50, P90 |
| Quarterly | 8 quarters | 6 | P10, P50, P90 |
| Yearly | 5 years | 5 | P10, P50, P90 |

- When to use: History > 2 years; seasonal pattern present

#### 6.3 Statistical / Time Series Models
- Architectures: ETS(A,N,A) — standard; SARIMA for complex seasonality

| Granularity | Model | Period |
|---|---|---|
| Daily | ETS(A,N,A) or TBATS | 7, 365 |
| Weekly | ETS(A,N,A) | 52 |
| Monthly | ETS(A,N,A) or SARIMA | 12 |
| Quarterly | ETS(A,N,A) | 4 |
| Yearly | ETS(A,N,N) | — |

- When to use: Always included — no causal model needed

#### 6.4 Baseline / Fallback Model
- Fallback: Same period last year
- Alert if fallback rate > 10%

### 7. Ensemble & Weighting

#### 7.2 Dynamic Weight Schedule

| History Length | LightGBM | N-BEATS | ETS |
|---|---|---|---|
| Up to 1 year | 55% | 0% | 45% |
| 1–2 years | 55% | 0% | 45% |
| > 2 years | 50% | 20% | 30% |

### 8. Uncertainty Quantification
- Method: Conformal prediction on residuals
- Output: [P10, P50, P90] — symmetric intervals expected for inelastic demand
- Use case: Standard safety stock from σ_residual × z_service_level; no promo-specific buffer needed

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Capping: min(forecast, 1.5 × full-year rolling max)
- Promotional override rule: If large promo planned (> 30% discount) on Inelastic SKU → flag for commercial review; ROI likely negative; do not increase forecast significantly
- Manual overrides: Standard S&OP consensus; supply constraint flag
- Alignment: ±20% of prior year same period

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | WMAPE Target | Bias Alert | Elasticity Monitor | Coverage |
|---|---|---|---|---|
| Daily | < 18% | \|Bias\| > 8% | Alert if PED < −1.0 (reclassify) | 80% P10–P90 |
| Weekly | < 15% | \|Bias\| > 7% | Alert if PED < −1.0 | 80% P10–P90 |
| Monthly | < 12% | \|Bias\| > 6% | Alert if PED < −1.0 | 80% P10–P90 |
| Quarterly | < 10% | \|Bias\| > 5% | Alert if PED < −1.0 | 80% P10–P90 |
| Yearly | < 8% | \|Bias\| > 4% | Alert if PED < −1.0 | 80% P10–P90 |

#### 10.2 Backtesting Protocol

| Granularity | Train | Test | Min History |
|---|---|---|---|
| Daily | 180 days | 30 days | 365 days |
| Weekly | 52 weeks | 13 weeks | 104 weeks |
| Monthly | 24 months | 6 months | 24 months |
| Quarterly | 8 quarters | 2 quarters | 8 quarters |
| Yearly | All available | 1 year | 3 years |

#### 10.3 Retraining

| Granularity | Cadence | Latency |
|---|---|---|
| Daily | Daily | T+4 hours |
| Weekly | Weekly | T+1 day |
| Monthly | Monthly | T+2 days |
| Quarterly | Quarterly | T+3 days |
| Yearly | Annually | T+7 days |

### 11. Exception Handling & Overrides
- Auto-detect: PED drops below −1.0 for 3 consecutive estimates → reclassify to Elastic; large promo uplift detected (> 15%) → flag for re-estimation
- Manual override: Pricing team major price change input (even if inelastic, very large changes may have some impact); supply constraint flag
- Override expiration: Single cycle

### 12. Reclassification

| Condition | Target Segment | Holding Period |
|---|---|---|
| PED drops below −1.0 for 3 estimates | Elastic | 3 estimates |
| Threshold behaviour detected | Threshold | 2 estimates |
| Saturation detected | Saturation | 2 estimates |

### 13. Review Cadence
- Monthly PED monitor; quarterly full elasticity re-estimation; annual pricing strategy alignment

---
