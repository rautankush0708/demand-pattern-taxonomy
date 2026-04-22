## C3 · Bi-Modal
### 1. Definition
Predicts demand for SKUs with two distinct significant demand peaks per cycle, requiring dual-peak modelling and separate peak-specific inventory policies for each of the two demand surges.

### 2. Detailed Description
- **Applicable scenarios:** Summer and winter peaks (apparel, beverages), back-to-school + holiday (stationery, toys), Q1 and Q3 budget cycles, dual-season sports categories
- **Boundaries:**

| Granularity | DCI_norm | Gini | Modality | Peak Separation | Min Cycles |
|---|---|---|---|---|---|
| Daily | DCI_norm > 0.30 | Gini > 0.40 | Exactly 2 significant peaks | ≥ 2 days between peaks | ≥ 2 weekly cycles |
| Weekly | DCI_norm > 0.25 | Gini > 0.35 | Exactly 2 significant peaks | ≥ 4 weeks between peaks | ≥ 2 annual cycles |
| Monthly | DCI_norm > 0.25 | Gini > 0.35 | Exactly 2 significant peaks | ≥ 3 months between peaks | ≥ 2 annual cycles |
| Quarterly | DCI_norm > 0.30 | Gini > 0.40 | Exactly 2 significant peaks | ≥ 1 quarter between peaks | ≥ 2 annual cycles |
| Yearly | DCI_norm > 0.30 | Gini > 0.40 | Exactly 2 significant peaks | ≥ 1 year between peaks | ≥ 4 years |

- **Key demand characteristics:** Two clearly separated demand surges per cycle; each peak has its own magnitude and timing; trough periods between peaks; each peak may have different drivers
- **Differentiation from other models:** Unlike Peaked, two peaks exist — managing them separately is required; unlike Multi-Modal, exactly two peaks; unlike Seasonal (which handles regular multi-peak), the two peaks may have different magnitudes and drivers

### 3. Business Impact
- **Primary risk (over-forecast):** Post-first-peak overstock carried into second peak; combined inventory burden
- **Primary risk (under-forecast):** Stockout at either peak — two windows of high commercial risk per cycle
- **Strategic importance:** High — managing both peaks correctly doubles the commercial opportunity vs single-peak

### 4. Priority Level
🔴 Tier 1 — Two independent peak events per cycle; each is individually high-stakes; combined error impact is significant.

### 5. Model Strategy Overview

#### 5.1 Dual-Peak Decomposition
```
Decompose demand into three components:
  Peak 1 component: Demand attributable to first peak (timed around t_peak1)
  Peak 2 component: Demand attributable to second peak (timed around t_peak2)
  Baseline component: Demand in trough periods between and outside peaks

Peak 1 SI: SI_1(p) = peak 1 period mean / overall mean
Peak 2 SI: SI_2(p) = peak 2 period mean / overall mean
Dual seasonal model: F(t) = baseline × SI_1(period_of_t) × SI_2(period_of_t)
```

#### 5.2 Feature Engineering

| Granularity | Peak 1 Features | Peak 2 Features | Baseline Features |
|---|---|---|---|
| Daily | Peak1 proximity, days to/from peak1, in-peak1 flag, SI_1 | Peak2 proximity, days to/from peak2, in-peak2 flag, SI_2 | 7/30/90-day rolling mean (excl. both peaks), holiday flag |
| Weekly | Weeks to/from peak1, in-peak1 flag, SI_1 | Weeks to/from peak2, in-peak2 flag, SI_2 | 4/8/13-week rolling mean (excl. peaks), promo flag |
| Monthly | Months to/from peak1, SI_1 | Months to/from peak2, SI_2 | 3/6/12-month rolling mean |
| Quarterly | In-peak1-quarter flag, SI_1 | In-peak2-quarter flag, SI_2 | 2/4-quarter rolling mean |
| Yearly | Years to peak1, SI_1 | Years to peak2, SI_2 | Annual baseline |

### 6. Model Families

#### 6.1 ML: LightGBM — three-way split model (peak1 / peak2 / baseline)
- Peak models: Higher complexity; peak-period upweighting in training
- Baseline model: Simpler; level-focused

#### 6.2 DL: TFT with dual seasonal decomposition; TBATS for daily (handles multiple seasonal periods natively)

**TBATS for Bi-Modal:**
```
TBATS(p, {m_1, m_2}, φ, {α, β}, {γ_1, γ_2})
p = number of ARMA components
m_1 = period of seasonal component 1 (distance between peaks)
m_2 = period of seasonal component 2 (full cycle)
Example monthly: TBATS with m_1 = 6 (6-month peak gap), m_2 = 12 (annual)
```

| Granularity | TBATS Configuration |
|---|---|
| Daily | m_1 = days between peaks; m_2 = 365 |
| Weekly | m_1 = weeks between peaks; m_2 = 52 |
| Monthly | m_1 = months between peaks; m_2 = 12 |
| Quarterly | m_1 = quarters between peaks; m_2 = 4 |
| Yearly | BSTS with dual seasonal components |

#### 6.3 Statistical: TBATS (primary for bi-modal) — handles dual seasonality natively

#### 6.4 Fallback: Prior year same period × trend adjustment; separate fallback for each peak

### 7. Ensemble

| Period | LightGBM | TFT/TBATS | ETS |
|---|---|---|---|
| Peak 1 window | 40% | 40% | 20% |
| Peak 2 window | 40% | 40% | 20% |
| Trough periods | 50% | 20% | 30% |

### 8. Uncertainty Quantification
- Output: [P10, P50, P90] — separate intervals for each peak
- Peak 1 buy: P75 of peak1 forecast
- Peak 2 buy: P75 of peak2 forecast (adjusted for unsold Peak1 stock remaining)
- Use case: Dual pre-season buy; inter-peak inventory run-down plan

### 9. Business Rules
- Non-negativity: max(0, forecast)
- Inter-peak run-down rule: Forecast for trough between peaks ≤ remaining peak1 stock / expected trough periods (prevents over-ordering for peak2 when peak1 stock remains)
- Separate peak locks: Peak1 forecast locked separately from Peak2 forecast
- Manual overrides: Independent buyer adjustments for each peak timing and magnitude

### 10. Evaluation

#### 10.1 Key Metrics

| Granularity | Overall WMAPE | Peak1 WMAPE | Peak2 WMAPE | Trough WMAPE | Bias Alert |
|---|---|---|---|---|---|
| Daily | < 28% | < 32% | < 32% | < 18% | \|Bias\| > 12% |
| Weekly | < 22% | < 28% | < 28% | < 15% | \|Bias\| > 10% |
| Monthly | < 20% | < 25% | < 25% | < 12% | \|Bias\| > 8% |
| Quarterly | < 18% | < 22% | < 22% | < 10% | \|Bias\| > 6% |
| Yearly | < 15% | < 20% | < 20% | < 8% | \|Bias\| > 5% |

#### 10.2 Backtesting — must include both peaks in test period; minimum 2 full cycles in train

#### 10.3 Retraining — pre-peak1 retrain + pre-peak2 retrain + standard cadence

### 11. Exception Handling
- Alert: Peak timing shifts > 1 period for either peak; peak magnitude changes > 25%; one peak disappears for 1 cycle → reclassify to Peaked

### 12. Reclassification

| Condition | Target | Holding Period |
|---|---|---|
| One peak disappears for 2 cycles | Peaked | 2 cycles |
| DCI_norm drops below threshold for 2 cycles | Uniform | 2 cycles |
| 3+ peaks emerge for 2 cycles | Multi-Modal | 2 cycles |

### 13. Review Cadence
- Pre-peak1 review; pre-peak2 review; post-cycle debrief; annual full re-evaluation

---
