# HANDOFF - pyGeoHet Stage 6C evidence-gate baseline

Date: 2026-08-05

## 1. Authoritative continuation source

After the Stage 6C documentation PR is merged, fetch the latest `main` branch of `hujinghaoabcd/pyGeoHet`. Do not reconstruct SWMI or GOZH from chat messages, search snippets or neighbouring model names.

Read in order:

1. `HANDOFF_NEXT_CONVERSATION.md`;
2. `PROJECT_STATUS.md`;
3. `DECISIONS.md`;
4. `docs/references/swmi-evidence-audit.md`;
5. `docs/references/stage6-information-ssh-audit.md`;
6. `VALIDATION_MATRIX.md`;
7. `MODEL_INVENTORY.md`;
8. `ROADMAP.md`;
9. `THIRD_PARTY_NOTICES.md`;
10. `PROJECT_STRUCTURE.md`.

## 2. Stable implementation baseline

Version `0.0.10` contains the completed Stage 6B implementation:

- nominal IN-SSH;
- continuous IC-SSH;
- shared-support histogram contracts;
- corrected seeded permutations;
- common-sample multi-factor workflows;
- immutable evidence and ten public examples.

The final Stage 6B CI passed on Ubuntu, Windows and macOS with Python 3.11, 3.12 and 3.13, plus Ruff, Black, mypy, all examples, wheel and sdist builds. Merge commit: `6e9a96368f9b1421045fbb6a6fda7c5d37859980`.

## 3. Stage 6C audit conclusion

The official 2026 SWMI source supports only this high-level sequence:

1. discretize geographical variables;
2. adjust probabilities with spatial-autocorrelation strength;
3. calculate entropy and mutual information from adjusted probabilities.

The complete paper equations, author code, supplement and numerical fixture are not pinned. The exact probability adjustment, spatial support, discretization, score normalization, multivariable grouping, interaction and inference procedures remain unknown.

Therefore there is deliberately no:

- `swmi()`;
- `SWMI` class;
- result placeholder;
- package export;
- empty module;
- inferred formula;
- version bump.

Do not replace the missing method with ordinary mutual information, the entropogram, medical-image SWMI, q, SRS-GD, PSD, PID or IC/IN-SSH.

## 4. SWMI reopening gate

Require all of the following before code:

- complete primary equations;
- exact probability adjustment;
- spatial-weight and neighbourhood contract;
- discretization and group-selection algorithm;
- score normalization and boundary cases;
- inference or resampling procedure;
- one hand-calculable example;
- one author/publisher numerical output;
- code/data provenance, licence and checksums.

## 5. Next active batch - Stage 7A GOZH audit

Audit the Geographically Optimal Zones-based Heterogeneity model independently of LESH/Shapley and OMGD.

Required questions:

- What is the initial geographical partition?
- Which merge, split, reassignment or search moves are admissible?
- What objective is optimized at each step?
- How are minimum zone size and finely divided zones controlled?
- What is the stopping rule?
- Are individual and interactive determinants calculated globally or per optimized zone?
- How are spatial support, neighbourhood and scale represented?
- How are ties and failed candidates retained?
- What is the computational complexity and search budget?
- Which author/reference implementation and licence can be pinned?
- Which published table can serve as a static fixture?

Do not start implementation until a symbol table, pseudocode, boundary table and at least one manual/numerical oracle exist.

## 6. Later Stage 7 batches

- Stage 7B: LESH/Shapley coalition values and contribution allocation.
- Stage 7C: OMGD multivariate stratification and spatial-scale search.

A common “multivariate” label does not make these methods one estimand.

## 7. Required checks for the evidence-gate PR

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

Every merge leaves status, validation, changelog, inventory, roadmap, decisions, notices and handoff documents consistent with the code and evidence state.
