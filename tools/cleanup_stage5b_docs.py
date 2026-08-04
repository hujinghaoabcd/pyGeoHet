"""Normalize Stage 5B documentation and remove all temporary machinery."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_section(text: str, start: str, end: str, replacement: str) -> str:
    left, remainder = text.split(start, 1)
    _, right = remainder.split(end, 1)
    return left + replacement.rstrip() + "\n\n" + end + right


def collapse_blank_lines(text: str) -> str:
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")
    return text.rstrip() + "\n"


readme_path = ROOT / "README.md"
readme = readme_path.read_text(encoding="utf-8")
readme = readme.replace(
    "> **Status - Stage 5A implemented:**",
    "> **Status - Stage 5B implemented:**",
)
spade_en = """## Spatial variance and SPADE

Stage 5A accepts an explicitly prepared nonnegative square spatial-weight matrix. It never silently chooses geometry representatives, CRS, distance units, neighbours, row standardization or symmetrization.

```python
import numpy as np
import pandas as pd
from pygeohet import (
    SPADE,
    compensated_spatial_determinant,
    multilevel_spatial_determinant,
    power_spatial_determinant,
    spatial_variance,
)

coordinates = np.arange(12, dtype=float)
distance = np.abs(coordinates[:, None] - coordinates[None, :])
weights = np.zeros_like(distance)
mask = distance > 0
weights[mask] = 1.0 / distance[mask] ** 2

y = np.asarray([0, 0, 1, 1, 4, 4, 5, 5, 9, 9, 10, 10], dtype=float)
region = np.repeat(["west", "centre", "east"], 4)
trend = coordinates.copy()

print(spatial_variance(y, weights).summary())
print(power_spatial_determinant(y, region, weights).summary())

labels = np.repeat([1, 2, 3], 4)
print(compensated_spatial_determinant(y, trend, labels, weights).summary())

psmd = multilevel_spatial_determinant(
    y,
    trend,
    weights,
    n_strata=(2, 3, 4),
    method="quantile",
)
print(psmd.candidates_frame())

factors = pd.DataFrame({"trend": trend, "region": region})
spade_result = SPADE(n_strata=(2, 3, 4), method="quantile").fit(
    y,
    factors,
    weights,
    continuous_factors=("trend",),
)
print(spade_result.to_frame())
```

The implemented formulas are:

```text
Gamma = sum_ij w_ij (y_i - y_j)^2 / 2 / sum_ij w_ij
PSD   = 1 - sum_h N_h Gamma_h / (N Gamma)
CPSD  = PSD(response) / PSD(original continuous factor)
PSMD  = mean CPSD over accepted explicit class-count levels
```

Missing observations remove the matching row and column from the weight matrix. Diagonal mass, symmetry and islands are audited. PSD and PSMD may use seeded conditional permutation inference.

The NTD SPADE reference route produces `0.2566528294856155`, matching the gdverse test expectation `0.256653` at six decimals. The raw GPKG is not redistributed.
"""
idsa_en = """## Fuzzy interaction zones and IDSA

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

`theta` is response PSD under fuzzy zones. `phi` measures the retained spatial information of canonical ordinal factor codes. `PID = theta / phi`. Permutation inference rebuilds response-derived memberships and zones on every shuffle. Exhaustive subset search is available for small factor sets.
"""
public_en = """## Public interfaces

```python
from pygeohet import (
    GeoDetector,
    OPGD,
    SpatialScaleOPGD,
    MSD,
    RGD,
    RID,
    SPADE,
    IDSA,
    q_statistic,
    spatial_variance,
    power_spatial_determinant,
    compensated_spatial_determinant,
    multilevel_spatial_determinant,
    fuzzy_overlay,
    power_interactive_determinant,
    optimize_spatial_discretization,
    stratify,
    evaluate_stratification,
    optimize_stratification,
    multiscale_discretize,
    robust_discretize,
    optimize_robust_discretization,
    compare_spatial_scales,
    factor_detector,
    interaction_detector,
    risk_detector,
    ecological_detector,
    geodetector,
    opgd,
    rgd,
    rid,
    spade,
    idsa,
)
```
"""
commitments_en = """## Statistical commitments

- q is computed from direct centered sums of squares;
- missing-row counts and sample scopes remain auditable;
- interaction components use one joint complete-case sample;
- categorical overlays use collision-safe labels;
- risk comparisons use two-sided Welch tests;
- ecological conventions are explicit;
- stratification, scale, MSD and robust searches retain candidate and tie evidence;
- spatial support scale, explanatory-value-grid scale and spatial-weight structure remain distinct;
- spatial weights are never silently constructed, normalized or symmetrized;
- PSD remains a spatial-variance estimand and is not called classical q under arbitrary weights;
- PSMD failures and accepted levels remain visible;
- fuzzy zones preserve factor-stratum identity and expose tie decisions;
- PID retains theta, phi, membership, zone and subset-search evidence;
- response-derived fuzzy zones are recomputed under IDSA permutation;
- model-complexity selection is explicit rather than hidden inside numerical kernels;
- external R, Python, QGIS, notebook and GIS implementations are never called at runtime;
- project status, validation records and handoff are merge gates.
"""
validation_en = """## Validation

The classical workflow reproduces the NTD factor q/p-values, interaction labels and risk-significance counts. MSD matches an independent exhaustive search. Robust segmentation matches an independent brute-force oracle and verifies B=q on selected labels.

Stage 5A has hand-computed spatial-variance tests and an externally checked categorical NTD PSD path. Stage 5B adds manual fuzzy AND/OR memberships, explicit ties, direct theta/phi decomposition, canonical-code invariance, response-overlay recomputation under permutation, CPSD candidate selection, greedy/exhaustive subset searches and missing-row reconstruction. IDSA remains implemented and provisional until pinned external PID fixtures and a published-case reproduction are complete.

See:

- [`docs/models/classic-detectors.md`](docs/models/classic-detectors.md)
- [`docs/models/stratification-opgd.md`](docs/models/stratification-opgd.md)
- [`docs/models/spatial-scale-opgd.md`](docs/models/spatial-scale-opgd.md)
- [`docs/models/msd.md`](docs/models/msd.md)
- [`docs/models/robust-rgd-rid.md`](docs/models/robust-rgd-rid.md)
- [`docs/models/spade.md`](docs/models/spade.md)
- [`docs/models/idsa.md`](docs/models/idsa.md)
- [`docs/references/spade-idsa-code-audit.md`](docs/references/spade-idsa-code-audit.md)
- [`docs/references/idsa-code-audit.md`](docs/references/idsa-code-audit.md)
- [`VALIDATION_MATRIX.md`](VALIDATION_MATRIX.md)
- [`ROADMAP.md`](ROADMAP.md)
- [`HANDOFF_NEXT_CONVERSATION.md`](HANDOFF_NEXT_CONVERSATION.md)
"""
readme = replace_section(readme, "## Spatial variance and SPADE", "## Fuzzy interaction zones and IDSA", spade_en)
readme = replace_section(readme, "## Fuzzy interaction zones and IDSA", "## Public interfaces", idsa_en)
readme = replace_section(readme, "## Public interfaces", "## Statistical commitments", public_en)
readme = replace_section(readme, "## Statistical commitments", "## Validation", commitments_en)
readme = replace_section(readme, "## Validation", "## Licence", validation_en)
readme_path.write_text(collapse_blank_lines(readme), encoding="utf-8")

zh_path = ROOT / "README.zh.md"
zh = zh_path.read_text(encoding="utf-8")
zh = zh.replace(
    "> **当前状态——阶段 5A 已实现：**",
    "> **当前状态——阶段 5B 已实现：**",
)
zh_tail = """## 空间方差与 SPADE

阶段 5A 接受已经准备好的非负方阵空间权重。核心不会静默决定几何代表点、CRS、距离单位、邻域、行标准化或对称化。

```python
import numpy as np
import pandas as pd
from pygeohet import (
    SPADE,
    compensated_spatial_determinant,
    multilevel_spatial_determinant,
    power_spatial_determinant,
    spatial_variance,
)

coordinates = np.arange(12, dtype=float)
distance = np.abs(coordinates[:, None] - coordinates[None, :])
weights = np.zeros_like(distance)
mask = distance > 0
weights[mask] = 1.0 / distance[mask] ** 2

y = np.asarray([0, 0, 1, 1, 4, 4, 5, 5, 9, 9, 10, 10], dtype=float)
region = np.repeat(["west", "centre", "east"], 4)
trend = coordinates.copy()

print(spatial_variance(y, weights).summary())
print(power_spatial_determinant(y, region, weights).summary())

labels = np.repeat([1, 2, 3], 4)
print(compensated_spatial_determinant(y, trend, labels, weights).summary())

psmd = multilevel_spatial_determinant(
    y,
    trend,
    weights,
    n_strata=(2, 3, 4),
    method="quantile",
)
print(psmd.candidates_frame())

factors = pd.DataFrame({"trend": trend, "region": region})
result = SPADE(n_strata=(2, 3, 4), method="quantile").fit(
    y,
    factors,
    weights,
    continuous_factors=("trend",),
)
print(result.to_frame())
```

已实现公式：

```text
Gamma = sum_ij w_ij (y_i - y_j)^2 / 2 / sum_ij w_ij
PSD   = 1 - sum_h N_h Gamma_h / (N Gamma)
CPSD  = 响应变量 PSD / 原连续解释变量的信息保留 PSD
PSMD  = 所有有效显式层数 CPSD 的平均值
```

缺失观测会同步删除权重矩阵对应的行和列。对角权重、矩阵对称性和孤岛均有审计信息。PSD 与 PSMD 支持固定随机种子的条件置换检验。

NTD SPADE 外部参考结果为 `0.2566528294856155`，与 gdverse 测试值 `0.256653` 在六位小数上一致。原始 GPKG 不在仓库中重新分发。

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

`theta` 是模糊分区下响应变量的 PSD，`phi` 表示有序离散因子的空间信息保留能力，最终 `PID = theta / phi`。置换检验会在每次打乱响应变量后重新计算风险、隶属度和模糊分区。

## 公共接口

```python
from pygeohet import (
    GeoDetector,
    OPGD,
    SpatialScaleOPGD,
    MSD,
    RGD,
    RID,
    SPADE,
    IDSA,
    q_statistic,
    spatial_variance,
    power_spatial_determinant,
    compensated_spatial_determinant,
    multilevel_spatial_determinant,
    fuzzy_overlay,
    power_interactive_determinant,
    optimize_spatial_discretization,
    stratify,
    optimize_stratification,
    multiscale_discretize,
    robust_discretize,
    optimize_robust_discretization,
    compare_spatial_scales,
    geodetector,
    opgd,
    rgd,
    rid,
    spade,
    idsa,
)
```

## 统计与开发原则

- q 直接按中心化平方和计算；
- 缺失行和实际样本范围可审计；
- 交互探测使用联合完整样本和防碰撞标签；
- 分层、尺度、MSD 和稳健搜索保留全部候选和并列规则；
- 地理支持尺度、解释变量网格尺度和空间权重结构严格区分；
- 空间权重不会被静默构建、标准化或对称化；
- PSD 是空间方差分解，不会在任意权重下冒充经典 q；
- PSMD 的失败层数和实际采用层数均保留；
- 模糊分区保留因子—分层身份并记录并列决策；
- PID 保留 theta、phi、隶属度、分区和子集搜索证据；
- IDSA 置换时重新计算响应变量驱动的模糊分区；
- 外部 R、Python、QGIS、Notebook 和 GIS 实现不作为运行时后端；
- 项目状态、验证矩阵和交接文档是合并门槛。

## 验证状态

经典工作流已复现 NTD 因子、交互和风险参考输出。MSD 与独立穷举程序一致；稳健分区与独立暴力枚举一致，并验证 B=q。

阶段 5A 已完成手工空间方差测试和分类变量 NTD PSD 外部核对。阶段 5B 增加模糊 AND/OR 隶属度、显式并列规则、theta/phi 直接分解、有序编码不变性、置换时重算模糊分区、CPSD 候选选择、贪心/穷举子集搜索和缺失行重建测试。IDSA 在固定外部 PID 参考输出和正式论文案例完成前仍标记为已实现、暂定验证。

详细说明见：

- `docs/models/classic-detectors.md`；
- `docs/models/stratification-opgd.md`；
- `docs/models/spatial-scale-opgd.md`；
- `docs/models/msd.md`；
- `docs/models/robust-rgd-rid.md`；
- `docs/models/spade.md`；
- `docs/models/idsa.md`；
- `docs/references/spade-idsa-code-audit.md`；
- `docs/references/idsa-code-audit.md`；
- `VALIDATION_MATRIX.md`；
- `ROADMAP.md`；
- `HANDOFF_NEXT_CONVERSATION.md`。
"""
zh = zh.split("## 空间方差与 SPADE", 1)[0] + zh_tail
zh_path.write_text(collapse_blank_lines(zh), encoding="utf-8")

project_structure = """# pyGeoHet project structure

```text
pyGeoHet/
├── src/pygeohet/
│   ├── __init__.py              public convenience API
│   ├── _version.py              package version
│   ├── exceptions.py            explicit statistical/data errors
│   ├── validation.py            factor coercion and complete-case contracts
│   ├── results.py               classical immutable result objects
│   ├── core/
│   │   ├── qstat.py             q and noncentral-F inference
│   │   ├── overlay.py           collision-safe tuple overlays
│   │   └── interaction.py       interaction-type classifier
│   ├── detectors/               factor, interaction, risk and ecological APIs
│   ├── spatial/
│   │   ├── __init__.py          spatial-statistic public exports
│   │   └── variance.py          prepared weights and spatial variance
│   ├── stratification/
│   │   ├── methods.py           six deterministic univariate methods
│   │   ├── optimal.py           q-guided candidate evaluation and selection
│   │   ├── msd.py               supervised exact/coarse-to-fine MSD search
│   │   └── results.py           immutable stratification/search evidence
│   ├── models/
│   │   ├── geodetector.py       integrated classical workflow
│   │   ├── opgd.py              audited optimal-discretization workflow
│   │   ├── spatial_scale.py     prepared-support OPGD scale comparison
│   │   ├── robust.py            exact robust discretization, RGD and RID
│   │   ├── spade_core.py        PSD and CPSD numerical core
│   │   ├── spade_results.py     immutable SPADE-family results
│   │   ├── spade.py             PSMD and integrated SPADE workflow
│   │   ├── idsa_results.py      immutable fuzzy-overlay and PID results
│   │   └── idsa.py              fuzzy overlay, PID and IDSA search
│   └── py.typed                 inline typing marker
├── tests/
│   ├── fixtures/reference/      static/provenance-only external records
│   ├── test_stratification.py   method, boundary and optimization contracts
│   ├── test_opgd.py             integrated OPGD workflow tests
│   ├── test_spatial_scale.py    scale scores, ties, failures and integration
│   ├── test_msd.py              exact oracle, refinement and audit contracts
│   ├── test_robust.py           brute-force, rank, duplicate-x, RGD/RID tests
│   ├── test_spade.py            variance, PSD, CPSD, PSMD and workflow tests
│   ├── test_idsa.py             fuzzy overlay, PID and IDSA search tests
│   └── test_*.py                classical analytical, edge and workflow tests
├── examples/
│   ├── 01_factor_detector.py
│   ├── 02_classic_workflow.py
│   ├── 03_stratification_opgd.py
│   ├── 04_spatial_scale_opgd.py
│   ├── 05_multiscale_discretization.py
│   ├── 06_robust_detectors.py
│   ├── 07_spade.py
│   └── 08_idsa.py
├── tools/
│   ├── validate_ntd_reference.py
│   └── validate_ntd_spade_reference.py
├── docs/
│   ├── theory/                  formulas and numerical conventions
│   ├── models/                  classic through IDSA manuals
│   ├── references/              paper/source-code audits
│   ├── validation/              published/reference case reports
│   └── development/             testing and handoff policies
├── .github/workflows/ci.yml     cross-platform gate with PR concurrency control
├── MODEL_INVENTORY.md           methods, references and implementation state
├── VALIDATION_MATRIX.md         evidence required for every public model
├── DECISIONS.md                 durable statistical and API decisions
├── PROJECT_STATUS.md            current factual state
├── ROADMAP.md                   ten-stage development plan
└── HANDOFF_NEXT_CONVERSATION.md authoritative continuation instructions
```

Automatic geographic-support aggregation is intentionally absent from the core package. Scale-specific datasets are prepared explicitly upstream and compared through `models/spatial_scale.py`. MSD's scales are explanatory-variable value-grid resolutions and remain separate from geographic support.

Stage 5A introduces a reusable `spatial` package and separates the SPADE numerical core, immutable results and workflow composition. Stage 5B keeps fuzzy overlay and PID in dedicated IDSA modules while reusing the Stage 5A spatial variance and PSD implementations.

Dense spatial weights are the current public contract. Sparse matrices, coordinate-to-weight builders and geometry adapters should be added as optional layers only after their numerical and dependency contracts are frozen.

Directories for information, multivariate, local and temporal-lagged methods are created only when implementation begins. Planned public names remain in the roadmap until working code, tests and documentation exist.
"""
(ROOT / "PROJECT_STRUCTURE.md").write_text(project_structure, encoding="utf-8")

validation_path = ROOT / "VALIDATION_MATRIX.md"
validation = validation_path.read_text(encoding="utf-8")
validation = validation.replace(
    "| IDSA fuzzy overlay and PID | paper/source audit complete | fixture pending | tie, normalization and missing-risk tests pending | pending | Stage 5B planned |",
    "| IDSA fuzzy overlay and PID | manual labels and direct theta/phi equality | fixture pending | ties, normalization, permutations, subset search and missing rows | pending | implemented, provisional |",
)
validation_path.write_text(collapse_blank_lines(validation), encoding="utf-8")

final_ci = """name: CI

on:
  push:
    branches: [main]
  pull_request:

concurrency:
  group: ci-${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true

jobs:
  test:
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ["3.11", "3.12", "3.13"]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip
      - run: python -m pip install --upgrade pip
      - run: python -m pip install -e ".[test]"
      - run: pytest --cov=pygeohet --cov-report=term-missing

  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip
      - run: python -m pip install -e ".[dev]"
      - run: ruff check src tests examples tools
      - run: black --check src tests examples tools
      - run: mypy src/pygeohet
      - run: python examples/01_factor_detector.py
      - run: python examples/02_classic_workflow.py
      - run: python examples/03_stratification_opgd.py
      - run: python examples/04_spatial_scale_opgd.py
      - run: python examples/05_multiscale_discretization.py
      - run: python examples/06_robust_detectors.py
      - run: python examples/07_spade.py
      - run: python examples/08_idsa.py
      - run: python -m build
"""
(ROOT / ".github/workflows/ci.yml").write_text(final_ci, encoding="utf-8")

for relative in (
    ".github/workflows/finalize-stage5b.yml",
    "tools/finalize_stage5b_docs.py",
    "tools/fix_stage5b_readmes.py",
):
    (ROOT / relative).unlink(missing_ok=True)

(ROOT / ".stage5b-cleanup-complete").write_text(
    "Delete this marker through the GitHub API to trigger the final clean CI run.\n",
    encoding="utf-8",
)

Path(__file__).unlink()
