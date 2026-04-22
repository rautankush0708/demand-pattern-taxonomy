## SH4 · Slow Recovery
### 1. Definition
Predicts demand for SKUs that deviate significantly during shocks and require an extended period to return to pre-shock baseline, demanding prolonged recovery modelling, sustained safety stock buffers, and multi-horizon recovery path forecasting.

### 2. Detailed Description
- **Applicable scenarios:** Consumer confidence-dependent categories, long-habit-formation categories, B2B contract-driven demand with long cycle changes, categories requiring infrastructure rebuilding
- **Boundaries:**

| Granularity | HRT Range | Recovery Condition | Min Shock Events |
|---|---|---|---|
| Daily | 14–90 days | RR reaches 0.80 but takes 14–90 days | ≥ 1 shock event |
| Weekly | 4–13 weeks | RR reaches 0.80 but takes 4–13 weeks | ≥ 1 shock event |
| Monthly | 3–9 months | RR reaches 0.80 but takes 3–9 months | ≥ 1 shock event |
| Quarterly | 1–3 quarters | RR reaches 0.80 but takes 1–3 quarters | ≥ 1 shock event |
| Yearly | 1–2 years | RR reaches 0.80 but takes 1–2 years | ≥ 1 shock event |

- **Key demand characteristics:** Significant deviation during shock; prolonged trough or elevated demand post-shock; gradual recovery; blended forecast required across recovery horizon
- **Differentiation from other models:** Unlike Fast Recovery, return to baseline is slow; unlike Permanent Shift, demand does eventually return; unlike Step Down, recovery is upward

### 3. Business Impact
- **Primary risk (over-forecast):** Early in recovery — applying pre-shock baseline before demand has recovered
- **Primary risk (under-forecast):** Late in recovery — applying shock-era baseline when demand has already started to recover
- **Strategic importance:** High — prolonged recovery creates sustained supply chain disruption; inventory strategy must evolve along recovery path

### 4. Priority Level
🟠 Tier 2 — Extended planning horizon required; blended model across recovery path is key.

### 5. Model Strategy Overview

#### 5.1 Recovery Path Model
```
Recovery path forecast at time t (post-shock, h periods into recovery):
  F(t+h) = μ_pre × RR_forecast(h) + μ_shock × (1 − RR_forecast(h))

where RR_forecast(h) = estimated recovery rate at horizon h:
  RR_forecast(h) = 1 − e^{−λ_slow × h}
  λ_slow = ln(2) / HRT_estimated   (slow recovery rate)

Blend weight toward pre-shock baseline increases with h:
  w_pre(h) = RR_forecast(h)
  w_shock(h) = 1 − RR_forecast(h)
  F(t+h) = w_pre(h) × μ_pre + w_shock(h) × μ_shock_current
```

#### 5.2 Feature Engineering

| Granularity | Recovery Path Features | Macro Recovery Signals |
|---|---|---|
| Daily | Recovery day index, RR(h), λ_slow, HRT estimate, days since shock end, cumulative demand deficit vs pre-shock | Consumer confidence index, mobility data, retail footfall index |
| Weekly | Recovery week, RR(h), HRT estimate, weeks since shock end | Consumer confidence, industry recovery index |
| Monthly | Recovery month, RR(h), months since shock end | GDP recovery rate, consumer confidence, employment index |
| Quarterly | Recovery quarter, RR(h), quarters since shock end | GDP growth, capital expenditure index |
| Yearly | Recovery year, RR(h), years since shock end | GDP, macro recovery indicator |

### 6. Model Families

#### 6.1 ML: LightGBM trained on recovery phase data across historical slow-recovery shocks
- Key: Recovery path features dominate; macro signals supplement

#### 6.2 DL: TFT with long lookback covering full shock + early recovery periods

| Granularity | Lookback | Includes |
|---|---|---|
| Daily | 180 days | Pre-shock + full shock + early recovery |
| Weekly | 52 weeks | Pre-shock + full shock + early recovery |
| Monthly | 24 months | Pre-shock + full shock + early recovery |
| Quarterly | 8 quarters | Pre-shock + shock + early recovery |
| Yearly | 5 years | Pre-shock + shock |

#### 6.3 Statistical: Intervention model with slow exponential recovery term + macro covariate

**Slow Recovery Formula:**
```
d(t) = μ_pre × (1 − e^{−λ_slow × h}) + μ_shock × e^{−λ_slow × h} + β_macro × macro(t) + ε(t)
where h = periods since shock end
      λ_slow = recovery rate (smaller than fast recovery; longer HRT)
      macro(t) = macro recovery index (external signal)
```

#### 6.4 Fallback: Linearly interpolated blend between shock-period mean and pre-shock mean over HRT horizon

### 7. Ensemble

| Recovery Phase | LightGBM | TFT | Intervention Model |
|---|---|---|---|
| Early recovery (h < HRT/2) | 25% | 25% | 50% |
| Mid recovery (HRT/2 < h < HRT) | 40% | 30% | 30% |
| Late recovery (h > HRT) | Standard ensemble per behavior segment |

### 8. Uncertainty Quantification
- Method: Scenario-based — slow recovery / fast recovery / permanent shift
- Output:

| Scenario | Probability | Description |
|---|---|---|
| Faster recovery than expected | 20% | HRT × 0.6 |
| Base recovery path | 60% | HRT as estimated |
| Slower / permanent shift | 20% | HRT × 2 or permanent |

- Intervals: [P10, P50, P90] — widest at mid-recovery; narrows as recovery confirmed

### 9. Business Rules
- Non-negativity: max(0, forecast)
- Recovery ramp: Increase safety stock gradually as recovery progresses — step up at 25%, 50%, 75% RR milestones
- Supply commitment rule: Increase commitments proportionally to RR confidence
- Manual overrides: Macro economic input; industry recovery data; customer sentiment input

### 10. Evaluation

| Granularity | Recovery WMAPE Target | RR Forecast Accuracy | Normal WMAPE | Bias Alert |
|---|---|---|---|---|
| Daily | < 35% during recovery | RR within ±15% of actual | Per Behavior standard | \|Bias\| > 15% |
| Weekly | < 30% | RR within ±12% | Per Behavior standard | \|Bias\| > 12% |
| Monthly | < 25% | RR within ±10% | Per Behavior standard | \|Bias\| > 10% |
| Quarterly | < 22% | RR within ±8% | Per Behavior standard | \|Bias\| > 8% |
| Yearly | < 20% | RR within ±6% | Per Behavior standard | \|Bias\| > 6% |

### 11. Exception Handling
- Alert: Recovery stalls at RR < 0.50 for 2× HRT → reclassify to Permanent Shift or Step Down; recovery completes faster than expected → reclassify to Fast Recovery for future shocks

### 12. Reclassification

| Condition | Target | Trigger |
|---|---|---|
| Recovery confirmed within fast threshold | Fast Recovery (future shocks) | Post-recovery |
| RR never reaches 0.80; level change > ±15% | Permanent Shift / Step Down | Post-stabilisation |
| No deviation in subsequent shock | Shock Resistant | Post-shock review |

### 13. Review Cadence
- Weekly during active recovery; monthly recovery path calibration; quarterly HRT update; annual full re-evaluation

---
