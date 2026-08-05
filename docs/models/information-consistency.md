# Information-consistency SSH

Stage 6B adds two separate estimators for measuring spatially stratified heterogeneity through distributional consistency rather than variance decomposition.

- `IN-SSH` is defined for a nominal target and categorical strata.
- `IC-SSH` is defined for a continuous target and categorical strata.

They are not aliases for classical q, SRS-GD, PSD, PID or a regression coefficient.

## Public interfaces

```python
from pygeohet import (
    InformationConsistency,
    continuous_information_consistency,
    information_consistency,
    nominal_information_consistency,
)
```

The scalar functions evaluate one supplied stratification. `InformationConsistency.fit()` and `information_consistency()` evaluate several factor columns on one joint complete-case sample.

## Nominal information consistency

For nominal target `Y` and strata `S`, pyGeoHet computes

\[
IN(Y,S)=\frac{I(Y;S)}{H(Y)}
       =1-\frac{H(Y\mid S)}{H(Y)}.
\]

All entropy components use the natural logarithm consistently. The logarithm base cancels in the normalized ratio, but the intermediate values remain auditable and are not calculated with mixed bases.

`IN` lies in `[0,1]`:

- `IN = 0` when the target distribution is the same in every stratum;
- `IN = 1` when the strata determine the target categories perfectly;
- a constant target has `H(Y)=0`, so the estimand is undefined and raises `InvalidDataError`.

```python
from pygeohet import nominal_information_consistency

result = nominal_information_consistency(
    target=["low", "low", "high", "high"],
    strata=["west", "west", "east", "east"],
    permutations=999,
    random_state=42,
)

print(result.summary())
print(result.contingency_frame())
```

The immutable result retains target and stratum probabilities, observed joint cells, target entropy, conditional entropy, mutual information, sample indices, dropped rows and permutation evidence.

## Continuous information consistency

Let `P_h` be the empirical target histogram in stratum `h`, `P` the global target histogram and `p_h` the sample share of the stratum. pyGeoHet computes

\[
IC(Y,S)=\sum_h p_h
\frac{\arctan\{D_{KL}(P_h\Vert P)\}}{\pi/2}.
\]

The arctangent transforms each nonnegative KL divergence to `[0,1)`. The weighted sum is returned in `[0,1]` up to floating-point tolerance.

Every global and stratum histogram uses the same target support and the same bin edges. The edges are resolved once from the complete target and then held fixed for the observed statistic and every response permutation. This prevents incomparable stratum-specific supports.

```python
from pygeohet import continuous_information_consistency

result = continuous_information_consistency(
    target=[0.0, 0.2, 0.8, 1.0, 5.0, 5.2, 5.8, 6.0],
    strata=["west"] * 4 + ["east"] * 4,
    bins="sturges",
    permutations=999,
    random_state=42,
)

print(result.summary())
print(result.contributions_frame())
print(result.histogram_frame())
```

Supported automatic bin methods are:

- `sturges`;
- `square_root` or `sqrt`;
- `rice`;
- `scott`;
- `freedman_diaconis` or `fd`.

An integer supplies an explicit equal-width bin count. A strictly increasing edge sequence supplies the complete support directly. At least two bins are required.

For KL evaluation, bins with zero stratum probability contribute zero. A positive stratum probability cannot coincide with zero global probability because the global histogram is formed from the same complete sample and edges; this invariant is checked explicitly.

## Multi-factor workflow

```python
import pandas as pd
from pygeohet import InformationConsistency

factors = pd.DataFrame(
    {
        "land_use": ["a", "a", "b", "b", "a", "a", "b", "b"],
        "region": ["north"] * 4 + ["south"] * 4,
    }
)

nominal = InformationConsistency(
    target_kind="nominal",
    permutations=999,
    random_state=42,
).fit(nominal_target, factors)

continuous = InformationConsistency(
    target_kind="continuous",
    bins="sturges",
    permutations=999,
    random_state=42,
).fit(continuous_target, factors)

print(nominal.to_frame())
print(continuous.to_frame())
```

All factor columns are evaluated on one joint complete-case sample. This makes factor values directly comparable and prevents each factor from obtaining a different missing-data scope.

## Missing data and strata

- `missing="drop"` removes every row missing in the target or any supplied factor.
- `missing="raise"` rejects the input instead.
- `min_stratum_size=2` is the default for both estimators.
- strata smaller than the minimum raise `SmallStratumError`; they are not silently merged or removed.
- the retained original row indices and dropped-row count are stored in each result.

## Permutation inference

The null procedure shuffles the target relative to fixed supplied strata. For continuous targets, the observed global support and bin edges remain fixed during permutation. The pseudo-p value is

\[
p=\frac{1+\#\{T_b\ge T_{obs}\}}{B+1}.
\]

This correction prevents a zero p value. `random_state` makes the null sequence reproducible. The null mean and sample standard deviation are retained.

Permutation inference is conditional on the supplied stratification and, for IC-SSH, the selected edge sequence. It is not adjusted for upstream factor selection, discretization search or histogram-method search.

## Numerical contracts

- category labels must be hashable;
- nominal targets must contain at least two categories;
- continuous targets must be finite, numeric and nonconstant;
- entropy uses one logarithm base throughout;
- all histograms share one support and edge sequence;
- explicit edges must cover the complete target range;
- zero-probability KL terms are omitted rather than smoothed;
- no R, C++ reference package or competing Python implementation is called at runtime;
- immutable outputs retain complete decomposition and sample evidence.

## Validation

Analytical tests cover:

- perfect nominal consistency (`IN=1`);
- nominal independence (`IN=0`);
- a hand-calculated partial contingency table;
- category relabeling invariance;
- constant-target failure;
- separated continuous strata with `KL=log(2)`;
- identical stratum distributions (`IC=0`);
- affine target invariance under automatic equal-width edges;
- deterministic Sturges, square-root, Rice, Scott and Freedman-Diaconis edges;
- fixed-edge seeded permutations and corrected p-value bounds;
- joint missing-data scope across multiple factors;
- invalid support and minimum-stratum failures.

The maintained `stscl/sshicm` source is used as implementation evidence and a future static comparison target. pyGeoHet deliberately does not reproduce its mixed logarithm bases, uncorrected permutation p values or independently constructed stratum histogram supports.

## References

Bai, H., Wang, H., Li, D., and Ge, Y. (2023). Information Consistency-Based Measures for Spatial Stratified Heterogeneity. *Annals of the American Association of Geographers*, 113(10), 2512-2524.

The detailed source audit and known convention differences are recorded in `docs/references/stage6-information-ssh-audit.md`.
