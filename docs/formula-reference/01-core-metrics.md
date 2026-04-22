# Core Metrics
## Frequency & Variability Foundations

---

> This module covers the fundamental dimensions of demand classification: **Frequency** (ADI) and **Quantity Variability** (CV²).

---

## 1. ADI — Average Demand Interval

> Measures demand **frequency**

```
ADI = Total Periods in Window / Number of Non-Zero Demand Periods
```

| Granularity | Formula | Threshold | Interpretation |
|---|---|---|---|
| Daily | Total Days / Days with Demand > 0 | 1.10 | < 1.10 = Regular |
| Weekly | Total Weeks / Weeks with Demand > 0 | 1.32 | < 1.32 = Regular |
| Monthly | Total Months / Months with Demand > 0 | 1.25 | < 1.25 = Regular |
| Quarterly | Total Quarters / Quarters with Demand > 0 | 1.20 | < 1.20 = Regular |
| Yearly | Total Years / Years with Demand > 0 | 1.10 | < 1.10 = Regular |

**Rules:**
- Use rolling window (see Section 9)
- Exclude structural zeros (supply failures, system downtime)
- ADI = 1.0 → demand every period; ADI = 4.0 → demand every 4th period

---

## 2. CV² — Squared Coefficient of Variation

> Measures demand **quantity variability**

```
CV² = (σ_nz / μ_nz)²
σ_nz = std dev of non-zero demand periods
μ_nz = mean of non-zero demand periods
CV² Threshold = 0.49 at all granularities
```

**Rules:**
- Always compute on **non-zero periods only**
- CV² < 0.49 → Smooth quantity; CV² ≥ 0.49 → Variable quantity

---

## 3. Behavior Classification Matrix

```
                    ADI
             < Threshold    ≥ Threshold
           ┌─────────────┬───────────────┐
CV² < 0.49 │   STABLE    │  INTERMITTENT │
           ├─────────────┼───────────────┤
CV² ≥ 0.49 │   ERRATIC   │     LUMPY     │
           └─────────────┴───────────────┘
```

**Sub-segment rules:**
| Boundary | Rule |
|---|---|
| Stable vs Slow Mover | Volume < 5th portfolio percentile |
| Intermittent vs Pulsed | CV of inter-arrival time < 0.30 |
| Stable vs Trending | Mann-Kendall p < 0.05 |
| Any vs Step Change | Chow/CUSUM significant |
