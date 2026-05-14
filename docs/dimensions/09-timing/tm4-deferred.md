# Segment Model Template

## Dimension 9 · Deferred

---

### 1. Definition
Predicts demand for SKUs where customer decision or approval cycles cause demand to arrive significantly later than the triggering event, requiring distributed lag models that spread expected demand across the post-trigger horizon.

### 2. Detailed Description
- **Applicable scenarios:** B2B capital procurement with long approval cycles, large project-based orders, demand delayed by regulatory approvals, consumer electronics with long consideration cycles
- **Boundaries:**

| Granularity | Detection Condition | Deferral Range | Min Events |
|---|---|---|---|
| Daily | Mean(dev_timing) > +7 days | 7–90 days after trigger | ≥ 5 events |
| Weekly | Mean(dev_timing) > +3 weeks | 3–26 weeks after | ≥ 5 events |
| Monthly | Mean(dev_timing) > +2 months | 2–12 months after | ≥ 5 events |
| Quarterly | Mean(dev_timing) > +1 quarter | 1–4 quarters after | ≥ 4 events |
| Yearly | Mean(dev_timing) > +1 year | 1–3 years after | ≥ 3 events |

- **Key demand characteristics:** Trigger event is visible; demand arrives with a variable but positive delay; deferral distribution is the key model component; pipeline visibility is critical
- **Differentiation from other models:** Unlike Lagging (fixed structural lag), deferral is variable and decision-driven; unlike Deferred (customer choice), Lagging is structural (supply chain physics)

### 3. Business Impact
- **Primary risk (over-forecast):** Ordering before deferred demand arrives — excess early inventory
- **Primary risk (under-forecast):** Not tracking pipeline; missing when large deferred orders land simultaneously
- **Strategic importance:** High in B2B — pipeline management is the primary planning tool; CRM integration is essential

### 4. Priority Level
🟠 **Tier 2** — High B2B relevance; requires CRM and pipeline data integration.

### 5. Model Strategy Overview

#### 5.1 Distributed Lag Model
```
d(t) = Σ_{L=L_min}^{L_max} P(demand at lag L) × trigger(t − L) × β_conversion

Deferral distribution P(L):
  Empirically estimated from historical trigger → demand lag observations
  Fit: Gamma or log-normal distribution to observed lags
  Mean(L) = μ_deferral; Std(L) = σ_deferral

Koyck geometric decay (if distribution unknown):
  d(t) = α + β × trigger(t) + λ × d(t−1) + ε(t)
  λ ∈ (0,1) = geometric decay factor
  Mean lag = λ / (1−λ)
```

#### 5.2 Analogue / Similarity Logic
- k = 3 analogues (similar deferral distribution in same category)
- Similarity: Mean deferral ±1 period, σ_deferral ±1 period, category, customer type

#### 5.3 Feature Engineering

| Granularity | Deferral Features | Pipeline Features | Baseline Features |
|---|---|---|---|
| Daily | trigger(t−7 to t−90) × deferral weights, mean deferral, σ_deferral | CRM pipeline value, expected close dates, approval stage | 7/30/90-day rolling mean |
| Weekly | trigger(t−3 to t−26 weeks) × weights, mean deferral | CRM pipeline, close probability | 4/8/13-week rolling mean |
| Monthly | trigger(t−2 to t−12 months) × weights | Pipeline value, approval stage | 3/6/12-month rolling mean |
| Quarterly | trigger(t−1 to t−4 quarters) × weights | Pipeline value | 2/4-quarter rolling mean |
| Yearly | trigger(t−1 to t−3 years) × weights | — | Annual rolling mean |

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM with distributed lag features (trigger × deferral weight per lag)
- Configuration: Objective = reg:squarederror; Metric = WMAPE
- Key features: Weighted trigger history across deferral range, pipeline value, approval stage, mean deferral, σ_deferral
- When to use: When ≥ 5 trigger-demand event pairs with observable lags

#### 6.2 Deep Learning (DL)
- Architectures: TFT with distributed lag encoding across full deferral range

| Granularity | Lookback (covers full deferral range) | Output |
|---|---|---|
| Daily | 180 days | P10, P50, P90 |
| Weekly | 52 weeks | P10, P50, P90 |
| Monthly | 24 months | P10, P50, P90 |
| Quarterly | 8 quarters | P10, P50, P90 |
| Yearly | 5 years | P10, P50, P90 |

#### 6.3 Statistical / Time Series Models
- Architectures: Koyck distributed lag model; Almon polynomial lag

**Koyck Model:**
```
d(t) = α + β × trigger(t) + λ × d(t−1) + ε(t)
λ optimised on validation MAE; typical range 0.3–0.7
Mean lag = λ / (1−λ) periods
```

| Granularity | Typical λ | Mean Deferral |
|---|---|---|
| Daily | 0.50 | 7–14 days |
| Weekly | 0.55 | 3–7 weeks |
| Monthly | 0.60 | 3–6 months |
| Quarterly | 0.65 | 2–4 quarters |
| Yearly | 0.70 | 1–2 years |

#### 6.4 Baseline / Fallback Model
- Fallback: Linearly interpolated demand based on trigger volume and historical conversion rate
- Alert if pipeline data unavailable for > 2 periods

### 7. Ensemble & Weighting

#### 7.2 Dynamic Weight Schedule

| Pipeline Data | LightGBM | TFT | Koyck |
|---|---|---|---|
| Available + ≥ 5 events | 50% | 25% | 25% |
| Available + < 5 events | 20% | 20% | 60% |
| Not available | 0% | 0% | 100% |

### 8. Uncertainty Quantification
- Method: Bootstrap on deferral distribution — sample from P(L) to generate demand scenarios
- Output: [P10, P50, P90] — wider when σ_deferral is large
- Use case: P75 for safety stock covering late-arriving deferred demand

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Pipeline alignment: Cross-reference with CRM expected close dates; alert if large pipeline not reflected in forecast
- Conversion rate cap: Forecast = trigger × max(historical conversion rate × 1.2)
- Manual overrides: Sales team pipeline update; approval stage change; deal size adjustment

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | WMAPE Target | Deferral Distribution Accuracy | Pipeline Alignment | Bias Alert |
|---|---|---|---|---|
| Daily | < 28% | Distribution within ±15% | Forecast vs pipeline ±20% | \|Bias\| > 12% |
| Weekly | < 24% | Distribution within ±12% | Forecast vs pipeline ±18% | \|Bias\| > 10% |
| Monthly | < 20% | Distribution within ±10% | Forecast vs pipeline ±15% | \|Bias\| > 8% |
| Quarterly | < 17% | Distribution within ±8% | Forecast vs pipeline ±12% | \|Bias\| > 6% |
| Yearly | < 14% | Distribution within ±6% | Forecast vs pipeline ±10% | \|Bias\| > 5% |

#### 10.2 Backtesting Protocol

| Granularity | Train | Test |
|---|---|---|
| Daily | 180 days | 30 days |
| Weekly | 52 weeks | 13 weeks |
| Monthly | 24 months | 6 months |
| Quarterly | 8 quarters | 2 quarters |
| Yearly | All available | 1 year |

#### 10.3 Retraining

| Granularity | Cadence | Latency |
|---|---|---|
| Daily | Daily | T+4 hours |
| Weekly | Weekly | T+1 day |
| Monthly | Monthly | T+2 days |
| Quarterly | Quarterly | T+3 days |
| Yearly | Annually | T+7 days |

### 11. Exception Handling & Overrides
- Auto-detect: Mean deferral shifts > 2 periods → re-estimate; large pipeline with no forecast coverage → alert; demand arrives outside deferral window → flag as anomaly
- Manual override: Sales team close date revision; deal cancellation flag; approval shortcut notification
- Override expiration: Per pipeline review cycle

### 12. Reclassification / Model Selection

| Condition | Target | Holding Period |
|---|---|---|
| Mean deferral drops below granularity threshold | Lagging or Coincident | 4 estimations |
| σ_deferral drops and lag becomes fixed | Lagging | 4 estimations |
| Demand becomes accelerated (pulls forward) | Accelerated | 3 estimations |

### 13. Review Cadence
- Monthly pipeline alignment review; quarterly deferral distribution recalibration; annual full re-evaluation

---

---
