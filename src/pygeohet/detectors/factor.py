"""Classical factor detector."""

from __future__ import annotations

from typing import Any

from pygeohet.core.qstat import q_statistic
from pygeohet.exceptions import InvalidDataError
from pygeohet.results import FactorDetectorResult
from pygeohet.validation import MissingPolicy, coerce_factor_frame


class FactorDetector:
    """Evaluate q-statistics for one or more categorical factors."""

    def __init__(
        self,
        *,
        missing: MissingPolicy = "drop",
        min_stratum_size: int = 2,
    ) -> None:
        self.missing = missing
        self.min_stratum_size = min_stratum_size

    def fit(self, y: Any, factors: Any) -> FactorDetectorResult:
        """Compute one auditable q-statistic result per factor."""

        factor_frame = coerce_factor_frame(factors)
        if factor_frame.empty or factor_frame.shape[1] == 0:
            raise InvalidDataError("factors must contain at least one column")

        results = {}
        for name in factor_frame.columns:
            results[name] = q_statistic(
                y,
                factor_frame[name],
                missing=self.missing,
                min_stratum_size=self.min_stratum_size,
            )
        return FactorDetectorResult(results)


def factor_detector(
    y: Any,
    factors: Any,
    *,
    missing: MissingPolicy = "drop",
    min_stratum_size: int = 2,
) -> FactorDetectorResult:
    """Functional interface to :class:`FactorDetector`."""

    return FactorDetector(
        missing=missing,
        min_stratum_size=min_stratum_size,
    ).fit(y, factors)
