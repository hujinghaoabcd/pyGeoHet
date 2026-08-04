# Classical geographical detectors

Stage 2 completes the four classical detector families while keeping their samples, estimands, and test conventions explicit.

## Factor detector

The factor detector reports the q-statistic and classical noncentral-F significance. Each factor uses its own complete-case sample, and its dropped-row count is retained.

## Interaction detector

For each pair \(X_1, X_2\), pyGeoHet forms a collision-safe tuple overlay and computes

\[
q(X_1),\qquad q(X_2),\qquad q(X_1\cap X_2)
\]

on one joint complete-case sample. The five mutually exclusive output codes are:

| code | relation |
|---|---|
| `weaken_nonlinear` | \(q_{12}<\min(q_1,q_2)\) |
| `weaken_univariate` | \(\min(q_1,q_2)\le q_{12}\le\max(q_1,q_2)\) |
| `enhance_bivariate` | \(\max(q_1,q_2)<q_{12}<q_1+q_2\) |
| `independent` | \(q_{12}\approx q_1+q_2\) |
| `enhance_nonlinear` | \(q_{12}>q_1+q_2\) |

Equality uses explicit absolute and relative tolerances. Overlay labels are tuples, not underscore-joined strings, so distinct category pairs cannot collide.

Original factor strata default to at least two observations. Overlay strata default to at least one observation because intersections can legitimately create singleton cells; these cells are retained rather than silently removed. Users can require a larger minimum through `min_overlay_size`.

## Risk detector

For every pair of strata, the risk detector computes the signed mean difference and the unequal-variance Welch statistic

\[
t=\frac{\bar y_1-\bar y_2}
{\sqrt{s_1^2/n_1+s_2^2/n_2}},
\]

with Welch-Satterthwaite degrees of freedom. The result contains stratum sample sizes, means, sample variances, t-statistics, degrees of freedom, two-sided p-values, significance flags, and a symmetric p-value matrix.

## Ecological detector

For factors \(X_1\) and \(X_2\), the primary-paper ratio is

\[
F=\frac{N_1(N_2-1)SSW_{X_1}}
{N_2(N_1-1)SSW_{X_2}},
\]

with degrees of freedom \((N_1-1,N_2-1)\). pyGeoHet uses one joint complete-case sample, so usually \(N_1=N_2\) and the ratio reduces to \(SSW_{X_1}/SSW_{X_2}\).

The default `alternative="two-sided"` tests equality of residual within-stratum dispersion without depending on factor order. `alternative="greater"` reproduces the upper-tail convention used by current `gdverse` ecological output. The selected convention is stored in `EcologicalDetectorResult`.

## Integrated workflow

```python
from pygeohet import GeoDetector

result = GeoDetector(
    alpha=0.05,
    ecological_alternative="two-sided",
    min_stratum_size=2,
    min_overlay_size=1,
).fit(y, factors)
```

With one factor, factor and risk detectors are returned and pairwise results are `None`. With two or more factors, interaction and ecological results are also produced.
