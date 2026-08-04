# HANDOFF - pyGeoHet Stage 3A baseline

Date: 2026-08-05

## 1. Authoritative continuation source

After the Stage 3A pull request is merged, the current `main` branch of `hujinghaoabcd/pyGeoHet` is the only authoritative baseline. A new conversation must fetch the latest `main` commit SHA before editing. Do not reconstruct this stage from chat text, old ZIP archives or the superseded pyGeoDetectorX blueprint.

Read in this order:

1. `HANDOFF_NEXT_CONVERSATION.md`;
2. `PROJECT_STATUS.md`;
3. `DECISIONS.md`;
4. `docs/theory/numerical-conventions.md`;
5. `docs/models/stratification-opgd.md`;
6. `VALIDATION_MATRIX.md`;
7. `ROADMAP.md`;
8. `MODEL_INVENTORY.md`.

## 2. Stage 3A completed work

- immutable `StratificationResult`, `StratificationEvaluationResult` and `OptimalStratificationResult`;
- aligned labels, ordered cut points, requested/actual strata, counts, duplicate cuts, collapse evidence and rejection reasons;
- equal interval with exact cuts retained in the lower stratum;
- quantile using the `lower` convention without splitting equal values;
- weighted Fisher-Jenks natural breaks over distinct values and frequencies;
- geometric intervals for strictly positive values with exact cuts entering the upper stratum;
- standard-deviation bands based on sample SD (`ddof=1`);
- head/tail breaks with configurable threshold and self-determined class count;
- joint-complete-case `evaluate_stratification` and `optimize_stratification`;
- complete method-by-class candidate tables including rejected candidates;
- explicit deterministic maximum-q tie policy;
- integrated `OPGD` / `opgd` workflow feeding selected labels into classic `GeoDetector`;
- Stage 3A tests, model manual and runnable example;
- public API and development version updated to `0.0.3`;
- CI concurrency that cancels superseded pull-request runs.

## 3. Non-negotiable decisions

Classical decisions remain in force, including direct centered sums of squares, explicit sample scope, no silent stratum deletion, tuple overlays and explicit ecological alternatives.

Stage 3A adds:

- stratification is an auditable statistical operation, never labels alone;
- method domain failures are rejected explicitly rather than repaired silently;
- optimization candidates use one joint complete-case sample for `y` and the current `x`;
- rejected candidates remain in the public candidate table;
- q ties within `q_tolerance` prefer fewer actual strata, fewer requested strata, earlier method order and earlier candidate;
- `require_requested_strata=True` is the OPGD default, while direct `stratify` still reports collapsed strata;
- the version `0.0.3` OPGD surface covers univariate method/class-count optimization, not spatial-scale optimization;
- spatial-scale OPGD and MSD require separate contracts and fixtures before public APIs are added.

## 4. Stage 3B objective

Freeze and implement spatial-scale optimization without conflating it with univariate discretization.

Required research and design order:

1. re-read the 2020 OPGD paper and identify the exact scale-search estimand and workflow;
2. inspect official GD/gdverse scale-related source at pinned commits;
3. define whether scale changes aggregation units, neighborhoods, raster resolution or another spatial support;
4. define input geometry/coordinate requirements and supported data structures;
5. define scale candidate construction, ordering and validation;
6. define edge handling, incomplete neighborhoods and missing spatial units;
7. define the common sample used to compare scales;
8. define objective values, ties, complexity penalties and whether q alone is sufficient;
9. design immutable scale-candidate and selected-scale result objects;
10. build static external reference fixtures before exposing the public workflow.

Do not infer missing spatial-scale details from the current `optimize_stratification` implementation.

## 5. Stage 3C objective

MSD remains after Stage 3B. Before coding:

- verify the paper's exact definition of “multiscale”;
- locate and pin author/reference code;
- determine whether the method is supervised by `y` and how candidate cuts are generated;
- document its relationship to OPGD, SPADE and later multivariate methods;
- define computational complexity controls and deterministic ties;
- prepare analytical and static-reference cases.

## 6. Known validation gap

Stage 3A has analytical, boundary, failure-mode and integrated workflow tests. It still requires:

- static reference fixtures for all six stratification methods where external outputs are stable;
- a method/class-count optimum fixture from GD or gdverse;
- reproduction of at least one documented OPGD case;
- larger simulation studies for search optimism and stability.

Do not relabel Stage 3A as fully externally validated until those records exist. The implementation state is “implemented, provisional” in `VALIDATION_MATRIX.md`.

## 7. Required checks

```bash
python -m pip install -e ".[test]"
pytest --cov=pygeohet --cov-report=term-missing
python examples/01_factor_detector.py
python examples/02_classic_workflow.py
python examples/03_stratification_opgd.py
python -m build
ruff check src tests examples tools
black --check src tests examples tools
mypy src/pygeohet
```

Optional NTD verification when the external reference CSV is available:

```bash
python tools/validate_ntd_reference.py \
  "path/to/GeoDetector_2018_Example(Disease Dataset).csv"
```

## 8. Merge discipline

Use a dedicated branch and pull request. Before merge:

- all matrix jobs must pass on Ubuntu, Windows and macOS for Python 3.11-3.13;
- Ruff, Black, mypy and package build must pass;
- new examples must run from the installed package;
- update status, validation, changelog, inventory, roadmap and this handoff;
- record any convention disagreement rather than silently choosing one.
