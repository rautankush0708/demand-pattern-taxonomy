## B7 · Pulsed

### 1. Definition
Predicts demand for SKUs with regular inter-arrival intervals and consistent quantities, where demand arrives in predictable bulk pulses — typically driven by periodic ordering behavior rather than underlying consumption patterns.

### 2. Detailed Description
- **Applicable scenarios:** B2B periodic procurement, regular bulk orders, contract call-offs, distributor stocking orders
- **Boundaries:**

| Granularity | ADI Threshold | CV² Threshold | Inter-Arrival CV |
|---|---|---|---|
| Daily | ADI ≥ 1.10 | CV² < 0.49 | CV_arrival < 0.30 |
| Weekly | ADI ≥ 1.32 | CV² < 0.49 | CV_arrival < 0.30 |
| Monthly | ADI ≥ 1.25 | CV² < 0.49 | CV_arrival < 0.30 |
| Quarterly | ADI ≥ 1.20 | CV² < 0.49 | CV_arrival < 0.30 |
| Yearly | ADI ≥ 1.10 | CV² < 0.49 | CV_arrival < 0.30 |

- **Key demand characteristics:** Regular timing, consistent quantity, predictable bulk arrivals, gaps between orders are expected
- **Differentiation:** Unlike Intermittent, inter-arrival intervals are regular (CV_arrival < 0.30); unlike Stable, demand does not occur every period; unlike Lumpy, quantity variance is low

### 3. Business Impact
- **Primary risk (over-forecast):** Stock build between pulse events
- **Primary risk (under-forecast):** Shortage when pulse arrives — often large quantity impact
- **Strategic importance:** High in B2B — pulse timing is the critical forecast dimension

### 4. Priority Level
🟠 Tier 2 — Timing accuracy is more important than quantity accuracy for this segment.

### 5. Model Strategy Overview

#### 5.1 Hurdle (Timing Model)
- Primary task: Predict when next pulse will occur
- Threshold: P(pulse in period t) > 0.50
- Classifier: Logistic Regression on inter-arrival time features
- Quantity model: Rolling non-zero mean (quantity is stable — low CV²)

#### 5.2 Analogue Logic
- k = 3 (pulsed SKUs from same customer or category)
- Similarity: Inter-arrival mean ±1 period, CV² ±0.1, customer type

#### 5.3 Feature Engineering

| Granularity | Timing Features | Quantity Features |
|---|---|---|
| Daily | Days since last pulse, mean inter-arrival (days), CV_arrival, day of week of pulses | Non-zero mean (90-day), quantity trend |
| Weekly | Weeks since last pulse, mean inter-arrival (weeks), CV_arrival, week of month pattern | Non-zero mean (13-week) |
| Monthly | Months since last pulse, mean inter-arrival (months), contract renewal flag | Non-zero mean (6-month) |
| Quarterly | Quarters since last pulse, mean inter-arrival | Non-zero mean |
| Yearly | Years since last pulse | Non-zero mean |

### 6. Model Families

#### 6.1 ML: Two-stage — Logistic Regression (timing) + Rolling Mean (quantity)
#### 6.2 DL: DeepAR — handles periodic patterns with zero inflation

| Granularity | Lookback | Features |
|---|---|---|
| Daily | 180 days | 8 |
| Weekly | 52 weeks | 8 |
| Monthly | 24 months | 6 |
| Quarterly | 8 quarters | 5 |
| Yearly | 5 years | 4 |

#### 6.3 Statistical: Croston with low α (stable inter-arrival exploitation)

| Granularity | α_z | α_p |
|---|---|---|
| Daily | 0.05 | 0.05 |
| Weekly | 0.05 | 0.05 |
| Monthly | 0.10 | 0.10 |
| Quarterly | 0.10 | 0.10 |
| Yearly | 0.15 | 0.15 |

#### 6.4 Fallback: Historical occurrence rate × historical non-zero mean

### 7. Ensemble

| Events in History | Logistic+Mean | Croston | DeepAR |
|---|---|---|---|
| < 8 events | 20% | 80% | 0% |
| 8–20 events | 60% | 40% | 0% |
| > 20 events | 50% | 25% | 25% |

### 8. Uncertainty Quantification
- [P10, P50, P90] — narrower than Intermittent due to regular timing
- Primary uncertainty: Timing of pulse (±1–2 periods); quantity uncertainty is low

### 9. Business Rules
- Forecast = 0 outside predicted pulse window (P(pulse) < 0.50)
- Pulse window: Center on predicted timing ± half inter-arrival std

### 10. Evaluation

| Granularity | Timing Accuracy Target | Quantity MAE | Bias Alert |
|---|---|---|---|
| Daily | Pulse predicted within ±3 days | < 15% of non-zero mean | \|Bias\| > 10% |
| Weekly | Pulse predicted within ±1 week | < 15% | \|Bias\| > 10% |
| Monthly | Pulse predicted within ±1 month | < 12% | \|Bias\| > 8% |
| Quarterly | Pulse predicted within ±1 quarter | < 12% | \|Bias\| > 8% |
| Yearly | Pulse predicted within ±1 year | < 10% | \|Bias\| > 6% |

### 11. Exception Handling
- Alert: Pulse expected but not arrived within 2× mean inter-arrival — check supply and customer status
- Alert: Inter-arrival CV rises above 0.30 for 5 events → reclassify to Intermittent

### 12. Reclassification

| Condition | Target | Holding Period |
|---|---|---|
| CV_arrival rises above 0.30 for 5 events | Intermittent | 5 events |
| CV² rises above 0.49 | Lumpy | 8 periods |
| ADI drops below threshold for 8 periods | Stable | 8 periods |

### 13. Review Cadence
- Per pulse event review; monthly pulsed portfolio review; quarterly full re-evaluation

---

