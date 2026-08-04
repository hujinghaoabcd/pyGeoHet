"""Optimal parameters-based geographical detector workflow."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

import pandas as pd

from pygeohet.detectors.ecological import EcologicalAlternative
from pygeohet.exceptions import InvalidDataError
from pygeohet.models.geodetector import GeoDetector
from pygeohet.results import GeoDetectorResult
from pygeohet.stratification import (
    OptimalStratificationResult,
    optimize_stratification,
)
from pygeohet.validation import MissingPolicy, coerce_factor_frame


@dataclass(frozen=True)
class OPGDResult:
    """Optimal discretizations, full candidate evidence, and detector results."""

    optimizations: Mapping[str, OptimalStratificationResult]
    discrete_labels: Mapping[str, tuple[int | None, ...]]
    detector: GeoDetectorResult

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "optimizations",
            MappingProxyType(dict(self.optimizations)),
        )
        object.__setattr__(
            self,
            "discrete_labels",
            MappingProxyType(
                {name: tuple(labels) for name, labels in self.discrete_labels.items()}
            ),
        )

    def optimal_frame(self) -> pd.DataFrame:
        """Return one winning-parameter row per continuous factor."""

        rows = []
        for factor, optimization in self.optimizations.items():
            row = optimization.best_series().to_dict()
            row["factor"] = factor
            rows.append(row)
        if not rows:
            return pd.DataFrame()
        frame = pd.DataFrame(rows)
        columns = [
            "factor",
            *[name for name in frame.columns if name != "factor"],
        ]
        return frame.loc[:, columns]

    def candidates_frame(self, factor: str | None = None) -> pd.DataFrame:
        """Return full candidate audits for one or all factors."""

        if factor is not None:
            try:
                frame = self.optimizations[factor].candidates_frame()
            except KeyError as exc:
                raise KeyError(factor) from exc
            frame.insert(0, "factor", factor)
            return frame

        frames = []
        for name, optimization in self.optimizations.items():
            frame = optimization.candidates_frame()
            frame.insert(0, "factor", name)
            frames.append(frame)
        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

    def discretized_frame(self) -> pd.DataFrame:
        """Return the selected discrete factor labels aligned to the input rows."""

        return pd.DataFrame(dict(self.discrete_labels), dtype=object)

    def summary(self) -> str:
        """Return optimal parameters followed by the classical workflow summary."""

        return "\n".join(
            [
                "Optimal discretization",
                self.optimal_frame().to_string(index=False),
                "",
                self.detector.summary(),
            ]
        )


class OPGD:
    """Optimize univariate discretization before running GeoDetector."""

    def __init__(
        self,
        *,
        methods: Sequence[str] = (
            "standard_deviation",
            "equal_interval",
            "geometric_interval",
            "quantile",
            "natural_breaks",
        ),
        n_strata: Iterable[int] = range(3, 9),
        alpha: float = 0.05,
        ecological_alternative: EcologicalAlternative = "two-sided",
        missing: MissingPolicy = "drop",
        min_stratum_size: int = 2,
        min_overlay_size: int = 1,
        require_requested_strata: bool = True,
        q_tolerance: float = 1e-12,
        head_tail_threshold: float = 0.4,
    ) -> None:
        self.methods = tuple(methods)
        self.n_strata = tuple(n_strata)
        self.alpha = alpha
        self.ecological_alternative = ecological_alternative
        self.missing = missing
        self.min_stratum_size = min_stratum_size
        self.min_overlay_size = min_overlay_size
        self.require_requested_strata = require_requested_strata
        self.q_tolerance = q_tolerance
        self.head_tail_threshold = head_tail_threshold

    def fit(self, y: Any, continuous_factors: Any) -> OPGDResult:
        """Optimize every continuous factor, then run the classical workflow."""

        factor_frame = coerce_factor_frame(continuous_factors)
        if factor_frame.empty or factor_frame.shape[1] == 0:
            raise InvalidDataError(
                "continuous_factors must contain at least one column"
            )

        optimizations: dict[str, OptimalStratificationResult] = {}
        labels: dict[str, tuple[int | None, ...]] = {}
        for name in factor_frame.columns:
            optimization = optimize_stratification(
                y,
                factor_frame[name],
                methods=self.methods,
                n_strata=self.n_strata,
                missing=self.missing,
                min_stratum_size=self.min_stratum_size,
                require_requested_strata=self.require_requested_strata,
                q_tolerance=self.q_tolerance,
                head_tail_threshold=self.head_tail_threshold,
            )
            if optimization.best is None:
                reasons = sorted(
                    {
                        item.rejection_reason
                        for item in optimization.candidates
                        if item.rejection_reason is not None
                    }
                )
                detail = "; ".join(reasons) if reasons else "no accepted candidate"
                raise InvalidDataError(
                    f"factor {name!r} has no valid discretization: {detail}"
                )
            optimizations[name] = optimization
            labels[name] = optimization.best.stratification.labels

        detector = GeoDetector(
            alpha=self.alpha,
            ecological_alternative=self.ecological_alternative,
            missing=self.missing,
            min_stratum_size=self.min_stratum_size,
            min_overlay_size=self.min_overlay_size,
        ).fit(y, pd.DataFrame(labels, dtype=object))

        return OPGDResult(
            optimizations=optimizations,
            discrete_labels=labels,
            detector=detector,
        )


def opgd(
    y: Any,
    continuous_factors: Any,
    *,
    methods: Sequence[str] = (
        "standard_deviation",
        "equal_interval",
        "geometric_interval",
        "quantile",
        "natural_breaks",
    ),
    n_strata: Iterable[int] = range(3, 9),
    alpha: float = 0.05,
    ecological_alternative: EcologicalAlternative = "two-sided",
    missing: MissingPolicy = "drop",
    min_stratum_size: int = 2,
    min_overlay_size: int = 1,
    require_requested_strata: bool = True,
    q_tolerance: float = 1e-12,
    head_tail_threshold: float = 0.4,
) -> OPGDResult:
    """Functional interface to :class:`OPGD`."""

    return OPGD(
        methods=methods,
        n_strata=n_strata,
        alpha=alpha,
        ecological_alternative=ecological_alternative,
        missing=missing,
        min_stratum_size=min_stratum_size,
        min_overlay_size=min_overlay_size,
        require_requested_strata=require_requested_strata,
        q_tolerance=q_tolerance,
        head_tail_threshold=head_tail_threshold,
    ).fit(y, continuous_factors)
