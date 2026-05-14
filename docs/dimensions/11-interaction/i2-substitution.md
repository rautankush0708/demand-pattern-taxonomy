# Segment Model Template

## Dimension 11 · Substitution

---

### 1. Definition
Predicts demand for SKUs that receive demand transfers from substitute SKUs during stockout events, requiring OOS-conditional forecasting that adjusts demand upward when substitutes are unavailable.

### 2. Detailed Description
- **Applicable scenarios:** Brand equivalents, size variants, flavour alternatives, competitor OOS response, category complements with partial substitutability
- **Boundaries:**

| Granularity | Detection Condition | Min OOS Events | Confidence |
|---|---|---|---|
| Daily | sub_rate > 0.20; \|r\| > 0.20 (negative); ≥ 3 OOS events | ≥ 3 | p < 0.05 on sub_rate |
| Weekly | sub_rate > 0.20; ≥ 3 OOS events | ≥ 3 | p < 0.05 |
| Monthly | sub_rate > 0.20; ≥ 3 OOS events | ≥ 3 | p < 0.05 |
| Quarterly | sub_rate > 0.15; ≥ 2 OOS events | ≥ 2 | p < 0.10 |
| Yearly | sub_rate > 0.15; ≥ 2 OOS events | ≥ 2 | p < 0.10 |

- **Key demand characteristics:** Demand spikes when substitute SKU is OOS; demand reverts to baseline when substitute is available; portfolio total demand is conserved — only allocation changes
- **Differentiation from other models:** Unlike Complementary, correlation is negative (one up when other down); unlike Cannibalistic, the effect is driven by external supply constraint not product cannibalisation

### 3. Business Impact
- **Primary risk (over-forecast):** Ignoring OOS state of substitute — over-ordering this SKU when substitute is available
- **Primary risk (under-forecast):** Not capturing substitution uplift — stockout of both SKUs simultaneously
- **Strategic importance:** High — substitution relationships define portfolio resilience; managing substitute OOS prevents cascading stockouts

### 4. Priority Level
🔴 **Tier 1** — Failure to model substitution creates double stockout risk (substitute and this SKU); portfolio service level is compromised.

### 5. Model Strategy Overview

#### 5.1 OOS-Conditional Model
```
d_A(t) = d_A_baseline(t) × (1 + sub_rate_A × OOS_B(t))
where OOS_B(t) = 1 if SKU_B is out-of-stock at time t; 0 otherwise
      sub_rate_A = proportion of SKU_B demand shifting to SKU_A during OOS
      sub_rate_A estimated from historical OOS events of SKU_B

Portfolio conservation:
  d_A(t) + d_B(t) ≈ d_total(t)   [total demand conserved; only allocation changes]
```

#### 5.2 Analogue / Similarity Logic
- k = 3 (similar substitution pairs in same category)
- Similarity: sub_rate ±0.05, category, price tier, product type
- Use: Supplement sub_rate estimate when OOS events are limited (< 5 events)

#### 5.3 Feature Engineering

**OOS-Conditional Features:**
```
OOS_B(t)        = 1 if substitute SKU_B inventory ≤ 0; 0 otherwise
days_OOS_B(t)   = consecutive days SKU_B has been OOS
sub_rate_A      = estimated substitution coefficient
OOS_B_severity  = (max_B_demand − current_B_inventory) / max_B_demand
expected_B_restock = days until SKU_B expected back in stock
```

| Granularity | OOS Features | Baseline Features |
|---|---|---|
| Daily | OOS_B flag, days OOS, OOS severity, expected restock (days), sub_rate | 7/30/90-day non-OOS baseline rolling mean, seasonal index, holiday flag |
| Weekly | OOS_B flag, weeks OOS, OOS severity, expected restock (weeks), sub_rate | 4/8/13-week non-OOS rolling mean, seasonal index |
| Monthly | OOS_B flag, months OOS, sub_rate | 3/6/12-month non-OOS rolling mean |
| Quarterly | OOS_B flag, quarters OOS, sub_rate | 2/4-quarter non-OOS rolling mean |
| Yearly | OOS_B flag, sub_rate | Annual non-OOS baseline |

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM with OOS flag and substitution rate features
- Configuration: Objective = reg:squarederror; Metric = WMAPE (OOS periods separately from non-OOS)
- Key features: OOS_B flag, days OOS, sub_rate, OOS severity, expected restock, baseline rolling mean, seasonal index
- Interaction term: OOS_B × sub_rate (primary interaction — captures substitution magnitude)
- When to use: Primary model when ≥ 5 OOS events with full inventory data

#### 6.2 Deep Learning (DL)
- Architectures: TFT with OOS_B flag as time-varying past observed covariate

| Granularity | Lookback | OOS Covariate | Output |
|---|---|---|---|
| Daily | 180 days | OOS_B(t−30 to t) | P10, P50, P90 |
| Weekly | 52 weeks | OOS_B(t−13 to t) | P10, P50, P90 |
| Monthly | 24 months | OOS_B(t−6 to t) | P10, P50, P90 |
| Quarterly | 8 quarters | OOS_B(t−2 to t) | P10, P50, P90 |
| Yearly | 5 years | OOS_B(t−1 to t) | P10, P50, P90 |

- When to use: When real-time inventory data for substitute SKU is available in model pipeline

#### 6.3 Statistical / Time Series Models
- Architectures: Intervention model with OOS dummy variable

**OOS Intervention Model:**
```
d_A(t) = baseline_A(t) + β_sub × OOS_B(t) + ARIMA(p,d,q) residual
β_sub = sub_rate × baseline_A_mean   [substitution uplift coefficient]
OOS_B(t) = binary indicator
```

- When to use: Interpretability requirement; sub_rate reporting

#### 6.4 Baseline / Fallback Model
- Fallback: Baseline rolling mean × (1 + sub_rate) during OOS periods; baseline only during non-OOS
- Logging & alerting: Alert if OOS_B inventory feed unavailable; alert if both A and B are OOS simultaneously (double stockout risk)

### 7. Ensemble & Weighting

#### 7.2 Dynamic Weight Schedule

| OOS Events in History | LightGBM | TFT | Intervention Model |
|---|---|---|---|
| < 5 OOS events | 20% | 10% | 70% |
| 5–10 OOS events | 50% | 20% | 30% |
| > 10 OOS events | 60% | 25% | 15% |

### 8. Uncertainty Quantification
- Method: Scenario analysis — substitute in stock vs substitute OOS
- Output: [P10, P50, P90] — separate intervals for OOS and non-OOS states

| State | P10 | P50 | P90 |
|---|---|---|---|
| Substitute in stock | Standard behavior interval | Standard | Standard |
| Substitute OOS | Baseline × (1 + sub_rate × 0.7) | Baseline × (1 + sub_rate) | Baseline × (1 + sub_rate × 1.3) |

- Use case: Safety stock = P75 of OOS state forecast to cover substitution surge risk

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- OOS state check: Mandatory — query substitute SKU inventory status each period before forecast
- Portfolio conservation: Verify d_A_forecast + d_B_forecast ≈ d_total_historical mean; rescale if > ±10%
- Double OOS alert: If both A and B are OOS → escalate to supply chain team immediately
- Manual overrides: Supply team restock timeline for substitute SKU; sub_rate adjustment input

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | Non-OOS WMAPE | OOS WMAPE | Sub Rate Accuracy | Portfolio Consistency | Bias Alert |
|---|---|---|---|---|---|
| Daily | Per behavior std | < 30% | ±15% | < 5% | \|Bias\| > 12% |
| Weekly | Per behavior std | < 25% | ±12% | < 5% | \|Bias\| > 10% |
| Monthly | Per behavior std | < 22% | ±10% | < 5% | \|Bias\| > 8% |
| Quarterly | Per behavior std | < 18% | ±8% | < 5% | \|Bias\| > 6% |
| Yearly | Per behavior std | < 15% | ±6% | < 5% | \|Bias\| > 5% |

#### 10.2 Backtesting Protocol

| Granularity | Method | Train | Test |
|---|---|---|---|
| Daily | Leave-one-OOS-event-out | All OOS events except last | Last OOS event |
| Weekly | Leave-one-OOS-event-out | All except last | Last event |
| Monthly | Leave-one-OOS-event-out | All except last | Last event |
| Quarterly | Leave-one-OOS-event-out | All except last | Last event |
| Yearly | Leave-one-OOS-event-out | All except last | Last event |

#### 10.3 Retraining

| Granularity | Cadence | Trigger | Latency |
|---|---|---|---|
| Daily | Daily | On OOS state change | T+4 hours |
| Weekly | Weekly | On OOS event | T+1 day |
| Monthly | Monthly | On OOS event | T+2 days |
| Quarterly | Quarterly | On OOS event | T+3 days |
| Yearly | Annually | — | T+7 days |

### 11. Exception Handling & Overrides
- Auto-detect: sub_rate rises above 0.50 for 3 OOS events → investigate if Halo effect developing; both A and B OOS → P1 alert to supply chain; substitute permanently discontinued → reclassify to Independent (no future OOS events)
- Manual override: Category manager sub_rate adjustment; substitute restock date input; portfolio restructuring flag
- Override expiration: Per OOS event

### 12. Reclassification / Model Selection

| Condition | Target | Holding Period | Transition |
|---|---|---|---|
| sub_rate drops below 0.10 for 5 OOS events | Independent | 5 events | Soft blend |
| r changes to positive AND Granger causality confirmed | Complementary or Halo | 4 estimations | Re-test |
| Substitute SKU discontinued | Independent (no future OOS) | Immediate | Hard switch |
| Cannibalism detected (δ < −0.15) | Cannibalistic | 3 estimations | Re-test |

### 13. Review Cadence
- Monthly sub_rate stability check; quarterly OOS event review; annual portfolio interaction map refresh

---

---
