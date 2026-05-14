# Segment Model Template

## Dimension 11 · Cannibalistic

---

### 1. Definition
Predicts demand for SKUs where growth in a related SKU systematically reduces demand for this SKU (δ < −0.15; p < 0.05), requiring portfolio-level demand sharing models that prevent double-counting and produce internally consistent total demand forecasts.

### 2. Detailed Description
- **Applicable scenarios:** New variant launch cannibalising existing SKU, premium version taking share from standard, own-label growth at expense of branded, reformulated product displacing original
- **Boundaries:**

| Granularity | Cannibalism Coefficient | Significance | Min Co-Active History |
|---|---|---|---|
| Daily | δ < −0.15 | p < 0.05 | ≥ 90 co-active days |
| Weekly | δ < −0.15 | p < 0.05 | ≥ 26 co-active weeks |
| Monthly | δ < −0.15 | p < 0.05 | ≥ 12 co-active months |
| Quarterly | δ < −0.10 | p < 0.10 | ≥ 4 co-active quarters |
| Yearly | δ < −0.10 | p < 0.10 | ≥ 2 co-active years |

- **Key demand characteristics:** As cannibalising SKU (A) grows, this SKU (B) demand falls; total portfolio demand may be stable — only intra-portfolio allocation changes; cannibalism often accompanies a new product launch
- **Differentiation from other models:** Unlike Substitution, cannibalism is endogenous (driven by own portfolio dynamics not external OOS); unlike Declining Lifecycle, the cause is a specific portfolio SKU not market forces

### 3. Business Impact
- **Primary risk (over-forecast):** Forecasting this SKU without accounting for cannibalising SKU growth — excess inventory on declining SKU
- **Primary risk (under-forecast):** Under-forecasting the cannibalising SKU because the cannibalised SKU's decline is not attributed correctly
- **Strategic importance:** Very high — cannibalism is the most common source of systematic forecast bias at new product launch; undetected cannibalism creates overstock on old SKU and understock on new

### 4. Priority Level
🔴 **Tier 1** — Cannibalism creates simultaneous overstock (old SKU) and understock (new SKU); portfolio-level P&L impact is severe.

### 5. Model Strategy Overview

#### 5.1 Cannibalism-Adjusted Model
```
d_B(t) = d_B_baseline(t) − δ × ΔQ_A(t)
where δ = cannibalism coefficient (< 0; estimated from regression)
      ΔQ_A(t) = change in SKU_A demand vs prior period

Portfolio total constraint:
  d_A(t) + d_B(t) ≤ M(t)   [market size constraint M estimated from pre-A history]
  If forecast violates → rescale: d_B(t) = M(t) − d_A(t)

Cannibalism rate: CR = |δ| × ΔQ_A_mean / d_B_baseline_mean × 100 [% of B demand at risk per period]
```

#### 5.2 Analogue / Similarity Logic
- k = 3 (prior new product launches in same category with similar cannibalism pattern)
- Similarity: |δ| ±0.05, category, price tier relationship between A and B

#### 5.3 Feature Engineering

**Cannibalism Features:**
```
d_A(t)       = demand of cannibalising SKU A at time t
ΔQ_A(t)      = d_A(t) − d_A(t−1)   [change in A demand]
A_growth_rate = rolling slope of d_A(t)
cannibalism_exposure = δ × d_A_mean / d_B_mean   [% of B demand at risk]
market_share_B = d_B(t) / (d_A(t) + d_B(t))   [B's share of combined portfolio]
```

| Granularity | Cannibalism Features | Baseline Features |
|---|---|---|
| Daily | d_A(t), ΔQ_A(t), A growth rate, market_share_B, cannibalism_exposure | 7/30/90-day non-cannibalised rolling mean, seasonal index |
| Weekly | d_A(t), ΔQ_A(t), A growth rate, market_share_B | 4/8/13-week baseline, seasonal index |
| Monthly | d_A(t), ΔQ_A(t), market_share_B | 3/6/12-month baseline |
| Quarterly | d_A(t), ΔQ_A(t) | 2/4-quarter baseline |
| Yearly | d_A(t), market_share_B | Annual baseline |

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM with cannibalism features (ΔQ_A as primary predictor)
- Configuration: Objective = reg:squarederror; Metric = WMAPE
- Key features: ΔQ_A, d_A, market_share_B, cannibalism_exposure, baseline rolling mean
- When to use: Primary model when ≥ 12 periods of co-active history

#### 6.2 Deep Learning (DL)
- Architectures: TFT with SKU_A demand as past observed covariate for SKU_B

| Granularity | Lookback | A Covariate | Output |
|---|---|---|---|
| Daily | 180 days | d_A(t−90 to t) | P10, P50, P90 |
| Weekly | 52 weeks | d_A(t−26 to t) | P10, P50, P90 |
| Monthly | 24 months | d_A(t−12 to t) | P10, P50, P90 |
| Quarterly | 8 quarters | d_A(t−4 to t) | P10, P50, P90 |
| Yearly | 5 years | d_A(t−2 to t) | P10, P50, P90 |

#### 6.3 Statistical / Time Series Models
- Architectures: SUR (Seemingly Unrelated Regressions) — joint system estimating A and B simultaneously

**SUR System:**
```
Equation A: d_A(t) = α_A + β_A × X_A(t) + ε_A(t)
Equation B: d_B(t) = α_B + β_B × X_B(t) + δ × d_A(t) + ε_B(t)
Estimate jointly via GLS — captures cross-equation correlation in errors
δ = cannibalism coefficient (target: < −0.15; p < 0.05)
```

- When to use: Interpretability; δ coefficient reporting; portfolio planning

#### 6.4 Baseline / Fallback Model
- Fallback: Independent model on B adjusted by market_share_B trend only
- Alert if portfolio total (A+B) exceeds market size M by > 10%

### 7. Ensemble & Weighting

#### 7.2 Dynamic Weight Schedule

| δ Magnitude | LightGBM | TFT | SUR |
|---|---|---|---|
| \|δ\| 0.15–0.30 (mild cannibalism) | 50% | 25% | 25% |
| \|δ\| 0.30–0.50 (moderate) | 45% | 25% | 30% |
| \|δ\| > 0.50 (severe) | 35% | 25% | 40% |

### 8. Uncertainty Quantification
- Method: Scenario analysis — A growth continues vs A plateaus vs A declines
- Output: [P10 (A continues growing), P50 (base), P90 (A plateaus)]
- Use case: P10 for conservative B inventory; P50 for base; joint A+B safety stock constrained by M

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Market size constraint: d_A_forecast + d_B_forecast ≤ M(t) × 1.05
- Cannibalism rate monitor: Alert if CR > 30% in any period (severe cannibalism)
- Portfolio P&L check: Verify incremental A revenue > lost B revenue (cannibalism ROI positive)
- Manual overrides: Commercial team A launch plan; market size M revision; cannibalism rate challenge

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | B WMAPE | A+B Total WMAPE | δ Stability | Portfolio Violations | Bias Alert |
|---|---|---|---|---|---|
| Daily | < 22% | < 15% | CV(δ) < 0.30 | < 5% of periods | \|Bias\| > 10% |
| Weekly | < 20% | < 12% | CV(δ) < 0.30 | < 5% | \|Bias\| > 8% |
| Monthly | < 18% | < 10% | CV(δ) < 0.30 | < 5% | \|Bias\| > 7% |
| Quarterly | < 15% | < 8% | CV(δ) < 0.30 | < 3% | \|Bias\| > 6% |
| Yearly | < 12% | < 6% | CV(δ) < 0.30 | < 3% | \|Bias\| > 5% |

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
- Auto-detect: δ becomes positive (A now lifting B) → reclassify to Complementary or Halo; market size violated for 3 periods → rescale and alert; B demand reaches near-zero (full cannibalism) → Lifecycle: Decline for B
- Manual override: Product rationalisation decision (plan to delist B); A launch delay → temporarily suspend cannibalism model
- Override expiration: Per quarterly review

### 12. Reclassification / Model Selection

| Condition | Target | Holding Period | Transition |
|---|---|---|---|
| δ becomes positive for 4 estimations | Complementary | 4 estimations | Re-test |
| B demand stabilises (δ → 0) for 4 estimations | Independent | 4 estimations | Soft blend |
| B demand → 0 permanently | Lifecycle: Phasing Out (B) | Planner decision | Planner review |

### 13. Review Cadence
- Monthly δ stability monitor; quarterly portfolio ROI review; annual cannibalism reassessment

---

---
