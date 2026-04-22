## TM1 · Leading
### 1. Definition
Predicts demand for SKUs where demand moves systematically ahead of an identifiable external trigger signal, enabling anticipatory forecasting by using leading indicators to predict demand before it materialises.

### 2. Detailed Description
- **Applicable scenarios:** Housing construction materials (leads permits), baby products (leads birth rate), school supplies (leads enrolment), B2B capital goods (leads equipment orders)
- **Boundaries:**

| Granularity | Detection | Lead Time |
|---|---|---|
| Daily | Max CCF at k < 0; |CCF| > 2/√n | k = 3–30 days ahead |
| Weekly | Max CCF at k < 0; |CCF| > 2/√n | k = 1–13 weeks ahead |
| Monthly | Max CCF at k < 0; |CCF| > 2/√n | k = 1–6 months ahead |
| Quarterly | Max CCF at k < 0; |CCF| > 2/√n | k = 1–4 quarters ahead |
| Yearly | Max CCF at k < 0; |CCF| > 2/√n | k = 1–2 years ahead |

- **Key demand characteristics:** Demand precedes observable external trigger; identifies future demand before conventional signals appear; requires leading indicator data pipeline

### 3. Business Impact
- **Primary risk (over-forecast):** Leading indicator signal false positive — demand anticipated but doesn't materialise
- **Primary risk (under-forecast):** Ignoring lead time — reactive rather than anticipatory; missing demand window
- **Strategic importance:** High — leading indicators extend effective forecast horizon; competitive advantage in early procurement

### 4. Priority Level
🟠 Tier 2 — High value when leading indicator data is available; requires external data pipeline investment.

### 5. Model Strategy

#### 5.1 Feature Engineering (Leading Indicator Features)
```
lead_indicator_lag_k(t) = trigger_signal(t + k)   [future value of leading indicator]
correlation_strength = CCF(optimal_k)
lead_time_estimate = k* = argmax |CCF(k)| for k < 0
```

| Granularity | Leading Indicators | Lead Time Features |
|---|---|---|
| Daily | Consumer confidence (daily), mobility index, news sentiment score | trigger(t+3 to t+30), CCF strength, lead time stability |
| Weekly | Consumer confidence (weekly), building permits, jobless claims | trigger(t+1 to t+13 weeks), CCF strength |
| Monthly | GDP leading index, PMI, industrial orders, building permits | trigger(t+1 to t+6 months), CCF strength |
| Quarterly | GDP growth, capital expenditure plans, business investment index | trigger(t+1 to t+4 quarters) |
| Yearly | Population growth, demographic index, macro investment cycle | trigger(t+1 to t+2 years) |

### 6. Model Families

#### 6.1 ML: LightGBM with leading indicator features
- Key features: Leading indicator values at optimal lag k*, CCF strength, lead time, baseline rolling mean, seasonal index

#### 6.2 DL: TFT — leading indicators as known future covariates (unique advantage)

| Granularity | Lookback | Leading Indicator Horizon | Output |
|---|---|---|---|
| Daily | 180 days | k* days ahead | P10, P50, P90 |
| Weekly | 52 weeks | k* weeks ahead | P10, P50, P90 |
| Monthly | 24 months | k* months ahead | P10, P50, P90 |
| Quarterly | 8 quarters | k* quarters ahead | P10, P50, P90 |
| Yearly | 5 years | k* years ahead | P10, P50, P90 |

#### 6.3 Statistical: ARIMAX with leading indicator as exogenous variable at lag k*
```
d(t) = α + β × trigger(t + k*) + Σγ × controls(t) + ARIMA residual
```

#### 6.4 Fallback: Standard behavior model without leading indicator

### 7. Ensemble

| Lead Indicator Confidence | LightGBM | TFT | ARIMAX |
|---|---|---|---|
| CCF < 0.40 (weak) | 30% | 10% | 60% |
| CCF 0.40–0.60 (moderate) | 50% | 25% | 25% |
| CCF > 0.60 (strong) | 55% | 35% | 10% |

### 8. Uncertainty Quantification
- [P10, P50, P90]; wider when leading indicator has high variance

### 9. Business Rules
- Lead indicator feed: Mandatory — flag if leading indicator data delayed
- Lead time drift: Alert if optimal k* shifts > 2 periods between estimations
- Manual overrides: Macroeconomist input on leading indicator forecast; lead time estimate adjustment

### 10. Evaluation

| Granularity | WMAPE Target | Lead Indicator R² | CCF Stability | Bias Alert |
|---|---|---|---|---|
| Daily | < 22% | > 0.25 | CV(k*) < 0.30 | \|Bias\| > 10% |
| Weekly | < 18% | > 0.25 | CV(k*) < 0.30 | \|Bias\| > 8% |
| Monthly | < 15% | > 0.20 | CV(k*) < 0.30 | \|Bias\| > 7% |
| Quarterly | < 12% | > 0.18 | CV(k*) < 0.30 | \|Bias\| > 6% |
| Yearly | < 10% | > 0.15 | CV(k*) < 0.30 | \|Bias\| > 5% |

### 11–13. Standard protocols + quarterly lead time recalibration; annual leading indicator relevance review

---
