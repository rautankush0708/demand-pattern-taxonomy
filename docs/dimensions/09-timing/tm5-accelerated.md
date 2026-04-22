## TM5 · Accelerated
### 1. Definition
Predicts demand for SKUs where customers pull forward purchases ahead of the expected timing — driven by anticipated price increases, supply scarcity signals, or promotional end-dates — creating artificial spikes followed by demand troughs.

### 2. Detailed Description
- **Applicable scenarios:** Pre-price-increase buying, end-of-promotion stockpiling, pre-shortage panic buying, fiscal year-end budget flush purchasing

### 5. Model Strategy

#### 5.1 Acceleration-Trough Model
```
Acceleration period: d_accel(t) = d_baseline(t) × (1 + accel_factor)
Post-acceleration trough: d_trough(t) = d_baseline(t) × (1 − trough_factor × e^{−λ_trough × h})
where h = periods after acceleration event ends
accel_factor and trough_factor estimated from historical acceleration events
Net demand: Σ d_accel + Σ d_trough = Σ d_baseline (demand conserved — only timing changes)
```

| Granularity | Acceleration Trigger | Post-Trough Duration |
|---|---|---|
| Daily | Price increase announcement > 3 days ahead | 7–21 days |
| Weekly | Promo end within 2 weeks; supply shortage signal | 2–6 weeks |
| Monthly | Price increase > 1 month ahead; policy change | 1–3 months |
| Quarterly | Annual price increase announcement | 1–2 quarters |
| Yearly | Regulatory change > 1 year ahead | 6–18 months |

### 6. Model Families

#### 6.1 ML: LightGBM with acceleration trigger features + post-trough features
#### 6.2 DL: TFT with known future acceleration triggers as covariates
#### 6.3 Statistical: Intervention model with acceleration impulse + trough correction

### Evaluation

| Granularity | Accel WMAPE | Trough WMAPE | Net Demand Conservation | Bias Alert |
|---|---|---|---|---|
| Daily | < 35% | < 30% | ±10% of baseline total | \|Bias\| > 15% |
| Weekly | < 30% | < 25% | ±8% | \|Bias\| > 12% |
| Monthly | < 25% | < 20% | ±6% | \|Bias\| > 10% |
| Quarterly | < 22% | < 18% | ±5% | \|Bias\| > 8% |
| Yearly | < 18% | < 15% | ±4% | \|Bias\| > 6% |

---

# DIMENSION 10 — RECURRENCE PATTERN

---
