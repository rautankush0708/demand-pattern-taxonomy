## SH3 · Fast Recovery

### 1. Definition
Predicts demand for SKUs that exhibit significant shock deviation but return to pre-shock baseline rapidly (within the fast recovery threshold), allowing short-horizon shock correction and return to standard modelling quickly.

### 2. Detailed Description
- **Applicable scenarios:** Discretionary categories with strong underlying need, weather-disrupted categories, short-duration supply disruptions, elastic demand with quick consumer readjustment
- **Boundaries:**

| Granularity | HRT Threshold | Recovery Condition | Min Shock Events |
|---|---|---|---|
| Daily | HRT < 14 days | RR > 0.80 within 14 days of shock end | ≥ 1 shock event |
| Weekly | HRT < 4 weeks | RR > 0.80 within 4 weeks of shock end | ≥ 1 shock event |
| Monthly | HRT < 3 months | RR > 0.80 within 3 months of shock end | ≥ 1 shock event |
| Quarterly | HRT < 1 quarter | RR > 0.80 within 1 quarter of shock end | ≥ 1 shock event |
| Yearly | HRT < 1 year | RR > 0.80 within 1 year of shock end | ≥ 1 shock event |

- **Key demand characteristics:** Sharp deviation during shock; rapid return to baseline; possible pent-up demand spike post-shock (over-recovery: RR > 1.0); normalises within recovery horizon
- **Differentiation from other models:** Unlike Shock Resistant, deviation does occur; unlike Slow Recovery, return is rapid; unlike Permanent Shift, demand returns to original baseline

### 3. Business Impact
- **Primary risk (over-forecast):** Ordering during shock using pre-shock baseline — not needed as recovery is fast
- **Primary risk (under-forecast):** Missing post-shock pent-up demand surge — over-recovery spike
- **Strategic importance:** Medium-high — fast recovery means short-duration impact; supply chain agility is the key requirement

### 4. Priority Level
🟠 Tier 2 — Short-duration impact; agility and rapid model response more important than complex shock modelling.

### 5. Model Strategy Overview

#### 5.1 Three-Phase Model
```
Phase 1 (Shock): Active during shock period
  Model: Shock-adjusted baseline (reduced/elevated per shock direction)
  Forecast: μ_pre × shock_factor  where shock_factor = mean historical shock ratio

Phase 2 (Recovery): Active from shock end to HRT
  Model: Recovery interpolation
  Forecast: μ_pre × [shock_factor + (1 − shock_factor) × RR(h)]
  where RR(h) = (1 − e^{−recovery_rate × h}) [exponential recovery curve]

Phase 3 (Post-recovery): Active after RR > 0.80
  Model: Standard behavior model — return to normal
  Pent-up demand adjustment: If RR spikes above 1.0 post-shock → capture with pent-up demand feature
```

#### 5.2 Feature Engineering

| Granularity | Shock Phase Features | Recovery Phase Features | Normal Phase Features |
|---|---|---|---|
| Daily | Shock flag, shock severity, shock type, shock day index, historical shock ratio | Recovery day index, RR(h), expected recovery curve, pent-up demand indicator | Standard behavior features |
| Weekly | Shock flag, severity, type, shock week index, historical ratio | Recovery week index, RR(h), pent-up indicator | Standard features |
| Monthly | Shock flag, severity, shock month index | Recovery month index, RR(h), pent-up indicator | Standard features |
| Quarterly | Shock flag, severity | Recovery quarter index, RR(h) | Standard features |
| Yearly | Shock flag, severity | Recovery year index | Standard features |

**Recovery Curve Formula:**
```
Exponential recovery:
  RR(h) = 1 − e^{−λ × h}
  λ = recovery rate = ln(2) / HRT   (estimated from historical shock events)

Pent-up demand factor:
  PUD = max(0, RR_observed(h) − 1.0)   [amount of over-recovery]
  PUD_forecast = PUD_historical_mean × shock_severity_ratio
```

### 6. Model Families

#### 6.1 ML: LightGBM — phase-specific models (3 models: shock / recovery / normal)
- Recovery model: Objective = reg:squarederror; recovery curve features as primary inputs

#### 6.2 DL: TFT — captures recovery dynamics in sequence

| Granularity | Lookback | Recovery Covariates |
|---|---|---|
| Daily | 180 days | Recovery day, RR curve, pent-up flag |
| Weekly | 52 weeks | Recovery week, RR curve |
| Monthly | 24 months | Recovery month, RR |
| Quarterly | 8 quarters | Recovery quarter, RR |
| Yearly | 5 years | Recovery year |

#### 6.3 Statistical: Intervention model with exponential recovery term

**Recovery Intervention Model:**
```
d(t) = baseline(t) + β_shock × shock_indicator(t)
       + β_recovery × recovery_curve(t) + β_pud × pent_up(t) + ε(t)

recovery_curve(t) = −shock_magnitude × e^{−λ × (t − t_shock_end)}
pent_up(t) = max(0, 1 − e^{−λ_pud × (t − t_shock_end)}) × pud_magnitude
```

#### 6.4 Fallback: Pre-shock rolling mean applied from shock end (assumes instant recovery)

### 7. Ensemble

| Phase | LightGBM | TFT | Intervention Model |
|---|---|---|---|
| Shock phase | 30% | 20% | 50% |
| Recovery phase | 40% | 30% | 30% |
| Normal phase | Standard ensemble per behavior segment |

### 8. Uncertainty Quantification
- Shock phase: [P5, P50, P95] — wide during shock
- Recovery phase: Narrowing from [P10, P50, P90] to standard as recovery confirmed
- Post-recovery: Standard [P10, P50, P90]
- Pent-up demand scenario: P90 includes pent-up spike; P10 excludes it

### 9. Business Rules
- Non-negativity: max(0, forecast)
- Recovery hold: Do not commit new supply during shock phase — wait for recovery signal
- Pent-up buy: On recovery phase entry, prepare additional stock at P75 for pent-up demand
- Manual overrides: Supply team recovery timeline input; pent-up demand magnitude confirmation

### 10. Evaluation

#### 10.1 Key Metrics

| Granularity | Shock WMAPE | Recovery WMAPE | Pent-Up Detection | Normal WMAPE | Bias Alert |
|---|---|---|---|---|---|
| Daily | < 45% | < 30% | Detected within 3 days | Per Behavior standard | \|Bias\| > 15% |
| Weekly | < 40% | < 25% | Detected within 1 week | Per Behavior standard | \|Bias\| > 12% |
| Monthly | < 35% | < 22% | Detected within 1 month | Per Behavior standard | \|Bias\| > 10% |
| Quarterly | < 30% | < 20% | Detected within 1 quarter | Per Behavior standard | \|Bias\| > 8% |
| Yearly | < 25% | < 18% | Detected within 1 year | Per Behavior standard | \|Bias\| > 6% |

#### 10.2 Backtesting — leave-one-shock-out; evaluate all three phases separately

#### 10.3 Retraining — immediate on shock detection; immediate on recovery confirmation; standard cadence otherwise

### 11. Exception Handling
- Alert: Recovery not confirmed by HRT → reclassify to Slow Recovery; permanent level change detected → Permanent Shift or Step Down

### 12. Reclassification

| Condition | Target | Trigger |
|---|---|---|
| Recovery exceeds HRT threshold for new shock | Slow Recovery | Post-shock assessment |
| Level change permanent | Permanent Shift / Step Down | Post-stabilisation |
| No deviation in new shock event | Shock Resistant | Post-shock reclassification |

### 13. Review Cadence
- Post-shock debrief within 1 week; quarterly HRT recalibration; annual full re-evaluation

---

