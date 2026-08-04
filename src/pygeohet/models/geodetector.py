"""Integrated classical geographical-detector workflow."""

from __future__ import annotations

from typing import Any

from pygeohet.detectors.ecological import (
    EcologicalAlternative,
    EcologicalDetector,
)
from pygeohet.detectors.factor import FactorDetector
from pygeohet.detectors.interaction import InteractionDetector
from pygeohet.detectors.risk import RiskDetector
from pygeohet.results import GeoDetectorResult
from pygeohet.validation import MissingPolicy, coerce_factor_frame


class GeoDetector:
    """Run the complete classical detector family with shared configuration."""

    def __init__(
        self,
        *,
        alpha: float = 0.05,
        ecological_alternative: EcologicalAlternative = "two-sided",
        missing: MissingPolicy = "drop",
        min_stratum_size: int = 2,
        min_overlay_size: int = 1,
        interaction_atol: float = 1e-12,
        interaction_rtol: float = 1e-9,
    ) -> None:
        self.alpha = alpha
        self.ecological_alternative = ecological_alternative
        self.missing = missing
        self.min_stratum_size = min_stratum_size
        self.min_overlay_size = min_overlay_size
        self.interaction_atol = interaction_atol
        self.interaction_rtol = interaction_rtol

    def fit(self, y: Any, factors: Any) -> GeoDetectorResult:
        """Run factor and risk detectors, plus pairwise detectors when possible."""

        factor_frame = coerce_factor_frame(factors)
        factor_result = FactorDetector(
            missing=self.missing,
            min_stratum_size=self.min_stratum_size,
        ).fit(y, factor_frame)
        risk_result = RiskDetector(
            alpha=self.alpha,
            missing=self.missing,
            min_stratum_size=self.min_stratum_size,
        ).fit(y, factor_frame)

        interaction_result = None
        ecological_result = None
        if factor_frame.shape[1] >= 2:
            interaction_result = InteractionDetector(
                missing=self.missing,
                min_stratum_size=self.min_stratum_size,
                min_overlay_size=self.min_overlay_size,
                atol=self.interaction_atol,
                rtol=self.interaction_rtol,
            ).fit(y, factor_frame)
            ecological_result = EcologicalDetector(
                alpha=self.alpha,
                alternative=self.ecological_alternative,
                missing=self.missing,
                min_stratum_size=self.min_stratum_size,
            ).fit(y, factor_frame)

        return GeoDetectorResult(
            factor=factor_result,
            risk=risk_result,
            interaction=interaction_result,
            ecological=ecological_result,
        )


def geodetector(
    y: Any,
    factors: Any,
    *,
    alpha: float = 0.05,
    ecological_alternative: EcologicalAlternative = "two-sided",
    missing: MissingPolicy = "drop",
    min_stratum_size: int = 2,
    min_overlay_size: int = 1,
    interaction_atol: float = 1e-12,
    interaction_rtol: float = 1e-9,
) -> GeoDetectorResult:
    """Functional interface to :class:`GeoDetector`."""

    return GeoDetector(
        alpha=alpha,
        ecological_alternative=ecological_alternative,
        missing=missing,
        min_stratum_size=min_stratum_size,
        min_overlay_size=min_overlay_size,
        interaction_atol=interaction_atol,
        interaction_rtol=interaction_rtol,
    ).fit(y, factors)
