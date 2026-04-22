# Statistical Tests
## Trend · Breaks · Seasonality

---

> This module defines the quantitative tests for detecting non-random patterns in demand series, including trends, level shifts, and seasonal cycles.

---

## 4. Mann-Kendall Trend Test

> Non-parametric test for monotonic trend

```
S = Σ_{j>i} sign(d_j − d_i)
Var(S) = n(n−1)(2n+5) / 18
Z = (S−1)/√Var(S)  if S > 0
  = 0              if S = 0
  = (S+1)/√Var(S)  if S < 0

Significant trend:  p < 0.05
No trend:           p ≥ 0.10
Watch zone:         0.05 ≤ p < 0.10 → monitor 2 more periods
```

| Granularity | Rolling Window | Slope Unit | Damping φ (Decline) |
|---|---|---|---|
| Daily | 90-day | Units/day | 0.90 |
| Weekly | 13-week | Units/week | 0.85 |
| Monthly | 6-month | Units/month | 0.80 |
| Quarterly | 4-quarter | Units/quarter | 0.75 |
| Yearly | 3-year | Units/year | 0.70 |

---

## 5. Structural Break Detection

| Granularity | Test | Window | Trigger |
|---|---|---|---|
| Daily | CUSUM | 30-day | CUSUM > 5σ |
| Weekly | Chow + CUSUM | 8-week | p < 0.05 |
| Monthly | Chow Test | 4-month | p < 0.05 |
| Quarterly | Chow Test | 2-quarter | p < 0.05 |
| Yearly | Chow Test | 2-year | p < 0.05 |

---

## 10. Seasonality Detection

| Granularity | Primary Lag | Secondary Lag | Detection |
|---|---|---|---|
| Daily | lag 7 (weekly) | lag 365 (annual) | FFT + ACF |
| Weekly | lag 52 (annual) | lag 13 (quarterly) | FFT + ACF |
| Monthly | lag 12 (annual) | lag 3 (quarterly) | ACF |
| Quarterly | lag 4 (annual) | lag 2 (bi-annual) | ACF |
| Yearly | — | — | Not applicable |

```
Significant seasonality: ACF(lag) > 2/√n
Seasonal Index (SI):     SI(p) = μ_period_p / μ_overall
Deseasonalised:          d_adj(t) = d(t) / SI(period_of_t)
Minimum cycles needed:   2 full cycles
```
