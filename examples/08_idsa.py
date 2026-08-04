"""Fuzzy overlay, fixed-strata PID and integrated IDSA example."""

import numpy as np
import pandas as pd

from pygeohet import IDSA, fuzzy_overlay, power_interactive_determinant

base_y = np.asarray([0.0, 2.0, 8.0, 10.0])
y = np.tile(base_y, 4)
discrete = pd.DataFrame(
    {
        "temperature_zone": np.tile([1, 1, 2, 2], 4),
        "moisture_zone": np.tile([1, 2, 1, 2], 4),
    }
)
weights = np.ones((len(y), len(y)), dtype=float)
np.fill_diagonal(weights, 0.0)

overlay = fuzzy_overlay(y, discrete, operation="and")
print(overlay.summary())
print(overlay.risk_frame().to_string(index=False))
print()

pid = power_interactive_determinant(y, discrete, weights)
print(pid.summary())
print(pid.information_frame().to_string(index=False))
print()

x1_base = np.repeat(np.arange(4, dtype=float), 4)
x2_base = np.tile(np.repeat(np.arange(2, dtype=float), 2), 4)
x3_base = np.tile(np.arange(4, dtype=float), 4)
x1 = np.tile(x1_base, 4)
x2 = np.tile(x2_base, 4)
x3 = np.tile(x3_base, 4)
response = 4.0 * x1 + 2.0 * x2 + 0.5 * x3
continuous = pd.DataFrame({"x1": x1, "x2": x2, "x3": x3})
spatial_weights = np.ones((len(response), len(response)), dtype=float)
np.fill_diagonal(spatial_weights, 0.0)

result = IDSA(
    methods=("quantile", "natural_breaks"),
    n_strata=(2, 3),
    search="greedy",
).fit(response, continuous, spatial_weights)
print(result.summary())
print(result.discretizations_frame().to_string(index=False))
print(result.combinations_frame().to_string(index=False))
