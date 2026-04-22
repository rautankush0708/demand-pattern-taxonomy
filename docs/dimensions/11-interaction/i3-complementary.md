## I3 · Complementary

### 1. Definition
Predicts demand for SKUs that move in sync with a correlated partner SKU (r > 0.50), enabling cross-SKU signal sharing to improve forecast accuracy for both SKUs simultaneously.

### 5. Model Strategy

#### 5.1 Cross-SKU Signal Sharing
```
d_A(t) = f(d_A_history, d_B_history, shared_features)
where d_B(t) provides additional signal for d_A(t) and vice versa

Feature: d_B(t−1), d_B(t−2), cross_correlation_strength
Cross-SKU feature weight proportional to |r(A,B)|
```

### 6. Model Families

#### 6.1 ML: LightGBM with lagged partner SKU demand as feature
#### 6.2 DL: DeepAR or TFT trained jointly across complementary SKU pairs (shared model)
#### 6.3 Statistical: Multivariate time series (VAR model if r > 0.70)

**VAR(1) for Complementary Pairs:**
```
[d_A(t)]   [c_A]   [A_11 A_12] [d_A(t-1)]   [ε_A(t)]
[d_B(t)] = [c_B] + [A_21 A_22] [d_B(t-1)] + [ε_B(t)]
A_12 > 0 → B Granger-causes A (useful cross-SKU feature)
A_21 > 0 → A Granger-causes B
```

### Evaluation

| Granularity | WMAPE Improvement vs Independent | Cross-Correlation Maintained | Bias Alert |
|---|---|---|---|
| Daily | > 5% improvement | r > 0.40 | |Bias| > 8% |
| Weekly | > 5% improvement | r > 0.40 | |Bias| > 7% |
| Monthly | > 5% improvement | r > 0.35 | |Bias| > 6% |
| Quarterly | > 5% improvement | r > 0.35 | |Bias| > 5% |
| Yearly | > 4% improvement | r > 0.30 | |Bias| > 4% |

---

