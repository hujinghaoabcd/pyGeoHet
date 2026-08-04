# Spatial-unit size effects and OPGD scale selection

## Scope

The 2020 OPGD paper separates parameter optimization into two operations:

1. optimize the discretization method and break number for every continuous explanatory variable;
2. compare factor-detector q values across candidate spatial units and select a spatial analysis scale.

pyGeoHet implements the second operation as an explicit comparison of **already prepared scale-specific datasets or factor-detector results**. The core package does not silently resample rasters, aggregate polygons, rebuild neighbourhoods, or change geographic support.

## Primary-paper selection rule

For each candidate spatial scale:

1. obtain the factor-detector q value of every explanatory variable after its scale-specific optimal discretization;
2. calculate the 90% quantile of those q values;
3. select the scale whose 90% quantile is highest.

The paper motivates this aggregate score by the expectation that a useful spatial scale produces high q values for most explanatory variables. Its vegetation example selects 40 km and its whole-area H1N1 example selects 100 km using the peak of the 90% quantile trend.

pyGeoHet exposes this rule as:

```python
compare_spatial_scales(
    results_by_scale,
    score_method="quantile",
    quantile=0.9,
    significant_only=False,
)
```

NumPy's linear quantile convention is used. It corresponds to the common R type-7 sample quantile convention used by `stats::quantile()`.

## Prepared-support boundary

A spatial scale is represented by a finite numeric value, such as grid width, aggregation distance, or another documented support size. Every scale-specific dataset must be prepared upstream.

This boundary is intentional:

- raster aggregation requires a chosen origin, alignment, resampling rule, nodata policy and summary statistic;
- polygon aggregation requires a zoning and attribute aggregation rule;
- point aggregation may require neighbourhood, tessellation or kernel choices;
- different studies use different meanings of “spatial unit size”.

Making these operations implicit would create a second, undocumented spatial model. pyGeoHet therefore compares supports but does not invent them.

## Comparing precomputed results

```python
from pygeohet import compare_spatial_scales

scale_effects = compare_spatial_scales(
    {
        5: factor_result_5km,
        10: factor_result_10km,
        20: factor_result_20km,
        40: factor_result_40km,
    }
)

print(scale_effects.best_series())
print(scale_effects.candidates_frame())
print(scale_effects.factors_frame())
```

Each value may be:

- `FactorDetectorResult`;
- `GeoDetectorResult`;
- `OPGDResult`;
- a DataFrame containing `factor`, `q`, and `p_value` columns.

All successful scales must contain the same factor set. Different numbers of spatial observations are allowed because aggregation changes sample size, but factor identity must remain comparable.

## Running OPGD at every scale

```python
from pygeohet import SpatialScaleOPGD

model = SpatialScaleOPGD(
    methods=["equal_interval", "quantile", "natural_breaks"],
    n_strata=range(3, 7),
)

result = model.fit(
    {
        10: (y_10km, factors_10km),
        20: (y_20km, factors_20km),
        40: (y_40km, factors_40km),
    }
)

print(result.scale_effects.best_series())
print(result.factors_frame())
print(result.best_opgd.detector.factor.to_frame())
```

Every mapping value is a `(response, continuous_factor_frame)` tuple. The scale-specific workflow uses the Stage 3A OPGD implementation, retains the complete discretization search for each successful scale, and records failures rather than silently dropping them.

At least two accepted scale candidates are required for a valid scale selection. When fewer than two survive, `selection_valid` is false and `best` is `None`.

## Significance filtering

The 2020 paper describes the 90% quantile of q values for all explanatory variables. The legacy `GD::sesu()` helper first replaces q values with missing values when their factor-detector p-value is at least 0.05 and then calculates the 90% quantile.

pyGeoHet keeps these conventions separate:

```python
# Primary-paper reading
compare_spatial_scales(results, significant_only=False)

# Legacy GD compatibility eligibility
compare_spatial_scales(
    results,
    significant_only=True,
    alpha=0.05,
)
```

When significance filtering is enabled, a factor is eligible when `p_value <= alpha`. A missing p-value is retained, matching the effective eligibility behaviour of the reference helpers. Excluded factors remain visible in the audit result.

## Newer gdverse divergence

The newer `gdverse::sesu_opgd()` implementation no longer follows the paper's direct 90% quantile maximum. It:

1. runs OPGD at each scale;
2. filters factor results by significance;
3. averages significant q values at each scale;
4. passes the mean trend to a LOESS-based stopping heuristic with a default 5% marginal increase threshold.

That is a distinct selection estimator. Stage 3B does not silently substitute it for the published 2020 rule. `score_method="mean"` is available for transparent descriptive comparison, but the gdverse LOESS stopping algorithm is not claimed as reproduced until a pinned numerical fixture and edge-case contract are added.

## Candidate result evidence

`SpatialScaleCandidateResult` stores:

- numeric spatial scale;
- input order;
- factor q and p-value mappings;
- eligible and excluded factor names;
- aggregate score;
- accepted/rejected state;
- rejection reason.

`SpatialScaleResult` stores every candidate, the selected candidate, scoring method, quantile, significance policy, alpha, tolerance, tie policy and whether the comparison is valid.

`SpatialScaleOPGDResult` additionally stores every successful scale-specific `OPGDResult` and all scale-level failures.

## Deterministic ties

The paper does not specify what to do when aggregate scale scores are equal within numerical tolerance. pyGeoHet exposes the policy rather than hiding it:

- `tie_break="first"` - prefer the earlier supplied candidate; default;
- `tie_break="smallest"` - prefer the numerically smallest spatial unit;
- `tie_break="largest"` - prefer the numerically largest spatial unit.

Scores within `score_tolerance` are treated as tied.

## Interpretation limits

Spatial scale selection is conditional on:

- the supplied candidate supports;
- upstream aggregation/resampling choices;
- the explanatory-variable set;
- scale-specific discretization searches;
- the aggregate score and significance policy.

A selected scale is therefore an analysis-support recommendation within the candidate set, not a universal geographic constant. Searching many supports and discretizations can increase selection optimism. Full candidate evidence should be reported, and external or resampling-based stability analysis is recommended.

## Sources and implementation conventions

Primary method source:

- Song, Y., Wang, J., Ge, Y., and Xu, C. (2020). *An optimal parameters-based geographical detector model enhances geographic characteristics of explanatory variables for spatial heterogeneity analysis: cases with different types of spatial data*. GIScience & Remote Sensing, 57(5), 593-610. DOI: 10.1080/15481603.2020.1760434.

Reference-code conventions were audited from pinned revisions of:

- `ausgis/GD`, function `sesu`;
- `stscl/gdverse`, function `sesu_opgd`;
- `stscl/sdsfun`, function `loess_optnum`.

These projects are development references only and are not runtime dependencies.
