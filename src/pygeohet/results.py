"""Immutable public result objects."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

import numpy as np
import pandas as pd

from pygeohet.core.interaction import InteractionType


@dataclass(frozen=True)
class QStatisticResult:
    """Result of one q-statistic calculation."""

    q: float
    p_value: float
    f_statistic: float
    noncentrality: float
    df1: int
    df2: int
    n_observations: int
    n_strata: int
    stratum_counts: Mapping[object, int]
    within_ss: float
    between_ss: float
    total_ss: float
    dropped_count: int

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "stratum_counts",
            MappingProxyType(dict(self.stratum_counts)),
        )

    def to_series(self) -> pd.Series:
        """Return the scalar result fields as a labelled series."""

        return pd.Series(
            {
                "q": self.q,
                "p_value": self.p_value,
                "f_statistic": self.f_statistic,
                "noncentrality": self.noncentrality,
                "df1": self.df1,
                "df2": self.df2,
                "n_observations": self.n_observations,
                "n_strata": self.n_strata,
                "within_ss": self.within_ss,
                "between_ss": self.between_ss,
                "total_ss": self.total_ss,
                "dropped_count": self.dropped_count,
            }
        )

    def summary(self) -> str:
        """Return a terminal-friendly statistical summary."""

        return (
            "QStatisticResult("
            f"q={self.q:.6g}, p_value={self.p_value:.6g}, "
            f"N={self.n_observations}, L={self.n_strata}, "
            f"SSW={self.within_ss:.6g}, SST={self.total_ss:.6g}, "
            f"dropped={self.dropped_count})"
        )


@dataclass(frozen=True)
class FactorDetectorResult:
    """Collection of q-statistic results for named factors."""

    factors: Mapping[str, QStatisticResult]

    def __post_init__(self) -> None:
        object.__setattr__(self, "factors", MappingProxyType(dict(self.factors)))

    def __getitem__(self, factor: str) -> QStatisticResult:
        return self.factors[factor]

    def to_frame(self) -> pd.DataFrame:
        """Return one row per factor with auditable scalar fields."""

        rows = []
        for name, result in self.factors.items():
            row = result.to_series().to_dict()
            row["factor"] = name
            rows.append(row)
        columns = [
            "factor",
            "q",
            "p_value",
            "f_statistic",
            "noncentrality",
            "df1",
            "df2",
            "n_observations",
            "n_strata",
            "within_ss",
            "between_ss",
            "total_ss",
            "dropped_count",
        ]
        return pd.DataFrame(rows, columns=columns)

    def summary(self) -> str:
        """Return a compact ordered text table."""

        return str(self.to_frame().to_string(index=False))


@dataclass(frozen=True)
class InteractionComparisonResult:
    """One pairwise interaction comparison on a joint complete-case sample."""

    factor_1: str
    factor_2: str
    factor_1_result: QStatisticResult
    factor_2_result: QStatisticResult
    overlay_result: QStatisticResult
    interaction: InteractionType
    dropped_count: int

    def to_series(self) -> pd.Series:
        """Return a flat auditable representation."""

        return pd.Series(
            {
                "factor_1": self.factor_1,
                "factor_2": self.factor_2,
                "q_1": self.factor_1_result.q,
                "q_2": self.factor_2_result.q,
                "q_overlay": self.overlay_result.q,
                "p_value_1": self.factor_1_result.p_value,
                "p_value_2": self.factor_2_result.p_value,
                "p_value_overlay": self.overlay_result.p_value,
                "interaction": self.interaction.value,
                "n_observations": self.overlay_result.n_observations,
                "overlay_strata": self.overlay_result.n_strata,
                "dropped_count": self.dropped_count,
            }
        )


@dataclass(frozen=True)
class InteractionDetectorResult:
    """Collection of pairwise classical interaction comparisons."""

    comparisons: tuple[InteractionComparisonResult, ...]

    def to_frame(self) -> pd.DataFrame:
        """Return one row per factor pair."""

        return pd.DataFrame([item.to_series() for item in self.comparisons])

    def summary(self) -> str:
        return str(self.to_frame().to_string(index=False))


@dataclass(frozen=True)
class RiskStratumSummary:
    """Sample summary for one stratum in the risk detector."""

    factor: str
    stratum: object
    n: int
    mean: float
    variance: float


@dataclass(frozen=True)
class RiskComparisonResult:
    """Welch comparison between two strata."""

    factor: str
    stratum_1: object
    stratum_2: object
    n_1: int
    n_2: int
    mean_1: float
    mean_2: float
    difference: float
    t_statistic: float
    df: float
    p_value: float
    significant: bool


@dataclass(frozen=True)
class RiskDetectorResult:
    """Risk-detector summaries and pairwise Welch tests."""

    strata: tuple[RiskStratumSummary, ...]
    comparisons: tuple[RiskComparisonResult, ...]
    alpha: float
    dropped_counts: Mapping[str, int]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "dropped_counts",
            MappingProxyType(dict(self.dropped_counts)),
        )

    def means_frame(self) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {
                    "factor": item.factor,
                    "stratum": item.stratum,
                    "n": item.n,
                    "mean": item.mean,
                    "variance": item.variance,
                    "dropped_count": self.dropped_counts[item.factor],
                }
                for item in self.strata
            ]
        )

    def comparisons_frame(self) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {
                    "factor": item.factor,
                    "stratum_1": item.stratum_1,
                    "stratum_2": item.stratum_2,
                    "n_1": item.n_1,
                    "n_2": item.n_2,
                    "mean_1": item.mean_1,
                    "mean_2": item.mean_2,
                    "difference": item.difference,
                    "t_statistic": item.t_statistic,
                    "df": item.df,
                    "p_value": item.p_value,
                    "significant": item.significant,
                }
                for item in self.comparisons
            ]
        )

    def pvalue_matrix(self, factor: str) -> pd.DataFrame:
        """Return a symmetric pairwise p-value matrix for one factor."""

        labels = [item.stratum for item in self.strata if item.factor == factor]
        if not labels:
            raise KeyError(factor)
        matrix = pd.DataFrame(
            np.eye(len(labels), dtype=float),
            index=labels,
            columns=labels,
        )
        for item in self.comparisons:
            if item.factor != factor:
                continue
            matrix.loc[item.stratum_1, item.stratum_2] = item.p_value
            matrix.loc[item.stratum_2, item.stratum_1] = item.p_value
        return matrix

    def summary(self) -> str:
        return str(self.comparisons_frame().to_string(index=False))


@dataclass(frozen=True)
class EcologicalComparisonResult:
    """One two-sided ecological variance-ratio comparison."""

    factor_1: str
    factor_2: str
    factor_1_result: QStatisticResult
    factor_2_result: QStatisticResult
    f_statistic: float
    df1: int
    df2: int
    p_value: float
    significant: bool
    more_explanatory: str | None
    dropped_count: int

    def to_series(self) -> pd.Series:
        return pd.Series(
            {
                "factor_1": self.factor_1,
                "factor_2": self.factor_2,
                "q_1": self.factor_1_result.q,
                "q_2": self.factor_2_result.q,
                "within_ss_1": self.factor_1_result.within_ss,
                "within_ss_2": self.factor_2_result.within_ss,
                "f_statistic": self.f_statistic,
                "df1": self.df1,
                "df2": self.df2,
                "p_value": self.p_value,
                "significant": self.significant,
                "more_explanatory": self.more_explanatory,
                "n_observations": self.factor_1_result.n_observations,
                "dropped_count": self.dropped_count,
            }
        )


@dataclass(frozen=True)
class EcologicalDetectorResult:
    """Collection of pairwise ecological comparisons."""

    comparisons: tuple[EcologicalComparisonResult, ...]
    alpha: float
    alternative: str

    def to_frame(self) -> pd.DataFrame:
        return pd.DataFrame([item.to_series() for item in self.comparisons])

    def summary(self) -> str:
        return str(self.to_frame().to_string(index=False))


@dataclass(frozen=True)
class GeoDetectorResult:
    """Integrated classical geographical-detector workflow result."""

    factor: FactorDetectorResult
    risk: RiskDetectorResult
    interaction: InteractionDetectorResult | None
    ecological: EcologicalDetectorResult | None

    def summary(self) -> str:
        sections = [
            "Factor detector",
            self.factor.summary(),
            "",
            "Risk detector",
            self.risk.summary(),
        ]
        if self.interaction is not None:
            sections.extend(["", "Interaction detector", self.interaction.summary()])
        if self.ecological is not None:
            sections.extend(["", "Ecological detector", self.ecological.summary()])
        return "\n".join(sections)
