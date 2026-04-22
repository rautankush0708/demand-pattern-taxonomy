
# PART 0 — FORMULA & THRESHOLD REFERENCE
## Driver Pattern Specific

---

## 0.1 Core Detection Metrics

### A. Seasonality Detection — ACF & FFT
> Identifies repeating calendar-driven demand cycles

**Autocorrelation Formula:**
```
ACF(lag k) = Σ[(d_t − d̄)(d_{t−k} − d̄)] / Σ[(d_t − d̄)²]

Significant seasonality: ACF(lag k) > 2 / √n
where n = number of observations

FFT Peak: Seasonal period p = 1 / f_peak
where f_peak = dominant frequency in FFT spectrum
Minimum 2 full cycles required for reliable detection
```

| Granularity | Primary Lag | Secondary Lag | Tertiary Lag | Min Obs |
|---|---|---|---|---|
| **Daily** | lag 7 (weekly) | lag 30 (monthly) | lag 365 (annual) | ≥ 365 days |
| **Weekly** | lag 52 (annual) | lag 13 (quarterly) | lag 4 (monthly) | ≥ 104 weeks |
| **Monthly** | lag 12 (annual) | lag 3 (quarterly) | lag 6 (bi-annual) | ≥ 24 months |
| **Quarterly** | lag 4 (annual) | lag 2 (bi-annual) | — | ≥ 8 quarters |
| **Yearly** | — | — | — | Not applicable |

**Seasonal Index Formula:**
```
Multiplicative SI(p) = μ_period_p / μ_overall
Additive      SI(p) = μ_period_p − μ_overall

Use multiplicative when SI varies proportionally with demand level
Use additive when SI is constant regardless of demand level

Deseasonalised demand: d_adj(t) = d(t) / SI(p)   [multiplicative]
                                  = d(t) − SI(p)   [additive]
```

---

### B. Event Correlation Detection
> Identifies demand spikes linked to discrete external events

**Uplift Formula:**
```
Event Uplift = (Mean demand in event window) / (Mean demand in baseline window) − 1

Event window:    T−w to T+w around event date (w = event influence window)
Baseline window: Same periods excluding event influence zones

Significant event effect: Uplift > 0.20 (20% above baseline) AND p < 0.05 (t-test)
```

| Granularity | Event Window (w) | Baseline Window |
|---|---|---|
| **Daily** | ±7 days | Same 14-day window excluding prior 3 event occurrences |
| **Weekly** | ±2 weeks | Same 4-week window prior year non-event |
| **Monthly** | ±1 month | Same month prior years non-event |
| **Quarterly** | ±1 quarter | Same quarter prior years |
| **Yearly** | ±6 months | Prior years baseline |

---

### C. Promotional Uplift Detection
> Quantifies demand increase attributable to promotions

**Promotional Uplift Formula:**
```
Promo Uplift = (Demand during promotion) / (Baseline demand same period) − 1

Baseline = deseasonalised rolling mean excluding promo periods
Significant promo effect: Uplift > 0.15 (15%) AND statistically significant (p < 0.05)

Post-promo dip factor: Dip = (Mean demand T+1 to T+w post-promo) / Baseline − 1
Total net uplift = Gross uplift + Dip factor (often negative)
```

| Granularity | Promo Window | Post-Promo Dip Window |
|---|---|---|
| **Daily** | Duration of promotion | 7 days post-promotion end |
| **Weekly** | Duration of promotion | 2 weeks post-promotion |
| **Monthly** | Duration of promotion | 1 month post-promotion |
| **Quarterly** | Duration of promotion | 1 quarter post-promotion |
| **Yearly** | Duration of promotion | 6 months post-promotion |

---

### D. Weather Correlation Detection
> Measures demand correlation with meteorological variables

**Correlation Formula:**
```
Pearson r = Σ[(d_t − d̄)(w_t − w̄)] / [√Σ(d_t − d̄)² × √Σ(w_t − w̄)²]

Significant weather effect: |r| > 0.30 AND p < 0.05
Lag correlation: Test r at lag 0, 1, 2, 3 periods — use max |r| lag
```

| Granularity | Weather Variables Tested | Lag Range |
|---|---|---|
| **Daily** | Temperature, rainfall, humidity, wind speed, UV index | lag 0–3 days |
| **Weekly** | Weekly mean temperature, total rainfall, frost days | lag 0–2 weeks |
| **Monthly** | Monthly mean temperature, total rainfall, sunshine hours | lag 0–1 month |
| **Quarterly** | Seasonal mean temperature, total rainfall | lag 0–1 quarter |
| **Yearly** | Annual mean temperature, rainfall deviation from norm | lag 0 |

---

### E. Customer Concentration — Herfindahl-Hirschman Index
> Measures demand concentration across customers

**HHI Formula:**
```
HHI = Σ(s_i)²
where s_i = share of customer i in total demand (as decimal)
HHI range: 0 (perfectly fragmented) to 1 (single customer monopoly)

Customer Driven threshold: HHI > 0.60
Top-3 customer share > 60% of total demand
```

| Granularity | Computation Window | Update Frequency |
|---|---|---|
| **Daily** | Rolling 90-day | Weekly |
| **Weekly** | Rolling 52-week | Monthly |
| **Monthly** | Rolling 12-month | Monthly |
| **Quarterly** | Rolling 4-quarter | Quarterly |
| **Yearly** | Rolling 3-year | Annually |

---

### F. Supply Constraint Detection
> Identifies periods where observed demand is below true demand due to stockouts

**Lost Sales Estimation Formula:**
```
Lost Sales Flag: Period flagged if:
  (1) Inventory on hand = 0 for ≥ 1 day in period AND
  (2) Demand in following period exceeds rolling mean by > 1σ (pent-up demand signal)

Unconstrained Demand Estimate:
  d_unconstrained(t) = d_observed(t) / Fill_Rate(t)
  where Fill_Rate(t) = Units shipped / Units ordered (if order data available)
  or Fill_Rate(t) = 1 − (Stockout days / Total days in period)

Supply Constrained flag: Stockout events > 2 in rolling window
```

| Granularity | Rolling Window | Stockout Flag Threshold |
|---|---|---|
| **Daily** | 90-day | > 5 stockout days in window |
| **Weekly** | 52-week | > 4 stockout weeks in window |
| **Monthly** | 12-month | > 2 stockout months in window |
| **Quarterly** | 4-quarter | > 1 stockout quarter in window |
| **Yearly** | 3-year | > 1 stockout year in window |

---

## 0.2 Driver Detection Decision Rules

```
For each SKU, test all drivers independently and stack all that apply:

D1 SEASONAL:          ACF(seasonal lag) > 2/√n   AND   ≥ 2 full cycles available
D2 EVENT DRIVEN:      Event Uplift > 20%           AND   p < 0.05
D3 PROMOTIONAL:       Promo Uplift > 15%           AND   p < 0.05
D4 WEATHER DRIVEN:    |Pearson r| > 0.30           AND   p < 0.05
D5 CUSTOMER DRIVEN:   HHI > 0.60                   OR    Top-3 share > 60%
D6 SUPPLY CONSTRAINED: Stockout events > threshold AND   unconstrained demand differs

If no driver detected → Driver = NONE (pure baseline demand; no external cause)
Multiple drivers can apply simultaneously → stack all flagged drivers
```

---

## 0.3 Rolling Window Reference

| Window Name | Daily | Weekly | Monthly | Quarterly | Yearly |
|---|---|---|---|---|---|
| **Short** | 7 days | 4 weeks | 2 months | 1 quarter | 1 year |
| **Medium** | 30 days | 8 weeks | 3 months | 2 quarters | 2 years |
| **Long** | 90 days | 13 weeks | 6 months | 3 quarters | 3 years |
| **Extended** | 180 days | 26 weeks | 12 months | 4 quarters | 4 years |
| **Full Year** | 365 days | 52 weeks | 12 months | 4 quarters | 5 years |
| **DL Lookback** | 90 days | 52 weeks | 24 months | 8 quarters | 5 years |

---

## 0.4 Accuracy Metric Formulas

```
WMAPE   = Σ|Forecast_t − Actual_t| / Σ Actual_t × 100

Bias    = Σ(Forecast_t − Actual_t) / Σ Actual_t × 100

Uplift Accuracy = |Predicted Uplift − Actual Uplift| / Actual Uplift × 100

Event Detection Rate = Events correctly flagged / Total events × 100  (Target > 90%)

Pinball(α,t) = α × (Actual_t − Q_α)     if Actual_t ≥ Q_α
             = (1−α) × (Q_α − Actual_t)  if Actual_t < Q_α

Coverage = Actuals within [P10, P90] / Total Periods × 100  (Target: 80%)
```

---

## 0.5 Retraining & Backtesting Reference

| Granularity | Retraining | Latency | Backtest Train | Backtest Test |
|---|---|---|---|---|
| **Daily** | Daily | T+4 hours | 180 days | 30 days |
| **Weekly** | Weekly | T+1 day | 52 weeks | 13 weeks |
| **Monthly** | Monthly | T+2 days | 24 months | 6 months |
| **Quarterly** | Quarterly | T+3 days | 8 quarters | 2 quarters |
| **Yearly** | Annually | T+7 days | All available | 1 year |

---

# PART 1 — SEGMENT TEMPLATES

---

