## B5 · Trending

### 1. Definition
Predicts demand for SKUs with a statistically confirmed directional slope (either positive or negative) that sits within the Stable/Slow Mover CV²-ADI quadrant, requiring trend-aware models to avoid systematic directional bias.

### 2. Detailed Description
- **Applicable scenarios:** Gradually growing or declining product lines without discrete lifecycle reclassification trigger, slow burn trends, gradual market share shifts
- **Boundaries:**

| Granularity | ADI | CV² | Trend Condition |
|---|---|---|---|
| Daily | < 1.10 | < 0.49 | Mann-Kendall p < 0.05 on 90-day window |
| Weekly | < 1.32 | < 0.49 | Mann-Kendall p < 0.05 on 13-week window |
| Monthly | < 1.25 | < 0.49 | Mann-Kendall p < 0.05 on 6-month window |
| Quarterly | < 1.20 | < 0.49 | Mann-Kendall p < 0.05 on 4-quarter window |
| Yearly | < 1.10 | < 0.49 | Mann-Kendall p < 0.05 on 3-year window |

- **Key demand characteristics:** Consistent directional movement, low variance around the trend, regular demand occurrence
- **Differentiation:** Unlike Stable, a trend exists; unlike Growth/Decline Lifecycle, this is behavioral — the Lifecycle segment may be Mature but demand still has a trend component

### 3. Business Impact
- **Primary risk (over-forecast):** Over-forecast on downward trending SKUs — inventory build
- **Primary risk (under-forecast):** Under-forecast on upward trending SKUs — stockouts
- **Strategic importance:** Medium-high — trend direction determines inventory strategy

### 4. Priority Level
🟠 Tier 2 — Trend models prevent systematic directional bias; medium complexity.

### 5. Model Strategy Overview

#### 5.1 Hurdle
- Threshold: P(demand > 0) > 0.75 — trending SKUs are regularly demanded
- Regressor: LightGBM / ETS with trend component

#### 5.2 Feature Engineering

| Granularity | Rolling Windows | Trend Features |
|---|---|---|
| Daily | 7, 30, 90, 180-day | β_90day slope, slope direction flag, periods of consistent direction |
| Weekly | 4, 8, 13, 26-week | β_13week slope, slope direction flag |
| Monthly | 2, 3, 6, 12-month | β_6month slope |
| Quarterly | 1, 2, 4-quarter | β_4quarter slope |
| Yearly | 1, 2, 3-year | β_3year slope |

### 6. Model Families

#### 6.1 ML: LightGBM with slope and direction features
- Regressor: reg:squarederror | WMAPE, RMSE

#### 6.2 DL: TFT — captures trend via attention mechanism

| Granularity | Lookback | Features |
|---|---|---|
| Daily | 180 days | 12 |
| Weekly | 52 weeks | 10 |
| Monthly | 24 months | 8 |
| Quarterly | 8 quarters | 6 |
| Yearly | 5 years | 5 |

#### 6.3 Statistical: ETS(A,A,N) — additive trend; damped if downward (phi = 0.85)

#### 6.4 Fallback: Rolling mean + slope extrapolation; alert if fallback > 15%

### 7. Ensemble

| History | LightGBM | TFT | ETS |
|---|---|---|---|
| Up to 6 months equiv. | 70% | 0% | 30% |
| 6–12 months equiv. | 60% | 30% | 10% |
| > 12 months equiv. | 50% | 40% | 10% |

### 8. Uncertainty Quantification
- Quantile regression: [P10, P50, P90]
- Upward trend: P75 for safety stock; downward trend: P50 for base (conservative)

### 9. Business Rules
- Capping: Upward — min(forecast, 2 × rolling max); Downward — max(forecast, 0) with decay cap
- Manual overrides: Commercial confirmation of trend continuation/reversal

### 10. Evaluation

| Granularity | WMAPE Target | Bias Alert (directional) |
|---|---|---|
| Daily | < 25% | Directional Bias > 12% |
| Weekly | < 20% | Directional Bias > 10% |
| Monthly | < 18% | Directional Bias > 8% |
| Quarterly | < 15% | Directional Bias > 6% |
| Yearly | < 12% | Directional Bias > 5% |

### 11. Exception Handling
- Alert: Trend reversal for 3 consecutive periods → evaluate reclassification to Stable

### 12. Reclassification

| Condition | Target | Holding Period |
|---|---|---|
| Trend p > 0.10 for 4 periods | Stable | 4 periods |
| CV² rises above 0.49 | Erratic | 8 periods |
| ADI rises above threshold | Lumpy or Intermittent | 8 periods |

### 13. Review Cadence
- Per cycle with slope monitor; bi-weekly review; quarterly full re-evaluation

---

