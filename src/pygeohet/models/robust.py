"""Robust geographical and interaction detector workflows."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Literal

import numpy as np
import pandas as pd

from pygeohet.core.qstat import q_statistic
from pygeohet.exceptions import InvalidDataError, MissingDataError
from pygeohet.models.geodetector import GeoDetector
from pygeohet.results import (
    GeoDetectorResult,
    InteractionDetectorResult,
    QStatisticResult,
)
from pygeohet.validation import MissingPolicy, coerce_factor_frame

RobustSelection = Literal["marginal_gain", "max_b"]
ROBUST_TIE_RULE = (
    "minimum within-stratum sum of squares (maximum B); objective values within "
    "b_tolerance are tied; then choose the lexicographically smallest cut tuple"
)


@dataclass(frozen=True)
class RobustDiscretizationResult:
    """One exact variance-change-point discretization and its B-value."""

    labels: tuple[int | None, ...]
    cut_points: tuple[float, ...]
    break_positions: tuple[int, ...]
    n_strata: int
    counts: Mapping[int, int]
    q_result: QStatisticResult
    n_observations: int
    dropped_count: int
    min_stratum_size: int
    duplicate_x_count: int
    tie_rule: str = ROBUST_TIE_RULE
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "counts", MappingProxyType(dict(self.counts)))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def b_value(self) -> float:
        """Return the RGD B-value, numerically equal to q on robust zones."""

        return self.q_result.q

    def labels_array(self, *, missing_value: float = np.nan) -> np.ndarray:
        """Return aligned labels, replacing dropped rows with ``missing_value``."""

        return np.asarray(
            [missing_value if value is None else value for value in self.labels],
            dtype=float,
        )

    def to_series(self) -> pd.Series:
        """Return scalar audit fields."""

        return pd.Series(
            {
                "n_strata": self.n_strata,
                "b_value": self.b_value,
                "p_value": self.q_result.p_value,
                "within_ss": self.q_result.within_ss,
                "total_ss": self.q_result.total_ss,
                "cut_points": self.cut_points,
                "break_positions": self.break_positions,
                "minimum_count": min(self.counts.values(), default=0),
                "n_observations": self.n_observations,
                "dropped_count": self.dropped_count,
                "duplicate_x_count": self.duplicate_x_count,
            }
        )

    def summary(self) -> str:
        """Return a compact terminal-friendly summary."""

        return (
            "RobustDiscretizationResult("
            f"strata={self.n_strata}, B={self.b_value:.6g}, "
            f"cuts={self.cut_points!r}, counts={dict(self.counts)!r})"
        )


@dataclass(frozen=True)
class RobustCandidateResult:
    """One requested class count in a robust discretization search."""

    n_strata: int
    result: RobustDiscretizationResult | None
    accepted: bool
    rejection_reason: str | None
    gain: float | None = None
    relative_gain: float | None = None

    def to_series(self) -> pd.Series:
        """Return one candidate row."""

        result = self.result
        return pd.Series(
            {
                "n_strata": self.n_strata,
                "accepted": self.accepted,
                "rejection_reason": self.rejection_reason,
                "b_value": None if result is None else result.b_value,
                "p_value": None if result is None else result.q_result.p_value,
                "within_ss": None if result is None else result.q_result.within_ss,
                "cut_points": None if result is None else result.cut_points,
                "minimum_count": (
                    None if result is None else min(result.counts.values(), default=0)
                ),
                "gain": self.gain,
                "relative_gain": self.relative_gain,
            }
        )


@dataclass(frozen=True)
class RobustOptimizationResult:
    """Complete class-count search and selected robust discretization."""

    candidates: tuple[RobustCandidateResult, ...]
    best: RobustCandidateResult
    selection: RobustSelection
    increase_rate: float
    b_tolerance: float

    def candidates_frame(self) -> pd.DataFrame:
        """Return every attempted class count, including rejected candidates."""

        return pd.DataFrame([candidate.to_series() for candidate in self.candidates])

    def best_series(self) -> pd.Series:
        """Return the selected candidate."""

        return self.best.to_series()

    def summary(self) -> str:
        """Return a compact optimization summary."""

        assert self.best.result is not None
        return (
            "RobustOptimizationResult("
            f"selection={self.selection!r}, strata={self.best.n_strata}, "
            f"B={self.best.result.b_value:.6g}, attempted={len(self.candidates)})"
        )


@dataclass(frozen=True)
class RGDResult:
    """Robust discretizations and integrated detector results."""

    optimizations: Mapping[str, RobustOptimizationResult]
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
        """Return one selected robust discretization per factor."""

        rows: list[dict[str, Any]] = []
        for factor, optimization in self.optimizations.items():
            row = optimization.best_series().to_dict()
            row["factor"] = factor
            rows.append(row)
        if not rows:
            return pd.DataFrame()
        frame = pd.DataFrame(rows)
        return frame.loc[:, ["factor", *[c for c in frame.columns if c != "factor"]]]

    def candidates_frame(self, factor: str | None = None) -> pd.DataFrame:
        """Return class-count audits for one or all factors."""

        if factor is not None:
            try:
                frame = self.optimizations[factor].candidates_frame()
            except KeyError as exc:
                raise KeyError(factor) from exc
            frame.insert(0, "factor", factor)
            return frame

        frames: list[pd.DataFrame] = []
        for name, optimization in self.optimizations.items():
            frame = optimization.candidates_frame()
            frame.insert(0, "factor", name)
            frames.append(frame)
        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

    def discretized_frame(self) -> pd.DataFrame:
        """Return robust labels aligned to the original rows."""

        return pd.DataFrame(dict(self.discrete_labels), dtype=object)

    def summary(self) -> str:
        """Return robust choices followed by the classical workflow summary."""

        return "\n".join(
            [
                "Robust discretization",
                self.optimal_frame().to_string(index=False),
                "",
                self.detector.summary(),
            ]
        )


@dataclass(frozen=True)
class RIDResult:
    """Robust factor optimization plus pairwise interaction results."""

    rgd: RGDResult
    interaction: InteractionDetectorResult

    def summary(self) -> str:
        """Return robust factor choices and interaction comparisons."""

        return "\n".join(
            [
                self.rgd.optimal_frame().to_string(index=False),
                "",
                self.interaction.summary(),
            ]
        )


def _prepare_numeric_pair(
    y: Any,
    x: Any,
    *,
    missing: MissingPolicy,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, int]:
    if missing not in {"drop", "raise"}:
        raise ValueError("missing must be either 'drop' or 'raise'")

    y_series = pd.Series(y, copy=False, name="y").reset_index(drop=True)
    x_series = pd.Series(x, copy=False, name="x").reset_index(drop=True)
    if y_series.ndim != 1 or x_series.ndim != 1:
        raise InvalidDataError("y and x must be one-dimensional")
    if len(y_series) != len(x_series):
        raise InvalidDataError("y and x must have equal length")
    if len(y_series) == 0:
        raise InvalidDataError("y and x must not be empty")

    y_numeric = pd.to_numeric(y_series, errors="raise").astype(float)
    x_numeric = pd.to_numeric(x_series, errors="raise").astype(float)
    missing_mask = y_numeric.isna() | x_numeric.isna()
    if missing == "raise" and bool(missing_mask.any()):
        raise MissingDataError("missing values are present in y or x")

    keep = ~missing_mask
    y_clean = y_numeric.loc[keep].to_numpy(dtype=float, copy=True)
    x_clean = x_numeric.loc[keep].to_numpy(dtype=float, copy=True)
    if y_clean.size == 0:
        raise InvalidDataError("no complete observations remain")
    if not bool(np.isfinite(y_clean).all()):
        raise InvalidDataError("y must contain only finite values")
    if not bool(np.isfinite(x_clean).all()):
        raise InvalidDataError("x must contain only finite values")
    return y_clean, x_clean, keep.to_numpy(dtype=bool), int(missing_mask.sum())


def _prefix_sums(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    return (
        np.concatenate(([0.0], np.cumsum(values, dtype=float))),
        np.concatenate(([0.0], np.cumsum(values * values, dtype=float))),
    )


def _interval_sse(
    start: int,
    stop: int,
    prefix: np.ndarray,
    prefix_sq: np.ndarray,
) -> float:
    count = stop - start
    total = float(prefix[stop] - prefix[start])
    total_sq = float(prefix_sq[stop] - prefix_sq[start])
    return max(total_sq - total * total / count, 0.0)


def _optimal_partition(
    y_sorted: np.ndarray,
    candidate_positions: tuple[int, ...],
    *,
    n_strata: int,
    min_stratum_size: int,
    objective_tolerance: float,
) -> tuple[tuple[int, ...], float] | None:
    """Return exact minimum-SSE ordered partition by dynamic programming."""

    n = len(y_sorted)
    nodes = (0, *candidate_positions, n)
    prefix, prefix_sq = _prefix_sums(y_sorted)
    previous: dict[int, tuple[float, tuple[int, ...]]] = {0: (0.0, ())}

    for segment_number in range(1, n_strata + 1):
        current: dict[int, tuple[float, tuple[int, ...]]] = {}
        for end_node in range(1, len(nodes)):
            end = nodes[end_node]
            if segment_number < n_strata and end == n:
                continue
            if segment_number == n_strata and end != n:
                continue

            best: tuple[float, tuple[int, ...]] | None = None
            for start_node, (prior_cost, prior_cuts) in previous.items():
                start = nodes[start_node]
                if start >= end or end - start < min_stratum_size:
                    continue
                remaining = n_strata - segment_number
                if n - end < remaining * min_stratum_size:
                    continue
                cost = prior_cost + _interval_sse(start, end, prefix, prefix_sq)
                cuts = prior_cuts if end == n else (*prior_cuts, end)
                if best is None or cost < best[0] - objective_tolerance:
                    best = (cost, cuts)
                elif abs(cost - best[0]) <= objective_tolerance and cuts < best[1]:
                    best = (cost, cuts)
            if best is not None:
                current[end_node] = best
        previous = current

    result = previous.get(len(nodes) - 1)
    if result is None:
        return None
    return result[1], result[0]


def robust_discretize(
    y: Any,
    x: Any,
    *,
    n_strata: int,
    missing: MissingPolicy = "drop",
    min_stratum_size: int = 2,
    b_tolerance: float = 1e-12,
) -> RobustDiscretizationResult:
    """Find exact RGD change points by minimizing ordered within-segment SSE.

    The response is stably sorted by the explanatory variable. Candidate breaks
    are restricted to boundaries between distinct explanatory values, so equal
    values are never split across robust zones.
    """

    if isinstance(n_strata, bool) or not isinstance(n_strata, (int, np.integer)):
        raise ValueError("n_strata must be an integer")
    classes = int(n_strata)
    if classes < 2:
        raise ValueError("n_strata must be at least 2")
    if isinstance(min_stratum_size, bool) or not isinstance(
        min_stratum_size, (int, np.integer)
    ):
        raise ValueError("min_stratum_size must be an integer")
    minimum = int(min_stratum_size)
    if minimum < 1:
        raise ValueError("min_stratum_size must be at least 1")
    if b_tolerance < 0.0:
        raise ValueError("b_tolerance must be nonnegative")

    y_clean, x_clean, keep_mask, dropped_count = _prepare_numeric_pair(
        y,
        x,
        missing=missing,
    )
    if len(y_clean) < classes * minimum:
        raise InvalidDataError(
            "not enough complete observations for n_strata and min_stratum_size"
        )

    order = np.argsort(x_clean, kind="mergesort")
    x_sorted = x_clean[order]
    y_sorted = y_clean[order]
    candidate_positions = tuple(
        int(index)
        for index in range(1, len(x_sorted))
        if x_sorted[index - 1] < x_sorted[index]
    )
    if len(candidate_positions) < classes - 1:
        raise InvalidDataError("x does not contain enough distinct break boundaries")

    centered = y_sorted - float(np.mean(y_sorted))
    total_ss = float(np.dot(centered, centered))
    scale = max(1.0, float(np.dot(y_sorted, y_sorted)))
    objective_tolerance = b_tolerance * max(total_ss, scale)
    solution = _optimal_partition(
        y_sorted,
        candidate_positions,
        n_strata=classes,
        min_stratum_size=minimum,
        objective_tolerance=objective_tolerance,
    )
    if solution is None:
        raise InvalidDataError(
            "no valid robust partition satisfies the requested class count and size"
        )

    break_positions, within_ss = solution
    cut_points = tuple(float(x_sorted[position]) for position in break_positions)
    labels_clean = np.searchsorted(
        np.asarray(cut_points, dtype=float),
        x_clean,
        side="right",
    ) + 1
    q_result = q_statistic(
        y_clean,
        labels_clean,
        missing="raise",
        min_stratum_size=minimum,
    )

    labels_full: list[int | None] = []
    clean_index = 0
    for keep in keep_mask:
        if keep:
            labels_full.append(int(labels_clean[clean_index]))
            clean_index += 1
        else:
            labels_full.append(None)
    counts_series = pd.Series(labels_clean).value_counts(sort=False)
    counts = {int(label): int(count) for label, count in counts_series.items()}

    return RobustDiscretizationResult(
        labels=tuple(labels_full),
        cut_points=cut_points,
        break_positions=break_positions,
        n_strata=classes,
        counts=counts,
        q_result=q_result,
        n_observations=len(y_clean),
        dropped_count=dropped_count,
        min_stratum_size=minimum,
        duplicate_x_count=int(len(x_clean) - len(np.unique(x_clean))),
        metadata={
            "ordering": "stable ascending x",
            "candidate_boundaries": len(candidate_positions),
            "rank_equivalence": True,
            "within_ss_from_dynamic_programming": within_ss,
            "equal_x_split": False,
        },
    )


def optimize_robust_discretization(
    y: Any,
    x: Any,
    *,
    n_strata: Iterable[int] = range(3, 9),
    selection: RobustSelection = "marginal_gain",
    increase_rate: float = 0.05,
    missing: MissingPolicy = "drop",
    min_stratum_size: int = 2,
    b_tolerance: float = 1e-12,
) -> RobustOptimizationResult:
    """Evaluate class counts and select a robust discretization."""

    if selection not in {"marginal_gain", "max_b"}:
        raise ValueError("selection must be 'marginal_gain' or 'max_b'")
    if increase_rate < 0.0:
        raise ValueError("increase_rate must be nonnegative")

    parsed: list[int] = []
    for value in n_strata:
        if isinstance(value, bool) or not isinstance(value, (int, np.integer)):
            raise ValueError("n_strata must contain integers")
        parsed.append(int(value))
    class_counts = tuple(sorted(set(parsed)))
    if not class_counts:
        raise ValueError("n_strata must contain at least one class count")

    provisional: list[RobustCandidateResult] = []
    accepted_results: list[tuple[int, RobustDiscretizationResult]] = []
    for classes in class_counts:
        try:
            result = robust_discretize(
                y,
                x,
                n_strata=classes,
                missing=missing,
                min_stratum_size=min_stratum_size,
                b_tolerance=b_tolerance,
            )
        except (InvalidDataError, ValueError) as exc:
            provisional.append(
                RobustCandidateResult(
                    n_strata=classes,
                    result=None,
                    accepted=False,
                    rejection_reason=str(exc),
                )
            )
        else:
            accepted_results.append((classes, result))
            provisional.append(
                RobustCandidateResult(
                    n_strata=classes,
                    result=result,
                    accepted=True,
                    rejection_reason=None,
                )
            )

    if not accepted_results:
        reasons = sorted(
            {
                candidate.rejection_reason
                for candidate in provisional
                if candidate.rejection_reason is not None
            }
        )
        raise InvalidDataError(
            "no robust discretization candidate was accepted: " + "; ".join(reasons)
        )

    gain_by_count: dict[int, tuple[float | None, float | None]] = {}
    previous: RobustDiscretizationResult | None = None
    for classes, result in accepted_results:
        if previous is None:
            gain_by_count[classes] = (None, None)
        else:
            gain = result.b_value - previous.b_value
            if abs(previous.b_value) <= b_tolerance:
                relative_gain = 0.0 if abs(gain) <= b_tolerance else float("inf")
            else:
                relative_gain = gain / abs(previous.b_value)
            gain_by_count[classes] = (float(gain), float(relative_gain))
        previous = result

    candidates = tuple(
        RobustCandidateResult(
            n_strata=candidate.n_strata,
            result=candidate.result,
            accepted=candidate.accepted,
            rejection_reason=candidate.rejection_reason,
            gain=gain_by_count.get(candidate.n_strata, (None, None))[0],
            relative_gain=gain_by_count.get(candidate.n_strata, (None, None))[1],
        )
        for candidate in provisional
    )
    accepted = [candidate for candidate in candidates if candidate.accepted]

    if selection == "max_b":
        best_b = max(
            candidate.result.b_value
            for candidate in accepted
            if candidate.result is not None
        )
        best = min(
            (
                candidate
                for candidate in accepted
                if candidate.result is not None
                and candidate.result.b_value >= best_b - b_tolerance
            ),
            key=lambda candidate: candidate.n_strata,
        )
    else:
        best = accepted[-1]
        for candidate in accepted[1:]:
            rate = candidate.relative_gain
            if rate is not None and rate <= increase_rate + b_tolerance:
                best = candidate
                break

    return RobustOptimizationResult(
        candidates=candidates,
        best=best,
        selection=selection,
        increase_rate=float(increase_rate),
        b_tolerance=float(b_tolerance),
    )


class RGD:
    """Optimize variance-change-point strata before running GeoDetector."""

    def __init__(
        self,
        *,
        n_strata: Iterable[int] = range(3, 9),
        selection: RobustSelection = "marginal_gain",
        increase_rate: float = 0.05,
        alpha: float = 0.05,
        missing: MissingPolicy = "drop",
        min_stratum_size: int = 2,
        min_overlay_size: int = 1,
        b_tolerance: float = 1e-12,
    ) -> None:
        self.n_strata = tuple(n_strata)
        self.selection = selection
        self.increase_rate = increase_rate
        self.alpha = alpha
        self.missing = missing
        self.min_stratum_size = min_stratum_size
        self.min_overlay_size = min_overlay_size
        self.b_tolerance = b_tolerance

    def fit(self, y: Any, continuous_factors: Any) -> RGDResult:
        """Robustly discretize every continuous factor and run all detectors."""

        factor_frame = coerce_factor_frame(continuous_factors)
        if factor_frame.empty or factor_frame.shape[1] == 0:
            raise InvalidDataError("continuous_factors must contain at least one column")

        optimizations: dict[str, RobustOptimizationResult] = {}
        labels: dict[str, tuple[int | None, ...]] = {}
        for name in factor_frame.columns:
            optimization = optimize_robust_discretization(
                y,
                factor_frame[name],
                n_strata=self.n_strata,
                selection=self.selection,
                increase_rate=self.increase_rate,
                missing=self.missing,
                min_stratum_size=self.min_stratum_size,
                b_tolerance=self.b_tolerance,
            )
            assert optimization.best.result is not None
            optimizations[name] = optimization
            labels[name] = optimization.best.result.labels

        detector = GeoDetector(
            alpha=self.alpha,
            missing=self.missing,
            min_stratum_size=self.min_stratum_size,
            min_overlay_size=self.min_overlay_size,
        ).fit(y, pd.DataFrame(labels, dtype=object))
        return RGDResult(
            optimizations=optimizations,
            discrete_labels=labels,
            detector=detector,
        )


def rgd(
    y: Any,
    continuous_factors: Any,
    *,
    n_strata: Iterable[int] = range(3, 9),
    selection: RobustSelection = "marginal_gain",
    increase_rate: float = 0.05,
    alpha: float = 0.05,
    missing: MissingPolicy = "drop",
    min_stratum_size: int = 2,
    min_overlay_size: int = 1,
    b_tolerance: float = 1e-12,
) -> RGDResult:
    """Functional interface to :class:`RGD`."""

    return RGD(
        n_strata=n_strata,
        selection=selection,
        increase_rate=increase_rate,
        alpha=alpha,
        missing=missing,
        min_stratum_size=min_stratum_size,
        min_overlay_size=min_overlay_size,
        b_tolerance=b_tolerance,
    ).fit(y, continuous_factors)


class RID:
    """Run robust discretization and report pairwise interaction detection."""

    def __init__(
        self,
        *,
        n_strata: Iterable[int] = range(3, 9),
        selection: RobustSelection = "marginal_gain",
        increase_rate: float = 0.05,
        alpha: float = 0.05,
        missing: MissingPolicy = "drop",
        min_stratum_size: int = 2,
        min_overlay_size: int = 1,
        b_tolerance: float = 1e-12,
    ) -> None:
        self.rgd_model = RGD(
            n_strata=n_strata,
            selection=selection,
            increase_rate=increase_rate,
            alpha=alpha,
            missing=missing,
            min_stratum_size=min_stratum_size,
            min_overlay_size=min_overlay_size,
            b_tolerance=b_tolerance,
        )

    def fit(self, y: Any, continuous_factors: Any) -> RIDResult:
        """Fit RGD and expose its joint-sample pairwise interaction results."""

        factor_frame = coerce_factor_frame(continuous_factors)
        if factor_frame.shape[1] < 2:
            raise InvalidDataError("RID requires at least two explanatory factors")
        rgd_result = self.rgd_model.fit(y, factor_frame)
        interaction = rgd_result.detector.interaction
        if interaction is None:
            raise InvalidDataError("RID could not construct pairwise interactions")
        return RIDResult(rgd=rgd_result, interaction=interaction)


def rid(
    y: Any,
    continuous_factors: Any,
    *,
    n_strata: Iterable[int] = range(3, 9),
    selection: RobustSelection = "marginal_gain",
    increase_rate: float = 0.05,
    alpha: float = 0.05,
    missing: MissingPolicy = "drop",
    min_stratum_size: int = 2,
    min_overlay_size: int = 1,
    b_tolerance: float = 1e-12,
) -> RIDResult:
    """Functional interface to :class:`RID`."""

    return RID(
        n_strata=n_strata,
        selection=selection,
        increase_rate=increase_rate,
        alpha=alpha,
        missing=missing,
        min_stratum_size=min_stratum_size,
        min_overlay_size=min_overlay_size,
        b_tolerance=b_tolerance,
    ).fit(y, continuous_factors)
