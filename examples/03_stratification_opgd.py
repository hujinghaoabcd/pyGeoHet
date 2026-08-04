"""Continuous-variable stratification and OPGD example."""

from __future__ import annotations

import pandas as pd

from pygeohet import OPGD, optimize_stratification, stratify


def main() -> None:
    y = [
        1.0,
        1.1,
        0.9,
        1.2,
        5.0,
        5.1,
        4.9,
        5.2,
        10.0,
        10.1,
        9.9,
        10.2,
    ]
    factors = pd.DataFrame(
        {
            "elevation": [
                10.0,
                11.0,
                12.0,
                13.0,
                40.0,
                41.0,
                42.0,
                43.0,
                80.0,
                81.0,
                82.0,
                83.0,
            ],
            "precipitation": [
                100.0,
                102.0,
                104.0,
                106.0,
                140.0,
                142.0,
                144.0,
                146.0,
                200.0,
                202.0,
                204.0,
                206.0,
            ],
        }
    )

    one = stratify(factors["elevation"], method="natural_breaks", n_strata=3)
    print(one.summary())
    print()

    search = optimize_stratification(
        y,
        factors["elevation"],
        methods=["equal_interval", "quantile", "natural_breaks"],
        n_strata=[2, 3, 4],
    )
    print(search.best_series().to_string())
    print()
    print(search.candidates_frame().to_string(index=False))
    print()

    result = OPGD(
        methods=["equal_interval", "quantile", "natural_breaks"],
        n_strata=[2, 3, 4],
    ).fit(y, factors)
    print(result.optimal_frame().to_string(index=False))
    print()
    print(result.detector.factor.to_frame().to_string(index=False))


if __name__ == "__main__":
    main()
