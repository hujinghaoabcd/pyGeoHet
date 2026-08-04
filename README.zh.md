# pyGeoHet

**pyGeoHet** 是一个面向空间分层异质性（SSH）分析的研究型 Python 工具箱。项目覆盖经典地理探测器工作流，并将继续扩展离散化、空间依赖、稳健探测、多变量分层、局地解释、类别响应和信息论 SSH 测度。

> **当前状态——阶段 3B 已实现：** q 统计量、四类经典探测器、统一 `GeoDetector` 工作流、六种连续变量分层方法、可审计的 q 引导候选搜索、单变量 `OPGD` 和基于预先准备空间支持的尺度选择均已可用。下一批为 MSD。

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

直接分层支持等间距、分位数、加权 Fisher–Jenks 自然断点、几何间隔、标准差和头尾断裂。结果不会只返回标签，而会保留断点、请求层数、实际层数、各层样本数、缺失行、层数折叠、候选拒绝原因和确定性并列规则。

## 空间尺度 OPGD

候选空间支持必须在上游明确准备。pyGeoHet 负责比较各尺度结果，不会静默聚合栅格、面或点数据。

```python
from pygeohet import SpatialScaleOPGD, compare_spatial_scales

# 比较已完成的因子探测、GeoDetector 或 OPGD 结果。
scale_effects = compare_spatial_scales(
    {
        10: result_10km,
        20: result_20km,
        40: result_40km,
    }
)
print(scale_effects.best_series())
print(scale_effects.factors_frame())

# 或在每个已准备尺度上运行 OPGD。
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

默认规则遵循 2020 年 OPGD 论文：选择解释变量 q 值 90% 分位数最高的空间支持。`significant_only=True` 显式提供旧版 GD 的显著性筛选约定。新版 gdverse 的“显著因子平均 q + LOESS 停止”属于不同估计器，不会被静默替代为默认规则。

也可以分别调用：

```python
from pygeohet import (
    q_statistic,
    stratify,
    evaluate_stratification,
    optimize_stratification,
    compare_spatial_scales,
    factor_detector,
    interaction_detector,
    risk_detector,
    ecological_detector,
    geodetector,
    opgd,
)
```

## 统计与开发原则

- q 直接按中心化平方和计算；
- 缺失行数量和实际样本范围必须可审计；
- 交互探测的三个 q 值使用同一个联合完整样本；
- 叠加层使用元组编码，避免字符串拼接造成类别碰撞；
- 风险探测使用双侧 Welch 检验；
- 生态探测默认采用不依赖因子顺序的双侧 F 检验，并提供显式 `greater` 兼容模式；
- 原始因子层默认至少两个样本，交互叠加形成的单样本单元显式保留，不静默删除；
- 分层结果必须记录断点、实际层数、边界规则、折叠与拒绝证据；
- OPGD 在同一联合样本上保留完整“方法 × 层数”候选表并公开并列规则；
- 空间尺度比较保留所有支持、评分、因子资格判断、失败原因和并列规则；
- 地理支持构建必须在上游明确完成；
- 运行时不调用 R、QGIS 或其他 GeoDetector 实现；
- 方法必须经过解析性质、静态参考、模拟和论文案例四层验证；
- 项目状态和下一对话交接文档是合并前的发布门槛。

## 验证状态

NTD 案例已复现 `gdverse`/`GD` 的因子 q/p 值、三组交互类型和风险显著组合数量。项目不重新分发第三方原始数据，而是提供带 SHA-256 校验的验证脚本。

阶段 3A 与 3B 已具备解析、边界、失败路径和统一工作流测试。分层与空间尺度的跨语言静态基准及公开 OPGD 案例复现仍需补充，因此当前标记为“已实现、暂定验证”，而不是“完全外部验证”。

详细说明见：

- `docs/models/classic-detectors.md`；
- `docs/models/stratification-opgd.md`；
- `docs/models/spatial-scale-opgd.md`；
- `docs/validation/ntd-reference.md`；
- `VALIDATION_MATRIX.md`；
- `ROADMAP.md`；
- `HANDOFF_NEXT_CONVERSATION.md`。
