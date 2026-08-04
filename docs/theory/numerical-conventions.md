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

## Analytical significance

For \(0<q<1\), the classical statistic is

\[
F = \frac{N-L}{L-1}\frac{q}{1-q}.
\]

pyGeoHet reports the upper-tail probability from the classical noncentral-F formulation and retains the degrees of freedom and noncentrality parameter in `QStatisticResult`. Future permutation inference will be a separate method rather than silently replacing this route.

## Valid strata

- at least two distinct strata are required;
- each stratum contains at least `min_stratum_size` observations, default 2;
- the response has nonzero finite total sum of squares;
- labels may be strings, numbers, categorical values, or other hashable values;
- label spelling and row order do not change q.

Singleton strata are not silently dropped because doing so changes the sample, strata count and significance calculation.

## Missing values

`missing="drop"` removes rows where either the response or current factor is missing and reports `dropped_count`. `missing="raise"` rejects any missing row. Infinite responses are invalid rather than treated as missing.

For a multi-factor factor detector, complete cases are selected separately for each factor. Stage 2 interactions will use one joint complete-case sample for all three compared q values.

## Interpretation

q is the proportion of response variation associated with a supplied stratification. It does not establish causality. A high q may also be affected by data-driven stratification complexity; optimization methods must return the full candidate search and not only the maximum q.
