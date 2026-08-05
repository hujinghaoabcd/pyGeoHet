# Project status

**Project:** pyGeoHet  
**Date:** 2026-08-05  
**Completed stage:** Stage 6A of 10 - spatial rough set geographical detectors  
**Next active stage:** Stage 6B - information-consistency SSH  
**Development version:** 0.0.9

## Completed

- package, documentation, testing and cross-platform CI foundation;
- direct q-statistic and four classical detector workflows;
- six continuous-variable stratification methods and auditable OPGD;
- prepared-support spatial-scale comparison;
- exact and coarse-to-fine MSD;
- exact robust change-point discretization, RGD and RID;
- prepared spatial-weight validation, spatial variance, PSD, CPSD, PSMD and SPADE;
- collision-safe fuzzy interaction zones, fixed PID and integrated IDSA;
- paper-aligned spatial rough-set model for nominal target variables;
- local regions defined as focal object plus prepared binary neighbours;
- exact multifeature tuple indiscernibility and local positive regions;
- local approximation quality, average explanatory power `D` and spatial entropy `SE`;
- SRS factor, ecological and interaction detectors;
- paired inference on common focal objects and seeded paper-style subsampling;
- explicit adjacency symmetry, island, missing-data and nominal-input contracts;
- immutable SRS evidence and integrated `SRSGeoDetector` workflow;
- Figure 1 hand-calculated SRS-GD fixture and monotonicity validation;
- paper/source discrepancy audit separating the published estimand from ambiguous reference C++ behaviour;
- public API regression protection, model manual, example and Stage 6 evidence plan.

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
    SRSGeoDetector,
    q_statistic,
    spatial_variance,
    power_spatial_determinant,
    compensated_spatial_determinant,
    multilevel_spatial_determinant,
    fuzzy_overlay,
    power_interactive_determinant,
    optimize_spatial_discretization,
    spatial_rough_set_measure,
    srs_factor_detector,
    srs_ecological_detector,
    srs_interaction_detector,
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
    srsgd,
)
```

## Stage 6A numerical contract

- the target and explanatory features are nominal or deliberately discretized;
- a prepared finite binary square adjacency matrix is required;
- diagonal entries are ignored and the focal object is added exactly once to each local region;
- symmetric adjacency is required by default;
- islands are rejected by default because self-only regions have trivially perfect local quality;
- multifeature indiscernibility requires equality on every feature and uses collision-safe tuples;
- a local equivalence class enters the positive region only when it contains one target category;
- local quality is positive-region size divided by local-region size;
- `D` is the mean local quality;
- `SE` is Shannon entropy of normalized local qualities and is undefined when all local qualities are zero;
- adding explanatory features cannot reduce local quality or `D` apart from numerical tolerance;
- one complete-case mask is applied to the target, all factors and both adjacency axes;
- factor comparisons use paired local-quality vectors on common focal objects;
- geometry, CRS, contiguity and distance choices remain upstream responsibilities;
- no R, gdverse, spatial geometry package or reference C++ code is called at runtime.

## Validation state

Stage 6A currently includes:

- exact transcription of the paper Figure 1 information system and adjacency matrix;
- hand-derived local-region sizes, positive-region sizes and local qualities;
- `a1` result `D = 0.7325757575757575` and `SE = 3.245554302578003`;
- `{a1,a2}` result `D = 0.8143939393939393` and `SE = 3.3720204818904733`;
- exact tuple-refinement monotonicity;
- focal-object inclusion independent of input diagonal values;
- joint row and adjacency permutation invariance;
- explicit island rejection and opt-in self-only regions;
- missing-row removal from both adjacency axes and original-row reconstruction;
- rejection of undiscretized continuous targets and factors;
- symmetric-adjacency enforcement and explicit directed relaxation;
- seeded subsampling reproducibility;
- integrated factor, ecological and interaction workflows;
- top-level public API protection.

The full Stage 6A CI passed on Ubuntu, Windows and macOS with Python 3.11, 3.12 and 3.13. Ruff, Black, mypy, all nine public examples, wheel build and source-distribution build also passed.

Stage 6A is **implemented, provisional** pending published Baltimore/Cincinnati case reproductions and a separately pinned compatibility table for the reviewed gdverse implementation. The paper-aligned result is the primary estimand; known source discrepancies are not hidden.

## Deliberately deferred

- automatic adjacency construction from geometry;
- sparse and large-graph SRS-GD optimization;
- spatial-dependence-adjusted inference for overlapping local regions;
- unpaired Welch compatibility inference unless required by a pinned table;
- silent use of reference C++ indexing and any-coordinate matching behaviour;
- Stage 6B information-consistency estimators until histogram and entropy contracts are frozen;
- Stage 6C SWMI until the complete 2026 primary-source formulas and a numerical reference are available;
- later multivariate, local, regression, observation-bias and temporal extensions.

## Immediate next task

Stage 6B implements information-consistency SSH in two independent layers:

1. `IN-SSH` for nominal targets using normalized mutual information;
2. `IC-SSH` for continuous targets using stratum-weighted, arctangent-normalized relative entropy.

Before code merge, freeze constant-target behaviour, common histogram support, bin-edge construction, zero-density handling, minimum stratum size, corrected permutation p-values and static outputs from a pinned `stscl/sshicm` revision. These estimators must remain separate from q, SRS-GD, PSD and PID.
