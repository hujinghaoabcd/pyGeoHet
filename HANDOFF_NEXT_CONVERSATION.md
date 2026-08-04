# HANDOFF - pyGeoHet Stage 2 baseline

Date: 2026-08-05

## 1. Authoritative continuation source

After the Stage 2 pull request is merged, the current `main` branch of `hujinghaoabcd/pyGeoHet` is the only authoritative baseline. A new conversation must fetch the latest `main` commit SHA before editing. Do not reconstruct Stage 2 from chat text, old ZIP archives, or the superseded pyGeoDetectorX blueprint.

Read in this order:

1. `HANDOFF_NEXT_CONVERSATION.md`;
2. `PROJECT_STATUS.md`;
3. `DECISIONS.md`;
4. `docs/theory/numerical-conventions.md`;
5. `VALIDATION_MATRIX.md`;
6. `ROADMAP.md`;
7. `docs/models/classic-detectors.md`.

## 2. Stage 2 completed work

- q and factor detector retained from Stage 1;
- tuple-based categorical overlay;
- five interaction categories with explicit tolerances;
- interaction q values calculated on one joint complete-case sample;
- original-factor minimum size 2 and explicit overlay minimum size 1;
- risk detector with manual Welch-Satterthwaite inference;
- ecological F ratio with `two-sided` primary and `greater` compatibility modes;
- complete `GeoDetector` workflow and immutable result hierarchy;
- NTD fixture, validator and published-case report;
- expanded tests, example, English/Chinese README and model documentation.

## 3. Non-negotiable decisions

- direct centered sums of squares for q;
- no silent factor-stratum removal or imputation;
- singleton overlay cells may be retained only through the explicit `min_overlay_size` policy;
- tuple overlay labels, never concatenated strings;
- interaction and ecological pair calculations use joint complete cases;
- risk inference is two-sided Welch;
- ecological inference always records its selected alternative;
- planned methods are not exposed as empty APIs;
- external implementations are reference-only and never runtime dependencies;
- status, validation, changelog and handoff updates are merge gates.

## 4. Stage 3 objective

Implement stratification and optimal discretization without building a large abstraction framework.

Recommended order:

1. define `StratificationResult` with labels, ordered cut points, requested and actual strata, counts, rejected/merged information and method metadata;
2. create one small `stratify(values, method=..., n_strata=...)` protocol;
3. implement equal interval and quantile with duplicate-edge handling;
4. implement natural breaks independently and validate against a static reference;
5. implement geometric interval and standard-deviation classification;
6. implement head/tail breaks for heavy-tailed inputs;
7. add `evaluate_stratification(y, labels)` returning q plus candidate audit fields;
8. implement optimal univariate candidate search with deterministic tie rules;
9. add OPGD method/class-count search and only then add scale search;
10. verify MSD primary-source definitions before implementing supervised cut search.

## 5. Stage 3 design constraints

- keep discretization separate from q calculation;
- no method may return only the winning q; retain the complete candidate table;
- record duplicate cut points, collapsed strata, minimum stratum size and rejection reasons;
- distinguish unsupervised from response-supervised stratification in APIs and docs;
- deterministic tie-breaking must be documented before coding OPGD;
- avoid scikit-learn unless a method genuinely requires it;
- do not create robust, spatial, information or multivariate directories during Stage 3.

## 6. Required checks

```bash
python -m pip install -e ".[test]"
pytest --cov=pygeohet --cov-report=term-missing
python examples/01_factor_detector.py
python examples/02_classic_workflow.py
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
