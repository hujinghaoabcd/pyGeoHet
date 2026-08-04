# Project status

**Project:** pyGeoHet  
**Date:** 2026-08-05  
**Completed stage:** Stage 4 of 10 - robust discretization, RGD and RID  
**Next active stage:** Stage 5 - spatial-dependence detector family  
**Development version:** 0.0.6

## Completed

- lean package, documentation, testing and CI foundation;
- direct q-statistic with noncentral-F significance;
- factor, interaction, risk and ecological detectors;
- collision-safe tuple overlays and integrated `GeoDetector` workflow;
- immutable auditable result objects for all classical detectors;
- NTD static reference fixture and hash-checking validator;
- six deterministic continuous-variable stratification methods;
- joint-complete-case q-guided candidate evaluation and complete audit tables;
- deterministic tie policy and integrated `OPGD` / `opgd` workflow;
- primary-paper spatial-scale scoring and prepared-support `SpatialScaleOPGD`;
- supervised MSD with exact and coarse-to-fine value-grid search modes;
- exact robust discretization using ordered response segmentation and dynamic programming;
- admissible change points restricted to boundaries between distinct explanatory values;
- B-value reporting with complete q decomposition and aligned missing-row labels;
- auditable class-count search through `marginal_gain` and `max_b` policies;
- integrated `RGD` / `rgd` and `RID` / `rid` workflows;
- independent brute-force, rank-invariance, duplicate-value, missing-data and integration tests;
- uploaded author and gdverse robust-code audit with explicit clean-room and licence boundaries;
- CI execution of all public examples and durable handoff system.

## Current public surface

```python
from pygeohet import (
    GeoDetector,
    OPGD,
    SpatialScaleOPGD,
    MSD,
    RGD,
    RID,
    FactorDetector,
    InteractionDetector,
    RiskDetector,
    EcologicalDetector,
    q_statistic,
    stratify,
    evaluate_stratification,
    optimize_stratification,
    multiscale_discretize,
    robust_discretize,
    optimize_robust_discretization,
    compare_spatial_scales,
    factor_detector,
    interaction_detector,
    risk_detector,
    ecological_detector,
    geodetector,
    opgd,
    rgd,
    rid,
)
```

## Stage 4 numerical contract

- `y` and one continuous `x` use one joint complete-case sample;
- rows are stably ordered by ascending `x`;
- equal `x` values cannot be split across robust zones;
- a segment cost is the response sum of squared deviations from its segment mean;
- prefix sums and exact dynamic programming solve a fixed-zone problem;
- B is `1 - SSW_R / SST` and equals q on the resulting robust labels;
- cut values belong to the latter zone;
- objective ties choose the lexicographically smallest break-position tuple;
- class-count selection is an explicit layer above segmentation;
- RGD and RID reuse the existing classical factor and interaction detectors;
- no runtime dependency on `ruptures`, R, GD or gdverse is introduced.

## Validation state

The classical workflow is validated against analytical properties and the NTD reference case. Stages 3A-3C and Stage 4 are **implemented, provisional** pending stable external fixtures and published-case reproductions.

Stage 4 currently has:

- equality with an independent brute-force ordered-partition oracle on small problems;
- B-value equality with the factor-detector q-value on the selected labels;
- duplicate-`x` indivisibility tests;
- invariance under strictly monotone explanatory-value transformations, including an extreme transformed value;
- missing-row reconstruction and explicit invalid-configuration tests;
- multi-factor RGD and two-factor RID integration tests;
- a source audit of the primary paper, uploaded author notebook and gdverse wrappers.

External validation still requires pinned author/gdverse outputs and a published RGD/RID case.

## Deliberately deferred

- `ruptures` or R-backed compatibility execution at runtime;
- row-level splitting of tied explanatory values;
- implicit LOESS class-count selection without a pinned formula and fixture;
- mixed already-categorical and continuous RID inputs without an explicit provenance contract;
- automatic spatial-support construction;
- SPADE, IDSA, categorical-response, information, multivariate, local and temporal-lag extensions;
- resampling-based uncertainty for optimized strata and class counts.

## Immediate next task

Stage 5 begins with a joint paper-and-source audit of SPADE and IDSA. Before implementation, freeze spatial-weight and neighbourhood contracts, spatial variance decomposition, multilevel discretization, fuzzy or deterministic overlay behaviour, missing-neighbour handling, coordinate/support requirements and independent small-lattice validation fixtures.
