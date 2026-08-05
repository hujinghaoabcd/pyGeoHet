
# HANDOFF - pyGeoHet Stage 5B baseline

Date: 2026-08-05

## 1. Authoritative continuation source

After PR #8 is merged, fetch the latest `main` branch of `hujinghaoabcd/pyGeoHet`. Do not reconstruct Stage 5B from chat text or old ZIP archives.

Read in order:

1. `HANDOFF_NEXT_CONVERSATION.md`;
2. `PROJECT_STATUS.md`;
3. `DECISIONS.md`;
4. `docs/models/spade.md`;
5. `docs/models/idsa.md`;
6. `docs/references/spade-idsa-code-audit.md`;
7. `docs/references/idsa-code-audit.md`;
8. `VALIDATION_MATRIX.md`;
9. `ROADMAP.md`;
10. `MODEL_INVENTORY.md`.

## 2. Completed Stage 5B baseline

Version `0.0.8` adds:

- `FuzzyRiskLevel`, `FuzzyOverlayResult` and `fuzzy_overlay()`;
- collision-safe `(factor, stratum)` zone identities;
- fuzzy AND/OR with explicit first/last ties;
- `InteractiveSpatialDeterminantResult` and `power_interactive_determinant()`;
- canonical ordinal class encoding;
- theta, phi and PID component evidence;
- response-permutation inference that rebuilds fuzzy zones;
- `SpatialDiscretizationCandidate`, `SpatialDiscretizationOptimizationResult` and `optimize_spatial_discretization()`;
- maximum-CPSD continuous-factor selection;
- `IDSA`, `idsa`, `IDSACombinationResult` and `IDSAResult`;
- greedy and bounded exhaustive subset search;
- full analytical, missing-data, invariance and integration tests;
- public example, model manual and source audit.

## 3. Non-negotiable decisions

- IDSA fuzzy zones are not Cartesian intersections.
- Membership normalization is global across all factor-stratum response means.
- Zone identities are tuples, not concatenated strings.
- Constant risk is undefined rather than silently set to zero.
- Fixed PID factors are ordered discretizations and are canonically encoded.
- Theta is response PSD; phi retains individual-factor spatial information; PID is theta/phi.
- Zero phi and invalid fuzzy zones are explicit failures.
- Response-derived overlays are recomputed under permutation.
- Continuous candidates use maximum CPSD until a pinned compatibility selector exists.
- Greedy and exhaustive searches retain every attempted combination.
- External R sources remain reference-only.

## 4. Validation debt

- pin gdverse and sdsfun versions and source hashes;
- create a static fuzzy membership/zone fixture;
- create external theta, phi and PID fixtures;
- compare maximum-CPSD with the reference LOESS selector;
- reproduce a published IDSA application;
- test weight, discretization and subset-selection sensitivity;
- develop selection-adjusted uncertainty rather than overinterpreting the current conditional p value.

## 5. Next active stage - Stage 6

Audit SRS-GD, SSHIC/SSHIN and SWMI before coding. Freeze:

- nominal-response and rough-set estimands;
- spatial neighbourhood and indiscernibility relations;
- continuous and nominal information-consistency formulas;
- SWMI weight normalization and significance tests;
- missing categories, unseen levels and degenerate neighbourhoods;
- immutable evidence and external fixtures;
- boundaries separating information methods from q, PSD and PID.

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
python examples/05_multiscale_discretization.py
python examples/06_robust_detectors.py
python examples/07_spade.py
python examples/08_idsa.py
python -m build
```

All status, validation, changelog, inventory, roadmap, structure and handoff files must match the code before merge.
