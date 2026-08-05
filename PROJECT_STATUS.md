# Project status

**Project:** pyGeoHet  
**Date:** 2026-08-05  
**Completed stage:** Stage 5B of 10 - fuzzy overlay and IDSA  
**Next active stage:** Stage 6 - categorical and information-consistency SSH  
**Development version:** 0.0.8

## Completed

- package, documentation, testing and cross-platform CI foundation;
- direct q-statistic and four classical detector workflows;
- six continuous-variable stratification methods and auditable OPGD;
- prepared-support spatial-scale comparison;
- exact and coarse-to-fine MSD;
- exact robust change-point discretization, RGD and RID;
- prepared spatial-weight validation, spatial variance, PSD, CPSD, PSMD and SPADE;
- collision-safe fuzzy AND/OR interaction zones;
- global factor-stratum risk normalization with explicit constant-risk failure;
- fixed-discretization `PID = theta / phi`;
- canonical ordinal encoding for discretized explanatory factors;
- CPSD-guided continuous-factor discretization with complete candidate evidence;
- greedy and bounded exhaustive IDSA factor-combination search;
- conditional permutation inference that recomputes response-derived fuzzy zones;
- immutable fuzzy membership, PID, discretization, combination and integrated IDSA results;
- tuple-label regression protection in the shared PSD core;
- top-level public API regression protection for Stage 5B symbols;
- source audits covering the IDSA paper, uploaded gdverse and maintained sdsfun code;
- durable handoff and validation tracking.

## Current public surface

```python
from pygeohet import (
    GeoDetector,
    OPGD,
    SpatialScaleOPGD,
    MSD,
    RGD,
    RID,
    SPADE,
    IDSA,
    q_statistic,
    spatial_variance,
    power_spatial_determinant,
    compensated_spatial_determinant,
    multilevel_spatial_determinant,
    fuzzy_overlay,
    power_interactive_determinant,
    optimize_spatial_discretization,
    stratify,
    optimize_stratification,
    multiscale_discretize,
    robust_discretize,
    optimize_robust_discretization,
    compare_spatial_scales,
    geodetector,
    opgd,
    rgd,
    rid,
    spade,
    idsa,
)
```

## Stage 5B numerical contract

- fuzzy membership is min-max normalization of all factor-stratum response means;
- fuzzy AND selects the minimum current membership and fuzzy OR the maximum;
- zone identity is `(factor_name, original_stratum_label)`, never a concatenated string;
- membership ties use an explicit first- or last-factor policy;
- equal risk at every factor-stratum makes membership undefined and raises an error;
- fixed PID factors are treated as ordered discretizations and canonically encoded as `1,...,K`;
- `theta` is response PSD under the fuzzy zones;
- `phi` is one minus the summed within-zone spatial variance of all discretized factors divided by their summed global spatial variance;
- `PID = theta / phi`, with explicit zero-denominator failure;
- fuzzy zones must satisfy the Stage 5A minimum-size and internal-weight contracts;
- continuous-factor candidates are selected by maximum CPSD with deterministic simplicity ties;
- greedy search follows iterative factor addition, while exhaustive search is explicitly bounded;
- response permutations recompute risks, memberships, fuzzy zones, theta, phi and PID;
- one joint complete-case sample is used in integrated IDSA and both weight-matrix axes are subset together;
- no R, gdverse, sdsfun, sf or spdep call occurs at runtime.

## Validation state

The classical workflow remains validated against the NTD reference case. The pinned categorical SPADE route remains externally checked. Stage 5B currently has analytical and property validation:

- manually derived fuzzy AND and OR labels;
- exact global min-max memberships;
- explicit first/last tie behaviour;
- constant-risk and missing-data failures;
- direct equality of reported PID with `theta / phi`;
- invariance to shifted and positively rescaled ordinal class codes;
- deterministic recomputation of fuzzy zones under permutation;
- maximum-CPSD candidate and simplicity-tie tests;
- greedy and exhaustive subset-search tests;
- joint missing-row reconstruction in final labels;
- collision-safe tuple strata accepted by the shared PSD core;
- documented Stage 5B symbols verified at the package top level.

Final CI for PR #8 passed on Ubuntu, Windows and macOS with Python 3.11, 3.12 and 3.13. Ruff, Black, mypy, all eight public examples, wheel build and source-distribution build also passed.

Stage 5B is **implemented, provisional** pending pinned external fuzzy-zone and PID fixtures and a published multivariable IDSA reproduction.

## Deliberately deferred

- silent assignment of order to arbitrary nominal categories;
- unpinned LOESS compatibility selection for CPSD class counts;
- automatic spatial-weight construction from geometry;
- sparse-weight and large-N IDSA optimization;
- fully selection-adjusted p-values after discretization and subset search;
- simultaneous uncertainty for weights, discretization and interaction selection;
- Stage 6 nominal-response, information-consistency and SWMI methods;
- later multivariate, local, regression, observation-bias and temporal extensions.

## Immediate next task

Stage 6 begins with an evidence audit for SRS-GD, SSHIC/SSHIN and SWMI. Before implementation, freeze nominal-response estimands, spatial rough-set neighbourhoods, information-consistency formulas, permutation nulls, missing-category handling and external fixtures. These methods must remain separate from variance-based q, PSD and PID.
