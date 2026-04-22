## T5 · Reverting
### 1. Definition
Predicts demand for SKUs that systematically deviate from a stable long-run mean and return to it, where mean-reversion models outperform trend extrapolation and prevent over-reaction to temporary deviations.

### 2. Detailed Description
- **Applicable scenarios:** Commodity-like demand, budget-constrained categories (spend reverts to annual budget), weather-normalised categories, post-shock recovery demand
- **Boundaries:**

| Granularity | Detection Condition | Half-Life Range | Min History |
|---|---|---|---|
| Daily | ADF p < 0.05 (stationary); reversion half-life estimated | 3–90 days | ≥ 180 days |
| Weekly | ADF p < 0.05; half-life estimable | 2–26 weeks | ≥ 52 weeks |
| Monthly | ADF p < 0.05; half-life estimable | 1–12 months | ≥ 24 months |
| Quarterly | ADF p < 0.05; half-life estimable | 1–4 quarters | ≥ 8 quarters |
| Yearly | ADF p < 0.05; half-life estimable | 1–3 years | ≥ 5 years |

- **Key demand characteristics:** Demand deviates above or below long-run mean; strong pull back toward mean; deviation magnitude decays exponentially at reversion half-life rate
- **Differentiation from other models:** Unlike Flat, demand does deviate noticeably; unlike Upward/Downward, deviation reverses direction; unlike Cyclical, reversion is probabilistic not structural

### 3. Business Impact
- **Primary risk (over-forecast):** Over-reacting to temporary upswing — building stock that isn't needed as demand reverts
- **Primary risk (under-forecast):** Under-reacting to temporary dip — cutting stock before demand recovers
- **Strategic importance:** Medium — primary value is avoiding over-reaction to noise

### 4. Priority Level
🟠 Tier 2 — Mean-reversion models prevent costly over-reactions; medium complexity.

### 5. Model Strategy Overview

#### 5.1 Mean Reversion Model (Primary)
```
Long-run mean: μ_LR = mean over extended window
Current deviation: dev(t) = d(t) − μ_LR
Reversion speed: α = estimated from regression Δdev(t) = α × dev(t-1) + ε(t)
                 α must be negative (−1 < α < 0) for reversion
Half-life: HL = −ln(2) / α

Forecast h periods ahead:
  dev_forecast(t+h) = dev(t) × (1+α)^h
  d_forecast(t+h) = μ_LR + dev_forecast(t+h)
  = μ_LR + (d(t) − μ_LR) × (1+α)^h
```

| Granularity | Long-Run Mean Window | Reversion Estimation Window |
|---|---|---|
| Daily | 365 days | 90-day rolling regression |
| Weekly | 52 weeks | 26-week rolling regression |
| Monthly | 24 months | 12-month rolling regression |
| Quarterly | 8 quarters | 4-quarter rolling regression |
| Yearly | 5 years | 3-year rolling regression |

#### 5.2 Feature Engineering

| Granularity | Reversion Features | Rolling Features |
|---|---|---|
| Daily | Current deviation (d(t) − μ_LR), deviation normalised by σ, half-life (days), reversion speed α, periods since last mean crossing | 7, 30, 90-day mean, std |
| Weekly | Current deviation, normalised deviation, half-life (weeks), α, weeks since last mean crossing | 4, 8, 13, 26-week mean, std |
| Monthly | Current deviation, normalised deviation, half-life (months), α | 2, 3, 6, 12-month mean, std |
| Quarterly | Current deviation, normalised deviation, half-life (quarters), α | 1, 2, 4-quarter mean, std |
| Yearly | Current deviation, normalised deviation, half-life (years), α | 1, 2, 3-year mean, std |

### 6. Model Families

#### 6.1 ML: LightGBM with deviation and reversion features
- Objective: reg:squarederror | Metric: WMAPE, RMSE

#### 6.2 DL: Not primary — mean reversion is well captured statistically

#### 6.3 Statistical: Ornstein-Uhlenbeck (OU) process — the natural model for mean-reverting demand

**OU Process:**
```
d(t+dt) = θ × (μ_LR − d(t)) × dt + σ × dW(t)
where θ = speed of reversion (θ > 0)
      μ_LR = long-run mean
      σ = volatility
      dW = Wiener process increment

Discrete-time equivalent:
d(t+1) = μ_LR + e^{−θ} × (d(t) − μ_LR) + σ × √[(1 − e^{−2θ}) / 2θ] × ε(t)
ε(t) ~ N(0,1)

θ = −ln(1+α)  where α = reversion speed from regression
Half-life HL = ln(2) / θ
```

| Granularity | θ Estimation | Typical HL Range |
|---|---|---|
| Daily | Daily regression on 90-day window | 7–30 days |
| Weekly | Weekly regression on 26-week window | 2–8 weeks |
| Monthly | Monthly regression on 12-month window | 1–4 months |
| Quarterly | Quarterly regression on 4-quarter window | 1–2 quarters |
| Yearly | Annual regression on 3-year window | 1–2 years |

#### 6.4 Fallback: Long-run mean as flat forecast (maximum reversion assumption)

### 7. Ensemble

| History | LightGBM | OU Process | ETS(A,N,N) |
|---|---|---|---|
| Up to 1 year | 20% | 50% | 30% |
| 1–2 years | 35% | 45% | 20% |
| > 2 years | 45% | 40% | 15% |

### 8. Uncertainty Quantification
- Method: OU analytical distribution — exact probability distribution available
- Output: [P10, P50, P90] from OU distribution conditioned on current deviation
- Use case: Deviation from mean triggers safety stock adjustment; large deviations trigger investigation

### 9. Business Rules
- Non-negativity: max(0, forecast)
- Mean anchor: Forecast must converge toward μ_LR as horizon increases
- Deviation alert: If |dev(t)| > 2σ → flag for planner review (unusual deviation)

### 10. Evaluation

| Granularity | WMAPE Target | Mean Convergence Check | Bias Alert |
|---|---|---|---|
| Daily | < 22% | Forecast approaches μ_LR at horizon ≥ 2×HL | \|Bias\| > 10% |
| Weekly | < 18% | Same | \|Bias\| > 8% |
| Monthly | < 15% | Same | \|Bias\| > 7% |
| Quarterly | < 12% | Same | \|Bias\| > 6% |
| Yearly | < 10% | Same | \|Bias\| > 5% |

### 11. Exception Handling
- Alert: ADF p rises above 0.10 (non-stationary → reclassify); half-life estimate > extended window (too slow to confirm reversion); mean level shift detected (structural break → Step Change behavior)

### 12. Reclassification

| Condition | Target | Holding Period |
|---|---|---|
| ADF p ≥ 0.10 for 4 periods | Flat (if no trend) or Upward/Downward Trend | 4 periods |
| FFT cycle detected on residuals | Cyclical Trend | 2 cycles |
| Structural break detected | Step Change (Behavior) | Immediate |

### 13. Review Cadence
- Monthly automated stationarity check; quarterly reversion speed calibration; annual full re-evaluation

---

*End of Dimension 5 · Trend Pattern*
*5 Segments Complete · T1 through T5*
