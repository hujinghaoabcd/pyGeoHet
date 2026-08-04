# Durable project decisions

## D001 - Package identity

The repository, distribution and import family use `pyGeoHet` / `pygeohet`. The scope is the SSH method family, not only classic GeoDetector variants.

## D002 - Direct sums of squares

q is calculated as `1 - SSW / SST` using direct centered sums of squares. No `ddof` choice appears in the public estimand.

## D003 - Small strata

Original factor strata default to `min_stratum_size=2`. They are never silently removed, merged, or imputed. Interaction overlays are different: intersections naturally create singleton cells, so `min_overlay_size=1` is the explicit default. These cells are retained and counted; users can require a larger minimum. Any later merge/drop policy must return an audit trail.

## D004 - Missing data and sample scope

The factor and risk detectors select complete cases separately for each factor. Interaction and ecological comparisons use one joint complete-case sample for both original factors and the overlay or F ratio. Every result reports dropped-row counts.

## D005 - q significance convention

The analytical q p-value follows the classical noncentral-F formulation. The noncentrality parameter and degrees of freedom are retained. Permutation inference will be a separate explicit method.

## D006 - No causal wording

q measures explanatory power or association under a supplied stratification. Package summaries do not describe a factor as causal without an external causal design.

## D007 - Result objects

Public statistical results are immutable and retain the information needed to audit variance decomposition, group sizes, pairwise tests, sample scope, and selected conventions.

## D008 - No empty public architecture

Modules and public names are introduced only with working code, tests and documentation. Planned models remain in the roadmap, not `__init__.py`.

## D009 - Runtime independence

pyGeoHet implements its own numerical route and has no runtime calls to R, gdverse, GD, QGIS or other GeoDetector packages.

## D010 - Handoff is a release gate

Every development batch updates `PROJECT_STATUS.md`, `VALIDATION_MATRIX.md`, `CHANGELOG.md`, and `HANDOFF_NEXT_CONVERSATION.md` before merge.

## D011 - Collision-safe overlays

Categorical overlays use tuples of original labels. String concatenation is prohibited because different category pairs can produce the same joined string.

## D012 - Interaction classification

The five classical interaction categories are mutually exclusive. Equality with `q(X1)+q(X2)` and boundary comparisons use explicit absolute and relative floating-point tolerances.

## D013 - Risk detector inference

Risk comparisons use two-sided unequal-variance Welch tests with sample variances (`ddof=1`) and Welch-Satterthwaite degrees of freedom. Zero-standard-error cases have deterministic limiting results instead of NaN propagation.

## D014 - Ecological detector inference

The primary ecological estimand is the paper's F ratio of residual within-stratum dispersion on a joint sample. `alternative="two-sided"` is the default because the stated null is equality and the scientific question is whether factor impacts differ. `alternative="greater"` is retained as an explicit compatibility mode for the upper-tail convention used by current gdverse output. The package never hides the convention used.

## D015 - Stratification is an auditable statistical operation

Continuous-variable stratification never returns labels alone. Every method records cuts, requested and achieved stratum counts, per-stratum counts, missing rows, duplicate cuts, collapsed strata, boundary conventions and rejection evidence. Equal values are not split by the quantile method. Geometric intervals reject nonpositive values rather than applying an undocumented shift.

## D016 - OPGD candidate scope and tie policy

All method-by-class-count candidates are evaluated on one joint complete-case sample for the response and the current explanatory variable. Rejected candidates remain in the result table. The optimizer maximizes q; q values within `q_tolerance` are tied, then fewer achieved strata, fewer requested strata, earlier user-supplied method order and earlier candidate are preferred. This rule is public and stored in the result.

## D017 - Stage 3 is delivered in controlled batches

Stage 3A contains univariate stratification and OPGD parameter search only. Spatial-scale optimization and multivariate stratification/MSD require separate numerical contracts and validation fixtures and are not implied by the `OPGD` name in version `0.0.3`.

## D018 - Spatial support is prepared explicitly upstream

Spatial-scale comparison does not silently resample rasters, aggregate polygons, rebuild neighbourhoods, or transform coordinates. Every candidate support is supplied as an already prepared dataset or factor-result table. The package compares supports but does not invent aggregation origins, alignment, summaries, nodata handling, zoning, kernels, or neighbourhood definitions.

## D019 - Spatial-scale estimators remain distinct

The Stage 3B primary convention follows the 2020 OPGD paper: calculate the 90% quantile of factor q values at each candidate support and select the maximum. `significant_only=True` is an explicit compatibility option for the legacy `GD::sesu()` eligibility filter. The newer gdverse mean-q plus LOESS stopping heuristic is a different estimator and is not silently substituted or claimed as reproduced.

## D020 - Comparable scales and deterministic selection

All successful candidate scales must contain the same factor set. Different observation counts are permitted because support aggregation changes sample size. A valid selection requires at least two accepted scales. Equal scores within `score_tolerance` use an explicit `first`, `smallest`, or `largest` tie policy, and failed scales remain in the public audit result.
