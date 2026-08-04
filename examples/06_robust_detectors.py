"""Robust discretization, RGD and RID example."""

import numpy as np
import pandas as pd

from pygeohet import RGD, RID, robust_discretize

x = np.arange(36, dtype=float)
secondary = np.tile(np.arange(9, dtype=float), 4)
y = np.select(
    [x < 9, x < 18, x < 27],
    [1.0, 5.0, 10.0],
    default=15.0,
) + 0.15 * secondary

single = robust_discretize(y, x, n_strata=4)
print(single.summary())
print()

factors = pd.DataFrame({"trend": x, "secondary": secondary})
rgd_result = RGD(
    n_strata=range(2, 6),
    selection="marginal_gain",
    increase_rate=0.05,
).fit(y, factors)
print(rgd_result.optimal_frame().to_string(index=False))
print()
print(rgd_result.candidates_frame("trend").to_string(index=False))
print()

rid_result = RID(
    n_strata=range(2, 5),
    selection="max_b",
).fit(y, factors)
print(rid_result.interaction.to_frame().to_string(index=False))
