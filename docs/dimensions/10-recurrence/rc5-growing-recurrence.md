## RC5 · Growing Recurrence

### 1. Definition
Predicts demand for SKUs where the frequency of demand events is increasing over time (Mann-Kendall on RR(t); p < 0.05; Z > 0), indicating growing customer adoption or expanding use cases.

### 5. Model Strategy

#### 5.1 Growing Recurrence Rate Model
```
RR_forecast(t+h) = RR(t) × (1 + β_RR × h)
where β_RR > 0 (growing rate slope)
Cap: RR_max = 1.0 (demand every period — cannot exceed)
```

### 6. Model Families

#### 6.1 ML: LightGBM with RR trend features
#### 6.2 Statistical: ETS(A,A,N) on RR(t) with growth cap

### Evaluation

| Granularity | RR Forecast Accuracy | WMAPE | Under-Forecast Alert |
|---|---|---|---|
| Daily | RR within ±20% | < 30% | Bias < −12% |
| Weekly | RR within ±18% | < 25% | Bias < −10% |
| Monthly | RR within ±15% | < 22% | Bias < −8% |
| Quarterly | RR within ±12% | < 18% | Bias < −6% |
| Yearly | RR within ±10% | < 15% | Bias < −5% |
