
# HANDOFF - pyGeoHet Stage 6A baseline

Date: 2026-08-05

## 1. Authoritative continuation source

After PR #9 is merged, fetch the latest `main` branch of `hujinghaoabcd/pyGeoHet`. Begin Stage 6B from a new branch based on merged `main`. Do not reconstruct SRS-GD from chat messages, old ZIP archives or ambiguous reference C++ behaviour.

Read in order:

1. `HANDOFF_NEXT_CONVERSATION.md`;
2. `PROJECT_STATUS.md`;
3. `DECISIONS.md`;
4. `docs/models/srsgd.md`;
5. `docs/references/stage6-information-ssh-audit.md`;
6. `VALIDATION_MATRIX.md`;
7. `MODEL_INVENTORY.md`;
8. `ROADMAP.md`;
9. `THIRD_PARTY_NOTICES.md`;
10. `PROJECT_STRUCTURE.md`.

## 2. Completed Stage 6A baseline

Version `0.0.9` adds:

- `SpatialRoughSetResult` and immutable detector-comparison results;
- `spatial_rough_set_measure()`;
- `srs_factor_detector()`;
- `srs_ecological_detector()`;
- `srs_interaction_detector()`;
- `SRSGeoDetector` / `srsgd`;
- prepared binary adjacency validation;
- focal-object local regions;
- exact tuple indiscernibility;
- local positive regions and approximation quality;
- average local explanatory power `D`;
- spatial entropy `SE` and normalized entropy;
- paired common-location inference and seeded subsampling;
- explicit islands, symmetry, missing-data and discrete-input contracts;
- Figure 1 hand-calculated fixture and public example;
- model manual, Stage 6 source audit and top-level API protection.

## 3. Non-negotiable SRS-GD decisions

- SRS-GD is for nominal or deliberately discretized targets and factors.
- It is not q calculated on category codes.
- Every local region contains the focal object exactly once.
- Input diagonal values do not alter the estimand.
- Symmetric binary adjacency is the primary contract.
- Islands are rejected by default because self-only regions have quality one.
- Multifeature indiscernibility means equality on every feature.
- Local positive regions contain only decision-consistent equivalence classes.
- No-positive-region quality is zero.
- `D` is mean local quality.
- `SE` measures evenness; larger `SE` means lower spatial heterogeneity.
- All-zero local quality makes `SE` undefined.
- Ecological and interaction comparisons are paired on common focal objects.
- One complete-case mask removes both adjacency axes.
- The paper estimand outranks ambiguous gdverse C++ operations.
- Geometry-to-adjacency construction remains upstream.

## 4. Stage 6A validation evidence

The Bai et al. (2022) Figure 1 table and adjacency matrix are transcribed into `tests/test_srsgd.py`.

For `a1`:

```text
local quality = (0.5, 0.0, 1.0, 0.6, 0.625, 1.0, 1.0,
                 1/3, 1.0, 1.0, 1.0)
D             = 0.7325757575757575
SE            = 3.245554302578003
```

For `{a1,a2}`:

```text
D  = 0.8143939393939393
SE = 3.3720204818904733
```

Tests cover positive-region sizes, exact refinement monotonicity, diagonal invariance, simultaneous row/adjacency permutation, islands, missing-axis alignment, continuous-input rejection, directed-matrix opt-in, seeded sampling and integrated workflows.

Final PR #9 CI passed on Ubuntu, Windows and macOS with Python 3.11, 3.12 and 3.13. Ruff, Black, mypy, all nine examples, wheel build and source-distribution build passed.

## 5. Stage 6A validation debt

- pin the uploaded gdverse SRS input and output table with source/version hashes;
- quantify all paper-versus-source discrepancies in a compatibility report;
- reproduce the Baltimore crime case;
- reproduce the Cincinnati land-cover case;
- add larger nominal null, perfect and noisy simulations;
- test neighbourhood-construction sensitivity outside the core;
- develop inference accounting for overlap and spatial dependence among local regions;
- add sparse adjacency only after its input and output contracts are fixed.

## 6. Next active batch - Stage 6B

Implement information-consistency SSH in two independent estimators.

### Nominal IN-SSH

Use

```text
IN = I(target; strata) / H(target)
   = 1 - H(target | strata) / H(target)
```

Freeze category factorization, constant-target failure, common-sample handling, natural-log/base-2 reporting and corrected pseudo-p values `(1 + exceedances) / (B + 1)`.

### Continuous IC-SSH

Use the stratum-weighted arctangent transform of relative entropy:

```text
IC = sum_h p_h * atan(KL(f_h || f_global)) / (pi / 2)
```

Freeze common histogram support, shared bin edges, bin-selection methods, zero-density masking or smoothing, minimum stratum size, constant response handling and sensitivity tables before implementation.

### External evidence

The maintained `stscl/sshicm` source was audited at commit `76b6c2879353716f2632c4f5cbb13bef3f6c8305`. Create static external candidate tables; never call R or the reference package at runtime.

SWMI remains Stage 6C and must not be implemented from an abstract or partial formula.

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
python examples/07_spade.py
python examples/08_idsa.py
python examples/09_srsgd.py
python -m build
```

All status, validation, changelog, inventory, roadmap, structure, notices and handoff files must match the code before merge.
