# Numerical conventions

This page is part of the statistical contract. Code changes that alter these rules require a decision-log entry, regression tests, and a changelog note.

## q-statistic

For response values \(y_i\) partitioned into \(L\) strata, pyGeoHet computes

\[
SST = \sum_{i=1}^{N}(y_i-\bar y)^2,
\qquad
SSW = \sum_{h=1}^{L}\sum_{i\in h}(y_i-\bar y_h)^2,
\]

\[
SSB = SST-SSW,
\qquad
q = 1-\frac{SSW}{SST}=\frac{SSB}{SST}.
\]

The implementation uses centered sums of squares directly. Population versus sample variance denominators cancel in q, but direct sums avoid ambiguous `ddof` conventions and retain the decomposition for auditing.

## Analytical q significance

For \(0<q<1\), the classical statistic is

\[
F = \frac{N-L}{L-1}\frac{q}{1-q}.
\]

pyGeoHet reports the upper-tail probability from the classical noncentral-F formulation and retains the degrees of freedom and noncentrality parameter in `QStatisticResult`. Future permutation inference will be a separate method rather than silently replacing this route.

## Factor strata and overlay strata

- at least two distinct strata are required;
- original factors use `min_stratum_size=2` by default;
- interaction overlays use `min_overlay_size=1` by default because intersections can naturally produce singleton cells;
- singleton overlay cells are retained and counted, not silently removed;
- users can require larger overlay cells explicitly;
- the response must have nonzero finite total sum of squares;
- labels may be strings, numbers, categorical values, or other hashable values;
- label spelling and row order do not change q.

## Missing values and joint samples

`missing="drop"` removes rows where required variables are missing and reports `dropped_count`. `missing="raise"` rejects any missing row. Infinite responses are invalid rather than treated as missing.

- factor and risk detectors use one complete-case sample per factor;
- interaction uses one joint sample for \(q(X_1)\), \(q(X_2)\), and \(q(X_1\cap X_2)\);
- ecological comparisons use one joint sample for both residual-dispersion calculations.

## Categorical overlay

Overlay labels are tuples of original category values. Underscore joins or other string concatenation are prohibited because they can map distinct pairs to the same label.

## Interaction categories

The classical five-class comparison uses explicit `atol` and `rtol` values. The equality case \(q_{12}=q_1+q_2\) is tested before inequality branches so floating noise does not create unstable category changes.

## Risk detector

Risk comparisons use sample variances and the unequal-variance Welch statistic with Welch-Satterthwaite degrees of freedom. p-values are two-sided and `alpha` is a significance level, not a confidence level. If both group standard errors are numerically zero, equal means produce `(t=0, p=1)` and unequal means produce an infinite signed t-statistic with `p=0`.

## Ecological detector

For factors \(X_1\) and \(X_2\), pyGeoHet evaluates

\[
F=\frac{N_1(N_2-1)SSW_{X_1}}
{N_2(N_1-1)SSW_{X_2}}
\]

with degrees of freedom \((N_1-1,N_2-1)\). Joint complete cases normally give \(N_1=N_2\), reducing the statistic to \(SSW_{X_1}/SSW_{X_2}\).

- `alternative="two-sided"` is the default test of equality and is invariant to factor order;
- `alternative="greater"` is an explicit compatibility mode for the upper-tail gdverse convention;
- the selected alternative is stored in the result;
- the factor with lower SSW is reported as more explanatory only when the selected test is significant.

## Interpretation

q is the proportion of response variation associated with a supplied stratification. It does not establish causality. A high q may also be affected by data-driven stratification complexity; optimization methods must return the full candidate search and not only the maximum q.
