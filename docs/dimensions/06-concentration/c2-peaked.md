## C2 · Peaked
### 1. Definition
Predicts demand for SKUs where demand is concentrated in one dominant period within the cycle, requiring period-specific uplift modelling and asymmetric safety stock policies to capture the peak accurately while avoiding excess inventory in non-peak periods.

### 2. Detailed Description
- **Applicable scenarios:** Holiday gift categories, summer peak products, back-to-school, Q4 budget flush categories, single-holiday driven demand
- **Boundaries:**

| Granularity | DCI_norm Threshold | Gini Threshold | Modality | Min Cycles |
|---|---|---|---|---|
| Daily | DCI_norm > 0.40 | Gini > 0.50 | 1 significant peak | ≥ 2 weekly cycles |
| Weekly | DCI_norm > 0.30 | Gini > 0.40 | 1 significant peak | ≥ 2 annual cycles |
| Monthly | DCI_norm > 0.30 | Gini > 0.40 | 1 significant peak | ≥ 2 annual cycles |
| Quarterly | DCI_norm > 0.40 | Gini > 0.50 | 1 significant peak | ≥ 2 annual cycles |
| Yearly | DCI_norm > 0.40 | Gini > 0.50 | 1 significant peak | ≥ 3 years |

- **Key demand characteristics:** One dominant demand period per cycle; remaining periods are troughs; strong seasonal index contrast between peak and non-peak; peak timing is predictable
- **Differentiation from other models:** Unlike Bi-Modal, only one significant peak; unlike Uniform, strong period concentration; unlike Skewed, the concentrated demand is at a specific known point not asymmetrically distributed

### 3. Business Impact
- **Primary risk (over-forecast):** Post-peak overstock — acute markdown pressure after single peak
- **Primary risk (under-forecast):** Stockout during the single peak — no recovery opportunity; peak is the season
- **Strategic importance:** Very high — the peak period often represents 40–70% of annual revenue for this segment

### 4. Priority Level
🔴 Tier 1 — Peak accuracy is mission-critical; one peak per cycle means one chance per year; error is unrecoverable.

### 5. Model Strategy Overview

#### 5.1 Dual-Model Approach
- **Peak model:** Applied during peak window (±n periods around peak); high-complexity model
- **Trough model:** Applied outside peak window; simpler level model
- Peak window definition:

| Granularity | Peak Window |
|---|---|
| Daily | ±3 days around peak day |
| Weekly | ±3 weeks around peak week |
| Monthly | ±1 month around peak month |
| Quarterly | Peak quarter only |
| Yearly | Peak year segment only |

#### 5.2 Analogue / Similarity Logic
- Number of analogues: k = 5 (same SKU prior years + similar category SKUs)
- Similarity criteria: Peak timing (same period ±1), peak SI magnitude ±0.2, category
- Temporal decay: weight = exp(−age / half-life)

| Granularity | Half-Life |
|---|---|
| Daily | 365 days (align to annual cycle) |
| Weekly | 52 weeks |
| Monthly | 12 months |
| Quarterly | 4 quarters |
| Yearly | 3 years |

#### 5.3 Feature Engineering

**Peak Index Features:**
```
peak_proximity(t) = exp(−|t − t_peak| / peak_half_width)
days_to_peak(t) = t_peak − t
days_since_peak(t) = t − t_peak
in_peak_window(t) = 1 if |t − t_peak| ≤ peak_window; else 0
peak_SI(period) = SI(peak_period) — the seasonal index of the peak period
trough_SI(period) = SI(trough_period)
SI_contrast = peak_SI / trough_SI  (ratio of peak to average trough)
```

| Granularity | Peak Features | Trough Features | Shared Features |
|---|---|---|---|
| Daily | Peak proximity, days to/from peak, in-peak flag, peak SI, day-of-peak pattern | Trough rolling mean (excl. peak), trough SI | Rolling mean (deseasonalised), holiday flag, promo flag |
| Weekly | Peak proximity (weeks), weeks to/from peak, in-peak flag, peak SI, week-of-peak pattern | Trough rolling mean | Rolling mean, seasonal index, promo flag |
| Monthly | Peak proximity (months), months to/from peak, in-peak flag, peak SI | Trough rolling mean | Rolling mean, seasonal index |
| Quarterly | In-peak-quarter flag, peak SI, quarters to peak | Trough rolling mean | Rolling mean |
| Yearly | In-peak-year flag, years to peak | — | Rolling mean |

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM — separate models for peak and trough periods
- Peak model: Objective = reg:squarederror; emphasis on peak period accuracy; higher weight on peak observations in training
- Trough model: Objective = reg:squarederror; emphasis on flat trough prediction
- When to use: Primary model — always applied; peak/trough split is key architectural decision

#### 6.2 Deep Learning (DL)
- Architectures: TFT with seasonal decomposition; N-BEATS with seasonality block (captures peak shape)

| Granularity | Lookback | Key Advantage | Output |
|---|---|---|---|
| Daily | 365 days (full annual cycle) | Captures day-level peak shape | P10, P50, P90 |
| Weekly | 104 weeks (2 cycles) | Learns peak week pattern | P10, P50, P90 |
| Monthly | 36 months (3 cycles) | Learns peak month profile | P10, P50, P90 |
| Quarterly | 12 quarters (3 cycles) | Learns peak quarter | P10, P50, P90 |
| Yearly | 5 years | Learns inter-year peak variation | P10, P50, P90 |

- Training: Loss = quantile loss with peak-period upweighting (×3 weight on peak periods); Adam lr = 0.001; Dropout = 0.1; Patience = 15

#### 6.3 Statistical / Time Series Models
- Architectures: ETS(A,N,A) or ETS(M,N,M) with strong seasonal component

**Seasonal Index for Peaked Demand:**
```
SI(peak_period) >> 1.0  (typically 2.0–5.0 for strongly peaked demand)
SI(trough_period) << 1.0 (typically 0.1–0.5)

Update seasonal index with low γ to preserve stable peak pattern:
  SI_new(p) = γ × (d(t) / l_t) + (1−γ) × SI_old(p)
  γ = 0.05–0.10 (lower than standard — peak SI should be stable year-on-year)

Forecast: F(t+h) = l_t × SI(period of t+h)
```

| Granularity | Seasonal Period | γ | Model |
|---|---|---|---|
| Daily | 7 (weekly peak) or 365 (annual peak) | 0.05 | TBATS or ETS(A,N,A) |
| Weekly | 52 (annual peak) | 0.07 | ETS(M,N,M) |
| Monthly | 12 (annual peak) | 0.07 | ETS(M,N,M) or SARIMA |
| Quarterly | 4 (annual peak) | 0.08 | ETS(A,N,A) |
| Yearly | — | — | Trend + SI pattern only |

- When to use: Always included — ETS seasonal models naturally capture single-peak patterns

#### 6.4 Baseline / Fallback Model
- Fallback: Prior year same period × trend adjustment factor
- Peak period fallback: Prior year peak × (1 + trend_rate) — simple and robust
- Logging & alerting: Alert if fallback deployed during peak window — P1 incident for Peaked SKUs

### 7. Ensemble & Weighting

#### 7.1 Ensemble Scheme
- Combination: D̂_t = w_lgbm × LightGBM + w_dl × TFT/NBEATS + w_ets × ETS
- Separate weights for peak vs trough periods

#### 7.2 Dynamic Weight Schedule

| Period | History | LightGBM | TFT / N-BEATS | ETS |
|---|---|---|---|---|
| Peak periods | < 3 cycles | 30% | 0% | 70% |
| Peak periods | 3–5 cycles | 40% | 30% | 30% |
| Peak periods | > 5 cycles | 40% | 35% | 25% |
| Trough periods | All | 50% | 20% | 30% |

### 8. Uncertainty Quantification
- Method: Quantile regression with asymmetric intervals (wider at peak — higher uncertainty)
- Output: [P10, P50, P90] — peak period intervals wider than trough

**Asymmetric Uncertainty:**
```
Peak period:   P90 − P50 > P50 − P10 (right-skewed uncertainty — upside risk of missed peak)
Trough period: Symmetric [P10, P90]
Pre-season buy: Use P75 for peak period stock commitment
```

- Use case: Pre-season buy = P75 of peak period forecast; post-peak run-down using P25

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Peak cap: min(peak_forecast, 3 × trough_mean × peak_SI)
- Trough floor: max(trough_forecast, 0) — allow near-zero in deep trough
- Pre-season lock: Peak period forecast locked 6–8 weeks before peak for procurement; in-season revisions to trough only
- Manual overrides: Buyer peak quantity input; early/late peak timing adjustment (±1 period)
- Alignment: Peak forecast within ±30% of prior year peak actual (wider than standard — peak variability is higher)

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | Overall WMAPE | Peak WMAPE | Trough WMAPE | Bias Alert | Peak Coverage |
|---|---|---|---|---|---|
| Daily | < 25% | < 30% | < 20% | \|Bias\| > 12% | 75% P10–P90 |
| Weekly | < 20% | < 25% | < 15% | \|Bias\| > 10% | 75% P10–P90 |
| Monthly | < 18% | < 22% | < 12% | \|Bias\| > 8% | 80% P10–P90 |
| Quarterly | < 15% | < 20% | < 10% | \|Bias\| > 6% | 80% P10–P90 |
| Yearly | < 12% | < 18% | < 8% | \|Bias\| > 5% | 80% P10–P90 |

#### 10.2 Backtesting Protocol

| Granularity | Train | Test | Peak Backtest Rule |
|---|---|---|---|
| Daily | 2 full cycles | 1 full cycle | Must include ≥ 1 full peak period |
| Weekly | 2 full cycles | 1 full cycle | Must include ≥ 1 full peak period |
| Monthly | 2 full cycles | 1 full cycle | Must include ≥ 1 full peak period |
| Quarterly | 2 full cycles | 1 full cycle | Must include ≥ 1 full peak period |
| Yearly | All available | 1 year | Must include ≥ 1 full peak |

#### 10.3 Retraining

| Granularity | Cadence | Pre-Peak Trigger | Latency |
|---|---|---|---|
| Daily | Daily | Retrain 2 weeks before peak window | T+4 hours |
| Weekly | Weekly | Retrain 4 weeks before peak window | T+1 day |
| Monthly | Monthly | Retrain 2 months before peak window | T+2 days |
| Quarterly | Quarterly | Retrain 1 quarter before peak | T+3 days |
| Yearly | Annually | Pre-season retrain | T+7 days |

### 11. Exception Handling & Overrides
- Auto-detect: Peak timing shifts > 1 period vs prior year → alert and adjust peak window; peak SI changes > 25% vs prior year → flag for buyer review; forecast misses peak by > 30% → P1 incident review
- Manual override: Buyer peak timing adjustment; early/late season call; peak magnitude input from commercial intelligence
- Override expiration: Per peak occurrence

### 12. Reclassification

| Condition | Target Segment | Holding Period |
|---|---|---|
| Second significant peak emerges for 2 cycles | Bi-Modal | 2 cycles |
| DCI_norm drops below 0.15 for 2 cycles | Uniform | 2 cycles |
| 3+ significant peaks detected | Multi-Modal | 2 cycles |
| |skewness| > 0.5 with no clear single peak | Skewed | 2 cycles |

### 13. Review Cadence
- Pre-peak review (6–8 weeks before peak); post-peak debrief within 2 weeks; annual SI calibration; quarterly monitoring

---
