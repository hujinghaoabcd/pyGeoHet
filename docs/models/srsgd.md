# SRS-GD: spatial rough set geographical detectors

## Problem and scope

SRS-GD analyzes **nominal target variables** using local rough-set approximation. It answers three questions:

1. how strongly each conditional feature explains the target on average across local regions;
2. whether one feature has significantly greater local explanatory power than another;
3. how much explanatory power and spatial-homogeneity change when another feature is added.

SRS-GD is not a drop-in replacement for variance-based q. Classical q is designed around a continuous response and between/within-stratum variance. SRS-GD instead evaluates whether local equivalence classes formed by discrete features contain only one target category.

## Inputs

- `target`: nominal or deliberately discretized decision labels;
- `factors`: one or more nominal or discretized conditional features;
- `adjacency`: a prepared binary `N x N` adjacency matrix.

The numerical core does not derive adjacency from geometry. CRS, distance thresholds, polygon contiguity and neighbour construction remain explicit upstream choices.

## Local region

For focal object `x`, the paper defines

\[
C(x)=\{y:M_{xy}=1\}\cup\{x\}.
\]

pyGeoHet therefore clears diagonal values in the supplied matrix and adds the focal object exactly once. A matrix with diagonal ones and the same matrix with diagonal zeros produce identical results.

Symmetric adjacency is required by default. Directed neighbourhoods can be evaluated only after explicitly setting `require_symmetric=False`.

## Local indiscernibility and positive region

For a feature set `A'`, two objects in `C(x)` are locally indiscernible when they have equal values for **every** feature in `A'`. pyGeoHet represents multifeature values as collision-safe tuples.

An equivalence class belongs to the local positive region when all objects in that class have the same target category. The local approximation quality is

\[
\gamma(x;A',d)=\frac{|POS^x_{A'}(d)|}{|C(x)|}.
\]

The returned local table records the region size, positive-region size and local quality for every original row.

## Average local explanatory power

\[
D(A',d)=\frac{1}{N}\sum_x\gamma(x;A',d).
\]

`D` lies in `[0,1]`. A larger value means that the feature set more consistently determines the nominal target within local regions.

```python
from pygeohet import spatial_rough_set_measure

result = spatial_rough_set_measure(
    target,
    factors[["land_use"]],
    adjacency,
)
print(result.summary())
print(result.local_frame())
```

## Spatial entropy of local explanatory power

Let

\[
p_x=\frac{\gamma(x;A',d)}{\sum_z\gamma(z;A',d)}.
\]

Then

\[
SE(A',d)=-\sum_xp_x\log_2p_x.
\]

A larger `SE` means local explanatory power is distributed more evenly and spatial heterogeneity is lower. `normalized_spatial_entropy` divides `SE` by `log2(N)`.

If every local quality is zero, `D=0` and `SE` is returned as `None`, because the normalization denominator is zero.

## Factor detector: SRSF

```python
from pygeohet import srs_factor_detector

factor = srs_factor_detector(target, factors, adjacency)
print(factor.to_frame())
print(factor["land_use"].local_frame())
```

All factors use one joint complete-case sample, which makes their `D` and local-quality vectors directly comparable.

A one-sample Student test assesses whether the sampled local qualities have a mean greater than zero. The default uses every complete focal object. Paper-style random subsampling is available through `sample_size` and `random_state`.

## Ecological detector: SRSE

```python
from pygeohet import srs_ecological_detector

ecological = srs_ecological_detector(
    target,
    factors,
    adjacency,
    alpha=0.05,
)
print(ecological.to_frame())
```

The paper compares local-quality samples from two feature sets. pyGeoHet uses a paired two-sided Student test because both qualities are evaluated at the same focal objects. A significant positive difference means the first feature is more explanatory; a significant negative difference means the second is more explanatory.

This differs from the reviewed gdverse wrapper, which applies an unpaired Welch test. A compatibility estimator can be added later if a pinned external table requires it.

## Interaction detector: SRSI

```python
from pygeohet import srs_interaction_detector

interaction = srs_interaction_detector(
    target,
    factors,
    adjacency,
    baseline="land_use",
)
print(interaction.to_frame())
```

For baseline feature set `A1` and added set `A2`, SRSI reports

\[
D(A_1\cup A_2,d)-D(A_1,d).
\]

Exact tuple refinement guarantees that the local and average gain cannot be negative, apart from numerical tolerance. A one-sided paired Student test evaluates whether the local gain is greater than zero.

`entropy_change` is `SE_joint - SE_baseline`:

- positive: spatial heterogeneity **decreased** because explanatory power became more even;
- negative: spatial heterogeneity **increased**;
- approximately zero: unchanged.

When no baseline is supplied, each unordered pair uses the earlier supplied factor as its baseline. Supplying `baseline` reproduces the directional design used in the paper.

## Integrated workflow

```python
from pygeohet import SRSGeoDetector

result = SRSGeoDetector(
    baseline="land_use",
    sample_size=None,
    random_state=42,
).fit(target, factors, adjacency)

print(result.factor.to_frame())
print(result.ecological.to_frame())
print(result.interaction.to_frame())
```

The estimator returns immutable result objects and does not retain partial fitted state after a failure.

## Missing data

One complete-case mask is applied to the target and all supplied factor columns. The same observations are removed from both axes of the adjacency matrix. Final local arrays are expanded to the original row count, with dropped positions represented by `None`.

`missing="raise"` rejects missing values instead of dropping them.

## Islands

The paper includes the focal object in every local region. Therefore, an isolated object has a self-only region and a trivially perfect local quality of one. This may strongly bias `D` when many islands exist.

pyGeoHet rejects islands by default. `allow_islands=True` is an explicit opt-in and the original island indices remain in the result.

## Nominal-data guardrails

SRS-GD requires discrete inputs:

- noninteger floating values are rejected;
- constant targets or factors are rejected;
- a feature or target with one unique label per observation is rejected as likely identifiers or undiscretized data;
- categorical strings, booleans, integer codes and integer-valued floats are accepted.

Continuous features should first be discretized using a scientifically justified method.

## Paper-figure validation

The information table and adjacency matrix in Figure 1 of Bai et al. (2022) are transcribed into the test suite. For feature `a1`, the literal paper definition gives

```text
D  = 0.7325757575757575
SE = 3.245554302578003
```

For `{a1,a2}`:

```text
D  = 0.8143939393939393
SE = 3.3720204818904733
```

The tests also verify local values, positive-region sizes, focal-object inclusion, row-and-adjacency permutation invariance, monotonicity, islands, missing-axis alignment, nominal guardrails and seeded inference.

## Relationship to gdverse

The uploaded gdverse source is used as a reference, but its C++ path differs from the paper in focal-object inclusion, neighbour indexing, multifeature matching and zero-positive-region handling. pyGeoHet implements the published estimand independently rather than targeting line-by-line parity. See `docs/references/stage6-information-ssh-audit.md`.

## Current limitations

- adjacency is dense; sparse large-graph support is deferred;
- geometry-to-adjacency adapters are not part of the core;
- the primary inference uses Student tests and is not adjusted for spatial dependence among overlapping local regions;
- full Baltimore and Cincinnati published-case reproductions remain pending;
- the gdverse compatibility output is documented but not treated as the primary oracle.
