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

---

# PART 1 — SEGMENT TEMPLATES

