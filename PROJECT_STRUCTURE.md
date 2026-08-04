# pyGeoHet project structure

```text
pyGeoHet/
├── src/pygeohet/
│   ├── __init__.py              public convenience API
│   ├── _version.py              package version
│   ├── exceptions.py            explicit statistical/data errors
│   ├── validation.py            factor coercion and complete-case contracts
│   ├── results.py               classical immutable result objects
│   ├── core/
│   │   ├── qstat.py             q and noncentral-F inference
│   │   ├── overlay.py           collision-safe tuple overlays
│   │   └── interaction.py       interaction-type classifier
│   ├── detectors/               factor, interaction, risk and ecological APIs
│   ├── stratification/
│   │   ├── methods.py           six deterministic univariate methods
│   │   ├── optimal.py           q-guided candidate evaluation and selection
│   │   ├── msd.py               supervised exact/coarse-to-fine MSD search
│   │   └── results.py           immutable stratification/search evidence
│   ├── models/
│   │   ├── geodetector.py       integrated classical workflow
│   │   ├── opgd.py              audited optimal-discretization workflow
│   │   ├── spatial_scale.py     prepared-support OPGD scale comparison
│   │   └── robust.py            exact robust discretization, RGD and RID
│   └── py.typed                 inline typing marker
├── tests/
│   ├── fixtures/reference/      static external-output records
│   ├── test_stratification.py   method, boundary and optimization contracts
│   ├── test_opgd.py             integrated OPGD workflow tests
│   ├── test_spatial_scale.py    scale scores, ties, failures and integration
│   ├── test_msd.py              exact oracle, refinement and audit contracts
│   ├── test_robust.py           brute-force, rank, duplicate-x, RGD/RID tests
│   └── test_*.py                classical analytical, edge and workflow tests
├── examples/
│   ├── 01_factor_detector.py
│   ├── 02_classic_workflow.py
│   ├── 03_stratification_opgd.py
│   ├── 04_spatial_scale_opgd.py
│   ├── 05_multiscale_discretization.py
│   └── 06_robust_detectors.py
├── tools/                       offline fixture validators/generators
├── docs/
│   ├── theory/                  formulas and numerical conventions
│   ├── models/                  classic, OPGD, scale, MSD and robust manuals
│   ├── references/              paper/source-code audits
│   ├── validation/              published-case reports
│   └── development/             testing and handoff policies
├── .github/workflows/ci.yml     cross-platform gate with PR concurrency control
├── MODEL_INVENTORY.md           methods, references and implementation state
├── VALIDATION_MATRIX.md         evidence required for every public model
├── DECISIONS.md                 durable statistical and API decisions
├── PROJECT_STATUS.md            current factual state
├── ROADMAP.md                   ten-stage development plan
└── HANDOFF_NEXT_CONVERSATION.md authoritative continuation instructions
```

Automatic geographic-support aggregation is intentionally absent from the core package. Scale-specific datasets are prepared explicitly upstream and compared through `models/spatial_scale.py`. MSD's scales are explanatory-variable value-grid resolutions and remain separate from geographic support.

The robust family lives in one focused `models/robust.py` module because fixed-K segmentation, class-count selection, RGD and RID share one numerical kernel. It reuses the existing q and interaction implementations instead of duplicating them. Separate robust subpackages should be introduced only when the implementation grows enough to justify them.

Directories for spatial-dependence, information, multivariate, local and temporal-lagged methods are created only when implementation begins. Planned public names remain in the roadmap until working code, tests and documentation exist.
