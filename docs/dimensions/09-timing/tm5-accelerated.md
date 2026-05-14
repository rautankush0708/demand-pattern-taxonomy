# Segment Model Template

## Dimension 9 · Accelerated

---

### 1. Definition
Predicts demand for SKUs where customers systematically pull forward purchases ahead of expected timing — driven by anticipated price increases, supply scarcity signals, or promotional end-dates — creating demand spikes followed by compensating troughs.

### 2. Detailed Description
- **Applicable scenarios:** Pre-price-increase buying, end-of-promotion stockpiling, pre-shortage panic buying, fiscal year-end budget flush purchasing, pre-tariff buying
- **Boundaries:**

| Granularity | Detection Condition | Acceleration Window | Post-Trough Duration |
|---|---|---|---|
| Daily | Mean(dev_timing) < −7 days; spike > 1.5σ followed by trough | ±7 days of trigger | 7–21 days |
| Weekly | Mean(dev_timing) < −3 weeks; spike followed by trough | ±3 weeks | 2–6 weeks |
| Monthly | Mean(dev_timing) < −2 months; spike followed by trough | ±2 months | 1–3 months |
| Quarterly | Mean(dev_timing) < −1 quarter; spike followed by trough | ±1 quarter | 1–2 quarters |
| Yearly | Mean(dev_timing) < −1 year; spike followed by trough | ±6 months | 6–18 months |

- **Key demand characteristics:** Demand spike precedes trigger event (price rise, promo end, scarcity); post-acceleration trough as customers work through stockpile; net demand conserved — only timing changes
- **Differentiation from other models:** Unlike Leading, acceleration is a customer response to a future signal — demand is pulled forward voluntarily; unlike standard promotions, the spike is driven by anticipation not price reduction

### 3. Business Impact
- **Primary risk (over-forecast):** Ordering during post-acceleration trough using pre-acceleration baseline — excess inventory
- **Primary risk (under-forecast):** Missing acceleration spike — stockout during buying surge
- **Strategic importance:** High — acceleration events create acute short-term supply pressure; correct modelling prevents both overstock and stockout

### 4. Priority Level
🔴 **Tier 1** — Acceleration spikes are acute; both over and under-forecast consequences are severe within a short window.

### 5. Model Strategy Overview

#### 5.1 Acceleration-Trough Model
```
Acceleration phase (before trigger):
  d_accel(t) = d_baseline(t) × (1 + accel_factor)
  accel_factor estimated from historical acceleration events

Post-acceleration trough (after trigger):
  d_trough(t) = d_baseline(t) × (1 − trough_factor × e^{−λ_trough × h})
  h = periods after acceleration event ends
  λ_trough = trough recovery rate

Demand conservation:
  Σ d_accel = Σ d_trough + Σ d_baseline_equivalent
  Net demand is conserved — only timing changes
```

#### 5.2 Analogue / Similarity Logic
- k = 5 (prior acceleration events of same trigger type in same category)
- Similarity: Trigger type (price/scarcity/promo-end), accel_factor ±0.10, category
- Temporal decay: weight = exp(−age / half-life)

| Granularity | Half-Life |
|---|---|
| Daily | 90 days |
| Weekly | 13 weeks |
| Monthly | 6 months |
| Quarterly | 3 quarters |
| Yearly | 2 years |

#### 5.3 Feature Engineering

**Acceleration Feature Construction:**
```
accel_trigger(t) = price_increase_announced OR promo_end_approaching OR scarcity_signal
days_to_trigger(t) = t_trigger − t_current
in_accel_window(t) = 1 if within acceleration window before trigger
in_trough_window(t) = 1 if within post-trough window after trigger
accel_factor = mean historical demand uplift during acceleration
trough_factor = mean historical demand deficit during trough
post_trough_day = t − t_trigger_end
```

| Granularity | Acceleration Features | Trough Features | Baseline Features |
|---|---|---|---|
| Daily | Trigger flag, days to trigger, accel window flag, accel_factor, trigger type | Post-trough flag, post-trough day, trough_factor, λ_trough | 7/30/90-day rolling mean, seasonal index |
| Weekly | Same structure weekly | Same weekly | 4/8/13-week rolling mean |
| Monthly | Same monthly | Same monthly | 3/6/12-month rolling mean |
| Quarterly | Trigger flag, quarters to trigger | Post-trough quarter flag | 2/4-quarter rolling mean |
| Yearly | Trigger flag, years to trigger | Post-trough flag | Annual rolling mean |

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM — separate models for acceleration, trough, and baseline periods
- Configuration: Objective = reg:squarederror; Metric = WMAPE, Net Demand Conservation
- Key features: Acceleration trigger flag, days to trigger, accel_factor, post-trough day, trough_factor, baseline rolling mean
- When to use: Primary model when ≥ 3 historical acceleration events available

#### 6.2 Deep Learning (DL)
- Architectures: TFT with acceleration trigger as known future covariate

| Granularity | Lookback | Future Covariate | Output |
|---|---|---|---|
| Daily | 180 days | Trigger date + type 30 days ahead | P10, P50, P90 |
| Weekly | 52 weeks | Trigger date 8 weeks ahead | P10, P50, P90 |
| Monthly | 24 months | Trigger date 3 months ahead | P10, P50, P90 |
| Quarterly | 8 quarters | Trigger 1 quarter ahead | P10, P50, P90 |
| Yearly | 5 years | Annual trigger calendar | P10, P50, P90 |

#### 6.3 Statistical / Time Series Models
- Architectures: Intervention model with acceleration impulse and trough correction

**Acceleration Intervention Model:**
```
d(t) = baseline(t)
      + β_accel × accel_indicator(t)
      + β_trough × trough_decay(t)
      + ARIMA residual

trough_decay(t) = −accel_magnitude × e^{−λ_trough × (t − t_trigger_end)}
β_accel estimated from historical acceleration events
λ_trough = trough recovery rate (estimated from historical trough periods)
```

#### 6.4 Baseline / Fallback Model
- Fallback: Pre-trigger baseline rolling mean; apply accel_factor = category average if trigger detected but no history
- Alert if acceleration trigger detected without model coverage

### 7. Ensemble & Weighting

#### 7.2 Dynamic Weight Schedule

| Phase | Prior Acceleration Events | LightGBM | TFT | Intervention |
|---|---|---|---|---|
| Acceleration phase | < 3 events | 20% | 20% | 60% |
| Acceleration phase | ≥ 3 events | 50% | 25% | 25% |
| Trough phase | < 3 events | 20% | 20% | 60% |
| Trough phase | ≥ 3 events | 50% | 25% | 25% |
| Baseline phase | Any | Standard behavior ensemble |

### 8. Uncertainty Quantification
- Method: Scenario analysis across acceleration magnitude and trough depth
- Output:

| Scenario | Description | P-level |
|---|---|---|
| Mild acceleration | 10–20% uplift; shallow trough | P25 |
| Base acceleration | Historical mean accel_factor | P50 |
| Strong acceleration | 30–50% uplift; deep trough | P75 |

- Use case: Pre-trigger stock build at P75; post-trigger run-down at P25

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Acceleration cap: min(accel_forecast, baseline × (1 + max_historical_accel_factor × 1.2))
- Trough floor: max(trough_forecast, baseline × 0.3) — prevent over-correction to near-zero
- Net demand conservation check: Σ forecast over (accel + trough) window ≈ Σ baseline × same window ± 10%
- Supply commitment rule: Do not commit additional supply during trough — demand will recover to baseline
- Manual overrides: Commercial team trigger confirmation; magnitude estimate input; trough duration adjustment

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | Accel WMAPE | Trough WMAPE | Conservation Check | Baseline WMAPE | Bias Alert |
|---|---|---|---|---|---|
| Daily | < 35% | < 30% | ±10% of baseline total | Per behavior std | \|Bias\| > 15% |
| Weekly | < 30% | < 25% | ±8% | Per behavior std | \|Bias\| > 12% |
| Monthly | < 25% | < 20% | ±6% | Per behavior std | \|Bias\| > 10% |
| Quarterly | < 22% | < 18% | ±5% | Per behavior std | \|Bias\| > 8% |
| Yearly | < 18% | < 15% | ±4% | Per behavior std | \|Bias\| > 6% |

#### 10.2 Backtesting Protocol

| Granularity | Method | Train | Test |
|---|---|---|---|
| Daily | Leave-one-acceleration-event-out | All events except last | Last event (accel + trough) |
| Weekly | Leave-one-event-out | All except last | Last event |
| Monthly | Leave-one-event-out | All except last | Last event |
| Quarterly | Leave-one-event-out | All except last | Last event |
| Yearly | Leave-one-event-out | All except last | Last event |

#### 10.3 Retraining

| Granularity | Cadence | Trigger | Latency |
|---|---|---|---|
| Daily | Daily | On trigger announcement | T+4 hours |
| Weekly | Weekly | On trigger announcement | T+1 day |
| Monthly | Monthly | On trigger announcement | T+2 days |
| Quarterly | Quarterly | On trigger announcement | T+3 days |
| Yearly | Annually | On trigger announcement | T+7 days |

### 11. Exception Handling & Overrides
- Auto-detect: Acceleration spike detected without trigger flag → investigate unlisted trigger; trough deeper than expected → check if pent-up demand released or genuine demand loss; net demand not conserved (> ±15%) → alert and remodel
- Manual override: Commercial team trigger magnitude revision; supply team trough duration input; finance team net demand conservation check
- Override expiration: Per acceleration event occurrence

### 12. Reclassification / Model Selection

| Condition | Target | Holding Period |
|---|---|---|
| Acceleration events disappear for 2 full years | Coincident or Lagging | 2 years |
| Trough does not materialise post-acceleration (3+ events) | Leading (demand genuinely leads) | 3 events |
| Acceleration becomes demand-destroying not timing-shifting | Shock Sensitive (Dim 7) | 2 events |

### 13. Review Cadence
- Per acceleration event debrief within 2 weeks of trough resolution; quarterly accel_factor recalibration; annual trigger type review

---

*End of Dimension 9 · Timing Pattern*
*5 Segments Complete · TM1 through TM5*

---
