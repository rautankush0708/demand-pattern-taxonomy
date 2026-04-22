# Dimension 9 · Timing Pattern
## Demand Forecasting Model Templates

---

> **Segments:** 5 · Leading · Lagging · Coincident · Deferred · Accelerated
> **Granularities:** Daily · Weekly · Monthly · Quarterly · Yearly

---

## 0.1 Timing Pattern Metrics

### A. Lead-Lag Correlation
```
Cross-correlation at lag k:
  CCF(k) = Σ[(d_t − d̄)(trigger_{t−k} − trigger̄)] / [n × σ_d × σ_trigger]

Leading:    Max CCF at k < 0 (demand moves before trigger)
Lagging:    Max CCF at k > 0 (demand moves after trigger)
Coincident: Max CCF at k = 0 (demand moves with trigger)

Significant lag: |CCF(k)| > 2/√n
```

| Granularity | Lag Range Tested | Trigger Variables |
|---|---|---|
| **Daily** | k = −30 to +30 days | Competitor price, weather, news sentiment, mobility index |
| **Weekly** | k = −13 to +13 weeks | Category trend, promotional activity, macroeconomic index |
| **Monthly** | k = −6 to +6 months | GDP, industrial output, consumer confidence |
| **Quarterly** | k = −4 to +4 quarters | GDP growth, capital expenditure |
| **Yearly** | k = −2 to +2 years | Macro economic cycle, population growth |

### B. Demand Arrival vs Expected Timing
```
Expected timing: t_expected = estimated from historical pattern or trigger date
Actual timing:   t_actual = date of demand event

Timing deviation: dev_timing = t_actual − t_expected (periods)

Leading:     Mean(dev_timing) < −1 period (demand arrives early)
Lagging:     Mean(dev_timing) > +1 period (demand arrives late)
Coincident:  |Mean(dev_timing)| ≤ 1 period (demand on time)
Deferred:    Mean(dev_timing) > granularity-specific threshold (demand significantly delayed)
Accelerated: Mean(dev_timing) < −granularity-specific threshold (demand significantly pulled forward)
```

| Granularity | Deferred Threshold | Accelerated Threshold |
|---|---|---|
| **Daily** | dev > +7 days | dev < −7 days |
| **Weekly** | dev > +3 weeks | dev < −3 weeks |
| **Monthly** | dev > +2 months | dev < −2 months |
| **Quarterly** | dev > +1 quarter | dev < −1 quarter |
| **Yearly** | dev > +1 year | dev < −1 year |

---

# PART 1 — SEGMENT TEMPLATES

## TM1 · Leading

### 1. Definition
Predicts demand for SKUs where demand moves systematically ahead of an identifiable external trigger signal, enabling anticipatory forecasting by using leading indicators to predict demand before it materialises.

### 2. Detailed Description
- **Applicable scenarios:** Housing construction materials (leads permits), baby products (leads birth rate), school supplies (leads enrolment), B2B capital goods (leads equipment orders)
- **Boundaries:**

| Granularity | Detection | Lead Time |
|---|---|---|
| Daily | Max CCF at k < 0; |CCF| > 2/√n | k = 3–30 days ahead |
| Weekly | Max CCF at k < 0; |CCF| > 2/√n | k = 1–13 weeks ahead |
| Monthly | Max CCF at k < 0; |CCF| > 2/√n | k = 1–6 months ahead |
| Quarterly | Max CCF at k < 0; |CCF| > 2/√n | k = 1–4 quarters ahead |
| Yearly | Max CCF at k < 0; |CCF| > 2/√n | k = 1–2 years ahead |

- **Key demand characteristics:** Demand precedes observable external trigger; identifies future demand before conventional signals appear; requires leading indicator data pipeline

### 3. Business Impact
- **Primary risk (over-forecast):** Leading indicator signal false positive — demand anticipated but doesn't materialise
- **Primary risk (under-forecast):** Ignoring lead time — reactive rather than anticipatory; missing demand window
- **Strategic importance:** High — leading indicators extend effective forecast horizon; competitive advantage in early procurement

### 4. Priority Level
🟠 Tier 2 — High value when leading indicator data is available; requires external data pipeline investment.

### 5. Model Strategy

#### 5.1 Feature Engineering (Leading Indicator Features)
```
lead_indicator_lag_k(t) = trigger_signal(t + k)   [future value of leading indicator]
correlation_strength = CCF(optimal_k)
lead_time_estimate = k* = argmax |CCF(k)| for k < 0
```

| Granularity | Leading Indicators | Lead Time Features |
|---|---|---|
| Daily | Consumer confidence (daily), mobility index, news sentiment score | trigger(t+3 to t+30), CCF strength, lead time stability |
| Weekly | Consumer confidence (weekly), building permits, jobless claims | trigger(t+1 to t+13 weeks), CCF strength |
| Monthly | GDP leading index, PMI, industrial orders, building permits | trigger(t+1 to t+6 months), CCF strength |
| Quarterly | GDP growth, capital expenditure plans, business investment index | trigger(t+1 to t+4 quarters) |
| Yearly | Population growth, demographic index, macro investment cycle | trigger(t+1 to t+2 years) |

### 6. Model Families

#### 6.1 ML: LightGBM with leading indicator features
- Key features: Leading indicator values at optimal lag k*, CCF strength, lead time, baseline rolling mean, seasonal index

#### 6.2 DL: TFT — leading indicators as known future covariates (unique advantage)

| Granularity | Lookback | Leading Indicator Horizon | Output |
|---|---|---|---|
| Daily | 180 days | k* days ahead | P10, P50, P90 |
| Weekly | 52 weeks | k* weeks ahead | P10, P50, P90 |
| Monthly | 24 months | k* months ahead | P10, P50, P90 |
| Quarterly | 8 quarters | k* quarters ahead | P10, P50, P90 |
| Yearly | 5 years | k* years ahead | P10, P50, P90 |

#### 6.3 Statistical: ARIMAX with leading indicator as exogenous variable at lag k*
```
d(t) = α + β × trigger(t + k*) + Σγ × controls(t) + ARIMA residual
```

#### 6.4 Fallback: Standard behavior model without leading indicator

### 7. Ensemble

| Lead Indicator Confidence | LightGBM | TFT | ARIMAX |
|---|---|---|---|
| CCF < 0.40 (weak) | 30% | 10% | 60% |
| CCF 0.40–0.60 (moderate) | 50% | 25% | 25% |
| CCF > 0.60 (strong) | 55% | 35% | 10% |

### 8. Uncertainty Quantification
- [P10, P50, P90]; wider when leading indicator has high variance

### 9. Business Rules
- Lead indicator feed: Mandatory — flag if leading indicator data delayed
- Lead time drift: Alert if optimal k* shifts > 2 periods between estimations
- Manual overrides: Macroeconomist input on leading indicator forecast; lead time estimate adjustment

### 10. Evaluation

| Granularity | WMAPE Target | Lead Indicator R² | CCF Stability | Bias Alert |
|---|---|---|---|---|
| Daily | < 22% | > 0.25 | CV(k*) < 0.30 | |Bias| > 10% |
| Weekly | < 18% | > 0.25 | CV(k*) < 0.30 | |Bias| > 8% |
| Monthly | < 15% | > 0.20 | CV(k*) < 0.30 | |Bias| > 7% |
| Quarterly | < 12% | > 0.18 | CV(k*) < 0.30 | |Bias| > 6% |
| Yearly | < 10% | > 0.15 | CV(k*) < 0.30 | |Bias| > 5% |

### 11–13. Standard protocols + quarterly lead time recalibration; annual leading indicator relevance review

---

## TM2 · Lagging

### 1. Definition
Predicts demand for SKUs where demand follows an identifiable external trigger signal with a consistent delay, enabling causal forecasting by detecting the trigger and applying the known lag to project demand.

### 2. Detailed Description
- **Applicable scenarios:** Aftermarket parts (follow equipment sales by lead time), consumables following capital equipment installation, re-order triggered by prior delivery cycle, categories driven by downstream production schedule
- **Boundaries:**

| Granularity | Detection | Lag Time |
|---|---|---|
| Daily | Max CCF at k > 0; |CCF| > 2/√n | k = 3–30 days after trigger |
| Weekly | Max CCF at k > 0; |CCF| > 2/√n | k = 1–13 weeks after |
| Monthly | Max CCF at k > 0; |CCF| > 2/√n | k = 1–6 months after |
| Quarterly | Max CCF at k > 0; |CCF| > 2/√n | k = 1–4 quarters after |
| Yearly | Max CCF at k > 0; |CCF| > 2/√n | k = 1–2 years after |

### 5. Model Strategy

#### 5.1 Feature Engineering
```
lagged_trigger(t) = trigger(t − k*)   [past value of trigger at optimal lag]
```

| Granularity | Lagged Trigger Features | Lag Features |
|---|---|---|
| Daily | trigger(t−3 to t−30 days), optimal lag k*, CCF strength | Lag stability CV(k*), lag drift indicator |
| Weekly | trigger(t−1 to t−13 weeks) | k*, CCF, lag drift |
| Monthly | trigger(t−1 to t−6 months) | k*, CCF |
| Quarterly | trigger(t−1 to t−4 quarters) | k*, CCF |
| Yearly | trigger(t−1 to t−2 years) | k*, CCF |

### 6. Model Families

#### 6.1 ML: LightGBM with lagged trigger features
#### 6.2 DL: TFT — lagged triggers as past observed covariates
#### 6.3 Statistical: ARIMAX with lagged exogenous variable

```
d(t) = α + β × trigger(t − k*) + ARIMA residual
k* = argmax |CCF(k)| for k > 0
```

### 7. Ensemble — same structure as TM1 Leading (by CCF strength)

### 8–10. Evaluation

| Granularity | WMAPE Target | Lag R² | Bias Alert |
|---|---|---|---|
| Daily | < 22% | > 0.25 | |Bias| > 10% |
| Weekly | < 18% | > 0.25 | |Bias| > 8% |
| Monthly | < 15% | > 0.20 | |Bias| > 7% |
| Quarterly | < 12% | > 0.18 | |Bias| > 6% |
| Yearly | < 10% | > 0.15 | |Bias| > 5% |

### 11–13. Standard protocols + quarterly lag recalibration

---

## TM3 · Coincident

### 1. Definition
Predicts demand for SKUs where demand moves simultaneously with an identifiable external trigger signal (max CCF at k = 0), requiring real-time external signal integration for contemporaneous demand forecasting.

### 2. Detailed Description
- **Applicable scenarios:** Weather-sensitive categories (temperature = same-day demand), real-time event demand, POS-driven replenishment, same-day consumption-purchase correlation

### 5. Model Strategy

#### 5.1 Feature Engineering
```
contemporaneous_trigger(t) = trigger(t)   [same-period trigger value]
CCF(0) = contemporaneous correlation strength
```

| Granularity | Contemporaneous Features |
|---|---|
| Daily | Same-day temperature, mobility index, event flag, POS data feed (same day) |
| Weekly | Same-week weather index, same-week event flag, same-week POS |
| Monthly | Same-month economic index, same-month category trend |
| Quarterly | Same-quarter GDP component, same-quarter category trend |
| Yearly | Same-year macro indicator, same-year demographic index |

### 6. Model Families

#### 6.1 ML: LightGBM with contemporaneous trigger
#### 6.2 DL: TFT with real-time covariate integration
#### 6.3 Statistical: ARIMAX(k=0 external regressor)

### Evaluation

| Granularity | WMAPE Target | Trigger R² | Bias Alert |
|---|---|---|---|
| Daily | < 20% | > 0.30 | |Bias| > 8% |
| Weekly | < 17% | > 0.25 | |Bias| > 7% |
| Monthly | < 14% | > 0.20 | |Bias| > 6% |
| Quarterly | < 11% | > 0.18 | |Bias| > 5% |
| Yearly | < 9% | > 0.15 | |Bias| > 4% |

---

## TM4 · Deferred

### 1. Definition
Predicts demand for SKUs where customer decision cycles cause demand to arrive significantly later than the triggering event, requiring extended post-trigger forecast horizons and patience-adjusted demand models.

### 2. Detailed Description
- **Applicable scenarios:** B2B capital procurement (long approval cycles), large project-based orders, demand delayed by regulatory approvals, consumer electronics with long consideration cycles

### 5. Model Strategy

#### 5.1 Deferral Model
```
Demand at time t arrives from triggers at times t−L_1, t−L_2, ..., t−L_max
Deferral distribution: P(demand arrives at lag L) = f(L) (empirically estimated)
F(t) = Σ P(demand at lag L) × trigger(t − L) × β_conversion
```

| Granularity | Deferral Distribution Window | Min Deferral Events |
|---|---|---|
| Daily | Lag 7–90 days | ≥ 5 events |
| Weekly | Lag 3–26 weeks | ≥ 5 events |
| Monthly | Lag 2–12 months | ≥ 5 events |
| Quarterly | Lag 1–4 quarters | ≥ 4 events |
| Yearly | Lag 1–3 years | ≥ 3 events |

### 6. Model Families

#### 6.1 ML: LightGBM with deferral distribution features (trigger × lag weight)
#### 6.2 DL: TFT with distributed lag encoding
#### 6.3 Statistical: Distributed lag model (Almon or Koyck lag structure)

**Koyck Distributed Lag:**
```
d(t) = α + β × trigger(t) + λ × d(t−1) + ε(t)
λ ∈ (0,1) = geometric decay factor
Mean lag = λ / (1−λ)   [average deferral period]
```

### Evaluation

| Granularity | WMAPE Target | Deferral Distribution Accuracy | Bias Alert |
|---|---|---|---|
| Daily | < 28% | Distribution within ±15% | |Bias| > 12% |
| Weekly | < 24% | Distribution within ±12% | |Bias| > 10% |
| Monthly | < 20% | Distribution within ±10% | |Bias| > 8% |
| Quarterly | < 17% | Distribution within ±8% | |Bias| > 6% |
| Yearly | < 14% | Distribution within ±6% | |Bias| > 5% |

---

## TM5 · Accelerated

### 1. Definition
Predicts demand for SKUs where customers pull forward purchases ahead of the expected timing — driven by anticipated price increases, supply scarcity signals, or promotional end-dates — creating artificial spikes followed by demand troughs.

### 2. Detailed Description
- **Applicable scenarios:** Pre-price-increase buying, end-of-promotion stockpiling, pre-shortage panic buying, fiscal year-end budget flush purchasing

### 5. Model Strategy

#### 5.1 Acceleration-Trough Model
```
Acceleration period: d_accel(t) = d_baseline(t) × (1 + accel_factor)
Post-acceleration trough: d_trough(t) = d_baseline(t) × (1 − trough_factor × e^{−λ_trough × h})
where h = periods after acceleration event ends
accel_factor and trough_factor estimated from historical acceleration events
Net demand: Σ d_accel + Σ d_trough = Σ d_baseline (demand conserved — only timing changes)
```

| Granularity | Acceleration Trigger | Post-Trough Duration |
|---|---|---|
| Daily | Price increase announcement > 3 days ahead | 7–21 days |
| Weekly | Promo end within 2 weeks; supply shortage signal | 2–6 weeks |
| Monthly | Price increase > 1 month ahead; policy change | 1–3 months |
| Quarterly | Annual price increase announcement | 1–2 quarters |
| Yearly | Regulatory change > 1 year ahead | 6–18 months |

### 6. Model Families

#### 6.1 ML: LightGBM with acceleration trigger features + post-trough features
#### 6.2 DL: TFT with known future acceleration triggers as covariates
#### 6.3 Statistical: Intervention model with acceleration impulse + trough correction

### Evaluation

| Granularity | Accel WMAPE | Trough WMAPE | Net Demand Conservation | Bias Alert |
|---|---|---|---|---|
| Daily | < 35% | < 30% | ±10% of baseline total | |Bias| > 15% |
| Weekly | < 30% | < 25% | ±8% | |Bias| > 12% |
| Monthly | < 25% | < 20% | ±6% | |Bias| > 10% |
| Quarterly | < 22% | < 18% | ±5% | |Bias| > 8% |
| Yearly | < 18% | < 15% | ±4% | |Bias| > 6% |
