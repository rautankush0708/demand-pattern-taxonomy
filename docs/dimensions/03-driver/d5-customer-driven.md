## D5 · Customer Driven

### 1. Definition
Predicts demand for SKUs where demand is highly concentrated among a small number of customers (HHI > 0.60), requiring customer-level forecasting and key account planning integration to avoid concentration risk mismanagement.

### 2. Detailed Description
- **Applicable scenarios:** B2B key account supply, single-customer dependency, distributor-led demand, strategic account categories
- **Boundaries:**

| Granularity | Detection Condition | Computation Window |
|---|---|---|
| Daily | HHI > 0.60 OR top-3 customers > 60% of demand | Rolling 90-day |
| Weekly | HHI > 0.60 OR top-3 customers > 60% of demand | Rolling 52-week |
| Monthly | HHI > 0.60 OR top-3 customers > 60% of demand | Rolling 12-month |
| Quarterly | HHI > 0.60 OR top-3 customers > 60% of demand | Rolling 4-quarter |
| Yearly | HHI > 0.60 OR top-3 customers > 60% of demand | Rolling 3-year |

- **Key demand characteristics:** Demand shaped by few large customers; ordering patterns reflect customer procurement cycles not end-consumer behaviour; single customer loss is catastrophic
- **Differentiation from other models:** Unlike other segments driven by market forces, demand here is shaped by individual customer decisions; customer forecast is more reliable than statistical model at this concentration level

### 3. Business Impact
- **Primary risk (over-forecast):** Customer churn leaves large inventory with no alternative demand
- **Primary risk (under-forecast):** Failure to service key account — contract penalty or relationship loss
- **Strategic importance:** Very high — key account revenue concentration means single forecast error has outsized P&L impact

### 4. Priority Level
🔴 Tier 1 — Key account demand is mission-critical; customer-level forecast is more valuable than statistical model.

### 5. Model Strategy Overview

#### 5.1 Customer-Level Decomposition
- Decompose total SKU demand into customer-level components
- Forecast each key account separately; sum to total
- Threshold: Model top customers individually if they represent > 10% of SKU demand each

#### 5.2 Analogue / Similarity Logic
- Analogues: Similar customers in same category (by order pattern, size, frequency)
- k = 3 analogues per key customer

#### 5.3 Feature Engineering

**Customer-Level Features:**
```
Customer share:         Customer_i demand / Total SKU demand (rolling window)
HHI:                   Σ(s_i)² across all customers
Customer order freq:   ADI computed at customer level
Customer order size:   CV² computed at customer level
Customer tenure:       Periods since first order
Customer contract:     Contract flag (contracted volume vs spot)
Churn risk score:      Based on order frequency change, complaints, contract expiry
```

| Granularity | Customer Features | Market Features |
|---|---|---|
| Daily | Customer daily order flag, days since last order, daily order size, contract flag | Category demand index, competitor availability |
| Weekly | Customer weekly order flag, weeks since last order, weekly order size, contract renewal week | Category trend |
| Monthly | Customer monthly order, months since last order, monthly volume, contract expiry flag | Market share index |
| Quarterly | Customer quarterly volume, HHI trend, contract status | Category quarterly index |
| Yearly | Customer annual volume, HHI, tenure, contract renewal | Annual market share |

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: LightGBM trained at customer × SKU level for key accounts; aggregate model for tail accounts
- Configuration: Objective = reg:absoluteerror; Metric = MAE per customer
- Key features: Customer order history features, contract status, churn risk, category demand index
- When to use: Primary model for key accounts with ≥ 6 months order history

#### 6.2 Deep Learning (DL)
- Architectures: DeepAR trained across customer portfolio for cross-customer learning

| Granularity | Lookback | Customer Features |
|---|---|---|
| Daily | 180 days | 10 per customer |
| Weekly | 52 weeks | 10 per customer |
| Monthly | 24 months | 8 per customer |
| Quarterly | 8 quarters | 6 per customer |
| Yearly | 5 years | 5 per customer |

#### 6.3 Statistical / Time Series Models
- Architectures: Croston (if customer orders are intermittent) or ETS (if regular)
- Apply at customer level; aggregate to SKU total

#### 6.4 Baseline / Fallback Model
- Fallback: Customer rolling mean order × expected order frequency
- Critical alert if key account (> 30% share) misses expected order

### 7. Ensemble & Weighting

| Customer Share | LightGBM | DeepAR | Statistical |
|---|---|---|---|
| > 30% (key account) | 70% | 20% | 10% |
| 10–30% (major account) | 50% | 30% | 20% |
| < 10% (tail) | 20% | 20% | 60% |

### 8. Uncertainty Quantification
- Method: Customer scenario analysis — customer orders vs does not order
- Output: [P10 (key customer churn), P50 (base), P90 (key customer volume spike)]
- Use case: Safety stock = P75; concentration risk report = P10 scenario

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Concentration risk flag: Alert if single customer > 40% of SKU demand
- Customer churn rule: If key customer misses 2+ consecutive expected orders → reforecast at P25
- Manual overrides: Account manager customer volume commitment input; contract signed/cancelled flag
- Alignment: Align with CRM pipeline and account plan

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | Total WMAPE Target | Key Account MAE | HHI Threshold Alert | Bias Alert |
|---|---|---|---|---|
| Daily | < 20% | < 15% of customer mean | HHI > 0.80 = critical alert | \|Bias\| > 10% |
| Weekly | < 18% | < 12% | HHI > 0.80 | \|Bias\| > 8% |
| Monthly | < 15% | < 10% | HHI > 0.80 | \|Bias\| > 7% |
| Quarterly | < 12% | < 8% | HHI > 0.80 | \|Bias\| > 6% |
| Yearly | < 10% | < 6% | HHI > 0.80 | \|Bias\| > 5% |

#### 10.2 Backtesting Protocol

| Granularity | Method | Train | Test |
|---|---|---|---|
| Daily | Rolling window per customer | 180 days | 30 days |
| Weekly | Rolling window per customer | 52 weeks | 13 weeks |
| Monthly | Rolling window per customer | 24 months | 6 months |
| Quarterly | Rolling window per customer | 8 quarters | 2 quarters |
| Yearly | Expanding window | All available | 1 year |

#### 10.3 Retraining & Data Freshness

| Granularity | Cadence | Latency |
|---|---|---|
| Daily | Daily | T+4 hours |
| Weekly | Weekly | T+1 day |
| Monthly | Monthly | T+2 days |
| Quarterly | Quarterly | T+3 days |
| Yearly | Annually | T+7 days |

### 11. Exception Handling & Overrides
- Automatic exception detection: HHI rises above 0.80 → critical concentration alert; key account misses 2 consecutive orders → reforecast trigger; new customer > 10% share detected → add to key account model
- Manual override: Account manager volume commitment; contract signed/cancelled flag
- Override expiration: Per order cycle

### 12. Reclassification / Model Selection
- Remove Customer Driven driver: HHI drops below 0.40 for 4 consecutive periods (demand diversified)
- Escalate: HHI > 0.80 → escalate to executive risk report

### 13. Review Cadence
- Performance monitoring: Weekly key account order tracking; monthly HHI trend
- Model review meeting: Monthly key account review with sales team
- Full model re-evaluation: Quarterly or on key account contract renewal/loss

---

