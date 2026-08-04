"""Shared data validation for SSH statistics."""

from __future__ import annotations

from collections.abc import Mapping
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


@dataclass(frozen=True)
class PreparedJointData:
    """Validated response and multiple factor columns on one complete-case sample."""

    y: np.ndarray
    factors: pd.DataFrame
    dropped_count: int


def coerce_factor_frame(factors: Any) -> pd.DataFrame:
    """Return factors as a shallow pandas data frame with stable column names."""

    if isinstance(factors, pd.DataFrame):
        frame = factors.copy(deep=False)
    elif isinstance(factors, Mapping):
        frame = pd.DataFrame(dict(factors))
    else:
        array = np.asarray(factors, dtype=object)
        if array.ndim == 1:
            frame = pd.DataFrame({"factor": array})
        elif array.ndim == 2:
            names = [f"factor_{index}" for index in range(array.shape[1])]
            frame = pd.DataFrame(array, columns=names)
        else:
            raise InvalidDataError("factors must be one- or two-dimensional")

    names = [str(name) for name in frame.columns]
    if len(set(names)) != len(names):
        raise InvalidDataError(
            "factor column names must be unique after string conversion"
        )
    frame.columns = names
    return frame.reset_index(drop=True)


def prepare_joint_data(
    y: Any,
    factors: Any,
    *,
    missing: MissingPolicy = "drop",
) -> PreparedJointData:
    """Align y and all factor columns, then apply one joint missing-value mask."""

    if missing not in {"drop", "raise"}:
        raise ValueError("missing must be either 'drop' or 'raise'")

    factor_frame = coerce_factor_frame(factors)
    if factor_frame.empty or factor_frame.shape[1] == 0:
        raise InvalidDataError("factors must contain at least one column")

    y_series = pd.Series(y, copy=False, name="y").reset_index(drop=True)
    if y_series.ndim != 1:
        raise InvalidDataError("y must be one-dimensional")
    if len(y_series) != len(factor_frame):
        raise InvalidDataError("y and factors must have equal length")
    if len(y_series) == 0:
        raise InvalidDataError("y and factors must not be empty")

    y_numeric = pd.to_numeric(y_series, errors="raise").astype(float)
    missing_mask = y_numeric.isna() | factor_frame.isna().any(axis=1)
    if missing == "raise" and bool(missing_mask.any()):
        raise MissingDataError("missing values are present in y or factors")

    keep = ~missing_mask
    y_clean = y_numeric.loc[keep].to_numpy(dtype=float, copy=True)
    factors_clean = factor_frame.loc[keep].reset_index(drop=True)
    dropped_count = int(missing_mask.sum())

    if y_clean.size == 0:
        raise InvalidDataError("no complete observations remain")
    if not bool(np.isfinite(y_clean).all()):
        raise InvalidDataError(
            "y must contain only finite values after missing handling"
        )

    return PreparedJointData(
        y=y_clean,
        factors=factors_clean,
        dropped_count=dropped_count,
    )


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

    y_series = pd.Series(y, copy=False, name="y").reset_index(drop=True)
    x_series = pd.Series(strata, copy=False, name="strata").reset_index(drop=True)
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
        raise InvalidDataError(
            "y must contain only finite values after missing handling"
        )

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
