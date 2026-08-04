# pyGeoHet

**pyGeoHet** 是一个面向空间分层异质性（SSH）分析的研究型 Python 工具箱。项目覆盖经典地理探测器工作流，并将继续扩展离散化、空间依赖、稳健探测、多变量分层、局地解释、类别响应和信息论 SSH 测度。

> **当前状态——阶段 2 已完成：** q 统计量、因子探测器、交互作用探测器、风险探测器、生态探测器以及统一 `GeoDetector` 工作流均已实现并完成验证。阶段 3 将开发分层与最优离散化。

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

也可以分别调用：

```python
from pygeohet import (
    q_statistic,
    factor_detector,
    interaction_detector,
    risk_detector,
    ecological_detector,
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
- 运行时不调用 R、QGIS 或其他 GeoDetector 实现；
- 方法必须经过解析性质、静态参考、模拟和论文案例四层验证；
- 项目状态和下一对话交接文档是合并前的发布门槛。

NTD 案例已复现 `gdverse`/`GD` 的因子 q/p 值、三组交互类型和风险显著组合数量。项目不重新分发第三方原始数据，而是提供带 SHA-256 校验的验证脚本。

详细说明见 `docs/models/classic-detectors.md`、`docs/validation/ntd-reference.md`、`VALIDATION_MATRIX.md` 和 `ROADMAP.md`。
