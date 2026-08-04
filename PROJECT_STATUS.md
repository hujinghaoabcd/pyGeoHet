# Project status

**Project:** pyGeoHet  
**Date:** 2026-08-05  
**Completed stage:** Stage 3A of 10 - univariate stratification and OPGD search  
**Next active stage:** Stage 3B - spatial-scale optimization and MSD contract  
**Development version:** 0.0.3

## Completed

- lean package, documentation, testing and CI foundation;
- direct q-statistic with noncentral-F significance;
- factor, interaction, risk and ecological detectors;
- collision-safe tuple overlays and integrated `GeoDetector` workflow;
- immutable auditable result objects for all classical detectors;
- NTD static reference fixture and hash-checking validator;
- continuous-variable stratification protocol with aligned labels and full audit evidence;
- equal interval, quantile, weighted Fisher-Jenks natural breaks, geometric interval, standard-deviation and head/tail breaks;
- joint-complete-case q-guided candidate evaluation;
- complete method-by-class-count candidate tables, including rejected candidates;
- deterministic tie policy and integrated `OPGD` / `opgd` workflow;
- GitHub Actions concurrency control for superseded pull-request runs;
- four-layer validation and durable handoff system.

## Current public surface

```python
from pygeohet import (
    GeoDetector,
    OPGD,
    FactorDetector,
    InteractionDetector,
    RiskDetector,
    EcologicalDetector,
    q_statistic,
    stratify,
    evaluate_stratification,
    optimize_stratification,
    factor_detector,
    interaction_detector,
    risk_detector,
    ecological_detector,
    geodetector,
    opgd,
)
```

## Validation state

The classical workflow passes analytical, edge-case and NTD reference checks. Stage 3A adds method-specific boundary tests, duplicate-edge and collapse tests, domain-restriction tests, joint-sample tests, complete-candidate-table tests and integrated OPGD workflow tests. The final merge gate is the full Ubuntu, Windows and macOS matrix on Python 3.11, 3.12 and 3.13 plus Ruff, Black, mypy and package build.

## Deliberately deferred

- spatial-scale optimization;
- multivariate stratification detector (MSD);
- robust, spatial, categorical-response, information, multivariate, local and temporal-lag extensions;
- resampling-based model-selection uncertainty.

## Immediate next task

Stage 3B must first freeze the spatial-scale and MSD numerical contracts from primary sources and reference implementations. It must define scale candidates, neighborhood construction, edge handling, sample scope, objective functions, deterministic ties, complexity limits and validation fixtures before exposing public APIs.
