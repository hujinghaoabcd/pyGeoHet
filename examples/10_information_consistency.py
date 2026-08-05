"""Nominal and continuous information-consistency SSH examples."""

import numpy as np
import pandas as pd

from pygeohet import (
    InformationConsistency,
    continuous_information_consistency,
    nominal_information_consistency,
)

nominal_target = np.asarray(["low", "low", "high", "high"] * 4)
nominal_strata = np.asarray(["a", "a", "b", "b"] * 4)
nominal = nominal_information_consistency(
    nominal_target,
    nominal_strata,
    permutations=99,
    random_state=42,
)
print(nominal.summary())
print(nominal.contingency_frame().to_string(index=False))
print()

continuous_target = np.asarray(
    [0.0, 0.2, 0.8, 1.0, 5.0, 5.2, 5.8, 6.0] * 3,
    dtype=float,
)
continuous_strata = np.asarray(["west"] * 4 + ["east"] * 4) repeat = None
