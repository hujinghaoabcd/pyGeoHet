"""Minimal installed-package example for Stage 1."""

import pandas as pd

from pygeohet import FactorDetector, q_statistic

frame = pd.DataFrame(
    {
        "y": [1.0, 1.2, 4.8, 5.0, 2.0, 2.1],
        "land_use": ["A", "A", "B", "B", "C", "C"],
        "region": ["north", "north", "south", "south", "north", "south"],
    }
)

single = q_statistic(frame["y"], frame["land_use"])
print(single.summary())

multiple = FactorDetector().fit(frame["y"], frame[["land_use", "region"]])
print(multiple.summary())
