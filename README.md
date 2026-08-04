# pyGeoHet

**pyGeoHet** is a research-oriented Python toolkit for spatially stratified heterogeneity (SSH) analysis. It covers the classical Geographical Detector workflow and extends it with auditable discretization, spatial-scale comparison, multiscale search, robust change-point detection and spatial-variance decomposition.

> **Status - Stage 5B implemented:** q-statistic, the four classical detectors, integrated `GeoDetector`, six continuous-variable stratification methods, univariate `OPGD`, prepared-support spatial-scale OPGD, multiscale discretization (`MSD`), robust discretization, `RGD`, `RID`, spatial variance, PSD, CPSD, PSMD and `SPADE` are available. Fuzzy interaction zones and IDSA are now available; Stage 6 will address categorical and information-consistency SSH.

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
    {10: result_10km, 20: result_20km, 40: result_40km}
)
print(scale_effects.best_series())

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

Robust discretization orders the response by a continuous explanatory variable and finds contiguous variance change-point zones. For fixed zone count `K`, pyGeoHet minimizes total within-zone response SSE exactly by dynamic programming. Its B-value is numerically equal to q evaluated on the robust labels.

```python
import numpy as np
import pandas as pd
from pygeohet import RGD, RID, robust_discretize

x = np.arange(24, dtype=float)
y = np.repeat([0.0, 4.0, 9.0, 13.0], 6)
fixed = robust_discretize(y, x, n_strata=4)

factors = pd.DataFrame(
    {
        "trend": x,
        "cycle": np.tile(np.arange(6, dtype=float), 4),
    }
)
rgd_result = RGD(
    n_strata=range(2, 6),
    selection="marginal_gain",
).fit(y, factors)
rid_result = RID(n_strata=range(2, 5), selection="max_b").fit(y, factors)
```

Equal explanatory values are never split; strictly monotone transforms preserve the ordered problem; model-complexity selection is explicit; and no `ruptures`, R or gdverse runtime dependency is introduced.

## Spatial variance and SPADE

Stage 5A accepts an explicitly prepared nonnegative square spatial-weight matrix. It never silently chooses geometry representatives, CRS, distance units, neighbours, row standardization or symmetrization.

```python
import numpy as np
import pandas as pd
from pygeohet import (
    SPADE,
    IDSA,
    compensated_spatial_determinant,
    multilevel_spatial_determinant,
    fuzzy_overlay,
    power_interactive_determinant,
    optimize_spatial_discretization,
    power_spatial_determinant,
    spatial_variance,
)

coordinates = np.arange(12, dtype=float)
distance = np.abs(coordinates[:, None] - coordinates[None, :])
weights = np.zeros_like(distance)
mask = distance > 0
weights[mask] = 1.0 / distance[mask] ** 2

y = np.asarray([0, 0, 1, 1, 4, 4, 5, 5, 9, 9, 10, 10], dtype=float)
region = np.repeat(["west", "centre", "east"], 4)
trend = coordinates.copy()

print(spatial_variance(y, weights).summary())
print(power_spatial_determinant(y, region, weights).summary())

labels = np.repeat([1, 2, 3], 4)
print(compensated_spatial_determinant(y, trend, labels, weights).summary())

psmd = multilevel_spatial_determinant(
    y,
    trend,
    weights,
    n_strata=(2, 3, 4),
    method="quantile",
)
print(psmd.candidates_frame())

factors = pd.DataFrame({"trend": trend, "region": region})
spade_result = SPADE(n_strata=(2, 3, 4), method="quantile").fit(
    y,
    factors,
    weights,
    continuous_factors=("trend",),
)
print(spade_result.to_frame())
```

The implemented formulas are:

```text
Gamma = sum_ij w_ij (y_i - y_j)^2 / 2 / sum_ij w_ij
PSD   = 1 - sum_h N_h Gamma_h / (N Gamma)
CPSD  = PSD(response) / PSD(original continuous factor)
PSMD  = mean CPSD over accepted explicit class-count levels
```

Missing observations remove the matching row and column from the weight matrix. Diagonal mass, symmetry and islands are audited. PSD and PSMD may use seeded conditional permutation inference.

The NTD SPADE reference route produces `0.2566528294856155`, matching the gdverse test expectation `0.256653` at six decimals. The raw GPKG is not redistributed.


## Fuzzy interaction zones and IDSA

IDSA builds response-informed fuzzy zones rather than Cartesian intersections. Factor-stratum response means are normalized globally, fuzzy AND selects the minimum membership and fuzzy OR the maximum. Zone labels preserve `(factor, stratum)` identity.

```python
from pygeohet import IDSA, fuzzy_overlay, power_interactive_determinant

overlay = fuzzy_overlay(y, discrete_factors, operation="and")
pid = power_interactive_determinant(y, discrete_factors, weights)

result = IDSA(
    methods=("quantile", "natural_breaks", "equal_interval"),
    n_strata=range(3, 9),
    search="greedy",
).fit(y, continuous_factors, weights)

print(result.discretizations_frame())
print(result.combinations_frame())
print(result.best.result.summary())
```

`theta` is response PSD under fuzzy zones. `phi` measures the retained spatial information of all canonical ordinal factor codes. `PID = theta / phi`. Permutation inference rebuilds response-derived memberships and zones on every shuffle. Exhaustive subset search is available for small factor sets.


## Public interfaces

```python
from pygeohet import (
    GeoDetector,
    OPGD,
    SpatialScaleOPGD,
    MSD,
    RGD,
    RID,
    SPADE,
    q_statistic,
    spatial_variance,
    power_spatial_determinant,
    compensated_spatial_determinant,
    multilevel_spatial_determinant,
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
    spade,
    idsa,
)
```

## Statistical commitments

- q is computed from direct centered sums of squares;
- missing-row counts and sample scopes remain auditable;
- interaction components use one joint complete-case sample;
- categorical overlays use collision-safe labels;
- risk comparisons use two-sided Welch tests;
- ecological conventions are explicit;
- stratification, scale, MSD and robust searches retain candidate and tie evidence;
- spatial support scale, explanatory-value-grid scale and spatial-weight structure remain distinct;
- spatial weights are never silently constructed, normalized or symmetrized;
- PSD remains a spatial-variance estimand and is not called classical q under arbitrary weights;
- PSMD failures and accepted levels remain visible;
- model-complexity selection is explicit rather than hidden inside numerical kernels;
- external R, Python, QGIS, notebook and GIS implementations are never called at runtime;
- project status, validation records and handoff are merge gates.

## Validation

The classical workflow reproduces the NTD factor q/p-values, interaction labels and risk-significance counts. MSD matches an independent exhaustive search. Robust segmentation matches an independent brute-force oracle and verifies B=q on selected labels.

Stage 5A has hand-computed spatial-variance tests, weight-scaling and row/weight permutation invariance, common missing-sample alignment, explicit island failures, CPSD identity, PSMD candidate averaging, deterministic permutation tests and mixed-factor integration. Its categorical NTD PSD path is externally checked; continuous CPSD/PSMD published-case reproduction remains provisional.

See:

- [`docs/models/classic-detectors.md`](docs/models/classic-detectors.md)
- [`docs/models/stratification-opgd.md`](docs/models/stratification-opgd.md)
- [`docs/models/spatial-scale-opgd.md`](docs/models/spatial-scale-opgd.md)
- [`docs/models/msd.md`](docs/models/msd.md)
- [`docs/models/robust-rgd-rid.md`](docs/models/robust-rgd-rid.md)
- [`docs/models/spade.md`](docs/models/spade.md)
- [`docs/models/idsa.md`](docs/models/idsa.md)
- [`docs/references/idsa-code-audit.md`](docs/references/idsa-code-audit.md)
- [`docs/references/spade-idsa-code-audit.md`](docs/references/spade-idsa-code-audit.md)
- [`VALIDATION_MATRIX.md`](VALIDATION_MATRIX.md)
- [`ROADMAP.md`](ROADMAP.md)
- [`HANDOFF_NEXT_CONVERSATION.md`](HANDOFF_NEXT_CONVERSATION.md)

## Licence

MIT. Scientific references, reviewed source projects, implementation-independence rules and third-party licence boundaries are recorded in `THIRD_PARTY_NOTICES.md` and the model documentation.
