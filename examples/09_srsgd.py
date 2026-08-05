"""Spatial rough set geographical detector example for a nominal target."""

import numpy as np
import pandas as pd

from pygeohet import SRSGeoDetector, spatial_rough_set_measure

# Figure 1 information system from Bai et al. (2022).
table = pd.DataFrame(
    {
        "a1": ["a", "b", "b", "b", "b", "c", "c", "d", "c", "a", "a"],
        "a2": ["b", "a", "a", "c", "c", "b", "c", "c", "b", "b", "b"],
        "a3": ["a", "a", "a", "a", "a", "c", "b", "b", "c", "a", "a"],
        "target": ["a", "a", "a", "b", "a", "a", "b", "b", "b", "b", "b"],
    }
)

adjacency = np.asarray(
    [
        [0, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0],
        [1, 0, 1, 1, 1, 0, 0, 0, 0, 1, 0],
        [0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0],
        [1, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0],
        [1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1],
        [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0],
        [1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1],
        [0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0],
    ],
    dtype=int,
)

single = spatial_rough_set_measure(
    table["target"],
    table[["a1"]],
    adjacency,
)
print(single.summary())
print(single.local_frame().to_string(index=False))
print()

result = SRSGeoDetector(baseline="a1").fit(
    table["target"],
    table[["a1", "a2", "a3"]],
    adjacency,
)
print(result.summary())
print("\nFactor detector")
print(result.factor.to_frame().to_string(index=False))
print("\nEcological detector")
print(result.ecological.to_frame().to_string(index=False))
print("\nInteraction detector")
print(result.interaction.to_frame().to_string(index=False))
