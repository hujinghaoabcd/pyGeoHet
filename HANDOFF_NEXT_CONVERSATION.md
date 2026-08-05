# HANDOFF - pyGeoHet Stage 6B baseline

Date: 2026-08-05

## 1. Authoritative continuation source

After PR #10 is merged, fetch the latest `main` branch of `hujinghaoabcd/pyGeoHet`. Do not reconstruct information consistency from chat messages, old ZIP archives or neighbouring entropy methods.

Read in order:

1. `HANDOFF_NEXT_CONVERSATION.md`;
2. `PROJECT_STATUS.md`;
3. `DECISIONS.md`;
4. `docs/models/information-consistency.md`;
5. `docs/references/stage6-information-ssh-audit.md`;
6. `VALIDATION_MATRIX.md`;
7. `MODEL_INVENTORY.md`;
8. `ROADMAP.md`;
9. `THIRD_PARTY_NOTICES.md`;
10. `PROJECT_STRUCTURE.md`.

## 2. Completed Stage 6B baseline

Version `0.0.10` adds:

- `nominal_information_consistency()`;
- `continuous_information_consistency()`;
- `InformationConsistency` and `information_consistency()`;
- immutable nominal contingency and entropy evidence;
- immutable continuous histogram and KL-contribution evidence;
- common-sample multi-factor results;
- Sturges, square-root, Rice, Scott and Freedman-Diaconis bin rules;
- explicit integer and custom-edge support;
- corrected seeded permutation inference;
- ten public examples and top-level API protection;
- analytical, invariance, missing-data, support and failure tests;
- model manual and expanded Stage 6 evidence audit.

## 3. Non-negotiable Stage 6B decisions

- IN-SSH and IC-SSH are separate from q, SRS-GD, PSD and PID.
- `IN = I(Y;S) / H(Y)` with one logarithm convention.
- a constant nominal target makes IN undefined.
- `IC = sum_h p_h * atan(KL(P_h || P)) / (pi/2)`.
- global and stratum continuous histograms use one shared support and edge sequence.
- explicit edges must cover the complete target.
- zero stratum-probability KL terms are omitted without pseudocount smoothing.
- the target is permuted relative to fixed supplied strata.
- continuous permutation keeps the observed edges fixed.
- pseudo-p values use `(1 + exceedances) / (B + 1)`.
- all factors in one workflow use one joint complete-case sample.
- no external R/C++ implementation is invoked at runtime.

## 4. Validation evidence

Nominal fixtures cover:

```text
perfect consistency: IN = 1
independence:        IN = 0
partial table:       IN = 1 - 0.75 * H_binary(2/3) / log(2)
```

Continuous fixtures cover:

```text
separated two-bin strata: KL_h = log(2)
IC = atan(log(2)) / (pi/2)
identical distributions: IC = 0
```

Tests also cover label relabeling, affine target transformation, five automatic bin methods, explicit edges, small strata, constant targets, fixed-edge seeded permutations, corrected p-value bounds, one joint missing-data sample and public exports.

The implementation CI passed across Ubuntu, Windows and macOS with Python 3.11, 3.12 and 3.13 before final documentation cleanup. The final clean branch must pass Ruff, Black, mypy, all ten examples, wheel and sdist builds before merge.

## 5. Validation debt

- pin static `stscl/sshicm` candidate and final-output tables;
- record exact build metadata, input hashes and tolerances;
- reproduce a published information-consistency application;
- add larger null and power simulations;
- quantify histogram-method and bin-count sensitivity;
- study spatial-dependence-aware and selection-aware inference.

## 6. Next stage decision

### Stage 6C - SWMI evidence gate

Do not implement SWMI from an abstract, secondary summary or partial formula. Proceed only after pinning:

- the complete probability adjustment;
- entropy and mutual-information equations;
- spatial-weight and discretization contracts;
- interaction and null procedures;
- at least one independent numerical output.

If those requirements cannot be met, record the evidence gap and move to Stage 7 without creating a provisional SWMI public name.

### Stage 7A - GOZH audit

The first implementable Stage 7 batch should audit GOZH zone optimization, stopping/merging rules, factor and interaction outputs, search complexity and external fixtures. Keep GOZH, LESH/Shapley and OMGD as separate numerical contracts.

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
python examples/10_information_consistency.py
python -m build
```

Every merge must leave status, validation, changelog, inventory, roadmap, structure, notices and handoff documents consistent with the code.
