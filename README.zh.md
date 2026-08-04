# pyGeoHet

**pyGeoHet** 是一个面向空间分层异质性（SSH）分析的研究型 Python 工具箱。项目覆盖经典地理探测器工作流，并扩展可审计离散化、空间尺度比较、多尺度搜索和稳健变化点探测。

> **当前状态——阶段 4 已实现：** q 统计量、四类经典探测器、统一 `GeoDetector`、六种连续变量分层方法、单变量 `OPGD`、显式空间支持尺度 OPGD、多尺度离散化 `MSD`、精确稳健离散化、`RGD` 和 `RID` 均已可用。下一阶段将开发 SPADE、IDSA 等空间依赖探测方法。

## 开发安装

```bash
python -m pip install -e ".[test]"
```

## 完整经典工作流

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
import pandas as pd
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

factors = pd.DataFrame(
    {
        "elevation": x,
        "precipitation": [100, 101, 102, 140, 141, 142, 200, 201, 202],
    }
)
result = OPGD(
    methods=["equal_interval", "quantile", "natural_breaks"],
    n_strata=[2, 3, 4],
).fit(y, factors)

print(result.optimal_frame())
print(result.detector.factor.to_frame())
```

直接分层支持等间距、分位数、加权 Fisher–Jenks 自然断点、几何间隔、标准差和头尾断裂。结果保留断点、请求层数、实际层数、各层样本数、缺失行、层数折叠、候选拒绝原因和确定性并列规则。

## 空间尺度 OPGD

候选空间支持必须在上游明确准备。pyGeoHet 负责比较各尺度结果，不会静默聚合栅格、面或点数据。

```python
from pygeohet import SpatialScaleOPGD, compare_spatial_scales

scale_effects = compare_spatial_scales(
    {
        10: result_10km,
        20: result_20km,
        40: result_40km,
    }
)
print(scale_effects.best_series())
print(scale_effects.factors_frame())

model = SpatialScaleOPGD(
    methods=["equal_interval", "quantile", "natural_breaks"],
    n_strata=[2, 3, 4],
)
scale_result = model.fit(
    {
        10: (y_10km, factors_10km),
        20: (y_20km, factors_20km),
        40: (y_40km, factors_40km),
    }
)
print(scale_result.scale_effects.best_series())
```

默认规则遵循 2020 年 OPGD 论文：选择解释变量 q 值 90% 分位数最高的空间支持。`significant_only=True` 显式提供旧版 GD 的显著性筛选约定。新版 gdverse 的“显著因子平均 q + LOESS 停止”属于不同估计器，不会被静默替代。

## 多尺度离散化 MSD

MSD 使用响应变量和 q 直接搜索一个连续解释变量的有序切点。这里的“尺度”是解释变量数值网格分辨率，不是地理观测支持尺度。

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

print(result.summary())
print(result.steps_frame())
```

`upscale=1` 表示在全部观测唯一值边界上执行精确全局搜索。粗到细搜索保留每个尺度的候选、选中切点、q、层内平方和与失败证据。

## 稳健离散化、RGD 与 RID

稳健离散化先按连续解释变量排列响应序列，再寻找连续的方差变化点分区。给定区域数 `K` 后，pyGeoHet 使用动态规划精确最小化所有区域的响应层内平方和。对应 B 值为：

```text
B = 1 - 稳健区域层内平方和 / 总平方和
```

其数值等于在稳健分层标签上计算的 q。

```python
import numpy as np
import pandas as pd
from pygeohet import RGD, RID, robust_discretize

x = np.arange(24, dtype=float)
y = np.repeat([0.0, 4.0, 9.0, 13.0], 6)

fixed = robust_discretize(y, x, n_strata=4)
print(fixed.summary())
print(fixed.cut_points)
print(fixed.b_value)

factors = pd.DataFrame(
    {
        "trend": x,
        "cycle": np.tile(np.arange(6, dtype=float), 4),
    }
)

rgd_result = RGD(
    n_strata=range(2, 6),
    selection="marginal_gain",
    increase_rate=0.05,
).fit(y, factors)
print(rgd_result.optimal_frame())
print(rgd_result.candidates_frame("trend"))

rid_result = RID(
    n_strata=range(2, 5),
    selection="max_b",
).fit(y, factors)
print(rid_result.interaction.to_frame())
```

稳健方法的重要约定：

- 相同解释变量值绝不会被拆分到不同区域；
- 对解释变量进行严格单调变换不会改变有序分区问题；
- `marginal_gain` 和 `max_b` 是两个显式区域数选择规则；
- 切点值归入后一分区；
- 缺失行标签会回填到原始行位置并记为 `None`；
- RGD 与 RID 复用已经测试的经典因子探测和交互探测实现；
- `ruptures`、R 和 gdverse 只作为公式和行为参考，不是运行时依赖。

实现保留论文的核心估计量和变化点逻辑，但代码结构、验证、动态规划和 API 均为独立实现，不机械照抄作者或 gdverse 源码。

## 公共接口

```python
from pygeohet import (
    GeoDetector,
    OPGD,
    SpatialScaleOPGD,
    MSD,
    RGD,
    RID,
    q_statistic,
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
)
```

## 统计与开发原则

- q 直接按中心化平方和计算；
- 缺失行数量和实际样本范围必须可审计；
- 交互探测的三个 q 值使用同一个联合完整样本；
- 叠加层使用元组编码，避免字符串拼接造成类别碰撞；
- 风险探测使用双侧 Welch 检验；
- 生态探测默认采用不依赖因子顺序的双侧 F 检验，并提供显式 `greater` 兼容模式；
- 原始因子层默认至少两个样本，交互叠加形成的自然单样本单元显式保留；
- 分层结果记录断点、实际层数、边界规则、折叠与拒绝证据；
- OPGD 保留完整“方法 × 层数”候选表和并列规则；
- 空间尺度比较保留所有支持、评分、因子资格、失败原因和并列规则；
- MSD 将地理支持尺度与解释变量数值网格尺度严格区分；
- 稳健离散化使用稳定排序、重复值安全边界、精确 SSE 优化和确定性变化点并列规则；
- 模型复杂度选择与数值内核分离，不做隐藏自动选择；
- 运行时不调用 R、QGIS、gdverse 或作者 Notebook；
- 项目状态、验证矩阵和下一对话交接文档是合并门槛。

## 验证状态

经典工作流已复现 GD/gdverse NTD 参考结果中的因子 q/p 值、交互类型和风险显著组合数量。

阶段 3A–3C 已具备解析、边界、失败路径和统一工作流测试。MSD 与独立穷举程序在小问题上得到相同全局最优解。阶段 4 的稳健离散化与独立暴力枚举一致，保持秩等价解，不拆分相同解释变量值，正确重建缺失行，并验证 RGD 的 B 值等于因子 q。

阶段 3 和阶段 4 当前均标记为 **已实现、暂定验证**。在固定外部版本、生成静态参考输出和完成正式论文案例复现前，不宣称完全外部一致。

详细说明见：

- `docs/models/classic-detectors.md`；
- `docs/models/stratification-opgd.md`；
- `docs/models/spatial-scale-opgd.md`；
- `docs/models/msd.md`；
- `docs/models/robust-rgd-rid.md`；
- `docs/references/msd-code-audit.md`；
- `docs/references/robust-code-audit.md`；
- `docs/validation/ntd-reference.md`；
- `VALIDATION_MATRIX.md`；
- `ROADMAP.md`；
- `HANDOFF_NEXT_CONVERSATION.md`。
