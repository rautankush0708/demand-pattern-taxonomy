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
| Daily | Per behavior std | < 30% | ±15% | \|Bias\| > 12% |
| Weekly | Per behavior std | < 25% | ±12% | \|Bias\| > 10% |
| Monthly | Per behavior std | < 22% | ±10% | \|Bias\| > 8% |
| Quarterly | Per behavior std | < 18% | ±8% | \|Bias\| > 6% |
| Yearly | Per behavior std | < 15% | ±6% | \|Bias\| > 5% |

---
