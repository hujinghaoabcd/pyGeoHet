# pyGeoHet

**pyGeoHet** is a research-oriented Python toolkit for spatially stratified heterogeneity (SSH) analysis. It covers the classical Geographical Detector workflow and extends it with auditable discretization, spatial-scale comparison, multiscale search and robust change-point detection.

> **Status - Stage 4 implemented:** q-statistic, the four classical detectors, integrated `GeoDetector`, six continuous-variable stratification methods, univariate `OPGD`, prepared-support spatial-scale OPGD, multiscale discretization (`MSD`), exact robust discretization, `RGD`, and `RID` are available. Stage 5 will develop spatial-dependence detectors such as SPADE and IDSA.

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

MSD searches ordered cut points of one continuous explanatory variable using the response and q. Its “scale” is the resolution of the explanatory-variable value grid, not geographic observation support.

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
```

Use `upscale=1` for an exact global search over all observed unique-value boundaries. Coarse-to-fine searches retain each scale's candidates, selected cuts, q, within-stratum sum of squares and failure evidence.

## Robust discretization, RGD and RID

Robust discretization orders the response by a continuous explanatory variable and finds contiguous variance change-point zones. For fixed zone count `K`, pyGeoHet minimizes total within-zone response SSE exactly by dynamic programming. The resulting B-value is

```text
B = 1 - robust within-zone SS / total SS
```

and is numerically equal to q evaluated on the robust labels.

```python
import numpy as np
import pandas as pd
from pygeohet import RGD, RID, robust_discretize

x = np.arange(24, dtype=float)
y = np.repeat([0.0, 4.0, 9.0, 13.0], 6)

fixed = robust_discretize(y, x, n_strata=4)
print(fixed.summary())
print(fixed.cut_points)
print(fixed.b_value)

factors = pd.DataFrame(
    {
        "trend": x,
        "cycle": np.tile(np.arange(6, dtype=float), 4),
    }
)

rgd_result = RGD(
    n_strata=range(2, 6),
    selection="marginal_gain",
    increase_rate=0.05,
).fit(y, factors)
print(rgd_result.optimal_frame())
print(rgd_result.candidates_frame("trend"))

rid_result = RID(
    n_strata=range(2, 5),
    selection="max_b",
).fit(y, factors)
print(rid_result.interaction.to_frame())
```

Important robust contracts:

- equal explanatory values are never split across zones;
- strictly monotone transformations of the explanatory values preserve the ordered problem;
- `marginal_gain` and `max_b` are explicit class-count policies;
- cut values belong to the latter zone;
- missing labels are expanded back to the original rows;
- RGD and RID reuse the tested classical detector and interaction implementations;
- `ruptures`, R and gdverse are reference evidence, not runtime dependencies.

The code follows the core published estimator but is independently organized and implemented. It is not a mechanical translation of author or gdverse source.

## Public interfaces

```python
from pygeohet import (
    GeoDetector,
    OPGD,
    SpatialScaleOPGD,
    MSD,
    RGD,
    RID,
    q_statistic,
    stratify,
    evaluate_stratification,
    optimize_stratification,
    multiscale_discretize,
    robust_discretize,
    optimize_robust_discretization,
    compare_spatial_scales,
    factor_detector,
    interaction_detector,
    risk_detector,
    ecological_detector,
    geodetector,
    opgd,
    rgd,
    rid,
)
```

## Statistical commitments

- q is computed from direct centered sums of squares;
- missing-row counts and sample scopes remain auditable;
- interaction components use one joint complete-case sample;
- overlays use tuple coding, not collision-prone string concatenation;
- risk comparisons use two-sided Welch tests;
- the ecological default is a factor-order-invariant two-sided F test, with an explicit `greater` compatibility mode;
- original factor strata default to a minimum size of two; natural singleton overlay cells remain explicit;
- stratification records cuts, achieved strata, boundary conventions, collapse and rejection evidence;
- OPGD retains a complete method-by-class candidate table and its tie rule;
- spatial-scale comparison retains every support, score, eligibility decision, failure and tie convention;
- MSD keeps geographic support scale separate from explanatory-value-grid scale;
- robust discretization uses a stable order, duplicate-value-safe boundaries, exact SSE optimization and deterministic break ties;
- model-complexity selection is explicit rather than hidden inside numerical kernels;
- external R, Python, QGIS or notebook implementations are never called at runtime;
- project status, validation records and next-conversation handoff are merge gates.

## Validation

The classical workflow reproduces the NTD factor q/p-values, interaction labels and risk-significance counts from GD/gdverse reference outputs.

Stages 3A-3C have analytical, boundary, rejection-path and integrated-workflow tests. MSD matches an independent exhaustive search on small problems. Stage 4 robust segmentation matches an independent brute-force oracle, preserves rank-equivalent solutions, prevents tied explanatory values from splitting, reconstructs missing rows and verifies that RGD B equals factor q.

Stages 3 and 4 remain **implemented, provisional** until pinned external fixtures and published-case reproductions are complete. Validation gaps are recorded rather than filled by assumed compatibility.

See:

- [`docs/models/classic-detectors.md`](docs/models/classic-detectors.md)
- [`docs/models/stratification-opgd.md`](docs/models/stratification-opgd.md)
- [`docs/models/spatial-scale-opgd.md`](docs/models/spatial-scale-opgd.md)
- [`docs/models/msd.md`](docs/models/msd.md)
- [`docs/models/robust-rgd-rid.md`](docs/models/robust-rgd-rid.md)
- [`docs/references/msd-code-audit.md`](docs/references/msd-code-audit.md)
- [`docs/references/robust-code-audit.md`](docs/references/robust-code-audit.md)
- [`docs/validation/ntd-reference.md`](docs/validation/ntd-reference.md)
- [`VALIDATION_MATRIX.md`](VALIDATION_MATRIX.md)
- [`ROADMAP.md`](ROADMAP.md)
- [`HANDOFF_NEXT_CONVERSATION.md`](HANDOFF_NEXT_CONVERSATION.md)

## Licence

MIT. Scientific references, reviewed source projects, implementation-independence rules and third-party licence boundaries are recorded in `THIRD_PARTY_NOTICES.md` and the model documentation.
