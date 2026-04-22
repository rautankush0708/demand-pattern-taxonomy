## SG5 · Amplified
### 1. Definition
Predicts demand for SKUs where the observed upstream order signal is amplified relative to true end-consumer demand due to the bullwhip effect (AR > 1.5), requiring demand sensing correction and end-to-end signal reconstruction to recover true consumption signal.

### 2. Detailed Description
- **Applicable scenarios:** Multi-tier supply chains where distributor or wholesaler ordering amplifies variability; categories with large distributor safety stocks and batch ordering behaviour

### 5. Model Strategy

#### 5.1 Bullwhip De-amplification
```
Amplification Ratio: AR = Var(Orders_upstream) / Var(d_downstream)

De-amplification:
  d_true(t) = d_upstream(t) / AR + (1 − 1/AR) × d_downstream_estimate(t)

If downstream (POS/consumption) data available:
  Use d_downstream directly — highest fidelity signal

If only upstream order data available:
  Apply exponential smoothing to orders: d_smoothed(t) = α × d(t) + (1−α) × d(t-1)
  α = 2 / (AR + 1)   [de-amplification smoothing factor derived from AR]
  Higher AR → lower α (more smoothing required)
```

| Granularity | AR Estimation Window | De-amplification Method |
|---|---|---|
| Daily | 90-day rolling | Exponential smoothing + POS comparison |
| Weekly | 52-week rolling | ETS smoothing on orders + POS if available |
| Monthly | 24-month rolling | ARIMA fitted on downstream; orders smoothed |
| Quarterly | 8-quarter rolling | Moving average de-amplification |
| Yearly | 3-year rolling | Long-run average de-amplification |

### 6. Model Families

#### 6.1 ML: LightGBM on de-amplified demand series
#### 6.2 DL: TFT with both upstream and downstream signals (if available)
#### 6.3 Statistical: State space model — observes upstream orders; estimates downstream state

**State Space De-amplification:**
```
State (true demand): μ(t) = μ(t-1) + η(t)      η ~ N(0, σ²_demand)
Observation (orders): d_obs(t) = μ(t) + AR_factor × noise(t)   noise ~ N(0, σ²_noise)
Kalman filter estimates μ(t) from noisy d_obs(t)
σ²_noise = (AR − 1) × σ²_demand   [calibrated from AR estimate]
```

### Evaluation

| Granularity | AR Estimate Accuracy | De-amplified WMAPE | Downstream Alignment | Bias Alert |
|---|---|---|---|---|
| Daily | AR within ±0.3 | < 25% | r(deamplified, POS) > 0.70 | \|Bias\| > 12% |
| Weekly | AR within ±0.3 | < 22% | r > 0.70 | \|Bias\| > 10% |
| Monthly | AR within ±0.2 | < 18% | r > 0.65 | \|Bias\| > 8% |
| Quarterly | AR within ±0.2 | < 15% | r > 0.65 | \|Bias\| > 6% |
| Yearly | AR within ±0.2 | < 12% | r > 0.60 | \|Bias\| > 5% |

### 9. Business Rules
- De-amplification mandatory: Raw upstream orders must NOT be used as demand input — always de-amplify first
- POS priority: If end-consumer POS data available → use directly; do not use upstream orders
- AR monitor: Alert if AR rises above 2.0 — severe bullwhip; supply chain structural review required

### 11. Exception Handling
- Alert: AR rises above 2.5 → escalate to supply chain leadership; POS data feed failure → fallback to de-amplified orders with wider prediction intervals

### 12. Reclassification

| Condition | Target | Trigger |
|---|---|---|
| AR drops below 1.2 for 6 months | Pure Signal | 6 months confirmation |
| SNR drops below 1.0 on de-amplified series | Noisy | Immediate |
| Distortion detected in addition to amplification | Distorted (primary) + Amplified (secondary) | Both flags active |

### 13. Review Cadence
- Monthly AR monitor; quarterly de-amplification calibration; annual supply chain structure review to identify root cause of bullwhip

---

*End of Dimension 12 · Signal Pattern*
*All 12 Dimensions Complete — 65 Segments Total*

---

# MASTER SUMMARY

| Dimension | Segments | Total |
|---|---|---|
| 1 · Lifecycle | Cold Start · New Launch · Growth · Mature · Decline · Phasing Out · Inactive | 7 |
| 2 · Behavior | Stable · Intermittent · Erratic · Lumpy · Trending · Step Change · Pulsed · Slow Mover | 8 |
| 3 · Driver | Seasonal · Event Driven · Promotional · Weather Driven · Customer Driven · Supply Constrained | 6 |
| 4 · Magnitude | High Volume · Medium Volume · Low Volume · Ultra Low | 4 |
| 5 · Trend | Upward · Downward · Flat · Cyclical · Reverting | 5 |
| 6 · Concentration | Uniform · Peaked · Bi-Modal · Multi-Modal · Skewed | 5 |
| 7 · Shock | Shock Resistant · Shock Sensitive · Fast Recovery · Slow Recovery · Permanent Shift · Step Down | 6 |
| 8 · Elasticity | Elastic · Inelastic · Threshold · Saturation | 4 |
| 9 · Timing | Leading · Lagging · Coincident · Deferred · Accelerated | 5 |
| 10 · Recurrence | Regular · Irregular · One Time · Declining · Growing | 5 |
| 11 · Interaction | Independent · Substitution · Complementary · Cannibalistic · Halo | 5 |
| 12 · Signal | Pure Signal · Distorted · Noisy · Lagged · Amplified | 5 |
| **TOTAL** | | **65** |
