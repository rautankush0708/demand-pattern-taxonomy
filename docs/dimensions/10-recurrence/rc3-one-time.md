# Segment Model Template

## Dimension 10 · One Time

---

### 1. Definition
Predicts whether demand will recur for SKUs with a single observed demand event, where the primary decision is stocking vs not stocking rather than quantity forecasting, and the classifier determines if a second demand event is likely.

### 2. Detailed Description
- **Applicable scenarios:** Project-specific custom items, one-off procurement, trial orders, unique event-specific demand, first purchase from a new customer
- **Boundaries:**

| Granularity | Condition | Min History |
|---|---|---|
| Daily | Exactly 1 demand event in full history | Any |
| Weekly | Exactly 1 demand event | Any |
| Monthly | Exactly 1 demand event | Any |
| Quarterly | Exactly 1 demand event | Any |
| Yearly | Exactly 1 demand event | Any |

- **Key demand characteristics:** Single demand observation; no inter-arrival time to estimate; no pattern detectable; recurrence is uncertain
- **Differentiation from other models:** Unlike Irregular, no second event has occurred; unlike Cold Start (Lifecycle), demand has occurred at least once; the single event is the only data point available

### 3. Business Impact
- **Primary risk (over-forecast):** Stocking for recurrence that never comes — holding cost on custom or niche item
- **Primary risk (under-forecast):** Not stocking when customer returns — lost repeat sale and damaged relationship
- **Strategic importance:** Medium — individually low; collectively important for long-tail range decisions

### 4. Priority Level
🟡 **Tier 3** — Low individual priority; primary value is in making correct stock vs no-stock decision.

### 5. Model Strategy Overview

#### 5.1 Recurrence Probability Classifier (Primary Model)
```
P(recurrence) = Logistic Regression on:
  - Category recurrence base rate (% of one-time SKUs that recur in category)
  - Customer tenure and order history (loyal vs new customer)
  - Time since first order (recurrence more likely if recent)
  - Product type (standard vs custom)
  - Order quantity of first event (large first order → lower recurrence probability)
  - Market context signals

Decision rule:
  P(recurrence) > 0.60 → STOCK (maintain in Cold Start lifecycle; monitor for second demand)
  P(recurrence) 0.30–0.60 → REVIEW (planner decision required)
  P(recurrence) < 0.30 → DO NOT STOCK (flag for potential Inactive lifecycle)
```

#### 5.2 Analogue / Similarity Logic
- Analogues: Similar SKUs that had a single event — compare % that had a second event
- k = 10 most similar one-time SKUs (same category, customer type, product type)
- Recurrence base rate from analogues: n_recurred / n_total_analogues

#### 5.3 Feature Engineering

| Feature | Description | Expected Direction |
|---|---|---|
| Category recurrence rate | % of one-time SKUs in category that recur | + (higher rate → more likely) |
| Customer tenure (periods) | How long the customer has been ordering | + (longer tenure → more likely) |
| Periods since first order | Time elapsed since first demand event | − (longer time → less likely) |
| First order quantity | Size of first demand event | − (very large → less likely to repeat) |
| Product type flag | Standard (1) vs custom (0) | + (standard → more likely to recur) |
| Customer order frequency | Other SKUs ordered by same customer | + (frequent buyer → more likely) |
| Seasonal proximity | Is next period a seasonal peak for category | + (approaching peak → more likely) |

### 6. Model Families

#### 6.1 Machine Learning (ML)
- Architectures: Logistic Regression (primary — prevent overfit on sparse data)
- Configuration: Objective = binary:logistic; Metric = AUC, Precision/Recall
- Regularisation: L2 (λ = 1.0) — essential to prevent overfit with small sample
- When to use: Always — single demand event means only recurrence classification is possible

#### 6.2 Deep Learning (DL)
- Not applicable — insufficient data for deep learning at individual SKU level
- Portfolio-level DeepAR: Train across all one-time SKUs for cross-learning of recurrence patterns

#### 6.3 Statistical / Time Series Models
- Not applicable for quantity forecasting — single point only
- Poisson rate estimate: λ = 1 / periods_since_first_demand (very rough baseline)

#### 6.4 Baseline / Fallback Model
- Fallback: Category recurrence base rate as P(recurrence)
- Quantity fallback: First order quantity (only data point)
- Alert on any second demand observation — immediate reclassification trigger

### 7. Ensemble & Weighting

#### 7.1 Ensemble Scheme
- Single model: Logistic Regression recurrence classifier
- No quantity ensemble — first order quantity is the only estimate
- Weight: 100% Logistic Regression; no ensemble for one-time events

#### 7.2 Dynamic Weight Schedule
- Not applicable — single classifier; no switching

### 8. Uncertainty Quantification
- Method: P(recurrence) probability output from classifier — binary uncertainty
- Output: P(recurrence) ∈ [0, 1] — not [P10, P50, P90] (inappropriate for single event)
- Use case: Stock/no-stock binary decision; reorder point = 1 unit if P(recurrence) > 0.60

### 9. Business Rules & Post-Processing
- Non-negativity: max(0, forecast)
- Stock decision: If P(recurrence) > 0.60 → stock 1 unit; if < 0.30 → do not stock; if 0.30–0.60 → planner review
- Range rationalisation trigger: If P(recurrence) < 0.20 AND 12+ periods since first order → flag for delisting
- Manual overrides: Sales team customer repeat intent input; commercial decision to maintain range; buyer strategic decision

### 10. Evaluation & Monitoring

#### 10.1 Key Metrics

| Granularity | Recurrence Prediction AUC | Detection Speed | False Positive Rate | False Negative Rate |
|---|---|---|---|---|
| Daily | > 0.68 | Within 3 days of 2nd demand | < 15% | < 20% |
| Weekly | > 0.68 | Within 1 week of 2nd demand | < 15% | < 20% |
| Monthly | > 0.65 | Within 1 month of 2nd demand | < 15% | < 20% |
| Quarterly | > 0.65 | Within 1 quarter | < 15% | < 20% |
| Yearly | > 0.62 | Within 1 year | < 15% | < 20% |

#### 10.2 Backtesting Protocol
- Method: Hold-out validation on completed one-time SKUs (those that eventually had or did not have a second event)
- Train: All one-time SKUs resolved before T
- Test: One-time SKUs resolved after T
- Min sample: ≥ 50 resolved one-time SKUs for reliable AUC estimation

#### 10.3 Retraining & Data Freshness

| Granularity | Cadence | Latency |
|---|---|---|
| Daily | Monthly | T+4 hours |
| Weekly | Monthly | T+1 day |
| Monthly | Quarterly | T+2 days |
| Quarterly | Semi-annually | T+3 days |
| Yearly | Annually | T+7 days |

### 11. Exception Handling & Overrides
- Automatic exception detection: Second demand event observed → immediate reclassification to Irregular; P(recurrence) changes significantly (> 0.20) after model update → planner notification
- Manual override: Sales team confirms repeat order expected → force P(recurrence) = 0.85; customer confirms no repeat → force to Lifecycle: Inactive
- Override expiration: 6 months — reassess if no second demand

### 12. Reclassification / Model Selection

| Condition | Target | Trigger | Transition |
|---|---|---|---|
| Second demand event observed | Irregular (assess CV_IAT on 2 events) | Immediate | Hard switch |
| P(recurrence) < 0.20 for 12+ periods since first order | Lifecycle: Inactive candidate | 12 periods | Planner review required |
| Commercial decision to keep in range | Maintain One Time | Manual override | Stay |

### 13. Review Cadence
- Monthly one-time watchlist review; quarterly recurrence classifier recalibration; annual one-time portfolio assessment for range rationalisation

---

---
