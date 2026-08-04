# pyGeoHet

**pyGeoHet** 是一个面向空间分层异质性（SSH）分析的研究型 Python 工具箱。项目覆盖经典地理探测器工作流，并扩展可审计离散化、空间尺度比较、多尺度搜索、稳健变化点探测和空间方差分解。

> **当前状态——阶段 5B 已实现：** q 统计量、四类经典探测器、统一 `GeoDetector`、六种连续变量分层方法、`OPGD`、显式空间支持尺度 OPGD、`MSD`、稳健离散化、`RGD`、`RID`、空间方差、PSD、CPSD、PSMD 和 `SPADE` 均已可用。模糊交互分区和 IDSA 已实现；下一阶段进入分类响应与信息一致性 SSH。

## 开发安装

```bash
python -m pip install -e ".[test]"
```

## 经典地理探测器

```python
import pandas as pd
from pygeohet import GeoDetector

frame = pd.DataFrame(
    {
        "y": [1.0, 1.2, 2.0, 2.2, 4.0, 4.2, 5.0, 5.2],
        "land_use": ["A", "A", "B", "B", "A", "A", "B", "B"],
        "region": ["north", "north", "north", "north", "south", "south", "south", "south"],
    }
)

result = GeoDetector().fit(frame["y"], frame[["land_use", "region"]])
print(result.factor.to_frame())
print(result.interaction.to_frame())
print(result.risk.comparisons_frame())
print(result.ecological.to_frame())
```

## 连续变量分层与 OPGD

```python
from pygeohet import OPGD, optimize_stratification

y = [1.0, 1.1, 1.2, 5.0, 5.1, 5.2, 10.0, 10.1, 10.2]
x = [10.0, 11.0, 12.0, 40.0, 41.0, 42.0, 80.0, 81.0, 82.0]

search = optimize_stratification(
    y,
    x,
    methods=["equal_interval", "quantile", "natural_breaks"],
    n_strata=[2, 3, 4],
)
print(search.best_series())
print(search.candidates_frame())
```

直接分层支持等间距、分位数、加权 Fisher–Jenks 自然断点、几何间隔、标准差和头尾断裂。结果保留断点、请求层数、实际层数、样本数、缺失行、层数折叠、候选拒绝原因和确定性并列规则。

## 空间尺度 OPGD

候选空间支持必须在上游明确准备。pyGeoHet 只比较各尺度结果，不会静默聚合栅格、面或点数据。

```python
from pygeohet import SpatialScaleOPGD, compare_spatial_scales

scale_effects = compare_spatial_scales(
    {10: result_10km, 20: result_20km, 40: result_40km}
)
print(scale_effects.best_series())
```

默认规则遵循 2020 年 OPGD 论文：选择解释变量 q 值 90% 分位数最高的空间支持。旧版 GD 的显著性筛选和新版 gdverse 的 LOESS 规则均作为不同约定显式区分。

## 多尺度离散化 MSD

MSD 使用响应变量和 q 搜索连续解释变量的有序切点。这里的“尺度”是解释变量数值网格分辨率，不是地理观测支持尺度。

```python
import numpy as np
from pygeohet import MSD

x = np.arange(100, dtype=float)
y = np.select(
    [x < 18, x < 41, x < 64, x < 85],
    [0.0, 10.0, 20.0, 30.0],
    default=40.0,
)

result = MSD(
    n_strata=5,
    upscale=6,
    buffer_scales=(3, 1),
    epsilon=1,
    base_resolution=1.0,
).fit(y, x)
print(result.steps_frame())
```

`upscale=1` 表示在全部唯一值边界上执行精确全局搜索。粗到细搜索保留每个尺度的候选、切点、q、层内平方和和失败证据。

## 稳健离散化、RGD 与 RID

稳健离散化先按连续解释变量排列响应序列，再寻找连续方差变化点。固定分区数后，pyGeoHet 用动态规划精确最小化区域内平方和。其 B 值在数值上等于稳健标签上的 q。

```python
import numpy as np
import pandas as pd
from pygeohet import RGD, RID, robust_discretize

x = np.arange(24, dtype=float)
y = np.repeat([0.0, 4.0, 9.0, 13.0], 6)
fixed = robust_discretize(y, x, n_strata=4)

factors = pd.DataFrame(
    {
        "trend": x,
        "cycle": np.tile(np.arange(6, dtype=float), 4),
    }
)
rgd_result = RGD(n_strata=range(2, 6)).fit(y, factors)
rid_result = RID(n_strata=range(2, 5), selection="max_b").fit(y, factors)
```

相同解释变量值绝不会被拆分；严格单调变换保持同一个有序问题；区域数选择与数值内核分离；运行时不依赖 `ruptures`、R 或 gdverse。

## 空间方差与 SPADE

阶段 5A 接受已经准备好的非负方阵空间权重。核心不会静默决定几何代表点、CRS、距离单位、邻域、行标准化或对称化。

```python
import numpy as np
import pandas as pd
from pygeohet import (
    SPADE,
    IDSA,
    IDSA,
    compensated_spatial_determinant,
    multilevel_spatial_determinant,
    fuzzy_overlay,
    power_interactive_determinant,
    optimize_spatial_discretization,
    fuzzy_overlay,
    power_interactive_determinant,
    optimize_spatial_discretization,
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

`theta` 是模糊分区下响应变量的 PSD，`phi` 表示所有有序离散因子的空间信息保留能力，最终 `PID = theta / phi`。置换检验会在每次打乱响应变量后重新计算风险、隶属度和模糊分区。


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
    q_statistic,
    spatial_variance,
    power_spatial_determinant,
    compensated_spatial_determinant,
    multilevel_spatial_determinant,
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
- 外部 R、Python、QGIS、Notebook 和 GIS 实现不作为运行时后端；
- 项目状态、验证矩阵和交接文档是合并门槛。

## 验证状态

经典工作流已复现 NTD 因子、交互和风险参考输出。MSD 与独立穷举程序一致；稳健分区与独立暴力枚举一致，并验证 B=q。

阶段 5A 包括手工空间方差、权重缩放、观测与权重同步重排、缺失样本同步裁剪、孤岛失败、CPSD 恒等、PSMD 候选平均、确定性置换和混合因子 SPADE 测试。分类变量 NTD PSD 路径已完成外部核对；连续 CPSD/PSMD 的正式论文案例仍属于暂定验证。

详细说明见：

- `docs/models/classic-detectors.md`；
- `docs/models/stratification-opgd.md`；
- `docs/models/spatial-scale-opgd.md`；
- `docs/models/msd.md`；
- `docs/models/robust-rgd-rid.md`；
- `docs/models/spade.md`；
- `docs/references/spade-idsa-code-audit.md`；
- `VALIDATION_MATRIX.md`；
- `ROADMAP.md`；
- `HANDOFF_NEXT_CONVERSATION.md`。


- `docs/models/idsa.md`；
- `docs/references/idsa-code-audit.md`。
