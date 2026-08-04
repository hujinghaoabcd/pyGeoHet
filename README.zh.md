# pyGeoHet

**pyGeoHet** 是一个面向空间分层异质性（SSH）分析的研究型 Python 工具箱。项目不仅实现经典地理探测器，还将逐步覆盖离散化与尺度优化、空间依赖、稳健探测、多变量分层、局地解释、类别响应和信息论 SSH 测度。

> **当前状态——阶段 1：** 已完成项目骨架、数值约定、验证体系、q 统计量和因子探测器。其余方法按照十阶段路线开发。

## 开发安装

```bash
python -m pip install -e ".[test]"
```

## 快速示例

```python
import pandas as pd
from pygeohet import FactorDetector, q_statistic

frame = pd.DataFrame(
    {
        "y": [1.0, 1.2, 4.8, 5.0, 2.0, 2.1],
        "land_use": ["A", "A", "B", "B", "C", "C"],
        "region": ["north", "north", "south", "south", "north", "south"],
    }
)

print(q_statistic(frame["y"], frame["land_use"]).summary())
print(FactorDetector().fit(frame["y"], frame[["land_use", "region"]]).to_frame())
```

## 不可妥协的设计原则

- 直接按平方和定义实现 q，避免方差自由度口径不清；
- 不静默删除单样本层，不自动填补缺失值；
- 结果对象保留样本数、层数和完整方差分解；
- 经典方法与扩展方法保持统计含义分离；
- 使用解析性质、跨语言静态基准、模拟和论文案例四层验证；
- 每一开发批次同步维护项目状态、路线图和下一对话交接文档；
- 运行时不依赖 R、QGIS 或其他 GeoDetector 软件。

详细路线见 `ROADMAP.md`，数值规则见 `docs/theory/numerical-conventions.md`。
