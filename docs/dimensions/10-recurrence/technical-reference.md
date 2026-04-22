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

# PART 1 — SEGMENT TEMPLATES

