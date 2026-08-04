"""Numerical core for SPADE PSD and CPSD statistics."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from pygeohet.exceptions import InvalidDataError, MissingDataError, SmallStratumError
from pygeohet.models.spade_results import (
    CompensatedSpatialDeterminantResult,
    PowerSpatialDeterminantResult,
    SpatialStratumVariance,
)
from pygeohet.spatial.variance import (
    SpatialVarianceResult,
    _coerce_weight_matrix,
    _spatial_variance_clean,
)
from pygeohet.validation import MissingPolicy


def validate_permutations(permutations: int) -> int:
    if isinstance(permutations, bool) or not isinstance(
        permutations, (int, np.integer)
    ):
        raise ValueError("permutations must be an integer")
    count = int(permutations)
    if count < 0:
        raise ValueError("permutations must be nonnegative")
    return count


def validate_minimum(min_stratum_size: int) -> int:
    if isinstance(min_stratum_size, bool) or not isinstance(
        min_stratum_size, (int, np.integer)
    ):
        raise ValueError("min_stratum_size must be an integer")
    minimum = int(min_stratum_size)
    if minimum < 2:
        raise ValueError("min_stratum_size must be at least 2 for spatial variance")
    return minimum


def _prepare_psd_sample(
    y: Any,
    strata: Any,
    weights: Any,
    *,
    missing: MissingPolicy,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, int]:
    if missing not in {"drop", "raise"}:
        raise ValueError("missing must be either 'drop' or 'raise'")
    y_series = pd.Series(y, copy=False, name="y").reset_index(drop=True)
    h_series = pd.Series(strata, copy=False, name="strata").reset_index(drop=True)
    if y_series.ndim != 1 or h_series.ndim != 1:
        raise InvalidDataError("y and strata must be one-dimensional")
    if len(y_series) != len(h_series):
        raise InvalidDataError("y and strata must have equal length")
    if len(y_series) == 0:
        raise InvalidDataError("y and strata must not be empty")

    matrix = _coerce_weight_matrix(weights, len(y_series))
    y_numeric = pd.to_numeric(y_series, errors="raise").astype(float)
    missing_mask = y_numeric.isna() | h_series.isna()
    if missing == "raise" and bool(missing_mask.any()):
        raise MissingDataError("missing values are present in y or strata")
    used = np.flatnonzero(~missing_mask.to_numpy(dtype=bool))
    y_clean = y_numeric.iloc[used].to_numpy(dtype=float, copy=True)
    strata_clean = h_series.iloc[used].to_numpy(copy=True)
    if y_clean.size < 2:
        raise InvalidDataError("at least two complete observations are required")
    if not bool(np.isfinite(y_clean).all()):
        raise InvalidDataError("y must contain only finite values")
    return (
        y_clean,
        strata_clean,
        matrix[np.ix_(used, used)].copy(),
        used,
        int(missing_mask.sum()),
    )


def prepare_cpsd_sample(
    y: Any,
    x: Any,
    strata: Any,
    weights: Any,
    *,
    missing: MissingPolicy,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, int]:
    if missing not in {"drop", "raise"}:
        raise ValueError("missing must be either 'drop' or 'raise'")
    y_series = pd.Series(y, copy=False, name="y").reset_index(drop=True)
    x_series = pd.Series(x, copy=False, name="x").reset_index(drop=True)
    h_series = pd.Series(strata, copy=False, name="strata").reset_index(drop=True)
    if len(y_series) != len(x_series) or len(y_series) != len(h_series):
        raise InvalidDataError("y, x and strata must have equal length")
    if len(y_series) == 0:
        raise InvalidDataError("y, x and strata must not be empty")

    matrix = _coerce_weight_matrix(weights, len(y_series))
    y_numeric = pd.to_numeric(y_series, errors="raise").astype(float)
    x_numeric = pd.to_numeric(x_series, errors="raise").astype(float)
    missing_mask = y_numeric.isna() | x_numeric.isna() | h_series.isna()
    if missing == "raise" and bool(missing_mask.any()):
        raise MissingDataError("missing values are present in y, x or strata")
    used = np.flatnonzero(~missing_mask.to_numpy(dtype=bool))
    y_clean = y_numeric.iloc[used].to_numpy(dtype=float, copy=True)
    x_clean = x_numeric.iloc[used].to_numpy(dtype=float, copy=True)
    strata_clean = h_series.iloc[used].to_numpy(copy=True)
    if y_clean.size < 2:
        raise InvalidDataError("at least two complete observations are required")
    if not bool(np.isfinite(y_clean).all()) or not bool(np.isfinite(x_clean).all()):
        raise InvalidDataError("y and x must contain only finite values")
    return (
        y_clean,
        x_clean,
        strata_clean,
        matrix[np.ix_(used, used)].copy(),
        used,
        int(missing_mask.sum()),
    )


def _spatial_variance_result(
    values: np.ndarray,
    weights: np.ndarray,
    *,
    allow_islands: bool,
    used_indices: tuple[int, ...],
    dropped_count: int,
) -> SpatialVarianceResult:
    value, numerator, audit = _spatial_variance_clean(
        values,
        weights,
        allow_islands=allow_islands,
    )
    return SpatialVarianceResult(
        value=value,
        numerator=numerator,
        weight_sum=audit.weight_sum,
        n_observations=len(values),
        dropped_count=dropped_count,
        used_indices=used_indices,
        diagonal_weight_removed=audit.diagonal_removed,
        island_count=audit.island_count,
        symmetric_weights=audit.symmetric,
    )


def psd_clean(
    y: np.ndarray,
    strata: np.ndarray,
    weights: np.ndarray,
    *,
    min_stratum_size: int,
    allow_islands: bool,
    used_indices: tuple[int, ...] | None = None,
    dropped_count: int = 0,
) -> PowerSpatialDeterminantResult:
    """Calculate PSD for an already aligned complete sample."""

    labels_array = np.asarray(strata, dtype=object)
    labels = tuple(pd.unique(pd.Series(labels_array, dtype=object)))
    if len(labels) < 2:
        raise InvalidDataError("at least two spatial strata are required")

    counts: list[int] = []
    for label in labels:
        counts.append(int(np.count_nonzero(labels_array == label)))
    too_small = [
        (label, count)
        for label, count in zip(labels, counts, strict=True)
        if count < min_stratum_size
    ]
    if too_small:
        details = ", ".join(f"{label!r}: {count}" for label, count in too_small)
        raise SmallStratumError(
            f"each spatial stratum must contain at least {min_stratum_size} "
            f"observations; too small: {details}"
        )

    resolved_indices = (
        tuple(range(len(y))) if used_indices is None else tuple(used_indices)
    )
    global_variance = _spatial_variance_result(
        y,
        weights,
        allow_islands=allow_islands,
        used_indices=resolved_indices,
        dropped_count=dropped_count,
    )
    scale = max(1.0, float(np.dot(y, y)))
    tolerance = 64.0 * np.finfo(float).eps * scale
    if global_variance.value <= tolerance:
        raise InvalidDataError(
            "global spatial variance is zero or numerically undefined"
        )

    contributions: list[SpatialStratumVariance] = []
    within = 0.0
    for label, count in zip(labels, counts, strict=True):
        indices = np.flatnonzero(labels_array == label)
        local_value, _, local_audit = _spatial_variance_clean(
            y[indices],
            weights[np.ix_(indices, indices)].copy(),
            allow_islands=allow_islands,
        )
        weighted = count * local_value
        within += weighted
        contributions.append(
            SpatialStratumVariance(
                label=label.item() if isinstance(label, np.generic) else label,
                count=count,
                spatial_variance=float(local_value),
                weighted_variance=float(weighted),
                weight_sum=local_audit.weight_sum,
                island_count=local_audit.island_count,
            )
        )

    total = len(y) * global_variance.value
    value = 1.0 - within / total
    return PowerSpatialDeterminantResult(
        value=float(value),
        global_variance=global_variance,
        strata=tuple(contributions),
        within_weighted_variance=float(within),
        total_weighted_variance=float(total),
        n_observations=len(y),
        dropped_count=dropped_count,
        used_indices=resolved_indices,
        min_stratum_size=min_stratum_size,
        allow_islands=allow_islands,
        metadata={
            "formula": "1 - sum_h(N_h * Gamma_h) / (N * Gamma)",
            "weight_normalization": "none",
            "diagonal_policy": "excluded",
            "directed_weights_allowed": True,
        },
    )


def _permutation_summary(
    observed: float,
    null_values: np.ndarray,
) -> tuple[float, float, float]:
    tolerance = 64.0 * np.finfo(float).eps * max(1.0, abs(observed))
    p_value = float(
        (1 + np.count_nonzero(null_values >= observed - tolerance))
        / (len(null_values) + 1)
    )
    null_mean = float(np.mean(null_values))
    null_sd = float(np.std(null_values, ddof=1)) if len(null_values) > 1 else 0.0
    return p_value, null_mean, null_sd


def power_spatial_determinant(
    y: Any,
    strata: Any,
    weights: Any,
    *,
    missing: MissingPolicy = "drop",
    min_stratum_size: int = 2,
    allow_islands: bool = False,
    permutations: int = 0,
    random_state: int | None = None,
) -> PowerSpatialDeterminantResult:
    """Calculate the SPADE power of spatial determinant (PSD)."""

    minimum = validate_minimum(min_stratum_size)
    permutation_count = validate_permutations(permutations)
    y_clean, strata_clean, matrix, used, dropped = _prepare_psd_sample(
        y,
        strata,
        weights,
        missing=missing,
    )
    result = psd_clean(
        y_clean,
        strata_clean,
        matrix,
        min_stratum_size=minimum,
        allow_islands=allow_islands,
        used_indices=tuple(int(index) for index in used),
        dropped_count=dropped,
    )
    if not permutation_count:
        return result

    rng = np.random.default_rng(random_state)
    null_values = np.empty(permutation_count, dtype=float)
    for index in range(permutation_count):
        null_values[index] = psd_clean(
            rng.permutation(y_clean),
            strata_clean,
            matrix,
            min_stratum_size=minimum,
            allow_islands=allow_islands,
        ).value
    p_value, null_mean, null_sd = _permutation_summary(result.value, null_values)
    return PowerSpatialDeterminantResult(
        value=result.value,
        global_variance=result.global_variance,
        strata=result.strata,
        within_weighted_variance=result.within_weighted_variance,
        total_weighted_variance=result.total_weighted_variance,
        n_observations=result.n_observations,
        dropped_count=result.dropped_count,
        used_indices=result.used_indices,
        min_stratum_size=result.min_stratum_size,
        allow_islands=result.allow_islands,
        p_value=p_value,
        permutations=permutation_count,
        null_mean=null_mean,
        null_standard_deviation=null_sd,
        random_state=random_state,
        metadata=result.metadata,
    )


def cpsd_clean(
    y: np.ndarray,
    x: np.ndarray,
    strata: np.ndarray,
    weights: np.ndarray,
    *,
    min_stratum_size: int,
    allow_islands: bool,
    denominator_tolerance: float,
) -> tuple[float, PowerSpatialDeterminantResult, PowerSpatialDeterminantResult]:
    local_indices = tuple(range(len(y)))
    response = psd_clean(
        y,
        strata,
        weights,
        min_stratum_size=min_stratum_size,
        allow_islands=allow_islands,
        used_indices=local_indices,
    )
    information = psd_clean(
        x,
        strata,
        weights,
        min_stratum_size=min_stratum_size,
        allow_islands=allow_islands,
        used_indices=local_indices,
    )
    if abs(information.value) <= denominator_tolerance:
        raise InvalidDataError(
            "information-retention PSD is zero; compensated PSD is undefined"
        )
    return float(response.value / information.value), response, information


def compensated_spatial_determinant(
    y: Any,
    x: Any,
    strata: Any,
    weights: Any,
    *,
    missing: MissingPolicy = "drop",
    min_stratum_size: int = 2,
    allow_islands: bool = False,
    denominator_tolerance: float = 1e-12,
) -> CompensatedSpatialDeterminantResult:
    """Calculate CPSD as response PSD divided by information-retention PSD."""

    minimum = validate_minimum(min_stratum_size)
    if denominator_tolerance < 0.0:
        raise ValueError("denominator_tolerance must be nonnegative")
    y_clean, x_clean, strata_clean, matrix, used, dropped = prepare_cpsd_sample(
        y,
        x,
        strata,
        weights,
        missing=missing,
    )
    value, response, information = cpsd_clean(
        y_clean,
        x_clean,
        strata_clean,
        matrix,
        min_stratum_size=minimum,
        allow_islands=allow_islands,
        denominator_tolerance=denominator_tolerance,
    )
    return CompensatedSpatialDeterminantResult(
        value=value,
        response_psd=response,
        information_psd=information,
        n_observations=len(y_clean),
        dropped_count=dropped,
        used_indices=tuple(int(index) for index in used),
        denominator_tolerance=float(denominator_tolerance),
    )
