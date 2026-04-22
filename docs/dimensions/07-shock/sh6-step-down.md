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
