"""Multiscale discretization with an auditable coarse-to-fine search path."""

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
print(result.stratification.to_series())
