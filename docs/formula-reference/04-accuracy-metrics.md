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

---

## 15. Performance Monitoring Indicators
> Comprehensive suite for daily model tracking, bias detection, and stability analysis.

### Required Data Fields
To calculate these indicators, the following data points must be captured daily:
| Field | Description |
|---|---|
| **SKU ID** | Unique identifier for the product/location. |
| **Date** | The forecast period being evaluated. |
| **Forecast** | Predicted demand for the period. |
| **Actual** | Observed demand for the period. |
| **Prev Forecast** | Forecast generated in the previous model run. |

---

### 15.1 Daily Forecast Error
**Definition:** Measures the raw difference between actual demand and forecasted demand for a single period.
**Formula:** `Error = Actual - Forecast`
**Example:**
| SKU ID | Forecast | Actual | Error |
|---|---|---|---|
| SKU001 | 100 | 110 | +10 |

### 15.2 Absolute Percentage Error (Daily APE)
**Definition:** Measures the percentage error for a single forecast observation, relative to actuals.
**Formula:** `APE = | (Actual - Forecast) / Actual | x 100`
**Example:**
| SKU ID | Forecast | Actual | APE |
|---|---|---|---|
| SKU001 | 90 | 100 | 10% |

### 15.3 Daily Forecast Accuracy
**Definition:** Represents the inverted error as an accuracy percentage (0-100%).
**Formula:** `Accuracy = 1 - ( |Actual - Forecast| / Actual )`
**Example:**
| SKU ID | Forecast | Actual | Accuracy |
|---|---|---|---|
| SKU001 | 90 | 100 | 90% |

### 15.4 Forecast Revision Indicator
**Definition:** Measures the change in forecast between two consecutive model runs. Large revisions indicate model instability.
**Formula:** `Revision = Forecast(today) - Forecast(previous)`
**Example:**
| SKU ID | Forecast Today | Forecast Previous | Revision |
|---|---|---|---|
| SKU001 | 120 | 100 | +20 |

### 15.5 Forecast Drift Indicator
**Definition:** Measures long-term change in forecasts across a sliding time window (e.g., 7 days).
**Formula:** `Drift = Forecast(t) - Forecast(t - n)`
**Example:**
| SKU ID | Day | Forecast | Drift |
|---|---|---|---|
| SKU001 | Day 1 | 100 | — |
| SKU001 | Day 7 | 130 | +30 |

### 15.6 Rolling Bias
**Definition:** Measures systematic over-forecasting or under-forecasting across a rolling window of N periods.
**Formula:** `Rolling Bias = Σ(Forecast - Actual) / N`
**Example:**
| SKU ID | Period | Forecast | Actual | Bias |
|---|---|---|---|---|
| SKU001 | 7-day | 105 | 100 | +5.0 |

### 15.7 Rolling MAD (Mean Absolute Deviation)
**Definition:** Measures the average absolute forecast error over a rolling window.
**Formula:** `MAD = Σ|Actual - Forecast| / N`
**Example:**
| SKU ID | Abs Error D1 | Abs Error D2 | Abs Error D3 | MAD |
|---|---|---|---|---|
| SKU001 | 10 | 5 | 10 | 8.33 |

### 15.8 Rolling Tracking Signal
**Definition:** Monitors forecast bias over time to identify persistent trends.
**Formula:** `Tracking Signal = Cumulative Forecast Error (CFE) / MAD`
**Control Limits:** `-4 <= Tracking Signal <= +4`
*   **TS > +4**: Persistent under-forecasting.
*   **TS < -4**: Persistent over-forecasting.

### 15.9 Forecast Revision %
**Definition:** Measures percentage change between forecasts to detect large model adjustments.
**Formula:** `Revision % = ((Forecast(today) - Forecast(prev)) / Forecast(prev)) x 100`
**Example:**
| SKU ID | Forecast Today | Forecast Previous | Revision % |
|---|---|---|---|
| SKU001 | 120 | 100 | +20% |

### 15.10 Forecast Volatility
**Definition:** Measures variability in forecasts across recent days. High volatility indicates unstable forecasting behavior.
**Formula:** `Volatility = std(Forecast over last N days)`
**Example:**
| SKU ID | Forecast Day 1 | Forecast Day 2 | Forecast Day 3 | Volatility |
|---|---|---|---|---|
| SKU001 | 100 | 120 | 105 | 10.4 |

### 15.11 Cumulative Forecast Error (CFE)
**Definition:** Measures total forecast bias over time.
**Formula:** `CFE = Σ(Actual - Forecast)`
*   **Positive CFE**: Under-forecasting trend.
*   **Negative CFE**: Over-forecasting trend.
**Example:**
| SKU ID | Day 1 Error | Day 2 Error | Day 3 Error | CFE |
|---|---|---|---|---|
| SKU001 | +10 | -5 | +10 | +15 |

### 15.12 Rolling MAPE
**Definition:** Measures average percentage forecast error over a rolling window.
**Formula:** `MAPE = (1/N) x Σ| (Actual - Forecast) / Actual | x 100`
**Example:**
| SKU ID | APE Day 1 | APE Day 2 | APE Day 3 | MAPE |
|---|---|---|---|---|
| SKU001 | 10% | 5% | 7% | 7.33% |

---

## 16. Model-Based Quantile Forecasting
> Transitioning from point forecasts to probabilistic distributions using Pinball Loss.

Instead of predicting a single number and adding a safety stock buffer, this approach trains models to predict the **conditional quantiles** directly.

### The Pinball Loss Function
The model minimizes this loss to find the optimal quantile $Q_q$:
$$L_q(y, ŷ) = q \cdot \max(y - ŷ, 0) + (1-q) \cdot \max(ŷ - y, 0)$$

### Implementation Framework
*   **P10 (Lower Bound)**: Optimized for $q=0.10$. Represents the "Low Demand" scenario.
*   **P50 (Point Forecast)**: Optimized for $q=0.50$. The median forecast (often more robust than mean).
*   **P90 (Upper Bound)**: Optimized for $q=0.90$. High-coverage scenario for service level targets.

### Supported Algorithms
| Model Type | Quantile Implementation |
|---|---|
| **LightGBM / XGBoost** | Set `objective="quantile"` and specify `alpha`. |
| **CatBoost** | Use `loss_function="Quantile:alpha=0.1"`. |
| **Neural Networks** | Use a Pinball Loss head with multiple output neurons. |

---

[**Back to Overview**](index.md)
