# Segment Model Template

## Dimension 12 · Amplified

---

### 1. Definition
Predicts demand for SKUs where the observed upstream order signal is amplified relative to true end-consumer demand due to the bullwhip effect (AR > 1.5), requiring demand sensing correction and end-to-end signal reconstruction to recover the true consumption baseline.

### 2. Detailed Description
- **Applicable scenarios:** Multi-tier supply chains where distributors or wholesalers amplify ordering variability; categories with large distributor safety stocks; batch-ordering behaviour by intermediaries; supply chain tiers far from end consumer
- **Boundaries:**

| Granularity | AR Threshold | Estimation Window | Downstream Data Required |
|---|---|---|---|
| Daily | AR > 1.5 | 90-day rolling | POS or retail offtake preferred |
| Weekly | AR > 1.5 | 52-week rolling | POS or retail offtake |
| Monthly | AR > 1.5 | 24-month rolling | Retail sell-through data |
| Quarterly | AR > 1.5 | 8-quarter rolling | Category consumption index |
| Yearly | AR > 1.5 | 3-year rolling | Market consumption data |

- **Key demand characteristics:** Upstream orders are far more variable than true end-consumer demand; batch ordering, safety stock overshoot, and forecasting errors at each tier amplify variability; true demand is smoother and more predictable than observed orders suggest
- **Differentiation from other models:** Unlike Noisy (random noise at measurement), Amplified has a structural cause — supply chain tier structure; unlike Distorted (systematic magnitude error), Amplified is a variance amplification not mean distortion

### 3. Business Impact
- **Primary risk (over-forecast):** Modelling on amplified orders — wildly variable forecast; excess safety stock at every tier; cascading overstock
- **Primary risk (under-forecast):** Not planning for amplified order peaks — production/supply capacity shock
- **Strategic importance:** Very high — bullwhip effect is one of the largest sources of supply chain waste; de-amplification is the foundation of demand-driven supply chain management

### 4. Priority Level
🔴 **Tier 1** — Amplified signal corrupts capacity planning and inventory policy across the entire supply chain; de-amplification must precede all other modelling.

### 5. Model Strategy Overview

#### 5.1 Bullwhip De-amplification Pipeline
```
STEP 1: Estimate Amplification Ratio
  AR = Var(Orders_upstream) / Var(d_downstream)
  If downstream POS available: use directly
  If not: estimate AR from order variability patterns

STEP 2: De-amplification

  Method A — POS Direct (best):
    d_true(t) = d_POS(t)   [use end-consumer POS data directly]
    No de-amplification needed — POS is the true signal

  Method B — Exponential Smoothing:
    d_smooth(t) = α_deamp × d_observed(t) + (1−α_deamp) × d_smooth(t−1)
    α_deamp = 2 / (AR + 1)   [de-amplification factor]
    Higher AR → lower α → more smoothing

  Method C — Kalman Filter State Space:
    State (true demand): μ(t) = μ(t-1) + η(t)   η ~ N(0, σ²_demand)
    Observation (orders): d_obs(t) = μ(t) + AR × noise(t)   noise ~ N(0, σ²_noise)
    σ²_noise = (AR − 1) × σ²_demand
    Kalman filter estimates true μ(t) from amplified d_obs(t)

STEP 3: Apply standard behavior model to de-amplified series
```

#### 5.2 Analogue / Similarity Logic
- Per Behavior segment — applied after de-amplification
- Additional: Analogues from same supply chain tier and category to validate AR estimate

#### 5.3 Feature Engineering
- All features computed on **de-amplified demand series** — never on raw amplified orders
- Additional features:

| Feature | Description |
|---|---|
| AR | Estimated amplification ratio |
| α_deamp | De-amplification smoothing factor |
| tier_distance | Supply chain tiers from end consumer |
| downstream_data_available | 1 if POS data available; 0 otherwise |
| order_batch_size | Mean batch size of upstream orders |
| reorder_interval | Mean time between upstream orders |

| Granularity | Amplification Features | De-Amplified Baseline Features |
|---|---|---|
| Daily | AR, α_deamp, tier_distance, order batch size | 7/30/90-day de-amplified rolling mean, seasonal index |
| Weekly | AR, α_deamp, tier_distance | 4/8/13-week de-amplified rolling mean, seasonal index |
| Monthly | AR, α_deamp | 3/6/12-month de-amplified rolling mean |
| Quarterly | AR, α_deamp | 2/4-quarter de-amplified rolling mean |
| Yearly | AR | Annual de-amplified rolling mean |

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: Standard LightGBM per Behavior segment — applied to de-amplified series
- Additional: AR and tier_distance as metadata features (characterise amplification structure)
- When to use: After de-amplification — same model as standard

#### 6.2 Deep Learning (DL)
- Architectures: TFT with both observed (amplified) and de-amplified series as inputs
- Observed orders: Past observed covariate (captures ordering patterns)
- De-amplified: Primary target series

| Granularity | Lookback | Covariates | Output |
|---|---|---|---|
| Daily | 180 days | d_obs(t) + d_deamp(t) | P10, P50, P90 |
| Weekly | 52 weeks | d_obs(t) + d_deamp(t) | P10, P50, P90 |
| Monthly | 24 months | d_obs(t) + d_deamp(t) | P10, P50, P90 |
| Quarterly | 8 quarters | d_obs(t) + d_deamp(t) | P10, P50, P90 |
| Yearly | 5 years | d_obs(t) only | P10, P50, P90 |

#### 6.3 Statistical / Time Series Models
- Architectures: Kalman filter de-amplification model (primary) → ETS on de-amplified output

**Kalman De-amplification:**
```
State:        μ(t) = μ(t-1) + η(t)              η ~ N(0, σ²_demand)
Observation:  d_obs(t) = μ(t) + noise(t)        noise ~ N(0, H)
H = (AR − 1) × σ²_demand   [amplification noise variance]

Kalman update:
  K(t) = σ²_demand / (σ²_demand + H)   [Kalman gain]
  μ_posterior(t) = μ_prior(t) + K(t) × (d_obs(t) − μ_prior(t))
  = de-amplified demand estimate
```

- When to use: Primary de-amplification method when no POS data available

#### 6.4 Baseline / Fallback Model
- Fallback: Simple exponential smoothing on raw orders (basic de-amplification without Kalman)
- Alert: If AR rises above 2.5 → severe bullwhip; escalate to supply chain leadership

### 7. Ensemble & Weighting

#### 7.1 Ensemble Scheme
- De-amplification: Kalman filter (primary) for de-amplification step — not ensemble
- Forecasting on de-amplified series: Standard ensemble per Behavior segment

#### 7.2 Dynamic Weight Schedule (De-amplification method selection)

| Data Availability | Method |
|---|---|
| POS data available | Method A (POS Direct) — 100%; no de-amplification needed |
| Partial POS + orders | 70% Method A + 30% Method B |
| Orders only | Method C (Kalman Filter) — 100% |

### 8. Uncertainty Quantification
- Method: Standard per Behavior segment on de-amplified series; additional uncertainty from AR estimate variance
- Output: [P10, P50, P90] — width reflects de-amplified demand uncertainty not amplified order uncertainty
- Use case: Safety stock based on de-amplified demand variability — substantially lower than amplified order variability

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, de-amplified forecast)
- Hard rule: Raw amplified orders must NEVER be used as demand input to models
- POS priority: If end-consumer POS data becomes available → immediately switch to Method A (POS Direct)
- AR monitor: Alert if AR rises above 2.0 — severe bullwhip; supply chain structural review required
- Capacity planning rule: Use de-amplified demand for capacity planning; use amplified order patterns for order management planning only
- Manual overrides: Supply chain team AR estimate revision; POS data feed activation; tier structure change

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | AR Estimate Accuracy | De-amplified WMAPE | Downstream Alignment | Supply Chain AR Monitor | Bias Alert |
|---|---|---|---|---|---|
| Daily | AR within ±0.3 | Per Behavior std | r(deamplified, POS) > 0.70 | Alert if AR > 2.0 | \|Bias\| > 10% |
| Weekly | AR within ±0.3 | Per Behavior std | r > 0.70 | Alert if AR > 2.0 | \|Bias\| > 8% |
| Monthly | AR within ±0.2 | Per Behavior std | r > 0.65 | Alert if AR > 2.0 | \|Bias\| > 7% |
| Quarterly | AR within ±0.2 | Per Behavior std | r > 0.65 | Alert if AR > 2.0 | \|Bias\| > 6% |
| Yearly | AR within ±0.2 | Per Behavior std | r > 0.60 | Alert if AR > 2.0 | \|Bias\| > 5% |

#### 10.2 Backtesting Protocol

| Granularity | Method | Train | Test |
|---|---|---|---|
| Daily | Rolling window on de-amplified | 180 days | 30 days |
| Weekly | Rolling window on de-amplified | 52 weeks | 13 weeks |
| Monthly | Rolling window on de-amplified | 24 months | 6 months |
| Quarterly | Rolling window on de-amplified | 8 quarters | 2 quarters |
| Yearly | Expanding window | All available | 1 year |

#### 10.3 Retraining

| Granularity | Cadence | POS/Downstream Feed | Latency |
|---|---|---|---|
| Daily | Daily | POS daily; order daily | T+4 hours |
| Weekly | Weekly | POS weekly | T+1 day |
| Monthly | Monthly | Retail sell-through monthly | T+2 days |
| Quarterly | Quarterly | Category consumption | T+3 days |
| Yearly | Annually | Market data | T+7 days |

### 11. Exception Handling & Overrides
- Auto-detect: AR rises above 2.5 → P1 escalation to supply chain leadership; POS data feed activated → immediately switch to Method A; AR drops below 1.2 for 6 months → reclassify to Pure Signal; Noisy signal detected on de-amplified series → apply noise correction as secondary step
- Manual override: Supply chain team AR override (e.g. known structural ordering change); POS integration go-live; new distribution tier added (increases expected AR)
- Override expiration: Per quarterly AR review

### 12. Reclassification / Model Selection

| Condition | Target | Holding Period | Transition |
|---|---|---|---|
| AR drops below 1.2 for 6 consecutive months | Pure Signal | 6 months | Hard switch — remove de-amplification |
| POS data available (AR → 1.0 effectively) | Pure Signal | Immediate | Hard switch to POS-based model |
| SNR of de-amplified series < 1.0 | Noisy (secondary) | 2 estimations | Add noise correction layer after de-amplification |
| DI detected on de-amplified series | Distorted (secondary) | 2 estimations | Apply distortion correction after de-amplification |

### 13. Review Cadence
- Monthly AR monitor with tier-by-tier breakdown; quarterly de-amplification calibration; annual supply chain structure review to identify bullwhip root causes and structural remediation opportunities

---

*End of Dimension 12 · Signal Pattern*
*5 Segments Complete · SG1 through SG5*

---

# MASTER SEGMENT INDEX

| Dim | Segment | Code |
|---|---|---|
| 1 | Cold Start | L1 |
| 1 | New Launch | L2 |
| 1 | Growth | L3 |
| 1 | Mature | L4 |
| 1 | Decline | L5 |
| 1 | Phasing Out | L6 |
| 1 | Inactive | L7 |
| 2 | Stable | B1 |
| 2 | Intermittent | B2 |
| 2 | Erratic | B3 |
| 2 | Lumpy | B4 |
| 2 | Trending | B5 |
| 2 | Step Change | B6 |
| 2 | Pulsed | B7 |
| 2 | Slow Mover | B8 |
| 3 | Seasonal | D1 |
| 3 | Event Driven | D2 |
| 3 | Promotional | D3 |
| 3 | Weather Driven | D4 |
| 3 | Customer Driven | D5 |
| 3 | Supply Constrained | D6 |
| 4 | High Volume | M1 |
| 4 | Medium Volume | M2 |
| 4 | Low Volume | M3 |
| 4 | Ultra Low | M4 |
| 5 | Upward Trend | T1 |
| 5 | Downward Trend | T2 |
| 5 | Flat | T3 |
| 5 | Cyclical Trend | T4 |
| 5 | Reverting | T5 |
| 6 | Uniform | C1 |
| 6 | Peaked | C2 |
| 6 | Bi-Modal | C3 |
| 6 | Multi-Modal | C4 |
| 6 | Skewed | C5 |
| 7 | Shock Resistant | SH1 |
| 7 | Shock Sensitive | SH2 |
| 7 | Fast Recovery | SH3 |
| 7 | Slow Recovery | SH4 |
| 7 | Permanent Shift | SH5 |
| 7 | Step Down | SH6 |
| 8 | Elastic | E1 |
| 8 | Inelastic | E2 |
| 8 | Threshold | E3 |
| 8 | Saturation | E4 |
| 9 | Leading | TM1 |
| 9 | Lagging | TM2 |
| 9 | Coincident | TM3 |
| 9 | Deferred | TM4 |
| 9 | Accelerated | TM5 |
| 10 | Regular | RC1 |
| 10 | Irregular | RC2 |
| 10 | One Time | RC3 |
| 10 | Declining Recurrence | RC4 |
| 10 | Growing Recurrence | RC5 |
| 11 | Independent | I1 |
| 11 | Substitution | I2 |
| 11 | Complementary | I3 |
| 11 | Cannibalistic | I4 |
| 11 | Halo | I5 |
| 12 | Pure Signal | SG1 |
| 12 | Distorted | SG2 |
| 12 | Noisy | SG3 |
| 12 | Lagged Signal | SG4 |
| 12 | Amplified | SG5 |

---
