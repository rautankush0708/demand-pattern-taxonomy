## SG1 · Pure Signal
### 1. Definition
Predicts demand for SKUs where the observed demand series accurately reflects true underlying consumption (SNR > 4.0; DI < 0.10), enabling direct application of statistical and ML models without pre-processing corrections.

### 5. Model Strategy
- Standard behavior model per segment — no signal correction required
- Signal quality monitoring: Monthly SNR check; alert if SNR drops below 2.0

### Evaluation — Standard per Behavior segment; add SNR as monitoring metric

---
