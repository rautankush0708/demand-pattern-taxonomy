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

