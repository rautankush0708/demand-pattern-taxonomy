## TM2 · Lagging
### 1. Definition
Predicts demand for SKUs where demand follows an identifiable external trigger signal with a consistent delay, enabling causal forecasting by detecting the trigger and applying the known lag to project demand.

### 2. Detailed Description
- **Applicable scenarios:** Aftermarket parts (follow equipment sales by lead time), consumables following capital equipment installation, re-order triggered by prior delivery cycle, categories driven by downstream production schedule
- **Boundaries:**

| Granularity | Detection | Lag Time |
|---|---|---|
| Daily | Max CCF at k > 0; |CCF| > 2/√n | k = 3–30 days after trigger |
| Weekly | Max CCF at k > 0; |CCF| > 2/√n | k = 1–13 weeks after |
| Monthly | Max CCF at k > 0; |CCF| > 2/√n | k = 1–6 months after |
| Quarterly | Max CCF at k > 0; |CCF| > 2/√n | k = 1–4 quarters after |
| Yearly | Max CCF at k > 0; |CCF| > 2/√n | k = 1–2 years after |

### 5. Model Strategy

#### 5.1 Feature Engineering
```
lagged_trigger(t) = trigger(t − k*)   [past value of trigger at optimal lag]
```

| Granularity | Lagged Trigger Features | Lag Features |
|---|---|---|
| Daily | trigger(t−3 to t−30 days), optimal lag k*, CCF strength | Lag stability CV(k*), lag drift indicator |
| Weekly | trigger(t−1 to t−13 weeks) | k*, CCF, lag drift |
| Monthly | trigger(t−1 to t−6 months) | k*, CCF |
| Quarterly | trigger(t−1 to t−4 quarters) | k*, CCF |
| Yearly | trigger(t−1 to t−2 years) | k*, CCF |

### 6. Model Families

#### 6.1 ML: LightGBM with lagged trigger features
#### 6.2 DL: TFT — lagged triggers as past observed covariates
#### 6.3 Statistical: ARIMAX with lagged exogenous variable

```
d(t) = α + β × trigger(t − k*) + ARIMA residual
k* = argmax |CCF(k)| for k > 0
```

### 7. Ensemble — same structure as TM1 Leading (by CCF strength)

### 8–10. Evaluation

| Granularity | WMAPE Target | Lag R² | Bias Alert |
|---|---|---|---|
| Daily | < 22% | > 0.25 | \|Bias\| > 10% |
| Weekly | < 18% | > 0.25 | \|Bias\| > 8% |
| Monthly | < 15% | > 0.20 | \|Bias\| > 7% |
| Quarterly | < 12% | > 0.18 | \|Bias\| > 6% |
| Yearly | < 10% | > 0.15 | \|Bias\| > 5% |

### 11–13. Standard protocols + quarterly lag recalibration

---
