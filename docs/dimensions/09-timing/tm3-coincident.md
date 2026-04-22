## TM3 · Coincident
### 1. Definition
Predicts demand for SKUs where demand moves simultaneously with an identifiable external trigger signal (max CCF at k = 0), requiring real-time external signal integration for contemporaneous demand forecasting.

### 2. Detailed Description
- **Applicable scenarios:** Weather-sensitive categories (temperature = same-day demand), real-time event demand, POS-driven replenishment, same-day consumption-purchase correlation

### 5. Model Strategy

#### 5.1 Feature Engineering
```
contemporaneous_trigger(t) = trigger(t)   [same-period trigger value]
CCF(0) = contemporaneous correlation strength
```

| Granularity | Contemporaneous Features |
|---|---|
| Daily | Same-day temperature, mobility index, event flag, POS data feed (same day) |
| Weekly | Same-week weather index, same-week event flag, same-week POS |
| Monthly | Same-month economic index, same-month category trend |
| Quarterly | Same-quarter GDP component, same-quarter category trend |
| Yearly | Same-year macro indicator, same-year demographic index |

### 6. Model Families

#### 6.1 ML: LightGBM with contemporaneous trigger
#### 6.2 DL: TFT with real-time covariate integration
#### 6.3 Statistical: ARIMAX(k=0 external regressor)

### Evaluation

| Granularity | WMAPE Target | Trigger R² | Bias Alert |
|---|---|---|---|
| Daily | < 20% | > 0.30 | \|Bias\| > 8% |
| Weekly | < 17% | > 0.25 | \|Bias\| > 7% |
| Monthly | < 14% | > 0.20 | \|Bias\| > 6% |
| Quarterly | < 11% | > 0.18 | \|Bias\| > 5% |
| Yearly | < 9% | > 0.15 | \|Bias\| > 4% |

---
