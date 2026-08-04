# Project status

**Project:** pyGeoHet  
**Date:** 2026-08-05  
**Completed stage:** Stage 2 of 10  
**Next active stage:** Stage 3 - stratification and optimal discretization  
**Development version:** 0.0.2

## Completed

- lean package, documentation, testing and CI foundation;
- direct q-statistic with noncentral-F significance;
- factor detector for one or multiple categorical factors;
- collision-safe tuple overlays;
- five-class interaction detector on joint complete cases;
- risk detector with stratum summaries, Welch comparisons and p-value matrices;
- ecological detector with documented two-sided and upper-tail compatibility conventions;
- integrated `GeoDetector` workflow;
- immutable auditable result objects for all classical detectors;
- NTD static reference fixture, hash-checking validator and published-case report;
- four-layer validation and durable handoff system.

## Current public surface

```python
from pygeohet import (
    GeoDetector,
    FactorDetector,
    InteractionDetector,
    RiskDetector,
    EcologicalDetector,
    q_statistic,
    factor_detector,
    interaction_detector,
    risk_detector,
    ecological_detector,
    geodetector,
)
```

## Validation state

The classical workflow passes analytical and edge-case tests. The NTD case reproduces `gdverse`/`GD` factor values, interaction labels and risk significance counts. The ecological compatibility mode reproduces the reference package's upper-tail decisions, while the primary two-sided convention is separately documented and tested.

## Not yet implemented

Continuous-variable discretization, candidate search tables, OPGD, MSD, robust, spatial, categorical-response, information, multivariate, local and temporal-lag extensions.

## Immediate next task

Stage 3 begins with a small stratification protocol and result object, followed by equal interval, quantile, natural breaks, geometric interval, standard-deviation and head/tail breaks. Candidate evaluation must retain cut points, actual layer counts, minimum layer size, q, p-value and rejection reason before OPGD search is added.
