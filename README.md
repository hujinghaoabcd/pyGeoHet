# pyGeoHet

**pyGeoHet** is a research-oriented Python toolkit for spatially stratified heterogeneity (SSH) analysis. It is designed to cover the classical Geographical Detector family and later extensions for discretization, spatial dependence, robustness, multivariate stratification, local explanation, categorical responses, and information-based SSH measures.

> **Status — Stage 1:** the project foundation, numerical conventions, validation system, q-statistic, and factor detector are implemented. The remaining model families are scheduled in the ten-stage roadmap.

## Installation for development

```bash
python -m pip install -e ".[test]"
```

## Quick start

```python
import pandas as pd
from pygeohet import FactorDetector, q_statistic

frame = pd.DataFrame(
    {
        "y": [1.0, 1.2, 4.8, 5.0, 2.0, 2.1],
        "land_use": ["A", "A", "B", "B", "C", "C"],
        "region": ["north", "north", "south", "south", "north", "south"],
    }
)

single = q_statistic(frame["y"], frame["land_use"])
print(single.q)
print(single.p_value)

result = FactorDetector().fit(frame["y"], frame[["land_use", "region"]])
print(result.to_frame())
```

## Design commitments

- direct sums-of-squares implementation with explicit statistical conventions;
- no silent singleton-stratum removal or hidden imputation;
- immutable result objects with sample counts and variance decomposition;
- separate classic and extended estimands instead of one ambiguous universal API;
- analytical, property-based, cross-language, simulation, and paper-case validation;
- continuously maintained project-status and next-conversation handoff documents;
- no runtime dependency on R, QGIS, or other GeoDetector implementations.

## Scope

The full method inventory and implementation order are documented in [`MODEL_INVENTORY.md`](MODEL_INVENTORY.md) and [`ROADMAP.md`](ROADMAP.md). The numerical contract is documented in [`docs/theory/numerical-conventions.md`](docs/theory/numerical-conventions.md).

## Licence

MIT. Scientific references and implementation-independence notes are recorded in `THIRD_PARTY_NOTICES.md` and the model documentation.
