## C4 · Multi-Modal

### 1. Definition
Predicts demand for SKUs with three or more distinct significant demand peaks per cycle, requiring decomposition-based modelling and period-specific inventory policies across multiple demand surges within the same cycle.

### 2. Detailed Description
- **Applicable scenarios:** Weekly promotions creating multiple monthly peaks, quarterly + mid-quarter peaks, multiple holiday categories, product lines with 3+ seasonal occasions
- **Boundaries:**

| Granularity | DCI_norm | Gini | Modality | Min Cycles |
|---|---|---|---|---|
| Daily | DCI_norm > 0.25 | Gini > 0.35 | ≥ 3 significant peaks | ≥ 2 weekly cycles |
| Weekly | DCI_norm > 0.20 | Gini > 0.30 | ≥ 3 significant peaks | ≥ 2 annual cycles |
| Monthly | DCI_norm > 0.20 | Gini > 0.30 | ≥ 3 significant peaks | ≥ 2 annual cycles |
| Quarterly | DCI_norm > 0.25 | Gini > 0.35 | ≥ 3 significant peaks | ≥ 3 annual cycles |
| Yearly | DCI_norm > 0.25 | Gini > 0.35 | ≥ 3 significant peaks | ≥ 5 years |

- **Key demand characteristics:** Multiple demand surges; complex intra-cycle pattern; individual peak accuracy is critical; standard seasonal models underfit
- **Differentiation from other models:** Unlike Bi-Modal, three or more peaks; unlike Peaked, demand is distributed across multiple occasions; most complex Concentration segment

### 3. Business Impact
- **Primary risk (over-forecast):** Simultaneous overstock across multiple peaks — compounding inventory burden
- **Primary risk (under-forecast):** Stockout across multiple occasions — compounding lost sales
- **Strategic importance:** High — complex demand management challenge; model sophistication directly translates to commercial value

### 4. Priority Level
🔴 Tier 1 — Multiple peak management is complex; error at any peak is commercially significant.

### 5. Model Strategy Overview

#### 5.1 Full Decomposition Approach
```
Demand Decomposition:
  d(t) = Baseline(t) + Σ Peak_k(t)   for k = 1 to K peaks

For each peak k:
  Peak_k(t) = A_k × proximity_k(t)
  proximity_k(t) = exp(−|t − t_peak_k| / half_width_k)
  A_k = peak amplitude (estimated from historical data)
  half_width_k = half-width of peak k (periods to decay to 50% of amplitude)

Reconstruct: F(t) = Baseline(t) + Σ A_k × proximity_k(t)
```

#### 5.2 Feature Engineering

| Granularity | Features per Peak (×K peaks) | Baseline Features |
|---|---|---|
| Daily | Proximity_k, days to/from peak_k, in-peak_k flag, SI_k; for k=1 to K | 7/30/90-day rolling mean (excl. all peaks), holiday flag |
| Weekly | Weeks to/from peak_k, in-peak_k flag, SI_k; for k=1 to K | 4/8/13-week rolling mean, promo flag |
| Monthly | Months to/from peak_k, in-peak_k flag, SI_k; for k=1 to K | 3/6/12-month rolling mean |
| Quarterly | In-peak_k flag, SI_k; for k=1 to K | 2/4-quarter rolling mean |
| Yearly | Years to peak_k, SI_k; for k=1 to K | Annual baseline |

### 6. Model Families

#### 6.1 ML: LightGBM with full peak decomposition features; one model per period type (each peak + baseline)

#### 6.2 DL: TBATS (handles multiple seasonal frequencies natively) + TFT with full seasonal decomposition

**TBATS Multi-Modal Configuration:**
```
TBATS(p, {m_1, m_2, ..., m_K}, φ, {α, β}, {γ_1, ..., γ_K})
m_k = period of k-th seasonal component
Optimise m_k via FFT peak detection on detrended series
```

| Granularity | TBATS Components |
|---|---|
| Daily | Up to 3 seasonal components: day-of-week (7), monthly (30), annual (365) |
| Weekly | Up to 3: monthly (4), quarterly (13), annual (52) |
| Monthly | Up to 3: quarterly (3), bi-annual (6), annual (12) |
| Quarterly | Up to 2: bi-annual (2), annual (4) |
| Yearly | BSTS with K seasonal components |

#### 6.3 Statistical: TBATS as primary — designed for multi-seasonal demand

#### 6.4 Fallback: Prior year same period × trend; separate fallback per peak

### 7. Ensemble

| Period Type | LightGBM | TBATS / TFT | Naive Prior Year |
|---|---|---|---|
| Peak periods | 40% | 45% | 15% |
| Trough periods | 50% | 30% | 20% |

### 8. Uncertainty Quantification
- [P10, P50, P90] — separate intervals per peak
- Use case: Individual peak stock buy per peak; consolidated safety stock across all peaks

### 9. Business Rules
- Separate peak locks: Each peak period locked independently for procurement
- Peak priority rule: If stock limited → prioritise highest-revenue peak by SI × expected volume
- Manual overrides: Independent adjustments per peak; peak cancellation flag for any individual peak

### 10. Evaluation

#### 10.1 Key Metrics

| Granularity | Overall WMAPE | Per-Peak WMAPE | Trough WMAPE | Bias Alert |
|---|---|---|---|---|
| Daily | < 30% | < 35% per peak | < 20% | \|Bias\| > 15% |
| Weekly | < 25% | < 30% per peak | < 18% | \|Bias\| > 12% |
| Monthly | < 22% | < 28% per peak | < 15% | \|Bias\| > 10% |
| Quarterly | < 20% | < 25% per peak | < 12% | \|Bias\| > 8% |
| Yearly | < 18% | < 22% per peak | < 10% | \|Bias\| > 6% |

#### 10.2 Backtesting — rolling seasonal window covering full cycle; ≥ 3 cycles in train

#### 10.3 Retraining — pre-each-peak retrain triggered + standard cadence

### 11. Exception Handling
- Alert: Number of peaks changes vs prior cycle → reclassify; any peak amplitude changes > 30%; peak timing shifts > 1 period

### 12. Reclassification

| Condition | Target | Holding Period |
|---|---|---|
| Reduces to 2 peaks for 2 cycles | Bi-Modal | 2 cycles |
| Reduces to 1 peak for 2 cycles | Peaked | 2 cycles |
| DCI_norm drops below threshold | Uniform | 2 cycles |

### 13. Review Cadence
- Pre-each-peak review; post-cycle full debrief; annual TBATS frequency re-calibration

---

