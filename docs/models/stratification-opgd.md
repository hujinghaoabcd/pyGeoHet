# Continuous-variable stratification and OPGD

## Purpose

Classic GeoDetector requires categorical strata. Continuous explanatory variables therefore need an explicit stratification step before q is evaluated. pyGeoHet treats that step as a statistical operation that must be reproducible and auditable rather than as an invisible preprocessing detail.

Stage 3A provides:

- six deterministic univariate stratification methods;
- immutable records of cut points, achieved strata and rejected candidates;
- q-guided method-by-class-count optimization;
- an integrated optimal parameters-based geographical detector (`OPGD`).

Spatial-scale optimization and multivariate stratification are not part of this batch.

## Public API

```python
from pygeohet import OPGD, optimize_stratification, stratify
```

### One stratification

```python
result = stratify(
    values,
    method="natural_breaks",
    n_strata=5,
    min_stratum_size=2,
)

print(result.summary())
print(result.cut_points)
print(result.counts)
```

The returned `StratificationResult` retains:

- canonical method name;
- labels aligned to the original rows;
- cut points;
- requested and achieved stratum counts;
- per-stratum sample counts;
- dropped-row count;
- duplicate cut-point count;
- collapsed-stratum count;
- rejection status and reason;
- method-specific metadata and boundary convention.

## Supported methods

### Equal interval

The observed range is divided into equal-width intervals. An observation exactly equal to an internal cut remains in the lower stratum.

### Quantile

Candidate cuts use NumPy's `lower` quantile convention. Equal values are never split across strata. Duplicate cut points are collapsed and recorded, so the achieved number of strata may be smaller than requested.

### Natural breaks

Natural breaks use a weighted Fisher-Jenks dynamic program over distinct values and their frequencies. Cut points are midpoints between adjacent distinct values. Ties in the dynamic program are resolved deterministically.

### Geometric interval

Geometric intervals require strictly positive values. An observation exactly equal to a geometric cut enters the upper stratum. Nonpositive candidates are rejected with an explicit reason rather than shifted silently.

### Standard deviation

Cuts are centered on the sample mean and use the sample standard deviation (`ddof=1`). Exact cut points remain in the lower stratum.

### Head/tail breaks

Head/tail breaks recursively split the current head at its arithmetic mean while the head proportion remains at or below the configured threshold. The default threshold is `0.4`. This method determines its own number of strata, so `n_strata=None` is valid.

## Missing data and sample scope

`stratify()` accepts `missing="drop"` or `missing="raise"`. With `drop`, missing labels remain `None` at their original row positions.

`optimize_stratification(y, x, ...)` first selects the joint complete cases of `y` and `x`. Every candidate is generated and evaluated on that same sample. The selected labels are then expanded back to the original row order, with dropped rows represented as `None`.

## Candidate optimization

```python
search = optimize_stratification(
    y,
    x,
    methods=[
        "standard_deviation",
        "equal_interval",
        "geometric_interval",
        "quantile",
        "natural_breaks",
    ],
    n_strata=range(3, 9),
)

print(search.best_series())
print(search.candidates_frame())
```

The candidate table retains successful and rejected candidates. It includes method, requested and achieved strata, minimum stratum size, cuts, q, p-value, sums of squares and rejection reason.

By default, a candidate is rejected when:

- it produces fewer than two nonempty strata;
- any stratum is smaller than `min_stratum_size`;
- the achieved number of strata differs from the requested number;
- the method's domain restriction is violated;
- q cannot be evaluated under the shared numerical contract.

Set `require_requested_strata=False` to allow collapsed candidates to compete.

## Deterministic tie policy

The optimizer maximizes q. Values within `q_tolerance` of the maximum are treated as tied. Ties are resolved by preferring:

1. fewer achieved strata;
2. fewer requested strata;
3. the earlier method in the user-supplied method order;
4. the earlier candidate.

The exact rule is stored in `OptimalStratificationResult.tie_rule`.

## Integrated OPGD

```python
model = OPGD(
    methods=["equal_interval", "quantile", "natural_breaks"],
    n_strata=range(3, 7),
)
result = model.fit(y, continuous_factors)

print(result.optimal_frame())
print(result.candidates_frame())
print(result.detector.factor.to_frame())
```

`OPGD` optimizes each continuous factor independently and then passes the selected labels to the existing classic `GeoDetector` workflow. `OPGDResult` therefore contains:

- one complete optimization object per factor;
- the selected discrete labels aligned to the original rows;
- the full factor, interaction, risk and ecological detector result.

The implementation has no runtime dependency on R, GD, gdverse or GIS software.

## Interpretation limits

A high q indicates strong explanatory power under the selected stratification. Searching many candidate stratifications is a model-selection operation and can increase optimism. The candidate table is retained so users can report the search space, inspect instability and perform external or resampling-based validation. The result does not establish causality.
