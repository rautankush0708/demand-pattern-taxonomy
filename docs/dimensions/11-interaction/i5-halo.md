## I5 · Halo

### 1. Definition
Predicts demand for SKUs where a hero SKU's performance lifts demand for associated SKUs (r > 0.40; causal direction confirmed), requiring hero-follower modelling where the hero SKU forecast is used as a leading input for follower SKU forecasts.

### 5. Model Strategy

#### 5.1 Hero-Follower Model
```
d_follower(t) = d_follower_baseline(t) × (1 + halo_factor × d_hero(t) / d_hero_mean)
halo_factor estimated from: d_follower(t) = α + β × d_hero(t) + controls + ε
β > 0 → positive halo; β / mean(d_follower) = halo elasticity

Causal direction test: Granger causality from hero to follower (not reverse)
  H0: d_hero does NOT Granger-cause d_follower
  Reject H0 at p < 0.05 → confirmed hero → follower direction
```

### 6. Model Families

#### 6.1 ML: LightGBM — hero SKU demand as primary feature for follower
#### 6.2 DL: Shared TFT across hero + follower SKUs
#### 6.3 Statistical: Dynamic regression (follower ~ hero + controls + ARIMA residual)

### Evaluation

| Granularity | Follower WMAPE | Halo Granger Causality | Halo Coefficient Stability | Bias Alert |
|---|---|---|---|---|
| Daily | < 22% | p < 0.05 confirmed | CV(β) < 0.30 | |Bias| > 10% |
| Weekly | < 18% | p < 0.05 | CV(β) < 0.30 | |Bias| > 8% |
| Monthly | < 15% | p < 0.05 | CV(β) < 0.30 | |Bias| > 7% |
| Quarterly | < 12% | p < 0.05 | CV(β) < 0.30 | |Bias| > 6% |
| Yearly | < 10% | p < 0.05 | CV(β) < 0.30 | |Bias| > 5% |
