# HANDOFF - pyGeoHet Stage 3B baseline

Date: 2026-08-05

## 1. Authoritative continuation source

After the Stage 3B pull request is merged, the current `main` branch of `hujinghaoabcd/pyGeoHet` is the only authoritative baseline. A new conversation must fetch the latest `main` commit SHA before editing. Do not reconstruct this stage from chat text, old ZIP archives or the superseded pyGeoDetectorX blueprint.

Read in this order:

1. `HANDOFF_NEXT_CONVERSATION.md`;
2. `PROJECT_STATUS.md`;
3. `DECISIONS.md`;
4. `docs/theory/numerical-conventions.md`;
5. `docs/models/stratification-opgd.md`;
6. `docs/models/spatial-scale-opgd.md`;
7. `VALIDATION_MATRIX.md`;
8. `ROADMAP.md`;
9. `MODEL_INVENTORY.md`.

## 2. Completed baseline

Stages 1-3A remain complete: direct q, four classical detectors, integrated GeoDetector, six stratification methods, complete q-guided candidate tables and univariate OPGD.

Stage 3B adds:

- immutable `SpatialScaleCandidateResult`, `SpatialScaleResult` and `SpatialScaleOPGDResult`;
- `compare_spatial_scales()` for precomputed factor, GeoDetector and OPGD outputs;
- the 2020 paper's default rule: maximize the 90% quantile of factor q values across candidate supports;
- `significant_only=True` for the legacy `GD::sesu()` p-value eligibility convention;
- explicit mean-q scoring for descriptive/reference comparisons;
- common-factor-set validation across successful scales;
- `first`, `smallest` and `largest` deterministic tie policies;
- a requirement for at least two accepted scales before selection is valid;
- `SpatialScaleOPGD`, which runs Stage 3A OPGD on each explicitly prepared scale dataset;
- retention of failed scale candidates and failure reasons;
- tests, model manual, public example, exports and version `0.0.4`.

## 3. Non-negotiable Stage 3B decisions

- Spatial support construction is upstream and explicit. The core does not silently aggregate rasters, polygons or points.
- The paper's 90% q-quantile maximum is the primary estimator.
- Legacy GD significance filtering is an explicit compatibility option, not part of the default paper reading.
- Newer gdverse mean-q plus LOESS stopping is a different estimator. It is documented but not claimed as reproduced.
- Successful scales must contain the same explanatory-factor set; observation counts may differ.
- Failed scales remain visible.
- A single successful support is insufficient for a scale comparison.
- Scale-score ties never depend on incidental dictionary sorting; the selected policy is stored in the result.

## 4. Stage 3C objective - MSD

Before coding Multiscale Discretization (MSD):

1. identify the exact primary paper and extract its formal estimand;
2. locate and pin author or official reference code;
3. establish what “multiscale” means in that method;
4. determine whether candidates are supervised by `y` and how break candidates are generated;
5. establish the role of spatial support, neighbourhoods and multiple resolutions;
6. define objective values, stopping rules, ties and complexity penalties;
7. define missing-data and common-sample contracts;
8. compare MSD explicitly with Stage 3A OPGD, Stage 3B support selection and later SPADE;
9. design immutable candidate and selected-model results;
10. prepare analytical and static external fixtures before adding public APIs.

Do not infer MSD from `SpatialScaleOPGD` or from generic multiresolution classification.

## 5. Known validation gaps

Stage 3A still needs stable external fixtures for all six stratification methods and a published OPGD case.

Stage 3B still needs:

- a static fixture reproducing the paper/legacy-GD 90% quantile scale table;
- a documented multi-scale OPGD case reproduction, preferably the vegetation or H1N1 example when redistributable inputs are available;
- a pinned fixture for the newer gdverse LOESS heuristic before compatibility implementation;
- simulation of scale-selection stability and search optimism.

Until then Stage 3A and 3B remain “implemented, provisional” rather than fully externally validated.

## 6. Required checks

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
python -m build
```

Optional NTD verification when the external reference CSV is available:

```bash
python tools/validate_ntd_reference.py \
  "path/to/GeoDetector_2018_Example(Disease Dataset).csv"
```

## 7. Merge discipline

Use a dedicated branch and pull request. Before merge:

- all matrix jobs must pass on Ubuntu, Windows and macOS for Python 3.11-3.13;
- Ruff, Black, mypy, all public examples and package build must pass;
- status, validation, changelog, inventory, roadmap and this handoff must match the code;
- external software remains reference-only and never a runtime dependency;
- disagreements among paper, GD and gdverse conventions must remain explicit.
