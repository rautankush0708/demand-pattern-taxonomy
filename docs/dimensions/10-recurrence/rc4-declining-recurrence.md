## RC4 · Declining Recurrence
### 1. Definition
Predicts demand for SKUs where the frequency of demand events is decreasing over time (Mann-Kendall on RR(t); p < 0.05; Z < 0), indicating a category or customer relationship in decline.

### 5. Model Strategy

#### 5.1 Recurrence Rate Trend Model
```
RR(t) = demand events in rolling window / window length
Forecast recurrence rate: RR_forecast(t+h) = RR(t) × (1 + β_RR × h)
where β_RR < 0 (declining rate slope)
Quantity per event: Historical non-zero mean (stable)
Demand forecast: RR_forecast(t+h) × quantity_per_event
```

### 6. Model Families

#### 6.1 ML: LightGBM with RR trend features + time index
#### 6.2 Statistical: ETS on RR(t) series with additive negative trend

### Evaluation

| Granularity | RR Forecast Accuracy | WMAPE | Over-Forecast Alert |
|---|---|---|---|
| Daily | RR within ±20% | < 30% | Bias > +12% |
| Weekly | RR within ±18% | < 25% | Bias > +10% |
| Monthly | RR within ±15% | < 22% | Bias > +8% |
| Quarterly | RR within ±12% | < 18% | Bias > +6% |
| Yearly | RR within ±10% | < 15% | Bias > +5% |

---
