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

