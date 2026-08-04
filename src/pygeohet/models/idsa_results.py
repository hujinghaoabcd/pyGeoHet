"""Immutable results for fuzzy overlay and IDSA workflows."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Literal

import pandas as pd

from pygeohet.models.spade_results import (
    CompensatedSpatialDeterminantResult,
    PowerSpatialDeterminantResult,
)
from pygeohet.stratification import StratificationResult

FuzzyOperation = Literal["and", "or"]
FuzzyTiePolicy = Literal["first", "last"]
FuzzyZone = tuple[str, Any]


@dataclass(frozen=True)
class FuzzyRiskLevel:
    """Response-risk membership attached to one factor stratum."""

    factor: str
    stratum: Any
    count: int
    mean_response: float
    membership: float

    @property
    def zone(self) -> FuzzyZone:
        return (self.factor, self.stratum)

    def to_series(self) -> pd.Series:
        return pd.Series(
            {
                "factor": self.factor,
                "stratum": self.stratum,
                "count": self.count,
                "mean_response": self.mean_response,
                "membership": self.membership,
            }
        )


@dataclass(frozen=True)
class FuzzyOverlayResult:
    """Collision-safe fuzzy AND/OR interaction zones and membership evidence."""

    labels: tuple[FuzzyZone | None, ...]
    memberships: Mapping[str, tuple[float | None, ...]]
    risk_levels: tuple[FuzzyRiskLevel, ...]
    factors: tuple[str, ...]
    operation: FuzzyOperation
    tie_policy: FuzzyTiePolicy
    membership_tolerance: float
    tied_row_count: int
    n_observations: int
    dropped_count: int
    used_indices: tuple[int, ...]
    risk_minimum: float
    risk_maximum: float

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "memberships",
            MappingProxyType(
                {name: tuple(values) for name, values in self.memberships.items()}
            ),
        )

    @property
    def zone_count(self) -> int:
        return len({label for label in self.labels if label is not None})

    def labels_series(self, *, name: str = "fuzzy_zone") -> pd.Series:
        return pd.Series(self.labels, dtype=object, name=name)

    def risk_frame(self) -> pd.DataFrame:
        return pd.DataFrame([level.to_series() for level in self.risk_levels])

    def membership_frame(self) -> pd.DataFrame:
        return pd.DataFrame(dict(self.memberships), dtype=float)

    def zones_frame(self) -> pd.DataFrame:
        observed = [label for label in self.labels if label is not None]
        counts = pd.Series(observed, dtype=object).value_counts(sort=False)
        return pd.DataFrame(
            {
                "zone": list(counts.index),
                "count": [int(value) for value in counts.to_numpy()],
            }
        )

    def summary(self) -> str:
        return (
            "FuzzyOverlayResult("
            f"operation={self.operation!r}, zones={self.zone_count}, "
            f"n={self.n_observations}, tied_rows={self.tied_row_count})"
        )


@dataclass(frozen=True)
class InteractiveSpatialDeterminantResult:
    """Fixed-strata IDSA power, information retention and fuzzy-zone evidence."""

    value: float
    theta: PowerSpatialDeterminantResult
    phi: float
    information_components: Mapping[str, PowerSpatialDeterminantResult]
    overlay: FuzzyOverlayResult
    encoded_factors: Mapping[str, tuple[int | None, ...]]
    n_observations: int
    dropped_count: int
    used_indices: tuple[int, ...]
    denominator_tolerance: float
    finely_divided_zone_count: int
    p_value: float | None = None
    permutations: int = 0
    valid_permutations: int = 0
    failed_permutations: int = 0
    null_mean: float | None = None
    null_standard_deviation: float | None = None
    random_state: int | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "information_components",
            MappingProxyType(dict(self.information_components)),
        )
        object.__setattr__(
            self,
            "encoded_factors",
            MappingProxyType(
                {name: tuple(values) for name, values in self.encoded_factors.items()}
            ),
        )
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def pid(self) -> float:
        return self.value

    def information_frame(self) -> pd.DataFrame:
        rows: list[dict[str, Any]] = []
        for factor, result in self.information_components.items():
            rows.append(
                {
                    "factor": factor,
                    "information_psd": result.value,
                    "within_weighted_variance": result.within_weighted_variance,
                    "total_weighted_variance": result.total_weighted_variance,
                    "global_spatial_variance": result.global_variance.value,
                }
            )
        return pd.DataFrame(rows)

    def to_series(self) -> pd.Series:
        return pd.Series(
            {
                "pid": self.value,
                "theta": self.theta.value,
                "phi": self.phi,
                "p_value": self.p_value,
                "factors": self.overlay.factors,
                "operation": self.overlay.operation,
                "zone_count": self.overlay.zone_count,
                "finely_divided_zone_count": self.finely_divided_zone_count,
                "n_observations": self.n_observations,
                "dropped_count": self.dropped_count,
                "permutations": self.permutations,
                "valid_permutations": self.valid_permutations,
                "failed_permutations": self.failed_permutations,
            }
        )

    def summary(self) -> str:
        p_text = "None" if self.p_value is None else f"{self.p_value:.6g}"
        return (
            "InteractiveSpatialDeterminantResult("
            f"PID={self.value:.6g}, theta={self.theta.value:.6g}, "
            f"phi={self.phi:.6g}, p={p_text}, zones={self.overlay.zone_count})"
        )


@dataclass(frozen=True)
class SpatialDiscretizationCandidate:
    """One method-by-level CPSD candidate for an IDSA explanatory factor."""

    candidate_index: int
    method_rank: int
    method: str
    requested_strata: int
    stratification: StratificationResult | None
    result: CompensatedSpatialDeterminantResult | None
    accepted: bool
    rejection_reason: str | None

    def to_series(self) -> pd.Series:
        return pd.Series(
            {
                "candidate_index": self.candidate_index,
                "method": self.method,
                "requested_strata": self.requested_strata,
                "actual_strata": (
                    None
                    if self.stratification is None
                    else self.stratification.actual_strata
                ),
                "accepted": self.accepted,
                "rejection_reason": self.rejection_reason,
                "cpsd": None if self.result is None else self.result.value,
                "response_psd": (
                    None if self.result is None else self.result.response_psd.value
                ),
                "information_psd": (
                    None if self.result is None else self.result.information_psd.value
                ),
                "cut_points": (
                    None
                    if self.stratification is None
                    else self.stratification.cut_points
                ),
            }
        )


@dataclass(frozen=True)
class SpatialDiscretizationOptimizationResult:
    """Complete CPSD-guided discretization search for one factor."""

    candidates: tuple[SpatialDiscretizationCandidate, ...]
    best: SpatialDiscretizationCandidate
    tie_rule: str
    cpsd_tolerance: float

    def candidates_frame(self) -> pd.DataFrame:
        return pd.DataFrame([candidate.to_series() for candidate in self.candidates])

    def best_series(self) -> pd.Series:
        return self.best.to_series()

    def summary(self) -> str:
        assert self.best.result is not None
        return (
            "SpatialDiscretizationOptimizationResult("
            f"method={self.best.method!r}, strata={self.best.requested_strata}, "
            f"CPSD={self.best.result.value:.6g})"
        )


@dataclass(frozen=True)
class IDSACombinationResult:
    """One attempted explanatory-factor subset in IDSA search."""

    factors: tuple[str, ...]
    result: InteractiveSpatialDeterminantResult | None
    accepted: bool
    rejection_reason: str | None
    search_step: int
    added_factor: str | None

    def to_series(self) -> pd.Series:
        return pd.Series(
            {
                "factors": self.factors,
                "factor_count": len(self.factors),
                "accepted": self.accepted,
                "rejection_reason": self.rejection_reason,
                "pid": None if self.result is None else self.result.value,
                "theta": None if self.result is None else self.result.theta.value,
                "phi": None if self.result is None else self.result.phi,
                "zone_count": (
                    None if self.result is None else self.result.overlay.zone_count
                ),
                "search_step": self.search_step,
                "added_factor": self.added_factor,
            }
        )


@dataclass(frozen=True)
class IDSAResult:
    """Optimized discretizations, attempted interactions and selected IDSA model."""

    discretizations: Mapping[str, SpatialDiscretizationOptimizationResult]
    discrete_labels: Mapping[str, tuple[int | None, ...]]
    combinations: tuple[IDSACombinationResult, ...]
    best: IDSACombinationResult
    search: str
    operation: FuzzyOperation
    tie_rule: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "discretizations",
            MappingProxyType(dict(self.discretizations)),
        )
        object.__setattr__(
            self,
            "discrete_labels",
            MappingProxyType(
                {name: tuple(values) for name, values in self.discrete_labels.items()}
            ),
        )

    def discretizations_frame(self) -> pd.DataFrame:
        rows: list[dict[str, Any]] = []
        for factor, result in self.discretizations.items():
            row = result.best_series().to_dict()
            row["factor"] = factor
            rows.append(row)
        if not rows:
            return pd.DataFrame()
        frame = pd.DataFrame(rows)
        return frame.loc[:, ["factor", *[name for name in frame if name != "factor"]]]

    def candidates_frame(self, factor: str) -> pd.DataFrame:
        try:
            frame = self.discretizations[factor].candidates_frame()
        except KeyError as exc:
            raise KeyError(factor) from exc
        frame.insert(0, "factor", factor)
        return frame

    def combinations_frame(self) -> pd.DataFrame:
        return pd.DataFrame([item.to_series() for item in self.combinations])

    def summary(self) -> str:
        assert self.best.result is not None
        return (
            "IDSAResult("
            f"search={self.search!r}, factors={self.best.factors!r}, "
            f"PID={self.best.result.value:.6g})"
        )
