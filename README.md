# pyGeoHet

**pyGeoHet** is a research-oriented Python toolkit for spatially stratified heterogeneity (SSH) analysis. It covers the classical Geographical Detector workflow and is being extended to discretization, spatial dependence, robustness, multivariate stratification, local explanation, categorical responses, and information-based SSH measures.

> **Status - Stage 2 complete:** q-statistic, factor, interaction, risk, and ecological detectors, plus the integrated `GeoDetector` workflow, are implemented and validated. Stage 3 will add stratification and optimal discretization.

## Installation for development

```bash
python -m pip install -e ".[test]"
```

## Complete classical workflow

```python
import pandas as pd
from pygeohet import GeoDetector

frame = pd.DataFrame(
    {
        "y": [1.0, 1.2, 2.0, 2.2, 4.0, 4.2, 5.0, 5.2],
        "land_use": ["A", "A", "B", "B", "A", "A", "B", "B"],
        "region": ["north", "north", "north", "north", "south", "south", "south", "south"],
    }
)

result = GeoDetector().fit(frame["y"], frame[["land_use", "region"]])

print(result.factor.to_frame())
print(result.interaction.to_frame())
print(result.risk.comparisons_frame())
print(result.ecological.to_frame())
```

Individual interfaces are also public:

```python
from pygeohet import (
    q_statistic,
    factor_detector,
    interaction_detector,
    risk_detector,
    ecological_detector,
)
```

## Statistical commitments

- q is computed from direct centered sums of squares;
- missing-row counts and sample scopes remain auditable;
- interaction components use one joint complete-case sample;
- overlays use tuple coding, not collision-prone string concatenation;
- risk comparisons use two-sided Welch tests;
- the ecological default is a factor-order-invariant two-sided F test, with an explicit `greater` compatibility mode;
- singleton overlay cells are retained explicitly, while original factor strata default to a minimum size of two;
- external R, Python, QGIS, or spreadsheet implementations are never called at runtime;
- each method is checked through analytical properties, static references, simulations, and published cases;
- project status and next-conversation handoff documents are release gates.

## Validation

The NTD published-case record reproduces the factor q/p-values, all three interaction labels, and risk significance counts from `gdverse`/`GD`. Raw third-party data are not redistributed; a hash-checking validator is provided in `tools/validate_ntd_reference.py`.

See:

- [`docs/models/classic-detectors.md`](docs/models/classic-detectors.md)
- [`docs/validation/ntd-reference.md`](docs/validation/ntd-reference.md)
- [`VALIDATION_MATRIX.md`](VALIDATION_MATRIX.md)
- [`ROADMAP.md`](ROADMAP.md)
- [`HANDOFF_NEXT_CONVERSATION.md`](HANDOFF_NEXT_CONVERSATION.md)

## Licence

MIT. Scientific references, reviewed source projects, and implementation-independence rules are recorded in `THIRD_PARTY_NOTICES.md` and the model documentation.
