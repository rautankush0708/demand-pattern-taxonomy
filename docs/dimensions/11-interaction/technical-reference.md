# PART 0 — FORMULA & THRESHOLD REFERENCE

## Dimension 11 · Interaction Pattern

---

---

## 0.1 Core Segmentation Metrics

### A. Cross-SKU Pearson Correlation
> Measures direction and strength of demand co-movement

```
r(A,B) = Σ[(d_A(t) − d̄_A)(d_B(t) − d̄_B)] / [n × σ_A × σ_B]

Strong complementary:  r > +0.50
Weak complementary:    +0.20 < r ≤ +0.50
Independent:           |r| ≤ 0.20
Weak substitution:     −0.30 ≤ r < −0.20
Strong substitution:   r < −0.30
```

| Granularity | Estimation Window | Min Overlap |
|---|---|---|
| **Daily** | 180-day rolling | ≥ 90 co-active days |
| **Weekly** | 52-week rolling | ≥ 26 co-active weeks |
| **Monthly** | 24-month rolling | ≥ 12 co-active months |
| **Quarterly** | 8-quarter rolling | ≥ 4 co-active quarters |
| **Yearly** | 3-year rolling | ≥ 2 co-active years |

---

### B. Substitution Rate
> Quantifies demand shift from SKU_B to SKU_A during SKU_B stockout

```
Substitution event: Period where SKU_B is OOS (stockout)
                    AND SKU_A demand spikes > 1.5σ above baseline

sub_rate(A←B) = mean(d_A during SKU_B OOS) / mean(d_A during SKU_B available) − 1

Significant substitution: sub_rate > 0.20 AND confirmed in ≥ 3 OOS events
```

| Granularity | OOS Threshold | Min OOS Events |
|---|---|---|
| **Daily** | Inventory on hand = 0 for ≥ 1 day | ≥ 3 events |
| **Weekly** | Inventory = 0 for ≥ 1 day in week | ≥ 3 events |
| **Monthly** | Inventory = 0 for ≥ 3 days in month | ≥ 3 events |
| **Quarterly** | Inventory = 0 in quarter | ≥ 2 events |
| **Yearly** | Inventory = 0 in year | ≥ 2 events |

---

### C. Cannibalism Coefficient
> Measures demand lost from one SKU per unit gained by another

```
Cannibalism coefficient:
  δ = ΔQ_B / ΔQ_A   (demand lost from B per unit gained by A)

Estimated via regression:
  ΔQ_B(t) = α + δ × ΔQ_A(t) + β × controls(t) + ε(t)

Significant cannibalism: p < 0.05 for δ AND |δ| > 0.15 AND δ < 0
```

| Granularity | Estimation Window | Min Correlated Periods |
|---|---|---|
| **Daily** | 180-day | ≥ 60 overlapping days |
| **Weekly** | 52-week | ≥ 26 overlapping weeks |
| **Monthly** | 24-month | ≥ 12 overlapping months |
| **Quarterly** | 8-quarter | ≥ 4 overlapping quarters |
| **Yearly** | 3-year | ≥ 2 overlapping years |

---

### D. Granger Causality Test
> Confirms causal direction for Halo and Complementary classifications

```
Granger causality from X to Y:
  H0: X does NOT Granger-cause Y
  Test: Does adding lagged X improve prediction of Y beyond Y's own lags?

  F-statistic on added regressors; reject H0 at p < 0.05
  Granger-causes confirmed: p < 0.05
  Halo direction: hero Granger-causes follower (not reverse)
```

| Granularity | Max Lag Tested | Min History |
|---|---|---|
| **Daily** | 30 days | ≥ 180 days |
| **Weekly** | 13 weeks | ≥ 52 weeks |
| **Monthly** | 6 months | ≥ 24 months |
| **Quarterly** | 4 quarters | ≥ 8 quarters |
| **Yearly** | 2 years | ≥ 5 years |

---

### E. Portfolio Conservation Check
> Ensures interaction models produce internally consistent portfolio totals

```
Total portfolio demand:  D_total(t) = Σ d_i(t) for all active SKUs
Portfolio conservation:  |Σ F_i(t) − D_total_forecast(t)| / D_total_forecast(t) < 10%

Cannibalism check: d_A(t) + d_B(t) ≤ M(t)   [market size constraint]
  If violated → rescale proportionally to historical share
```

---

## 0.2 Classification Decision Rules

```
STEP 1: Compute cross-SKU Pearson r for all paired SKUs
  |r| < 0.20 for all pairs → INDEPENDENT

STEP 2: For r < −0.20 (negative correlation)
  Run substitution detection (Section 0.1B)
  sub_rate > 0.20 in ≥ 3 OOS events → SUBSTITUTION
  Else: run cannibalism test (Section 0.1C)
  |δ| > 0.15; p < 0.05; δ < 0 → CANNIBALISTIC

STEP 3: For r > +0.20 (positive correlation)
  Run Granger causality (Section 0.1D)
  Hero Granger-causes follower (p < 0.05) → HALO
  Mutual Granger causality OR VAR → COMPLEMENTARY

STEP 4: Apply portfolio conservation check
  Adjust cannibalistic and halo forecasts to maintain consistency
```

---

## 0.3 Rolling Window Reference

| Window | Daily | Weekly | Monthly | Quarterly | Yearly |
|---|---|---|---|---|---|
| Short | 7 days | 4 weeks | 2 months | 1 quarter | 1 year |
| Medium | 30 days | 8 weeks | 3 months | 2 quarters | 2 years |
| Long | 90 days | 13 weeks | 6 months | 3 quarters | 3 years |
| Extended | 180 days | 26 weeks | 12 months | 4 quarters | 4 years |
| DL Lookback | 180 days | 52 weeks | 24 months | 8 quarters | 5 years |

---

## 0.4 Accuracy Metrics

```
WMAPE   = Σ|Forecast_t − Actual_t| / Σ Actual_t × 100
Bias    = Σ(Forecast_t − Actual_t) / Σ Actual_t × 100
MAE     = (1/n) × Σ|Forecast_t − Actual_t|

Interaction-specific:
  Portfolio Consistency = |Σ Forecast_i − Σ Actual_i| / Σ Actual_i × 100  (Target < 5%)
  Substitution Accuracy = |sub_rate_predicted − sub_rate_actual| / sub_rate_actual × 100
  Cannibalism Coefficient Stability = CV(δ across rolling windows)  (Target < 0.30)
  Halo Granger p-value              (Target < 0.05 maintained)
  WMAPE Improvement vs Independent  (Target > 5% for non-independent segments)
```

---

## 0.5 Retraining & Backtesting Reference

| Granularity | Retraining | Latency | Train | Test |
|---|---|---|---|---|
| **Daily** | Daily | T+4 hours | 180 days | 30 days |
| **Weekly** | Weekly | T+1 day | 52 weeks | 13 weeks |
| **Monthly** | Monthly | T+2 days | 24 months | 6 months |
| **Quarterly** | Quarterly | T+3 days | 8 quarters | 2 quarters |
| **Yearly** | Annually | T+7 days | All available | 1 year |

---
