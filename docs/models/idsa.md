# IDSA: interactive detector for spatial associations

## Scope

IDSA measures the spatial interaction of two or more explanatory variables after constructing response-informed fuzzy interaction zones. Stage 5B provides four connected layers:

- `fuzzy_overlay()` for collision-safe fuzzy AND/OR zones;
- `power_interactive_determinant()` for fixed discretized factors;
- `optimize_spatial_discretization()` for CPSD-guided continuous-factor discretization;
- `IDSA` / `idsa` for greedy or exhaustive factor-combination search.

IDSA is not the classical interaction detector and is not robust RID. Classical interaction uses Cartesian tuple intersections and q; RID uses robust change-point strata and the classical interaction detector. IDSA uses response-risk memberships, spatial variance and `PID = theta / phi`.

## Fuzzy risk memberships

For factor `X_i` and stratum `h`, calculate the response mean

\[
\bar y_{ih}=\frac{1}{N_{ih}}\sum_{j\in(i,h)}y_j.
\]

All factor-stratum means are normalized together:

\[
\mu_{ih}=\frac{\bar y_{ih}-\min_{r,s}\bar y_{rs}}
{\max_{r,s}\bar y_{rs}-\min_{r,s}\bar y_{rs}}.
\]

For observation `j`, fuzzy AND selects the factor-stratum identity with the minimum current membership. Fuzzy OR selects the maximum.

```python
from pygeohet import fuzzy_overlay

overlay = fuzzy_overlay(
    y,
    discrete_factors,
    operation="and",
    tie_policy="first",
)
print(overlay.labels_series())
print(overlay.risk_frame())
print(overlay.membership_frame())
```

Zone labels are tuples `(factor_name, original_stratum_label)`. String concatenation is never used, so names such as `("a_b", "c")` and `("a", "b_c")` cannot collide.

The default tie rule matches the reviewed reference behaviour: the first factor in supplied column order wins. `tie_policy="last"` is available explicitly. Ties within `membership_tolerance` are counted. If all factor-stratum response means are equal, min-max membership is undefined and the function raises an error.

## Fixed-strata PID

Given fuzzy zones `Z`, IDSA defines the spatial explanatory component

\[
\theta=1-\frac{\sum_kN_k\Gamma_{y,k}}{N\Gamma_y},
\]

which is the Stage 5A PSD of the response under the fuzzy zones.

The information-retention component is

\[
\phi=1-
\frac{\sum_i\sum_kN_k\Gamma_{x_i,k}}
     {\sum_iN\Gamma_{x_i}}.
\]

The power of interactive determinant is

\[
PID=\frac{\theta}{\phi}.
\]

```python
from pygeohet import power_interactive_determinant

result = power_interactive_determinant(
    y,
    discrete_factors,
    weights,
    operation="and",
    permutations=999,
    random_state=42,
)
print(result.summary())
print(result.information_frame())
print(result.overlay.zones_frame())
```

Fixed IDSA factors must represent ordered discretizations. pyGeoHet converts each finite numeric factor's sorted unique values to canonical codes `1,...,K`. This preserves the intended ordinal structure while making the statistic invariant to harmless shifts or positive rescaling of external class codes. Arbitrary unordered nominal labels are not silently assigned an order.

A zero `phi` makes PID undefined. Fuzzy zones must satisfy the explicit minimum-zone and internal spatial-weight contracts inherited from PSD; singleton or internally disconnected zones are not silently removed.

## Conditional permutation inference

When permutations are requested, pyGeoHet shuffles the response and recomputes:

1. factor-stratum response risks;
2. normalized memberships;
3. fuzzy zones;
4. `theta`, `phi` and PID.

This is more appropriate than holding response-derived zones fixed under the null. Invalid permuted overlays are counted separately, and the pseudo-p value uses the valid null samples:

\[
p=\frac{1+\#\{PID_b\ge PID_{obs}\}}{1+B_{valid}}.
\]

The test remains conditional on the supplied spatial weights and factor discretizations.

## CPSD-guided discretization

Continuous-factor IDSA first searches method-by-class-count candidates using CPSD:

```python
from pygeohet import optimize_spatial_discretization

search = optimize_spatial_discretization(
    y,
    x,
    weights,
    methods=("quantile", "natural_breaks", "equal_interval"),
    n_strata=range(3, 9),
)
print(search.best_series())
print(search.candidates_frame())
```

The current primary rule is transparent maximum CPSD. Values within `cpsd_tolerance` are tied, then fewer actual strata, fewer requested strata, earlier method order and earlier candidate are preferred. Rejected candidates remain in the table.

The maintained reference workflow may apply a LOESS-based stopping rule after CPSD calculation. pyGeoHet does not claim that compatibility estimator without a pinned external table. Maximum CPSD is an explicit independent choice, not an accidental approximation.

## Integrated IDSA

```python
from pygeohet import IDSA

result = IDSA(
    methods=("quantile", "natural_breaks", "equal_interval"),
    n_strata=range(3, 9),
    search="greedy",
    operation="and",
).fit(y, continuous_factors, weights)

print(result.discretizations_frame())
print(result.combinations_frame())
print(result.best.result.summary())
```

### Greedy search

The greedy route follows the paper's iterative structure:

1. rank individual factors by their optimized CPSD;
2. start with the strongest factor;
3. evaluate every possible second factor;
4. retain the pair with maximum valid PID;
5. add the remaining factor that maximizes PID;
6. stop when no addition exceeds the current PID within `pid_tolerance`.

All attempted additions, including failures, remain in the combination table.

### Exhaustive search

`search="exhaustive"` evaluates every subset of size two or greater. `max_combinations` prevents accidental exponential searches. PID ties choose fewer factors and then earlier supplied factor order.

Permutation inference in integrated IDSA is applied only to the final selected subset, not to every candidate during model search. The resulting p value therefore describes the selected fitted interaction conditional on the selection procedure; it is not a fully selection-adjusted inferential guarantee.

## Spatial and missing-data contracts

- `W` is a prepared finite nonnegative square matrix.
- No CRS, coordinate, centroid, distance, neighbour, kernel or normalization choice is inferred.
- One joint complete-case mask is used for the response and all factors in integrated IDSA.
- The same observations are removed from both axes of `W`.
- Diagonal weights are excluded by the Stage 5A spatial-variance core.
- Islands and fuzzy zones without positive internal weighted pairs are explicit failures.
- Missing labels are expanded back to original row positions as `None` in final outputs.

## Source relationship

The formulas and fuzzy-zone construction were checked against Song and Wu (2021), gdverse `idsa`/`pid_idsa`, and sdsfun `fuzzyoverlay`/`spvar`. pyGeoHet independently implements the sample contracts, canonical ordinal encoding, spatial components, immutable results, candidate search and permutation route. It does not translate GPL source line by line and does not call R at runtime.

## Validation

Stage 5B includes:

- hand-derived fuzzy AND and OR labels;
- global min-max membership values;
- explicit first/last tie behaviour;
- constant-risk and missing-data failures;
- direct `PID = theta / phi` component equality;
- invariance to shifted/rescaled ordinal codes;
- selection-aware recomputation of fuzzy zones under permutation;
- maximum-CPSD candidate tie tests;
- greedy and exhaustive integrated searches;
- joint missing-row reconstruction.

Full external validation still requires a pinned fuzzy-zone/PID table and a published multivariable IDSA reproduction.
