"""Prepared spatial-scale comparison with OPGD at every scale."""

from __future__ import annotations

import pandas as pd

from pygeohet import SpatialScaleOPGD


def main() -> None:
    y = [1.0] * 4 + [5.0] * 4 + [10.0] * 4
    fine_factors = pd.DataFrame(
        {
            "elevation": [
                0.0,
                0.1,
                0.2,
                0.3,
                5.0,
                5.1,
                5.2,
                5.3,
                10.0,
                10.1,
                10.2,
                10.3,
            ],
            "precipitation": [
                1.0,
                1.1,
                1.2,
                1.3,
                6.0,
                6.1,
                6.2,
                6.3,
                11.0,
                11.1,
                11.2,
                11.3,
            ],
        }
    )
    coarse_factors = pd.DataFrame(
        {
            "elevation": [0.0, 1.0, 2.0, 3.0] * 3,
            "precipitation": [3.0, 2.0, 1.0, 0.0] * 3,
        }
    )

    result = SpatialScaleOPGD(
        methods=["equal_interval", "quantile", "natural_breaks"],
        n_strata=[2, 3],
    ).fit(
        {
            10: (y, fine_factors),
            20: (y, coarse_factors),
        }
    )

    print(result.scale_effects.summary())
    print()
    print(result.candidates_frame().to_string(index=False))
    print()
    print(result.factors_frame().to_string(index=False))


if __name__ == "__main__":
    main()
