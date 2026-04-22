# PART 0 — SHARED FORMULA REFERENCE
## Dimensions 9–12

---

## 0.1 Timing Pattern Metrics

### A. Lead-Lag Correlation
```
Cross-correlation at lag k:
  CCF(k) = Σ[(d_t − d̄)(trigger_{t−k} − trigger̄)] / [n × σ_d × σ_trigger]

Leading:    Max CCF at k < 0 (demand moves before trigger)
Lagging:    Max CCF at k > 0 (demand moves after trigger)
Coincident: Max CCF at k = 0 (demand moves with trigger)

Significant lag: |CCF(k)| > 2/√n
```

| Granularity | Lag Range Tested | Trigger Variables |
|---|---|---|
| **Daily** | k = −30 to +30 days | Competitor price, weather, news sentiment, mobility index |
| **Weekly** | k = −13 to +13 weeks | Category trend, promotional activity, macroeconomic index |
| **Monthly** | k = −6 to +6 months | GDP, industrial output, consumer confidence |
| **Quarterly** | k = −4 to +4 quarters | GDP growth, capital expenditure |
| **Yearly** | k = −2 to +2 years | Macro economic cycle, population growth |

### B. Demand Arrival vs Expected Timing
```
Expected timing: t_expected = estimated from historical pattern or trigger date
Actual timing:   t_actual = date of demand event

Timing deviation: dev_timing = t_actual − t_expected (periods)

Leading:     Mean(dev_timing) < −1 period (demand arrives early)
Lagging:     Mean(dev_timing) > +1 period (demand arrives late)
Coincident:  |Mean(dev_timing)| ≤ 1 period (demand on time)
Deferred:    Mean(dev_timing) > granularity-specific threshold (demand significantly delayed)
Accelerated: Mean(dev_timing) < −granularity-specific threshold (demand significantly pulled forward)
```

| Granularity | Deferred Threshold | Accelerated Threshold |
|---|---|---|
| **Daily** | dev > +7 days | dev < −7 days |
| **Weekly** | dev > +3 weeks | dev < −3 weeks |
| **Monthly** | dev > +2 months | dev < −2 months |
| **Quarterly** | dev > +1 quarter | dev < −1 quarter |
| **Yearly** | dev > +1 year | dev < −1 year |

---

## 0.2 Recurrence Pattern Metrics

### A. Inter-Arrival Time Statistics
```
Inter-arrival time: IAT_i = t_i − t_{i-1} (periods between consecutive demand events)
Mean IAT: μ_IAT = (1/n) × Σ IAT_i
Std IAT:  σ_IAT = sqrt[(1/(n-1)) × Σ(IAT_i − μ_IAT)²]
CV_IAT:   CV_IAT = σ_IAT / μ_IAT

Regular:   CV_IAT < 0.20 (highly consistent intervals)
Irregular: 0.20 ≤ CV_IAT < 0.60 (variable but recurring)
One Time:  n = 1 (single demand event observed)
```

### B. Recurrence Rate Trend
```
Recurrence rate at time t: RR(t) = demand events in rolling window / window length
Trend in RR: Mann-Kendall test on RR(t) series

Declining Recurrence: Mann-Kendall p < 0.05; Z < 0 (demand frequency decreasing)
Growing Recurrence:   Mann-Kendall p < 0.05; Z > 0 (demand frequency increasing)
```

| Granularity | Rolling Window for RR | Trend Window |
|---|---|---|
| **Daily** | 90-day | 180-day MK test |
| **Weekly** | 26-week | 52-week MK test |
| **Monthly** | 12-month | 24-month MK test |
| **Quarterly** | 4-quarter | 8-quarter MK test |
| **Yearly** | 3-year | 5-year MK test |

---

## 0.3 Interaction Pattern Metrics

### A. Cross-SKU Correlation
```
Pearson correlation between SKU_A and SKU_B demand:
  r(A,B) = Σ[(d_A(t) − d̄_A)(d_B(t) − d̄_B)] / [n × σ_A × σ_B]

Complementary: r > +0.50 (demand moves together)
Substitution:  r < −0.30 AND SKU_B stockout → SKU_A spike
Cannibalistic: r < −0.30 AND SKU_A grows → SKU_B shrinks
Halo:          r > +0.40 AND causal direction (hero → follower)
Independent:   |r| < 0.20
```

### B. Substitution Detection
```
Substitution event: Period where SKU_B is OOS (stockout)
                    AND SKU_A demand spikes > 1.5σ above baseline

Substitution rate: sub_rate = mean(d_A during SKU_B OOS) / mean(d_A during SKU_B available) − 1

Significant substitution: sub_rate > 0.20 AND confirmed in ≥ 3 OOS events
```

### C. Cannibalism Detection
```
Cannibalism coefficient: δ = ΔQ_B / ΔQ_A (demand lost from B per unit gained by A)

Estimated via regression:
  ΔQ_B(t) = α + δ × ΔQ_A(t) + β × controls(t) + ε(t)
  δ < 0 → A cannibalises B; |δ| = cannibalism rate
  Significant: p < 0.05 for δ AND |δ| > 0.15
```

---

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

d_true_estimate(t) = unconstrained demand (Section D6 — Supply Constrained driver)
```

### C. Bullwhip Amplification
```
Bullwhip effect: Order variance amplifies upstream from retail to distributor to manufacturer

Amplification ratio: AR = Var(Orders_upstream) / Var(Orders_downstream)
AR > 1.5 → Amplified signal (upstream orders more variable than downstream demand)
AR < 1.2 → Clean signal (minimal amplification)

Measured at each supply chain tier where data available
```

### D. Lag Between Signal and Consumption
```
Signal lag: L = t_order − t_consumption (periods between order and actual use)
Measured from order data vs consumption/POS data

Lagged Signal: Mean(L) > granularity threshold
  Daily: L > 3 days
  Weekly: L > 1 week
  Monthly: L > 1 month
  Quarterly: L > 1 quarter
  Yearly: L > 6 months
```

---

## 0.5 Shared Rolling Window Reference

| Window | Daily | Weekly | Monthly | Quarterly | Yearly |
|---|---|---|---|---|---|
| Short | 7 days | 4 weeks | 2 months | 1 quarter | 1 year |
| Medium | 30 days | 8 weeks | 3 months | 2 quarters | 2 years |
| Long | 90 days | 13 weeks | 6 months | 3 quarters | 3 years |
| Extended | 180 days | 26 weeks | 12 months | 4 quarters | 4 years |
| DL Lookback | 180 days | 52 weeks | 24 months | 8 quarters | 5 years |

---

## 0.6 Shared Accuracy Metrics

```
WMAPE = Σ|Forecast_t − Actual_t| / Σ Actual_t × 100
Bias  = Σ(Forecast_t − Actual_t) / Σ Actual_t × 100
MAE   = (1/n) × Σ|Forecast_t − Actual_t|
MASE  = MAE_model / MAE_naive
Pinball(α) = α × (Actual − Q_α)_+ + (1−α) × (Q_α − Actual)_+
Coverage  = P(Actual ∈ [P10,P90])   Target: 80%
```

---

# DIMENSION 9 — TIMING PATTERN

---

---

# PART 1 — SEGMENT TEMPLATES

