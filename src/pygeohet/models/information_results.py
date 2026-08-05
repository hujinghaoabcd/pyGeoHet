"""Immutable results for information-consistency SSH estimators."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Literal, TypeAlias

import pandas as pd

InformationTargetKind = Literal["nominal", "continuous"]


@dataclass(frozen=True)
class NominalJointCount:
    """One cell of the nominal target-by-stratum contingency table."""

    stratum: Any
    target: Any
    count: int
    joint_probability: float
    conditional_probability: float

    def to_series(self) -> pd.Series:
        return pd.Series(
            {
                "stratum": self.stratum,
                "target": self.target,
                "count": self.count,
                "joint_probability": self.joint_probability,
                "conditional_probability": self.conditional_probability,
            }
        )


@dataclass(frozen=True)
class NominalInformationConsistencyResult:
    """Normalized mutual information and complete nominal evidence."""

    value: float
    target_entropy: float
    conditional_entropy: float
    mutual_information: float
    target_probabilities: Mapping[Any, float]
    stratum_probabilities: Mapping[Any, float]
    joint_counts: tuple[NominalJointCount, ...]
    n_observations: int
    total_length: int
    dropped_count: int
    used_indices: tuple[int, ...]
    p_value: float | None = None
    permutations: int = 0
    null_mean: float | None = None
    null_standard_deviation: float | None = None
    random_state: int | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "target_probabilities",
            MappingProxyType(dict(self.target_probabilities)),
        )
        object.__setattr__(
            self,
            "stratum_probabilities",
            MappingProxyType(dict(self.stratum_probabilities)),
        )
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def IN(self) -> float:
        """Return the nominal information-consistency statistic."""

        return self.value

    def contingency_frame(self) -> pd.DataFrame:
        """Return observed target-by-stratum cells."""

        return pd.DataFrame([cell.to_series() for cell in self.joint_counts])

    def to_series(self) -> pd.Series:
        """Return scalar fields as a labelled series."""

        return pd.Series(
            {
                "kind": "nominal",
                "IN": self.value,
                "target_entropy": self.target_entropy,
                "conditional_entropy": self.conditional_entropy,
                "mutual_information": self.mutual_information,
                "p_value": self.p_value,
                "n_observations": self.n_observations,
                "dropped_count": self.dropped_count,
                "target_categories": len(self.target_probabilities),
                "strata": len(self.stratum_probabilities),
                "permutations": self.permutations,
            }
        )

    def summary(self) -> str:
        p_text = "None" if self.p_value is None else f"{self.p_value:.6g}"
        return (
            "NominalInformationConsistencyResult("
            f"IN={self.value:.6g}, H={self.target_entropy:.6g}, "
            f"H_cond={self.conditional_entropy:.6g}, p={p_text}, "
            f"n={self.n_observations}, strata={len(self.stratum_probabilities)})"
        )


@dataclass(frozen=True)
class ContinuousStratumContribution:
    """One stratum's relative-entropy contribution to continuous IC-SSH."""

    stratum: Any
    count: int
    probability: float
    kl_divergence: float
    transformed_divergence: float
    weighted_contribution: float
    histogram_probabilities: tuple[float, ...]

    def to_series(self) -> pd.Series:
        return pd.Series(
            {
                "stratum": self.stratum,
                "count": self.count,
                "probability": self.probability,
                "kl_divergence": self.kl_divergence,
                "transformed_divergence": self.transformed_divergence,
                "weighted_contribution": self.weighted_contribution,
                "histogram_probabilities": self.histogram_probabilities,
            }
        )


@dataclass(frozen=True)
class ContinuousInformationConsistencyResult:
    """Histogram relative-entropy information consistency and evidence."""

    value: float
    bin_edges: tuple[float, ...]
    bin_method: str
    global_histogram_probabilities: tuple[float, ...]
    contributions: tuple[ContinuousStratumContribution, ...]
    n_observations: int
    total_length: int
    dropped_count: int
    used_indices: tuple[int, ...]
    p_value: float | None = None
    permutations: int = 0
    null_mean: float | None = None
    null_standard_deviation: float | None = None
    random_state: int | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def IC(self) -> float:
        """Return the continuous information-consistency statistic."""

        return self.value

    @property
    def bin_count(self) -> int:
        return len(self.bin_edges) - 1

    def contributions_frame(self) -> pd.DataFrame:
        """Return one row per observed stratum."""

        return pd.DataFrame(
            [contribution.to_series() for contribution in self.contributions]
        )

    def histogram_frame(self) -> pd.DataFrame:
        """Return global histogram bins and probabilities."""

        return pd.DataFrame(
            {
                "left": self.bin_edges[:-1],
                "right": self.bin_edges[1:],
                "global_probability": self.global_histogram_probabilities,
            }
        )

    def to_series(self) -> pd.Series:
        """Return scalar fields as a labelled series."""

        return pd.Series(
            {
                "kind": "continuous",
                "IC": self.value,
                "p_value": self.p_value,
                "n_observations": self.n_observations,
                "dropped_count": self.dropped_count,
                "strata": len(self.contributions),
                "bin_method": self.bin_method,
                "bin_count": self.bin_count,
                "permutations": self.permutations,
            }
        )

    def summary(self) -> str:
        p_text = "None" if self.p_value is None else f"{self.p_value:.6g}"
        return (
            "ContinuousInformationConsistencyResult("
            f"IC={self.value:.6g}, p={p_text}, n={self.n_observations}, "
            f"strata={len(self.contributions)}, bins={self.bin_count}, "
            f"method={self.bin_method!r})"
        )


InformationConsistencyResult: TypeAlias = (
    NominalInformationConsistencyResult | ContinuousInformationConsistencyResult
)


@dataclass(frozen=True)
class InformationConsistencyFactorResult:
    """Common-sample information-consistency results for multiple factors."""

    target_kind: InformationTargetKind
    factors: Mapping[str, InformationConsistencyResult]
    n_observations: int
    total_length: int
    dropped_count: int
    used_indices: tuple[int, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "factors", MappingProxyType(dict(self.factors)))

    def __getitem__(self, factor: str) -> InformationConsistencyResult:
        return self.factors[factor]

    def to_frame(self) -> pd.DataFrame:
        """Return one row per factor ordered by decreasing consistency."""

        rows: list[dict[str, Any]] = []
        value_name = "IN" if self.target_kind == "nominal" else "IC"
        for name, result in self.factors.items():
            row = result.to_series().to_dict()
            row["factor"] = name
            rows.append(row)
        if not rows:
            return pd.DataFrame()
        frame = pd.DataFrame(rows)
        columns = ["factor", *[column for column in frame if column != "factor"]]
        return frame.loc[:, columns].sort_values(
            [value_name, "factor"],
            ascending=[False, True],
            kind="stable",
            ignore_index=True,
        )

    def summary(self) -> str:
        return (
            "InformationConsistencyFactorResult("
            f"kind={self.target_kind!r}, factors={len(self.factors)}, "
            f"n={self.n_observations}, dropped={self.dropped_count})"
        )
