"""Immutable results for spatial rough set geographical detectors."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Literal

import pandas as pd

SpatialHeterogeneityChange = Literal["increased", "decreased", "unchanged"]


@dataclass(frozen=True)
class SpatialRoughSetResult:
    """Local approximation quality and aggregate SRS-GD evidence."""

    feature_names: tuple[str, ...]
    average_local_power: float
    spatial_entropy: float | None
    normalized_spatial_entropy: float | None
    local_quality: tuple[float | None, ...]
    region_size: tuple[int | None, ...]
    positive_region_size: tuple[int | None, ...]
    n_observations: int
    total_length: int
    dropped_count: int
    used_indices: tuple[int, ...]
    island_indices: tuple[int, ...]
    adjacency_symmetric: bool
    t_statistic: float | None = None
    p_value: float | None = None
    test_sample_indices: tuple[int, ...] = ()
    random_state: int | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def D(self) -> float:
        """Average local explanatory power from the paper notation."""

        return self.average_local_power

    @property
    def SE(self) -> float | None:
        """Spatial entropy from the paper notation."""

        return self.spatial_entropy

    def to_series(self) -> pd.Series:
        """Return scalar result fields as a labelled series."""

        return pd.Series(
            {
                "features": self.feature_names,
                "D": self.average_local_power,
                "SE": self.spatial_entropy,
                "normalized_SE": self.normalized_spatial_entropy,
                "t_statistic": self.t_statistic,
                "p_value": self.p_value,
                "n_observations": self.n_observations,
                "dropped_count": self.dropped_count,
                "island_count": len(self.island_indices),
                "adjacency_symmetric": self.adjacency_symmetric,
            }
        )

    def local_frame(self) -> pd.DataFrame:
        """Return one row per original observation, including dropped rows."""

        used = set(self.used_indices)
        islands = set(self.island_indices)
        tested = set(self.test_sample_indices)
        return pd.DataFrame(
            {
                "index": range(self.total_length),
                "used": [index in used for index in range(self.total_length)],
                "island": [index in islands for index in range(self.total_length)],
                "tested": [index in tested for index in range(self.total_length)],
                "region_size": self.region_size,
                "positive_region_size": self.positive_region_size,
                "local_quality": self.local_quality,
            }
        )

    def summary(self) -> str:
        """Return a terminal-friendly statistical summary."""

        entropy = (
            "undefined"
            if self.spatial_entropy is None
            else f"{self.spatial_entropy:.6g}"
        )
        p_text = "None" if self.p_value is None else f"{self.p_value:.6g}"
        return (
            "SpatialRoughSetResult("
            f"features={self.feature_names!r}, D={self.average_local_power:.6g}, "
            f"SE={entropy}, p={p_text}, n={self.n_observations}, "
            f"islands={len(self.island_indices)}, dropped={self.dropped_count})"
        )


@dataclass(frozen=True)
class SRSFactorDetectorResult:
    """Collection of single-feature SRSF results on one common sample."""

    factors: Mapping[str, SpatialRoughSetResult]

    def __post_init__(self) -> None:
        object.__setattr__(self, "factors", MappingProxyType(dict(self.factors)))

    def __getitem__(self, factor: str) -> SpatialRoughSetResult:
        return self.factors[factor]

    def to_frame(self) -> pd.DataFrame:
        """Return one row per factor ordered by descending average local power."""

        rows: list[dict[str, Any]] = []
        for name, result in self.factors.items():
            row = result.to_series().to_dict()
            row["factor"] = name
            rows.append(row)
        if not rows:
            return pd.DataFrame()
        frame = pd.DataFrame(rows)
        columns = ["factor", *[column for column in frame if column != "factor"]]
        return frame.loc[:, columns].sort_values(
            ["D", "factor"],
            ascending=[False, True],
            kind="stable",
            ignore_index=True,
        )

    def summary(self) -> str:
        return str(self.to_frame().to_string(index=False))


@dataclass(frozen=True)
class SRSEcologicalComparisonResult:
    """Paired comparison of local explanatory power for two feature sets."""

    feature_1: tuple[str, ...]
    feature_2: tuple[str, ...]
    result_1: SpatialRoughSetResult
    result_2: SpatialRoughSetResult
    difference: float
    t_statistic: float
    p_value: float
    significant: bool
    more_explanatory: tuple[str, ...] | None
    sample_indices: tuple[int, ...]

    def to_series(self) -> pd.Series:
        return pd.Series(
            {
                "feature_1": self.feature_1,
                "feature_2": self.feature_2,
                "D_1": self.result_1.D,
                "D_2": self.result_2.D,
                "difference": self.difference,
                "t_statistic": self.t_statistic,
                "p_value": self.p_value,
                "significant": self.significant,
                "more_explanatory": self.more_explanatory,
                "sample_size": len(self.sample_indices),
            }
        )


@dataclass(frozen=True)
class SRSEcologicalDetectorResult:
    """Collection of pairwise SRS ecological comparisons."""

    comparisons: tuple[SRSEcologicalComparisonResult, ...]

    def to_frame(self) -> pd.DataFrame:
        return pd.DataFrame([comparison.to_series() for comparison in self.comparisons])

    def summary(self) -> str:
        return str(self.to_frame().to_string(index=False))


@dataclass(frozen=True)
class SRSInteractionComparisonResult:
    """Incremental SRSI evidence after adding one feature set."""

    baseline_features: tuple[str, ...]
    added_features: tuple[str, ...]
    joint_features: tuple[str, ...]
    baseline_result: SpatialRoughSetResult
    joint_result: SpatialRoughSetResult
    power_gain: float
    entropy_change: float | None
    heterogeneity_change: SpatialHeterogeneityChange | None
    t_statistic: float
    p_value: float
    significant_gain: bool
    sample_indices: tuple[int, ...]

    def to_series(self) -> pd.Series:
        return pd.Series(
            {
                "baseline_features": self.baseline_features,
                "added_features": self.added_features,
                "joint_features": self.joint_features,
                "D_baseline": self.baseline_result.D,
                "D_joint": self.joint_result.D,
                "power_gain": self.power_gain,
                "SE_baseline": self.baseline_result.SE,
                "SE_joint": self.joint_result.SE,
                "entropy_change": self.entropy_change,
                "heterogeneity_change": self.heterogeneity_change,
                "t_statistic": self.t_statistic,
                "p_value": self.p_value,
                "significant_gain": self.significant_gain,
                "sample_size": len(self.sample_indices),
            }
        )


@dataclass(frozen=True)
class SRSInteractionDetectorResult:
    """Collection of pairwise or explicitly based SRS interactions."""

    comparisons: tuple[SRSInteractionComparisonResult, ...]

    def to_frame(self) -> pd.DataFrame:
        return pd.DataFrame([comparison.to_series() for comparison in self.comparisons])

    def summary(self) -> str:
        return str(self.to_frame().to_string(index=False))


@dataclass(frozen=True)
class SRSGeoDetectorResult:
    """Integrated SRS-GD factor, ecological and interaction results."""

    factor: SRSFactorDetectorResult
    ecological: SRSEcologicalDetectorResult
    interaction: SRSInteractionDetectorResult

    def summary(self) -> str:
        return (
            "SRSGeoDetectorResult("
            f"factors={len(self.factor.factors)}, "
            f"ecological={len(self.ecological.comparisons)}, "
            f"interactions={len(self.interaction.comparisons)})"
        )
