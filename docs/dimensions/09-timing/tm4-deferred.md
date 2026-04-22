## TM4 · Deferred
### 1. Definition
Predicts demand for SKUs where customer decision cycles cause demand to arrive significantly later than the triggering event, requiring extended post-trigger forecast horizons and patience-adjusted demand models.

### 2. Detailed Description
- **Applicable scenarios:** B2B capital procurement (long approval cycles), large project-based orders, demand delayed by regulatory approvals, consumer electronics with long consideration cycles

### 5. Model Strategy

#### 5.1 Deferral Model
```
Demand at time t arrives from triggers at times t−L_1, t−L_2, ..., t−L_max
Deferral distribution: P(demand arrives at lag L) = f(L) (empirically estimated)
F(t) = Σ P(demand at lag L) × trigger(t − L) × β_conversion
```

| Granularity | Deferral Distribution Window | Min Deferral Events |
|---|---|---|
| Daily | Lag 7–90 days | ≥ 5 events |
| Weekly | Lag 3–26 weeks | ≥ 5 events |
| Monthly | Lag 2–12 months | ≥ 5 events |
| Quarterly | Lag 1–4 quarters | ≥ 4 events |
| Yearly | Lag 1–3 years | ≥ 3 events |

### 6. Model Families

#### 6.1 ML: LightGBM with deferral distribution features (trigger × lag weight)
#### 6.2 DL: TFT with distributed lag encoding
#### 6.3 Statistical: Distributed lag model (Almon or Koyck lag structure)

**Koyck Distributed Lag:**
```
d(t) = α + β × trigger(t) + λ × d(t−1) + ε(t)
λ ∈ (0,1) = geometric decay factor
Mean lag = λ / (1−λ)   [average deferral period]
```

### Evaluation

| Granularity | WMAPE Target | Deferral Distribution Accuracy | Bias Alert |
|---|---|---|---|
| Daily | < 28% | Distribution within ±15% | \|Bias\| > 12% |
| Weekly | < 24% | Distribution within ±12% | \|Bias\| > 10% |
| Monthly | < 20% | Distribution within ±10% | \|Bias\| > 8% |
| Quarterly | < 17% | Distribution within ±8% | \|Bias\| > 6% |
| Yearly | < 14% | Distribution within ±6% | \|Bias\| > 5% |

---
