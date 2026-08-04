# HANDOFF - pyGeoHet Stage 3C baseline

Date: 2026-08-05

## 1. Authoritative continuation source

After PR #5 is merged, the current `main` branch of `hujinghaoabcd/pyGeoHet` is the only authoritative baseline. A new conversation must fetch the latest `main` commit SHA before editing. Do not reconstruct this stage from chat text, old ZIP archives or the superseded pyGeoDetectorX blueprint.

Read in this order:

1. `HANDOFF_NEXT_CONVERSATION.md`;
2. `PROJECT_STATUS.md`;
3. `DECISIONS.md`;
4. `docs/theory/numerical-conventions.md`;
5. `docs/models/stratification-opgd.md`;
6. `docs/models/spatial-scale-opgd.md`;
7. `docs/models/msd.md`;
8. `docs/references/msd-code-audit.md`;
9. `VALIDATION_MATRIX.md`;
10. `ROADMAP.md`;
11. `MODEL_INVENTORY.md`.

## 2. Completed baseline

Stages 1-3B remain complete: direct q, four classical detectors, integrated GeoDetector, six stratification methods, complete q-guided candidate tables, univariate OPGD and prepared-support spatial-scale OPGD.

Stage 3C adds version `0.0.5` and:

- `MSD` and `multiscale_discretize()`;
- immutable `MSDScaleResult` and `MSDResult`;
- one joint complete-case sample sorted stably by the explanatory variable;
- exact global search with `upscale=1`;
- paper-style coarse-to-fine value-grid search for explicit upscale/buffer sequences;
- one selected cut from each mapped epsilon neighbourhood during refinement;
- cached interval within-stratum sums of squares;
- equivalent q maximization with a deterministic lexicographic cut-tuple tie rule;
- explicit `origin`, `base_resolution`, `min_stratum_size` and cut-membership contracts;
- per-scale candidates, selected cuts, combination counts, q and objective evidence;
- exhaustive-enumeration tests and a 6 -> 3 -> 1 known-threshold recovery;
- public example, model manual, paper/source-code audit and updated project documents.

## 3. Non-negotiable Stage 3 decisions

- Stage 3B spatial support scale and Stage 3C MSD value-grid scale are different estimands.
- Geographic support construction remains explicit upstream.
- MSD is supervised by `y` and uses a fixed user-supplied number of strata.
- All MSD scales use the same joint complete-case sample.
- Coarse-to-fine scales are explicit, strictly decreasing and end at 1.
- Every previous cut contributes one mapped epsilon neighbourhood; refinement chooses exactly one ordered cut from each neighbourhood.
- Cut values belong to the latter class.
- `upscale=1` is the exact-search reference mode.
- Objective ties never depend on container ordering; the lexicographically smallest cut tuple is selected and the rule is stored.
- Class counts above 10 are rejected under the current paper-derived practical contract.
- Failed or invalid configurations raise explicit errors; the package does not silently fall back to another estimator.
- External software is reference-only and is never called at runtime.

## 4. Reference-code evidence and unresolved MSD gap

The user explicitly requires uploaded code examples to be studied, not only papers. Stage 3C inspected the uploaded `gdverse` and GD source, especially:

- `R/gd_optunidisc.R`;
- `R/opgd.R`;
- `R/sesu_opgd.R`;
- `R/robustdisc.R`;
- `R/rgd.R`;
- `R/rid.R`;
- `inst/python/cpd_disc.py`;
- package tests and vignettes.

No MSD implementation was found in those uploaded archives. The MSD primary paper reports Figshare DOI `10.6084/m9.figshare.13643318`, but the archive bytes were not retrievable in this development environment. Therefore the current implementation is paper-derived and independently validated, but author-code parity is not claimed.

Required future MSD validation:

1. retrieve and pin the Figshare article version and archive files;
2. record names, sizes, checksums, licence and runtime environment;
3. run the author example without modification;
4. compare candidate grids, neighbourhood mapping, boundary membership, ties, q and final cuts;
5. store a static fixture with provenance;
6. reproduce one published MSD case;
7. expose a compatibility mode only when a real, documented discrepancy exists.

## 5. Next active stage - robust detector family

Stage 4 must begin with source and formula audit, not immediate API creation.

Mandatory references:

- uploaded `Robust_Geographical_Detector` Python/notebook archive;
- uploaded `gdverse` files `R/robustdisc.R`, `R/rgd.R`, `R/rid.R` and `inst/python/cpd_disc.py`;
- RGD and RID primary papers;
- any bundled examples, tests and data licences.

Freeze before coding:

1. sorted/ranked sample representation;
2. variance change-point objective and segment cost;
3. dynamic-programming recursion and backtracking;
4. minimum segment size and requested/selected change-point count;
5. candidate pruning and computational complexity;
6. exact B-value formula and inference/reporting meaning;
7. RGD factor workflow and RID interaction workflow boundaries;
8. missing data, ties, duplicate `x`, constant segments and outlier contracts;
9. independent brute-force fixtures for small problems;
10. perturbation/outlier simulations and author/reference static fixtures.

Do not reuse MSD result types merely because both methods search ordered cut points. Robust discretization needs its own estimator and audit objects.

## 6. Known validation gaps

- Stage 3A: stable external fixtures for all six stratification methods and a published OPGD case.
- Stage 3B: static paper/GD scale fixture, a published multi-scale OPGD case, and pinned gdverse LOESS evidence.
- Stage 3C: Figshare author-code fixture and published MSD case.
- Model-selection optimism and stability under resampling remain future work.

Until these are completed, Stage 3A-3C remain “implemented, provisional”.

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
- status, validation, changelog, inventory, roadmap and this handoff match the code;
- uploaded/reference source use and licence boundaries are documented;
- disagreements among paper, author code, GD and gdverse remain explicit;
- no method is marked externally validated without the required fixture and case evidence.
