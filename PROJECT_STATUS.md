# Project status

**Project:** pyGeoHet  
**Date:** 2026-08-05  
**Completed stage:** Stage 3B of 10 - prepared-support spatial-scale OPGD selection  
**Next active stage:** Stage 3C - multiscale discretization (MSD)  
**Development version:** 0.0.4

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
- primary-paper spatial-scale scoring based on the 90% quantile of factor q values;
- optional legacy-GD significance filtering and explicit mean-q descriptive scoring;
- prepared-support `compare_spatial_scales()` and integrated `SpatialScaleOPGD`;
- strict common-factor validation, deterministic scale ties and failed-scale evidence;
- CI execution of all public examples and durable handoff system.

## Current public surface

```python
from pygeohet import (
    GeoDetector,
    OPGD,
    SpatialScaleOPGD,
    FactorDetector,
    InteractionDetector,
    RiskDetector,
    EcologicalDetector,
    q_statistic,
    stratify,
    evaluate_stratification,
    optimize_stratification,
    compare_spatial_scales,
    factor_detector,
    interaction_detector,
    risk_detector,
    ecological_detector,
    geodetector,
    opgd,
)
```

## Validation state

The classical workflow passes analytical, edge-case and NTD reference checks. Stage 3A and 3B add method-boundary tests, collapse and domain-restriction tests, joint-sample tests, full candidate-table tests, spatial-scale quantile tests, significance-filter tests, common-factor tests, deterministic tie tests, failed-scale retention and integrated OPGD/scale workflows. External scale fixtures and a full published-case reproduction remain necessary before Stage 3B is labelled fully externally validated.

## Deliberately deferred

- automatic raster, polygon or point-support aggregation;
- newer gdverse mean-plus-LOESS scale selection compatibility;
- multiscale discretization detector (MSD);
- robust, spatial, categorical-response, information, multivariate, local and temporal-lag extensions;
- resampling-based model-selection uncertainty.

## Immediate next task

Stage 3C must freeze the MSD estimand and candidate-generation contract from the paper and pinned author/reference code. It must establish whether “multiscale” refers to multiresolution support, multiple discretization scales, hierarchical breaks, or another supervised construction; define its objective, ties, complexity controls, sample scope and validation fixtures before public APIs are added.
