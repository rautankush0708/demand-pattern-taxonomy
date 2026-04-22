# Contributing to Demand Pattern Taxonomy

Thank you for your interest in improving the Demand Pattern Taxonomy! We welcome contributions from data scientists, demand planners, and supply chain experts.

## How to Contribute

### 1. Improvements to Documentation
If you find a typo, or have suggestions for clearer thresholds:
1. Fork the repository.
2. Edit the relevant `.md` file in `docs/dimensions/` or `docs/formula-reference/`.
3. Ensure formulas are correctly formatted for MathJax.
4. Submit a Pull Request.

### 2. Improvements to the Python Engine
If you want to implement a new formula or fix a bug in the code:
1. Fork the repository.
2. Install dependencies: `pip install -r requirements.txt`.
3. Make your changes in `src/demand_taxonomy/`.
4. Add or update tests in `tests/`.
5. Run tests: `pytest`.
6. Submit a Pull Request.

### 3. Proposing New Dimensions
If you have a proposal for a 13th dimension:
1. Open an Issue with the label `new-dimension`.
2. Provide the mathematical definition and the 5-granularity threshold table.
3. Once discussed, use the `docs/templates/segment-template.md` to create the specification.

## Code Style
- Use `numpy` for mathematical operations where possible.
- Follow PEP 8 guidelines for Python code.
- Ensure all docstrings explain the formula being implemented.

---

*Together, let's build the standard for demand intelligence.*
