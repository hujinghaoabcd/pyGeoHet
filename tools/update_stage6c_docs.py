"""Synchronize Stage 6C evidence-gate records once, then remove this file."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text, encoding="utf-8")


def update_readme() -> None:
    path = "README.md"
    text = read(path)
    old = (
        "> **Status - Stage 6B implemented:** classical GeoDetector, OPGD, "
        "spatial-scale comparison, MSD, RGD/RID, SPADE, IDSA, paper-aligned "
        "SRS-GD, nominal IN-SSH and continuous IC-SSH are available. Stage 6C "
        "SWMI remains evidence-gated."
    )
    new = (
        "> **Status - Stage 6B implemented:** classical GeoDetector, OPGD, "
        "spatial-scale comparison, MSD, RGD/RID, SPADE, IDSA, paper-aligned "
        "SRS-GD, nominal IN-SSH and continuous IC-SSH are available. The Stage "
        "6C SWMI evidence audit is complete and implementation remains blocked; "
        "Stage 7A GOZH is the next active batch."
    )
    if old in text:
        text = text.replace(old, new, 1)
    link = (
        "- [`docs/references/swmi-evidence-audit.md`]"
        "(docs/references/swmi-evidence-audit.md)"
    )
    if link not in text:
        marker = (
            "- [`docs/references/stage6-information-ssh-audit.md`]"
            "(docs/references/stage6-information-ssh-audit.md)"
        )
        if marker not in text:
            raise RuntimeError("Stage 6 audit link not found in README")
        text = text.replace(marker, marker + "\n" + link, 1)
    write(path, text)


def update_inventory() -> None:
    path = "MODEL_INVENTORY.md"
    lines = read(path).splitlines()
    replaced = False
    for index, line in enumerate(lines):
        if line.startswith("| Spatial information | SWMI |"):
            lines[index] = (
                "| Spatial information | SWMI | spatial-autocorrelation-adjusted "
                "probability and mutual information | 2026 primary paper metadata "
                "and abstract; no complete equations/code fixture pinned | evidence "
                "audit complete; implementation blocked and no API | 6C |"
            )
            replaced = True
            break
    if not replaced:
        raise RuntimeError("SWMI inventory row not found")
    write(path, "\n".join(lines) + "\n")


def update_validation() -> None:
    path = "VALIDATION_MATRIX.md"
    text = read(path)
    row = (
        "| SWMI evidence gate | official metadata, abstract and workflow claims "
        "audited | no authoritative code or static output found | formula, support, "
        "discretization and inference contracts unresolved | publisher cases not "
        "numerically reproducible | blocked; no implementation |"
    )
    marker = "| InformationConsistency workflow |"
    if row not in text:
        lines = text.splitlines()
        insert_at = None
        for index, line in enumerate(lines):
            if line.startswith(marker):
                insert_at = index + 1
                break
        if insert_at is None:
            raise RuntimeError("InformationConsistency validation row not found")
        lines.insert(insert_at, row)
        text = "\n".join(lines) + "\n"
    section = """
## Stage 6C SWMI evidence-gate result

The official source confirms only a workflow of variable discretization, spatial-autocorrelation-based probability adjustment, and entropy/mutual-information calculation. The audit could not pin the exact adjustment, spatial support, discretization search, normalized score, multivariable grouping, interaction or null procedure.

No authoritative repository, supplementary archive or machine-readable numerical output was found by exact title, DOI, PII, acronym and author searches. The publisher states that data are available on request. A secondary summary and figure captions are not a numerical oracle.

Consequently:

- analytical validation cannot be defined without inventing equations;
- cross-language/static validation has no source output;
- simulation targets cannot be tied to the published estimand;
- the NO2 and vegetation cases cannot yet be reproduced;
- no code, API placeholder or version bump is allowed.

The complete reopening checklist is in `docs/references/swmi-evidence-audit.md`.
"""
    if "## Stage 6C SWMI evidence-gate result" not in text:
        text = text.rstrip() + "\n\n" + section.strip() + "\n"
    write(path, text)


def update_decisions() -> None:
    path = "DECISIONS.md"
    text = read(path)
    addition = """

## D060 - SWMI remains blocked without its probability-adjustment equation

The accessible 2026 source confirms a high-level sequence but does not expose the exact spatial-autocorrelation probability adjustment. Ordinary mutual information, normalized mutual information, entropograms, medical-image SWMI, q, SRS-GD, PSD, PID and IC/IN-SSH are not substitutes.

## D061 - Evidence-gated methods receive no public placeholders

A blocked method has no empty module, class, function, result type, import or version bump. Its evidence audit belongs in documentation until a complete estimand, boundary contract and numerical oracle are pinned.

## D062 - SWMI reopening requires equations and numerical provenance

Implementation requires the full primary equations, spatial-support and discretization contracts, adjusted marginal and joint probabilities, score normalization, multivariable grouping, inference procedure, one manual oracle and one author/publisher numerical output with version, licence and checksum provenance.

## D063 - Stage 7 is separated into GOZH, contribution and OMGD batches

GOZH zone optimization, LESH/Shapley contribution allocation and OMGD multivariate stratification/scale are different estimands and search problems. They are audited and implemented in separate batches; a shared multivariate label does not justify a combined optimizer or result type.
"""
    if "## D060 - SWMI remains blocked" not in text:
        text = text.rstrip() + addition + "\n"
    write(path, text)


def update_changelog() -> None:
    path = "CHANGELOG.md"
    text = read(path)
    entry = """## Unreleased - Stage 6C evidence audit

### Added

- a dedicated SWMI evidence-gate audit with known facts, unresolved equations, search record, implementation gate and reopening procedure;
- an explicit Stage 7A/7B/7C split for GOZH, LESH/Shapley and OMGD.

### Changed

- SWMI is recorded as implementation-blocked rather than merely planned;
- no SWMI code, placeholder API or version change is introduced;
- Stage 7A GOZH evidence and numerical-contract review becomes the next active batch.

"""
    if "## Unreleased - Stage 6C evidence audit" not in text:
        header = "# Changelog\n\n"
        if not text.startswith(header):
            raise RuntimeError("unexpected changelog header")
        text = header + entry + text[len(header) :]
    write(path, text)


def update_notices() -> None:
    path = "THIRD_PARTY_NOTICES.md"
    text = read(path)
    old = (
        "The 2026 SWMI paper is recent and no authoritative executable reference "
        "has yet been pinned. No SWMI code or API will be introduced until the "
        "complete probability-weighting equations, null procedure and at least one "
        "independent numerical output are available."
    )
    new = (
        "The 2026 SWMI evidence audit found accessible official metadata, "
        "highlights and an abstract, but not the complete probability-adjustment "
        "equations, executable reference, supplement or numerical fixture. The "
        "publisher states that data are available on request. No SWMI code or API "
        "is introduced. Reopening requires complete equations, licence/provenance "
        "records and at least one independent numerical output. See "
        "`docs/references/swmi-evidence-audit.md`."
    )
    if old in text:
        text = text.replace(old, new, 1)
    elif new not in text:
        raise RuntimeError("SWMI notice paragraph not found")
    write(path, text)


def update_handoff() -> None:
    write(
        "HANDOFF_NEXT_CONVERSATION.md",
        """# HANDOFF - pyGeoHet Stage 6C evidence-gate baseline

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
""",
    )


def main() -> None:
    update_readme()
    update_inventory()
    update_validation()
    update_decisions()
    update_changelog()
    update_notices()
    update_handoff()


if __name__ == "__main__":
    main()
