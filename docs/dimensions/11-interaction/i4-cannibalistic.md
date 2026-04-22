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
