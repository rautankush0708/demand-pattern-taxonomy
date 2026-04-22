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
