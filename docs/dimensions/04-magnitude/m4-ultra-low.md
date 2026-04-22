## M4 · Ultra Low
### 1. Definition
Predicts demand for SKUs in the bottom 5th percentile of portfolio demand volume where near-zero absolute quantities make statistical forecasting unreliable, and the primary decision is whether to stock at all rather than how much to forecast.

### 2. Detailed Description
- **Applicable scenarios:** Extreme long-tail variants, obsolescence-risk items, single-customer specialty products, very slow MRO items
- **Boundaries:**

| Granularity | Percentile | Absolute Guardrail | Rolling Window |
|---|---|---|---|
| Daily | < 5th percentile | < 1 unit/day | 90-day rolling mean |
| Weekly | < 5th percentile | < 5 units/week | 26-week rolling mean |
| Monthly | < 5th percentile | < 20 units/month | 6-month rolling mean |
| Quarterly | < 5th percentile | < 60 units/quarter | 4-quarter rolling mean |
| Yearly | < 5th percentile | < 240 units/year | 3-year rolling mean |

- **Key demand characteristics:** Near-zero volume; all percentage metrics meaningless; inventory decision is binary; make-to-order consideration; very high relative holding cost
- **Differentiation from other models:** Unlike Low Volume, even MAE in units may be near zero; primary question is stock vs no-stock not how much to forecast; demand often Poisson or near-Poisson distributed

### 3. Business Impact
- **Primary risk (over-forecast):** Any stock build is disproportionately costly relative to volume
- **Primary risk (under-forecast):** Single unit stockout may have outsized customer impact (niche loyalty)
- **Strategic importance:** Low individually; collectively represents range management risk

### 4. Priority Level
🟡 Tier 3 — Lowest individual priority; range rationalisation decision more impactful than forecast accuracy.

### 5. Model Strategy Overview

#### 5.1 Stock vs No-Stock Decision (Primary Model)
- Primary question: Should this SKU be stocked at all?
- Stocking trigger: P(demand > 0 in next period) > stocking threshold

| Granularity | Stocking Threshold |
|---|---|
| Daily | P(demand > 0) > 0.20 |
| Weekly | P(demand > 0) > 0.30 |
| Monthly | P(demand > 0) > 0.40 |
| Quarterly | P(demand > 0) > 0.50 |
| Yearly | P(demand > 0) > 0.60 |

- If P(demand > 0) < threshold → consider make-to-order or delist
- Classifier: Logistic Regression on minimal features (avoid overfitting)

#### 5.2 Quantity Forecast (Secondary — given stocking decision is yes)
- Method: Historical non-zero mean (simplest reliable estimate)
- Do not use ML or DL — insufficient data; models overfit

#### 5.3 Analogue / Similarity Logic
- Pool Ultra Low SKUs for shared Poisson model estimation
- k = 10 most similar Ultra Low SKUs (same subcategory, similar ADI, similar price tier)
- Pooled Poisson rate: λ = Σ demand_events_i / Σ total_periods_i across pool

#### 5.4 Feature Engineering
- Minimal: Periods since last demand, prior year same-period demand, seasonal flag, category demand trend
- No complex feature engineering — overfit risk is extreme at this volume

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: Not recommended — insufficient data for individual SKU ML
- Cross-SKU pooling: Group Ultra Low SKUs; train single pooled Logistic Regression for stocking trigger
- When to use: Stocking trigger classification only; not for quantity forecast

#### 6.2 Deep Learning (DL)
- Not applicable — data too sparse

#### 6.3 Statistical / Time Series Models
- Architectures: Poisson model (primary) — demand arrival rate λ

**Poisson Demand Model:**
```
Demand ~ Poisson(λ)
λ = Mean demand over rolling window (non-zero and zero periods included)
P(demand = k) = (λ^k × e^{−λ}) / k!
P(demand > 0) = 1 − e^{−λ}
Forecast = λ (expected value of Poisson)
Safety stock = z_SL × √λ   (Poisson variance = mean = λ)
```

| Granularity | λ Estimation Window | Update Frequency |
|---|---|---|
| Daily | 180-day rolling | Weekly |
| Weekly | 52-week rolling | Monthly |
| Monthly | 24-month rolling | Monthly |
| Quarterly | 8-quarter rolling | Quarterly |
| Yearly | 3-year rolling | Annually |

- When to use: Primary model — Poisson is the natural distribution for rare demand events

#### 6.4 Baseline / Fallback Model
- Fallback: Fixed forecast = 1 unit per period (minimum viable stock signal)
- Logging & alerting: Alert on any demand event (each event is significant at Ultra Low volume)

### 7. Ensemble & Weighting
- No ensemble — Poisson model is primary and sufficient
- Stocking trigger (Logistic Regression) × Quantity (Poisson mean) = Final forecast

### 8. Uncertainty Quantification
- Method: Poisson distribution — exact probability mass function
- Output: P(demand = 0), P(demand = 1), P(demand = 2), ... up to P(demand = 5)
- Use case: Stock 1 unit if P(demand ≥ 1) > stocking threshold; stock 2 units if P(demand ≥ 2) > secondary threshold

**Stocking Decision Matrix:**
```
P(demand ≥ 1) = 1 − e^{−λ}
P(demand ≥ 2) = 1 − e^{−λ} − λ × e^{−λ}
P(demand ≥ k) = 1 − Σ P(demand = j) for j = 0 to k-1

Stock k units if P(demand ≥ k) > threshold
Threshold = f(holding_cost, stockout_cost, service_level_target)
```

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Rounding: Always round to whole units — fractional units impossible
- Make-to-order trigger: If P(demand > 0) < stocking threshold AND lead time allows → switch to make-to-order
- Range rationalisation trigger: If no demand in 13 consecutive weeks → flag for delisting review
- Manual overrides: Commercial decision to maintain range; customer commitment to order

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | Primary Metric | Secondary | Stockout Alert |
|---|---|---|---|
| Daily | MAE in units (target < 0.5 units) | Fill Rate > 80% | Any stockout on active stocked item |
| Weekly | MAE in units (target < 1 unit) | Fill Rate > 80% | Any stockout on active stocked item |
| Monthly | MAE in units (target < 2 units) | Fill Rate > 75% | Any stockout |
| Quarterly | MAE in units (target < 5 units) | Fill Rate > 70% | Any stockout |
| Yearly | MAE in units (target < 10 units) | Fill Rate > 65% | Any stockout |

- **Note:** MAPE, WMAPE, MASE all explicitly avoided — meaningless at Ultra Low volume
- Primary KPI: Stock/no-stock decision accuracy (did we stock when demand arrived?)

#### 10.2 Backtesting Protocol

| Granularity | Method | Train | Test | Min Events |
|---|---|---|---|---|
| Daily | Leave-one-out on demand events | All events except last | Last event | 3 events |
| Weekly | Leave-one-out | All events except last | Last event | 3 events |
| Monthly | Leave-one-out | All events except last | Last event | 3 events |
| Quarterly | Leave-one-out | All events except last | Last event | 2 events |
| Yearly | Leave-one-out | All events except last | Last event | 2 events |

#### 10.3 Retraining

| Granularity | Cadence | Latency |
|---|---|---|
| Daily | Monthly (low priority) | T+4 hours |
| Weekly | Monthly | T+1 day |
| Monthly | Quarterly | T+2 days |
| Quarterly | Semi-annually | T+3 days |
| Yearly | Annually | T+7 days |

### 11. Exception Handling & Overrides
- Automatic exception: Any demand event → immediate alert; volume rises above 5th percentile for 3 months → reclassify to Low Volume; no demand for 13 consecutive weeks → delist flag
- Manual override: Commercial team range retention decision; customer special order flag
- Override expiration: Per review cycle

### 12. Reclassification
- To Low Volume: Percentile rises above 5th for 4 consecutive months
- To Inactive: Zero demand ≥ 13 consecutive weeks (Lifecycle reclassification triggered simultaneously)
- Hard switch for both directions — no blend needed at this volume level

### 13. Review Cadence
- Monthly automated Ultra Low watchlist; quarterly range rationalisation review; annual full portfolio long-tail assessment

---

*End of Dimension 4 · Magnitude Pattern*
*4 Segments Complete · M1 through M4*
