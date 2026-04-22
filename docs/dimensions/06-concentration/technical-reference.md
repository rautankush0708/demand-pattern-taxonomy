
# PART 0 — FORMULA & THRESHOLD REFERENCE
## Concentration Pattern Specific

---

## 0.1 Core Segmentation Metrics

### A. Demand Concentration Index (DCI)
> Measures how unevenly demand is distributed across periods in a cycle

**General Formula:**
```
DCI = Σ [d_p / Σ d_p × (d_p / Σ d_p)]   = Σ s_p²
where s_p = share of period p in total cycle demand
DCI = Σ s_p²

DCI range: 1/n (perfectly uniform) to 1.0 (all demand in one period)
n = number of periods in cycle

Normalised DCI: DCI_norm = (DCI − 1/n) / (1 − 1/n)
DCI_norm = 0 → perfectly uniform
DCI_norm = 1 → all demand in one period
```

| Granularity | Cycle Length (n) | Uniform DCI | Peaked DCI | Formula |
|---|---|---|---|---|
| **Daily** | 7 (weekly cycle) | DCI_norm < 0.15 | DCI_norm > 0.40 | Σ(d_day / Σ d_week)² |
| **Weekly** | 52 (annual cycle) | DCI_norm < 0.10 | DCI_norm > 0.30 | Σ(d_week / Σ d_year)² |
| **Monthly** | 12 (annual cycle) | DCI_norm < 0.10 | DCI_norm > 0.30 | Σ(d_month / Σ d_year)² |
| **Quarterly** | 4 (annual cycle) | DCI_norm < 0.15 | DCI_norm > 0.40 | Σ(d_quarter / Σ d_year)² |
| **Yearly** | Available history | DCI_norm < 0.15 | DCI_norm > 0.40 | Σ(d_year / Σ d_total)² |

---

### B. Gini Coefficient of Demand Distribution
> Alternative concentration measure — more sensitive to inequality across the full distribution

**General Formula:**
```
Gini = 1 − 2 × Σ [F(d_p) × (d_p / Σ d_p)]
where F(d_p) = cumulative frequency up to period p (sorted ascending)

Gini = 0 → perfect equality (uniform demand)
Gini = 1 → perfect inequality (all demand in one period)

Uniform:   Gini < 0.20
Moderate:  0.20 ≤ Gini < 0.50
Peaked:    Gini ≥ 0.50
```

| Granularity | Uniform | Moderate | Peaked |
|---|---|---|---|
| **Daily** | Gini < 0.20 | 0.20–0.50 | > 0.50 |
| **Weekly** | Gini < 0.15 | 0.15–0.40 | > 0.40 |
| **Monthly** | Gini < 0.15 | 0.15–0.40 | > 0.40 |
| **Quarterly** | Gini < 0.20 | 0.20–0.50 | > 0.50 |
| **Yearly** | Gini < 0.20 | 0.20–0.50 | > 0.50 |

---

### C. Modality Detection
> Identifies number of distinct demand peaks within a cycle

**General Formula:**
```
Demand distribution histogram over cycle periods:
  Peak = local maximum where d_p > d_{p-1} AND d_p > d_{p+1}
  Peak is significant if d_p > mean_demand × 1.5

Modes:
  0–1 peaks → Uniform or single-peaked → classify further by DCI
  1 peak    → Peaked
  2 peaks   → Bi-Modal
  3+ peaks  → Multi-Modal

Skewness test (additional check for Skewed classification):
  Pearson skewness = 3 × (mean − median) / std
  |skewness| > 0.5 → demand distribution is skewed
  skewness > 0     → right-skewed (demand concentrated early in cycle)
  skewness < 0     → left-skewed (demand concentrated late in cycle)
```

| Granularity | Significant Peak Threshold | Bi-Modal Gap Requirement |
|---|---|---|
| **Daily** | d_p > μ_daily × 1.5 | Peaks separated by ≥ 2 days |
| **Weekly** | d_p > μ_weekly × 1.5 | Peaks separated by ≥ 4 weeks |
| **Monthly** | d_p > μ_monthly × 1.5 | Peaks separated by ≥ 3 months |
| **Quarterly** | d_p > μ_quarterly × 1.5 | Peaks separated by ≥ 1 quarter |
| **Yearly** | d_p > μ_yearly × 1.5 | Peaks separated by ≥ 1 year |

---

### D. Seasonal Index Dispersion
> Measures how spread the seasonal indices are — high dispersion = concentrated demand

**Formula:**
```
SI(p) = μ_period_p / μ_overall   [multiplicative seasonal index]
SI_dispersion = std(SI) / mean(SI) = CV of seasonal indices

Low dispersion:  SI_dispersion < 0.20 → Uniform
High dispersion: SI_dispersion > 0.50 → Peaked / Multi-Modal
```

| Granularity | Uniform Threshold | Concentrated Threshold |
|---|---|---|
| **Daily** | SI_dispersion < 0.20 | SI_dispersion > 0.50 |
| **Weekly** | SI_dispersion < 0.15 | SI_dispersion > 0.40 |
| **Monthly** | SI_dispersion < 0.15 | SI_dispersion > 0.40 |
| **Quarterly** | SI_dispersion < 0.20 | SI_dispersion > 0.50 |
| **Yearly** | SI_dispersion < 0.20 | SI_dispersion > 0.50 |

---

## 0.2 Concentration Classification Decision Rules

```
STEP 1: Compute DCI_norm and Gini over most recent full cycle
STEP 2: Detect number of significant peaks (modality)
STEP 3: Compute skewness of demand distribution

Classification rules:

  DCI_norm < threshold AND Gini < threshold → UNIFORM
  DCI_norm > threshold AND 1 significant peak → PEAKED
  DCI_norm > threshold AND 2 significant peaks → BI-MODAL
  DCI_norm > threshold AND 3+ significant peaks → MULTI-MODAL
  DCI_norm moderate AND |skewness| > 0.5 → SKEWED

Note: Must use ≥ 2 full cycles to compute reliable DCI and Gini
      Single-cycle estimates are noisy — flag as provisional
```

---

## 0.3 Seasonal Index Formulas

```
Multiplicative SI: SI(p) = μ_period_p / μ_overall
Additive SI:       SI(p) = μ_period_p − μ_overall

Deseasonalised demand: d_adj(t) = d(t) / SI(period_of_t)   [multiplicative]

Seasonal index update (exponential smoothing):
  SI_new(p) = γ × (d(t) / l_t) + (1−γ) × SI_old(p)
  γ ∈ [0.05, 0.20] — low γ preserves stable seasonal pattern

ACF(lag) > 2/√n → Significant seasonality at that lag
Minimum 2 full cycles for reliable SI estimation
```

---

## 0.4 Rolling Window Reference

| Window Name | Daily | Weekly | Monthly | Quarterly | Yearly |
|---|---|---|---|---|---|
| **Short** | 7 days | 4 weeks | 2 months | 1 quarter | 1 year |
| **Medium** | 30 days | 8 weeks | 3 months | 2 quarters | 2 years |
| **Long** | 90 days | 13 weeks | 6 months | 3 quarters | 3 years |
| **Extended** | 180 days | 26 weeks | 12 months | 4 quarters | 4 years |
| **Full Cycle** | 365 days | 52 weeks | 12 months | 4 quarters | Varies |
| **DL Lookback** | 365 days | 104 weeks | 36 months | 12 quarters | 5 years |

---

## 0.5 Accuracy Metric Formulas

```
WMAPE   = Σ|Forecast_t − Actual_t| / Σ Actual_t × 100
Bias    = Σ(Forecast_t − Actual_t) / Σ Actual_t × 100
MAE     = (1/n) × Σ|Forecast_t − Actual_t|

Peak Period WMAPE (critical for Peaked / Bi-Modal / Multi-Modal):
  Peak_WMAPE = Σ_{peak periods}|Forecast_t − Actual_t| / Σ_{peak periods} Actual_t × 100
  Target: Peak_WMAPE < 1.5 × overall WMAPE target

Trough Period WMAPE:
  Trough_WMAPE = Σ_{trough periods}|Forecast_t − Actual_t| / Σ_{trough periods} Actual_t × 100

Pinball(α,t) = α × (Actual_t − Q_α)     if Actual_t ≥ Q_α
             = (1−α) × (Q_α − Actual_t)  if Actual_t < Q_α
Coverage = Actuals within [P10, P90] / n × 100  (Target: 80%)
```

---

## 0.6 Retraining & Backtesting Reference

| Granularity | Retraining | Latency | Backtest Train | Backtest Test |
|---|---|---|---|---|
| **Daily** | Daily | T+4 hours | 365 days (full cycle) | 30 days |
| **Weekly** | Weekly | T+1 day | 104 weeks (2 cycles) | 13 weeks |
| **Monthly** | Monthly | T+2 days | 36 months (3 cycles) | 6 months |
| **Quarterly** | Quarterly | T+3 days | 12 quarters (3 cycles) | 2 quarters |
| **Yearly** | Annually | T+7 days | All available | 1 year |

---

# PART 1 — SEGMENT TEMPLATES

---

