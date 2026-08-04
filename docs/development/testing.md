# Testing and validation

Run the Stage 1 checks with:

```bash
python -m pip install -e ".[test]"
pytest --cov=pygeohet --cov-report=term-missing
python examples/01_factor_detector.py
```

Unit tests are necessary but not sufficient. Promotion of a model to stable also requires the four-layer evidence in `VALIDATION_MATRIX.md`: analytical/properties, static cross-language fixtures, simulations, and a published-case reproduction.

Reference fixtures must be generated independently. Do not import or execute a reference package inside the pytest process.
