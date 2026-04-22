## E4 · Saturation

### 1. Definition
Predicts demand for SKUs where demand response to stimulus follows a diminishing returns curve, reaching a maximum ceiling beyond which additional stimulus generates negligible incremental demand, requiring non-linear causal models and saturation-aware promotional investment optimisation.

### 2. Detailed Description
- **Applicable scenarios:** Market-penetration-limited categories, loyalty-capped demand, population-constrained categories, categories where all reachable customers have already responded, high-frequency-purchase categories where stockpiling is limited
- **Boundaries:**

| Granularity | Detection Condition | Q_max Confidence | Min Events |
|---|---|---|---|
| Daily | Q ≥ 0.90 × Q_max at peak stimulus AND β₂ < 0.50 in Adstock model | p < 0.05 for Q_max | ≥ 10 events across stimulus range |
| Weekly | Q ≥ 0.90 × Q_max AND β₂ < 0.50 | p < 0.05 | ≥ 8 events |
| Monthly | Q ≥ 0.90 × Q_max AND β₂ < 0.50 | p < 0.05 | ≥ 6 events |
| Quarterly | Q ≥ 0.90 × Q_max AND β₂ < 0.50 | p < 0.05 | ≥ 4 events |
| Yearly | Q ≥ 0.90 × Q_max AND β₂ < 0.50 | p < 0.05 | ≥ 3 events |

- **Key demand characteristics:** Strong response at low stimulus levels; diminishing returns as stimulus increases; demand ceiling (Q_max) that cannot be breached regardless of promotional depth; promotional ROI falls sharply as ceiling is approached
- **Differentiation from other models:** Unlike Elastic, response is not proportional — it decelerates with stimulus; unlike Threshold, response starts immediately (no dead zone); unlike Inelastic, there IS a strong response — just with a ceiling

### 3. Business Impact
- **Primary risk (over-forecast):** Over-estimating ceiling — deploying excessive promotional spend beyond saturation point
- **Primary risk (under-forecast):** Under-deploying promotion below saturation — leaving demand unrealised
- **Strategic importance:** High — Q_max defines the revenue ceiling for promotional investment; optimal promotional depth is the inflection point of ROI curve

### 4. Priority Level
🟠 Tier 2 — Non-linear model required; primary business value is defining optimal promotional depth and ROI ceiling.

### 5. Model Strategy Overview

#### 5.1 Saturation Curve Model
```
Logistic saturation model:
  Q(t) = Q_max / (1 + e^{−λ × (stimulus(t) − T_mid)})
  where Q_max = demand ceiling
        λ = steepness of saturation curve
        T_mid = stimulus level at 50% of Q_max (inflection point)

Power saturation (Adstock) model:
  Q(t) = baseline(t) × (1 + α × stimulus(t)^β)
  where β < 1 → diminishing returns (β = 0.50 → square root diminishing returns)
        α = initial response rate

Optimal promotional depth (ROI maximisation):
  Marginal response = dQ/dstimulus = 0.5 × Q_max × λ × e^{−λ×(s−T_mid)} / (1 + e^{−λ×(s−T_mid)})²
  ROI = (Margin × ΔQ − Promo_cost) / Promo_cost
  Optimal stimulus: s* = argmax ROI(s)
```

#### 5.2 Feature Engineering

| Granularity | Saturation Features | Stimulus Features | Baseline Features |
|---|---|---|---|
| Daily | Stimulus level, stimulus^0.5 (square root — captures diminishing returns), stimulus^2 (quadratic), distance from Q_max, saturation ratio (Q/Q_max) | Promo depth, promo type, display flag, distribution on promo | 7/30/90-day non-promo rolling mean, seasonal index |
| Weekly | Stimulus level, stimulus^0.5, distance from Q_max, saturation ratio | Promo depth, promo type | 4/8/13-week baseline, seasonal index |
| Monthly | Stimulus level, stimulus^0.5, saturation ratio | Promo depth, promo type | 3/6/12-month baseline |
| Quarterly | Stimulus level, stimulus^0.5, saturation ratio | Promo depth | 2/4-quarter baseline |
| Yearly | Annual stimulus level, saturation ratio | Annual promo intensity | Annual baseline |

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM with non-linear stimulus features (stimulus^0.5, stimulus^2, saturation ratio)
- Configuration: Objective = reg:squarederror; Metric = WMAPE, Uplift Accuracy
- Key features: Stimulus^0.5 (primary non-linear feature), saturation ratio, baseline rolling mean, seasonal index, promo type
- When to use: Primary model — non-linear features enable tree models to learn saturation curve

#### 6.2 Deep Learning (DL)
- Architectures: TFT with non-linear stimulus encoding as known future covariate

| Granularity | Lookback | Future Covariates | Output |
|---|---|---|---|
| Daily | 180 days | Promo plan 30 days ahead (with depth encoding) | P10, P50, P90 |
| Weekly | 52 weeks | Promo plan 8 weeks ahead | P10, P50, P90 |
| Monthly | 24 months | Promo plan 3 months ahead | P10, P50, P90 |
| Quarterly | 8 quarters | Promo plan 1 quarter ahead | P10, P50, P90 |
| Yearly | 5 years | Annual promo plan | P10, P50, P90 |

#### 6.3 Statistical / Time Series Models
- Architectures: Non-linear least squares (NLS) — logistic saturation curve

**NLS Saturation Fitting:**
```
Q(t) = Q_max × [1 − e^{−λ × stimulus(t)}] + ε(t)
Estimate: Q_max, λ via NLS minimising Σε²
Confidence interval for Q_max: Delta method or bootstrap
Starting values: Q_max_0 = 1.5 × max(Q_observed); λ_0 = 0.05
```

- When to use: Interpretability; Q_max reporting; ROI curve generation for trade planning

#### 6.4 Baseline / Fallback Model
- Fallback: Baseline × min(saturation_factor, 2.0) where saturation_factor based on historical mean uplift at current stimulus level
- Alert if Q_max estimate changes > 20% between estimations

### 7. Ensemble & Weighting

| Stimulus Level | LightGBM | TFT | NLS Saturation |
|---|---|---|---|
| Low (< 50% of saturation point) | 40% | 20% | 40% |
| Medium (50–90% of saturation point) | 50% | 25% | 25% |
| High (> 90% of saturation point — near ceiling) | 30% | 20% | 50% |

### 8. Uncertainty Quantification
- Method: Q_max bootstrap CI + quantile regression on residuals
- Output: [P10, P50, P90] — P90 capped at Q_max upper confidence bound
- Key output: Q_max estimate + 90% CI for trade planning

**ROI Curve Output:**
```
For each stimulus level s ∈ {0%, 5%, 10%, ..., 50%}:
  Expected uplift: ΔQ(s) = F_saturation(s) − baseline
  Marginal uplift: MΔQ(s) = ΔQ(s) − ΔQ(s − 5%)
  Marginal ROI(s) = (Margin × MΔQ(s)) / Marginal_promo_cost(s)
  Optimal s* = argmax ROI(s) [where marginal ROI = 1.0]
```

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Ceiling enforcement: max(forecast, 0); min(forecast, Q_max × 1.05) — hard ceiling with 5% buffer
- Over-promotion flag: If planned stimulus > optimal s* → alert trade team; ROI negative beyond s*
- Q_max advisory: Communicate Q_max and optimal promotional depth to trade team each cycle
- Manual overrides: Trade team ceiling challenge; market research on unrealised potential

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | Baseline WMAPE | Near-Ceiling WMAPE | Q_max Accuracy | ROI Curve Accuracy | Bias Alert |
|---|---|---|---|---|---|
| Daily | < 18% | < 25% | Q_max within ±15% | ROI peak within ±10% | \|Bias\| > 10% |
| Weekly | < 15% | < 22% | Q_max within ±12% | ROI peak within ±8% | \|Bias\| > 8% |
| Monthly | < 12% | < 20% | Q_max within ±10% | ROI peak within ±7% | \|Bias\| > 7% |
| Quarterly | < 10% | < 18% | Q_max within ±8% | ROI peak within ±6% | \|Bias\| > 6% |
| Yearly | < 8% | < 15% | Q_max within ±6% | ROI peak within ±5% | \|Bias\| > 5% |

#### 10.2 Backtesting Protocol
- Validate Q_max estimate on held-out near-ceiling promotional events
- Leave-one-out on events at different stimulus levels
- Min events: ≥ 3 events at stimulus levels > 80% of saturation point

#### 10.3 Retraining
- Standard cadence per granularity
- Re-estimate Q_max quarterly — saturation ceiling may shift with distribution or market size changes

### 11. Exception Handling & Overrides
- Auto-detect: Q_max rises significantly (> 20%) → market expansion detected; re-evaluate saturation model; β₂ rises above 0.80 → diminishing returns weakening → reclassify to Elastic; Q_max approaches zero (category collapse) → Lifecycle: Decline
- Manual override: Market expansion plan (new distribution, new geography) that raises effective Q_max; trade team ceiling challenge
- Override expiration: Per quarterly re-estimation

### 12. Reclassification

| Condition | Target | Holding Period |
|---|---|---|
| β₂ rises above 0.80 for 3 estimates | Elastic | 3 estimates |
| Non-linear piecewise threshold detected | Threshold | 2 estimates |
| Q_max shrinks to near-baseline | Inelastic | 3 estimates |
| New distribution expands Q_max significantly | Elastic (temporarily) | Until new Q_max estimated |

### 13. Review Cadence
- Monthly saturation ratio monitor; quarterly Q_max re-estimation and ROI curve refresh; annual trade strategy alignment

---

*End of Dimension 8 · Elasticity Pattern*
*4 Segments Complete · E1 through E4*
