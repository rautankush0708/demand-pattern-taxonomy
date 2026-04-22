## SG4 · Lagged Signal
### 1. Definition
Predicts demand for SKUs where the observed demand signal consistently lags true consumption by a known duration (L > granularity threshold), requiring lag correction to align the demand signal with actual consumption timing before modelling.

### 5. Model Strategy

#### 5.1 Signal Lag Correction
```
d_corrected(t) = d_observed(t + L)   [shift observed signal back by lag L]
OR equivalently:
d_true(t) = d_observed(t − L)   [true consumption at t = observed orders at t+L]

Forecast at t for horizon h:
  F_true(t+h) = Model(d_corrected history)
  F_observed(t+h) = F_true(t + h + L)   [shift forecast forward by lag]
```

| Granularity | Lag Estimation | Min Lag Observations |
|---|---|---|
| Daily | Cross-correlation of orders vs POS; Mean(L) estimated | ≥ 30 paired observations |
| Weekly | Order-to-POS lag; Mean(L) in weeks | ≥ 20 paired observations |
| Monthly | Order-to-consumption lag | ≥ 12 paired observations |
| Quarterly | Order-to-use lag | ≥ 8 paired observations |
| Yearly | Long-cycle lag | ≥ 3 paired observations |

### 6. Model Families

#### 6.1 ML: LightGBM on lag-corrected series + lag features
#### 6.2 Statistical: Standard model on corrected series; ARIMAX with lag structure

### Evaluation

| Granularity | Lag Estimate Accuracy | WMAPE on Corrected | Bias Alert |
|---|---|---|---|
| Daily | Lag within ±2 days | Per behavior standard | \|Bias\| > 8% |
| Weekly | Lag within ±1 week | Per behavior standard | \|Bias\| > 7% |
| Monthly | Lag within ±1 month | Per behavior standard | \|Bias\| > 6% |
| Quarterly | Lag within ±1 quarter | Per behavior standard | \|Bias\| > 5% |
| Yearly | Lag within ±6 months | Per behavior standard | \|Bias\| > 4% |

---
