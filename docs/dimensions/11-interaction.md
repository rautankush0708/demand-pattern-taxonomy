# Dimension 11 · Interaction Pattern
## Demand Forecasting Model Templates

---

> **Segments:** 5 · Independent · Substitution · Complementary · Cannibalistic · Halo
> **Granularities:** Daily · Weekly · Monthly · Quarterly · Yearly

---

## 0.3 Interaction Pattern Metrics

### A. Cross-SKU Correlation
```
Pearson correlation between SKU_A and SKU_B demand:
  r(A,B) = Σ[(d_A(t) − d̄_A)(d_B(t) − d̄_B)] / [n × σ_A × σ_B]

Complementary: r > +0.50 (demand moves together)
Substitution:  r < −0.30 AND SKU_B stockout → SKU_A spike
Cannibalistic: r < −0.30 AND SKU_A grows → SKU_B shrinks
Halo:          r > +0.40 AND causal direction (hero → follower)
Independent:   |r| < 0.20
```

### B. Substitution Detection
```
Substitution event: Period where SKU_B is OOS (stockout)
                    AND SKU_A demand spikes > 1.5σ above baseline

Substitution rate: sub_rate = mean(d_A during SKU_B OOS) / mean(d_A during SKU_B available) − 1

Significant substitution: sub_rate > 0.20 AND confirmed in ≥ 3 OOS events
```

### C. Cannibalism Detection
```
Cannibalism coefficient: δ = ΔQ_B / ΔQ_A (demand lost from B per unit gained by A)

Estimated via regression:
  ΔQ_B(t) = α + δ × ΔQ_A(t) + β × controls(t) + ε(t)
  δ < 0 → A cannibalises B; |δ| = cannibalism rate
  Significant: p < 0.05 for δ AND |δ| > 0.15
```

---

# PART 1 — SEGMENT TEMPLATES

## I1 · Independent

### 1. Definition
Predicts demand for SKUs with no statistically significant cross-SKU correlation (|r| < 0.20), where standalone models are optimal and portfolio-level effects can be ignored.

### 5. Model Strategy
- Standard behavior model per segment — no cross-SKU features required
- Cross-correlation monitoring: Monthly check — alert if |r| rises above 0.30 with any portfolio SKU

### Evaluation — Standard per Behavior segment

---

## I2 · Substitution

### 1. Definition
Predicts demand for SKUs that see demand increases when a substitute SKU is unavailable, requiring OOS-conditional forecasting and portfolio-level inventory coordination.

### 5. Model Strategy

#### 5.1 Substitution-Conditional Model
```
d_A(t) = d_A_baseline(t) + sub_rate_A × d_A_baseline(t) × OOS_B(t)
where OOS_B(t) = 1 if SKU_B is out-of-stock at time t
      sub_rate_A = proportion of SKU_B demand shifting to SKU_A during OOS
      sub_rate_A estimated from historical OOS events of SKU_B

Portfolio total demand conservation:
  d_A(t) + d_B(t) ≈ d_total(t)   [total demand conserved; only distribution changes]
```

| Granularity | OOS Detection | Substitution Features |
|---|---|---|
| Daily | Real-time inventory flag | OOS flag for each substitute SKU, days since OOS start, sub rate |
| Weekly | Weekly inventory review | OOS week flag, weeks since OOS |
| Monthly | Monthly inventory review | OOS month flag |
| Quarterly | Quarterly review | OOS quarter flag |
| Yearly | Annual review | OOS year flag |

### 6. Model Families

#### 6.1 ML: LightGBM with OOS flags and substitution rate features
#### 6.2 Statistical: Intervention model with OOS dummy variable

### Evaluation

| Granularity | Baseline WMAPE | OOS-Period WMAPE | Sub Rate Accuracy | Bias Alert |
|---|---|---|---|---|
| Daily | Per behavior std | < 30% | ±15% | |Bias| > 12% |
| Weekly | Per behavior std | < 25% | ±12% | |Bias| > 10% |
| Monthly | Per behavior std | < 22% | ±10% | |Bias| > 8% |
| Quarterly | Per behavior std | < 18% | ±8% | |Bias| > 6% |
| Yearly | Per behavior std | < 15% | ±6% | |Bias| > 5% |

---

## I3 · Complementary

### 1. Definition
Predicts demand for SKUs that move in sync with a correlated partner SKU (r > 0.50), enabling cross-SKU signal sharing to improve forecast accuracy for both SKUs simultaneously.

### 5. Model Strategy

#### 5.1 Cross-SKU Signal Sharing
```
d_A(t) = f(d_A_history, d_B_history, shared_features)
where d_B(t) provides additional signal for d_A(t) and vice versa

Feature: d_B(t−1), d_B(t−2), cross_correlation_strength
Cross-SKU feature weight proportional to |r(A,B)|
```

### 6. Model Families

#### 6.1 ML: LightGBM with lagged partner SKU demand as feature
#### 6.2 DL: DeepAR or TFT trained jointly across complementary SKU pairs (shared model)
#### 6.3 Statistical: Multivariate time series (VAR model if r > 0.70)

**VAR(1) for Complementary Pairs:**
```
[d_A(t)]   [c_A]   [A_11 A_12] [d_A(t-1)]   [ε_A(t)]
[d_B(t)] = [c_B] + [A_21 A_22] [d_B(t-1)] + [ε_B(t)]
A_12 > 0 → B Granger-causes A (useful cross-SKU feature)
A_21 > 0 → A Granger-causes B
```

### Evaluation

| Granularity | WMAPE Improvement vs Independent | Cross-Correlation Maintained | Bias Alert |
|---|---|---|---|
| Daily | > 5% improvement | r > 0.40 | |Bias| > 8% |
| Weekly | > 5% improvement | r > 0.40 | |Bias| > 7% |
| Monthly | > 5% improvement | r > 0.35 | |Bias| > 6% |
| Quarterly | > 5% improvement | r > 0.35 | |Bias| > 5% |
| Yearly | > 4% improvement | r > 0.30 | |Bias| > 4% |

---

## I4 · Cannibalistic

### 1. Definition
Predicts demand for SKUs where growth of a related SKU systematically reduces demand (δ < −0.15), requiring portfolio-level demand sharing models to avoid double-counting and produce internally consistent forecasts.

### 5. Model Strategy

#### 5.1 Cannibalism-Adjusted Model
```
d_B(t) = d_B_baseline(t) − δ × ΔQ_A(t)
where δ = cannibalism coefficient (< 0)
      ΔQ_A(t) = change in SKU_A demand vs prior period
      δ estimated from: ΔQ_B(t) = α + δ × ΔQ_A(t) + controls + ε

Portfolio total (A+B) must not exceed market size:
  d_A(t) + d_B(t) ≤ M(t)   [market size constraint]
  If violated → rescale proportionally to history share
```

### 6. Model Families

#### 6.1 ML: LightGBM with ΔQ_A as feature for SKU_B forecast
#### 6.2 Statistical: System of equations (SUR — Seemingly Unrelated Regressions)

**SUR for Cannibalism:**
```
Equation 1: d_A(t) = α_A + β_A × X_A(t) + ε_A(t)
Equation 2: d_B(t) = α_B + β_B × X_B(t) + δ × d_A(t) + ε_B(t)
Estimate jointly via GLS — captures cross-equation correlation
```

### Evaluation

| Granularity | WMAPE (A+B total) | Cannibalism Coefficient Stability | Portfolio Constraint Violations |
|---|---|---|---|
| Daily | < 20% | CV(δ) < 0.30 | < 5% of periods |
| Weekly | < 18% | CV(δ) < 0.30 | < 5% |
| Monthly | < 15% | CV(δ) < 0.30 | < 5% |
| Quarterly | < 12% | CV(δ) < 0.30 | < 3% |
| Yearly | < 10% | CV(δ) < 0.30 | < 3% |

---

## I5 · Halo

### 1. Definition
Predicts demand for SKUs where a hero SKU's performance lifts demand for associated SKUs (r > 0.40; causal direction confirmed), requiring hero-follower modelling where the hero SKU forecast is used as a leading input for follower SKU forecasts.

### 5. Model Strategy

#### 5.1 Hero-Follower Model
```
d_follower(t) = d_follower_baseline(t) × (1 + halo_factor × d_hero(t) / d_hero_mean)
halo_factor estimated from: d_follower(t) = α + β × d_hero(t) + controls + ε
β > 0 → positive halo; β / mean(d_follower) = halo elasticity

Causal direction test: Granger causality from hero to follower (not reverse)
  H0: d_hero does NOT Granger-cause d_follower
  Reject H0 at p < 0.05 → confirmed hero → follower direction
```

### 6. Model Families

#### 6.1 ML: LightGBM — hero SKU demand as primary feature for follower
#### 6.2 DL: Shared TFT across hero + follower SKUs
#### 6.3 Statistical: Dynamic regression (follower ~ hero + controls + ARIMA residual)

### Evaluation

| Granularity | Follower WMAPE | Halo Granger Causality | Halo Coefficient Stability | Bias Alert |
|---|---|---|---|---|
| Daily | < 22% | p < 0.05 confirmed | CV(β) < 0.30 | |Bias| > 10% |
| Weekly | < 18% | p < 0.05 | CV(β) < 0.30 | |Bias| > 8% |
| Monthly | < 15% | p < 0.05 | CV(β) < 0.30 | |Bias| > 7% |
| Quarterly | < 12% | p < 0.05 | CV(β) < 0.30 | |Bias| > 6% |
| Yearly | < 10% | p < 0.05 | CV(β) < 0.30 | |Bias| > 5% |
