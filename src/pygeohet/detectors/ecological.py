"""Classical ecological detector with an explicit two-sided F convention."""

from __future__ import annotations

from itertools import combinations
from typing import Any, Literal

import numpy as np
from scipy.stats import f as f_distribution

from pygeohet.core.qstat import q_statistic
from pygeohet.exceptions import InvalidDataError
from pygeohet.results import (
    EcologicalComparisonResult,
    EcologicalDetectorResult,
)
from pygeohet.validation import MissingPolicy, coerce_factor_frame, prepare_joint_data


EcologicalAlternative = Literal["two-sided", "greater"]


class EcologicalDetector:
    """Compare residual within-stratum dispersion between factor pairs."""

    def __init__(
        self,
        *,
        alpha: float = 0.05,
        alternative: EcologicalAlternative = "two-sided",
        missing: MissingPolicy = "drop",
        min_stratum_size: int = 2,
    ) -> None:
        if not 0.0 < alpha < 1.0:
            raise ValueError("alpha must lie strictly between 0 and 1")
        if alternative not in {"two-sided", "greater"}:
            raise ValueError("alternative must be 'two-sided' or 'greater'")
        self.alpha = alpha
        self.alternative = alternative
        self.missing = missing
        self.min_stratum_size = min_stratum_size

    def fit(self, y: Any, factors: Any) -> EcologicalDetectorResult:
        """Return pairwise two-sided variance-ratio tests."""

        factor_frame = coerce_factor_frame(factors)
        if factor_frame.shape[1] < 2:
            raise InvalidDataError(
                "ecological detector requires at least two factor columns"
            )

        comparisons_out = []
        for factor_1, factor_2 in combinations(factor_frame.columns, 2):
            pair = factor_frame[[factor_1, factor_2]]
            prepared = prepare_joint_data(y, pair, missing=self.missing)
            result_1 = q_statistic(
                prepared.y,
                prepared.factors[factor_1],
                missing="raise",
                min_stratum_size=self.min_stratum_size,
            )
            result_2 = q_statistic(
                prepared.y,
                prepared.factors[factor_2],
                missing="raise",
                min_stratum_size=self.min_stratum_size,
            )
            n_1 = result_1.n_observations
            n_2 = result_2.n_observations
            f_statistic, p_value = _ecological_f_test(
                result_1.within_ss,
                result_2.within_ss,
                n_1,
                n_2,
                alternative=self.alternative,
            )
            significant = p_value < self.alpha
            more_explanatory = None
            if significant:
                if result_1.within_ss < result_2.within_ss:
                    more_explanatory = str(factor_1)
                elif result_2.within_ss < result_1.within_ss:
                    more_explanatory = str(factor_2)

            comparisons_out.append(
                EcologicalComparisonResult(
                    factor_1=str(factor_1),
                    factor_2=str(factor_2),
                    factor_1_result=result_1,
                    factor_2_result=result_2,
                    f_statistic=f_statistic,
                    df1=n_1 - 1,
                    df2=n_2 - 1,
                    p_value=p_value,
                    significant=significant,
                    more_explanatory=more_explanatory,
                    dropped_count=prepared.dropped_count,
                )
            )

        return EcologicalDetectorResult(
            tuple(comparisons_out), self.alpha, self.alternative
        )


def _ecological_f_test(
    within_ss_1: float,
    within_ss_2: float,
    n_1: int,
    n_2: int,
    *,
    alternative: EcologicalAlternative,
) -> tuple[float, float]:
    """Evaluate the primary-paper ecological F ratio and a two-sided p-value."""

    numerator = n_1 * (n_2 - 1) * within_ss_1
    denominator = n_2 * (n_1 - 1) * within_ss_2
    tolerance = np.finfo(float).eps * max(1.0, numerator, denominator)

    if numerator <= tolerance and denominator <= tolerance:
        return 1.0, 1.0
    if denominator <= tolerance:
        return float("inf"), 0.0
    if numerator <= tolerance:
        if alternative == "greater":
            return 0.0, 1.0
        return 0.0, 0.0

    f_statistic = float(numerator / denominator)
    df1 = n_1 - 1
    df2 = n_2 - 1
    upper = float(f_distribution.sf(f_statistic, df1, df2))
    if alternative == "greater":
        p_value = upper
    else:
        lower = float(f_distribution.cdf(f_statistic, df1, df2))
        p_value = float(min(1.0, 2.0 * min(lower, upper)))
    return f_statistic, p_value


def ecological_detector(
    y: Any,
    factors: Any,
    *,
    alpha: float = 0.05,
    alternative: EcologicalAlternative = "two-sided",
    missing: MissingPolicy = "drop",
    min_stratum_size: int = 2,
) -> EcologicalDetectorResult:
    """Functional interface to :class:`EcologicalDetector`."""

    return EcologicalDetector(
        alpha=alpha,
        alternative=alternative,
        missing=missing,
        min_stratum_size=min_stratum_size,
    ).fit(y, factors)
