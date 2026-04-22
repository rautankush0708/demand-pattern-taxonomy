## D2 · Event Driven
### 1. Definition
Predicts demand for SKUs where discrete, non-recurring external events cause statistically significant demand spikes or drops, requiring event calendar integration and event-specific uplift modelling.

### 2. Detailed Description
- **Applicable scenarios:** Sports events, product launches, political events, natural disasters, trade shows, one-time regulatory changes
- **Boundaries:**

| Granularity | Detection Condition | Event Window |
|---|---|---|
| Daily | Uplift > 20% in ±7 days of event; p < 0.05 | ±7 days |
| Weekly | Uplift > 20% in ±2 weeks of event; p < 0.05 | ±2 weeks |
| Monthly | Uplift > 20% in ±1 month of event; p < 0.05 | ±1 month |
| Quarterly | Uplift > 20% in ±1 quarter of event; p < 0.05 | ±1 quarter |
| Yearly | Uplift > 20% in ±6 months of event; p < 0.05 | ±6 months |

- **Key demand characteristics:** Spike or drop around discrete event dates; demand may be pulled forward or pushed back around events; post-event normalisation
- **Differentiation from other models:** Unlike Seasonal, pattern does not repeat every year at same calendar position; unlike Promotional, driven by external events not internal pricing decisions

### 3. Business Impact
- **Primary risk (over-forecast):** Overbuying for event that doesn't materialise or is cancelled
- **Primary risk (under-forecast):** Stockout during event — event windows are short; recovery impossible
- **Strategic importance:** High — event-period revenue is often disproportionately large

### 4. Priority Level
🔴 Tier 1 — Event windows are narrow; stockout during event is unrecoverable; cancellation risk requires scenario planning.

### 5. Model Strategy Overview

#### 5.1 Zero-Demand Handling (Hurdle)
- Active event threshold: P(demand > 0) > 0.70 in event window; standard threshold outside
- Classifier: Logistic Regression with event proximity features
- Regressor: LightGBM with event uplift features
- Fallback: Baseline forecast × historical event uplift factor

#### 5.2 Analogue / Similarity Logic
- Number of analogues: k = 5 (prior occurrences of same or similar events)
- Similarity criteria: Event type, event magnitude (attendance, reach), category, season
- Temporal decay: weight = exp(−age / half-life)

| Granularity | Half-Life |
|---|---|
| Daily | 180 days |
| Weekly | 26 weeks |
| Monthly | 12 months |
| Quarterly | 4 quarters |
| Yearly | 3 years |

- Aggregation: Weighted mean of event uplift profiles

#### 5.3 Feature Engineering

**Event Uplift Feature Construction:**
```
Days to event:       t_event − t_current
Days since event:    t_current − t_event
Event proximity:     exp(−|t_event − t_current| / event_half_life)
Uplift indicator:    1 if within event window; 0 otherwise
Post-event dip:      1 if within post-event normalisation window
```

| Granularity | Event Features | Baseline Features |
|---|---|---|
| Daily | Days to event, days since event, event type flag, event magnitude score, proximity decay, post-event dip flag | 7/30/90-day rolling mean (excl. event periods), seasonal index |
| Weekly | Weeks to event, weeks since event, event type, magnitude, proximity, post-event flag | 4/13/26-week rolling mean (excl. events), seasonal index |
| Monthly | Months to event, months since, event type, magnitude | 3/6/12-month rolling mean (excl. events) |
| Quarterly | Quarters to event, quarters since, event type | 2/4-quarter rolling mean |
| Yearly | — | Annual baseline |

- External signals: Event calendar feed (sports, political, trade), event confirmed/cancelled flag, event attendance forecast

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM — separate models for event periods and baseline periods
- Configuration: Objective = reg:squarederror; Metric = WMAPE, Uplift Accuracy
- Key features: Event proximity, event type flags, event magnitude, days to/since event, baseline rolling mean, seasonal index
- When to use: Primary model when ≥ 3 prior event occurrences available in history

#### 6.2 Deep Learning (DL)
- Architectures: TFT with known future inputs (event calendar fed as future covariate)

| Granularity | Lookback | Future Covariates | Output |
|---|---|---|---|
| Daily | 180 days | Event calendar 90 days ahead | P10, P50, P90 |
| Weekly | 52 weeks | Event calendar 13 weeks ahead | P10, P50, P90 |
| Monthly | 24 months | Event calendar 6 months ahead | P10, P50, P90 |
| Quarterly | 8 quarters | Event calendar 2 quarters ahead | P10, P50, P90 |
| Yearly | 5 years | Event calendar 1 year ahead | P10, P50, P90 |

- Training: Loss = quantile loss; Adam lr = 0.001; Dropout = 0.1; Patience = 10
- When to use: When event calendar is available as future input — TFT leverages known future events

#### 6.3 Statistical / Time Series Models
- Architectures: Regression with event dummies on ARIMA residuals (RegARIMA)

**RegARIMA Formula:**
```
d_t = Σ β_k × X_{k,t} + η_t
where X_{k,t} = event indicator variables (proximity, type, magnitude)
      η_t     = ARIMA(p,d,q) residual process
      β_k     = event uplift coefficient (estimated via OLS on deseasonalised series)
```

- When to use: Interpretability required; event uplift coefficients needed for reporting

#### 6.4 Baseline / Fallback Model
- Fallback triggers: No prior event occurrences; event calendar missing
- Fallback model: Baseline forecast (ignore event) + manual uplift override from commercial team
- Logging & alerting: Alert if event detected with no model coverage; alert on event cancellation

### 7. Ensemble & Weighting

#### 7.1 Ensemble Scheme
- Combination: D̂_t = w_lgbm × LightGBM + w_tft × TFT + w_stat × RegARIMA
- Weight determination: Error-inverse on event-period WMAPE from prior events

#### 7.2 Dynamic Weight Schedule

| Prior Event Occurrences | LightGBM | TFT | RegARIMA |
|---|---|---|---|
| < 3 events | 0% | 30% | 70% |
| 3–5 events | 50% | 20% | 30% |
| > 5 events | 60% | 30% | 10% |

### 8. Uncertainty Quantification
- Method: Scenario-based quantiles — event occurs vs event cancelled
- Output: [P10 (cancelled scenario), P50 (base), P90 (high attendance)] — three-scenario approach
- Use case: Safety stock = P75 assuming event occurs; contingency stock for cancellation at P10

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Event cap: min(forecast, 3 × historical max single event demand)
- Cancellation rule: If event confirmed cancelled → revert to baseline forecast immediately
- Manual overrides: Event magnitude input (attendance, reach); cancellation flag; competitor event flag
- Alignment: Cross-reference with event confirmed status in event calendar system

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | Event WMAPE Target | Baseline WMAPE | Uplift Accuracy | Bias Alert |
|---|---|---|---|---|
| Daily | < 30% | < 20% | < 25% error on uplift | \|Bias\| > 15% |
| Weekly | < 25% | < 18% | < 20% error on uplift | \|Bias\| > 12% |
| Monthly | < 20% | < 15% | < 18% error on uplift | \|Bias\| > 10% |
| Quarterly | < 18% | < 12% | < 15% error on uplift | \|Bias\| > 8% |
| Yearly | < 15% | < 10% | < 12% error on uplift | \|Bias\| > 6% |

#### 10.2 Backtesting Protocol

| Granularity | Method | Train | Test |
|---|---|---|---|
| Daily | Leave-one-event-out | All events except last | Last event |
| Weekly | Leave-one-event-out | All events except last | Last event |
| Monthly | Leave-one-event-out | All events except last | Last event |
| Quarterly | Leave-one-event-out | All events except last | Last event |
| Yearly | Leave-one-event-out | All events except last | Last event |

#### 10.3 Retraining & Data Freshness

| Granularity | Cadence | Trigger | Latency |
|---|---|---|---|
| Daily | Daily + Event trigger | On event calendar update | T+4 hours |
| Weekly | Weekly + Event trigger | On event calendar update | T+1 day |
| Monthly | Monthly + Event trigger | On event calendar update | T+2 days |
| Quarterly | Quarterly + Event trigger | On event calendar update | T+3 days |
| Yearly | Annually | — | T+7 days |

### 11. Exception Handling & Overrides
- Automatic exception detection: Event confirmed cancelled → immediate baseline revert; new event added to calendar → trigger model rerun; demand spike > 5 × baseline outside event window → investigate unlisted event
- Manual override process: Commercial team event magnitude adjustment; planner cancellation flag
- Override expiration: Per event occurrence

### 12. Reclassification / Model Selection
- Promote to Seasonal: If event recurs annually at same calendar position for ≥ 3 years
- Remove Event Driven driver: If no event occurrences in rolling 2-year window
- Add Seasonal driver: If recurring events create apparent seasonality alongside event signal

### 13. Review Cadence
- Performance monitoring: Per event occurrence — post-event debrief within 2 weeks
- Model review meeting: Monthly event calendar review with commercial team
- Full model re-evaluation: Annually; after any event type change

---
