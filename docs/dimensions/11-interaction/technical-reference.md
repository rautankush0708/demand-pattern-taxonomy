## 0.3 Interaction Pattern Metrics

### A. Cross-SKU Correlation
```
Pearson correlation between SKU_A and SKU_B demand:
  r(A,B) = Σ[(d_A(t) − d̄_A)(d_B(t) − d̄_B)] / [n × σ_A × σ_B]

Complementary: r > +0.50 (demand moves together)
Substitution:  r < −0.30 AND SKU_B stockout → SKU_A spike
Cannibalistic: r < −0.30 AND SKU_A grows → SKU_B shrinks
Halo:          r > +0.40 AND causal direction (hero → follower)
Independent:   |r| < 0.20
```

### B. Substitution Detection
```
Substitution event: Period where SKU_B is OOS (stockout)
                    AND SKU_A demand spikes > 1.5σ above baseline

Substitution rate: sub_rate = mean(d_A during SKU_B OOS) / mean(d_A during SKU_B available) − 1

Significant substitution: sub_rate > 0.20 AND confirmed in ≥ 3 OOS events
```

### C. Cannibalism Detection
```
Cannibalism coefficient: δ = ΔQ_B / ΔQ_A (demand lost from B per unit gained by A)

Estimated via regression:
  ΔQ_B(t) = α + δ × ΔQ_A(t) + β × controls(t) + ε(t)
  δ < 0 → A cannibalises B; |δ| = cannibalism rate
  Significant: p < 0.05 for δ AND |δ| > 0.15
```

---

# PART 1 — SEGMENT TEMPLATES

