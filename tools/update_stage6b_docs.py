"""One-time Stage 6B documentation synchronization. Remove after execution."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text, encoding="utf-8")


def replace_required(text: str, old: str, new: str, *, path: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise RuntimeError(f"required block not found in {path}: {old[:80]!r}")
    return text.replace(old, new, 1)


def update_readme() -> None:
    path = "README.md"
    text = read(path)
    text = replace_required(
        text,
        "> **Status - Stage 6A implemented:** classical GeoDetector, OPGD, spatial-scale comparison, MSD, RGD/RID, SPADE, IDSA and paper-aligned SRS-GD are available. Stage 6B will add nominal and continuous information-consistency SSH; SWMI remains evidence-gated.",
        "> **Status - Stage 6B implemented:** classical GeoDetector, OPGD, spatial-scale comparison, MSD, RGD/RID, SPADE, IDSA, paper-aligned SRS-GD, nominal IN-SSH and continuous IC-SSH are available. Stage 6C SWMI remains evidence-gated.",
        path=path,
    )
    marker = "\n\n## Public interfaces\n"
    section = """

## Information-consistency SSH

Stage 6B adds two distributional SSH estimators that remain separate from variance-based q and local rough-set SRS-GD.

```python
import pandas as pd
from pygeohet import (
    InformationConsistency,
    continuous_information_consistency,
    nominal_information_consistency,
)

nominal = nominal_information_consistency(
    nominal_target,
    nominal_strata,
    permutations=999,
    random_state=42,
)
print(nominal.contingency_frame())

continuous = continuous_information_consistency(
    continuous_target,
    continuous_strata,
    bins="sturges",
    permutations=999,
    random_state=42,
)
print(continuous.contributions_frame())
print(continuous.histogram_frame())

workflow = InformationConsistency(
    target_kind="continuous",
    bins="sturges",
).fit(continuous_target, factor_frame)
print(workflow.to_frame())
```

Nominal `IN = I(Y;S) / H(Y)`. Continuous `IC` is the stratum-share-weighted `atan(KL(P_h || P)) / (pi/2)`. All entropy terms use natural logarithms consistently. Continuous strata and the global target use one common histogram support and shared edges. Permutation inference shuffles the target relative to fixed strata and uses `(1 + exceedances) / (B + 1)`.
"""
    if "## Information-consistency SSH" not in text:
        if marker not in text:
            raise RuntimeError("README public-interface marker not found")
        text = text.replace(marker, section + marker, 1)
    text = replace_required(
        text,
        "    SRSGeoDetector,\n    q_statistic,",
        "    SRSGeoDetector,\n    InformationConsistency,\n    q_statistic,",
        path=path,
    )
    text = replace_required(
        text,
        "    srs_interaction_detector,\n    stratify,",
        "    srs_interaction_detector,\n    nominal_information_consistency,\n    continuous_information_consistency,\n    information_consistency,\n    stratify,",
        path=path,
    )
    text = replace_required(
        text,
        "- adjacency symmetry, focal-object inclusion and islands are never silently inferred;\n- model-complexity selection is explicit rather than hidden inside numerical kernels;",
        "- adjacency symmetry, focal-object inclusion and islands are never silently inferred;\n- nominal information consistency retains entropy and contingency evidence;\n- continuous information consistency uses one shared histogram support and edge sequence;\n- information-consistency permutations use fixed supplied strata and corrected pseudo-p values;\n- model-complexity selection is explicit rather than hidden inside numerical kernels;",
        path=path,
    )
    text = replace_required(
        text,
        "Stage 5A has hand-computed spatial-variance tests and an externally checked categorical NTD PSD path. Stage 5B adds manual fuzzy memberships, direct theta/phi decomposition and auditable IDSA search. Stage 6A reproduces the SRS-GD paper Figure 1 local qualities, `D` and `SE`, verifies exact tuple-refinement monotonicity, and tests adjacency permutation, islands, missing axes and discrete-input guards. SRS-GD remains implemented and provisional until published Baltimore/Cincinnati reproductions and a pinned compatibility table are complete.",
        "Stage 5A has hand-computed spatial-variance tests and an externally checked categorical NTD PSD path. Stage 5B adds manual fuzzy memberships, direct theta/phi decomposition and auditable IDSA search. Stage 6A reproduces the SRS-GD paper Figure 1 local qualities, `D` and `SE`, verifies exact tuple-refinement monotonicity, and tests adjacency permutation, islands, missing axes and discrete-input guards. Stage 6B adds hand-computed nominal entropy/MI and continuous KL examples, perfect and null extremes, label and affine invariance, shared-edge checks, five automatic histogram rules, seeded fixed-edge permutations, common-sample workflows and explicit failure contracts. SRS-GD and information consistency remain implemented and provisional until their published/static external reproductions are complete.",
        path=path,
    )
    text = replace_required(
        text,
        "- [`docs/models/srsgd.md`](docs/models/srsgd.md)\n- [`docs/references/stage6-information-ssh-audit.md`](docs/references/stage6-information-ssh-audit.md)",
        "- [`docs/models/srsgd.md`](docs/models/srsgd.md)\n- [`docs/models/information-consistency.md`](docs/models/information-consistency.md)\n- [`docs/references/stage6-information-ssh-audit.md`](docs/references/stage6-information-ssh-audit.md)",
        path=path,
    )
    write(path, text)


def update_roadmap() -> None:
    path = "ROADMAP.md"
    text = read(path)
    text = replace_required(
        text,
        "**Status:** next active batch after PR #9 merge.",
        "**Status:** implementation and full cross-platform CI complete in PR #10. Hand-calculated nominal and continuous fixtures, shared-edge contracts, corrected seeded permutations, common-sample workflows, public exports and the model manual are complete. Static `sshicm` candidate tables and a published-case reproduction remain validation debt.",
        path=path,
    )
    write(path, text)


def update_inventory() -> None:
    path = "MODEL_INVENTORY.md"
    text = read(path)
    text = replace_required(
        text,
        "| Information | SSHIC/SSHIN | distribution differences beyond variance | 2023 paper; pinned stscl/sshicm source | next active batch after formula and fixture freeze | 6B |",
        "| Information | IC-SSH / IN-SSH | continuous and nominal distribution consistency across strata | 2023 paper; pinned stscl/sshicm source | implemented with shared-support histograms, normalized MI and corrected permutations; external fixture pending | 6B |",
        path=path,
    )
    text = replace_required(
        text,
        "and Stage 6 separation between the published SRS-GD estimand and ambiguous reference-source operations.",
        "and Stage 6 separation between the published SRS-GD estimand, information-consistency distributions and ambiguous reference-source operations.",
        path=path,
    )
    write(path, text)


def update_structure() -> None:
    path = "PROJECT_STRUCTURE.md"
    text = read(path)
    text = replace_required(
        text,
        "│   │   ├── srsgd_results.py     immutable local rough-set evidence\n│   │   └── srsgd.py             SRS factor, ecological and interaction workflows",
        "│   │   ├── srsgd_results.py     immutable local rough-set evidence\n│   │   ├── srsgd.py             SRS factor, ecological and interaction workflows\n│   │   ├── information_results.py immutable entropy, KL and workflow evidence\n│   │   └── information.py       nominal IN-SSH and continuous IC-SSH",
        path=path,
    )
    text = replace_required(
        text,
        "│   ├── test_srsgd.py            Figure 1, adjacency and nominal-target tests\n│   ├── test_public_api.py",
        "│   ├── test_srsgd.py            Figure 1, adjacency and nominal-target tests\n│   ├── test_information.py      entropy, KL, histogram and workflow tests\n│   ├── test_public_api.py",
        path=path,
    )
    text = replace_required(
        text,
        "│   ├── 08_idsa.py\n│   └── 09_srsgd.py",
        "│   ├── 08_idsa.py\n│   ├── 09_srsgd.py\n│   └── 10_information_consistency.py",
        path=path,
    )
    text = replace_required(
        text,
        "Stage 6A adds SRS-GD as a dedicated nominal-target model family. It consumes a prepared binary adjacency matrix and does not reuse variance-based q, spatial PSD or fuzzy PID. Stage 6B information-consistency methods will remain in separate modules after their entropy and density contracts are frozen.",
        "Stage 6A adds SRS-GD as a dedicated nominal-target model family. It consumes a prepared binary adjacency matrix and does not reuse variance-based q, spatial PSD or fuzzy PID. Stage 6B adds separate information modules for nominal normalized mutual information and continuous shared-support relative entropy; these methods do not reuse q or SRS-GD internals.",
        path=path,
    )
    write(path, text)


def update_validation() -> None:
    path = "VALIDATION_MATRIX.md"
    text = read(path)
    row = "| SRS-GD | Figure 1 local quality, D and SE | paper/source audit; external compatibility table pending | tuple monotonicity, adjacency permutation, islands, missing axes and nominal guards | Baltimore/Cincinnati pending | implemented, provisional |"
    new_rows = row + "\n| Nominal IN-SSH | perfect/null extremes and hand contingency calculation | pinned `sshicm` source audited; static table pending | relabeling, constant target, missing scope and corrected seeded permutations | pending | implemented, provisional |\n| Continuous IC-SSH | fixed-bin `KL=log(2)` example and zero-divergence case | pinned `sshicm` source audited; static table pending | affine invariance, five bin methods, fixed-edge permutations, support and small-stratum failures | pending | implemented, provisional |\n| InformationConsistency workflow | scalar estimators composed on one joint sample | external multi-factor table pending | factor ordering, common missing mask and public API tests | pending | implemented, provisional |"
    text = replace_required(text, row, new_rows, path=path)
    section = """

## Stage 6B validation state and gaps

| Method | Analytical | Cross-language/static | Simulation/edge cases | Published case | Status |
|---|---:|---:|---:|---:|---|
| Nominal IN-SSH | `IN=1`, `IN=0`, and a hand-calculated partial table | `stscl/sshicm` commit pinned; static outputs pending | category relabeling, zero entropy, missing policy and corrected seeded permutations | pending | implemented, provisional |
| Continuous IC-SSH | separated fixed-bin strata with `KL=log(2)` and identical distributions with `IC=0` | histogram/relative-entropy source audited; static outputs pending | shared support, explicit edges, five automatic rules, affine invariance, small strata and fixed-edge permutations | pending | implemented, provisional |
| Multi-factor workflow | direct scalar/workflow equality on one joint sample | external candidate ranking pending | common complete cases, factor ordering and functional/class APIs | pending | implemented, provisional |

Stage 6B deliberately differs from the reviewed source where that source mixes logarithm bases, uses uncorrected `exceedances/B` p values or creates incompatible global and stratum histogram supports. Remaining work is to pin static candidate and final-output tables from the audited revision, reproduce a published application, add larger null/power simulations, and quantify sensitivity to histogram selection. No fully external-validation claim is made before those records exist.
"""
    if "## Stage 6B validation state and gaps" not in text:
        text = text.rstrip() + section + "\n"
    write(path, text)


def update_decisions() -> None:
    path = "DECISIONS.md"
    text = read(path)
    addition = """

## D055 - Nominal information consistency is normalized mutual information

`IN-SSH = I(Y;S) / H(Y) = 1 - H(Y|S) / H(Y)`. Natural logarithms are used consistently for target, conditional and mutual information terms. A constant target has zero entropy and makes the statistic undefined; it is not assigned zero or one.

## D056 - Continuous information consistency uses one shared histogram support

`IC-SSH = sum_h p_h * atan(KL(P_h || P)) / (pi/2)`. The global and every stratum histogram use one edge sequence resolved from the complete target. Stratum-specific supports are prohibited because their densities are not directly comparable.

## D057 - Information-consistency zero and bin rules are explicit

KL terms with zero stratum probability are omitted. Positive stratum mass must have positive global mass under the shared sample and edges. Automatic methods are Sturges, square root, Rice, Scott and Freedman-Diaconis; deterministic equal-width edges span the complete target range. Explicit edges must be finite, strictly increasing and cover the complete target.

## D058 - Information-consistency inference is conditional and corrected

Permutation inference shuffles the target relative to fixed supplied strata. Continuous permutations reuse the observed edge sequence. The pseudo-p value is `(1 + exceedances) / (B + 1)`. Inference is conditional on the supplied strata and bins and is not selection-adjusted for upstream discretization or factor search.

## D059 - Multi-factor information consistency uses one common sample

`InformationConsistency` applies one complete-case mask to the target and every supplied factor before evaluating factor-specific IN or IC values. This differs from independent factor-wise deletion and preserves direct comparability. The result retains common original indices and factor-specific decomposition evidence.
"""
    if "## D055 - Nominal information consistency" not in text:
        text = text.rstrip() + addition + "\n"
    write(path, text)


def update_changelog() -> None:
    path = "CHANGELOG.md"
    text = read(path)
    entry = """# Changelog

## 0.0.10 - 2026-08-05

### Added

- nominal `nominal_information_consistency()` using normalized mutual information;
- continuous `continuous_information_consistency()` using stratum-weighted arctangent-normalized KL divergence;
- shared global/stratum histogram support with Sturges, square-root, Rice, Scott and Freedman-Diaconis rules;
- explicit integer and edge-sequence histogram contracts;
- immutable contingency, entropy, histogram, KL-contribution and multi-factor result objects;
- `InformationConsistency` / `information_consistency()` common-sample workflows;
- corrected seeded permutation inference with fixed continuous edges;
- analytical perfect, null, partial contingency, `KL=log(2)` and zero-divergence tests;
- label and affine invariance, missing-scope, small-stratum, support and public API tests;
- tenth runnable example, model manual and expanded Stage 6 source audit.

### Changed

- package development version advanced to `0.0.10`;
- public API exports nominal, continuous and integrated information-consistency interfaces;
- CI runs ten public examples;
- entropy components use one natural-log convention rather than mixed bases;
- continuous density comparison uses one shared support rather than per-stratum supports;
- permutation p values use `(1 + exceedances) / (B + 1)`;
- Stage 6C SWMI remains evidence-gated and Stage 7 becomes the next implementable family after the evidence review.
"""
    if "## 0.0.10 - 2026-08-05" not in text:
        if not text.startswith("# Changelog\n"):
            raise RuntimeError("unexpected CHANGELOG header")
        text = entry + text[len("# Changelog\n") :]
    write(path, text)


def update_audit() -> None:
    path = "docs/references/stage6-information-ssh-audit.md"
    text = read(path)
    text = replace_required(
        text,
        "Important edge cases to freeze before coding:",
        "Frozen pyGeoHet contracts:",
        path=path,
    )
    text = replace_required(
        text,
        "Before implementation pyGeoHet must freeze:",
        "Frozen pyGeoHet contracts:",
        path=path,
    )
    text = replace_required(
        text,
        "No continuous IC-SSH code should be merged until direct hand calculations and a static `sshicm` candidate table are available.",
        "The implementation is supported by direct hand calculations. Static `sshicm` candidate and final-output tables remain external-validation debt and are not required at runtime.",
        path=path,
    )
    addition = """

## Stage 6B implemented contract

pyGeoHet independently implements:

- nominal `IN = I(target; strata) / H(target)` with natural logarithms used consistently;
- explicit zero-target-entropy failure;
- continuous `IC = sum_h p_h * atan(KL(P_h || P)) / (pi/2)`;
- one complete-target support and one shared bin edge sequence;
- Sturges, square-root, Rice, Scott and Freedman-Diaconis automatic counts;
- explicit equal-width integer counts and complete custom edge sequences;
- omission of zero stratum-probability KL terms without pseudocount smoothing;
- a common complete-case sample for multi-factor comparisons;
- target permutations relative to fixed strata and fixed continuous edges;
- corrected pseudo-p values `(1 + exceedances) / (B + 1)`;
- immutable contingency, histogram, contribution, sample and null evidence.

The reviewed source is not copied or called at runtime. pyGeoHet does not reproduce mixed entropy bases, uncorrected p values, or density comparisons built on incompatible supports.

## Stage 6B analytical fixtures

Nominal tests include perfect determination (`IN=1`), independence (`IN=0`) and a four-observation partial table with

```text
H(Y)     = log(2)
H(Y | S) = 0.75 * H_binary(2/3)
IN       = 1 - H(Y | S) / H(Y)
```

The continuous separated-strata fixture uses global probabilities `(0.5, 0.5)`. Each stratum has `KL=log(2)`, giving

```text
IC = atan(log(2)) / (pi/2)
```

Identical stratum distributions produce zero KL divergence and `IC=0`.

## Stage 6B remaining evidence debt

- generate static input, candidate and final-output tables from the pinned `stscl/sshicm` revision;
- record exact source/package build metadata and tolerances;
- reproduce at least one published application;
- add larger nominal and continuous null/power simulations;
- quantify histogram-method and bin-count sensitivity;
- examine permutation validity under spatial dependence and selected stratifications.
"""
    if "## Stage 6B implemented contract" not in text:
        text = text.rstrip() + addition + "\n"
    write(path, text)


def update_notices() -> None:
    path = "THIRD_PARTY_NOTICES.md"
    text = read(path)
    text = replace_required(
        text,
        "The IDSA source audit identified fuzzy response-risk membership zones that differ from classical tuple intersection. Stage 5B will implement those formulas independently with collision-safe labels and explicit tie rules. No provisional IDSA API is exported before that work is complete.",
        "The IDSA source audit identified fuzzy response-risk membership zones that differ from classical tuple intersection. Stage 5B implements those formulas independently with collision-safe labels, explicit tie rules and immutable evidence.",
        path=path,
    )
    text = replace_required(
        text,
        "Stage 6B evidence includes Bai et al. (2023), *Information Consistency-Based Measures for Spatial Stratified Heterogeneity*, and maintained `stscl/sshicm` source pinned during the audit to commit `76b6c2879353716f2632c4f5cbb13bef3f6c8305`. That source is used to verify formulas and future static outputs, not as a runtime backend.",
        "Stage 6B evidence includes Bai et al. (2023), *Information Consistency-Based Measures for Spatial Stratified Heterogeneity*, and maintained `stscl/sshicm` source pinned during the audit to commit `76b6c2879353716f2632c4f5cbb13bef3f6c8305`. That source is used to verify formulas and future static outputs, not as a runtime backend. pyGeoHet independently implements consistent natural-log entropy, shared-support histograms and corrected permutation p values rather than reproducing known source conventions mechanically.",
        path=path,
    )
    write(path, text)


def update_status() -> None:
    write(
        "PROJECT_STATUS.md",
        """# Project status

**Project:** pyGeoHet  
**Date:** 2026-08-05  
**Completed stage:** Stage 6B of 10 - information-consistency SSH  
**Next evidence gate:** Stage 6C - spatially weighted mutual information  
**Next implementable family if 6C evidence remains insufficient:** Stage 7 - multivariate stratification and contribution  
**Development version:** 0.0.10

## Completed

- package, immutable result, documentation, testing and cross-platform CI foundation;
- classical q and four-detector workflows;
- auditable univariate stratification, OPGD, spatial-scale comparison and MSD;
- robust change-point discretization, RGD and RID;
- prepared spatial variance, PSD, CPSD, PSMD and SPADE;
- fuzzy overlay, PID and IDSA;
- paper-aligned SRS-GD for nominal targets;
- nominal IN-SSH by normalized mutual information;
- continuous IC-SSH by stratum-weighted transformed KL divergence;
- one shared continuous histogram support and edge sequence;
- corrected seeded permutation inference;
- common complete-case multi-factor information workflow;
- immutable entropy, contingency, histogram, KL, sample and null evidence;
- ten public examples and top-level API regression protection.

## Stage 6B public surface

```python
from pygeohet import (
    InformationConsistency,
    ContinuousInformationConsistencyResult,
    InformationConsistencyFactorResult,
    NominalInformationConsistencyResult,
    continuous_information_consistency,
    information_consistency,
    nominal_information_consistency,
)
```

## Numerical contract

### Nominal

```text
IN = I(Y; S) / H(Y)
   = 1 - H(Y | S) / H(Y)
```

- natural logarithms are used consistently;
- category names do not affect the result;
- a constant target has zero entropy and is rejected;
- contingency probabilities and entropy components remain public evidence.

### Continuous

```text
IC = sum_h p_h * atan(KL(P_h || P)) / (pi / 2)
```

- the global target and every stratum use one shared support and edges;
- automatic methods are Sturges, square root, Rice, Scott and Freedman-Diaconis;
- explicit integer counts and edge sequences are supported;
- zero stratum-probability KL terms are omitted without smoothing;
- a positive stratum bin cannot have zero global mass under the shared sample.

### Inference and workflow

- the target is shuffled relative to fixed supplied strata;
- continuous permutations reuse the observed edge sequence;
- pseudo-p values use `(1 + exceedances) / (B + 1)`;
- all factors in one workflow use one joint complete-case sample;
- minimum strata and missing-data policies are explicit;
- no R, C++ reference package or competing implementation is called at runtime.

## Validation state

The Stage 6B suite includes perfect, null and hand-calculated partial nominal cases; category relabeling invariance; constant-target failure; a continuous fixed-bin `KL=log(2)` case; identical-distribution `IC=0`; affine invariance; five automatic histogram methods; explicit support failures; small-stratum failures; corrected seeded permutations; common-sample multi-factor ranking; and public API tests.

The first full Stage 6B implementation CI passed on Ubuntu, Windows and macOS with Python 3.11, 3.12 and 3.13. Ruff, Black and mypy passed after the explicit histogram-label type fix. The clean final CI must also pass with ten examples, wheel build and source-distribution build before PR #10 merge.

Stage 6B is **implemented, provisional**. Static outputs from the pinned `stscl/sshicm` revision, a published application reproduction, larger simulations and histogram-sensitivity analysis remain validation debt.

## Deliberately deferred

- automatic discretization of inputs for information consistency;
- selection-adjusted inference for searched factors or bins;
- spatial-dependence-adjusted permutation schemes;
- kernel density estimation or adaptive bins inside the core estimator;
- Stage 6C SWMI until full probability weighting, null procedure and numerical fixtures are verified;
- Stage 7 GOZH, LESH/Shapley and OMGD until Stage 6B is merged and their separate contracts are audited.

## Immediate next task

1. finish the clean PR #10 CI and merge Stage 6B;
2. audit the complete SWMI equations and search for an authoritative numerical reference;
3. if SWMI remains evidence-gated, begin Stage 7A with GOZH evidence and numerical-contract review rather than inventing a provisional SWMI API.
""",
    )


def update_handoff() -> None:
    write(
        "HANDOFF_NEXT_CONVERSATION.md",
        """# HANDOFF - pyGeoHet Stage 6B baseline

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
""",
    )


def main() -> None:
    update_readme()
    update_roadmap()
    update_inventory()
    update_structure()
    update_validation()
    update_decisions()
    update_changelog()
    update_audit()
    update_notices()
    update_status()
    update_handoff()


if __name__ == "__main__":
    main()
