# Dimension 7 · Shock Pattern
## Demand Forecasting Model Templates

---

> **Segments:** 6 · Shock Resistant · Shock Sensitive · Fast Recovery · Slow Recovery · Permanent Shift · Step Down
> **Granularities:** Daily · Weekly · Monthly · Quarterly · Yearly
> **Note:** Shock Pattern describes how demand **responds to sudden external disruptions**. It is detected retrospectively from historical shock events and used to determine model resilience strategies, safety stock buffers, and scenario planning requirements. Classification requires at least one historical shock event in the demand history.

---

# PART 0 — FORMULA & THRESHOLD REFERENCE
## Shock Pattern Specific

---

## 0.1 Core Segmentation Metrics

### A. Shock Detection
> Identifies demand disruptions that qualify as shocks

**General Formula:**
```
Shock = period where demand deviates from rolling baseline by > threshold

Baseline: μ_baseline(t) = rolling mean over pre-shock window (excl. event periods)
Deviation: dev(t) = (d(t) − μ_baseline(t)) / σ_baseline(t)   [normalised]

Shock threshold: |dev(t)| > 2.0 (demand > 2σ above or below baseline)
Shock duration: Consecutive periods where |dev(t)| > 1.5σ

Positive shock: dev(t) > +2.0 (demand spike)
Negative shock: dev(t) < −2.0 (demand collapse)
```

| Granularity | Pre-Shock Baseline Window | Shock Threshold | Min Shock Duration |
|---|---|---|---|
| **Daily** | 90-day rolling (excl. shock) | \|dev\| > 2.0σ | ≥ 3 consecutive days |
| **Weekly** | 13-week rolling (excl. shock) | \|dev\| > 2.0σ | ≥ 2 consecutive weeks |
| **Monthly** | 6-month rolling (excl. shock) | \|dev\| > 2.0σ | ≥ 1 month |
| **Quarterly** | 4-quarter rolling (excl. shock) | \|dev\| > 2.0σ | ≥ 1 quarter |
| **Yearly** | 3-year rolling (excl. shock) | \|dev\| > 2.0σ | ≥ 1 year |

---

### B. Recovery Rate
> Measures how quickly demand returns to pre-shock baseline

**General Formula:**
```
Post-shock baseline: μ_post = rolling mean starting T periods after shock end

Recovery at horizon h:
  RR(h) = (μ_post_h − μ_shock) / (μ_pre − μ_shock)
  where μ_pre   = pre-shock baseline mean
        μ_shock = mean demand during shock
        μ_post_h = mean demand h periods after shock

RR(h) = 0 → no recovery (still at shock level)
RR(h) = 1 → full recovery (back to pre-shock baseline)
RR(h) > 1 → over-recovery (pent-up demand spike)

Half-recovery time (HRT): h where RR(h) = 0.5
```

| Granularity | Fast Recovery (HRT) | Slow Recovery (HRT) | No Recovery |
|---|---|---|---|
| **Daily** | HRT < 14 days | HRT 14–90 days | HRT > 90 days or RR never reaches 0.8 |
| **Weekly** | HRT < 4 weeks | HRT 4–13 weeks | HRT > 13 weeks or RR never reaches 0.8 |
| **Monthly** | HRT < 3 months | HRT 3–9 months | HRT > 9 months or RR never reaches 0.8 |
| **Quarterly** | HRT < 1 quarter | HRT 1–3 quarters | HRT > 3 quarters or RR never reaches 0.8 |
| **Yearly** | HRT < 1 year | HRT 1–2 years | HRT > 2 years or RR never reaches 0.8 |

---

### C. Permanent Shift Detection
> Identifies shocks that result in a lasting level change

**General Formula:**
```
Post-shock mean: μ_post = mean demand over extended window after shock fully passes
Pre-shock mean:  μ_pre  = mean demand over pre-shock window

Level change: Δ = (μ_post − μ_pre) / μ_pre × 100   [% change]

Permanent Shift (upward): Δ > +15% AND RR stabilises above 1.10 for ≥ 2× HRT
Step Down (downward):     Δ < −15% AND RR stabilises below 0.85 for ≥ 2× HRT
Transient (recovers):     |Δ| < 15% at 2× HRT after shock end
```

| Granularity | Permanent Shift Threshold | Step Down Threshold | Stabilisation Window |
|---|---|---|---|
| **Daily** | Δ > +15%; stable for ≥ 30 days | Δ < −15%; stable for ≥ 30 days | 30 days post-shock end |
| **Weekly** | Δ > +15%; stable for ≥ 8 weeks | Δ < −15%; stable for ≥ 8 weeks | 8 weeks post-shock end |
| **Monthly** | Δ > +15%; stable for ≥ 3 months | Δ < −15%; stable for ≥ 3 months | 3 months post-shock end |
| **Quarterly** | Δ > +15%; stable for ≥ 2 quarters | Δ < −15%; stable for ≥ 2 quarters | 2 quarters post-shock end |
| **Yearly** | Δ > +15%; stable for ≥ 1 year | Δ < −15%; stable for ≥ 1 year | 1 year post-shock end |

---

### D. Shock Resistance Score
> Quantifies how much demand deviates from baseline during shock events

**Formula:**
```
SRS = 1 − (|dev_shock| / max_possible_dev)
where dev_shock = mean(|dev(t)|) during shock period
      max_possible_dev = 5.0 (5σ maximum considered)

SRS = 1.0 → completely resistant (demand unchanged during shock)
SRS = 0.0 → completely sensitive (demand at 5σ deviation)

Shock Resistant:  SRS > 0.60 (deviation < 2σ during shock)
Shock Sensitive:  SRS < 0.40 (deviation > 3σ during shock)
Intermediate:     0.40 ≤ SRS ≤ 0.60
```

---

## 0.2 Shock Pattern Classification Decision Rules

```
STEP 1: Identify historical shock events in demand history (Section 0.1A)
  If no shock events detected → classify as SHOCK RESISTANT (no evidence of sensitivity)

STEP 2: Compute Shock Resistance Score (Section 0.1D)
  SRS > 0.60 → SHOCK RESISTANT
  SRS < 0.40 → proceed to STEP 3

STEP 3: Compute Recovery Rate at standard horizon (Section 0.1B)
  RR(2× HRT) > 0.80 → demand recovers → classify by speed:
    HRT < fast threshold → FAST RECOVERY
    HRT ≥ fast threshold → SLOW RECOVERY
  RR never reaches 0.80 → proceed to STEP 4

STEP 4: Compute Level Change (Section 0.1C)
  Δ > +15% AND stable → PERMANENT SHIFT
  Δ < −15% AND stable → STEP DOWN
  |Δ| < 15% but RR < 0.80 → SLOW RECOVERY (extreme slow case)
```

---

## 0.3 Scenario Planning Framework

```
For all Shock Pattern segments, maintain scenario forecasts:

Base scenario:     Expected demand given no shock (standard model output)
Mild shock:        Base × shock_sensitivity_factor × (1 − SRS)
Severe shock:      Base × max_deviation_factor
Recovery path:     Base + (Pre_shock − current) × RR(h) for h = 1 to H

Scenario weights:
  Shock Resistant: Base = 90%; Mild = 8%; Severe = 2%
  Shock Sensitive: Base = 60%; Mild = 25%; Severe = 15%
  Fast Recovery:   Revert to base within recovery horizon
  Slow Recovery:   Weighted blend base + shock path for full recovery horizon
  Permanent Shift: New baseline = μ_post; old baseline discarded
  Step Down:       New baseline = μ_post; supply reduction triggered
```

---

## 0.4 Rolling Window Reference

| Window Name | Daily | Weekly | Monthly | Quarterly | Yearly |
|---|---|---|---|---|---|
| **Short** | 7 days | 4 weeks | 2 months | 1 quarter | 1 year |
| **Medium** | 30 days | 8 weeks | 3 months | 2 quarters | 2 years |
| **Long** | 90 days | 13 weeks | 6 months | 3 quarters | 3 years |
| **Extended** | 180 days | 26 weeks | 12 months | 4 quarters | 4 years |
| **Pre-Shock** | 90 days | 13 weeks | 6 months | 4 quarters | 3 years |
| **Post-Shock** | 30 days | 8 weeks | 3 months | 2 quarters | 1 year |

---

## 0.5 Accuracy Metric Formulas

```
Standard metrics:
  WMAPE = Σ|Forecast_t − Actual_t| / Σ Actual_t × 100
  Bias  = Σ(Forecast_t − Actual_t) / Σ Actual_t × 100
  MAE   = (1/n) × Σ|Forecast_t − Actual_t|

Shock-specific metrics:
  Shock Detection Rate = Shocks correctly flagged / Total shocks × 100  (Target > 85%)
  False Alarm Rate = Non-shock periods flagged as shock / Total non-shock periods × 100  (Target < 5%)
  Recovery Forecast Error = WMAPE computed only on post-shock recovery period
  Scenario Coverage = % of shock outcomes within scenario range [P10, P90]  (Target > 80%)
```

---

## 0.6 Retraining & Backtesting Reference

| Granularity | Retraining | Latency | Backtest Train | Backtest Test |
|---|---|---|---|---|
| **Daily** | Daily + shock trigger | T+4 hours | 180 days | 30 days |
| **Weekly** | Weekly + shock trigger | T+1 day | 52 weeks | 13 weeks |
| **Monthly** | Monthly + shock trigger | T+2 days | 24 months | 6 months |
| **Quarterly** | Quarterly + shock trigger | T+3 days | 8 quarters | 2 quarters |
| **Yearly** | Annually + shock trigger | T+7 days | All available | 1 year |

---

# PART 1 — SEGMENT TEMPLATES

---

## SH1 · Shock Resistant

### 1. Definition
Predicts demand for SKUs where historical shock events have caused no statistically significant deviation from the demand baseline, indicating the SKU is insensitive to external disruptions and requires no shock-specific modelling adjustments.

### 2. Detailed Description
- **Applicable scenarios:** Essential staples, utility-driven demand, contractually committed supply, inelastic needs (medications, food staples)
- **Boundaries:**

| Granularity | SRS Threshold | Condition | Min Shock Events |
|---|---|---|---|
| Daily | SRS > 0.60 (deviation < 2σ during shocks) | No significant deviation in any historical shock | ≥ 1 shock event observed |
| Weekly | SRS > 0.60 | Same | ≥ 1 shock event observed |
| Monthly | SRS > 0.60 | Same | ≥ 1 shock event observed |
| Quarterly | SRS > 0.60 | Same | ≥ 1 shock event observed |
| Yearly | SRS > 0.60 | Same | ≥ 1 shock event observed |

- **Key demand characteristics:** Demand continues near-normal during external disruptions; consumption-driven not discretionary; customers cannot defer or substitute
- **Differentiation from other models:** Unlike Shock Sensitive, demand does not deviate significantly; unlike Fast/Slow Recovery, no recovery needed — demand was never disrupted; standard models require no shock adjustment

### 3. Business Impact
- **Primary risk (over-forecast):** Standard model risk only — no shock amplification
- **Primary risk (under-forecast):** Standard model risk only
- **Strategic importance:** High — resistant SKUs provide stable baseline revenue during market disruptions; planning confidence is high

### 4. Priority Level
🟠 Tier 2 — Low shock management burden; primary value is confidence in standard model outputs during disruptions.

### 5. Model Strategy Overview

#### 5.1 Shock Monitoring (Passive)
- Active shock monitoring: Run shock detection algorithm each period (Section 0.1A)
- If SRS drops below 0.60 for a new shock event → reclassify immediately
- No shock-specific model adjustment during normal periods

#### 5.2 Standard Model Application
- Apply standard behavior-appropriate model without shock adjustment
- Shock resistance confirmed → standard safety stock policy applies

#### 5.3 Feature Engineering
- Standard features per Behavior segment
- Additional: Shock resistance score (SRS) as metadata feature — low weight but confirms stability
- Shock event flag: Historical shock event dates as binary features — validate no demand response

### 6. Model Families
- Apply standard model family per Behavior × Lifecycle × Magnitude segment
- No shock-specific model component required

#### 6.4 Baseline / Fallback Model
- Fallback: Standard rolling mean — same as non-shock periods
- If new shock detected: Immediately rerun shock classification before next forecast cycle

### 7. Ensemble & Weighting
- Standard ensemble per behavior segment — no shock weighting required
- Scenario planning: Maintain 10% weight on mild-shock scenario as contingency

### 8. Uncertainty Quantification
- Standard [P10, P50, P90] — no shock-specific widening required
- Scenario: Base = 90%; Mild shock = 8%; Severe shock = 2%
- Use case: Standard safety stock; no shock buffer required

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- No shock cap or floor adjustments — standard rules apply
- Shock watch: Automated monitoring; alert if demand deviates > 2σ from baseline
- Manual overrides: Standard only — no shock-specific adjustments

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | WMAPE Target | Bias Alert | Shock Detection Rate | SRS Monitor |
|---|---|---|---|---|
| Daily | Per Behavior segment standard | Per Behavior standard | Alert if SRS drops below 0.60 | Weekly SRS check |
| Weekly | Per Behavior segment standard | Per Behavior standard | Alert if SRS drops below 0.60 | Weekly SRS check |
| Monthly | Per Behavior segment standard | Per Behavior standard | Alert if SRS drops below 0.60 | Monthly SRS check |
| Quarterly | Per Behavior segment standard | Per Behavior standard | Alert if SRS drops below 0.60 | Quarterly SRS check |
| Yearly | Per Behavior segment standard | Per Behavior standard | Alert if SRS drops below 0.60 | Annual SRS check |

#### 10.2 Backtesting Protocol
- Standard per Behavior segment
- Additional: Evaluate forecast accuracy during historical shock periods — confirm no degradation

#### 10.3 Retraining
- Standard cadence per Behavior segment
- Additional trigger: Immediate retrain on new shock detection

### 11. Exception Handling & Overrides
- Auto-detect: SRS drops below 0.60 on new shock → immediate reclassification trigger
- Manual override: Supply chain team shock flag (supply disruption may create apparent demand shock on resistant SKU)
- Override expiration: Per shock event

### 12. Reclassification

| Condition | Target Segment | Trigger |
|---|---|---|
| New shock event with SRS < 0.40 | Shock Sensitive | Immediate — new shock event |
| New shock event with fast recovery (HRT < fast threshold) | Fast Recovery | Post-shock reclassification |
| New shock event with permanent level change (Δ > ±15%) | Permanent Shift or Step Down | Post-shock stabilisation |

### 13. Review Cadence
- Per cycle SRS monitoring; quarterly shock history review; annual full re-evaluation

---

## SH2 · Shock Sensitive

### 1. Definition
Predicts demand for SKUs that exhibit significant demand deviation during external shock events (SRS < 0.40), requiring shock-aware scenario planning, wider prediction intervals, and rapid model adaptation protocols during disruption periods.

### 2. Detailed Description
- **Applicable scenarios:** Discretionary categories, luxury goods, travel-related demand, restaurant and hospitality supply, event-dependent categories, panic-buying susceptible staples
- **Boundaries:**

| Granularity | SRS Threshold | Deviation Condition | Min Shock Events |
|---|---|---|---|
| Daily | SRS < 0.40 (deviation > 3σ) | Demand deviates > 3σ during shocks | ≥ 1 shock event |
| Weekly | SRS < 0.40 | Same | ≥ 1 shock event |
| Monthly | SRS < 0.40 | Same | ≥ 1 shock event |
| Quarterly | SRS < 0.40 | Same | ≥ 1 shock event |
| Yearly | SRS < 0.40 | Same | ≥ 1 shock event |

- **Key demand characteristics:** Large demand swings during disruptions; high sensitivity to external events; recovery pattern may vary; standard models fail catastrophically during shock periods
- **Differentiation from other models:** Unlike Shock Resistant, significant deviation occurs; unlike Fast/Slow Recovery, sensitivity classification is independent of recovery speed — a sensitive SKU may recover quickly or slowly

### 3. Business Impact
- **Primary risk (over-forecast):** Massive overstock during negative shocks (demand collapse)
- **Primary risk (under-forecast):** Severe stockout during positive shocks (demand surge, panic buying)
- **Strategic importance:** High — Shock Sensitive SKUs create the most acute supply chain stress during disruptions

### 4. Priority Level
🔴 Tier 1 — Shock events create acute inventory crises for sensitive SKUs; scenario planning and rapid response are critical.

### 5. Model Strategy Overview

#### 5.1 Dual-State Model Architecture
```
Normal state: Standard behavior model — applied when no shock detected
Shock state:  Shock-specific model — activated immediately on shock detection

State switching:
  Normal → Shock: When dev(t) > 2σ for consecutive periods (Section 0.1A)
  Shock → Recovery: When dev(t) returns within 1.5σ of baseline
  Recovery → Normal: After recovery confirmed (RR > 0.80)

Shock model inputs:
  Shock type (positive/negative)
  Shock severity (dev magnitude)
  Shock duration so far
  Analogous historical shocks
```

#### 5.2 Analogue / Similarity Logic (Shock Analogues)
- Number of analogues: k = 5 (most similar historical shock events for this SKU + similar SKUs)
- Similarity criteria: Shock type (positive/negative), shock severity (dev magnitude ±1σ), category, season of shock
- Temporal decay: weight = exp(−age / half-life)

| Granularity | Half-Life |
|---|---|
| Daily | 365 days |
| Weekly | 52 weeks |
| Monthly | 12 months |
| Quarterly | 4 quarters |
| Yearly | 3 years |

#### 5.3 Feature Engineering

| Granularity | Normal State Features | Shock State Features |
|---|---|---|
| Daily | Standard behavior features | Shock severity (dev magnitude), shock type flag, shock duration (days), analogous shock trajectory, external shock index (news sentiment, mobility index) |
| Weekly | Standard behavior features | Shock severity, shock type, shock duration (weeks), analogous shock trajectory |
| Monthly | Standard behavior features | Shock severity, shock type, shock duration (months), analogous trajectory |
| Quarterly | Standard behavior features | Shock severity, shock type, shock duration (quarters) |
| Yearly | Standard behavior features | Shock severity, shock type, shock duration |

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Normal state: Standard LightGBM per behavior segment
- Shock state: XGBoost trained on historical shock periods only; shock analogue features as primary inputs
- State classifier: Logistic Regression — P(shock state) based on current deviation and external signals

#### 6.2 Deep Learning (DL)
- Architectures: TFT with shock event as past observed covariate
- Shock encoding: Binary shock flag + shock severity as time-varying covariate in TFT
- When to use: When ≥ 3 historical shock events available for training

#### 6.3 Statistical / Time Series Models
- Normal state: Standard ETS per behavior segment
- Shock state: Intervention model — add impulse/step function to baseline model

**Intervention Model:**
```
d(t) = baseline_model(t) + β_shock × shock_indicator(t) + ε(t)
shock_indicator(t) = 1 during shock period; 0 otherwise
β_shock = estimated shock impact coefficient (from historical shock events)
β_shock_positive > 0 (demand surge)
β_shock_negative < 0 (demand collapse)
```

#### 6.4 Baseline / Fallback Model
- Fallback during shock: Historical mean shock deviation × baseline; P10/P90 as bounds
- Alert: Shock state activated — P1 alert to supply chain team immediately

### 7. Ensemble & Weighting

#### 7.2 Dynamic Weight Schedule

| State | LightGBM/XGBoost | TFT | Statistical |
|---|---|---|---|
| Normal state | 50% | 25% | 25% |
| Shock state (< 3 shock events) | 20% | 20% | 60% (intervention model) |
| Shock state (≥ 3 shock events) | 40% | 30% | 30% |

### 8. Uncertainty Quantification
- Method: Scenario analysis — three scenarios during shock
- Output:

| Scenario | Probability | Forecast |
|---|---|---|
| Severe shock continues | 30% | Baseline × min_shock_factor |
| Moderate shock, partial recovery | 50% | Baseline × mean_shock_factor |
| Shock resolves quickly | 20% | Baseline (return to normal) |

- Prediction intervals significantly wider during shock: [P5, P50, P95]
- Use case: Inventory decisions held; supply commitments minimised during shock state

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Shock state rules:
  - Positive shock: Cap at 3 × pre-shock baseline (prevent extreme over-order)
  - Negative shock: Floor at 0.1 × pre-shock baseline (prevent complete write-off of open orders)
- Commitment freeze: During shock state, no new long-lead-time commitments without explicit approval
- Manual overrides: Supply chain crisis team input; government/regulatory guidance integration

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | Normal WMAPE | Shock WMAPE | Shock Detection Rate | False Alarm Rate | Bias Alert |
|---|---|---|---|---|---|
| Daily | Per Behavior standard | < 50% | > 85% | < 5% | \|Bias\| > 20% shock state |
| Weekly | Per Behavior standard | < 45% | > 85% | < 5% | \|Bias\| > 18% |
| Monthly | Per Behavior standard | < 40% | > 85% | < 5% | \|Bias\| > 15% |
| Quarterly | Per Behavior standard | < 35% | > 85% | < 5% | \|Bias\| > 12% |
| Yearly | Per Behavior standard | < 30% | > 85% | < 5% | \|Bias\| > 10% |

#### 10.2 Backtesting Protocol
- Backtesting split: Separate evaluation on shock periods vs normal periods
- Leave-one-shock-out: Hold out most recent shock; train on prior shocks; test on held-out shock
- Min shock events for reliable backtest: ≥ 3 shock events

#### 10.3 Retraining
- Normal cadence per Behavior segment
- Shock trigger: Immediate retrain on shock detection; retrain again on shock resolution

### 11. Exception Handling & Overrides
- Auto-detect: Shock state activated → P1 alert; SRS improves above 0.60 for 3+ consecutive shocks → reclassify to Shock Resistant
- Manual override: Crisis team shock severity and expected duration input; supply allocation decision override
- Override expiration: Per shock event

### 12. Reclassification

| Condition | Target Segment | Trigger |
|---|---|---|
| SRS improves above 0.60 for ≥ 3 consecutive shock events | Shock Resistant | Post-shock review |
| Recovery confirmed fast (HRT < fast threshold) | Fast Recovery (supplementary) | Post-shock |
| Recovery confirmed slow (HRT ≥ slow threshold) | Slow Recovery (supplementary) | Post-shock |
| Level change permanent (Δ > ±15%) | Permanent Shift or Step Down | Post-stabilisation |

### 13. Review Cadence
- Continuous monitoring during shock state; post-shock debrief within 2 weeks; quarterly shock history update; annual full re-evaluation

---

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

## SH5 · Permanent Shift

### 1. Definition
Predicts demand for SKUs where a shock has caused a lasting upward level change (Δ > +15%) that does not revert to the pre-shock baseline, requiring complete rebaselining and treatment as a new demand regime from the shock point forward.

### 2. Detailed Description
- **Applicable scenarios:** Demand permanently unlocked by crisis (e.g. hygiene products post-pandemic), new distribution channels opened during disruption, lasting consumer behaviour change, regulatory-driven permanent demand increase
- **Boundaries:**

| Granularity | Level Change | Stabilisation | Direction |
|---|---|---|---|
| Daily | Δ > +15% | Stable for ≥ 30 days post-shock | Upward only |
| Weekly | Δ > +15% | Stable for ≥ 8 weeks | Upward only |
| Monthly | Δ > +15% | Stable for ≥ 3 months | Upward only |
| Quarterly | Δ > +15% | Stable for ≥ 2 quarters | Upward only |
| Yearly | Δ > +15% | Stable for ≥ 1 year | Upward only |

- **Key demand characteristics:** Shock breaks demand to a sustainably higher level; new normal is structurally above pre-shock baseline; pre-shock history is no longer representative
- **Differentiation from other models:** Unlike Fast/Slow Recovery, demand does not return to pre-shock baseline; unlike Step Down, shift is upward; unlike Growth Lifecycle, change is shock-driven not organic

### 3. Business Impact
- **Primary risk (over-forecast):** If shift reverts unexpectedly — large overstock at elevated baseline
- **Primary risk (under-forecast):** Failing to recognise permanent shift → chronic stockout at new higher demand level
- **Strategic importance:** Very high — permanent upward shift creates a new revenue and capacity baseline; supply chain must be restructured to serve new level

### 4. Priority Level
🔴 Tier 1 — Complete model rebaselining required; supply capacity must be reassessed; failure to recognise shift creates chronic stockout.

### 5. Model Strategy Overview

#### 5.1 Full Rebaselining Protocol
```
On permanent shift confirmation:
  STEP 1: Set new baseline = μ_post (post-shock stabilised mean)
  STEP 2: Discard pre-shock history from model training (contaminated baseline)
  STEP 3: Apply Cold Start model on post-shift data during warm-up period
  STEP 4: Graduate to standard behavior model after warm-up
  STEP 5: Retain pre-shock history as metadata only (for shift magnitude reference)

Warm-up period after shift:
  Granularity-specific (see Lifecycle Dimension — Cold Start thresholds)
```

#### 5.2 Feature Engineering (Post-Shift)
- All features computed on post-shift data only
- Shift magnitude feature: Δ retained as metadata to characterise shift severity
- Shift date feature: Used to validate data cutoff for training
- Pre-shift data: Excluded from all feature computation

### 6. Model Families
- During warm-up: Cold Start model (Dimension 1 — L1 template)
- After warm-up: Standard behavior model on post-shift data (per Behavior × Magnitude segment)

#### 6.3 Statistical: ETS reinitialized at shift point; α = 0.3 (faster adaptation) during first post-shift cycle

#### 6.4 Fallback: Post-shift rolling mean; do not use pre-shift data

### 7. Ensemble
- Warm-up: Analogue-based (similar shift magnitude events from other SKUs)
- Post-warm-up: Standard ensemble per behavior segment on post-shift data

### 8. Uncertainty Quantification
- Warm-up: [P5, P50, P95] — high uncertainty post-shift
- Post-warm-up: [P10, P50, P90] — standard; narrows as new baseline confirmed
- Shift reversion risk scenario: P10 = pre-shift baseline (worst case reversion)
- Use case: Capacity planning at P75 of new baseline; retain optionality to reduce at P25

### 9. Business Rules
- Non-negativity: max(0, forecast)
- Training data hard cutoff: Only post-shift data in model training
- Capacity review trigger: Permanent shift confirmed → mandatory capacity and supply review within 30 days
- Manual overrides: Commercial team new baseline confirmation; category manager structural demand assessment

### 10. Evaluation

| Granularity | Shift Detection Speed | Post-Shift WMAPE | New Baseline Accuracy | Bias Alert |
|---|---|---|---|---|
| Daily | Detected within 14 days of stabilisation | < 25% warm-up | New baseline within ±10% | \|Bias\| > 12% |
| Weekly | Detected within 4 weeks | < 22% | Within ±10% | \|Bias\| > 10% |
| Monthly | Detected within 2 months | < 18% | Within ±8% | \|Bias\| > 8% |
| Quarterly | Detected within 1 quarter | < 15% | Within ±6% | \|Bias\| > 6% |
| Yearly | Detected within 1 year | < 12% | Within ±5% | \|Bias\| > 5% |

### 11. Exception Handling
- Alert: New baseline shows decline → assess if reversion; post-shift CV² increases → Erratic emerging from shift
- Manual override: If shift reverts → discard post-shift history and revert to pre-shift baseline

### 12. Reclassification

| Condition | Target | Trigger |
|---|---|---|
| New baseline confirmed stable for 2 full cycles | Standard behavior segment on post-shift data | Auto-graduation |
| New baseline reverts to pre-shift level | Original pre-shift behavior segment | Recovery confirmed |
| Second shock on top of permanent shift | Shock Sensitive (new shock layer) | New shock detection |

### 13. Review Cadence
- Weekly during warm-up; monthly new baseline validation; quarterly capacity alignment review; annual full re-evaluation

---

## SH6 · Step Down

### 1. Definition
Predicts demand for SKUs where a shock has caused a lasting downward level change (Δ < −15%) that does not recover, requiring complete rebaselining at the lower level and immediate inventory run-down management.

### 2. Detailed Description
- **Applicable scenarios:** Permanent consumer behaviour change against category, lasting distribution loss, regulatory restriction, category disruption by substitute product, demographic or structural market decline
- **Boundaries:**

| Granularity | Level Change | Stabilisation | Direction |
|---|---|---|---|
| Daily | Δ < −15% | Stable for ≥ 30 days | Downward only |
| Weekly | Δ < −15% | Stable for ≥ 8 weeks | Downward only |
| Monthly | Δ < −15% | Stable for ≥ 3 months | Downward only |
| Quarterly | Δ < −15% | Stable for ≥ 2 quarters | Downward only |
| Yearly | Δ < −15% | Stable for ≥ 1 year | Downward only |

- **Key demand characteristics:** Shock breaks demand to a sustainably lower level; new normal is structurally below pre-shock baseline; excess inventory at old baseline must be run down immediately
- **Differentiation from other models:** Unlike Slow Recovery, demand does not recover; unlike Step Down lifecycle (Phasing Out), the lower level is the new normal — not approaching zero; unlike Permanent Shift, direction is downward

### 3. Business Impact
- **Primary risk (over-forecast):** Catastrophic inventory build at pre-shift baseline → massive write-off
- **Primary risk (under-forecast):** Minimal — over-forecast is the dominant risk
- **Strategic importance:** Very high — Step Down requires immediate supply chain and inventory restructuring; failure to recognise creates acute write-off risk

### 4. Priority Level
🔴 Tier 1 — Immediate action required; over-forecast at pre-shift baseline is catastrophically costly; supply reduction must begin immediately.

### 5. Model Strategy Overview

#### 5.1 Full Rebaselining Protocol (Downward)
```
On Step Down confirmation:
  STEP 1: Set new (lower) baseline = μ_post
  STEP 2: Immediately stop ordering above new baseline
  STEP 3: Initiate inventory run-down plan (excess = stock at old baseline)
  STEP 4: Apply post-shift Cold Start model during warm-up
  STEP 5: Graduate to standard behavior model at new lower baseline after warm-up
  STEP 6: Flag for Lifecycle: Decline or Phasing Out assessment
```

#### 5.2 Feature Engineering (Post-Shift)
- All features computed on post-shift data only
- Step down magnitude: |Δ| retained as metadata
- Run-down timeline feature: Periods of excess inventory at old baseline level (supply chain planning)
- Pre-shift data: Excluded from model training

### 6. Model Families
- Immediate: Emergency flat forecast at post-shift rolling mean — prevent any upward drift
- Warm-up: Cold Start model on post-shift data
- Post-warm-up: Standard behavior model at new baseline; Decline Lifecycle likely

#### 6.3 Statistical: ETS reinitialised at new (lower) level; use high α (0.4) initially — fast level adaptation critical

**Step Down ETS Initialisation:**
```
l_0 = μ_post (post-shift stabilised mean)   [NOT pre-shift mean]
b_0 = 0 or slight negative if further decline detected
α = 0.40 (fast adaptation — prioritise new level over history)
```

#### 6.4 Fallback: Post-shift rolling mean only; hard rule against using pre-shift data

### 7. Ensemble
- Warm-up: Post-shift rolling mean (primary) + category index (supplementary)
- Post-warm-up: Standard ensemble per behavior segment on post-shift data

### 8. Uncertainty Quantification
- Warm-up: [P5, P50, P95] — high uncertainty; risk of further step down
- Post-warm-up: [P10, P50, P90]
- Further decline risk: P10 = 50% × new baseline (further step down scenario)
- Use case: Order only to P10 initially — conservative; increase as new baseline confirmed

### 9. Business Rules
- Non-negativity: max(0, forecast)
- Hard supply cap: Immediately cap all new orders at new baseline × (1 + small safety buffer)
- Run-down plan: Excess inventory = (old stock − new safety stock) must be cleared within run-down horizon
- Emergency review: Step Down confirmed → mandatory emergency supply chain review within 7 days
- Manual overrides: Category manager new baseline confirmation; clearance decision; delisting review

### 10. Evaluation

| Granularity | Detection Speed | Post-Shift WMAPE | Over-Forecast Alert | Inventory Run-Down KPI |
|---|---|---|---|---|
| Daily | Detected within 7 days | < 25% warm-up | Bias > +10% | Excess cleared within 30 days |
| Weekly | Detected within 2 weeks | < 22% | Bias > +10% | Excess cleared within 8 weeks |
| Monthly | Detected within 1 month | < 18% | Bias > +8% | Excess cleared within 3 months |
| Quarterly | Detected within 1 quarter | < 15% | Bias > +6% | Excess cleared within 2 quarters |
| Yearly | Detected within 1 year | < 12% | Bias > +5% | Excess cleared within 1 year |

### 11. Exception Handling
- Alert: Any forecast above new baseline → immediate over-forecast alert; further step down detected (second Δ < −15%) → emergency review; pre-shift data accidentally used → retrain immediately with post-shift data only
- Manual override: Emergency supply stop order; accelerated clearance authorisation

### 12. Reclassification

| Condition | Target | Trigger |
|---|---|---|
| New baseline stable for 2 full cycles | Standard behavior segment at new lower baseline | Auto-graduation |
| Further step down detected | Step Down (second level) | New shift detection |
| Demand approaches zero at new baseline | Lifecycle: Phasing Out or Inactive | Lifecycle reclassification |
| Demand recovers to pre-shift level | Fast or Slow Recovery | Recovery detection |

### 13. Review Cadence
- Daily during first 2 weeks post-detection; weekly during warm-up; monthly new baseline validation; quarterly inventory run-down progress; annual full re-evaluation

---

*End of Dimension 7 · Shock Pattern*
*6 Segments Complete · SH1 through SH6*
