# pyGeoHet

**pyGeoHet** is a research-oriented Python toolkit for spatially stratified heterogeneity (SSH) analysis. It covers the classical Geographical Detector workflow and is being extended to discretization, spatial dependence, robustness, multivariate stratification, local explanation, categorical responses, and information-based SSH measures.

> **Status - Stage 3C implemented:** q-statistic, the four classical detectors, the integrated `GeoDetector` workflow, six continuous-variable stratification methods, audited q-guided candidate search, univariate `OPGD`, prepared-support spatial-scale OPGD selection, and supervised multiscale discretization (`MSD`) are available. Stage 4 will develop the robust detector family.

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

factors = pd.DataFrame(
    {
        "elevation": x,
        "precipitation": [100, 101, 102, 140, 141, 142, 200, 201, 202],
    }
)
result = OPGD(
    methods=["equal_interval", "quantile", "natural_breaks"],
    n_strata=[2, 3, 4],
).fit(y, factors)

print(result.optimal_frame())
print(result.detector.factor.to_frame())
```

Supported direct stratification methods are equal interval, quantile, weighted Fisher-Jenks natural breaks, geometric interval, standard deviation, and head/tail breaks. Every result retains cuts, requested and achieved strata, counts, missing rows, collapsed strata, rejected candidates, and the deterministic tie rule.

## Spatial-scale OPGD

Candidate spatial supports are prepared explicitly upstream. pyGeoHet compares their factor results and does not silently aggregate rasters, polygons, or points.

```python
from pygeohet import SpatialScaleOPGD, compare_spatial_scales

scale_effects = compare_spatial_scales(
    {
        10: result_10km,
        20: result_20km,
        40: result_40km,
    }
)
print(scale_effects.best_series())
print(scale_effects.factors_frame())

model = SpatialScaleOPGD(
    methods=["equal_interval", "quantile", "natural_breaks"],
    n_strata=[2, 3, 4],
)
scale_result = model.fit(
    {
        10: (y_10km, factors_10km),
        20: (y_20km, factors_20km),
        40: (y_40km, factors_40km),
    }
)
print(scale_result.scale_effects.best_series())
```

The default follows the 2020 OPGD paper: select the support with the highest 90% quantile of factor q values. `significant_only=True` exposes the legacy GD significance filter. The newer gdverse mean-plus-LOESS heuristic is documented as a distinct estimator and is not silently substituted.

## Multiscale discretization (MSD)

MSD searches ordered cut points of one continuous explanatory variable using the response and the q-statistic. Its “scale” is the resolution of the explanatory-variable value grid, not the geographic observation support used by `SpatialScaleOPGD`.

```python
import numpy as np
from pygeohet import MSD

x = np.arange(100, dtype=float)
y = np.select(
    [x < 18, x < 41, x < 64, x < 85],
    [0.0, 10.0, 20.0, 30.0],
    default=40.0,
)

result = MSD(
    n_strata=5,
    upscale=6,
    buffer_scales=(3, 1),
    epsilon=1,
    base_resolution=1.0,
).fit(y, x)

print(result.summary())
print(result.steps_frame())
print(result.stratification.to_series())
```

Use `upscale=1` for an exact global search over all observed unique-value boundaries. A coarse-to-fine run requires explicitly decreasing `buffer_scales` ending at 1. Each result retains candidate counts, selected cuts, q, within-stratum sum of squares, scale sequence, grid origin and resolution, missing-row count, and tie rule.

Individual interfaces are also public:

```python
from pygeohet import (
    MSD,
    q_statistic,
    stratify,
    evaluate_stratification,
    optimize_stratification,
    multiscale_discretize,
    compare_spatial_scales,
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
- spatial-scale comparison retains every support, score, factor eligibility decision, failure and tie convention;
- MSD uses one joint sample, an explicit value grid, one refined cut per mapped neighbourhood, and a deterministic cut-tuple tie rule;
- geographic support construction remains explicit upstream;
- external R, Python, QGIS, or spreadsheet implementations are never called at runtime;
- each method is checked through analytical properties, static references, simulations, and published cases;
- project status and next-conversation handoff documents are release gates.

## Validation

The NTD published-case record reproduces the factor q/p-values, all three interaction labels, and risk significance counts from `gdverse`/`GD`. Raw third-party data are not redistributed; a hash-checking validator is provided in `tools/validate_ntd_reference.py`.

Stages 3A and 3B have analytical, boundary, rejection-path and integrated-workflow tests. MSD additionally matches exhaustive enumeration on small problems and recovers known thresholds through a 6 -> 3 -> 1 coarse-to-fine search. Static author-code parity and a published MSD case remain required before Stage 3 methods are labelled fully externally validated.

See:

- [`docs/models/classic-detectors.md`](docs/models/classic-detectors.md)
- [`docs/models/stratification-opgd.md`](docs/models/stratification-opgd.md)
- [`docs/models/spatial-scale-opgd.md`](docs/models/spatial-scale-opgd.md)
- [`docs/models/msd.md`](docs/models/msd.md)
- [`docs/references/msd-code-audit.md`](docs/references/msd-code-audit.md)
- [`docs/validation/ntd-reference.md`](docs/validation/ntd-reference.md)
- [`VALIDATION_MATRIX.md`](VALIDATION_MATRIX.md)
- [`ROADMAP.md`](ROADMAP.md)
- [`HANDOFF_NEXT_CONVERSATION.md`](HANDOFF_NEXT_CONVERSATION.md)

## Licence

MIT. Scientific references, reviewed source projects, and implementation-independence rules are recorded in `THIRD_PARTY_NOTICES.md` and the model documentation.
