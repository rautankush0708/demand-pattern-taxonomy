# Accuracy Metrics
## Performance · Horizons · Safety Stock

---

> This module defines how we measure the "Truth" of our forecasts and how we translate those forecasts into supply chain parameters like Safety Stock.

---

## 11. Accuracy Metrics

```
WMAPE   = Σ|Forecast_t − Actual_t| / Σ Actual_t × 100
Bias    = Σ(Forecast_t − Actual_t) / Σ Actual_t × 100
MAE     = (1/n) × Σ|Forecast_t − Actual_t|
RMSE    = sqrt[(1/n) × Σ(Forecast_t − Actual_t)²]
MASE    = MAE_model / MAE_naive
Pinball = α × (Actual − Q_α)_+  +  (1−α) × (Q_α − Actual)_+
Coverage= P(Actual ∈ [P10, P90])   Target: 80%

Tracking Signal:
  TS(t) = Σ(Forecast_t − Actual_t) / MAE
  |TS| > 4 → systematic bias → reforecast required
```

**WMAPE Targets by Granularity:**

| Segment Type | Daily | Weekly | Monthly | Quarterly | Yearly |
|---|---|---|---|---|---|
| High Volume / Stable | < 15% | < 12% | < 10% | < 8% | < 6% |
| Medium Volume | < 22% | < 18% | < 15% | < 12% | < 10% |
| Low Volume | MAE primary | MAE primary | MASE < 1.2 | MASE < 1.2 | MASE < 1.2 |
| Ultra Low | MAE < 1 unit | MAE < 2 units | MAE < 5 units | MAE < 10 units | MAE < 20 units |

**Bias Alert Thresholds:**

| Granularity | High Volume | Medium | Low Volume | Ultra Low |
|---|---|---|---|---|
| Daily | > 5% | > 8% | > 12% | > 20% |
| Weekly | > 5% | > 8% | > 12% | > 20% |
| Monthly | > 4% | > 7% | > 10% | > 15% |
| Quarterly | > 4% | > 6% | > 8% | > 12% |
| Yearly | > 3% | > 5% | > 6% | > 10% |

---

## 12. Retraining & Backtesting Reference

| Granularity | Retraining | Latency | Train Window | Test Window |
|---|---|---|---|---|
| Daily | Daily | T+4 hours | 180 days | 30 days |
| Weekly | Weekly | T+1 day | 52 weeks | 13 weeks |
| Monthly | Monthly | T+2 days | 24 months | 6 months |
| Quarterly | Quarterly | T+3 days | 8 quarters | 2 quarters |
| Yearly | Annually | T+7 days | All available | 1 year |

---

## 13. Forecast Horizon Reference

| Granularity | Short | Medium | Long | Max Reliable |
|---|---|---|---|---|
| Daily | 1–7 days | 8–30 days | 31–90 days | 90 days |
| Weekly | 1–4 weeks | 5–13 weeks | 14–26 weeks | 52 weeks |
| Monthly | 1–3 months | 4–6 months | 7–12 months | 18 months |
| Quarterly | 1 quarter | 2 quarters | 3–4 quarters | 6 quarters |
| Yearly | 1 year | 2 years | 3 years | 5 years |

---

## 14. Safety Stock Formula

```
SS = z × σ_forecast_error × √(Lead_time + Review_period)
σ_forecast_error = RMSE over backtesting period
z service level factors:
  z = 1.28 → 90% service level
  z = 1.65 → 95% service level
  z = 2.05 → 98% service level
  z = 2.33 → 99% service level
```
