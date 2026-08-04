"""One-time README consistency fixer for Stage 5B; removed before merge."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_section(text: str, start: str, end: str, replacement: str) -> str:
    left, remainder = text.split(start, 1)
    _, right = remainder.split(end, 1)
    return left + start + replacement + end + right


readme_path = ROOT / "README.md"
readme = readme_path.read_text(encoding="utf-8")
readme_api = """
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
"""
readme = replace_section(
    readme,
    "## Public interfaces\n\n```python\n",
    "```\n\n## Statistical commitments",
    readme_api,
)
readme = readme.replace(
    "- PSMD failures and accepted levels remain visible;\n",
    "- PSMD failures and accepted levels remain visible;\n"
    "- fuzzy zones preserve factor-stratum identity and expose tie decisions;\n"
    "- PID retains theta, phi, membership, zone and subset-search evidence;\n"
    "- response-derived fuzzy zones are recomputed under IDSA permutation;\n",
)
readme = readme.replace(
    "Stage 5A has hand-computed spatial-variance tests, weight-scaling and row/weight permutation invariance, common missing-sample alignment, explicit island failures, CPSD identity, PSMD candidate averaging, deterministic permutation tests and mixed-factor integration. Its categorical NTD PSD path is externally checked; continuous CPSD/PSMD published-case reproduction remains provisional.",
    "Stage 5A has hand-computed spatial-variance tests and an externally checked categorical NTD PSD path. Stage 5B adds manual fuzzy AND/OR memberships, explicit ties, direct theta/phi decomposition, canonical-code invariance, response-overlay recomputation under permutation, CPSD candidate selection, greedy/exhaustive subset searches and missing-row reconstruction. IDSA remains implemented and provisional until pinned external PID fixtures and a published-case reproduction are complete.",
)
readme_path.write_text(readme.rstrip() + "\n", encoding="utf-8")

zh_path = ROOT / "README.zh.md"
zh = zh_path.read_text(encoding="utf-8")
zh_api = """
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
"""
zh = replace_section(
    zh,
    "## 公共接口\n\n```python\n",
    "```\n\n## 统计与开发原则",
    zh_api,
)
zh = zh.replace(
    "- PSMD 的失败层数和实际采用层数均保留；\n",
    "- PSMD 的失败层数和实际采用层数均保留；\n"
    "- 模糊分区保留因子—分层身份并记录并列决策；\n"
    "- PID 保留 theta、phi、隶属度、分区和子集搜索证据；\n"
    "- IDSA 置换时重新计算响应变量驱动的模糊分区；\n",
)
zh = zh.replace(
    "阶段 5A 包括手工空间方差、权重缩放、观测与权重同步重排、缺失样本同步裁剪、孤岛失败、CPSD 恒等、PSMD 候选平均、确定性置换和混合因子 SPADE 测试。分类变量 NTD PSD 路径已完成外部核对；连续 CPSD/PSMD 的正式论文案例仍属于暂定验证。",
    "阶段 5A 已完成手工空间方差测试和分类变量 NTD PSD 外部核对。阶段 5B 增加模糊 AND/OR 隶属度、显式并列规则、theta/phi 直接分解、有序编码不变性、置换时重算模糊分区、CPSD 候选选择、贪心/穷举子集搜索和缺失行重建测试。IDSA 在固定外部 PID 参考输出和正式论文案例完成前仍标记为已实现、暂定验证。",
)
old_links = """
- `docs/models/spade.md`；
- `docs/references/spade-idsa-code-audit.md`；
- `VALIDATION_MATRIX.md`；
- `ROADMAP.md`；
- `HANDOFF_NEXT_CONVERSATION.md`。


- `docs/models/idsa.md`；
- `docs/references/idsa-code-audit.md`。
"""
new_links = """
- `docs/models/spade.md`；
- `docs/models/idsa.md`；
- `docs/references/spade-idsa-code-audit.md`；
- `docs/references/idsa-code-audit.md`；
- `VALIDATION_MATRIX.md`；
- `ROADMAP.md`；
- `HANDOFF_NEXT_CONVERSATION.md`。
"""
zh = zh.replace(old_links, new_links)
zh_path.write_text(zh.rstrip() + "\n", encoding="utf-8")
