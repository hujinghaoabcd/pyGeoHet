# Project status

**Project:** pyGeoHet  
**Date:** 2026-08-05  
**Completed stage:** Stage 5A of 10 - spatial variance and SPADE  
**Next active stage:** Stage 5B - fuzzy overlay and IDSA  
**Development version:** 0.0.7

## Completed

- package, documentation, testing and cross-platform CI foundation;
- direct q-statistic and four classical detector workflows;
- six continuous-variable stratification methods and auditable OPGD;
- prepared-support spatial-scale comparison;
- exact and coarse-to-fine MSD;
- exact robust change-point discretization, RGD and RID;
- explicit spatial-weight validation and weighted spatial variance;
- power of spatial determinant (PSD);
- compensated power of spatial determinant (CPSD);
- power of spatial and multilevel discretization determinant (PSMD);
- integrated `SPADE` / `spade` workflow for continuous and categorical factors;
- immutable spatial variance, stratum contribution, PSD, CPSD, PSMD candidate and integrated results;
- optional seeded permutation inference for PSD and PSMD;
- provenance-only NTD SPADE fixture and offline validator;
- gdverse/sdsfun formula and source audit with independent Python implementation.

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
    q_statistic,
    spatial_variance,
    power_spatial_determinant,
    compensated_spatial_determinant,
    multilevel_spatial_determinant,
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
)
```

## Stage 5A numerical contract

- the core accepts a prepared square nonnegative spatial-weight matrix;
- no CRS, centroid, neighbourhood, distance unit, bandwidth, symmetrization or row-standardization rule is inferred;
- diagonal weights are excluded and reported;
- directed matrices are accepted and their asymmetry is reported;
- missing rows subset the value/factor vectors and both weight-matrix axes together;
- islands are rejected by default and may only be retained explicitly;
- spatial variance is the weighted average pairwise semivariance;
- PSD is `1 - sum_h(N_h * Gamma_h) / (N * Gamma)`;
- CPSD is response PSD divided by information-retention PSD;
- PSMD is the mean CPSD over at least two explicitly accepted discretization levels;
- invalid PSMD levels remain in the candidate table;
- permutation inference shuffles the response while holding weights and strata fixed;
- geometry libraries and external R packages are not runtime dependencies.

## Validation state

The classical workflow remains validated against the NTD reference case. Stages 3, 4 and parts of Stage 5A are implemented with explicit validation boundaries.

Stage 5A includes:

- a hand-calculated weighted semivariance test;
- invariance to global rescaling of spatial weights;
- direct PSD decomposition and simultaneous row/weight permutation invariance;
- missing-sample alignment across both axes of the weight matrix;
- explicit global and within-stratum island failures;
- CPSD identity when response and information variable coincide;
- PSMD equality to the mean of accepted CPSD candidates;
- deterministic seeded permutation tests;
- mixed continuous/categorical SPADE workflow tests;
- external NTD parity: `0.2566528294856155`, matching the gdverse expectation `0.256653` at six decimals.

The raw NTD GPKG is not redistributed. The fixture records its SHA-256 and preparation contract.

## Deliberately deferred

- automatic construction of weights from geometry or coordinates;
- sparse-weight storage and large-N approximation;
- hidden row normalization or implicit matrix symmetrization;
- treating PSD as numerically identical to classical q under arbitrary weights;
- IDSA fuzzy interaction zones and PID, which require a distinct estimand;
- categorical-response, information, multivariate, local and temporal-lag extensions;
- selection-aware uncertainty for optimized discretization levels.

## Immediate next task

Stage 5B implements IDSA in a separate batch. It begins with a collision-safe fuzzy overlay object, explicit risk-membership normalization and tie rules, followed by the paper's spatial power component, information-retention component and `PID = theta / phi`. Classical tuple intersection must not be substituted for the fuzzy zone.
