## C5 · Skewed
### 1. Definition
Predicts demand for SKUs where demand within a cycle is asymmetrically distributed — concentrated earlier or later in the cycle — requiring asymmetric seasonal indices and lead-time-aware inventory positioning to capture directional demand concentration.

### 2. Detailed Description
- **Applicable scenarios:** Budget-front-loaded categories (spend early in fiscal year), end-of-period purchasing (budget flush), early adopter purchase patterns, product ramp-up within cycle
- **Boundaries:**

| Granularity | Skewness Threshold | DCI_norm | Gini | Min Cycles |
|---|---|---|---|---|
| Daily | \|Pearson skewness\| > 0.5 | 0.15–0.40 | 0.20–0.50 | ≥ 2 weekly cycles |
| Weekly | \|Pearson skewness\| > 0.5 | 0.10–0.30 | 0.15–0.40 | ≥ 2 annual cycles |
| Monthly | \|Pearson skewness\| > 0.5 | 0.10–0.30 | 0.15–0.40 | ≥ 2 annual cycles |
| Quarterly | \|Pearson skewness\| > 0.5 | 0.15–0.40 | 0.20–0.50 | ≥ 2 annual cycles |
| Yearly | \|Pearson skewness\| > 0.5 | 0.15–0.40 | 0.20–0.50 | ≥ 3 years |

**Skewness Direction:**
```
Pearson skewness = 3 × (mean − median) / std

Positive skewness (> 0.5): Right-skewed → demand concentrated EARLY in cycle
  Example: Heavy January demand, tapering through the year (budget front-loading)

Negative skewness (< −0.5): Left-skewed → demand concentrated LATE in cycle
  Example: Low start-of-year demand, heavy December (budget flush, gift buying)
```

- **Key demand characteristics:** Asymmetric within-cycle distribution; demand trails off or builds across the cycle; not a single sharp peak but a gradual concentration at one end
- **Differentiation from other models:** Unlike Peaked, no single dominant period — concentration is gradual; unlike Uniform, distribution is clearly asymmetric; unlike Bi-Modal/Multi-Modal, concentration is at one end of the cycle not in distinct peaks

### 3. Business Impact
- **Primary risk (over-forecast for positive skew):** Over-ordering early; stock depletes quickly then demand falls away leaving no excess — lower risk
- **Primary risk (negative skew over-forecast):** Carrying excess early-cycle stock before late-cycle demand arrives — highest risk for left-skewed categories
- **Strategic importance:** Medium-high — correct timing of stock build relative to skew direction is the key operational challenge

### 4. Priority Level
🟠 Tier 2 — Skew direction determines inventory positioning strategy; medium complexity once direction confirmed.

### 5. Model Strategy Overview

#### 5.1 Skew-Aware Seasonal Index
```
Construct period-specific seasonal indices reflecting asymmetric pattern:

Right-skewed (front-loaded):
  SI(early periods) > 1.0 (demand above average)
  SI(late periods) < 1.0 (demand below average)
  Gradient: Seasonal index decreases monotonically across cycle

Left-skewed (end-loaded):
  SI(early periods) < 1.0
  SI(late periods) > 1.0
  Gradient: Seasonal index increases monotonically across cycle

Compute SI(p) = μ_period_p / μ_overall for each period in cycle
Verify skewness direction: skewness(SI values) confirms direction
```

#### 5.2 Feature Engineering

| Granularity | Skew Direction Features | Cycle Position Features | Rolling Features |
|---|---|---|---|
| Daily | Skewness flag (positive/negative), day in cycle (1 to n), cycle position ratio (day/n), cumulative cycle demand, SI gradient | Day of week, holiday flag, days to cycle end | 7/30-day rolling mean, SI |
| Weekly | Skewness flag, week in cycle, cycle position ratio, cumulative cycle demand, SI gradient | Week of year, promo flag | 4/8-week rolling mean, SI |
| Monthly | Skewness flag, month in cycle, cycle position ratio, SI gradient | Month of year, fiscal period flag | 3/6-month rolling mean, SI |
| Quarterly | Skewness flag, quarter in cycle, cycle position ratio | Fiscal year quarter, budget cycle flag | 2/4-quarter rolling mean, SI |
| Yearly | Skewness flag, year in sequence, cycle position | Budget year flag | Annual rolling mean |

### 6. Model Families

#### 6.1 ML: LightGBM with cycle position and skew direction features
- Objective: reg:squarederror; Metric: WMAPE
- Cycle position ratio is the primary feature — captures gradual within-cycle concentration

#### 6.2 DL: TFT — attention mechanism naturally captures within-cycle asymmetric patterns

| Granularity | Lookback | Key Feature |
|---|---|---|
| Daily | 365 days | Day-in-cycle index |
| Weekly | 104 weeks | Week-in-cycle index |
| Monthly | 36 months | Month-in-cycle index |
| Quarterly | 12 quarters | Quarter-in-cycle index |
| Yearly | 5 years | Year-in-cycle index |

#### 6.3 Statistical: ETS(A,N,A) with asymmetric seasonal indices

**Asymmetric Seasonal Index Update:**
```
For right-skewed (front-loaded): Apply higher weight to early-cycle observations in SI estimation
  γ_early = 0.15 (faster update — early cycle SI more variable)
  γ_late = 0.05 (slower update — late cycle SI stable at low level)

For left-skewed (end-loaded): Reverse — faster update for late periods
  γ_late = 0.15; γ_early = 0.05
```

#### 6.4 Fallback: Prior year same period × (1 + trend_rate); maintains skew pattern from prior year

### 7. Ensemble

| Skew Strength | LightGBM | TFT | ETS(A,N,A) |
|---|---|---|---|
| Mild (\|skewness\| 0.5–1.0) | 45% | 20% | 35% |
| Moderate (\|skewness\| 1.0–2.0) | 50% | 25% | 25% |
| Strong (\|skewness\| > 2.0) | 55% | 30% | 15% |

### 8. Uncertainty Quantification
- Method: Quantile regression with cycle-position-conditioned intervals
- Output: [P10, P50, P90] — asymmetric across cycle (wider early for right-skew; wider late for left-skew)
- Use case:
  - Right-skew: Stock early at P75; reduce to P25 for later periods
  - Left-skew: Conservative early stock at P25; build to P75 approach to cycle end

### 9. Business Rules
- Non-negativity: max(0, forecast)
- Inventory build timing rule: Right-skew → front-load inventory; Left-skew → hold stock, build toward cycle end
- Alignment: SI gradient direction must match historical skew direction — alert if reversed
- Manual overrides: Budget cycle change (fiscal year shift); pricing structure change affecting skew direction

### 10. Evaluation

#### 10.1 Key Metrics

| Granularity | WMAPE Target | Early-Cycle WMAPE | Late-Cycle WMAPE | Bias Alert | Skew Direction Accuracy |
|---|---|---|---|---|---|
| Daily | < 22% | < 25% | < 20% | \|Bias\| > 10% | Direction correct > 90% of cycles |
| Weekly | < 18% | < 22% | < 18% | \|Bias\| > 8% | Direction correct > 90% |
| Monthly | < 15% | < 18% | < 15% | \|Bias\| > 7% | Direction correct > 90% |
| Quarterly | < 12% | < 15% | < 12% | \|Bias\| > 6% | Direction correct > 90% |
| Yearly | < 10% | < 12% | < 10% | \|Bias\| > 5% | Direction correct > 90% |

#### 10.2 Backtesting — rolling seasonal window ≥ 2 full cycles; evaluate early and late cycle separately

#### 10.3 Retraining — standard cadence + triggered on fiscal year / budget cycle change

### 11. Exception Handling
- Alert: Skew direction reverses vs prior cycle → investigate structural change; |skewness| drops below 0.3 for 2 cycles → reclassify to Uniform or Peaked

### 12. Reclassification

| Condition | Target | Holding Period |
|---|---|---|
| |skewness| drops below 0.3 for 2 cycles; DCI_norm below threshold | Uniform | 2 cycles |
| Single clear peak emerges for 2 cycles | Peaked | 2 cycles |
| |skewness| drops below 0.3; single peak remains high | Peaked | 2 cycles |
| Two peaks emerge at opposite ends of skew for 2 cycles | Bi-Modal | 2 cycles |

### 13. Review Cadence
- Quarterly skewness monitor; annual skew direction confirmation; full re-evaluation on any fiscal/budget cycle change

---

*End of Dimension 6 · Concentration Pattern*
*5 Segments Complete · C1 through C5*
