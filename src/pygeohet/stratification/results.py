"""Immutable stratification and optimization result objects."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

import numpy as np
import pandas as pd

from pygeohet.results import QStatisticResult


@dataclass(frozen=True)
class StratificationResult:
    """Auditable result of one continuous-variable stratification."""

    method: str
    labels: tuple[int | None, ...]
    cut_points: tuple[float, ...]
    requested_strata: int | None
    actual_strata: int
    counts: Mapping[int, int]
    n_observations: int
    dropped_count: int
    duplicate_cut_points: int
    collapsed_strata: int
    min_stratum_size: int
    rejected: bool
    rejection_reason: str | None
    supervised: bool = False
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "counts", MappingProxyType(dict(self.counts)))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def labels_array(self, *, missing_value: float = np.nan) -> np.ndarray:
        """Return labels as a float array, using ``missing_value`` for dropped rows."""

        return np.asarray(
            [missing_value if label is None else label for label in self.labels],
            dtype=float,
        )

    def to_series(self) -> pd.Series:
        """Return scalar audit fields as a labelled series."""

        return pd.Series(
            {
                "method": self.method,
                "requested_strata": self.requested_strata,
                "actual_strata": self.actual_strata,
                "n_observations": self.n_observations,
                "dropped_count": self.dropped_count,
                "minimum_count": min(self.counts.values(), default=0),
                "duplicate_cut_points": self.duplicate_cut_points,
                "collapsed_strata": self.collapsed_strata,
                "rejected": self.rejected,
                "rejection_reason": self.rejection_reason,
                "cut_points": self.cut_points,
            }
        )

    def summary(self) -> str:
        """Return a compact terminal-friendly summary."""

        state = "rejected" if self.rejected else "accepted"
        return (
            "StratificationResult("
            f"method={self.method!r}, requested={self.requested_strata}, "
            f"actual={self.actual_strata}, state={state}, "
            f"counts={dict(self.counts)!r}, cuts={self.cut_points!r})"
        )


@dataclass(frozen=True)
class StratificationEvaluationResult:
    """One stratification candidate and its q-statistic evaluation."""

    candidate_index: int
    method_rank: int
    stratification: StratificationResult
    q_result: QStatisticResult | None
    accepted: bool
    rejection_reason: str | None

    def to_series(self) -> pd.Series:
        """Return one flat candidate-audit row."""

        q_result = self.q_result
        return pd.Series(
            {
                "candidate_index": self.candidate_index,
                "method_rank": self.method_rank,
                "method": self.stratification.method,
                "requested_strata": self.stratification.requested_strata,
                "actual_strata": self.stratification.actual_strata,
                "minimum_count": min(self.stratification.counts.values(), default=0),
                "cut_points": self.stratification.cut_points,
                "duplicate_cut_points": self.stratification.duplicate_cut_points,
                "collapsed_strata": self.stratification.collapsed_strata,
                "dropped_count": self.stratification.dropped_count,
                "accepted": self.accepted,
                "rejection_reason": self.rejection_reason,
                "q": None if q_result is None else q_result.q,
                "p_value": None if q_result is None else q_result.p_value,
                "within_ss": None if q_result is None else q_result.within_ss,
                "between_ss": None if q_result is None else q_result.between_ss,
                "total_ss": None if q_result is None else q_result.total_ss,
            }
        )


@dataclass(frozen=True)
class OptimalStratificationResult:
    """Complete candidate table and deterministic winning stratification."""

    candidates: tuple[StratificationEvaluationResult, ...]
    best: StratificationEvaluationResult | None
    tie_rule: str
    q_tolerance: float

    def candidates_frame(self) -> pd.DataFrame:
        """Return every attempted candidate, including rejected candidates."""

        return pd.DataFrame([item.to_series() for item in self.candidates])

    def best_series(self) -> pd.Series:
        """Return the winning candidate as a series."""

        if self.best is None:
            return pd.Series(dtype=object)
        return self.best.to_series()

    def summary(self) -> str:
        """Return a compact optimization summary."""

        if self.best is None:
            return (
                "OptimalStratificationResult(no accepted candidate; "
                f"attempted={len(self.candidates)})"
            )
        row = self.best.to_series()
        return (
            "OptimalStratificationResult("
            f"method={row['method']!r}, requested={row['requested_strata']}, "
            f"actual={row['actual_strata']}, q={row['q']:.6g}, "
            f"attempted={len(self.candidates)})"
        )
