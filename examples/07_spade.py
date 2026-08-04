"""Spatial variance, PSD, CPSD, PSMD and SPADE example."""

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
distances = np.abs(coordinates[:, None] - coordinates[None, :])
weights = np.zeros_like(distances)
mask = distances > 0.0
weights[mask] = 1.0 / distances[mask] ** 2

y = np.asarray([0, 0, 1, 1, 4, 4, 5, 5, 9, 9, 10, 10], dtype=float)
region = np.repeat(["west", "centre", "east"], 4)
trend = coordinates.copy()

print(spatial_variance(y, weights).summary())
print(power_spatial_determinant(y, region, weights).summary())

trend_labels = np.repeat([1, 2, 3], 4)
print(compensated_spatial_determinant(y, trend, trend_labels, weights).summary())

psmd = multilevel_spatial_determinant(
    y,
    trend,
    weights,
    n_strata=(2, 3, 4),
    method="quantile",
)
print(psmd.summary())
print(psmd.candidates_frame().to_string(index=False))

factors = pd.DataFrame({"trend": trend, "region": region})
result = SPADE(n_strata=(2, 3, 4), method="quantile").fit(
    y,
    factors,
    weights,
    continuous_factors=("trend",),
)
print(result.summary())
