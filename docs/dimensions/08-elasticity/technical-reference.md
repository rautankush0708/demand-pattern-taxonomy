
# PART 0 — FORMULA & THRESHOLD REFERENCE
## Elasticity Pattern Specific

---

## 0.1 Core Segmentation Metrics

### A. Price Elasticity of Demand (PED)
> Measures percentage change in demand for a 1% change in price

**General Formula:**
```
PED = % Change in Quantity Demanded / % Change in Price
    = (ΔQ / Q) / (ΔP / P)
    = (dQ/dP) × (P/Q)

PED < 0 always (inverse relationship — higher price → lower demand)
|PED| < 1 → Inelastic (demand changes less than price)
|PED| = 1 → Unit elastic
|PED| > 1 → Elastic (demand changes more than price)
|PED| > 2 → Highly elastic
```

**Log-Log Regression Estimation:**
```
ln(Q_t) = α + β × ln(P_t) + γ × X_t + ε_t
where β = PED (directly estimated)
      X_t = control variables (seasonality, promotions, distribution)
      β < −1 → Elastic
      −1 < β < 0 → Inelastic
```

| Granularity | Estimation Window | Min Price Changes Required | Method |
|---|---|---|---|
| **Daily** | 180-day rolling | ≥ 10 price change events | Log-log OLS with controls |
| **Weekly** | 52-week rolling | ≥ 8 price change events | Log-log OLS with controls |
| **Monthly** | 24-month rolling | ≥ 6 price change events | Log-log OLS with controls |
| **Quarterly** | 8-quarter rolling | ≥ 4 price change events | Log-log OLS with controls |
| **Yearly** | 3-year rolling | ≥ 3 price change events | Log-log OLS with controls |

---

### B. Promotional Elasticity
> Measures demand response to promotional discount depth

**General Formula:**
```
Promo Elasticity = % Change in Demand / % Change in Price (during promotion)
                = ln(Q_promo / Q_baseline) / ln(P_promo / P_regular)

Uplift Factor = Q_promo / Q_baseline − 1   [expressed as % uplift per % discount]
```

**Estimation:**
```
Q_promo(t) = Q_baseline(t) × exp(β_promo × depth(t) + β_type × promo_type(t))
where depth(t) = (P_regular − P_promo) / P_regular × 100   [% discount]
      β_promo = promotional elasticity coefficient
      β_type = promotion type multiplier {price_cut, multibuy, display, TPR}
```

| Granularity | Min Promotions Required | Controls |
|---|---|---|
| **Daily** | ≥ 8 promotion events | Season, baseline trend, distribution |
| **Weekly** | ≥ 6 promotion events | Season, baseline trend |
| **Monthly** | ≥ 5 promotion events | Season, trend |
| **Quarterly** | ≥ 4 promotion events | Trend |
| **Yearly** | ≥ 3 promotion events | Trend |

---

### C. Threshold Detection
> Identifies non-linear demand response with a stimulus activation threshold

**General Formula:**
```
Demand response is non-linear:
  d(t) = d_baseline(t)                           if stimulus(t) < threshold
  d(t) = d_baseline(t) × response_factor(t)     if stimulus(t) ≥ threshold

Threshold estimation:
  Fit piecewise regression with unknown breakpoint T*:
  Q(t) = α + β_1 × stimulus(t) × I(stimulus < T*) + β_2 × stimulus(t) × I(stimulus ≥ T*)
  Estimate T* via grid search: minimise RSS across candidate threshold values T* ∈ [5%, 50%]

Threshold confirmed: RSS reduction > 20% vs linear model AND p < 0.05 for β_2 − β_1
```

| Granularity | Grid Search Range | Step Size | Min Events Above Threshold |
|---|---|---|---|
| **Daily** | 5%–50% discount depth | 2.5% | ≥ 5 events |
| **Weekly** | 5%–50% discount depth | 2.5% | ≥ 5 events |
| **Monthly** | 5%–50% discount depth | 5% | ≥ 4 events |
| **Quarterly** | 5%–50% discount depth | 5% | ≥ 3 events |
| **Yearly** | 5%–50% discount depth | 10% | ≥ 3 events |

---

### D. Saturation Detection
> Identifies maximum demand ceiling beyond which additional stimulus generates no further response

**General Formula:**
```
Saturation model:
  Q(t) = Q_max × [1 − e^{−λ × stimulus(t)}]   [Logistic saturation curve]
  where Q_max = demand ceiling (estimated via NLS)
        λ = rate of saturation

Saturation confirmed:
  (1) Q_max estimated and statistically significant (p < 0.05)
  (2) Current observed demand at stimulus peak ≥ 0.90 × Q_max
  (3) Marginal response at high stimulus < 10% of marginal response at low stimulus

Alternative: Adstock diminishing returns model:
  Response(t) = β_1 × stimulus(t)^β_2   where β_2 < 1 → diminishing returns
  β_2 < 0.50 → strong saturation signal
```

| Granularity | NLS Estimation Window | Saturation Threshold |
|---|---|---|
| **Daily** | 365-day rolling | Observed demand ≥ 0.90 × Q_max |
| **Weekly** | 104-week rolling | Observed demand ≥ 0.90 × Q_max |
| **Monthly** | 36-month rolling | Observed demand ≥ 0.90 × Q_max |
| **Quarterly** | 12-quarter rolling | Observed demand ≥ 0.90 × Q_max |
| **Yearly** | 5-year rolling | Observed demand ≥ 0.90 × Q_max |

---

## 0.2 Elasticity Classification Decision Rules

```
STEP 1: Estimate PED via log-log regression (Section 0.1A)
  Sufficient price variation detected?
    YES → proceed with PED estimate
    NO  → use Promotional Elasticity as proxy (Section 0.1B)

STEP 2: Test for non-linearity
  Run Threshold detection (Section 0.1C)
  Threshold confirmed? → THRESHOLD segment

  Run Saturation detection (Section 0.1D)
  Saturation confirmed? → SATURATION segment

STEP 3: Apply linear elasticity classification (if no non-linearity)
  |PED| > 1.0 OR Promo Elasticity β_promo > 0.015/% → ELASTIC
  |PED| < 1.0 AND Promo Elasticity β_promo < 0.008/% → INELASTIC

Confidence rules:
  < minimum price changes required → provisional estimate; flag as low confidence
  Conflicting PED and Promo Elasticity signals → use Promo Elasticity (more data)
  Coefficient of variation of PED estimates > 0.50 → flag as unstable elasticity
```

---

## 0.3 Elasticity Coefficient Reference Table

| Segment | PED Range | Promo Uplift per 10% Discount | Behaviour |
|---|---|---|---|
| **Elastic** | PED < −1.0 | > 15% uplift | Large demand response to small price/promo change |
| **Inelastic** | −1.0 < PED < 0 | < 8% uplift | Small demand response to large price/promo change |
| **Threshold** | Non-linear (PED varies by stimulus level) | < 5% below T*; > 20% above T* | No response below threshold; large response above |
| **Saturation** | Diminishing (PED → 0 at high stimulus) | > 20% at low stimulus; < 5% at high stimulus | Strong early response; caps at ceiling |

---

## 0.4 Rolling Window Reference

| Window Name | Daily | Weekly | Monthly | Quarterly | Yearly |
|---|---|---|---|---|---|
| **Short** | 7 days | 4 weeks | 2 months | 1 quarter | 1 year |
| **Medium** | 30 days | 8 weeks | 3 months | 2 quarters | 2 years |
| **Long** | 90 days | 13 weeks | 6 months | 3 quarters | 3 years |
| **Estimation** | 180 days | 52 weeks | 24 months | 8 quarters | 3 years |
| **DL Lookback** | 180 days | 52 weeks | 24 months | 8 quarters | 5 years |

---

## 0.5 Accuracy Metric Formulas

```
Standard metrics:
  WMAPE = Σ|Forecast_t − Actual_t| / Σ Actual_t × 100
  Bias  = Σ(Forecast_t − Actual_t) / Σ Actual_t × 100

Elasticity-specific metrics:
  Uplift Accuracy = |Predicted Uplift − Actual Uplift| / Actual Uplift × 100
  Elasticity Stability = CV(PED estimates over rolling windows)  (Target < 0.30)
  Price Response R² = R² of log-log regression (Target > 0.30)
  Promotion Forecast Lift = WMAPE improvement vs no-promo model (Target > 10%)

Pinball Loss:
  Pinball(α,t) = α × (Actual_t − Q_α)     if Actual_t ≥ Q_α
               = (1−α) × (Q_α − Actual_t)  if Actual_t < Q_α
Coverage = Actuals within [P10, P90] / n × 100  (Target: 80%)
```

---

## 0.6 Retraining & Backtesting Reference

| Granularity | Retraining | Latency | Backtest Train | Backtest Test |
|---|---|---|---|---|
| **Daily** | Daily | T+4 hours | 180 days | 30 days |
| **Weekly** | Weekly | T+1 day | 52 weeks | 13 weeks |
| **Monthly** | Monthly | T+2 days | 24 months | 6 months |
| **Quarterly** | Quarterly | T+3 days | 8 quarters | 2 quarters |
| **Yearly** | Annually | T+7 days | All available | 1 year |

---

# PART 1 — SEGMENT TEMPLATES

---

