"""Run all four classical geographical detectors."""

import pandas as pd

from pygeohet import GeoDetector

frame = pd.DataFrame(
    {
        "y": [1.0, 1.2, 2.0, 2.2, 4.0, 4.2, 5.0, 5.2],
        "land_use": ["A", "A", "B", "B", "A", "A", "B", "B"],
        "region": [
            "north",
            "north",
            "north",
            "north",
            "south",
            "south",
            "south",
            "south",
        ],
    }
)

result = GeoDetector().fit(frame["y"], frame[["land_use", "region"]])

print("Factor detector")
print(result.factor.to_frame())
print("\nInteraction detector")
print(result.interaction.to_frame())
print("\nRisk detector")
print(result.risk.comparisons_frame())
print("\nEcological detector")
print(result.ecological.to_frame())
