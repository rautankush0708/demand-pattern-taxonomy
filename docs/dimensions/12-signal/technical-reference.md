## 0.4 Signal Pattern Metrics

### A. Signal Noise Ratio
```
Signal-to-Noise Ratio (SNR):
  Signal component: Trend + Seasonal = fitted values from STL decomposition
  Noise component:  Residual from STL decomposition

  SNR = Var(Signal) / Var(Noise)
  SNR > 4.0 → Pure Signal (noise < 20% of total variance)
  SNR 1.0–4.0 → Moderate noise
  SNR < 1.0 → Noisy (noise > 50% of total variance)
```

### B. Distortion Detection
```
Distortion factors: Supply constraints, returns, order cancellations, reporting errors
Distortion index: DI = |d_observed(t) − d_true_estimate(t)| / d_true_estimate(t)

Distorted: DI > 0.15 in > 20% of periods
Pure: DI < 0.10 in > 90% of periods

d_true_estimate(t) = unconstrained demand
```

### C. Bullwhip Amplification
```
Bullwhip effect: Order variance amplifies upstream from retail to distributor to manufacturer

Amplification ratio: AR = Var(Orders_upstream) / Var(Orders_downstream)
AR > 1.5 → Amplified signal (upstream orders more variable than downstream demand)
AR < 1.2 → Clean signal (minimal amplification)
```

### D. Lag Between Signal and Consumption
```
Signal lag: L = t_order − t_consumption (periods between order and actual use)

Lagged Signal: Mean(L) > granularity threshold
  Daily: L > 3 days
  Weekly: L > 1 week
  Monthly: L > 1 month
  Quarterly: L > 1 quarter
  Yearly: L > 6 months
```

---

# PART 1 — SEGMENT TEMPLATES

