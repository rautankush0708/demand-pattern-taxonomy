## SG5 · Amplified

### 1. Definition
Predicts demand for SKUs where the observed upstream order signal is amplified relative to true end-consumer demand due to the bullwhip effect (AR > 1.5), requiring demand sensing correction and end-to-end signal reconstruction to recover true consumption signal.

### 2. Detailed Description
- **Applicable scenarios:** Multi-tier supply chains where distributor or wholesaler ordering amplifies variability; categories with large distributor safety stocks and batch ordering behaviour

### 5. Model Strategy

#### 5.1 Bullwhip De-amplification
```
Amplification Ratio: AR = Var(Orders_upstream) / Var(d_downstream)

De-amplification:
  d_true(t) = d_upstream(t) / AR + (1 − 1/AR) × d_downstream_estimate(t)

If downstream (POS/consumption) data available:
  Use d_downstream directly — highest fidelity signal

If only upstream order data available:
  Apply exponential smoothing to orders: d_smoothed(t) = α × d(t) + (1−α) × d(t-1)
  α = 2 / (AR + 1)   [de-amplification smoothing factor derived from AR]
```

| Granularity | AR Estimation Window | De-amplification Method |
|---|---|---|
| Daily | 90-day rolling | Exponential smoothing + POS comparison |
| Weekly | 52-week rolling | ETS smoothing on orders + POS if available |
| Monthly | 24-month rolling | ARIMA fitted on downstream; orders smoothed |
| Quarterly | 8-quarter rolling | Moving average de-amplification |
| Yearly | 3-year rolling | Long-run average de-amplification |

### 6. Model Families

#### 6.1 ML: LightGBM on de-amplified demand series
#### 6.2 DL: TFT with both upstream and downstream signals (if available)
#### 6.3 Statistical: State space model — observes upstream orders; estimates downstream state

### Evaluation

| Granularity | AR Estimate Accuracy | De-amplified WMAPE | Downstream Alignment | Bias Alert |
|---|---|---|---|---|
| Daily | AR within ±0.3 | < 25% | r(deamplified, POS) > 0.70 | |Bias| > 12% |
| Weekly | AR within ±0.3 | < 22% | r > 0.70 | |Bias| > 10% |
| Monthly | AR within ±0.2 | < 18% | r > 0.65 | |Bias| > 8% |
| Quarterly | AR within ±0.2 | < 15% | r > 0.65 | |Bias| > 6% |
| Yearly | AR within ±0.2 | < 12% | r > 0.60 | |Bias| > 5% |
