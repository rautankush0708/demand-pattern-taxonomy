# Global Glossary
## Technical Definitions · Metrics · Symbols

---

> This glossary provides the standardized definitions for all terms used across the Demand Pattern Taxonomy.

---

### A
*   **ADI (Average Demand Interval):** A measure of demand frequency. Calculated as the total number of periods divided by the number of periods with non-zero demand.
*   **AR (Autoregressive) Bullwhip:** A measure of signal amplification where the variance of the forecast exceeds the variance of the actual demand.

*   **APE (Absolute Percentage Error):** Measures the percentage error for a single observation: `| (Actual - Forecast) / Actual | x 100`.
*   **Bias:** The systematic over or under-forecasting of demand. Calculated as the sum of errors divided by the sum of actuals.
*   **β (Beta):** In this taxonomy, specifically refers to the rolling slope coefficient calculated via linear regression or the Mann-Kendall test.

### C
*   **CFE (Cumulative Forecast Error):** The total sum of errors over time. Positive indicates under-forecasting; negative indicates over-forecasting.
*   **CV² (Squared Coefficient of Variation):** A measure of demand quantity variability. Calculated as the variance of non-zero demand divided by the square of the mean of non-zero demand.
*   **Cold Start:** The lifecycle stage for SKUs with history below the minimum threshold for statistical analysis.
*   **Coverage:** The percentage of actual demand observations that fall within the predicted P10–P90 probability interval.

### D
*   **Daily Forecast Error:** The raw difference between actuals and forecasts (`Actual - Forecast`).
*   **DCI (Demand Concentration Index):** A metric used to quantify how "peaked" demand is within a given window.

### D
*   **DCI (Demand Concentration Index):** A metric used to quantify how "peaked" demand is within a given window.
*   **Daily Forecast Error:** The raw difference between actuals and forecasts (`Actual - Forecast`).
*   **Discontinuation Flag:** A system-level binary attribute indicating that a product is no longer being actively replenished or sold.
*   **Drift Indicator:** Measures long-term changes in forecasts across a window: `Forecast(t) - Forecast(t - n)`.

### E
*   **Elasticity (Price):** The percentage change in demand quantity in response to a 1% change in price.
*   **ETS:** A family of statistical models representing Error, Trend, and Seasonality.

### G
*   **Gini Coefficient:** A measure of statistical dispersion used here to identify demand inequality (concentration) across time or customers.
*   **Granularity:** The time-scale of the demand signal (Daily, Weekly, Monthly, Quarterly, Yearly).

### H
*   **HHI (Herfindahl-Hirschman Index):** Used to measure customer or channel concentration. High HHI indicates demand is driven by a few large entities.
*   **HRT (High Resolution Tracking):** A monitoring protocol for SKUs in volatile or high-priority segments.

### M
*   **MAE (Mean Absolute Error):** The average of the absolute differences between forecasts and actuals.
*   **MASE (Mean Absolute Scaled Error):** A scale-independent accuracy metric that compares model error to a naive one-step forecast.
*   **Mann-Kendall Test:** A non-parametric test used to confirm the presence of a monotonic trend.

### P
*   **Pinball Loss:** The objective function used to train quantile models. It applies asymmetric weights to over- and under-predictions.

### Q
*   **Quantile:** A point in a distribution that divides it into intervals with equal probabilities. Q50 is the median.

### R
| Metric | Calculation | Purpose |
| :--- | :--- | :--- |
| **Revision Indicator** | `Forecast(today) - Forecast(yesterday)` | Tracks absolute model stability. |
| **Revision %** | `(Revision / Forecast(prev)) * 100` | Tracks relative model adjustments. |
| **Drift Indicator** | `Forecast(t) - Forecast(t - 7)` | Identifies long-term forecast "creep". |
| **Volatility** | `std(Forecast over last N days)` | Measures stability of the forecast signal. |
| **CFE** | `Σ(Actual - Forecast)` | Cumulative bias (Total over- or under-stock). |
| **Rolling MAD** | `Σ|Actual - Forecast| / N` | Average deviation over N days. |
| **Rolling MAPE** | `(1/N) * Σ(APE)` | Average percentage error over window. |
| **Tracking Signal** | `CFE / MAD` | Alerts when bias exceeds ±4. |

---

## 16. Model-Based Quantile Forecasting
> Directly predicting the probability distribution using Gradient Boosting or Neural Networks.

In this approach, the model is trained to output specific quantiles (e.g., P10, P50, P90) directly by optimizing the **Pinball Loss** function. This removes the need for traditional "Error standard deviation" assumptions.

### The Pinball Loss Function
```
L_q(y, ŷ) = q * max(y - ŷ, 0) + (1-q) * max(ŷ - y, 0)
```
*   **q = 0.10**: Penalizes under-prediction heavily (Lower Bound).
*   **q = 0.90**: Penalizes over-prediction heavily (Upper Bound).
*   **q = 0.50**: Median forecast (often more robust than the Mean).

### CI Construction
*   **CI Lower**: Predicted $Q_{0.10}(X_t)$
*   **Point Forecast**: Predicted $Q_{0.50}(X_t)$
*   **CI Upper**: Predicted $Q_{0.90}(X_t)$

### Implementation recommendation
*   **LightGBM / XGBoost**: Use `objective="quantile"` and `alpha=[0.1, 0.5, 0.9]`.
*   **CatBoost**: Use `loss_function="Quantile:alpha=0.1"`.

---

[**Back to Overview**](index.md)

### S
*   **SNR (Signal-to-Noise Ratio):** The ratio of the mean demand to the standard deviation. Used to determine the "cleanliness" of the demand signal.
*   **Stability:** The inverse of Revision; high stability means the forecast does not fluctuate wildly between runs.
*   **SRS (Shock Resilience Score):** A metric quantifying the percentage of demand retained during a major supply or market disruption.

### T
*   **Tracking Signal:** Monitors forecast bias over time. Calculated as `CFE / MAD`. Control limits are typically -4 to +4.

### V
*   **Volatility (Forecast):** The standard deviation of the forecast signal over a recent window. High volatility indicates "nervous" model behavior.

### W
*   **WMAPE (Weighted Mean Absolute Percentage Error):** The primary accuracy metric, calculated as the sum of absolute errors divided by the sum of total actual demand.

---

[**Back to Home**](index.md)
