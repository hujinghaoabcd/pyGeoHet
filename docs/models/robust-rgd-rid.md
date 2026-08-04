# Robust discretization, RGD and RID

## Purpose

The robust detector family replaces ad hoc continuous-variable classification with an ordered variance change-point problem. For a response `y` and continuous explanatory variable `x`, observations are ordered by `x`, then divided into a fixed number of contiguous zones that minimize the response sum of squares within zones.

For robust zones `z = 1, ..., K`, the RGD B-value is

\[
B = 1 - \frac{SSW_R}{SST}
  = 1 - \frac{\sum_z \sum_{i \in z}(y_i-\bar y_z)^2}
                 {\sum_i(y_i-\bar y)^2}.
\]

This is numerically the classical q-statistic evaluated on the robust zones. The name B-value records that the zones came from the RGD optimization rather than from a generic discretization method.

## Exact robust discretization

```python
from pygeohet import robust_discretize

result = robust_discretize(
    y,
    x,
    n_strata=5,
    min_stratum_size=2,
)

print(result.b_value)
print(result.cut_points)
print(result.labels)
```

The implementation uses the following contract:

1. `y` and `x` are converted to one joint numeric sample.
2. Complete observations are stably ordered by ascending `x`.
3. Candidate changes are allowed only between distinct `x` values.
4. The cost of a segment is its response sum of squared deviations from its own mean.
5. Dynamic programming finds the exact minimum-cost ordered partition for the requested number of strata.
6. Objective ties within `b_tolerance` use the lexicographically smallest break-position tuple.
7. A cut value belongs to the latter class.
8. Labels are expanded back to the original row order and dropped rows are represented by `None`.

Restricting candidates to distinct-value boundaries is deliberate. Equal explanatory values represent the same rank location and are never split merely because their input row order differs.

## Class-count search

```python
from pygeohet import optimize_robust_discretization

search = optimize_robust_discretization(
    y,
    x,
    n_strata=range(3, 9),
    selection="marginal_gain",
    increase_rate=0.05,
)

print(search.best_series())
print(search.candidates_frame())
```

Two selection rules are available:

- `marginal_gain`: select the first accepted class count whose relative B-value increase over the previous accepted count is no greater than `increase_rate`; use the largest accepted count when no threshold crossing occurs.
- `max_b`: select the largest B-value; values within `b_tolerance` are tied and the smaller class count wins.

The full candidate table retains rejected class counts, B-values, p-values, cut points, absolute gains and relative gains. The numerical change-point solution is independent of the selection rule.

## RGD workflow

```python
from pygeohet import RGD

model = RGD(
    n_strata=range(3, 9),
    selection="marginal_gain",
    increase_rate=0.05,
)
result = model.fit(y, continuous_factors)

print(result.optimal_frame())
print(result.candidates_frame("temperature"))
print(result.detector.factor.to_frame())
```

Each continuous factor is optimized separately. The selected labels are then passed to the same tested classical `GeoDetector` workflow used elsewhere in the package. This gives factor, risk, interaction and ecological outputs without maintaining a second implementation of those statistics.

For every factor, the B-value stored in the robust optimization is expected to equal the q-value produced by the factor detector on the selected robust labels.

## RID workflow

```python
from pygeohet import RID

result = RID(
    n_strata=range(3, 7),
    selection="max_b",
).fit(y, continuous_factors)

print(result.interaction.to_frame())
```

RID first performs the same robust factor optimization as RGD and then applies collision-safe spatial intersection and the five-class interaction classification on one joint complete-case sample for every factor pair.

RID currently expects at least two continuous explanatory factors. Mixed continuous and already-categorical factors will be added only with an explicit sample-alignment and provenance contract.

## Robustness meaning

The rank-based formulation is invariant to strictly monotone transformations of the explanatory values. An extreme value of `x` changes its magnitude but not its order, so it does not create an artificial distance scale. Outlying response values are not discarded; the optimization places change points to minimize their contribution to within-zone dispersion.

“Robust” does not mean causal, outlier-proof, or free from model-selection optimism. B measures association under the optimized ordered stratification.

## Computational characteristics

For `M` admissible distinct-value boundaries and `K` strata, the exact dynamic program is quadratic in the number of candidate nodes for each segment count. Prefix sums make every interval cost constant-time. This is appropriate for transparent statistical analysis and exact validation; future acceleration may add pruning without changing the public estimand.

## Validation state

The implementation is checked against an independent brute-force enumeration on small problems and against invariance, duplicate-value, missing-data, integration and interaction tests. It is labelled implemented and provisional until a pinned author/reference fixture and a published RGD/RID case are reproduced.
