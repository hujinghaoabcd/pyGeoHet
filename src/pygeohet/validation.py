"""Shared data validation for SSH statistics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

import numpy as np
import pandas as pd

from pygeohet.exceptions import (
    InvalidDataError,
    MissingDataError,
    SmallStratumError,
)

MissingPolicy = Literal["drop", "raise"]


@dataclass(frozen=True)
class PreparedFactorData:
    """Validated response and categorical stratum labels."""

    y: np.ndarray
    strata: np.ndarray
    counts: pd.Series
    dropped_count: int


def prepare_factor_data(
    y: Any,
    strata: Any,
    *,
    missing: MissingPolicy = "drop",
    min_stratum_size: int = 2,
) -> PreparedFactorData:
    """Return aligned complete cases and validated stratum counts."""

    if missing not in {"drop", "raise"}:
        raise ValueError("missing must be either 'drop' or 'raise'")
    if isinstance(min_stratum_size, bool) or min_stratum_size < 1:
        raise ValueError("min_stratum_size must be a positive integer")

    y_series = pd.Series(y, copy=False, name="y")
    x_series = pd.Series(strata, copy=False, name="strata")
    if y_series.ndim != 1 or x_series.ndim != 1:
        raise InvalidDataError("y and strata must be one-dimensional")
    if len(y_series) != len(x_series):
        raise InvalidDataError("y and strata must have equal length")
    if len(y_series) == 0:
        raise InvalidDataError("y and strata must not be empty")

    y_numeric = pd.to_numeric(y_series, errors="raise").astype(float)
    missing_mask = y_numeric.isna() | x_series.isna()
    if missing == "raise" and bool(missing_mask.any()):
        raise MissingDataError("missing values are present in y or strata")

    keep = ~missing_mask
    y_clean = y_numeric.loc[keep].to_numpy(dtype=float, copy=True)
    x_clean = x_series.loc[keep].to_numpy(copy=True)
    dropped_count = int(missing_mask.sum())

    if y_clean.size == 0:
        raise InvalidDataError("no complete observations remain")
    if not bool(np.isfinite(y_clean).all()):
        raise InvalidDataError("y must contain only finite values after missing handling")

    counts = pd.Series(x_clean, copy=False).value_counts(sort=False, dropna=False)
    if len(counts) < 2:
        raise InvalidDataError("at least two strata are required")

    too_small = counts[counts < min_stratum_size]
    if not too_small.empty:
        details = ", ".join(
            f"{label!r}: {int(count)}" for label, count in too_small.items()
        )
        raise SmallStratumError(
            f"each stratum must contain at least {min_stratum_size} observations; "
            f"too small: {details}"
        )

    return PreparedFactorData(
        y=y_clean,
        strata=x_clean,
        counts=counts,
        dropped_count=dropped_count,
    )
