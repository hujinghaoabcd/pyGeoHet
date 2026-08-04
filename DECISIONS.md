# Durable project decisions

## D001 — Package identity

The repository, distribution and import family use `pyGeoHet` / `pygeohet`. The scope is the SSH method family, not only classic GeoDetector variants.

## D002 — Direct sums of squares

q is calculated as `1 - SSW / SST` using direct centered sums of squares. No `ddof` choice appears in the public estimand.

## D003 — Small strata

The default minimum stratum size is two. Singleton strata raise `SmallStratumError`; they are never silently removed. Later merge/drop policies must return an audit trail.

## D004 — Missing data

The default is pairwise complete cases for one factor and factorwise complete cases across a factor table. Dropped-row counts are reported. Stage 2 interactions must use one joint complete-case sample for q(X1), q(X2), and q(X1∩X2).

## D005 — Significance convention

The Stage 1 analytical p-value follows the classical noncentral-F formulation. The noncentrality parameter and degrees of freedom are retained. Permutation inference will be a separate explicit method.

## D006 — No causal wording

q measures explanatory power or association under a supplied stratification. Package summaries do not describe a factor as causal without an external causal design.

## D007 — Result objects

Public statistical results are immutable and retain the information needed to audit the variance decomposition and sample scope.

## D008 — No empty public architecture

Modules and public names are introduced only with working code, tests and documentation. Planned models remain in the roadmap, not `__init__.py`.

## D009 — Runtime independence

pyGeoHet implements its own numerical route and has no runtime calls to R, gdverse, GD, QGIS or other GeoDetector packages.

## D010 — Handoff is a release gate

Every development batch updates `PROJECT_STATUS.md`, `VALIDATION_MATRIX.md`, `CHANGELOG.md`, and `HANDOFF_NEXT_CONVERSATION.md` before merge.
