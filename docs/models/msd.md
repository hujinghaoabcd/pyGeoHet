# Multiscale discretization (MSD)

## Purpose

MSD is a supervised bivariate discretization method. It searches cut points of a continuous explanatory variable `x` using the response `y`, with the GeoDetector q-statistic as the objective. The method is different from Stage 3A OPGD: OPGD selects among named univariate discretizers and requested class counts, while MSD directly searches ordered cut points for one fixed class count.

The implementation follows Meng et al. (2021), *Development of a multiscale discretization method for the geographical detector model*, DOI `10.1080/13658816.2021.1884686`.

## Objective

For ordered cut points that create `L` strata, MSD maximizes

\[
q = 1 - \frac{\sum_{h=1}^{L}\sum_{i\in h}(y_i-\bar y_h)^2}
{\sum_i(y_i-\bar y)^2}.
\]

For a fixed response sample, maximizing q is equivalent to minimizing within-stratum sum of squares. pyGeoHet computes interval costs from prefix sums and reuses them throughout the search.

## Search stages

1. Sort the joint complete-case sample by `x`.
2. Map `x` to a value grid defined by `origin` and `base_resolution`.
3. At `upscale`, search all combinations of `L-1` available coarse boundaries.
4. At every buffer scale, map an epsilon neighbourhood around each previously selected cut.
5. Select exactly one cut from every mapped neighbourhood, preserving order.
6. End at scale 1 and calculate the final q-statistic and significance result.

`upscale=1` performs an exact global search over all observed unique-value boundaries. For `upscale>1`, `buffer_scales` is mandatory, strictly decreasing, and must end at 1.

## Public API

```python
from pygeohet import MSD, multiscale_discretize

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

The functional interface is equivalent:

```python
result = multiscale_discretize(
    y,
    x,
    n_strata=5,
    upscale=6,
    buffer_scales=(3, 1),
)
```

## Parameters

- `n_strata`: fixed requested number of strata. Values 2-10 are accepted; the upper limit records the practical limitation stated in the paper.
- `upscale`: positive integer coarse value-grid scale. Use 1 for exact search.
- `buffer_scales`: refinement scales. Required for `upscale>1`; must decrease and end at 1.
- `epsilon`: nonnegative neighbourhood radius in the preceding scale's cut-code units.
- `base_resolution`: resolution of the original value grid. When omitted, the minimum positive spacing among unique `x` values is recorded and used.
- `origin`: grid origin. The minimum observed `x` is the default.
- `missing`: `drop` or `raise`. Dropping uses one joint complete-case sample and records the dropped count.
- `min_stratum_size`: minimum complete observations in every final or intermediate stratum.
- `q_tolerance`: numerical tolerance for equivalent objectives.

## Result contract

`MSDResult` contains:

- the final `StratificationResult`;
- the final `QStatisticResult`;
- one immutable `MSDScaleResult` for every search scale;
- candidate codes and candidate cut values;
- per-step selected codes and cut values;
- raw candidate-combination counts;
- per-step q and within-stratum sum of squares;
- the resolved value-grid origin and resolution;
- the deterministic tie rule.

A cut-point value belongs to the latter class. Missing rows are expanded back to their original positions as `None` labels.

## Tie rule

The primary objective is minimum within-stratum sum of squares, equivalently maximum q. Values within `q_tolerance` are tied. pyGeoHet then selects the lexicographically smallest cut-point tuple. The rule is stored in every final result and does not depend on hash or dictionary order.

## Validation

Current tests cover:

- equality with exhaustive enumeration on small problems;
- the exact-search special case;
- a paper-style 6 -> 3 -> 1 coarse-to-fine path;
- recovery of known synthetic thresholds;
- latter-class boundary membership;
- joint missing-data handling;
- deterministic ties;
- invalid class and scale contracts;
- auditable step tables.

External parity with the authors' Figshare archive and a published case remains pending, so MSD is currently **implemented, provisional** rather than fully externally validated.

## Method boundaries

MSD's scales are discretization value-grid scales, not alternative geographic observation supports. Stage 3B `SpatialScaleOPGD` compares prepared spatial supports. Later SPADE and IDSA introduce spatial dependence and spatial overlay concepts. These estimands remain separate.

## Reporting recommendations

A study using MSD should report the fixed class count, origin, base resolution, upscale, full buffer-scale sequence, epsilon, minimum stratum size, missing-data policy, final cut points, q and p-value, and whether exact or coarse-to-fine search was used.
