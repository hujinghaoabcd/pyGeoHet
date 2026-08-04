"""Immutable public result objects."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

import pandas as pd


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

        return self.to_frame().to_string(index=False)
