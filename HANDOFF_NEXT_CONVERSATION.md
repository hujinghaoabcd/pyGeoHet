# HANDOFF - pyGeoHet Stage 4 baseline

Date: 2026-08-05

## 1. Authoritative continuation source

After PR #6 is merged, the current `main` branch of `hujinghaoabcd/pyGeoHet` is the only authoritative baseline. A new conversation must fetch the latest `main` commit SHA before editing. Do not reconstruct Stage 4 from chat text, old ZIP copies or earlier design sketches.

Read in this order:

1. `HANDOFF_NEXT_CONVERSATION.md`;
2. `PROJECT_STATUS.md`;
3. `DECISIONS.md`;
4. `docs/theory/numerical-conventions.md`;
5. `docs/models/robust-rgd-rid.md`;
6. `docs/references/robust-code-audit.md`;
7. `VALIDATION_MATRIX.md`;
8. `ROADMAP.md`;
9. `MODEL_INVENTORY.md`;
10. the Stage 5 papers and uploaded reference source selected during the new audit.

## 2. Completed baseline

Stages 1-3C remain complete in implementation terms:

- direct q and noncentral-F significance;
- factor, interaction, risk and ecological detectors;
- integrated `GeoDetector`;
- six deterministic univariate stratification methods;
- complete q-guided candidate tables and integrated OPGD;
- prepared-support spatial-scale OPGD;
- exact and coarse-to-fine MSD.

Stage 4 adds version `0.0.6` and:

- `RobustDiscretizationResult` for one fixed-zone exact robust solution;
- `RobustCandidateResult` and `RobustOptimizationResult` for complete class-count evidence;
- `robust_discretize()` for exact ordered least-squares segmentation;
- `optimize_robust_discretization()` for explicit class-count selection;
- `RGD`, `rgd`, `RGDResult`;
- `RID`, `rid`, `RIDResult`;
- one joint numeric complete-case sample for each response/factor pair;
- stable ascending explanatory-variable ordering;
- candidate change points only between distinct explanatory values;
- prefix-sum segment costs and exact dynamic programming;
- deterministic break-position ties;
- B-value represented by the complete q variance decomposition on robust zones;
- explicit `marginal_gain` and `max_b` selection policies;
- aligned labels with `None` on dropped rows;
- reuse of the classical `GeoDetector` and interaction detector rather than duplicate implementations;
- brute-force, monotone-rank, duplicate-value, missingness and RGD/RID integration tests;
- a public example, model manual and source-code audit.

## 3. Non-negotiable Stage 4 decisions

- Robust discretization is an ordered response-segmentation problem, not another generic OPGD method.
- Strictly monotone transformations of `x` preserve the candidate order and should preserve the solution.
- Equal `x` values are indivisible and never split by incidental row ordering.
- Fixed-K segmentation minimizes total within-zone response SSE exactly.
- `B = 1 - SSW_R / SST`; it is numerically q on the robust labels, but the B name records the robust construction process.
- Segment costs use prefix sums; the current solver is exact dynamic programming, not a heuristic.
- Objective ties within `b_tolerance` select the lexicographically smallest break-position tuple.
- Cut values belong to the latter zone.
- `min_stratum_size=2` is the package default; users may explicitly request 1 where mathematically acceptable.
- Class-count selection remains separate from fixed-K segmentation.
- `marginal_gain` and `max_b` are explicit estimators; no undocumented LOESS fallback exists.
- RGD reuses the classical detector workflow; RID reuses the collision-safe interaction detector.
- `ruptures`, R, reticulate, GD and gdverse are not runtime dependencies.
- Reference implementations are studied for formulas, expected behaviour and validation, not copied mechanically.

## 4. Source audit completed for Stage 4

The Stage 4 audit used all three evidence tracks:

1. the primary RGD paper and its B-value/change-point formulas;
2. the uploaded author archive, especially `CPD_1.ipynb` and bundled documentation;
3. the uploaded gdverse source, especially:
   - `R/robustdisc.R`;
   - `R/rgd.R`;
   - `R/rid.R`;
   - `inst/python/cpd_disc.py`;
   - robust-method vignettes and help pages.

The author notebook and gdverse helper use `ruptures.Dynp(model="l2")`. pyGeoHet implements the same core least-squares segmentation estimand independently with prefix sums and dynamic programming.

The reviewed gdverse snapshot is GPL-3. The author archive did not expose a licence file in the reviewed snapshot. Neither source was copied or translated line by line.

## 5. Known Stage 4 validation gaps

The robust family is **implemented, provisional**, not externally validated. Remaining work:

1. pin an executable author notebook or gdverse release by version and file hashes;
2. produce static external fixtures for fixed-K break positions, cuts, labels and B-values;
3. produce a class-count selection fixture;
4. record tied-`x` behaviour as a deliberate compatibility difference;
5. reproduce a published RGD case with data provenance;
6. reproduce an official RID interaction example;
7. add response-outlier, perturbation and unbalanced-zone simulations;
8. quantify class-count selection stability and optimism under resampling;
9. benchmark the exact solver and add pruning only if it preserves the public estimand.

Do not delay Stage 5 merely to force superficial numerical parity where source conventions are ambiguous. Preserve these gaps explicitly.

## 6. Next active stage - Stage 5 spatial-dependence detectors

Stage 5 targets SPADE and IDSA. It must start with evidence and numerical-contract work before public API creation.

### Required source audit

1. identify the exact SPADE and IDSA primary papers and equations;
2. locate their official or author implementations in the uploaded archives or current public repositories;
3. inspect gdverse wrappers, tests, vignettes and any upstream package calls;
4. audit licences before adapting implementation ideas;
5. distinguish spatial dependence, spatial support scale, multilevel zoning and fuzzy overlay from Stage 3/4 estimands.

### Freeze before coding

- supported spatial input form: coordinates, adjacency, distance matrix or weights;
- weight standardization and symmetry policy;
- disconnected observations and islands;
- coordinate reference and distance-unit requirements;
- spatial variance or information-loss formula;
- neighbourhood order and multilevel aggregation;
- candidate zoning/discretization construction;
- deterministic versus fuzzy membership;
- IDSA overlay and interaction-zone semantics;
- missing `y`, missing factor, missing neighbour and zero-weight-row handling;
- minimum zone size and degenerate local neighbourhoods;
- exact tie rules and any random seeds;
- immutable result and audit table design;
- small-lattice analytical fixtures and independent brute-force checks;
- external static fixtures and at least one published-case reproduction.

### Recommended implementation sequence

1. add internal spatial-weight validation utilities only when the contract is frozen;
2. implement and test the core spatial variance/dependence statistic;
3. implement SPADE candidate zoning and audit results;
4. add integrated SPADE workflow;
5. audit IDSA separately rather than assuming it is a trivial SPADE overlay;
6. implement deterministic/fuzzy overlay only after its formula is verified;
7. update exports, examples, manuals, validation matrix and handoff in the same PR.

## 7. Required checks

```bash
python -m pip install -e ".[test]"
pytest --cov=pygeohet --cov-report=term-missing
ruff check src tests examples tools
black --check src tests examples tools
mypy src/pygeohet
python examples/01_factor_detector.py
python examples/02_classic_workflow.py
python examples/03_stratification_opgd.py
python examples/04_spatial_scale_opgd.py
python examples/05_multiscale_discretization.py
python examples/06_robust_detectors.py
python -m build
```

Optional NTD verification when the external reference CSV is available:

```bash
python tools/validate_ntd_reference.py \
  "path/to/GeoDetector_2018_Example(Disease Dataset).csv"
```

## 8. Merge discipline

Use a dedicated branch and pull request. Before merge:

- all matrix jobs pass on Ubuntu, Windows and macOS for Python 3.11-3.13;
- Ruff, Black, mypy, all public examples and package build pass;
- new spatial methods have analytical/property tests before public export;
- status, validation, changelog, inventory, roadmap, structure and handoff match the code;
- source and licence audits are recorded;
- external software remains reference-only and never a runtime dependency;
- disagreements among papers, author code and gdverse remain explicit;
- no method is labelled externally validated without the required fixture and case evidence.
