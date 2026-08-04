"""Classical interaction detector."""

from __future__ import annotations

from itertools import combinations
from typing import Any

from pygeohet.core.interaction import classify_interaction
from pygeohet.core.overlay import categorical_overlay
from pygeohet.core.qstat import q_statistic
from pygeohet.exceptions import InvalidDataError
from pygeohet.results import (
    InteractionComparisonResult,
    InteractionDetectorResult,
)
from pygeohet.validation import MissingPolicy, coerce_factor_frame, prepare_joint_data


class InteractionDetector:
    """Evaluate pairwise overlays of categorical factors."""

    def __init__(
        self,
        *,
        missing: MissingPolicy = "drop",
        min_stratum_size: int = 2,
        min_overlay_size: int = 1,
        atol: float = 1e-12,
        rtol: float = 1e-9,
    ) -> None:
        self.missing = missing
        if isinstance(min_overlay_size, bool) or min_overlay_size < 1:
            raise ValueError("min_overlay_size must be a positive integer")
        self.min_stratum_size = min_stratum_size
        self.min_overlay_size = min_overlay_size
        self.atol = atol
        self.rtol = rtol

    def fit(self, y: Any, factors: Any) -> InteractionDetectorResult:
        """Compute q values and interaction types for every factor pair."""

        factor_frame = coerce_factor_frame(factors)
        if factor_frame.shape[1] < 2:
            raise InvalidDataError(
                "interaction detector requires at least two factor columns"
            )

        comparisons_out = []
        for factor_1, factor_2 in combinations(factor_frame.columns, 2):
            pair = factor_frame[[factor_1, factor_2]]
            prepared = prepare_joint_data(y, pair, missing=self.missing)
            x1 = prepared.factors[factor_1]
            x2 = prepared.factors[factor_2]
            overlay = categorical_overlay(x1, x2)

            result_1 = q_statistic(
                prepared.y,
                x1,
                missing="raise",
                min_stratum_size=self.min_stratum_size,
            )
            result_2 = q_statistic(
                prepared.y,
                x2,
                missing="raise",
                min_stratum_size=self.min_stratum_size,
            )
            overlay_result = q_statistic(
                prepared.y,
                overlay,
                missing="raise",
                min_stratum_size=self.min_overlay_size,
            )
            interaction = classify_interaction(
                result_1.q,
                result_2.q,
                overlay_result.q,
                atol=self.atol,
                rtol=self.rtol,
            )
            comparisons_out.append(
                InteractionComparisonResult(
                    factor_1=str(factor_1),
                    factor_2=str(factor_2),
                    factor_1_result=result_1,
                    factor_2_result=result_2,
                    overlay_result=overlay_result,
                    interaction=interaction,
                    dropped_count=prepared.dropped_count,
                )
            )

        return InteractionDetectorResult(tuple(comparisons_out))


def interaction_detector(
    y: Any,
    factors: Any,
    *,
    missing: MissingPolicy = "drop",
    min_stratum_size: int = 2,
    min_overlay_size: int = 1,
    atol: float = 1e-12,
    rtol: float = 1e-9,
) -> InteractionDetectorResult:
    """Functional interface to :class:`InteractionDetector`."""

    return InteractionDetector(
        missing=missing,
        min_stratum_size=min_stratum_size,
        min_overlay_size=min_overlay_size,
        atol=atol,
        rtol=rtol,
    ).fit(y, factors)
