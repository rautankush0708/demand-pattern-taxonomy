## T4 · Cyclical Trend
### 1. Definition
Predicts demand for SKUs exhibiting long-wave demand cycles beyond the primary seasonal frequency, where standard seasonal models underfit and multi-period cycle-aware models are required to capture boom-bust or long-cycle patterns.

### 2. Detailed Description
- **Applicable scenarios:** Business cycle-sensitive categories, commodities, capital goods, construction materials, economic-cycle-driven categories, fashion macro-cycles
- **Boundaries:**

| Granularity | Detection Condition | Cycle Period Range | Min Obs |
|---|---|---|---|
| Daily | FFT peak on detrended/deseasonalised series; amplitude > 10% of mean; cycle period > 14 days | 14 days to 3 years | ≥ 2 full cycles |
| Weekly | FFT peak; amplitude > 10%; cycle period > 8 weeks | 8 weeks to 3 years | ≥ 2 full cycles |
| Monthly | FFT peak; amplitude > 10%; cycle period > 6 months | 6 months to 5 years | ≥ 2 full cycles |
| Quarterly | FFT peak; amplitude > 10%; cycle period > 2 quarters | 2 quarters to 5 years | ≥ 2 full cycles |
| Yearly | FFT peak; amplitude > 10%; cycle period > 2 years | 2 years to 10 years | ≥ 2 full cycles |

- **Key demand characteristics:** Long-wave oscillation beyond primary seasonality; demand rises and falls in multi-period cycles; standard seasonal models treat troughs as anomalies
- **Differentiation from other models:** Unlike Seasonal (short calendar cycle), cycles are longer; unlike Upward/Downward Trend, direction reverses cyclically; unlike Reverting, deviations are not random but structured

### 3. Business Impact
- **Primary risk (over-forecast):** Inventory build at cycle peak — missed trough
- **Primary risk (under-forecast):** Stockout at cycle trough recovery — missed upturn
- **Strategic importance:** High for capital goods, industrial, and economic-cycle-sensitive categories

### 4. Priority Level
🟠 Tier 2 — Complex modelling required; data pipeline for macro indicators needed; medium-high implementation effort.

### 5. Model Strategy Overview

#### 5.1 Cycle Decomposition (Primary Pre-Processing Step)
```
STEP 1: Remove seasonal component → d_adj(t) = d(t) / SI(t)
STEP 2: Remove linear trend → d_dt(t) = d_adj(t) − (β₀ + β₁ × t)
STEP 3: Identify cycle via FFT → cycle period T_c = 1 / f_peak
STEP 4: Fit sinusoidal cycle → C(t) = A × sin(2π × t / T_c + φ)
         A = amplitude (estimated via OLS); φ = phase offset
STEP 5: Reconstruct forecast → F(t) = Trend(t) + Seasonal(t) + Cycle(t) + ε(t)
```

#### 5.2 Feature Engineering

| Granularity | Cycle Features | Macro Features | Rolling Features |
|---|---|---|---|
| Daily | Cycle phase (t mod T_c / T_c), cycle position index, days to cycle peak/trough | Consumer confidence, industrial output index | 7, 30, 90-day mean, std |
| Weekly | Cycle phase, weeks to cycle peak/trough, cycle amplitude index | PMI, GDP growth rate, industry index | 4, 8, 13, 26-week mean, std |
| Monthly | Cycle phase (month in cycle), months to peak/trough | GDP growth, industry output, commodity price | 2, 3, 6, 12-month mean, std |
| Quarterly | Cycle phase (quarter in cycle), quarters to peak/trough | GDP growth, capital expenditure index | 1, 2, 4-quarter mean, std |
| Yearly | Cycle phase (year in cycle), years to peak/trough | GDP, macro cycle indicator | 1, 2, 3-year mean, std |

### 6. Model Families

#### 6.1 ML: LightGBM with cycle phase features + macro economic indicators
- Objective: reg:squarederror | Metric: WMAPE, RMSE
- Key features: Cycle phase, cycle amplitude, macro index, rolling means, seasonal index

#### 6.2 DL: TFT with long lookback (captures full cycle)

| Granularity | Lookback (covers ≥ 2 cycles) | Features |
|---|---|---|
| Daily | 2 × T_c (days) | 18 |
| Weekly | 2 × T_c (weeks) | 15 |
| Monthly | 2 × T_c (months) | 12 |
| Quarterly | 2 × T_c (quarters) | 10 |
| Yearly | 2 × T_c (years) | 8 |

#### 6.3 Statistical: BSTS (Bayesian Structural Time Series) with cycle component

**BSTS Cycle Component:**
```
Cycle(t) = ρ × cos(λ) × Cycle(t-1) + ρ × sin(λ) × Cycle*(t-1) + ε_c(t)
Cycle*(t) = −ρ × sin(λ) × Cycle(t-1) + ρ × cos(λ) × Cycle*(t-1) + ε_c*(t)
where λ = 2π / T_c (cycle frequency); ρ ∈ (0,1) = damping factor
```

| Granularity | λ Computation | ρ |
|---|---|---|
| Daily | 2π / T_c_days | 0.90 |
| Weekly | 2π / T_c_weeks | 0.90 |
| Monthly | 2π / T_c_months | 0.85 |
| Quarterly | 2π / T_c_quarters | 0.85 |
| Yearly | 2π / T_c_years | 0.80 |

#### 6.4 Fallback: Seasonal model (treats cycle as long-season); alert if cycle missed

### 7. Ensemble

| History (Full Cycles) | LightGBM | TFT | BSTS |
|---|---|---|---|
| 2 cycles | 40% | 0% | 60% |
| 3 cycles | 45% | 25% | 30% |
| ≥ 4 cycles | 40% | 35% | 25% |

### 8. Uncertainty Quantification
- Method: Scenario analysis — early cycle, mid-cycle, late cycle scenarios
- Output: [P10, P50, P90] conditioned on cycle position
- Use case: Strategic inventory positioning at cycle trough; run-down at cycle peak

### 9. Business Rules
- Non-negativity: max(0, forecast)
- Cycle position flag: Attach cycle phase label (early expansion / late expansion / early contraction / late contraction) to all forecasts for planner context
- Manual overrides: Macro economist input on cycle turning point; commodity price signal

### 10. Evaluation

| Granularity | WMAPE Target | Cycle Phase WMAPE | Bias Alert |
|---|---|---|---|
| Daily | < 25% | Peak/trough < 30% | \|Bias\| > 12% |
| Weekly | < 22% | Peak/trough < 28% | \|Bias\| > 10% |
| Monthly | < 20% | Peak/trough < 25% | \|Bias\| > 8% |
| Quarterly | < 18% | Peak/trough < 22% | \|Bias\| > 6% |
| Yearly | < 15% | Peak/trough < 20% | \|Bias\| > 5% |

### 11. Exception Handling
- Alert: Cycle period changes significantly (> 20%) between detections → re-detect cycle; macro shock → evaluate permanent cycle disruption

### 12. Reclassification

| Condition | Target | Holding Period |
|---|---|---|
| FFT cycle no longer significant for 2 full cycles | Flat or Reverting | 2 cycles |
| Mann-Kendall p < 0.05 confirms monotonic direction | Upward or Downward Trend | 4 periods |

### 13. Review Cadence
- Quarterly cycle position update; semi-annual macro review; annual full re-evaluation

---
