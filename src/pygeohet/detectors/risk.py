"""Classical risk detector using pairwise Welch tests."""

from __future__ import annotations

from itertools import combinations
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import t as student_t

from pygeohet.exceptions import InvalidDataError
from pygeohet.results import (
    RiskComparisonResult,
    RiskDetectorResult,
    RiskStratumSummary,
)
from pygeohet.validation import MissingPolicy, coerce_factor_frame, prepare_factor_data


class RiskDetector:
    """Compare response means between all pairs of strata."""

    def __init__(
        self,
        *,
        alpha: float = 0.05,
        missing: MissingPolicy = "drop",
        min_stratum_size: int = 2,
    ) -> None:
        if not 0.0 < alpha < 1.0:
            raise ValueError("alpha must lie strictly between 0 and 1")
        self.alpha = alpha
        self.missing = missing
        self.min_stratum_size = min_stratum_size

    def fit(self, y: Any, factors: Any) -> RiskDetectorResult:
        """Return stratum summaries and pairwise Welch comparisons."""

        factor_frame = coerce_factor_frame(factors)
        if factor_frame.empty or factor_frame.shape[1] == 0:
            raise InvalidDataError("factors must contain at least one column")

        summaries = []
        comparisons_out = []
        dropped_counts = {}

        for factor in factor_frame.columns:
            prepared = prepare_factor_data(
                y,
                factor_frame[factor],
                missing=self.missing,
                min_stratum_size=self.min_stratum_size,
            )
            factor_name = str(factor)
            dropped_counts[factor_name] = prepared.dropped_count
            labels = list(pd.unique(prepared.strata))
            group_values = {}

            for label in labels:
                values = prepared.y[prepared.strata == label]
                mean = float(np.mean(values))
                variance = float(np.var(values, ddof=1))
                group_values[label] = values
                summaries.append(
                    RiskStratumSummary(
                        factor=factor_name,
                        stratum=label,
                        n=int(values.size),
                        mean=mean,
                        variance=variance,
                    )
                )

            for stratum_1, stratum_2 in combinations(labels, 2):
                comparison = _welch_comparison(
                    factor_name,
                    stratum_1,
                    stratum_2,
                    group_values[stratum_1],
                    group_values[stratum_2],
                    alpha=self.alpha,
                )
                comparisons_out.append(comparison)

        return RiskDetectorResult(
            strata=tuple(summaries),
            comparisons=tuple(comparisons_out),
            alpha=self.alpha,
            dropped_counts=dropped_counts,
        )


def _welch_comparison(
    factor: str,
    stratum_1: object,
    stratum_2: object,
    values_1: np.ndarray,
    values_2: np.ndarray,
    *,
    alpha: float,
) -> RiskComparisonResult:
    n_1 = int(values_1.size)
    n_2 = int(values_2.size)
    mean_1 = float(np.mean(values_1))
    mean_2 = float(np.mean(values_2))
    variance_1 = float(np.var(values_1, ddof=1))
    variance_2 = float(np.var(values_2, ddof=1))
    difference = mean_1 - mean_2

    component_1 = variance_1 / n_1
    component_2 = variance_2 / n_2
    standard_error_sq = component_1 + component_2
    tolerance = np.finfo(float).eps * max(
        1.0,
        abs(mean_1),
        abs(mean_2),
        variance_1,
        variance_2,
    )

    if standard_error_sq <= tolerance:
        if abs(difference) <= tolerance:
            t_statistic = 0.0
            df = float("inf")
            p_value = 1.0
        else:
            t_statistic = float(np.copysign(np.inf, difference))
            df = float("inf")
            p_value = 0.0
    else:
        t_statistic = float(difference / np.sqrt(standard_error_sq))
        denominator = component_1**2 / (n_1 - 1) + component_2**2 / (n_2 - 1)
        df = float(standard_error_sq**2 / denominator)
        p_value = float(2.0 * student_t.sf(abs(t_statistic), df))
        p_value = float(min(max(p_value, 0.0), 1.0))

    return RiskComparisonResult(
        factor=factor,
        stratum_1=stratum_1,
        stratum_2=stratum_2,
        n_1=n_1,
        n_2=n_2,
        mean_1=mean_1,
        mean_2=mean_2,
        difference=difference,
        t_statistic=t_statistic,
        df=df,
        p_value=p_value,
        significant=p_value < alpha,
    )


def risk_detector(
    y: Any,
    factors: Any,
    *,
    alpha: float = 0.05,
    missing: MissingPolicy = "drop",
    min_stratum_size: int = 2,
) -> RiskDetectorResult:
    """Functional interface to :class:`RiskDetector`."""

    return RiskDetector(
        alpha=alpha,
        missing=missing,
        min_stratum_size=min_stratum_size,
    ).fit(y, factors)
