# Decision Engine
## Classification Logic · Threshold Summary

---

> This module provides the "Master Logic" that synthesizes all metrics and tests into a final SKU fingerprint across 12 dimensions.

---

## 15. Master Classification Decision Tree

```
INPUT: SKU demand history at chosen granularity
  │
  ├── STEP 1: LIFECYCLE
  │     ├── Zero demand ≥ Inactive threshold?    → INACTIVE
  │     ├── History < Cold Start upper bound?    → COLD START
  │     ├── History in New Launch range?         → NEW LAUNCH
  │     ├── Discontinuation flag set?            → PHASING OUT
  │     ├── Slope p < 0.05 positive?             → GROWTH
  │     ├── Slope p < 0.05 negative?             → DECLINE
  │     └── Slope p ≥ 0.10?                     → MATURE
  │
  ├── STEP 2: STRUCTURAL BREAK CHECK
  │     └── Chow/CUSUM significant?             → STEP CHANGE (Behavior)
  │
  ├── STEP 3: BEHAVIOR (CV² × ADI)
  │     ├── Low CV², Low ADI
  │     │     ├── Volume < 5th pctile?           → SLOW MOVER
  │     │     ├── Trend detected?                → TRENDING
  │     │     └── Default                        → STABLE
  │     ├── Low CV², High ADI
  │     │     ├── CV_arrival < 0.30?             → PULSED
  │     │     └── Default                        → INTERMITTENT
  │     ├── High CV², Low ADI                    → ERRATIC
  │     └── High CV², High ADI                   → LUMPY
  │
  ├── STEP 4: MAGNITUDE
  │     └── Volume percentile vs portfolio
  │
  ├── STEP 5: TREND
  │     └── Mann-Kendall direction + ADF + FFT
  │
  ├── STEP 6: CONCENTRATION
  │     └── DCI_norm + Gini + Modality + Skewness
  │
  ├── STEP 7: DRIVER (stack all that apply)
  │     ├── ACF seasonal?                        → SEASONAL
  │     ├── Event calendar correlation?          → EVENT DRIVEN
  │     ├── Promo uplift > 15%?                  → PROMOTIONAL
  │     ├── Weather |r| > 0.30?                  → WEATHER DRIVEN
  │     ├── HHI > 0.60?                          → CUSTOMER DRIVEN
  │     └── Stockout events > threshold?         → SUPPLY CONSTRAINED
  │
  ├── STEP 8: SHOCK
  │     └── SRS + Recovery Rate + Level Change
  │
  ├── STEP 9: ELASTICITY
  │     └── PED log-log regression + NLS saturation + Threshold test
  │
  ├── STEP 10: TIMING
  │     └── CCF at lags k = −H to +H
  │
  ├── STEP 11: RECURRENCE
  │     └── CV_IAT + MK test on recurrence rate
  │
  ├── STEP 12: INTERACTION
  │     └── Cross-SKU Pearson r + OOS substitution + Granger causality
  │
  └── STEP 13: SIGNAL
        └── SNR + DI + AR bullwhip + Signal lag L

OUTPUT: 12-dimension SKU fingerprint
```

---

## 16. Quantitative Threshold Summary

| Metric | Threshold | Separates |
|---|---|---|
| History (weeks) | < 8 | Cold Start |
| History (weeks) | 8–16 | New Launch |
| Zero demand streak | > 13 weeks | Inactive |
| ADI (weekly) | 1.32 | Regular vs Intermittent |
| CV² | 0.49 | Smooth vs Variable |
| Inter-arrival CV | < 0.30 | Pulsed vs Intermittent |
| Volume | < 5th pctile | Slow Mover |
| Mann-Kendall p | < 0.05 | Trend significant |
| Chow / CUSUM | Significant | Step Change |
| Herfindahl Index | > 0.60 | Customer Driven |
| ACF (seasonal lag) | > 2/√n | Seasonal |
| Stockout events | > 2 in window | Supply Constrained |
| PED | < −1.0 | Elastic |
| Promo uplift | > 15% per 10% discount | Elastic |
| SNR | > 4.0 | Pure Signal |
| SNR | < 1.0 | Noisy |
| Bullwhip AR | > 1.5 | Amplified Signal |
| Distortion Index | > 0.15 in > 20% periods | Distorted |
| SRS | > 0.60 | Shock Resistant |
| SRS | < 0.40 | Shock Sensitive |
| Recovery Rate | RR > 0.80 within fast HRT | Fast Recovery |
| Level Change Δ | > +15% permanent | Permanent Shift |
| Level Change Δ | < −15% permanent | Step Down |
| DCI_norm (weekly) | > 0.30 | Peaked |
| Gini (weekly) | > 0.40 | Peaked |
| Skewness | > 0.50 | Skewed |
| CCF(k) | > 2/√n at k < 0 | Leading |
| CCF(k) | > 2/√n at k > 0 | Lagging |
| CV_IAT | < 0.20 | Regular Recurrence |
| Pearson r (cross-SKU) | > 0.50 | Complementary |
| Cannibalism δ | < −0.15 | Cannibalistic |
| Halo Granger p | < 0.05 | Halo confirmed |
