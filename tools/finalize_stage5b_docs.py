"""One-time Stage 5B documentation finalizer; removed before merge."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text.rstrip() + "\n", encoding="utf-8")


def prepend_once(path: str, marker: str, section: str) -> None:
    text = read(path)
    if marker not in text:
        heading, rest = text.split("\n", 1)
        write(path, heading + "\n\n" + section.strip() + "\n\n" + rest.lstrip())


def append_once(path: str, marker: str, section: str) -> None:
    text = read(path)
    if marker not in text:
        write(path, text + "\n\n" + section.strip())


prepend_once(
    "CHANGELOG.md",
    "## 0.0.8 - 2026-08-05",
    """
## 0.0.8 - 2026-08-05

### Added

- collision-safe fuzzy AND/OR zones through `fuzzy_overlay()`;
- global min-max normalization of factor-stratum response risks;
- explicit first/last membership tie policies and tied-row evidence;
- fixed-discretization `power_interactive_determinant()` with `PID = theta / phi`;
- canonical ordinal encoding for externally supplied discrete class codes;
- CPSD-guided `optimize_spatial_discretization()` with complete candidate tables;
- integrated `IDSA` / `idsa` with greedy and bounded exhaustive subset search;
- response-permutation inference that recomputes fuzzy memberships and zones;
- immutable fuzzy-risk, overlay, PID, discretization and combination results;
- analytical fuzzy-label, component, invariance, search and missing-data tests;
- IDSA example, model manual and detailed paper/source audit.

### Changed

- package development version advanced to `0.0.8`;
- public API now exports fuzzy overlay, PID, spatial discretization and IDSA interfaces;
- CI runs eight public examples;
- continuous-factor selection uses explicit maximum CPSD with deterministic simplicity ties;
- reference LOESS selection remains a separate unimplemented compatibility estimator;
- Stage 6 categorical and information-consistency SSH becomes the next active stage.
""",
)

append_once(
    "DECISIONS.md",
    "## D039 - Fuzzy zones preserve source identity",
    """
## D039 - Fuzzy zones preserve source identity

IDSA fuzzy zones are stored as `(factor_name, original_stratum_label)` tuples. Concatenated text labels are prohibited because factor names and stratum labels may contain the same separators and collide.

## D040 - Fuzzy memberships use one global risk scale

For all supplied factors, response means are calculated within every factor stratum and normalized together by `(risk - global_min) / (global_max - global_min)`. Fuzzy AND selects the minimum current membership and fuzzy OR the maximum. Equal global risks make the membership scale undefined and raise an error.

## D041 - Fuzzy ties are explicit

The reference-compatible default selects the first supplied factor among memberships tied within `membership_tolerance`. `last` is an explicit alternative. Tied observations are counted and retained in the result.

## D042 - Fixed PID uses canonical ordinal codes

The IDSA information component requires ordered discretized explanatory factors. Each finite numeric factor is mapped by sorted unique value to canonical codes `1,...,K`. This prevents harmless shifts or positive rescaling of external class labels from changing the result. Unordered nominal labels are not silently assigned an order.

## D043 - PID components remain separately auditable

`theta` is response PSD under fuzzy zones. `phi` is `1 - sum_i(within_i) / sum_i(total_i)` from the spatial-variance decompositions of all canonical discretized factors under the same zones. `PID = theta / phi`. Zero information denominator or zero `phi` is an explicit failure; values are not clipped to an assumed range.

## D044 - Response-derived zones are recomputed under permutation

IDSA response permutations recalculate factor-stratum risks, memberships, fuzzy zones, theta, phi and PID. Invalid permuted zone systems are counted. Holding the observed response-derived overlay fixed is not the default null.

## D045 - Continuous IDSA selection is transparent

Continuous factors are discretized by maximizing CPSD across an explicit method-by-level grid. CPSD ties prefer fewer actual and requested strata, then earlier method order. The reference LOESS stopping heuristic is not claimed until a pinned external table is available.

## D046 - IDSA subset search is bounded and auditable

Greedy search follows iterative addition from the strongest individual CPSD factor and stops when PID no longer improves. Exhaustive search is available for small factor sets and is limited by `max_combinations`. Every attempted subset and failure remains public. Final permutation inference is not described as fully selection-adjusted.
""",
)

append_once(
    "VALIDATION_MATRIX.md",
    "## Stage 5B validation state and gaps",
    """
## Stage 5B validation state and gaps

| Method | Analytical | Cross-language/static | Simulation/edge cases | Published case | Status |
|---|---:|---:|---:|---:|---|
| Fuzzy overlay | manual AND/OR labels and min-max memberships | sdsfun source contract audited | ties, constant risk, missing rows and collision-safe labels | pending | implemented, provisional |
| Fixed PID | direct theta/phi equality | gdverse `pid_idsa` formula audited | canonical-code invariance, zero denominator and invalid zones | pending | implemented, provisional |
| IDSA permutation | deterministic recomputation of response-derived overlay | external null table pending | valid/failed permutation accounting | pending | implemented, provisional |
| CPSD discretization | maximum-CPSD and simplicity tie rule | reference candidate table pending | rejected candidates and degenerate levels | pending | implemented, provisional |
| Integrated IDSA | greedy and exhaustive subset search | gdverse final-output fixture pending | joint missing sample, bounded search and failure retention | pending | implemented, provisional |

Stage 5B still requires a pinned gdverse/sdsfun environment, a static fuzzy-zone table, external theta/phi/PID outputs, comparison of maximum-CPSD and LOESS selectors, a published IDSA reproduction, and selection-stability experiments. No full external-validation claim is made before those records exist.
""",
)

inventory = read("MODEL_INVENTORY.md")
inventory = inventory.replace(
    "| Spatial interaction | Fuzzy overlay | response-risk membership AND/OR zones | IDSA paper; sdsfun `fuzzyoverlay` | source/formula audit complete; Stage 5B next | 5B |",
    "| Spatial interaction | Fuzzy overlay | response-risk membership AND/OR zones | IDSA paper; sdsfun `fuzzyoverlay` | implemented with tuple identities, explicit ties and audit tables | 5B |",
)
inventory = inventory.replace(
    "| Spatial interaction | IDSA / PID | spatially informed interactive determinant | IDSA paper; gdverse `idsa`/`pid_idsa`; sdsfun | planned for next branch after contract freeze | 5B |",
    "| Spatial interaction | IDSA / PID | spatially informed interactive determinant | IDSA paper; gdverse `idsa`/`pid_idsa`; sdsfun | implemented with fixed PID, CPSD discretization and subset search; external case pending | 5B |",
)
write("MODEL_INVENTORY.md", inventory)

roadmap = read("ROADMAP.md")n = None
roadmap = roadmap.replace(
    "**Status:** next active batch after Stage 5A merge. Classical tuple intersection must not be substituted for fuzzy interaction zones.",
    "**Status:** implemented in PR #8. Analytical tests and source audits are complete; pinned external PID fixtures, LOESS-selector comparison and a published IDSA case remain validation debt.",
)
write("ROADMAP.md", roadmap)

structure = read("PROJECT_STRUCTURE.md")
structure = structure.replace(
    "│   │   └── spade.py             PSMD and integrated SPADE workflow",
    "│   │   ├── spade.py             PSMD and integrated SPADE workflow\n│   │   ├── idsa_results.py      immutable fuzzy-overlay and PID results\n│   │   └── idsa.py              fuzzy overlay, PID and IDSA search",
)
structure = structure.replace(
    "│   ├── test_spade.py            variance, PSD, CPSD, PSMD and workflow tests",
    "│   ├── test_spade.py            variance, PSD, CPSD, PSMD and workflow tests\n│   ├── test_idsa.py             fuzzy overlay, PID and IDSA search tests",
)
structure = structure.replace(
    "│   └── 07_spade.py",
    "│   ├── 07_spade.py\n│   └── 08_idsa.py",
)
append = """

Stage 5B keeps fuzzy overlay and PID in a dedicated model module. It reuses Stage 5A spatial variance and PSD rather than duplicating those formulas. Fuzzy zone construction, information retention and subset search remain separate from classical tuple interaction and robust RID.
"""
if "Stage 5B keeps fuzzy overlay" not in structure:
    structure += append
write("PROJECT_STRUCTURE.md", structure)

append_once(
    "THIRD_PARTY_NOTICES.md",
    "## IDSA Stage 5B source boundary",
    """
## IDSA Stage 5B source boundary

Stage 5B reviewed Song and Wu (2021), uploaded gdverse `R/idsa.R` and `R/pid_idsa.R`, and maintained sdsfun `R/fuzzyoverlay.R`, `R/vector_toolkits.R` and `R/spvar.R`. These GPL-family sources define formulas, workflow expectations and comparison targets. pyGeoHet independently implements sample alignment, tuple zone identities, canonical ordinal encoding, spatial components, candidate search, immutable results and permutation inference. It does not copy source line by line and does not call R, gdverse or sdsfun at runtime.
""",
)

handoff = """
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
"""
write("HANDOFF_NEXT_CONVERSATION.md", handoff)

readme_section = """
## Fuzzy interaction zones and IDSA

IDSA builds response-informed fuzzy zones rather than Cartesian intersections. Factor-stratum response means are normalized globally, fuzzy AND selects the minimum membership and fuzzy OR the maximum. Zone labels preserve `(factor, stratum)` identity.

```python
from pygeohet import IDSA, fuzzy_overlay, power_interactive_determinant

overlay = fuzzy_overlay(y, discrete_factors, operation="and")
pid = power_interactive_determinant(y, discrete_factors, weights)

result = IDSA(
    methods=("quantile", "natural_breaks", "equal_interval"),
    n_strata=range(3, 9),
    search="greedy",
).fit(y, continuous_factors, weights)

print(result.discretizations_frame())
print(result.combinations_frame())
print(result.best.result.summary())
```

`theta` is response PSD under fuzzy zones. `phi` measures the retained spatial information of all canonical ordinal factor codes. `PID = theta / phi`. Permutation inference rebuilds response-derived memberships and zones on every shuffle. Exhaustive subset search is available for small factor sets.
"""

readme = read("README.md")
readme = readme.replace(
    "> **Status - Stage 5A implemented:**",
    "> **Status - Stage 5B implemented:**",
)
readme = readme.replace(
    "Stage 5B will add fuzzy interaction zones and IDSA.",
    "Fuzzy interaction zones and IDSA are now available; Stage 6 will address categorical and information-consistency SSH.",
)
if "## Fuzzy interaction zones and IDSA" not in readme:
    readme = readme.replace("## Public interfaces", readme_section + "\n\n## Public interfaces")
readme = readme.replace(
    "    SPADE,\n",
    "    SPADE,\n    IDSA,\n",
    1,
)
readme = readme.replace(
    "    multilevel_spatial_determinant,\n",
    "    multilevel_spatial_determinant,\n    fuzzy_overlay,\n    power_interactive_determinant,\n    optimize_spatial_discretization,\n",
    1,
)
readme = readme.replace("    spade,\n", "    spade,\n    idsa,\n", 1)
if "docs/models/idsa.md" not in readme:
    readme = readme.replace(
        "- [`docs/models/spade.md`](docs/models/spade.md)",
        "- [`docs/models/spade.md`](docs/models/spade.md)\n- [`docs/models/idsa.md`](docs/models/idsa.md)\n- [`docs/references/idsa-code-audit.md`](docs/references/idsa-code-audit.md)",
    )
write("README.md", readme)

zh_section = """
## 模糊交互分区与 IDSA

IDSA 构造响应变量驱动的模糊分区，而不是简单笛卡尔交叉。所有因子—分层响应均值统一归一化；模糊 AND 选择最小隶属度，模糊 OR 选择最大隶属度；分区标签保留 `(因子名, 原分层值)` 身份。

```python
from pygeohet import IDSA, fuzzy_overlay, power_interactive_determinant

overlay = fuzzy_overlay(y, discrete_factors, operation="and")
pid = power_interactive_determinant(y, discrete_factors, weights)

result = IDSA(
    methods=("quantile", "natural_breaks", "equal_interval"),
    n_strata=range(3, 9),
    search="greedy",
).fit(y, continuous_factors, weights)
```

`theta` 是模糊分区下响应变量的 PSD，`phi` 表示所有有序离散因子的空间信息保留能力，最终 `PID = theta / phi`。置换检验会在每次打乱响应变量后重新计算风险、隶属度和模糊分区。
"""

zh = read("README.zh.md")
zh = zh.replace(
    "> **当前状态——阶段 5A 已实现：**",
    "> **当前状态——阶段 5B 已实现：**",
)
zh = zh.replace(
    "下一批将实现模糊交互分区和 IDSA。",
    "模糊交互分区和 IDSA 已实现；下一阶段进入分类响应与信息一致性 SSH。",
)
if "## 模糊交互分区与 IDSA" not in zh:
    zh = zh.replace("## 公共接口", zh_section + "\n\n## 公共接口")
zh = zh.replace("    SPADE,\n", "    SPADE,\n    IDSA,\n", 1)
zh = zh.replace(
    "    multilevel_spatial_determinant,\n",
    "    multilevel_spatial_determinant,\n    fuzzy_overlay,\n    power_interactive_determinant,\n    optimize_spatial_discretization,\n",
    1,
)
zh = zh.replace("    spade,\n", "    spade,\n    idsa,\n", 1)
if "docs/models/idsa.md" not in zh:
    zh += "\n\n- `docs/models/idsa.md`；\n- `docs/references/idsa-code-audit.md`。\n"
write("README.zh.md", zh)
