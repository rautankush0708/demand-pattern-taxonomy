## RC2 · Irregular

### 1. Definition
Predicts demand for SKUs that recur but with inconsistent timing (0.20 ≤ CV_IAT < 0.60), requiring probabilistic timing models rather than deterministic interval forecasting.

### 2. Detailed Description
- **Applicable scenarios:** Project-based demand, opportunistic purchasing, variable-cycle MRO, demand driven by unpredictable triggers

### 5. Model Strategy

#### 5.1 Probabilistic Timing Model
```
P(demand in period t) = f(periods since last demand, season, trigger signals)
Estimate via Logistic Regression or Survival model:
  Hazard function: h(t|s) = h_0(t) × e^{β × covariates(s)}
  where s = periods since last demand event
  h_0(t) = baseline hazard (empirically estimated from IAT distribution)
```

### 6. Model Families

#### 6.1 ML: XGBoost (timing classifier) + rolling non-zero mean (quantity)
#### 6.2 Statistical: Croston/SBA (α = 0.10–0.20)
#### 6.3 Survival model: Cox proportional hazard for timing; OLS for quantity

### Evaluation

| Granularity | Timing AUC | Quantity MAE | Bias Alert |
|---|---|---|---|
| Daily | > 0.70 | < 20% of mean | |Bias| > 12% |
| Weekly | > 0.70 | < 18% | |Bias| > 10% |
| Monthly | > 0.68 | < 15% | |Bias| > 8% |
| Quarterly | > 0.65 | < 12% | |Bias| > 6% |
| Yearly | > 0.65 | < 10% | |Bias| > 5% |

---

