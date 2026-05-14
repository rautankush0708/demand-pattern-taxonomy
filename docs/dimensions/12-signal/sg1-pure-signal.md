# Segment Model Template

## Dimension 12 · Pure Signal

---

### 1. Definition
Predicts demand for SKUs where the observed demand series accurately reflects true underlying consumption (SNR > 4.0; DI < 0.10), enabling direct application of statistical and ML models without pre-processing corrections.

### 2. Detailed Description
- **Applicable scenarios:** POS-connected demand, consumer direct-to-brand, highly transparent supply chains, categories with minimal returns or stockouts, B2C subscription demand
- **Boundaries:**

| Granularity | SNR Threshold | DI Threshold | AR Threshold | Lag Threshold |
|---|---|---|---|---|
| Daily | SNR > 4.0 | DI < 0.10 in > 90% of days | AR < 1.2 | L ≤ 3 days |
| Weekly | SNR > 4.0 | DI < 0.10 in > 90% of weeks | AR < 1.2 | L ≤ 1 week |
| Monthly | SNR > 4.0 | DI < 0.10 in > 90% of months | AR < 1.2 | L ≤ 1 month |
| Quarterly | SNR > 3.0 | DI < 0.10 in > 90% of quarters | AR < 1.2 | L ≤ 1 quarter |
| Yearly | SNR > 2.0 | DI < 0.10 in > 90% of years | AR < 1.2 | L ≤ 6 months |

- **Key demand characteristics:** Observed demand = true consumption; model directly on raw data; no correction pipeline needed; highest forecast accuracy potential
- **Differentiation from other models:** Unlike all other Signal segments, no pre-processing correction is required; models are applied directly to observed demand; data quality monitoring is passive not active

### 3. Business Impact
- **Primary risk (over-forecast):** Standard model risk only — no signal amplification
- **Primary risk (under-forecast):** Standard model risk only
- **Strategic importance:** High — pure signal gives highest possible forecast accuracy; data pipeline investment to maintain pure signal quality is justified

### 4. Priority Level
🟠 **Tier 2** — Standard model applied; primary value is confirming data quality and enabling full model accuracy potential.

### 5. Model Strategy Overview

#### 5.1 Zero-Demand Handling (Hurdle)
- Per Behavior segment standard — no signal correction needed
- Classifier: Per Behavior segment
- Regressor: Per Behavior segment

#### 5.2 Analogue / Similarity Logic
- Per Behavior segment standard — no signal-specific analogues

#### 5.3 Feature Engineering
- Standard features per Behavior × Lifecycle × Magnitude segment
- Additional signal quality metadata: SNR, DI, AR monitored as passive metadata features
- Signal watch: Monthly SNR, DI, AR recomputation — alert if any threshold breached

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Standard LightGBM per Behavior segment — full feature set applicable; no signal correction
- When to use: Always — pure signal enables maximum feature richness

#### 6.2 Deep Learning (DL)
- Standard TFT / N-BEATS per Behavior segment — full lookback applicable; no signal degradation

| Granularity | Lookback | Features | Output |
|---|---|---|---|
| Daily | 365 days | Full feature set | P10, P50, P90 |
| Weekly | 52 weeks | Full feature set | P10, P50, P90 |
| Monthly | 24 months | Full feature set | P10, P50, P90 |
| Quarterly | 8 quarters | Full feature set | P10, P50, P90 |
| Yearly | 5 years | Full feature set | P10, P50, P90 |

#### 6.3 Statistical / Time Series Models
- Standard ETS / SARIMA per Behavior segment — applied directly to raw demand

#### 6.4 Baseline / Fallback Model
- Standard per Behavior segment
- Logging & alerting: Monthly signal quality check; alert if SNR drops below 2.0; alert if DI rises above 0.12; alert if AR rises above 1.3

### 7. Ensemble & Weighting
- Standard ensemble per Behavior segment — no signal-related weight adjustment needed

### 8. Uncertainty Quantification
- Standard [P10, P50, P90] per Behavior segment
- No signal-correction uncertainty widening needed

### 9. Business Rules & Post-Processing
- Standard per Behavior segment
- No signal correction adjustments
- Monthly signal quality audit: Re-run SNR, DI, AR; reclassify if any threshold crossed

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | WMAPE Target | Bias Alert | SNR Monitor | DI Monitor | AR Monitor |
|---|---|---|---|---|---|
| Daily | Per Behavior std | Per Behavior std | Alert if SNR < 2.0 | Alert if DI > 0.12 | Alert if AR > 1.3 |
| Weekly | Per Behavior std | Per Behavior std | Alert if SNR < 2.0 | Alert if DI > 0.12 | Alert if AR > 1.3 |
| Monthly | Per Behavior std | Per Behavior std | Alert if SNR < 2.0 | Alert if DI > 0.12 | Alert if AR > 1.3 |
| Quarterly | Per Behavior std | Per Behavior std | Alert if SNR < 1.5 | Alert if DI > 0.12 | Alert if AR > 1.3 |
| Yearly | Per Behavior std | Per Behavior std | Alert if SNR < 1.0 | Alert if DI > 0.12 | Alert if AR > 1.3 |

#### 10.2 Backtesting Protocol
- Standard per Behavior segment
- Additional validation: Confirm WMAPE does not degrade when model trained on raw vs smoothed data (validates purity)

#### 10.3 Retraining
- Standard cadence per Behavior segment
- Additional trigger: Monthly signal quality check; reclassify immediately if threshold breached

### 11. Exception Handling & Overrides
- Auto-detect: SNR drops below 2.0 → run full signal audit; DI rises above 0.15 → investigate distortion source; AR rises above 1.5 → investigate supply chain amplification
- Manual override: Data team signal quality escalation; supply chain flag for stockout period
- Override expiration: Per monthly signal audit

### 12. Reclassification / Model Selection

| Condition | Target | Holding Period | Transition |
|---|---|---|---|
| SNR drops below 1.0 for 2 consecutive estimations | Noisy | 2 estimations | Hard switch → apply noise correction |
| DI rises above 0.15 in > 20% of periods | Distorted | 2 estimations | Hard switch → apply correction |
| AR rises above 1.5 for 2 estimations | Amplified | 2 estimations | Hard switch → de-amplify |
| Lag L confirmed > threshold | Lagged Signal | 2 estimations | Hard switch → lag correction |

### 13. Review Cadence
- Monthly signal quality audit; quarterly data pipeline review; annual full signal integrity assessment

---

---
