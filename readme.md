![Demand Pattern Taxonomy Logo](docs/assets/logo.png)

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
| 1 | [Lifecycle](docs/dimensions/01-lifecycle.md) | 7 | Where in commercial life is demand? |
| 2 | [Behavior](docs/dimensions/02-behavior.md) | 8 | What is the statistical shape of demand? |
| 3 | [Driver](docs/dimensions/03-driver.md) | 6 | What causes demand to move? |
| 4 | [Magnitude](docs/dimensions/04-magnitude.md) | 4 | How large is the demand? |
| 5 | [Trend](docs/dimensions/05-trend.md) | 5 | Where is demand heading? |
| 6 | [Concentration](docs/dimensions/06-concentration.md) | 5 | How is demand distributed in time? |
| 7 | [Shock](docs/dimensions/07-shock.md) | 6 | How does demand react to disruptions? |
| 8 | [Elasticity](docs/dimensions/08-elasticity.md) | 4 | How sensitive is demand to stimuli? |
| 9 | [Timing](docs/dimensions/09-timing.md) | 5 | When does demand arrive vs expectation? |
| 10 | [Recurrence](docs/dimensions/10-recurrence.md) | 5 | How consistently does demand repeat? |
| 11 | [Interaction](docs/dimensions/11-interaction.md) | 5 | How does demand relate to other SKUs? |
| 12 | [Signal](docs/dimensions/12-signal.md) | 5 | How clearly can true demand be read? |
| | **Total** | **65** | |

---

## Formula Reference

All core segmentation formulas, thresholds, and decision trees are documented in:

→ [**Formula Reference**](docs/formula-reference/01-core-metrics.md)

Covers: ADI · CV² · Mann-Kendall · DCI · Gini · PED · SNR · CCF · HHI · and all granularity-specific thresholds.

---

## Repository Structure (Pro Architecture)

```
demand-pattern-taxonomy/
├── mkdocs.yml                 # MkDocs configuration
├── docs/                      # Documentation content
│   ├── index.md               # Portal Landing Page
│   ├── formula-reference/     # Mathematical foundations
│   │   ├── 01-core-metrics.md
│   │   └── ...
│   ├── dimensions/            # 12-Dimension specifications
│   │   ├── 01-lifecycle.md
│   │   └── ...
│   ├── templates/             # Blank segment templates
│   └── assets/                # Images and logos
├── src/                       # Python Taxonomy Engine
│   └── demand_taxonomy/       # Automated classification logic
├── .github/workflows/         # CI/CD Automation
└── CHANGELOG.md               # Version history
```

---

## Automation Engine

This repository includes a Python library in `src/` to automate the classification process:
```python
from demand_taxonomy.metrics import calculate_adi, get_behavior_segment
adi = calculate_adi([10, 0, 12, 0, 11])
segment = get_behavior_segment(adi, 0.05) # "INTERMITTENT"
```

---

## Versioning

| Version | Date | Change |
|---|---|---|
| v1.0.0 | 2026-04 | Initial release — 12 dimensions · 65 segments |

---

*Pure Demand Pattern Taxonomy — built for supply chain and demand planning practitioners.*
