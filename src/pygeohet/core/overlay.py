"""Collision-safe categorical overlay utilities."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from pygeohet.exceptions import InvalidDataError


def categorical_overlay(first: Any, second: Any) -> np.ndarray:
    """Combine two categorical vectors using tuple labels rather than strings."""

    first_series = pd.Series(first, copy=False).reset_index(drop=True)
    second_series = pd.Series(second, copy=False).reset_index(drop=True)
    if first_series.ndim != 1 or second_series.ndim != 1:
        raise InvalidDataError("overlay inputs must be one-dimensional")
    if len(first_series) != len(second_series):
        raise InvalidDataError("overlay inputs must have equal length")
    if len(first_series) == 0:
        raise InvalidDataError("overlay inputs must not be empty")
    if bool(first_series.isna().any() or second_series.isna().any()):
        raise InvalidDataError("overlay inputs must not contain missing values")

    overlay = np.empty(len(first_series), dtype=object)
    overlay[:] = list(zip(first_series.tolist(), second_series.tolist(), strict=True))
    return overlay
