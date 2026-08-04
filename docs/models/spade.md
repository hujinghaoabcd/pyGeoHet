# SPADE: spatial association detector

## Scope

SPADE extends geographical-detector variance decomposition by replacing ordinary variance with spatial variance. Stage 5A implements four connected statistics:

- spatial variance `Gamma`;
- power of spatial determinant `PSD`;
- compensated power of spatial determinant `CPSD`;
- power of spatial and multilevel discretization determinant `PSMD`;
- integrated `SPADE` workflows for categorical and continuous factors.

IDSA and fuzzy interaction zones are intentionally deferred to Stage 5B because they require a separate overlay and interaction estimand.

## Spatial variance

For values `y_i` and a prepared nonnegative spatial-weight matrix `W`,

\[
\Gamma(y;W)=
\frac{\sum_i\sum_{j\ne i}w_{ij}(y_i-y_j)^2/2}
     {\sum_i\sum_{j\ne i}w_{ij}}.
\]

```python
from pygeohet import spatial_variance

result = spatial_variance(y, weights)
print(result.value)
print(result.to_series())
```

The core accepts a prepared dense matrix and does not infer coordinates, CRS, neighbourhoods, bandwidths or row standardization. The diagonal is excluded. Directed matrices are accepted and reported. Nonnegative weights may be globally rescaled without changing the statistic.

Rows containing missing values are removed together with the same rows and columns of the weight matrix. Islands are rejected by default. `allow_islands=True` retains explicit zero-row observations when the remaining matrix still has positive total weight.

## PSD

For a categorical spatial stratification `h=1,...,L`,

\[
PSD = 1-
\frac{\sum_h N_h\Gamma_h}
     {N\Gamma}.
\]

```python
from pygeohet import power_spatial_determinant

result = power_spatial_determinant(
    y,
    strata,
    weights,
    permutations=999,
    random_state=42,
)
print(result.value)
print(result.strata_frame())
```

Each induced stratum uses the corresponding submatrix of `W`. pyGeoHet does not silently drop singleton strata or strata with no internal spatial links. `min_stratum_size` defaults to two, and invalid within-stratum weight structures raise explicit errors.

Permutation inference shuffles `y` while holding the spatial weights and supplied strata fixed. The pseudo-p value is `(1 + count(null >= observed)) / (B + 1)`.

## CPSD

CPSD compensates for information retained by one discretization of a continuous explanatory variable:

\[
CPSD(y,x,h,W)=
\frac{PSD(y,h,W)}{PSD(x,h,W)}.
\]

```python
from pygeohet import compensated_spatial_determinant

result = compensated_spatial_determinant(y, x, labels, weights)
print(result.response_psd.value)
print(result.information_psd.value)
print(result.value)
```

A zero or numerically negligible information PSD makes the ratio undefined and raises an error rather than returning infinity.

## PSMD

For explicit discretization levels `K`, PSMD is the mean accepted CPSD:

\[
PSMD = \frac{1}{|K^*|}\sum_{k\in K^*}CPSD_k.
\]

```python
from pygeohet import multilevel_spatial_determinant

result = multilevel_spatial_determinant(
    y,
    x,
    weights,
    n_strata=(3, 4, 5, 6),
    method="quantile",
)
print(result.value)
print(result.candidates_frame())
```

Every requested level remains in the candidate table. With `invalid="omit"`, failed levels are retained but omitted from the mean; `invalid="raise"` stops immediately. At least two levels must be accepted. `head_tail_breaks` is not allowed because it chooses its own number of classes and therefore cannot represent an explicit PSMD level sequence.

## Integrated SPADE

```python
from pygeohet import SPADE

result = SPADE(
    n_strata=range(3, 9),
    method="quantile",
).fit(
    y,
    factors,
    weights,
    continuous_factors=("elevation", "temperature"),
)
print(result.to_frame())
```

Categorical factors receive PSD. Continuous factors receive PSMD. When `continuous_factors` is omitted, all columns are treated as continuous, matching the dominant current reference workflow. Mixed inputs should therefore identify categorical columns explicitly by supplying the continuous subset.

## Numerical and software boundaries

- The package implements the published formulas independently.
- No R, gdverse, sdsfun, sf or spdep call occurs at runtime.
- Weight construction remains upstream and explicit.
- Sparse matrices and automatic geographic-neighbour construction are deferred.
- PSD is a spatial-variance decomposition and should not be described as identical to classical q for arbitrary finite samples and weights.
- The statistics measure spatially stratified association, not causality.

## Validation

Stage 5A includes hand-computed spatial variance, global weight-scale invariance, direct PSD decomposition, row-and-weight permutation invariance, missing-sample alignment, island failures, CPSD identity, PSMD candidate averaging and deterministic permutation tests.

The external NTD check uses the gdverse GPKG, polygon centroids, second-power inverse-distance weights and the `soiltype` stratification. pyGeoHet obtains `0.2566528295`, which matches the gdverse reference value `0.256653` at six decimal places. The raw GPKG is not redistributed.
