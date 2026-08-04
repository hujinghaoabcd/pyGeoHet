# Project status

**Project:** pyGeoHet  
**Date:** 2026-08-05  
**Active stage:** Stage 1 of 10  
**Development version:** 0.0.1

## Completed

- repository and package skeleton;
- explicit project scope and ten-stage roadmap;
- numerical-conventions document;
- direct q-statistic and noncentral-F significance implementation;
- immutable statistical result objects;
- classic factor detector for multiple factors;
- validation, tests, example, documentation and CI foundation;
- project handoff policy and next-conversation handoff document.

## Current provisional public surface

```python
from pygeohet import (
    FactorDetector,
    FactorDetectorResult,
    QStatisticResult,
    factor_detector,
    q_statistic,
)
```

## Not yet implemented

Interaction, risk and ecological detectors; discretization; OPGD and all later SSH-family extensions. Their names are not exposed as placeholders.

## Immediate next task

Stage 2: implement the remaining three classical detectors and the integrated `GeoDetector` workflow, with common-complete-case interaction calculations and independently generated reference fixtures.
