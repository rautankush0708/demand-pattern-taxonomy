## T2 · Downward Trend
### 1. Definition
Predicts demand for SKUs with a statistically confirmed negative demand slope, where damped trend-aware models are required to prevent systematic over-forecasting and inventory accumulation in declining demand environments.

### 2. Detailed Description
- **Applicable scenarios:** Declining categories, distribution losses, market share erosion, ageing products, price-driven volume decline
- **Boundaries:**

| Granularity | Detection Condition | Slope | Min History |
|---|---|---|---|
| Daily | Mann-Kendall p < 0.05; Z < 0; 90-day window | β₁ < 0 | ≥ 56 days |
| Weekly | Mann-Kendall p < 0.05; Z < 0; 13-week window | β₁ < 0 | ≥ 8 weeks |
| Monthly | Mann-Kendall p < 0.05; Z < 0; 6-month window | β₁ < 0 | ≥ 4 months |
| Quarterly | Mann-Kendall p < 0.05; Z < 0; 4-quarter window | β₁ < 0 | ≥ 2 quarters |
| Yearly | Mann-Kendall p < 0.05; Z < 0; 3-year window | β₁ < 0 | ≥ 2 years |

- **Key demand characteristics:** Falling mean demand, negative slope, possibly rising CV² as volume shrinks, approaching zero asymptotically (damped model) or rapidly (steep decline)
- **Differentiation from other models:** Unlike Flat, slope is confirmed negative; unlike Reverting, demand is not bouncing back to a long-run mean but continuing downward; unlike Phasing Out lifecycle, decline is market-driven not supply-side-decided

### 3. Business Impact
- **Primary risk (over-forecast):** Systematic inventory accumulation — the dominant risk; write-off and obsolescence
- **Primary risk (under-forecast):** Minimal — over-forecast risk dominates entirely for this segment
- **Strategic importance:** Medium — primary goal is inventory run-down management, not service level optimisation

### 4. Priority Level
🟠 Tier 2 — Over-forecast prevention dominates; damped models and conservative forecasting are the primary tools.

### 5. Model Strategy Overview

#### 5.1 Zero-Demand Handling (Hurdle)
- Active event threshold: P(demand > 0) > 0.50 — declining SKUs approach zero over time
- Classifier: Logistic Regression with trend and time-to-zero features
- Regressor: LightGBM with negative slope features + damped ETS
- Fallback: Flat rolling mean (conservative — prevents over-extrapolation of decline)

#### 5.2 Analogue / Similarity Logic
- Number of analogues: k = 3 (SKUs that previously showed similar downward trend — now Inactive or Phasing Out)
- Similarity criteria: Category, slope magnitude (%/period), volume at decline start
- Temporal decay: weight = exp(−age / half-life)

| Granularity | Half-Life |
|---|---|
| Daily | 60 days |
| Weekly | 8 weeks |
| Monthly | 4 months |
| Quarterly | 2 quarters |
| Yearly | 1.5 years |

#### 5.3 Feature Engineering

| Granularity | Trend Features | Rolling Features | Decline Context Features |
|---|---|---|---|
| Daily | β₁_90day (negative), relative slope, periods since peak demand, slope acceleration (Δβ₁) | 7, 30, 90-day mean, std | Distribution loss rate, competitor gain flag, price increase flag |
| Weekly | β₁_13week (negative), relative slope, weeks since peak | 4, 8, 13, 26-week mean, std | Distribution point loss, category decline index |
| Monthly | β₁_6month (negative), relative slope, months since peak | 2, 3, 6, 12-month mean, std | Category decline index |
| Quarterly | β₁_4quarter (negative), relative slope, quarters since peak | 1, 2, 4-quarter mean, std | Category index |
| Yearly | β₁_3year (negative), relative slope, years since peak | 1, 2, 3-year mean, std | Market share index |

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM with downward bias correction
- Configuration: Objective = reg:squarederror; Metric = WMAPE, MAE; over-forecast penalty applied
- Over-forecast correction: If bias > 0 for 3 consecutive periods → apply −β₁ × 1.5 × h correction
- When to use: Primary model

#### 6.2 Deep Learning (DL)
- Architectures: TFT (attention captures declining trend)
- Not recommended for steep decline SKUs — model complexity unjustified as volume approaches zero
- When to use: Only if history > 1 year AND decline is mild (relative slope < 2%/period)

#### 6.3 Statistical / Time Series Models
- Architectures: ETS(A,A,N) with **damped trend** — critical for downward trend to prevent forecast crossing zero

**Damped Holt's Linear Trend:**
```
Level:    l_t = α × d_t + (1−α)(l_{t-1} + phi × b_{t-1})
Trend:    b_t = β × (l_t − l_{t-1}) + (1−β) × phi × b_{t-1}
Forecast: F(t+h) = l_t + (phi + phi² + ... + phi^h) × b_t
phi < 1 → trend fades over horizon (prevents forecast going negative)
```

| Granularity | Mild Slope phi | Moderate Slope phi | Strong Slope phi |
|---|---|---|---|
| Daily | 0.95 | 0.90 | 0.85 |
| Weekly | 0.90 | 0.85 | 0.80 |
| Monthly | 0.85 | 0.80 | 0.75 |
| Quarterly | 0.80 | 0.75 | 0.70 |
| Yearly | 0.75 | 0.70 | 0.65 |

- When to use: Always included — damped trend is essential safety model for decline

#### 6.4 Baseline / Fallback Model
- Fallback triggers: Slope reversal detected (reclassification triggered)
- Fallback model: Rolling mean (conservative hold — no trend extrapolation)
- Logging & alerting: Alert if fallback triggered AND over-forecast bias > 10%

### 7. Ensemble & Weighting

#### 7.2 Dynamic Weight Schedule

| Decline Stage (Relative Slope) | LightGBM | ETS(damped) | TFT |
|---|---|---|---|
| Mild (< 2%/period) | 55% | 30% | 15% |
| Moderate (2–5%/period) | 50% | 45% | 5% |
| Strong (> 5%/period) | 40% | 60% | 0% |

- Weight determination: Error-inverse on over-forecast-penalised WMAPE

### 8. Uncertainty Quantification
- Method: Quantile regression
- Output: [P10, P50, P90] — P10 for minimum buy; P50 for base; P90 for maximum exposure
- Use case: Inventory run-down planning using P10; obsolescence risk using P90

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Decline cap: max(forecast, 0) — damped model prevents negative; hard floor at zero
- Ceiling: min(forecast, prior rolling mean) — forecast must not drift upward
- Anti-accumulation rule: If bias > +10% for 3 periods → apply additional −β₁ × 0.5 × h correction
- Manual overrides: Delisting date; clearance promotion; distribution reinstatement plan
- Alignment: Forecast cannot exceed current stock on hand + confirmed inbound

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | WMAPE Target | Over-Forecast Bias Alert | Tracking Signal Alert | Coverage |
|---|---|---|---|---|
| Daily | < 28% | Bias > +10% | TS > +4 | 80% P10–P90 |
| Weekly | < 22% | Bias > +10% | TS > +4 | 80% P10–P90 |
| Monthly | < 18% | Bias > +8% | TS > +4 | 80% P10–P90 |
| Quarterly | < 15% | Bias > +6% | TS > +4 | 80% P10–P90 |
| Yearly | < 12% | Bias > +5% | TS > +4 | 80% P10–P90 |

#### 10.2 Backtesting Protocol

| Granularity | Train | Test | Over-Forecast Check |
|---|---|---|---|
| Daily | 180 days | 30 days | Confirm no systematic over-forecast |
| Weekly | 52 weeks | 13 weeks | Confirm no systematic over-forecast |
| Monthly | 24 months | 6 months | Confirm no systematic over-forecast |
| Quarterly | 8 quarters | 2 quarters | Confirm no systematic over-forecast |
| Yearly | All available | 1 year | Confirm no systematic over-forecast |

#### 10.3 Retraining

| Granularity | Cadence | Latency |
|---|---|---|
| Daily | Daily | T+4 hours |
| Weekly | Weekly | T+1 day |
| Monthly | Monthly | T+2 days |
| Quarterly | Quarterly | T+3 days |
| Yearly | Annually | T+7 days |

### 11. Exception Handling & Overrides
- Auto-detect: Slope reversal (Z positive) for 3 consecutive periods → reclassification trigger; forecast > prior rolling mean → immediate over-forecast alert; demand reaches zero for 3+ consecutive periods → Inactive reclassification trigger
- Manual override: Commercial decision to reinvest; distribution plan reversal
- Override expiration: Single cycle

### 12. Reclassification

| Condition | Target Segment | Holding Period | Transition |
|---|---|---|---|
| Mann-Kendall p > 0.10 for 4 periods | Flat | 4 periods | Soft blend |
| Mann-Kendall p < 0.05; Z > 0 for 3 periods | Upward Trend | 3 periods | Soft blend |
| Zero demand ≥ Inactive threshold | Flat → Lifecycle: Inactive | Immediate | Hard switch |

### 13. Review Cadence
- Per cycle automated dashboard with over-forecast alert; bi-weekly obsolescence review; quarterly full re-evaluation

---
