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

