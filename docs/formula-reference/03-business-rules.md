# Business Rules
## Lifecycle · History · Data Quality

---

> This module defines the "Guardrails" of the taxonomy: when a product is considered new, when history is sufficient for testing, and how we handle missing or zero data.

---

## 6. Lifecycle Boundaries

| Stage | Daily | Weekly | Monthly | Quarterly | Yearly |
|---|---|---|---|---|---|
| Cold Start | < 56 days | < 8 weeks | < 2 months | < 1 quarter | < 1 year |
| New Launch | 56–112 days | 8–16 weeks | 2–4 months | 1–2 quarters | 1–2 years |
| Growth | Slope p < 0.05 (+) | Same | Same | Same | Same |
| Mature | Slope p ≥ 0.10 | Same | Same | Same | Same |
| Decline | Slope p < 0.05 (−) | Same | Same | Same | Same |
| Phasing Out | Discontinuation flag | Same | Same | Same | Same |
| Inactive | 0 demand ≥ 91 days | ≥ 13 weeks | ≥ 3 months | ≥ 1 quarter | ≥ 1 year |

---

## 7. Minimum History Requirements

| Requirement | Daily | Weekly | Monthly | Quarterly | Yearly |
|---|---|---|---|---|---|
| Cold Start | < 56 days | < 8 weeks | < 2 months | < 1 quarter | < 1 year |
| Min for ADI | ≥ 30 days | ≥ 13 weeks | ≥ 6 months | ≥ 4 quarters | ≥ 3 years |
| Min non-zero for CV² | ≥ 10 days | ≥ 8 weeks | ≥ 6 months | ≥ 4 quarters | ≥ 3 years |
| Min for Trend | ≥ 90 days | ≥ 13 weeks | ≥ 6 months | ≥ 4 quarters | ≥ 3 years |
| Min for Seasonality | ≥ 365 days | ≥ 104 weeks | ≥ 24 months | ≥ 8 quarters | ≥ 3 years |

---

## 8. Zero Period Definition

| Granularity | Zero Period | Structural Zero | Random Zero |
|---|---|---|---|
| Daily | Day where net demand = 0 | Supply failure / system outage → exclude from ADI | No customer demand → include in ADI |
| Weekly | Week where net demand = 0 | Confirmed stockout week → exclude | No demand → include |
| Monthly | Month where net demand = 0 | Supply constraint month → exclude | No demand → include |
| Quarterly | Quarter where net demand = 0 | External disruption → exclude | No demand → include |
| Yearly | Year where net demand = 0 | Delisting gap → exclude | No demand → include |

---

## 9. Rolling Window Reference

| Window | Daily | Weekly | Monthly | Quarterly | Yearly |
|---|---|---|---|---|---|
| Short | 7 days | 4 weeks | 2 months | 1 quarter | 1 year |
| Medium | 30 days | 8 weeks | 3 months | 2 quarters | 2 years |
| Long | 90 days | 13 weeks | 6 months | 3 quarters | 3 years |
| Extended | 180 days | 26 weeks | 12 months | 4 quarters | 4 years |
| Full Year | 365 days | 52 weeks | 12 months | 4 quarters | 5 years |
| DL Lookback | 90 days | 52 weeks | 24 months | 8 quarters | 5 years |

**Formulas:**
```
Rolling Mean:   μ_w(t) = (1/w) × Σ d_{t-i}   for i = 0 to w-1
Rolling Std:    σ_w(t) = sqrt[(1/w) × Σ (d_{t-i} − μ_w)²]
Rolling CV²:    CV²_w(t) = [σ_w(t) / μ_w(t)]²   (non-zero only)
Rolling Slope:  β_w(t) = Σ[(i − ī)(d_{t-i} − d̄)] / Σ[(i − ī)²]
Decay Weight:   w_i = exp(−i / half_life) / Σ exp(−j / half_life)
```
