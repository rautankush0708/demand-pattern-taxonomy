# Dimension 3 · Driver Pattern
## Demand Forecasting Model Templates

---

> **Segments:** 6 · Seasonal · Event Driven · Promotional · Weather Driven · Customer Driven · Supply Constrained
> **Granularities:** Daily · Weekly · Monthly · Quarterly · Yearly
> **Note:** Driver is an overlay dimension — a SKU carries one or more drivers simultaneously alongside its Lifecycle and Behavior classifications. Driver segments are not mutually exclusive.

---

# PART 0 — FORMULA & THRESHOLD REFERENCE
## Driver Pattern Specific

---

## 0.1 Core Detection Metrics

### A. Seasonality Detection — ACF & FFT
> Identifies repeating calendar-driven demand cycles

**Autocorrelation Formula:**
```
ACF(lag k) = Σ[(d_t − d̄)(d_{t−k} − d̄)] / Σ[(d_t − d̄)²]

Significant seasonality: ACF(lag k) > 2 / √n
where n = number of observations

FFT Peak: Seasonal period p = 1 / f_peak
where f_peak = dominant frequency in FFT spectrum
Minimum 2 full cycles required for reliable detection
```

| Granularity | Primary Lag | Secondary Lag | Tertiary Lag | Min Obs |
|---|---|---|---|---|
| **Daily** | lag 7 (weekly) | lag 30 (monthly) | lag 365 (annual) | ≥ 365 days |
| **Weekly** | lag 52 (annual) | lag 13 (quarterly) | lag 4 (monthly) | ≥ 104 weeks |
| **Monthly** | lag 12 (annual) | lag 3 (quarterly) | lag 6 (bi-annual) | ≥ 24 months |
| **Quarterly** | lag 4 (annual) | lag 2 (bi-annual) | — | ≥ 8 quarters |
| **Yearly** | — | — | — | Not applicable |

**Seasonal Index Formula:**
```
Multiplicative SI(p) = μ_period_p / μ_overall
Additive      SI(p) = μ_period_p − μ_overall

Use multiplicative when SI varies proportionally with demand level
Use additive when SI is constant regardless of demand level

Deseasonalised demand: d_adj(t) = d(t) / SI(p)   [multiplicative]
                                  = d(t) − SI(p)   [additive]
```

---

### B. Event Correlation Detection
> Identifies demand spikes linked to discrete external events

**Uplift Formula:**
```
Event Uplift = (Mean demand in event window) / (Mean demand in baseline window) − 1

Event window:    T−w to T+w around event date (w = event influence window)
Baseline window: Same periods excluding event influence zones

Significant event effect: Uplift > 0.20 (20% above baseline) AND p < 0.05 (t-test)
```

| Granularity | Event Window (w) | Baseline Window |
|---|---|---|
| **Daily** | ±7 days | Same 14-day window excluding prior 3 event occurrences |
| **Weekly** | ±2 weeks | Same 4-week window prior year non-event |
| **Monthly** | ±1 month | Same month prior years non-event |
| **Quarterly** | ±1 quarter | Same quarter prior years |
| **Yearly** | ±6 months | Prior years baseline |

---

### C. Promotional Uplift Detection
> Quantifies demand increase attributable to promotions

**Promotional Uplift Formula:**
```
Promo Uplift = (Demand during promotion) / (Baseline demand same period) − 1

Baseline = deseasonalised rolling mean excluding promo periods
Significant promo effect: Uplift > 0.15 (15%) AND statistically significant (p < 0.05)

Post-promo dip factor: Dip = (Mean demand T+1 to T+w post-promo) / Baseline − 1
Total net uplift = Gross uplift + Dip factor (often negative)
```

| Granularity | Promo Window | Post-Promo Dip Window |
|---|---|---|
| **Daily** | Duration of promotion | 7 days post-promotion end |
| **Weekly** | Duration of promotion | 2 weeks post-promotion |
| **Monthly** | Duration of promotion | 1 month post-promotion |
| **Quarterly** | Duration of promotion | 1 quarter post-promotion |
| **Yearly** | Duration of promotion | 6 months post-promotion |

---

### D. Weather Correlation Detection
> Measures demand correlation with meteorological variables

**Correlation Formula:**
```
Pearson r = Σ[(d_t − d̄)(w_t − w̄)] / [√Σ(d_t − d̄)² × √Σ(w_t − w̄)²]

Significant weather effect: |r| > 0.30 AND p < 0.05
Lag correlation: Test r at lag 0, 1, 2, 3 periods — use max |r| lag
```

| Granularity | Weather Variables Tested | Lag Range |
|---|---|---|
| **Daily** | Temperature, rainfall, humidity, wind speed, UV index | lag 0–3 days |
| **Weekly** | Weekly mean temperature, total rainfall, frost days | lag 0–2 weeks |
| **Monthly** | Monthly mean temperature, total rainfall, sunshine hours | lag 0–1 month |
| **Quarterly** | Seasonal mean temperature, total rainfall | lag 0–1 quarter |
| **Yearly** | Annual mean temperature, rainfall deviation from norm | lag 0 |

---

### E. Customer Concentration — Herfindahl-Hirschman Index
> Measures demand concentration across customers

**HHI Formula:**
```
HHI = Σ(s_i)²
where s_i = share of customer i in total demand (as decimal)
HHI range: 0 (perfectly fragmented) to 1 (single customer monopoly)

Customer Driven threshold: HHI > 0.60
Top-3 customer share > 60% of total demand
```

| Granularity | Computation Window | Update Frequency |
|---|---|---|
| **Daily** | Rolling 90-day | Weekly |
| **Weekly** | Rolling 52-week | Monthly |
| **Monthly** | Rolling 12-month | Monthly |
| **Quarterly** | Rolling 4-quarter | Quarterly |
| **Yearly** | Rolling 3-year | Annually |

---

### F. Supply Constraint Detection
> Identifies periods where observed demand is below true demand due to stockouts

**Lost Sales Estimation Formula:**
```
Lost Sales Flag: Period flagged if:
  (1) Inventory on hand = 0 for ≥ 1 day in period AND
  (2) Demand in following period exceeds rolling mean by > 1σ (pent-up demand signal)

Unconstrained Demand Estimate:
  d_unconstrained(t) = d_observed(t) / Fill_Rate(t)
  where Fill_Rate(t) = Units shipped / Units ordered (if order data available)
  or Fill_Rate(t) = 1 − (Stockout days / Total days in period)

Supply Constrained flag: Stockout events > 2 in rolling window
```

| Granularity | Rolling Window | Stockout Flag Threshold |
|---|---|---|
| **Daily** | 90-day | > 5 stockout days in window |
| **Weekly** | 52-week | > 4 stockout weeks in window |
| **Monthly** | 12-month | > 2 stockout months in window |
| **Quarterly** | 4-quarter | > 1 stockout quarter in window |
| **Yearly** | 3-year | > 1 stockout year in window |

---

## 0.2 Driver Detection Decision Rules

```
For each SKU, test all drivers independently and stack all that apply:

D1 SEASONAL:          ACF(seasonal lag) > 2/√n   AND   ≥ 2 full cycles available
D2 EVENT DRIVEN:      Event Uplift > 20%           AND   p < 0.05
D3 PROMOTIONAL:       Promo Uplift > 15%           AND   p < 0.05
D4 WEATHER DRIVEN:    |Pearson r| > 0.30           AND   p < 0.05
D5 CUSTOMER DRIVEN:   HHI > 0.60                   OR    Top-3 share > 60%
D6 SUPPLY CONSTRAINED: Stockout events > threshold AND   unconstrained demand differs

If no driver detected → Driver = NONE (pure baseline demand; no external cause)
Multiple drivers can apply simultaneously → stack all flagged drivers
```

---

## 0.3 Rolling Window Reference

| Window Name | Daily | Weekly | Monthly | Quarterly | Yearly |
|---|---|---|---|---|---|
| **Short** | 7 days | 4 weeks | 2 months | 1 quarter | 1 year |
| **Medium** | 30 days | 8 weeks | 3 months | 2 quarters | 2 years |
| **Long** | 90 days | 13 weeks | 6 months | 3 quarters | 3 years |
| **Extended** | 180 days | 26 weeks | 12 months | 4 quarters | 4 years |
| **Full Year** | 365 days | 52 weeks | 12 months | 4 quarters | 5 years |
| **DL Lookback** | 90 days | 52 weeks | 24 months | 8 quarters | 5 years |

---

## 0.4 Accuracy Metric Formulas

```
WMAPE   = Σ|Forecast_t − Actual_t| / Σ Actual_t × 100

Bias    = Σ(Forecast_t − Actual_t) / Σ Actual_t × 100

Uplift Accuracy = |Predicted Uplift − Actual Uplift| / Actual Uplift × 100

Event Detection Rate = Events correctly flagged / Total events × 100  (Target > 90%)

Pinball(α,t) = α × (Actual_t − Q_α)     if Actual_t ≥ Q_α
             = (1−α) × (Q_α − Actual_t)  if Actual_t < Q_α

Coverage = Actuals within [P10, P90] / Total Periods × 100  (Target: 80%)
```

---

## 0.5 Retraining & Backtesting Reference

| Granularity | Retraining | Latency | Backtest Train | Backtest Test |
|---|---|---|---|---|
| **Daily** | Daily | T+4 hours | 180 days | 30 days |
| **Weekly** | Weekly | T+1 day | 52 weeks | 13 weeks |
| **Monthly** | Monthly | T+2 days | 24 months | 6 months |
| **Quarterly** | Quarterly | T+3 days | 8 quarters | 2 quarters |
| **Yearly** | Annually | T+7 days | All available | 1 year |

---

# PART 1 — SEGMENT TEMPLATES

---

## D1 · Seasonal

### 1. Definition
Predicts demand for SKUs where a statistically significant portion of demand variance is explained by repeating calendar-driven cycles, requiring seasonal decomposition and period-aware modelling to capture predictable peaks and troughs.

### 2. Detailed Description
- **Applicable scenarios:** Holiday-driven categories, back-to-school, summer/winter cycles, quarterly budget cycles, agricultural seasons
- **Boundaries:**

| Granularity | Detection Condition | Min History |
|---|---|---|
| Daily | ACF(lag 7) > 2/√n OR ACF(lag 365) > 2/√n | ≥ 365 days (2 cycles) |
| Weekly | ACF(lag 52) > 2/√n OR ACF(lag 13) > 2/√n | ≥ 104 weeks (2 cycles) |
| Monthly | ACF(lag 12) > 2/√n OR ACF(lag 3) > 2/√n | ≥ 24 months (2 cycles) |
| Quarterly | ACF(lag 4) > 2/√n | ≥ 8 quarters (2 cycles) |
| Yearly | Not applicable | Not applicable |

- **Key demand characteristics:** Predictable recurring peaks and troughs aligned to calendar; seasonality may be multiplicative (amplitude scales with level) or additive (fixed amplitude)
- **Differentiation from other models:** Unlike Event Driven, pattern repeats predictably every cycle without external trigger; unlike Promotional, not caused by pricing or trade activity

### 3. Business Impact
- **Primary risk (over-forecast):** Post-peak overstock — classic markdown and write-off problem
- **Primary risk (under-forecast):** Stockout at seasonal peak — lost sales at highest value moment
- **Strategic importance:** Very high — peak season performance disproportionately drives annual revenue

### 4. Priority Level
🔴 Tier 1 — Peak season stockouts and post-season overstock are the two most costly inventory errors in seasonal categories.

### 5. Model Strategy Overview

#### 5.1 Zero-Demand Handling (Hurdle)
- Active event threshold: P(demand > 0) > 0.60 in season; may approach 0 in off-season
- Classifier type: Seasonal classifier — trained separately for in-season vs off-season periods
- Regressor type: LightGBM with seasonal features; ETS with seasonal component
- Fallback: Same period prior year × trend adjustment factor

#### 5.2 Analogue / Similarity Logic
- Number of analogues: k = 3 (SKUs with similar seasonal profiles in same category)
- Similarity criteria: Seasonal index correlation > 0.80, category, price tier
- Temporal decay: weight = exp(−age / half-life)

| Granularity | Half-Life |
|---|---|
| Daily | 365 days (align to annual cycle) |
| Weekly | 52 weeks |
| Monthly | 12 months |
| Quarterly | 4 quarters |
| Yearly | Not applicable |

- Aggregation: Weighted mean of seasonal index profiles

#### 5.3 Feature Engineering

**Seasonal Index Computation:**
```
SI(p) = μ_period_p / μ_overall   [multiplicative]
SI(p) = μ_period_p − μ_overall   [additive]

Deseasonalised demand: d_adj(t) = d(t) / SI(period_of_t)
```

| Granularity | Seasonal Features | Cycle Features |
|---|---|---|
| Daily | Day of week index, month index, holiday flag, days to peak, days since trough, annual SI | Week of year, quarter flag, season flag |
| Weekly | Week of year SI, quarter SI, holiday week flag, weeks to peak, weeks since trough | Month flag, season start/end flag |
| Monthly | Month of year SI, quarter SI, season flag, months to peak, months since trough | Half-year flag, fiscal period flag |
| Quarterly | Quarter of year SI, half-year flag, quarters to peak | Fiscal year flag |
| Yearly | Not applicable | — |

- External signals: Retail calendar, school term dates, public holidays, fiscal year calendar

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM with seasonal index features
- Configuration: Objective = reg:squarederror; Metric = WMAPE, RMSE
- Key features: Seasonal index, rolling mean (deseasonalised), period of year, holiday flag, days/weeks to peak, trend component
- When to use: Primary model — seasonal features make ML very effective here

#### 6.2 Deep Learning (DL)
- Architectures: TFT / N-BEATS (N-BEATS has explicit seasonality block)

| Granularity | Lookback | Features | Output |
|---|---|---|---|
| Daily | 365 days (full cycle) | 18 | P10, P50, P90 |
| Weekly | 104 weeks (2 cycles) | 15 | P10, P50, P90 |
| Monthly | 36 months (3 cycles) | 12 | P10, P50, P90 |
| Quarterly | 12 quarters (3 cycles) | 10 | P10, P50, P90 |
| Yearly | Not applicable | — | — |

- Training: Loss = MAE; Adam lr = 0.001; Dropout = 0.1; Early stopping patience = 15
- When to use: Complex multi-frequency seasonality (e.g. day-of-week + annual); history > 2 full cycles

#### 6.3 Statistical / Time Series Models
- Architectures: ETS(A,N,A) or ETS(M,N,M); SARIMA(p,d,q)(P,D,Q)_m; TBATS for multiple seasons

| Granularity | Primary Model | Seasonal Period (m) | Variant |
|---|---|---|---|
| Daily | TBATS | 7 + 365 | Dual seasonality |
| Weekly | SARIMA / ETS | 52 | ETS(A,N,A) or (M,N,M) |
| Monthly | SARIMA / ETS | 12 | ETS(A,N,A) with period=12 |
| Quarterly | ETS | 4 | ETS(A,N,A) with period=4 |
| Yearly | ETS(A,N,N) | — | No seasonality at yearly |

**SARIMA Formula:**
```
SARIMA(p,d,q)(P,D,Q)_m:
Non-seasonal: AR(p) × I(d) × MA(q)
Seasonal:     AR(P) × I(D) × MA(Q) at lag m
Combine:      (1 − φ_1B − ... − φ_pB^p)(1 − Φ_1B^m − ... − Φ_PB^{Pm})(1−B)^d(1−B^m)^D d_t
            = (1 + θ_1B + ... + θ_qB^q)(1 + Θ_1B^m + ... + Θ_QB^{Qm}) ε_t
```

- When to use: Strong seasonal signal; interpretability and prediction intervals required

#### 6.4 Baseline / Fallback Model
- Fallback triggers: Fewer than 2 full seasonal cycles; model convergence failure
- Fallback model: Same period last year (naive seasonal) × trend factor
- Logging & alerting: Alert if fallback rate > 15%

### 7. Ensemble & Weighting

#### 7.1 Ensemble Scheme
- Combination: D̂_t = w_lgbm × LightGBM + w_stat × ETS/SARIMA + w_dl × TFT/NBEATS
- Weight determination: Error-inverse weighting on rolling 4-period in-season WMAPE

#### 7.2 Dynamic Weight Schedule

| History (Full Cycles) | LightGBM | ETS / SARIMA | TFT / N-BEATS |
|---|---|---|---|
| 2 cycles | 50% | 50% | 0% |
| 3 cycles | 50% | 30% | 20% |
| ≥ 4 cycles | 40% | 25% | 35% |

### 8. Uncertainty Quantification
- Method: Quantile regression + conformal prediction on seasonal residuals
- Output: [P10, P50, P90] — wider at peak (higher uncertainty); narrower in trough
- Use case: Pre-season buy quantity (P75–P90 for safety); post-season markdown trigger (P10 threshold)

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Peak cap: min(forecast, 1.5 × prior year same period peak demand)
- Trough floor: max(forecast, 0) — allow zero in deep off-season
- Manual overrides: Buyer peak buy quantity input; season start/end date adjustment
- Alignment: Pre-season forecast locked for procurement; in-season revisions allowed weekly

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | WMAPE Target (In-Season) | WMAPE Target (Off-Season) | Bias Alert | Peak Accuracy |
|---|---|---|---|---|
| Daily | < 20% | < 30% | \|Bias\| > 10% | Peak week WMAPE < 25% |
| Weekly | < 18% | < 25% | \|Bias\| > 8% | Peak week WMAPE < 20% |
| Monthly | < 15% | < 20% | \|Bias\| > 7% | Peak month WMAPE < 18% |
| Quarterly | < 12% | < 18% | \|Bias\| > 6% | Peak quarter WMAPE < 15% |
| Yearly | < 10% | — | \|Bias\| > 5% | — |

#### 10.2 Backtesting Protocol

| Granularity | Method | Train | Test | Min History |
|---|---|---|---|---|
| Daily | Rolling seasonal window | 2 full cycles | 1 full cycle | 3 cycles |
| Weekly | Rolling seasonal window | 2 full cycles | 1 full cycle | 3 cycles |
| Monthly | Rolling seasonal window | 2 full cycles | 1 full cycle | 3 cycles |
| Quarterly | Rolling seasonal window | 2 full cycles | 1 full cycle | 3 cycles |
| Yearly | Expanding window | All available | 1 year | 3 years |

#### 10.3 Retraining & Data Freshness

| Granularity | Cadence | Incremental | Latency |
|---|---|---|---|
| Daily | Daily | No | T+4 hours |
| Weekly | Weekly | No | T+1 day |
| Monthly | Monthly | No | T+2 days |
| Quarterly | Quarterly | No | T+3 days |
| Yearly | Annually | No | T+7 days |

### 11. Exception Handling & Overrides
- Automatic exception detection: Peak forecast > 2 × prior year peak; seasonal index shift > 20% vs prior year; off-season demand unexpectedly non-zero for 3+ periods
- Manual override process: Buyer pre-season sign-off; in-season reforecast approval; timestamp and reason logged
- Override expiration: Per season unless permanent SI shift confirmed

### 12. Reclassification / Model Selection
- Remove Seasonal driver: If ACF(seasonal lag) < 2/√n for 2 consecutive full cycles
- Add Promotional driver: If promo uplift detected layered on seasonal signal
- Add Event Driven driver: If one-time event distorts seasonal pattern
- Switching logic: Driver flags are additive — seasonal flag removed if no longer significant

### 13. Review Cadence
- Performance monitoring: Weekly in-season dashboard; monthly off-season check
- Model review meeting: Pre-season review (6 weeks before peak); post-season debrief
- Full model re-evaluation: Annually post full cycle; after any seasonal calendar change

---

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

## D3 · Promotional

### 1. Definition
Predicts demand for SKUs where internal pricing and trade promotion activities cause statistically significant demand uplifts, requiring promotion calendar integration, uplift modelling, and post-promotion dip correction.

### 2. Detailed Description
- **Applicable scenarios:** Price promotions, multi-buy offers, display/feature promotions, trade deal periods, loyalty reward events, clearance sales
- **Boundaries:**

| Granularity | Detection Condition | Promo Window |
|---|---|---|
| Daily | Uplift > 15% during promotion; p < 0.05 | Duration of promotion |
| Weekly | Uplift > 15% during promotion; p < 0.05 | Duration of promotion |
| Monthly | Uplift > 15% during promotion; p < 0.05 | Duration of promotion |
| Quarterly | Uplift > 15% during promotion; p < 0.05 | Duration of promotion |
| Yearly | Uplift > 15% during promotion; p < 0.05 | Duration of promotion |

- **Key demand characteristics:** Demand spike during promotion; post-promotion dip (demand pull-forward); baseline demand between promotions; promotion frequency and depth are key drivers
- **Differentiation from other models:** Unlike Event Driven, promotions are internally controlled and planned; unlike Seasonal, timing is commercially set not calendar-driven; post-promo dip is a distinct Promotional characteristic

### 3. Business Impact
- **Primary risk (over-forecast):** Excess promotional stock left after promotion ends; post-promo inventory overhang
- **Primary risk (under-forecast):** Out-of-stock during promotion — lost sales at promoted price; retailer penalty
- **Strategic importance:** Very high — promotional ROI is directly linked to forecast accuracy

### 4. Priority Level
🔴 Tier 1 — Promotional forecast errors have immediate P&L impact; over-stock post-promo forces clearance at further discount.

### 5. Model Strategy Overview

#### 5.1 Zero-Demand Handling (Hurdle)
- Active event threshold: P(demand > 0) > 0.85 during promotion; standard threshold in baseline
- Classifier: Rule-based — promotional period always active
- Regressor: LightGBM with promotion depth and type features

#### 5.2 Analogue / Similarity Logic
- Number of analogues: k = 5 (prior promotions of same type on same or similar SKU)
- Similarity criteria: Promotion type (price/multi-buy/display), discount depth ±5%, category, season
- Temporal decay: weight = exp(−age / half-life)

| Granularity | Half-Life |
|---|---|
| Daily | 90 days |
| Weekly | 13 weeks |
| Monthly | 6 months |
| Quarterly | 3 quarters |
| Yearly | 2 years |

- Aggregation: Weighted mean of promotion uplift profiles

#### 5.3 Feature Engineering

**Promotional Feature Construction:**
```
Promo flag:         1 if period is promotional; 0 otherwise
Promo depth:        (Regular price − Promo price) / Regular price
Promo type:         One-hot encoded {price_cut, multibuy, display, TPR, clearance}
Promo duration:     Number of periods promotion is active
Days into promo:    t_current − t_promo_start
Days left in promo: t_promo_end − t_current
Post-promo flag:    1 if within post-promo dip window; 0 otherwise
Post-promo day:     t_current − t_promo_end (for dip modelling)
Baseline demand:    Rolling mean on non-promo periods (deseasonalised)
Uplift factor:      Estimated = f(promo_depth, promo_type, category_elasticity)
```

| Granularity | Promo Features | Baseline Features |
|---|---|---|
| Daily | Promo flag, depth, type, days into/left in promo, post-promo flag, post-promo day, distribution on promotion | 7/30/90-day non-promo rolling mean, seasonal index, day of week |
| Weekly | Promo flag, depth, type, week of promo, post-promo flag, distribution coverage | 4/8/13-week non-promo rolling mean, seasonal index |
| Monthly | Promo flag, depth, type, month of promo, post-promo dip flag | 3/6/12-month non-promo rolling mean, seasonal index |
| Quarterly | Promo flag, depth, type, post-promo flag | 2/4-quarter non-promo rolling mean |
| Yearly | Annual promo count, average depth | Annual non-promo baseline |

- External signals: Promotion calendar feed, retailer feature/display confirmation, distribution on promotion, competitor promotional activity

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM — separate models for promotional and baseline periods
- Configuration (promo model): Objective = reg:squarederror; Metric = WMAPE, Uplift Accuracy
- Configuration (baseline model): Objective = reg:squarederror; Metric = WMAPE
- Key features: All promotional features, price elasticity index, category promotional intensity, competitive promo flag
- When to use: Primary model when ≥ 5 prior promotions in history

#### 6.2 Deep Learning (DL)
- Architectures: TFT with promotion calendar as known future covariate

| Granularity | Lookback | Future Covariates | Output |
|---|---|---|---|
| Daily | 180 days | Promo calendar 30 days ahead | P10, P50, P90 |
| Weekly | 52 weeks | Promo calendar 8 weeks ahead | P10, P50, P90 |
| Monthly | 24 months | Promo calendar 3 months ahead | P10, P50, P90 |
| Quarterly | 8 quarters | Promo calendar 1 quarter ahead | P10, P50, P90 |
| Yearly | 5 years | Annual promo plan | P10, P50, P90 |

- Training: Loss = quantile loss; Adam lr = 0.001; Dropout = 0.15; Patience = 10
- When to use: When promo calendar available as future input; complex promo patterns

#### 6.3 Statistical / Time Series Models
- Architectures: RegARIMA with promotion dummy variables + post-promo dip correction

**Promotional Uplift Model:**
```
d_promo(t) = d_baseline(t) × (1 + β_uplift × promo_depth(t) × promo_type_factor)
d_postpromo(t) = d_baseline(t) × (1 + β_dip × post_promo_day(t))

β_uplift estimated from historical promotions via OLS
β_dip estimated from post-promo periods via OLS
promo_type_factor = {price_cut: 1.0, multibuy: 0.8, display: 0.6, TPR: 0.9}
```

- When to use: Interpretability required; uplift coefficients needed for trade planning

#### 6.4 Baseline / Fallback Model
- Fallback triggers: No prior promotions; promotion calendar missing
- Fallback model: Baseline forecast × category average uplift factor for promotion type
- Logging & alerting: Alert if promo period detected without model coverage; alert if post-promo dip not modelled

### 7. Ensemble & Weighting

#### 7.1 Ensemble Scheme
- Combination: D̂_t = w_lgbm × LightGBM + w_tft × TFT + w_stat × RegARIMA
- Weight determination: Error-inverse on promotional period WMAPE

#### 7.2 Dynamic Weight Schedule

| Prior Promotions in History | LightGBM | TFT | RegARIMA |
|---|---|---|---|
| < 5 promotions | 20% | 30% | 50% |
| 5–10 promotions | 50% | 20% | 30% |
| > 10 promotions | 60% | 30% | 10% |

### 8. Uncertainty Quantification
- Method: Quantile regression on promotional residuals
- Output: [P10, P50, P90] — wider during promotion; narrower in baseline
- Use case: Promotional stock buy = P75; post-promo rundown = P25 for residual stock

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Promo cap: min(forecast, 3 × baseline rolling mean)
- Post-promo dip: max(forecast_postpromo, 0.5 × baseline) — prevent over-correction
- Manual overrides: Trade team promotional depth confirmation; display confirmation; retailer acceptance
- Alignment: Promotional forecast must align with confirmed promotional stock commitment

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | Promo WMAPE Target | Baseline WMAPE | Post-Promo Dip Accuracy | Bias Alert |
|---|---|---|---|---|
| Daily | < 25% | < 20% | Dip within ±20% of actual | \|Bias\| > 12% |
| Weekly | < 22% | < 18% | Dip within ±18% | \|Bias\| > 10% |
| Monthly | < 20% | < 15% | Dip within ±15% | \|Bias\| > 8% |
| Quarterly | < 18% | < 12% | Dip within ±12% | \|Bias\| > 6% |
| Yearly | < 15% | < 10% | — | \|Bias\| > 5% |

#### 10.2 Backtesting Protocol

| Granularity | Method | Train | Test |
|---|---|---|---|
| Daily | Leave-one-promo-out | All promos except last | Last promotion |
| Weekly | Leave-one-promo-out | All promos except last | Last promotion |
| Monthly | Leave-one-promo-out | All promos except last | Last promotion |
| Quarterly | Leave-one-promo-out | All promos except last | Last promotion |
| Yearly | Leave-one-promo-out | All promos except last | Last promotion |

#### 10.3 Retraining & Data Freshness

| Granularity | Cadence | Event Trigger | Latency |
|---|---|---|---|
| Daily | Daily | On promo calendar update | T+4 hours |
| Weekly | Weekly | On promo calendar update | T+1 day |
| Monthly | Monthly | On promo calendar update | T+2 days |
| Quarterly | Quarterly | On promo plan update | T+3 days |
| Yearly | Annually | On annual plan | T+7 days |

### 11. Exception Handling & Overrides
- Automatic exception detection: Promo period demand < baseline (promotion had no effect → flag for review); post-promo demand > promo demand (demand timing anomaly); forecast > 3 × baseline during non-promo period
- Manual override process: Trade manager promo depth confirmation; display uplift manual input; logistics team stock availability confirmation
- Override expiration: Per promotion occurrence

### 12. Reclassification / Model Selection
- Remove Promotional driver: If uplift consistently < 10% across last 5 promotions (promotion-insensitive)
- Promote to Event Driven: If promotions are discrete, non-recurring events rather than regular trade activity
- Add Seasonal driver: If promotional calendar aligns with seasonal peaks

### 13. Review Cadence
- Performance monitoring: Per promotion debrief within 1 week post-promotion end
- Model review meeting: Monthly promotional planning review with trade/commercial team
- Full model re-evaluation: Quarterly or after major promotional strategy change

---

## D4 · Weather Driven

### 1. Definition
Predicts demand for SKUs where meteorological variables explain a statistically significant portion of demand variance, requiring weather data integration and weather-conditioned forecasting.

### 2. Detailed Description
- **Applicable scenarios:** Beverages (temperature-driven), apparel (temperature/rainfall), energy (heating/cooling), outdoor leisure, agriculture, ice cream, umbrellas, cold/flu remedies
- **Boundaries:**

| Granularity | Detection Condition | Weather Variables |
|---|---|---|
| Daily | \|Pearson r\| > 0.30 with temperature or rainfall; p < 0.05 | Temperature, rainfall, humidity, UV |
| Weekly | \|Pearson r\| > 0.30 with weekly mean temperature or rainfall; p < 0.05 | Weekly mean temp, total rainfall |
| Monthly | \|Pearson r\| > 0.30 with monthly mean temperature; p < 0.05 | Monthly mean temp, rainfall, sunshine |
| Quarterly | \|Pearson r\| > 0.30 with seasonal temperature deviation; p < 0.05 | Seasonal deviation from norm |
| Yearly | \|Pearson r\| > 0.30 with annual temperature anomaly; p < 0.05 | Annual anomaly |

- **Key demand characteristics:** Demand correlated with weather conditions, often with a lag; weather-driven spikes and troughs layered on top of seasonal pattern; forecast uncertainty driven by weather forecast uncertainty
- **Differentiation from other models:** Unlike Seasonal, correlation is with weather variable values not calendar position; unlike Event Driven, weather effect is continuous not discrete

### 3. Business Impact
- **Primary risk (over-forecast):** Overstock during unexpected cold/wet summer (e.g. ice cream, beer)
- **Primary risk (under-forecast):** Stockout during unexpected heat wave (e.g. cold drinks, fans)
- **Strategic importance:** High — weather uncertainty compounds demand uncertainty; responsive supply chain critical

### 4. Priority Level
🟠 Tier 2 — High value when weather forecasts are integrated; requires external data pipeline.

### 5. Model Strategy Overview

#### 5.1 Zero-Demand Handling (Hurdle)
- Active event threshold: P(demand > 0) > 0.70 in peak weather conditions; may drop in adverse weather
- Classifier: Logistic Regression with weather threshold features
- Regressor: LightGBM with weather variables as primary features

#### 5.2 Analogue / Similarity Logic
- Analogues: Prior periods with similar weather conditions (not similar SKUs)
- k = 10 most similar weather periods in history
- Similarity: Euclidean distance on normalised weather variables (temperature, rainfall) over window

#### 5.3 Feature Engineering

**Weather Feature Construction:**
```
Temperature deviation:  temp_t − temp_seasonal_norm_t
Rainfall deviation:     rain_t − rain_seasonal_norm_t
Heat index:             Combined temperature + humidity index
Extreme weather flag:   1 if temperature > seasonal norm + 2σ
Cold snap flag:         1 if temperature < seasonal norm − 2σ
Weather forecast:       Predicted temperature/rainfall T+1 to T+H ahead
Weather lag features:   temp_{t−1}, temp_{t−2}, rain_{t−1}, rain_{t−2}
```

| Granularity | Weather Features | Lag Range | Forecast Horizon |
|---|---|---|---|
| Daily | Daily temperature, rainfall, humidity, UV, extreme flags | lag 0–3 days | 7-day weather forecast |
| Weekly | Weekly mean temp, total rainfall, frost days, heat wave flag | lag 0–2 weeks | 2-week weather forecast |
| Monthly | Monthly mean temp, total rainfall, sunshine hours, deviation from norm | lag 0–1 month | 1-month outlook |
| Quarterly | Seasonal mean temp, seasonal rainfall total, deviation | lag 0–1 quarter | Seasonal outlook |
| Yearly | Annual temp anomaly, El Niño/La Niña index | lag 0 | Annual climate forecast |

- External signals: Weather forecast API (14-day horizon), climate outlook (seasonal), historical weather database

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM with weather variables as primary features
- Configuration: Objective = reg:squarederror; Metric = WMAPE, RMSE
- Key features: Temperature (observed and forecast), rainfall, weather deviation from norm, extreme flags, seasonal index, rolling baseline mean
- When to use: Primary model — weather variables as tabular features work well with LightGBM

#### 6.2 Deep Learning (DL)
- Architectures: TFT with weather forecast as known future covariate

| Granularity | Lookback | Future Covariates | Output |
|---|---|---|---|
| Daily | 365 days | 7-day weather forecast | P10, P50, P90 |
| Weekly | 104 weeks | 2-week weather forecast | P10, P50, P90 |
| Monthly | 36 months | 1-month outlook | P10, P50, P90 |
| Quarterly | 8 quarters | Seasonal outlook | P10, P50, P90 |
| Yearly | 5 years | Annual climate forecast | P10, P50, P90 |

- Training: Loss = quantile loss; Adam lr = 0.001; Dropout = 0.1; Patience = 10
- When to use: When weather forecast feed is available as future input — critical advantage

#### 6.3 Statistical / Time Series Models
- Architectures: Dynamic Regression (ARIMAX) with weather as exogenous variable

**ARIMAX Formula:**
```
d_t = β_0 + β_temp × temp_t + β_rain × rain_t + β_extreme × extreme_t + η_t
η_t = ARIMA(p,d,q) residual
β coefficients estimated via maximum likelihood
```

- When to use: Interpretability required; coefficient quantification for weather sensitivity reporting

#### 6.4 Baseline / Fallback Model
- Fallback triggers: Weather forecast API unavailable; model convergence failure
- Fallback model: Seasonal model (ignore weather component) — conservative approach
- Logging & alerting: Alert if weather feed unavailable; alert if temperature deviation > 3σ from norm

### 7. Ensemble & Weighting

#### 7.2 Dynamic Weight Schedule

| Weather Correlation Strength | LightGBM | TFT | ARIMAX |
|---|---|---|---|
| \|r\| 0.30–0.50 | 50% | 20% | 30% |
| \|r\| 0.50–0.70 | 55% | 30% | 15% |
| \|r\| > 0.70 | 60% | 35% | 5% |

### 8. Uncertainty Quantification
- Method: Scenario quantiles — cold scenario (P10), normal scenario (P50), hot scenario (P90)
- Output: [P10, P50, P90] based on weather forecast uncertainty cone
- Use case: Safety stock = P75 in high weather-sensitivity season; P50 in low-sensitivity periods

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Extreme weather cap: min(forecast, 2 × rolling max) during heat waves
- Weather revision: Reforecast triggered automatically when 7-day weather forecast updates significantly (> 3°C deviation)
- Manual overrides: Supply chain team response to extreme weather forecast; buying team weather hedging decision

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | WMAPE Target | Weather Sensitivity R² | Bias Alert |
|---|---|---|---|
| Daily | < 22% | R² > 0.15 vs no-weather model | \|Bias\| > 10% |
| Weekly | < 20% | R² > 0.15 | \|Bias\| > 8% |
| Monthly | < 18% | R² > 0.12 | \|Bias\| > 7% |
| Quarterly | < 15% | R² > 0.10 | \|Bias\| > 6% |
| Yearly | < 12% | R² > 0.08 | \|Bias\| > 5% |

- Secondary KPI: WMAPE improvement vs seasonal-only model (must be > 5% better to justify weather data cost)

#### 10.2 Backtesting Protocol

| Granularity | Method | Train | Test |
|---|---|---|---|
| Daily | Rolling window | 365 days | 30 days |
| Weekly | Rolling window | 104 weeks | 13 weeks |
| Monthly | Rolling window | 36 months | 6 months |
| Quarterly | Rolling window | 8 quarters | 2 quarters |
| Yearly | Expanding window | All available | 1 year |

#### 10.3 Retraining & Data Freshness

| Granularity | Cadence | Weather Feed Update | Latency |
|---|---|---|---|
| Daily | Daily + weather forecast update | Every 6 hours | T+4 hours |
| Weekly | Weekly + weekly forecast update | Daily | T+1 day |
| Monthly | Monthly + monthly outlook | Weekly | T+2 days |
| Quarterly | Quarterly + seasonal outlook | Monthly | T+3 days |
| Yearly | Annually | Annually | T+7 days |

### 11. Exception Handling & Overrides
- Automatic exception detection: Weather API feed failure → fallback to seasonal model; temperature deviation > 3σ → trigger reforecast; demand deviation > 2σ from weather-adjusted forecast → investigate supply constraint
- Manual override: Buyer weather hedging decision; contingency stock for extreme weather

### 12. Reclassification / Model Selection
- Remove Weather Driven driver: If \|r\| drops below 0.20 for 2 consecutive years
- Add Seasonal driver: Weather driver often co-exists with seasonality — test both simultaneously
- Add Event Driven driver: Extreme weather events (floods, droughts) treated as events

### 13. Review Cadence
- Performance monitoring: Daily in peak weather-sensitive season; weekly otherwise
- Model review meeting: Monthly weather sensitivity review; seasonal outlook briefing
- Full model re-evaluation: Annually at season start; after any climate anomaly year

---

## D5 · Customer Driven

### 1. Definition
Predicts demand for SKUs where demand is highly concentrated among a small number of customers (HHI > 0.60), requiring customer-level forecasting and key account planning integration to avoid concentration risk mismanagement.

### 2. Detailed Description
- **Applicable scenarios:** B2B key account supply, single-customer dependency, distributor-led demand, strategic account categories
- **Boundaries:**

| Granularity | Detection Condition | Computation Window |
|---|---|---|
| Daily | HHI > 0.60 OR top-3 customers > 60% of demand | Rolling 90-day |
| Weekly | HHI > 0.60 OR top-3 customers > 60% of demand | Rolling 52-week |
| Monthly | HHI > 0.60 OR top-3 customers > 60% of demand | Rolling 12-month |
| Quarterly | HHI > 0.60 OR top-3 customers > 60% of demand | Rolling 4-quarter |
| Yearly | HHI > 0.60 OR top-3 customers > 60% of demand | Rolling 3-year |

- **Key demand characteristics:** Demand shaped by few large customers; ordering patterns reflect customer procurement cycles not end-consumer behaviour; single customer loss is catastrophic
- **Differentiation from other models:** Unlike other segments driven by market forces, demand here is shaped by individual customer decisions; customer forecast is more reliable than statistical model at this concentration level

### 3. Business Impact
- **Primary risk (over-forecast):** Customer churn leaves large inventory with no alternative demand
- **Primary risk (under-forecast):** Failure to service key account — contract penalty or relationship loss
- **Strategic importance:** Very high — key account revenue concentration means single forecast error has outsized P&L impact

### 4. Priority Level
🔴 Tier 1 — Key account demand is mission-critical; customer-level forecast is more valuable than statistical model.

### 5. Model Strategy Overview

#### 5.1 Customer-Level Decomposition
- Decompose total SKU demand into customer-level components
- Forecast each key account separately; sum to total
- Threshold: Model top customers individually if they represent > 10% of SKU demand each

#### 5.2 Analogue / Similarity Logic
- Analogues: Similar customers in same category (by order pattern, size, frequency)
- k = 3 analogues per key customer

#### 5.3 Feature Engineering

**Customer-Level Features:**
```
Customer share:         Customer_i demand / Total SKU demand (rolling window)
HHI:                   Σ(s_i)² across all customers
Customer order freq:   ADI computed at customer level
Customer order size:   CV² computed at customer level
Customer tenure:       Periods since first order
Customer contract:     Contract flag (contracted volume vs spot)
Churn risk score:      Based on order frequency change, complaints, contract expiry
```

| Granularity | Customer Features | Market Features |
|---|---|---|
| Daily | Customer daily order flag, days since last order, daily order size, contract flag | Category demand index, competitor availability |
| Weekly | Customer weekly order flag, weeks since last order, weekly order size, contract renewal week | Category trend |
| Monthly | Customer monthly order, months since last order, monthly volume, contract expiry flag | Market share index |
| Quarterly | Customer quarterly volume, HHI trend, contract status | Category quarterly index |
| Yearly | Customer annual volume, HHI, tenure, contract renewal | Annual market share |

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM trained at customer × SKU level for key accounts; aggregate model for tail accounts
- Configuration: Objective = reg:absoluteerror; Metric = MAE per customer
- Key features: Customer order history features, contract status, churn risk, category demand index
- When to use: Primary model for key accounts with ≥ 6 months order history

#### 6.2 Deep Learning (DL)
- Architectures: DeepAR trained across customer portfolio for cross-customer learning

| Granularity | Lookback | Customer Features |
|---|---|---|
| Daily | 180 days | 10 per customer |
| Weekly | 52 weeks | 10 per customer |
| Monthly | 24 months | 8 per customer |
| Quarterly | 8 quarters | 6 per customer |
| Yearly | 5 years | 5 per customer |

#### 6.3 Statistical / Time Series Models
- Architectures: Croston (if customer orders are intermittent) or ETS (if regular)
- Apply at customer level; aggregate to SKU total

#### 6.4 Baseline / Fallback Model
- Fallback: Customer rolling mean order × expected order frequency
- Critical alert if key account (> 30% share) misses expected order

### 7. Ensemble & Weighting

| Customer Share | LightGBM | DeepAR | Statistical |
|---|---|---|---|
| > 30% (key account) | 70% | 20% | 10% |
| 10–30% (major account) | 50% | 30% | 20% |
| < 10% (tail) | 20% | 20% | 60% |

### 8. Uncertainty Quantification
- Method: Customer scenario analysis — customer orders vs does not order
- Output: [P10 (key customer churn), P50 (base), P90 (key customer volume spike)]
- Use case: Safety stock = P75; concentration risk report = P10 scenario

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Concentration risk flag: Alert if single customer > 40% of SKU demand
- Customer churn rule: If key customer misses 2+ consecutive expected orders → reforecast at P25
- Manual overrides: Account manager customer volume commitment input; contract signed/cancelled flag
- Alignment: Align with CRM pipeline and account plan

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | Total WMAPE Target | Key Account MAE | HHI Threshold Alert | Bias Alert |
|---|---|---|---|---|
| Daily | < 20% | < 15% of customer mean | HHI > 0.80 = critical alert | \|Bias\| > 10% |
| Weekly | < 18% | < 12% | HHI > 0.80 | \|Bias\| > 8% |
| Monthly | < 15% | < 10% | HHI > 0.80 | \|Bias\| > 7% |
| Quarterly | < 12% | < 8% | HHI > 0.80 | \|Bias\| > 6% |
| Yearly | < 10% | < 6% | HHI > 0.80 | \|Bias\| > 5% |

#### 10.2 Backtesting Protocol

| Granularity | Method | Train | Test |
|---|---|---|---|
| Daily | Rolling window per customer | 180 days | 30 days |
| Weekly | Rolling window per customer | 52 weeks | 13 weeks |
| Monthly | Rolling window per customer | 24 months | 6 months |
| Quarterly | Rolling window per customer | 8 quarters | 2 quarters |
| Yearly | Expanding window | All available | 1 year |

#### 10.3 Retraining & Data Freshness

| Granularity | Cadence | Latency |
|---|---|---|
| Daily | Daily | T+4 hours |
| Weekly | Weekly | T+1 day |
| Monthly | Monthly | T+2 days |
| Quarterly | Quarterly | T+3 days |
| Yearly | Annually | T+7 days |

### 11. Exception Handling & Overrides
- Automatic exception detection: HHI rises above 0.80 → critical concentration alert; key account misses 2 consecutive orders → reforecast trigger; new customer > 10% share detected → add to key account model
- Manual override: Account manager volume commitment; contract signed/cancelled flag
- Override expiration: Per order cycle

### 12. Reclassification / Model Selection
- Remove Customer Driven driver: HHI drops below 0.40 for 4 consecutive periods (demand diversified)
- Escalate: HHI > 0.80 → escalate to executive risk report

### 13. Review Cadence
- Performance monitoring: Weekly key account order tracking; monthly HHI trend
- Model review meeting: Monthly key account review with sales team
- Full model re-evaluation: Quarterly or on key account contract renewal/loss

---

## D6 · Supply Constrained

### 1. Definition
Predicts true (unconstrained) demand for SKUs where historical observed demand is systematically below true demand due to supply stockouts, ensuring forecasts reflect genuine customer appetite rather than corrupted supply-limited actuals.

### 2. Detailed Description
- **Applicable scenarios:** Frequently out-of-stock SKUs, supply-limited launches, allocation periods, supply chain disrupted categories
- **Boundaries:**

| Granularity | Detection Condition | Window |
|---|---|---|
| Daily | Stockout days > 5 in rolling 90-day window | 90-day rolling |
| Weekly | Stockout weeks > 4 in rolling 52-week window | 52-week rolling |
| Monthly | Stockout months > 2 in rolling 12-month window | 12-month rolling |
| Quarterly | Stockout quarters > 1 in rolling 4-quarter window | 4-quarter rolling |
| Yearly | Stockout years > 1 in rolling 3-year window | 3-year rolling |

- **Key demand characteristics:** Observed demand systematically understates true demand; pent-up demand post-stockout; lost sales not captured in demand signal
- **Differentiation from other models:** Unlike all other segments, this is a **data correction driver** not a demand shape driver — the primary function is to reconstruct unconstrained demand before any other model is applied

### 3. Business Impact
- **Primary risk (over-forecast of unconstrained):** Safety stock set too high post-correction
- **Primary risk (under-correction):** Forecast trained on constrained demand perpetuates stockout cycle
- **Strategic importance:** Critical — supply-constrained forecasts trained on raw actuals are systematically biased downward; this corrupts safety stock, reorder points, and capacity planning

### 4. Priority Level
🔴 Tier 1 — Must be corrected before any other model is applied; uncorrected supply constraint silently corrupts all downstream forecasting.

### 5. Model Strategy Overview

#### 5.1 Lost Sales Reconstruction (Primary Step)
- Step 1: Flag all stockout periods using inventory on hand data
- Step 2: Estimate lost sales in each stockout period
- Step 3: Replace observed demand with unconstrained demand estimate
- Step 4: Apply standard behavior model on corrected demand series

**Lost Sales Estimation Methods:**

```
Method 1 — Fill Rate Adjustment (when order data available):
  d_unconstrained(t) = d_observed(t) / Fill_Rate(t)
  Fill_Rate(t) = Units_Shipped(t) / Units_Ordered(t)

Method 2 — Pre-Stockout Trend Extrapolation (when order data unavailable):
  d_unconstrained(t) = d_rolling_mean(t−1 to t−w, excl. stockout periods)
  where w = medium rolling window for granularity

Method 3 — Post-Stockout Pent-Up Demand (supplementary signal):
  Pent-up demand = Mean(d_{t+1} to d_{t+k}) − rolling mean, for k periods post-stockout
  Lost sales proxy = Pent-up demand × stockout duration ratio

Method 4 — Category Index (when no inventory data):
  d_unconstrained(t) = d_observed(t) × (Category_growth_rate_t / SKU_growth_rate_pre_stockout)
```

| Granularity | Preferred Method | Fallback Method |
|---|---|---|
| Daily | Fill Rate Adjustment (Method 1) | Pre-Stockout Extrapolation (Method 2) |
| Weekly | Fill Rate Adjustment (Method 1) | Pre-Stockout Extrapolation (Method 2) |
| Monthly | Fill Rate Adjustment (Method 1) | Post-Stockout Pent-Up (Method 3) |
| Quarterly | Category Index (Method 4) | Pre-Stockout Extrapolation (Method 2) |
| Yearly | Category Index (Method 4) | Pre-Stockout Extrapolation (Method 2) |

#### 5.2 Feature Engineering (Post-Correction)
- All features computed on **corrected unconstrained demand series**, not raw observed demand
- Stockout flag retained as feature in downstream model
- Stockout frequency feature: Number of stockout periods in rolling window
- Correction magnitude feature: d_unconstrained / d_observed ratio (signals correction scale)

### 6. Model Families

#### 6.1 ML: LightGBM on corrected demand series
- Additional feature: Stockout frequency, correction ratio, inventory policy flag
- When to use: After demand correction; same as standard behavior model

#### 6.2 DL: TFT on corrected demand series
- Additional covariate: Stockout flag as past observed covariate

#### 6.3 Statistical: Standard behavior model on corrected series
- Croston if intermittent; ETS if stable — applied to corrected demand

#### 6.4 Fallback: Category-level growth applied to last clean (non-stockout) demand observation

### 7. Ensemble & Weighting
- Same ensemble as underlying behavior segment applied to corrected demand
- Additional correction model weight: 10% weight to category index model as sanity check

### 8. Uncertainty Quantification
- Wider intervals during correction: [P5, P50, P95] — higher uncertainty from correction assumptions
- Standard intervals when correction validated: [P10, P50, P90]
- Use case: Safety stock set higher than standard segment due to stockout risk; reorder point elevated

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, corrected forecast)
- Correction cap: d_unconstrained ≤ 3 × d_observed (prevent over-correction)
- Correction floor: d_unconstrained ≥ d_observed (correction only upward; stockout never inflates downward)
- Manual overrides: Supply chain team stockout root cause flag; allocation policy input
- Alignment: Corrected forecast used for capacity and replenishment; observed demand used for actual sales reporting

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | Correction Accuracy | Post-Correction WMAPE | Stockout Rate Target | Bias Alert |
|---|---|---|---|---|
| Daily | Lost sales estimate within ±30% of fill-rate measure | < 25% | Stockout days < 3% | \|Bias\| > 15% |
| Weekly | Lost sales within ±25% | < 22% | Stockout weeks < 5% | \|Bias\| > 12% |
| Monthly | Lost sales within ±20% | < 18% | Stockout months < 8% | \|Bias\| > 10% |
| Quarterly | Lost sales within ±18% | < 15% | Stockout quarters < 10% | \|Bias\| > 8% |
| Yearly | Lost sales within ±15% | < 12% | Stockout years < 15% | \|Bias\| > 6% |

#### 10.2 Backtesting Protocol

| Granularity | Method | Notes |
|---|---|---|
| Daily | Rolling window on corrected series | Validate correction by comparing to fill-rate actuals where available |
| Weekly | Rolling window on corrected series | Same validation |
| Monthly | Rolling window | Same validation |
| Quarterly | Rolling window | Category index validation |
| Yearly | Expanding window | Category validation |

#### 10.3 Retraining & Data Freshness

| Granularity | Cadence | Stockout Flag Update | Latency |
|---|---|---|---|
| Daily | Daily | Real-time inventory feed | T+4 hours |
| Weekly | Weekly | Daily inventory update | T+1 day |
| Monthly | Monthly | Weekly inventory update | T+2 days |
| Quarterly | Quarterly | Monthly | T+3 days |
| Yearly | Annually | Quarterly | T+7 days |

### 11. Exception Handling & Overrides
- Automatic exception detection: Stockout rate > 20% in rolling window → escalate to supply chain; correction ratio > 3× → cap and alert; consecutive stockouts for 3+ periods → flag for root cause analysis
- Manual override: Supply team root cause and resolution timeline input; allocation policy flag; force unconstrained demand value from commercial intelligence
- Override expiration: Until stockout resolved and inventory replenished

### 12. Reclassification / Model Selection
- Remove Supply Constrained driver: Stockout rate < 2% for 6 consecutive periods — demand signal clean
- Retain flag: Even after stockout resolved, correct historical data permanently; do not revert to raw actuals
- Escalate: Chronic supply constraint (> 4 quarters) → escalate to supply strategy review

### 13. Review Cadence
- Performance monitoring: Daily stockout watchlist; weekly correction accuracy review
- Model review meeting: Weekly supply review with procurement and supply chain teams
- Full model re-evaluation: Quarterly; immediately on supply disruption resolution

---

*End of Dimension 3 · Driver Pattern*
*6 Segments Complete · D1 through D6*
