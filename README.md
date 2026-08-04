# pyGeoHet

**pyGeoHet** is a research-oriented Python toolkit for spatially stratified heterogeneity (SSH) analysis. It covers the classical Geographical Detector workflow and is being extended to discretization, spatial dependence, robustness, multivariate stratification, local explanation, categorical responses, and information-based SSH measures.

> **Status - Stage 3A implemented:** q-statistic, the four classical detectors, the integrated `GeoDetector` workflow, six continuous-variable stratification methods, audited q-guided candidate search, and univariate `OPGD` are available. Spatial-scale OPGD and MSD remain later Stage 3 batches.

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

## Continuous variables and OPGD

```python
import pandas as pd
from pygeohet import OPGD, optimize_stratification

y = [1.0, 1.1, 1.2, 5.0, 5.1, 5.2, 10.0, 10.1, 10.2]
x = [10.0, 11.0, 12.0, 40.0, 41.0, 42.0, 80.0, 81.0, 82.0]

search = optimize_stratification(
    y,
    x,
    methods=["equal_interval", "quantile", "natural_breaks"],
    n_strata=[2, 3, 4],
)
print(search.best_series())
print(search.candidates_frame())

factors = pd.DataFrame({"elevation": x, "precipitation": [100, 101, 102, 140, 141, 142, 200, 201, 202]})
result = OPGD(
    methods=["equal_interval", "quantile", "natural_breaks"],
    n_strata=[2, 3, 4],
).fit(y, factors)

print(result.optimal_frame())
print(result.detector.factor.to_frame())
```

Supported direct stratification methods are equal interval, quantile, weighted Fisher-Jenks natural breaks, geometric interval, standard deviation, and head/tail breaks. Every result retains cuts, requested and achieved strata, counts, missing rows, collapsed strata, rejected candidates, and the deterministic tie rule.

Individual interfaces are also public:

```python
from pygeohet import (
    q_statistic,
    stratify,
    evaluate_stratification,
    optimize_stratification,
    factor_detector,
    interaction_detector,
    risk_detector,
    ecological_detector,
    geodetector,
    opgd,
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
- stratification records cuts, achieved strata, boundary conventions, collapse and rejection evidence;
- OPGD evaluates a complete method-by-class candidate table on one joint sample and exposes its tie rule;
- external R, Python, QGIS, or spreadsheet implementations are never called at runtime;
- each method is checked through analytical properties, static references, simulations, and published cases;
- project status and next-conversation handoff documents are release gates.

## Validation

The NTD published-case record reproduces the factor q/p-values, all three interaction labels, and risk significance counts from `gdverse`/`GD`. Raw third-party data are not redistributed; a hash-checking validator is provided in `tools/validate_ntd_reference.py`.

Stage 3A currently has analytical, boundary, rejection-path and integrated workflow tests. Static cross-language stratification fixtures and a published OPGD reproduction remain required before the new methods are labelled fully externally validated.

See:

- [`docs/models/classic-detectors.md`](docs/models/classic-detectors.md)
- [`docs/models/stratification-opgd.md`](docs/models/stratification-opgd.md)
- [`docs/validation/ntd-reference.md`](docs/validation/ntd-reference.md)
- [`VALIDATION_MATRIX.md`](VALIDATION_MATRIX.md)
- [`ROADMAP.md`](ROADMAP.md)
- [`HANDOFF_NEXT_CONVERSATION.md`](HANDOFF_NEXT_CONVERSATION.md)

## Licence

MIT. Scientific references, reviewed source projects, and implementation-independence rules are recorded in `THIRD_PARTY_NOTICES.md` and the model documentation.
