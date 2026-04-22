# Demand Pattern Taxonomy
## Pure Demand Forecasting Model Templates

---

> **12 Dimensions · 65 Segments · 5 Granularities**
> A complete specification for demand pattern classification and forecasting model selection across any time granularity.

---

## What This Repository Contains

This repository is the single source of truth for the **Pure Demand Pattern Taxonomy** — a structured framework for classifying SKU demand across 12 independent dimensions and selecting the appropriate forecasting model for each segment.

Every segment includes a fully populated 13-section forecasting model template covering:

- Segment definition and boundaries
- Applicable scenarios and key demand characteristics
- Business impact and priority level
- Model strategy (hurdle, analogue, feature engineering)
- Model families (ML · DL · Statistical · Fallback)
- Ensemble weighting schedules
- Uncertainty quantification
- Business rules and post-processing
- Evaluation metrics and targets
- Backtesting protocol
- Retraining cadence
- Reclassification logic
- Review cadence

All templates are fully populated with **specific quantitative values** across all 5 time granularities: **Daily · Weekly · Monthly · Quarterly · Yearly**.

---

## The 12 Dimensions

| # | Dimension | Segments | Core Question |
|---|---|---|---|
| 1 | [Lifecycle](docs/01-lifecycle.md) | 7 | Where in commercial life is demand? |
| 2 | [Behavior](docs/02-behavior.md) | 8 | What is the statistical shape of demand? |
| 3 | [Driver](docs/03-driver.md) | 6 | What causes demand to move? |
| 4 | [Magnitude](docs/04-magnitude.md) | 4 | How large is the demand? |
| 5 | [Trend](docs/05-trend.md) | 5 | Where is demand heading? |
| 6 | [Concentration](docs/06-concentration.md) | 5 | How is demand distributed in time? |
| 7 | [Shock](docs/07-shock.md) | 6 | How does demand react to disruptions? |
| 8 | [Elasticity](docs/08-elasticity.md) | 4 | How sensitive is demand to stimuli? |
| 9 | [Timing](docs/09-timing.md) | 5 | When does demand arrive vs expectation? |
| 10 | [Recurrence](docs/10-recurrence.md) | 5 | How consistently does demand repeat? |
| 11 | [Interaction](docs/11-interaction.md) | 5 | How does demand relate to other SKUs? |
| 12 | [Signal](docs/12-signal.md) | 5 | How clearly can true demand be read? |
| | **Total** | **65** | |

---

## Logical Grouping

```
DEMAND IDENTITY      → Lifecycle · Magnitude · Recurrence
DEMAND SHAPE         → Behavior · Concentration · Trend
DEMAND CAUSALITY     → Driver · Elasticity · Timing
DEMAND CONTEXT       → Interaction · Shock · Signal
```

---

## Formula Reference

All core segmentation formulas, thresholds, and decision trees are documented in:

→ [Formula Reference](docs/00-formula-reference.md)

Covers: ADI · CV² · Mann-Kendall · DCI · Gini · PED · SNR · CCF · HHI · and all granularity-specific thresholds.

---

## SKU Fingerprint

Every SKU receives a multi-dimensional fingerprint:

```
SKU-A:
  Lifecycle    → Mature
  Behavior     → Stable
  Driver       → Seasonal + Promotional
  Magnitude    → High Volume
  Trend        → Flat
  Concentration→ Peaked
  Shock        → Shock Resistant
  Elasticity   → Elastic
  Timing       → Coincident
  Recurrence   → Regular
  Interaction  → Independent
  Signal       → Pure Signal
```

---

## Classification Rules

- **Lifecycle** is assigned first — determines eligibility for Behavior classification
- **Behavior** uses the ADI × CV² matrix with granularity-specific thresholds
- **Driver** is an overlay — multiple drivers can apply simultaneously
- **All other dimensions** are independent overlays applied in parallel

---

## Granularities Supported

| Granularity | Thresholds | Rolling Windows | Retraining | Latency |
|---|---|---|---|---|
| Daily | Dimension-specific | 7/30/90/180/365 days | Daily | T+4 hours |
| Weekly | Dimension-specific | 4/8/13/26/52 weeks | Weekly | T+1 day |
| Monthly | Dimension-specific | 2/3/6/12/24 months | Monthly | T+2 days |
| Quarterly | Dimension-specific | 1/2/3/4/8 quarters | Quarterly | T+3 days |
| Yearly | Dimension-specific | 1/2/3/4/5 years | Annually | T+7 days |

---

## Repository Structure

```
demand-pattern-taxonomy/
├── README.md
├── docs/
│   ├── 00-formula-reference.md     # All formulas + thresholds
│   ├── 01-lifecycle.md             # 7 segments
│   ├── 02-behavior.md              # 8 segments
│   ├── 03-driver.md                # 6 segments
│   ├── 04-magnitude.md             # 4 segments
│   ├── 05-trend.md                 # 5 segments
│   ├── 06-concentration.md         # 5 segments
│   ├── 07-shock.md                 # 6 segments
│   ├── 08-elasticity.md            # 4 segments
│   ├── 09-timing.md                # 5 segments
│   ├── 10-recurrence.md            # 5 segments
│   ├── 11-interaction.md           # 5 segments
│   └── 12-signal.md                # 5 segments
└── mkdocs.yml
```

---

## How to Use

1. **Classify your SKU** — run each dimension's decision tree against your demand history
2. **Read the segment template** — locate your segment in the relevant dimension file
3. **Select your model family** — follow the model strategy for your granularity
4. **Apply thresholds** — use the Formula Reference for granularity-specific values
5. **Monitor and reclassify** — use the reclassification rules to keep segments current

---

## Versioning

| Version | Date | Change |
|---|---|---|
| v1.0.0 | 2026-04 | Initial release — 12 dimensions · 65 segments |

---

*Pure Demand Pattern Taxonomy — built for supply chain and demand planning practitioners.*
