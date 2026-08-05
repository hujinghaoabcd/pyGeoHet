"""One-time Stage 6A documentation finalizer; remove before merge."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text.rstrip() + "\n", encoding="utf-8")


def append_once(path: str, marker: str, section: str) -> None:
    text = read(path)
    if marker not in text:
        write(path, text + "\n\n" + section.strip())


def prepend_after_heading(path: str, marker: str, section: str) -> None:
    text = read(path)
    if marker not in text:
        heading, remainder = text.split("\n", 1)
        write(path, heading + "\n\n" + section.strip() + "\n\n" + remainder.lstrip())


prepend_after_heading(
    "CHANGELOG.md",
    "## 0.0.9 - 2026-08-05",
    """
## 0.0.9 - 2026-08-05

### Added

- paper-aligned spatial rough-set numerical core for nominal targets;
- prepared binary adjacency validation with explicit symmetry and island evidence;
- local regions containing the focal object and its supplied neighbours;
- exact tuple-based local indiscernibility and decision-consistent positive regions;
- immutable `SpatialRoughSetResult` with local quality, region sizes, `D` and `SE`;
- public `spatial_rough_set_measure()` and SRS factor, ecological and interaction detectors;
- integrated `SRSGeoDetector` / `srsgd` workflow;
- paired common-location inference and reproducible paper-style subsampling;
- Figure 1 hand-calculated local-quality, `D`, `SE` and monotonicity fixtures;
- row-and-adjacency permutation, island, missing-axis and discrete-input tests;
- Stage 6 evidence audit, SRS-GD model manual, public example and API regression protection.

### Changed

- package development version advanced to `0.0.9`;
- CI runs nine public examples;
- Stage 6 is split into 6A SRS-GD, 6B information consistency and evidence-gated 6C SWMI;
- the published SRS-GD estimand is primary when reviewed reference C++ behaviour is ambiguous;
- multifeature indiscernibility requires equality on every feature rather than any-coordinate matching;
- adjacency diagonal values are ignored and the focal object is added exactly once;
- geometry-to-adjacency construction remains an explicit upstream responsibility;
- final CI passed on Ubuntu, Windows and macOS with Python 3.11, 3.12 and 3.13;
- Ruff, Black, mypy, nine examples, wheel build and source-distribution build passed;
- Stage 6B information-consistency SSH becomes the next active batch.
""",
)

append_once(
    "DECISIONS.md",
    "## D047 - SRS-GD targets nominal decisions",
    """
## D047 - SRS-GD targets nominal decisions

SRS-GD is a separate estimator for nominal or deliberately discretized target variables. It is not classical q applied to category codes. Noninteger continuous targets or features are rejected rather than silently coerced.

## D048 - Local regions always include the focal object

For focal object `x`, the primary paper defines `C(x)` as its binary neighbours union `{x}`. Input diagonal values are therefore ignored and the focal object is added exactly once. Self-only island regions are rejected by default because they create trivially perfect local quality.

## D049 - Multifeature indiscernibility uses exact tuples

Objects are locally indiscernible under a feature set only when every named feature agrees. Collision-safe tuples implement this equivalence relation. Any-coordinate matching is not used because it violates the paper definition and can destroy refinement monotonicity.

## D050 - Local positive regions require decision consistency

Within each focal local region, an equivalence class belongs to the positive region only when all objects in that class share one target category. Local quality is positive-region size divided by local-region size; no-positive-region cases receive zero rather than an invented degree-based value.

## D051 - Average power and spatial entropy remain distinct

`D` is the arithmetic mean of local approximation qualities. `SE` is Shannon entropy of those qualities after normalization by their sum. Larger `SE` means more even local explanatory power and therefore lower spatial heterogeneity. When every local quality is zero, `SE` is undefined and returned as `None`.

## D052 - SRS comparisons are paired on common focal objects

SRS ecological and interaction inference compares local-quality values evaluated at the same focal objects. Paired Student tests are the primary convention. A random focal-object subset is optional and seeded; all complete focal objects are used by default.

## D053 - Paper estimand outranks ambiguous reference operations

The reviewed gdverse C++ path differs from Bai et al. (2022) in focal-object inclusion, neighbour indexing, multifeature matching and zero-positive-region handling. pyGeoHet implements the published estimand independently and records compatibility values separately rather than reproducing ambiguous source behaviour silently.

## D054 - Information-consistency methods require separate contracts

Stage 6B nominal IN-SSH uses normalized mutual information. Continuous IC-SSH uses stratum-weighted, arctangent-normalized relative entropy. Neither is implemented by reusing q, SRS-GD, PSD or PID. Histogram support, bin edges, zero-density handling, constant targets and corrected permutation p-values must be frozen before merge.
""",
)

validation = read("VALIDATION_MATRIX.md")
row_marker = "| SRS-GD |"
if row_marker not in validation:
    validation = validation.replace(
        "| IDSA fuzzy overlay and PID | manual labels and direct theta/phi equality | fixture pending | ties, normalization, permutations, subset search and missing rows | pending | implemented, provisional |",
        "| IDSA fuzzy overlay and PID | manual labels and direct theta/phi equality | fixture pending | ties, normalization, permutations, subset search and missing rows | pending | implemented, provisional |\n| SRS-GD | Figure 1 local quality, D and SE | paper/source audit; external compatibility table pending | tuple monotonicity, adjacency permutation, islands, missing axes and nominal guards | Baltimore/Cincinnati pending | implemented, provisional |",
    )
section = """
## Stage 6A validation state and gaps

| Method | Analytical | Cross-language/static | Simulation/edge cases | Published case | Status |
|---|---:|---:|---:|---:|---|
| Local rough-set measure | Figure 1 local regions, positive regions and quality | primary paper fixture; gdverse discrepancy audit | diagonal invariance, row/adjacency permutation, islands and missing axes | pending | implemented, provisional |
| Average local power `D` | hand mean `0.7325757575757575` for `a1` | independent paper transcription | exact refinement monotonicity and nominal-input guards | pending | implemented, provisional |
| Spatial entropy `SE` | hand entropy `3.245554302578003` for `a1` | independent paper transcription | normalized entropy and undefined all-zero contract | pending | implemented, provisional |
| SRS factor detector | one-sample local-quality inference | gdverse factor output pending | common sample, seeded subset and public API tests | Baltimore/Cincinnati pending | implemented, provisional |
| SRS ecological detector | paired local-quality difference | Welch compatibility table pending | equal/unequal factors and common-location sampling | Baltimore/Cincinnati pending | implemented, provisional |
| SRS interaction detector | `{a1,a2}` D/SE and nonnegative gain | gdverse interaction output pending | exact tuple refinement, entropy direction and zero gain | Baltimore/Cincinnati pending | implemented, provisional |
| Integrated SRSGeoDetector | factor/ecological/interaction composition | external workflow fixture pending | three-factor Figure 1 workflow | pending | implemented, provisional |

Stage 6A follows the published spatial rough-set estimand. Known differences in the reviewed reference C++ implementation are documented rather than hidden. Remaining work includes pinned gdverse input/output fixtures, published Baltimore and Cincinnati reproductions, larger nominal simulations, neighbourhood sensitivity analysis and inference that accounts for dependence among overlapping local regions.
"""
if "## Stage 6A validation state and gaps" not in validation:
    validation = validation.rstrip() + "\n\n" + section.strip() + "\n"
write("VALIDATION_MATRIX.md", validation)

inventory = read("MODEL_INVENTORY.md")
inventory = inventory.replace(
    "| Categorical | SRS-GD | nominal target and local rough-set power | paper C++ / gdverse follow-up | planned | 6 |",
    "| Categorical | SRS-GD | nominal target and local rough-set power | Bai et al. (2022); uploaded gdverse source | paper-aligned implementation with Figure 1 fixture; external cases pending | 6A |",
)
inventory = inventory.replace(
    "| Information | SSHIC/SSHIN | distribution differences beyond variance | sshicm | planned | 6 |",
    "| Information | SSHIC/SSHIN | distribution differences beyond variance | 2023 paper; pinned stscl/sshicm source | next active batch after formula and fixture freeze | 6B |",
)
inventory = inventory.replace(
    "| Spatial information | SWMI | spatially weighted mutual information | no full public package found | source audit | 6 |",
    "| Spatial information | SWMI | spatially weighted mutual information | 2026 paper; no authoritative implementation pinned | evidence-gated; no API until full formulas and fixture are verified | 6C |",
)
inventory = inventory.replace(
    "This policy governs the ecological detector, Stage 3 scale and MSD distinctions, Stage 4 robust source differences, and Stage 5 separation between prepared spatial weights, SPADE variance decomposition and IDSA fuzzy interaction zones.",
    "This policy governs the ecological detector, Stage 3 scale and MSD distinctions, Stage 4 robust source differences, Stage 5 separation between prepared spatial weights, SPADE variance decomposition and IDSA fuzzy interaction zones, and Stage 6 separation between the published SRS-GD estimand and ambiguous reference-source operations.",
)
write("MODEL_INVENTORY.md", inventory)

roadmap = read("ROADMAP.md")
roadmap = roadmap.replace(
    "**Status:** implementation and final CI complete in PR #8; merge is the final Stage 5 action. Analytical tests and source audits are complete. Pinned external PID fixtures, LOESS-selector comparison and a published IDSA case remain validation debt.",
    "**Status:** complete and merged in PR #8. Analytical tests and source audits are complete. Pinned external PID fixtures, LOESS-selector comparison and a published IDSA case remain validation debt.",
)
old_stage6 = """## Stage 6 - Categorical and information-consistency SSH (`0.4.0`)

Spatial rough-set GD for nominal targets; continuous and nominal information-consistency measures; permutation inference; SWMI after primary-source verification.

**Status:** next active stage after PR #8 is merged.
"""
new_stage6 = """## Stage 6 - Categorical and information-consistency SSH (`0.4.0`)

### Stage 6A - Spatial rough-set geographical detectors (`0.0.9`)

Nominal-target spatial information systems; focal-object local regions; exact multifeature indiscernibility; local positive regions; average local explanatory power `D`; spatial entropy `SE`; factor, ecological and interaction detectors; paired inference and immutable local evidence.

**Status:** implementation and final CI complete in PR #9. The paper Figure 1 local values, `D`, `SE` and refinement monotonicity are reproduced. Published Baltimore/Cincinnati cases and a pinned gdverse compatibility table remain validation debt.

### Stage 6B - Information-consistency SSH

Nominal `IN-SSH` by normalized mutual information and continuous `IC-SSH` by stratum-weighted arctangent-normalized relative entropy; corrected seeded permutation inference; common histogram support and explicit density contracts.

**Status:** next active batch after PR #9 merge.

### Stage 6C - Spatially weighted mutual information

Spatial probability adjustment, weighted entropy and mutual information only after the complete 2026 paper equations, implementation evidence and a numerical fixture are pinned.

**Status:** evidence-gated; no provisional public API.
"""
if old_stage6 in roadmap:
    roadmap = roadmap.replace(old_stage6, new_stage6)
write("ROADMAP.md", roadmap)

structure = read("PROJECT_STRUCTURE.md")
structure = structure.replace(
    "│   │   ├── idsa_results.py      immutable fuzzy-overlay and PID results\n│   │   └── idsa.py              fuzzy overlay, PID and IDSA search",
    "│   │   ├── idsa_results.py      immutable fuzzy-overlay and PID results\n│   │   ├── idsa.py              fuzzy overlay, PID and IDSA search\n│   │   ├── srsgd_results.py     immutable local rough-set evidence\n│   │   └── srsgd.py             SRS factor, ecological and interaction workflows",
)
structure = structure.replace(
    "│   ├── test_idsa.py             fuzzy overlay, PID and IDSA search tests\n│   └── test_*.py                classical analytical, edge and workflow tests",
    "│   ├── test_idsa.py             fuzzy overlay, PID and IDSA search tests\n│   ├── test_srsgd.py            Figure 1, adjacency and nominal-target tests\n│   ├── test_public_api.py       documented top-level API regression tests\n│   └── test_*.py                classical analytical, edge and workflow tests",
)
structure = structure.replace(
    "│   ├── 07_spade.py\n│   └── 08_idsa.py",
    "│   ├── 07_spade.py\n│   ├── 08_idsa.py\n│   └── 09_srsgd.py",
)
structure = structure.replace(
    "│   ├── models/                  classic through IDSA manuals",
    "│   ├── models/                  classic through SRS-GD manuals",
)
append_text = """

Stage 6A adds SRS-GD as a dedicated nominal-target model family. It consumes a prepared binary adjacency matrix and does not reuse variance-based q, spatial PSD or fuzzy PID. Stage 6B information-consistency methods will remain in separate modules after their entropy and density contracts are frozen.
"""
if "Stage 6A adds SRS-GD" not in structure:
    structure += append_text
write("PROJECT_STRUCTURE.md", structure)

append_once(
    "THIRD_PARTY_NOTICES.md",
    "## SRS-GD and Stage 6 information-source boundary",
    """
## SRS-GD and Stage 6 information-source boundary

Stage 6A reviewed Bai et al. (2022), *Spatial rough set-based geographical detectors for nominal target variables*, and uploaded gdverse wrappers, tests and `src/roughset.cpp`. The paper is the primary estimand. The reviewed source is used to understand software contracts and construct compatibility questions, but differs from the paper in focal-object inclusion, neighbour indexing, multifeature matching and zero-positive-region handling.

pyGeoHet independently implements prepared binary adjacency validation, complete-case alignment across both matrix axes, exact tuple equivalence classes, local positive regions, immutable evidence and paired inference. It does not copy or translate the reviewed C++ line by line and does not call gdverse or R at runtime.

Stage 6B evidence includes Bai et al. (2023), *Information Consistency-Based Measures for Spatial Stratified Heterogeneity*, and maintained `stscl/sshicm` source pinned during the audit to commit `76b6c2879353716f2632c4f5cbb13bef3f6c8305`. That source is used to verify formulas and future static outputs, not as a runtime backend.

The 2026 SWMI paper is recent and no authoritative executable reference has yet been pinned. No SWMI code or API will be introduced until the complete probability-weighting equations, null procedure and at least one independent numerical output are available.
""",
)

readme = read("README.md")
readme = readme.replace(
    "> **Status - Stage 5B implemented:** q-statistic, the four classical detectors, integrated `GeoDetector`, six continuous-variable stratification methods, univariate `OPGD`, prepared-support spatial-scale OPGD, multiscale discretization (`MSD`), robust discretization, `RGD`, `RID`, spatial variance, PSD, CPSD, PSMD and `SPADE` are available. Fuzzy interaction zones and IDSA are now available; Stage 6 will address categorical and information-consistency SSH.",
    "> **Status - Stage 6A implemented:** classical GeoDetector, OPGD, spatial-scale comparison, MSD, RGD/RID, SPADE, IDSA and paper-aligned SRS-GD are available. Stage 6B will add nominal and continuous information-consistency SSH; SWMI remains evidence-gated.",
)
srs_section = """
## Nominal targets and SRS-GD

SRS-GD evaluates a nominal target through local rough-set approximation. Every local region contains the focal object and its prepared binary neighbours. Objects are indiscernible only when all selected feature values agree, and a local equivalence class contributes to the positive region only when it contains one target category.

```python
from pygeohet import SRSGeoDetector, spatial_rough_set_measure

single = spatial_rough_set_measure(
    nominal_target,
    factors[["land_use"]],
    adjacency,
)
print(single.summary())
print(single.local_frame())

result = SRSGeoDetector(baseline="land_use").fit(
    nominal_target,
    factors,
    adjacency,
)
print(result.factor.to_frame())
print(result.ecological.to_frame())
print(result.interaction.to_frame())
```

`D` is mean local approximation quality. `SE` is Shannon entropy of normalized local qualities; larger `SE` means local explanatory power is more even and spatial heterogeneity is lower. The core does not construct adjacency from geometry. Islands, symmetry, missing rows, focal-object inclusion and exact tuple refinement are explicit contracts.
"""
if "## Nominal targets and SRS-GD" not in readme:
    readme = readme.replace(
        "## Public interfaces", srs_section + "\n\n## Public interfaces"
    )
readme = readme.replace(
    "    IDSA,\n    q_statistic,", "    IDSA,\n    SRSGeoDetector,\n    q_statistic,", 1
)
readme = readme.replace(
    "    optimize_spatial_discretization,\n    stratify,",
    "    optimize_spatial_discretization,\n    spatial_rough_set_measure,\n    srs_factor_detector,\n    srs_ecological_detector,\n    srs_interaction_detector,\n    stratify,",
    1,
)
readme = readme.replace("    idsa,\n)", "    idsa,\n    srsgd,\n)", 1)
readme = readme.replace(
    "- response-derived fuzzy zones are recomputed under IDSA permutation;",
    "- response-derived fuzzy zones are recomputed under IDSA permutation;\n- SRS-GD nominal targets, local regions, exact tuple indiscernibility and positive regions remain explicit;\n- adjacency symmetry, focal-object inclusion and islands are never silently inferred;",
)
readme = readme.replace(
    "Stage 5A has hand-computed spatial-variance tests and an externally checked categorical NTD PSD path. Stage 5B adds manual fuzzy AND/OR memberships, explicit ties, direct theta/phi decomposition, canonical-code invariance, response-overlay recomputation under permutation, CPSD candidate selection, greedy/exhaustive subset searches and missing-row reconstruction. IDSA remains implemented and provisional until pinned external PID fixtures and a published-case reproduction are complete.",
    "Stage 5A has hand-computed spatial-variance tests and an externally checked categorical NTD PSD path. Stage 5B adds manual fuzzy memberships, direct theta/phi decomposition and auditable IDSA search. Stage 6A reproduces the SRS-GD paper Figure 1 local qualities, `D` and `SE`, verifies exact tuple-refinement monotonicity, and tests adjacency permutation, islands, missing axes and discrete-input guards. SRS-GD remains implemented and provisional until published Baltimore/Cincinnati reproductions and a pinned compatibility table are complete.",
)
if "docs/models/srsgd.md" not in readme:
    readme = readme.replace(
        "- [`docs/models/idsa.md`](docs/models/idsa.md)",
        "- [`docs/models/idsa.md`](docs/models/idsa.md)\n- [`docs/models/srsgd.md`](docs/models/srsgd.md)\n- [`docs/references/stage6-information-ssh-audit.md`](docs/references/stage6-information-ssh-audit.md)",
    )
write("README.md", readme)

zh = read("README.zh.md")
zh = zh.replace(
    "> **当前状态——阶段 5B 已实现：** q 统计量、四类经典探测器、统一 `GeoDetector`、六种连续变量分层方法、`OPGD`、显式空间支持尺度 OPGD、`MSD`、稳健离散化、`RGD`、`RID`、空间方差、PSD、CPSD、PSMD 和 `SPADE` 均已可用。模糊交互分区和 IDSA 已实现；下一阶段进入分类响应与信息一致性 SSH。",
    "> **当前状态——阶段 6A 已实现：** 经典 GeoDetector、OPGD、空间尺度比较、MSD、RGD/RID、SPADE、IDSA 和论文对齐的 SRS-GD 均已可用。下一批进入名义型与连续型信息一致性 SSH；SWMI 仍由证据门槛控制。",
)
zh_section = """
## 名义型目标变量与 SRS-GD

SRS-GD 通过局部粗糙集近似分析名义型目标变量。每个局部区域由中心对象和已准备好的二值邻居组成；只有全部所选特征都相同的对象才不可分辨；局部等价类只有在目标类别完全一致时才进入正域。

```python
from pygeohet import SRSGeoDetector, spatial_rough_set_measure

single = spatial_rough_set_measure(
    nominal_target,
    factors[["land_use"]],
    adjacency,
)
result = SRSGeoDetector(baseline="land_use").fit(
    nominal_target,
    factors,
    adjacency,
)
```

`D` 是局部近似质量的平均值，`SE` 是归一化局部质量的 Shannon 熵；`SE` 越大，局部解释力越均匀、空间异质性越弱。核心不会从几何数据静默构造邻接关系，矩阵对称性、孤岛、缺失行、中心对象和多特征元组细化均有明确契约。
"""
if "## 名义型目标变量与 SRS-GD" not in zh:
    zh = zh.replace("## 公共接口", zh_section + "\n\n## 公共接口")
zh = zh.replace(
    "    IDSA,\n    q_statistic,", "    IDSA,\n    SRSGeoDetector,\n    q_statistic,", 1
)
zh = zh.replace(
    "    optimize_spatial_discretization,\n    stratify,",
    "    optimize_spatial_discretization,\n    spatial_rough_set_measure,\n    srs_factor_detector,\n    srs_ecological_detector,\n    srs_interaction_detector,\n    stratify,",
    1,
)
zh = zh.replace("    idsa,\n)", "    idsa,\n    srsgd,\n)", 1)
zh = zh.replace(
    "- IDSA 置换时重新计算响应变量驱动的模糊分区；",
    "- IDSA 置换时重新计算响应变量驱动的模糊分区；\n- SRS-GD 的名义型目标、局部区域、精确元组不可分辨关系和正域均显式保留；\n- 邻接矩阵对称性、中心对象和孤岛不会被静默处理；",
)
zh = zh.replace(
    "阶段 5A 已完成手工空间方差测试和分类变量 NTD PSD 外部核对。阶段 5B 增加模糊 AND/OR 隶属度、显式并列规则、theta/phi 直接分解、有序编码不变性、置换时重算模糊分区、CPSD 候选选择、贪心/穷举子集搜索和缺失行重建测试。IDSA 在固定外部 PID 参考输出和正式论文案例完成前仍标记为已实现、暂定验证。",
    "阶段 5A 已完成手工空间方差测试和分类变量 NTD PSD 外部核对，阶段 5B 已完成模糊分区、theta/phi 分解和 IDSA 搜索验证。阶段 6A 已复现 SRS-GD 论文图 1 的局部质量、`D` 和 `SE`，并验证精确元组细化单调性、邻接置换、孤岛、缺失矩阵轴和离散输入契约。正式 Baltimore/Cincinnati 案例和固定兼容输出完成前，SRS-GD 标记为已实现、暂定验证。",
)
if "docs/models/srsgd.md" not in zh:
    zh = zh.replace(
        "- `docs/models/idsa.md`；",
        "- `docs/models/idsa.md`；\n- `docs/models/srsgd.md`；\n- `docs/references/stage6-information-ssh-audit.md`；",
    )
write("README.zh.md", zh)

write(
    "HANDOFF_NEXT_CONVERSATION.md",
    """
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
""",
)
