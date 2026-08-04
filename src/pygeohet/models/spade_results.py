"""Immutable result objects for SPADE statistics."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

import pandas as pd

from pygeohet.spatial import SpatialVarianceResult
from pygeohet.stratification import StratificationResult


@dataclass(frozen=True)
class SpatialStratumVariance:
    """One stratum contribution to the PSD numerator."""

    label: Any
    count: int
    spatial_variance: float
    weighted_variance: float
    weight_sum: float
    island_count: int

    def to_series(self) -> pd.Series:
        return pd.Series(
            {
                "stratum": self.label,
                "count": self.count,
                "spatial_variance": self.spatial_variance,
                "weighted_variance": self.weighted_variance,
                "weight_sum": self.weight_sum,
                "island_count": self.island_count,
            }
        )


@dataclass(frozen=True)
class PowerSpatialDeterminantResult:
    """Power of spatial determinant and complete variance evidence."""

    value: float
    global_variance: SpatialVarianceResult
    strata: tuple[SpatialStratumVariance, ...]
    within_weighted_variance: float
    total_weighted_variance: float
    n_observations: int
    dropped_count: int
    used_indices: tuple[int, ...]
    min_stratum_size: int
    allow_islands: bool
    p_value: float | None = None
    permutations: int = 0
    null_mean: float | None = None
    null_standard_deviation: float | None = None
    random_state: int | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def q(self) -> float:
        """Compatibility alias for the PSD value."""

        return self.value

    def strata_frame(self) -> pd.DataFrame:
        return pd.DataFrame([item.to_series() for item in self.strata])

    def to_series(self) -> pd.Series:
        return pd.Series(
            {
                "psd": self.value,
                "p_value": self.p_value,
                "global_spatial_variance": self.global_variance.value,
                "within_weighted_variance": self.within_weighted_variance,
                "total_weighted_variance": self.total_weighted_variance,
                "n_strata": len(self.strata),
                "n_observations": self.n_observations,
                "dropped_count": self.dropped_count,
                "permutations": self.permutations,
            }
        )

    def summary(self) -> str:
        p_text = "None" if self.p_value is None else f"{self.p_value:.6g}"
        return (
            "PowerSpatialDeterminantResult("
            f"PSD={self.value:.6g}, p={p_text}, strata={len(self.strata)}, "
            f"n={self.n_observations})"
        )


@dataclass(frozen=True)
class CompensatedSpatialDeterminantResult:
    """CPSD ratio and its response/information PSD components."""

    value: float
    response_psd: PowerSpatialDeterminantResult
    information_psd: PowerSpatialDeterminantResult
    n_observations: int
    dropped_count: int
    used_indices: tuple[int, ...]
    denominator_tolerance: float

    def to_series(self) -> pd.Series:
        return pd.Series(
            {
                "cpsd": self.value,
                "response_psd": self.response_psd.value,
                "information_psd": self.information_psd.value,
                "n_observations": self.n_observations,
                "dropped_count": self.dropped_count,
            }
        )

    def summary(self) -> str:
        return (
            "CompensatedSpatialDeterminantResult("
            f"CPSD={self.value:.6g}, response_PSD={self.response_psd.value:.6g}, "
            f"information_PSD={self.information_psd.value:.6g})"
        )


@dataclass(frozen=True)
class MultilevelSpatialCandidate:
    """One requested discretization level in PSMD."""

    requested_strata: int
    stratification: StratificationResult | None
    result: CompensatedSpatialDeterminantResult | None
    accepted: bool
    rejection_reason: str | None

    def to_series(self) -> pd.Series:
        stratification = self.stratification
        result = self.result
        return pd.Series(
            {
                "requested_strata": self.requested_strata,
                "actual_strata": (
                    None if stratification is None else stratification.actual_strata
                ),
                "accepted": self.accepted,
                "rejection_reason": self.rejection_reason,
                "cpsd": None if result is None else result.value,
                "response_psd": None if result is None else result.response_psd.value,
                "information_psd": (
                    None if result is None else result.information_psd.value
                ),
                "cut_points": (
                    None if stratification is None else stratification.cut_points
                ),
            }
        )


@dataclass(frozen=True)
class MultilevelSpatialDeterminantResult:
    """Power of spatial and multilevel discretization determinant."""

    value: float
    candidates: tuple[MultilevelSpatialCandidate, ...]
    method: str
    requested_levels: tuple[int, ...]
    accepted_levels: tuple[int, ...]
    n_observations: int
    dropped_count: int
    used_indices: tuple[int, ...]
    p_value: float | None = None
    permutations: int = 0
    null_mean: float | None = None
    null_standard_deviation: float | None = None
    random_state: int | None = None

    def candidates_frame(self) -> pd.DataFrame:
        return pd.DataFrame([candidate.to_series() for candidate in self.candidates])

    def to_series(self) -> pd.Series:
        return pd.Series(
            {
                "psmd": self.value,
                "p_value": self.p_value,
                "method": self.method,
                "requested_levels": self.requested_levels,
                "accepted_levels": self.accepted_levels,
                "n_observations": self.n_observations,
                "dropped_count": self.dropped_count,
                "permutations": self.permutations,
            }
        )

    def summary(self) -> str:
        p_text = "None" if self.p_value is None else f"{self.p_value:.6g}"
        return (
            "MultilevelSpatialDeterminantResult("
            f"PSMD={self.value:.6g}, p={p_text}, method={self.method!r}, "
            f"levels={self.accepted_levels!r})"
        )


SPADEFactorResult = PowerSpatialDeterminantResult | MultilevelSpatialDeterminantResult


@dataclass(frozen=True)
class SPADEResult:
    """SPADE results for categorical and continuous explanatory factors."""

    factors: Mapping[str, SPADEFactorResult]
    continuous_factors: tuple[str, ...]
    categorical_factors: tuple[str, ...]
    weight_shape: tuple[int, int]

    def __post_init__(self) -> None:
        object.__setattr__(self, "factors", MappingProxyType(dict(self.factors)))

    def to_frame(self) -> pd.DataFrame:
        rows: list[dict[str, Any]] = []
        continuous = set(self.continuous_factors)
        for factor, result in self.factors.items():
            if isinstance(result, MultilevelSpatialDeterminantResult):
                rows.append(
                    {
                        "factor": factor,
                        "kind": "continuous",
                        "statistic": "PSMD",
                        "value": result.value,
                        "p_value": result.p_value,
                        "method": result.method,
                        "levels": result.accepted_levels,
                        "n_observations": result.n_observations,
                        "dropped_count": result.dropped_count,
                    }
                )
            else:
                rows.append(
                    {
                        "factor": factor,
                        "kind": (
                            "continuous" if factor in continuous else "categorical"
                        ),
                        "statistic": "PSD",
                        "value": result.value,
                        "p_value": result.p_value,
                        "method": None,
                        "levels": None,
                        "n_observations": result.n_observations,
                        "dropped_count": result.dropped_count,
                    }
                )
        return pd.DataFrame(rows)

    def summary(self) -> str:
        return self.to_frame().to_string(index=False)
