"""Spatial-unit size effects and primary-paper OPGD scale selection."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Literal

import numpy as np
import pandas as pd

from pygeohet.exceptions import InvalidDataError
from pygeohet.models.opgd import OPGD, OPGDResult
from pygeohet.results import FactorDetectorResult, GeoDetectorResult

ScaleScoreMethod = Literal["quantile", "mean"]
ScaleTieBreak = Literal["first", "smallest", "largest"]

_PAPER_TIE_RULE = (
    "maximum scale score; values within score_tolerance are tied; "
    "ties follow the configured tie_break policy"
)


@dataclass(frozen=True)
class SpatialScaleCandidateResult:
    """Factor-level q evidence and one aggregate score at one spatial scale."""

    scale: float
    source_order: int
    q_values: Mapping[str, float]
    p_values: Mapping[str, float]
    eligible_factors: tuple[str, ...]
    excluded_factors: tuple[str, ...]
    score: float | None
    accepted: bool
    rejection_reason: str | None

    def __post_init__(self) -> None:
        object.__setattr__(self, "q_values", MappingProxyType(dict(self.q_values)))
        object.__setattr__(self, "p_values", MappingProxyType(dict(self.p_values)))

    def to_series(self) -> pd.Series:
        """Return one scale-level audit row."""

        return pd.Series(
            {
                "scale": self.scale,
                "source_order": self.source_order,
                "score": self.score,
                "accepted": self.accepted,
                "eligible_factor_count": len(self.eligible_factors),
                "excluded_factor_count": len(self.excluded_factors),
                "eligible_factors": self.eligible_factors,
                "excluded_factors": self.excluded_factors,
                "rejection_reason": self.rejection_reason,
            }
        )

    def factors_frame(self) -> pd.DataFrame:
        """Return one row per factor at this scale."""

        eligible = set(self.eligible_factors)
        return pd.DataFrame(
            [
                {
                    "scale": self.scale,
                    "factor": factor,
                    "q": q_value,
                    "p_value": self.p_values[factor],
                    "eligible": factor in eligible,
                }
                for factor, q_value in self.q_values.items()
            ]
        )


@dataclass(frozen=True)
class SpatialScaleResult:
    """Complete spatial-scale candidate evidence and deterministic selection."""

    candidates: tuple[SpatialScaleCandidateResult, ...]
    best: SpatialScaleCandidateResult | None
    score_method: ScaleScoreMethod
    quantile: float
    significant_only: bool
    alpha: float
    tie_break: ScaleTieBreak
    tie_rule: str
    score_tolerance: float
    selection_valid: bool
    selection_reason: str | None

    def candidates_frame(self) -> pd.DataFrame:
        """Return one row per attempted spatial scale."""

        return pd.DataFrame([candidate.to_series() for candidate in self.candidates])

    def factors_frame(self) -> pd.DataFrame:
        """Return long-form factor q and p evidence across all scales."""

        frames = [candidate.factors_frame() for candidate in self.candidates]
        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

    def best_series(self) -> pd.Series:
        """Return the selected scale as a series."""

        if self.best is None:
            return pd.Series(dtype=object)
        return self.best.to_series()

    def summary(self) -> str:
        """Return a compact text summary."""

        if self.best is None:
            return (
                "SpatialScaleResult(no valid selection; "
                f"reason={self.selection_reason!r}, "
                f"attempted={len(self.candidates)})"
            )
        return (
            "SpatialScaleResult("
            f"scale={self.best.scale:g}, score={self.best.score:.6g}, "
            f"method={self.score_method!r}, "
            f"eligible={len(self.best.eligible_factors)}, "
            f"attempted={len(self.candidates)})"
        )


@dataclass(frozen=True)
class SpatialScaleOPGDResult:
    """Scale effects plus the OPGD result produced at every successful scale."""

    scale_effects: SpatialScaleResult
    opgd_results: Mapping[float, OPGDResult]
    failures: Mapping[float, str]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "opgd_results",
            MappingProxyType(dict(self.opgd_results)),
        )
        object.__setattr__(self, "failures", MappingProxyType(dict(self.failures)))

    @property
    def best_opgd(self) -> OPGDResult | None:
        """Return the OPGD workflow result at the selected scale."""

        best = self.scale_effects.best
        if best is None:
            return None
        return self.opgd_results.get(best.scale)

    def candidates_frame(self) -> pd.DataFrame:
        return self.scale_effects.candidates_frame()

    def factors_frame(self) -> pd.DataFrame:
        return self.scale_effects.factors_frame()

    def summary(self) -> str:
        sections = [self.scale_effects.summary()]
        if self.failures:
            sections.extend(["", f"Failed scales: {dict(self.failures)!r}"])
        if self.best_opgd is not None:
            sections.extend(["", "Selected-scale OPGD", self.best_opgd.summary()])
        return "\n".join(sections)


def _coerce_scale(scale: Any) -> float:
    if isinstance(scale, bool):
        raise ValueError("spatial scales must be finite numeric values")
    try:
        value = float(scale)
    except (TypeError, ValueError) as exc:
        raise ValueError("spatial scales must be finite numeric values") from exc
    if not np.isfinite(value):
        raise ValueError("spatial scales must be finite numeric values")
    return value


def _factor_frame(result: Any) -> pd.DataFrame:
    if isinstance(result, OPGDResult):
        frame = result.detector.factor.to_frame()
    elif isinstance(result, GeoDetectorResult):
        frame = result.factor.to_frame()
    elif isinstance(result, FactorDetectorResult):
        frame = result.to_frame()
    elif isinstance(result, pd.DataFrame):
        frame = result.copy()
    else:
        raise TypeError(
            "scale results must be OPGDResult, GeoDetectorResult, "
            "FactorDetectorResult, or a DataFrame"
        )

    required = {"factor", "q", "p_value"}
    missing = required.difference(frame.columns)
    if missing:
        raise InvalidDataError(
            f"factor result table is missing columns: {sorted(missing)!r}"
        )
    selected = frame.loc[:, ["factor", "q", "p_value"]].copy()
    selected["factor"] = selected["factor"].astype(str)
    if selected["factor"].duplicated().any():
        raise InvalidDataError("factor names must be unique within each scale")
    selected["q"] = pd.to_numeric(selected["q"], errors="raise").astype(float)
    selected["p_value"] = pd.to_numeric(
        selected["p_value"], errors="raise"
    ).astype(float)
    if not bool(np.isfinite(selected["q"]).all()):
        raise InvalidDataError("q values must be finite")
    if bool(((selected["q"] < 0.0) | (selected["q"] > 1.0)).any()):
        raise InvalidDataError("q values must lie in [0, 1]")
    finite_p = selected["p_value"].dropna()
    if not bool(np.isfinite(finite_p).all()):
        raise InvalidDataError("non-missing p-values must be finite")
    return selected.reset_index(drop=True)


def _scale_score(
    q_values: np.ndarray,
    *,
    score_method: ScaleScoreMethod,
    quantile: float,
) -> float:
    if score_method == "quantile":
        return float(np.quantile(q_values, quantile, method="linear"))
    if score_method == "mean":
        return float(np.mean(q_values))
    raise ValueError("score_method must be either 'quantile' or 'mean'")


def _choose_best(
    candidates: list[SpatialScaleCandidateResult],
    *,
    tie_break: ScaleTieBreak,
    score_tolerance: float,
) -> SpatialScaleCandidateResult | None:
    accepted = [
        candidate
        for candidate in candidates
        if candidate.accepted and candidate.score is not None
    ]
    if len(accepted) < 2:
        return None
    maximum = max(float(candidate.score) for candidate in accepted)
    tied = [
        candidate
        for candidate in accepted
        if maximum - float(candidate.score) <= score_tolerance
    ]
    if tie_break == "first":
        return min(tied, key=lambda candidate: candidate.source_order)
    if tie_break == "smallest":
        return min(tied, key=lambda candidate: (candidate.scale, candidate.source_order))
    if tie_break == "largest":
        return max(tied, key=lambda candidate: (candidate.scale, -candidate.source_order))
    raise ValueError("tie_break must be 'first', 'smallest', or 'largest'")


def _compare_frames(
    frames: Mapping[float, pd.DataFrame],
    *,
    failures: Mapping[float, str] | None,
    source_order: Mapping[float, int],
    score_method: ScaleScoreMethod,
    quantile: float,
    significant_only: bool,
    alpha: float,
    tie_break: ScaleTieBreak,
    score_tolerance: float,
) -> SpatialScaleResult:
    if score_method not in {"quantile", "mean"}:
        raise ValueError("score_method must be either 'quantile' or 'mean'")
    if not 0.0 <= quantile <= 1.0:
        raise ValueError("quantile must lie in [0, 1]")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie strictly between 0 and 1")
    if score_tolerance < 0.0:
        raise ValueError("score_tolerance must be nonnegative")
    if tie_break not in {"first", "smallest", "largest"}:
        raise ValueError("tie_break must be 'first', 'smallest', or 'largest'")

    failures = failures or {}
    successful_scales = list(frames)
    if successful_scales:
        reference_factors = tuple(frames[successful_scales[0]]["factor"])
        reference_set = set(reference_factors)
        for scale in successful_scales[1:]:
            current = tuple(frames[scale]["factor"])
            if set(current) != reference_set:
                raise InvalidDataError(
                    "all successful spatial scales must contain the same factors"
                )

    candidates: list[SpatialScaleCandidateResult] = []
    for scale, order in sorted(source_order.items(), key=lambda item: item[1]):
        if scale in failures:
            candidates.append(
                SpatialScaleCandidateResult(
                    scale=scale,
                    source_order=order,
                    q_values={},
                    p_values={},
                    eligible_factors=(),
                    excluded_factors=(),
                    score=None,
                    accepted=False,
                    rejection_reason=failures[scale],
                )
            )
            continue

        frame = frames[scale]
        q_values = {
            str(row.factor): float(row.q)
            for row in frame.itertuples(index=False)
        }
        p_values = {
            str(row.factor): float(row.p_value)
            for row in frame.itertuples(index=False)
        }
        if significant_only:
            eligible = tuple(
                factor
                for factor in q_values
                if np.isnan(p_values[factor]) or p_values[factor] <= alpha
            )
        else:
            eligible = tuple(q_values)
        excluded = tuple(factor for factor in q_values if factor not in eligible)

        if not eligible:
            candidates.append(
                SpatialScaleCandidateResult(
                    scale=scale,
                    source_order=order,
                    q_values=q_values,
                    p_values=p_values,
                    eligible_factors=(),
                    excluded_factors=excluded,
                    score=None,
                    accepted=False,
                    rejection_reason="no eligible factor q values remain at this scale",
                )
            )
            continue

        score = _scale_score(
            np.asarray([q_values[factor] for factor in eligible], dtype=float),
            score_method=score_method,
            quantile=quantile,
        )
        candidates.append(
            SpatialScaleCandidateResult(
                scale=scale,
                source_order=order,
                q_values=q_values,
                p_values=p_values,
                eligible_factors=eligible,
                excluded_factors=excluded,
                score=score,
                accepted=True,
                rejection_reason=None,
            )
        )

    best = _choose_best(
        candidates,
        tie_break=tie_break,
        score_tolerance=score_tolerance,
    )
    accepted_count = sum(candidate.accepted for candidate in candidates)
    selection_valid = best is not None
    selection_reason = None
    if not selection_valid:
        selection_reason = (
            "at least two spatial scales with eligible factor q values are required"
        )

    return SpatialScaleResult(
        candidates=tuple(candidates),
        best=best,
        score_method=score_method,
        quantile=float(quantile),
        significant_only=bool(significant_only),
        alpha=float(alpha),
        tie_break=tie_break,
        tie_rule=_PAPER_TIE_RULE,
        score_tolerance=float(score_tolerance),
        selection_valid=selection_valid,
        selection_reason=selection_reason,
    )


def compare_spatial_scales(
    results_by_scale: Mapping[Any, Any],
    *,
    score_method: ScaleScoreMethod = "quantile",
    quantile: float = 0.9,
    significant_only: bool = False,
    alpha: float = 0.05,
    tie_break: ScaleTieBreak = "first",
    score_tolerance: float = 1e-12,
) -> SpatialScaleResult:
    """Compare already-computed factor results across prepared spatial scales.

    The primary-paper convention is ``score_method='quantile'`` with
    ``quantile=0.9`` and ``significant_only=False``. Set
    ``significant_only=True`` to reproduce the significance filtering used by
    the legacy GD ``sesu`` helper before its 90% quantile calculation.
    """

    if len(results_by_scale) < 2:
        raise InvalidDataError("at least two spatial scales are required")

    frames: dict[float, pd.DataFrame] = {}
    source_order: dict[float, int] = {}
    for order, (raw_scale, result) in enumerate(results_by_scale.items()):
        scale = _coerce_scale(raw_scale)
        if scale in frames:
            raise InvalidDataError("spatial scales must be unique after numeric coercion")
        frames[scale] = _factor_frame(result)
        source_order[scale] = order

    return _compare_frames(
        frames,
        failures=None,
        source_order=source_order,
        score_method=score_method,
        quantile=quantile,
        significant_only=significant_only,
        alpha=alpha,
        tie_break=tie_break,
        score_tolerance=score_tolerance,
    )


class SpatialScaleOPGD:
    """Run OPGD on prepared datasets and compare their spatial-unit sizes."""

    def __init__(
        self,
        *,
        score_method: ScaleScoreMethod = "quantile",
        quantile: float = 0.9,
        significant_only: bool = False,
        scale_alpha: float = 0.05,
        tie_break: ScaleTieBreak = "first",
        score_tolerance: float = 1e-12,
        **opgd_kwargs: Any,
    ) -> None:
        self.score_method = score_method
        self.quantile = quantile
        self.significant_only = significant_only
        self.scale_alpha = scale_alpha
        self.tie_break = tie_break
        self.score_tolerance = score_tolerance
        self.opgd_kwargs = dict(opgd_kwargs)

    def fit(
        self,
        data_by_scale: Mapping[Any, tuple[Any, Any]],
    ) -> SpatialScaleOPGDResult:
        """Fit scale-specific OPGD models to already prepared scale datasets.

        Each mapping value is ``(response, continuous_factor_frame)``. pyGeoHet
        does not silently aggregate coordinates, rasters, or polygons; spatial
        support preparation remains an explicit upstream operation.
        """

        if len(data_by_scale) < 2:
            raise InvalidDataError("at least two spatial scales are required")

        opgd_results: dict[float, OPGDResult] = {}
        failures: dict[float, str] = {}
        frames: dict[float, pd.DataFrame] = {}
        source_order: dict[float, int] = {}

        for order, (raw_scale, data) in enumerate(data_by_scale.items()):
            scale = _coerce_scale(raw_scale)
            if scale in source_order:
                raise InvalidDataError(
                    "spatial scales must be unique after numeric coercion"
                )
            source_order[scale] = order
            if not isinstance(data, tuple) or len(data) != 2:
                failures[scale] = (
                    "each scale value must be a (response, continuous_factors) tuple"
                )
                continue
            response, factors = data
            try:
                result = OPGD(**self.opgd_kwargs).fit(response, factors)
            except (InvalidDataError, TypeError, ValueError) as exc:
                failures[scale] = str(exc)
                continue
            opgd_results[scale] = result
            frames[scale] = result.detector.factor.to_frame()

        scale_effects = _compare_frames(
            frames,
            failures=failures,
            source_order=source_order,
            score_method=self.score_method,
            quantile=self.quantile,
            significant_only=self.significant_only,
            alpha=self.scale_alpha,
            tie_break=self.tie_break,
            score_tolerance=self.score_tolerance,
        )
        return SpatialScaleOPGDResult(
            scale_effects=scale_effects,
            opgd_results=opgd_results,
            failures=failures,
        )
