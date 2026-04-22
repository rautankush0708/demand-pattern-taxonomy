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

# PART 1 — SEGMENT TEMPLATES

