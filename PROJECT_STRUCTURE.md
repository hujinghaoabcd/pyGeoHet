# pyGeoHet project structure

```text
pyGeoHet/
├── src/pygeohet/
│   ├── __init__.py              public convenience API
│   ├── _version.py              package version
│   ├── exceptions.py            explicit statistical/data errors
│   ├── validation.py            factor coercion and complete-case contracts
│   ├── results.py               immutable result objects
│   ├── core/
│   │   ├── qstat.py             q and noncentral-F inference
│   │   ├── overlay.py           collision-safe tuple overlays
│   │   └── interaction.py       interaction-type classifier
│   ├── detectors/               factor, interaction, risk and ecological APIs
│   ├── models/                  integrated GeoDetector workflow
│   └── py.typed                 inline typing marker
├── tests/
│   ├── fixtures/reference/      static external-output records
│   └── test_*.py                analytical, edge and workflow tests
├── examples/                    installed-package runnable examples
├── tools/                       offline fixture validators/generators
├── docs/
│   ├── theory/                  formulas and numerical conventions
│   ├── models/                  model manuals
│   ├── validation/              published-case reports
│   └── development/             testing and handoff policies
├── .github/workflows/ci.yml     compact cross-platform quality gate
├── MODEL_INVENTORY.md           methods, references and implementation state
├── VALIDATION_MATRIX.md         evidence required for every public model
├── DECISIONS.md                 durable statistical and API decisions
├── PROJECT_STATUS.md            current factual state
├── ROADMAP.md                   ten-stage development plan
└── HANDOFF_NEXT_CONVERSATION.md authoritative continuation instructions
```

Directories for stratification, robust, spatial, information, multivariate, local and experimental-lagged methods are created only when implementation begins. This keeps the package proportional to the algorithms.
