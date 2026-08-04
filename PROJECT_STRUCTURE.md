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
│   ├── spatial/
│   │   ├── __init__.py          spatial-statistic public exports
│   │   └── variance.py          prepared weights and spatial variance
│   ├── stratification/
│   │   ├── methods.py           six deterministic univariate methods
│   │   ├── optimal.py           q-guided candidate evaluation and selection
│   │   ├── msd.py               supervised exact/coarse-to-fine MSD search
│   │   └── results.py           immutable stratification/search evidence
│   ├── models/
│   │   ├── geodetector.py       integrated classical workflow
│   │   ├── opgd.py              audited optimal-discretization workflow
│   │   ├── spatial_scale.py     prepared-support OPGD scale comparison
│   │   ├── robust.py            exact robust discretization, RGD and RID
│   │   ├── spade_core.py        PSD and CPSD numerical core
│   │   ├── spade_results.py     immutable SPADE-family results
│   │   ├── spade.py             PSMD and integrated SPADE workflow
│   │   ├── idsa_results.py      immutable fuzzy-overlay and PID results
│   │   └── idsa.py              fuzzy overlay, PID and IDSA search
│   └── py.typed                 inline typing marker
├── tests/
│   ├── fixtures/reference/      static/provenance-only external records
│   ├── test_stratification.py   method, boundary and optimization contracts
│   ├── test_opgd.py             integrated OPGD workflow tests
│   ├── test_spatial_scale.py    scale scores, ties, failures and integration
│   ├── test_msd.py              exact oracle, refinement and audit contracts
│   ├── test_robust.py           brute-force, rank, duplicate-x, RGD/RID tests
│   ├── test_spade.py            variance, PSD, CPSD, PSMD and workflow tests
│   ├── test_idsa.py             fuzzy overlay, PID and IDSA search tests
│   └── test_*.py                classical analytical, edge and workflow tests
├── examples/
│   ├── 01_factor_detector.py
│   ├── 02_classic_workflow.py
│   ├── 03_stratification_opgd.py
│   ├── 04_spatial_scale_opgd.py
│   ├── 05_multiscale_discretization.py
│   ├── 06_robust_detectors.py
│   ├── 07_spade.py
│   └── 08_idsa.py
├── tools/
│   ├── validate_ntd_reference.py
│   └── validate_ntd_spade_reference.py
├── docs/
│   ├── theory/                  formulas and numerical conventions
│   ├── models/                  classic through SPADE manuals
│   ├── references/              paper/source-code audits
│   ├── validation/              published/reference case reports
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

Stage 5A introduces a small `spatial` package because prepared-weight validation and spatial variance are reusable statistical primitives. SPADE is separated into a numerical core, immutable result definitions and workflow composition. This keeps future IDSA code from duplicating spatial variance while preventing fuzzy-overlay logic from being mixed into the PSD implementation.

Dense spatial weights are the current public contract. Sparse matrices, coordinate-to-weight builders and geometry adapters should be added as separate optional layers only after their numerical and dependency contracts are frozen.

Directories for information, multivariate, local and temporal-lagged methods are created only when implementation begins. Planned public names remain in the roadmap until working code, tests and documentation exist.


Stage 5B keeps fuzzy overlay and PID in a dedicated model module. It reuses Stage 5A spatial variance and PSD rather than duplicating those formulas. Fuzzy zone construction, information retention and subset search remain separate from classical tuple interaction and robust RID.
