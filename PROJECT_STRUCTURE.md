# pyGeoHet project structure

```text
pyGeoHet/
├── src/pygeohet/
│   ├── __init__.py              public convenience API
│   ├── _version.py              package version
│   ├── exceptions.py            explicit statistical/data errors
│   ├── validation.py            shared input contracts
│   ├── results.py               immutable result objects
│   ├── core/                    mathematical SSH primitives
│   ├── detectors/               detector APIs
│   └── py.typed                 inline typing marker
├── tests/                       unit, property and future reference tests
├── examples/                    installed-package runnable examples
├── docs/
│   ├── theory/                  formulas and numerical conventions
│   └── development/             testing and handoff policies
├── .github/workflows/ci.yml     compact cross-platform quality gate
├── MODEL_INVENTORY.md           methods, references and implementation state
├── VALIDATION_MATRIX.md         evidence required for every public model
├── DECISIONS.md                 durable statistical and API decisions
├── PROJECT_STATUS.md            current factual state
├── ROADMAP.md                   ten-stage development plan
└── HANDOFF_NEXT_CONVERSATION.md authoritative continuation instructions
```

Directories for robust, spatial, information, multivariate, local, and experimental-lagged methods are created only when implementation begins. This prevents an empty architecture from becoming more complex than the algorithms.
