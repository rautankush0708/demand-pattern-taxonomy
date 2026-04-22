## RC3 · One Time
### 1. Definition
Predicts demand for SKUs with a single observed demand event and no recurrence expectation, where the primary decision is whether future demand will occur at all.

### 2. Detailed Description
- **Applicable scenarios:** Project-specific custom items, one-off procurement, trial orders, unique event-specific demand

### 5. Model Strategy

#### 5.1 Recurrence Probability Model
```
P(recurrence) = Logistic Regression on:
  - Category recurrence base rate
  - Customer tenure and order history
  - Time since first order
  - Product type (standard vs custom)
  - Market context signals

If P(recurrence) > 0.50 → Maintain in Cold Start lifecycle; monitor for second demand
If P(recurrence) < 0.20 → Flag for potential Inactive lifecycle
```

### 6. Model Families
- Not applicable for quantity forecast — single event only
- Recurrence classifier: Logistic Regression (simple; prevent overfit)
- Quantity estimate: First order quantity (only data point available)

### Evaluation
- Primary KPI: Recurrence detection within 2 periods of second demand event
- Secondary KPI: False positive rate (flagging non-recurring as recurring)

---
