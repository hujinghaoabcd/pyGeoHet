# Project status

**Project:** pyGeoHet  
**Date:** 2026-08-05  
**Completed stage:** Stage 3C of 10 - multiscale discretization (MSD)  
**Next active stage:** Stage 4 - robust geographical detector family  
**Development version:** 0.0.5

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
- supervised MSD with exact-search and coarse-to-fine value-grid modes;
- immutable MSD scale-path evidence, explicit grid origin/resolution and deterministic cut ties;
- independent exhaustive-enumeration tests and a 6 -> 3 -> 1 synthetic recovery case;
- paper/source-code audit that records the uploaded GD/gdverse reference implementations and the unresolved Figshare archive gap;
- CI execution of all public examples and durable handoff system.

## Current public surface

```python
from pygeohet import (
    GeoDetector,
    OPGD,
    SpatialScaleOPGD,
    MSD,
    FactorDetector,
    InteractionDetector,
    RiskDetector,
    EcologicalDetector,
    q_statistic,
    stratify,
    evaluate_stratification,
    optimize_stratification,
    multiscale_discretize,
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

The classical workflow passes analytical, edge-case and NTD reference checks. Stage 3A and 3B pass method-boundary, collapse, domain, joint-sample, candidate-table, scale-score, significance-filter, common-factor, deterministic-tie and failed-scale tests. Stage 3C additionally passes exact-search comparison against independent exhaustive enumeration, known-threshold recovery through a 6 -> 3 -> 1 path, cut-membership, missing-sample, invalid-contract and audit-table tests.

Stages 3A-3C remain **implemented, provisional**. Stable external fixtures, published-case reproductions and parity with the MSD author Figshare archive are still required before they are marked fully externally validated.

## Deliberately deferred

- automatic raster, polygon or point-support aggregation;
- newer gdverse mean-plus-LOESS scale selection compatibility;
- automatic choice of MSD class count, upscale or buffer sequence;
- author-code compatibility mode before the Figshare archive is pinned and executed;
- robust, spatial, categorical-response, information, multivariate, local and temporal-lag extensions;
- resampling-based model-selection uncertainty.

## Immediate next task

Stage 4 begins with an audit of the uploaded `Robust_Geographical_Detector` research code, gdverse `robustdisc.R`/`rgd.R`/`rid.R`, and the RGD/RID papers. Before adding public APIs, freeze the sorted-sample contract, variance-change-point objective, dynamic-programming recursion, minimum segment size, B-value definition, outlier sensitivity experiments and compatibility boundaries between RGD, RID and MSD.
