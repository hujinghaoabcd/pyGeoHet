"""Spatial variance and prepared spatial-weight contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from pygeohet.exceptions import InvalidDataError, MissingDataError
from pygeohet.validation import MissingPolicy


@dataclass(frozen=True)
class SpatialVarianceResult:
    """Auditable weighted average semivariance."""

    value: float
    numerator: float
    weight_sum: float
    n_observations: int
    dropped_count: int
    used_indices: tuple[int, ...]
    diagonal_weight_removed: float
    island_count: int
    symmetric_weights: bool

    def to_series(self) -> pd.Series:
        """Return scalar audit fields."""

        return pd.Series(
            {
                "spatial_variance": self.value,
                "weighted_semisquared_sum": self.numerator,
                "weight_sum": self.weight_sum,
                "n_observations": self.n_observations,
                "dropped_count": self.dropped_count,
                "diagonal_weight_removed": self.diagonal_weight_removed,
                "island_count": self.island_count,
                "symmetric_weights": self.symmetric_weights,
            }
        )

    def summary(self) -> str:
        """Return a compact terminal-friendly summary."""

        return (
            "SpatialVarianceResult("
            f"value={self.value:.6g}, n={self.n_observations}, "
            f"weight_sum={self.weight_sum:.6g}, islands={self.island_count})"
        )


@dataclass(frozen=True)
class _WeightAudit:
    matrix: np.ndarray
    weight_sum: float
    diagonal_removed: float
    island_count: int
    symmetric: bool


def _coerce_weight_matrix(weights: Any, n_observations: int) -> np.ndarray:
    matrix = np.asarray(weights, dtype=float)
    if matrix.ndim != 2 or matrix.shape != (n_observations, n_observations):
        raise InvalidDataError(
            "weights must be a square matrix with one row and column per observation"
        )
    if not bool(np.isfinite(matrix).all()):
        raise InvalidDataError("weights must contain only finite values")
    if bool((matrix < 0.0).any()):
        raise InvalidDataError("weights must be nonnegative")
    return matrix.copy()


def _audit_weight_matrix(
    matrix: np.ndarray,
    *,
    allow_islands: bool,
) -> _WeightAudit:
    diagonal_removed = float(np.trace(matrix))
    np.fill_diagonal(matrix, 0.0)
    weight_sum = float(np.sum(matrix, dtype=float))
    if not np.isfinite(weight_sum) or weight_sum <= 0.0:
        raise InvalidDataError("off-diagonal spatial weights must have positive total")
    row_sums = np.sum(matrix, axis=1, dtype=float)
    island_count = int(np.count_nonzero(row_sums <= 0.0))
    if island_count and not allow_islands:
        raise InvalidDataError(
            f"spatial weights contain {island_count} island observations; "
            "set allow_islands=True to retain them explicitly"
        )
    symmetric = bool(np.allclose(matrix, matrix.T, rtol=1e-12, atol=1e-15))
    return _WeightAudit(
        matrix=matrix,
        weight_sum=weight_sum,
        diagonal_removed=diagonal_removed,
        island_count=island_count,
        symmetric=symmetric,
    )


def _spatial_variance_clean(
    values: np.ndarray,
    weights: np.ndarray,
    *,
    allow_islands: bool,
) -> tuple[float, float, _WeightAudit]:
    audit = _audit_weight_matrix(weights.copy(), allow_islands=allow_islands)
    differences = values[:, None] - values[None, :]
    semisquared = 0.5 * differences * differences
    numerator = float(np.sum(audit.matrix * semisquared, dtype=float))
    value = numerator / audit.weight_sum
    return float(value), numerator, audit


def spatial_variance(
    values: Any,
    weights: Any,
    *,
    missing: MissingPolicy = "drop",
    allow_islands: bool = False,
) -> SpatialVarianceResult:
    """Calculate the weighted average semivariance from the SPADE papers.

    The diagonal is excluded from both numerator and denominator. Weights are not
    row-standardized or symmetrized. Directed matrices are accepted and audited.
    """

    if missing not in {"drop", "raise"}:
        raise ValueError("missing must be either 'drop' or 'raise'")

    series = pd.Series(values, copy=False, name="value").reset_index(drop=True)
    if series.ndim != 1 or len(series) == 0:
        raise InvalidDataError("values must be a nonempty one-dimensional vector")
    numeric = pd.to_numeric(series, errors="raise").astype(float)
    matrix = _coerce_weight_matrix(weights, len(numeric))

    missing_mask = numeric.isna().to_numpy(dtype=bool)
    if missing == "raise" and bool(missing_mask.any()):
        raise MissingDataError("missing values are present in values")
    used_indices = np.flatnonzero(~missing_mask)
    clean = numeric.iloc[used_indices].to_numpy(dtype=float, copy=True)
    if clean.size < 2:
        raise InvalidDataError("at least two complete observations are required")
    if not bool(np.isfinite(clean).all()):
        raise InvalidDataError("values must contain only finite values")

    subset = matrix[np.ix_(used_indices, used_indices)].copy()
    value, numerator, audit = _spatial_variance_clean(
        clean,
        subset,
        allow_islands=allow_islands,
    )
    return SpatialVarianceResult(
        value=value,
        numerator=numerator,
        weight_sum=audit.weight_sum,
        n_observations=int(clean.size),
        dropped_count=int(missing_mask.sum()),
        used_indices=tuple(int(index) for index in used_indices),
        diagonal_weight_removed=audit.diagonal_removed,
        island_count=audit.island_count,
        symmetric_weights=audit.symmetric,
    )
