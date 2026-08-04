"""Bivariate multiscale discretization for GeoDetector-style q maximization."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from itertools import product
from math import comb, prod
from types import MappingProxyType
from typing import Any

import numpy as np
import pandas as pd

from pygeohet.core.qstat import q_statistic
from pygeohet.exceptions import InvalidDataError
from pygeohet.results import QStatisticResult
from pygeohet.stratification.optimal import _prepare_joint_numeric
from pygeohet.stratification.results import StratificationResult
from pygeohet.validation import MissingPolicy

MSD_TIE_RULE = (
    "minimum within-stratum sum of squares (maximum q); objective values within "
    "q_tolerance are tied; then choose the lexicographically smallest cut-point tuple"
)


@dataclass(frozen=True)
class MSDScaleResult:
    """One auditable coarse or refined search step in MSD."""

    scale: int
    candidate_codes: tuple[int, ...]
    candidate_cut_points: tuple[float, ...]
    selected_codes: tuple[int, ...]
    selected_cut_points: tuple[float, ...]
    q: float | None
    within_ss: float | None
    raw_combinations: int
    accepted: bool
    rejection_reason: str | None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_series(self) -> pd.Series:
        """Return scalar audit fields for this scale."""

        return pd.Series(
            {
                "scale": self.scale,
                "candidate_count": len(self.candidate_codes),
                "raw_combinations": self.raw_combinations,
                "selected_codes": self.selected_codes,
                "selected_cut_points": self.selected_cut_points,
                "q": self.q,
                "within_ss": self.within_ss,
                "accepted": self.accepted,
                "rejection_reason": self.rejection_reason,
            }
        )


@dataclass(frozen=True)
class MSDResult:
    """Final supervised stratification plus the complete multiscale search path."""

    stratification: StratificationResult
    q_result: QStatisticResult
    steps: tuple[MSDScaleResult, ...]
    n_strata: int
    upscale: int
    buffer_scales: tuple[int, ...]
    epsilon: int
    origin: float
    base_resolution: float
    tie_rule: str
    q_tolerance: float

    def steps_frame(self) -> pd.DataFrame:
        """Return one row per coarse or refinement scale."""

        return pd.DataFrame([step.to_series() for step in self.steps])

    def summary(self) -> str:
        """Return a compact terminal-friendly summary."""

        return (
            "MSDResult("
            f"strata={self.n_strata}, q={self.q_result.q:.6g}, "
            f"cuts={self.stratification.cut_points!r}, "
            f"scales={(self.upscale, *self.buffer_scales)!r})"
        )


def _validate_scales(
    upscale: int,
    buffer_scales: Sequence[int] | None,
) -> tuple[int, tuple[int, ...]]:
    if isinstance(upscale, bool) or not isinstance(upscale, (int, np.integer)):
        raise ValueError("upscale must be an integer")
    coarse = int(upscale)
    if coarse < 1:
        raise ValueError("upscale must be at least 1")

    if buffer_scales is None:
        buffers: tuple[int, ...] = ()
    else:
        parsed: list[int] = []
        for value in buffer_scales:
            if isinstance(value, bool) or not isinstance(value, (int, np.integer)):
                raise ValueError("buffer_scales must contain integers")
            parsed.append(int(value))
        buffers = tuple(parsed)

    if coarse == 1:
        if buffers:
            raise ValueError("buffer_scales must be empty when upscale is 1")
        return coarse, buffers
    if not buffers:
        raise ValueError("buffer_scales are required when upscale is greater than 1")
    previous = coarse
    for scale in buffers:
        if scale < 1 or scale >= previous:
            raise ValueError("buffer_scales must be positive and strictly decreasing")
        previous = scale
    if buffers[-1] != 1:
        raise ValueError("buffer_scales must end at the original scale 1")
    return coarse, buffers


def _infer_resolution(unique_x: np.ndarray) -> float:
    differences = np.diff(unique_x)
    positive = differences[differences > 0.0]
    if positive.size == 0:
        raise InvalidDataError("x must contain at least two distinct values")
    resolution = float(np.min(positive))
    if not np.isfinite(resolution) or resolution <= 0.0:
        raise InvalidDataError("could not infer a positive base resolution from x")
    return resolution


def _grid_codes(
    x_sorted: np.ndarray,
    *,
    origin: float,
    base_resolution: float,
    scale: int,
) -> np.ndarray:
    width = base_resolution * float(scale)
    adjusted = (x_sorted - origin) / width
    tolerance = np.finfo(float).eps * np.maximum(1.0, np.abs(adjusted)) * 8.0
    return np.floor(adjusted + tolerance).astype(np.int64)


def _candidate_positions(
    x_sorted: np.ndarray,
    codes: np.ndarray,
) -> tuple[dict[int, int], dict[int, float]]:
    first_positions: dict[int, int] = {}
    cut_values: dict[int, float] = {}
    for index in range(1, len(codes)):
        if codes[index] != codes[index - 1]:
            code = int(codes[index])
            first_positions[code] = index
            cut_values[code] = float(x_sorted[index])
    return first_positions, cut_values


def _prefix_sums(y_sorted: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    prefix = np.concatenate(([0.0], np.cumsum(y_sorted, dtype=float)))
    prefix_sq = np.concatenate(([0.0], np.cumsum(y_sorted * y_sorted, dtype=float)))
    return prefix, prefix_sq


def _interval_sse(
    start: int,
    stop: int,
    prefix: np.ndarray,
    prefix_sq: np.ndarray,
) -> float:
    count = stop - start
    if count <= 0:
        return float("inf")
    total = float(prefix[stop] - prefix[start])
    total_sq = float(prefix_sq[stop] - prefix_sq[start])
    return max(total_sq - total * total / count, 0.0)


def _best_partition(
    y_sorted: np.ndarray,
    allowed_positions: Sequence[int],
    *,
    n_strata: int,
    min_stratum_size: int,
    objective_tolerance: float,
) -> tuple[tuple[int, ...], float] | None:
    n = len(y_sorted)
    nodes = (0, *tuple(sorted(set(int(value) for value in allowed_positions))), n)
    prefix, prefix_sq = _prefix_sums(y_sorted)

    previous: dict[int, tuple[float, tuple[int, ...]]] = {0: (0.0, ())}
    for class_number in range(1, n_strata + 1):
        current: dict[int, tuple[float, tuple[int, ...]]] = {}
        for end_node in range(1, len(nodes)):
            end = nodes[end_node]
            if class_number < n_strata and end == n:
                continue
            if class_number == n_strata and end != n:
                continue
            best: tuple[float, tuple[int, ...]] | None = None
            for start_node, (prior_ss, prior_cuts) in previous.items():
                start = nodes[start_node]
                if start >= end or end - start < min_stratum_size:
                    continue
                remaining_classes = n_strata - class_number
                if n - end < remaining_classes * min_stratum_size:
                    continue
                candidate_ss = prior_ss + _interval_sse(
                    start,
                    end,
                    prefix,
                    prefix_sq,
                )
                candidate_cuts = prior_cuts if end == n else (*prior_cuts, end)
                if best is None or candidate_ss < best[0] - objective_tolerance:
                    best = (candidate_ss, candidate_cuts)
                elif abs(candidate_ss - best[0]) <= objective_tolerance:
                    if candidate_cuts < best[1]:
                        best = (candidate_ss, candidate_cuts)
            if best is not None:
                current[end_node] = best
        previous = current

    result = previous.get(len(nodes) - 1)
    if result is None:
        return None
    within_ss, cuts = result
    return cuts, within_ss


def _best_grouped_partition(
    y_sorted: np.ndarray,
    position_groups: Sequence[Sequence[int]],
    *,
    min_stratum_size: int,
    objective_tolerance: float,
) -> tuple[tuple[int, ...], float] | None:
    n = len(y_sorted)
    prefix, prefix_sq = _prefix_sums(y_sorted)
    best: tuple[float, tuple[int, ...]] | None = None
    for raw_cuts in product(*position_groups):
        cuts = tuple(int(value) for value in raw_cuts)
        if tuple(sorted(cuts)) != cuts or len(set(cuts)) != len(cuts):
            continue
        boundaries = (0, *cuts, n)
        if any(
            stop - start < min_stratum_size
            for start, stop in zip(boundaries[:-1], boundaries[1:])
        ):
            continue
        within_ss = sum(
            _interval_sse(start, stop, prefix, prefix_sq)
            for start, stop in zip(boundaries[:-1], boundaries[1:])
        )
        if best is None or within_ss < best[0] - objective_tolerance:
            best = (within_ss, cuts)
        elif abs(within_ss - best[0]) <= objective_tolerance and cuts < best[1]:
            best = (within_ss, cuts)
    if best is None:
        return None
    return best[1], best[0]


def _labels_from_cuts(x: np.ndarray, cut_points: tuple[float, ...]) -> np.ndarray:
    return np.searchsorted(np.asarray(cut_points), x, side="right") + 1


def _raw_combination_count(candidate_count: int, n_strata: int) -> int:
    cut_count = n_strata - 1
    return comb(candidate_count, cut_count) if candidate_count >= cut_count else 0


def multiscale_discretize(
    y: Any,
    x: Any,
    *,
    n_strata: int,
    upscale: int = 1,
    buffer_scales: Sequence[int] | None = None,
    epsilon: int = 1,
    base_resolution: float | None = None,
    origin: float | None = None,
    missing: MissingPolicy = "drop",
    min_stratum_size: int = 2,
    q_tolerance: float = 1e-12,
) -> MSDResult:
    """Find a q-maximizing supervised discretization through MSD refinement.

    ``scale=1`` is the original value grid. A larger ``upscale`` first searches
    coarser bins; each subsequent buffer scale chooses one cut from each mapped
    epsilon neighbourhood. Set ``upscale=1`` for an exact global search over all
    observed unique-value boundaries.
    """

    if isinstance(n_strata, bool) or not isinstance(n_strata, (int, np.integer)):
        raise ValueError("n_strata must be an integer")
    classes = int(n_strata)
    if classes < 2:
        raise ValueError("n_strata must be at least 2")
    if classes > 10:
        raise ValueError("n_strata must not exceed the paper's practical limit of 10")
    if isinstance(epsilon, bool) or not isinstance(epsilon, (int, np.integer)):
        raise ValueError("epsilon must be an integer")
    neighbourhood = int(epsilon)
    if neighbourhood < 0:
        raise ValueError("epsilon must be nonnegative")
    if min_stratum_size < 1:
        raise ValueError("min_stratum_size must be at least 1")
    if q_tolerance < 0.0:
        raise ValueError("q_tolerance must be nonnegative")

    coarse_scale, buffers = _validate_scales(upscale, buffer_scales)
    y_clean, x_clean, keep_mask, dropped_count = _prepare_joint_numeric(
        y,
        x,
        missing=missing,
    )
    order = np.argsort(x_clean, kind="mergesort")
    x_sorted = x_clean[order]
    y_sorted = y_clean[order]
    unique_x = np.unique(x_sorted)
    if unique_x.size < classes:
        raise InvalidDataError("x must contain at least n_strata distinct values")
    if len(y_clean) < classes * min_stratum_size:
        raise InvalidDataError(
            "not enough complete observations for n_strata and min_stratum_size"
        )

    resolved_origin = float(unique_x[0] if origin is None else origin)
    if not np.isfinite(resolved_origin):
        raise ValueError("origin must be finite")
    resolved_resolution = (
        _infer_resolution(unique_x)
        if base_resolution is None
        else float(base_resolution)
    )
    if not np.isfinite(resolved_resolution) or resolved_resolution <= 0.0:
        raise ValueError("base_resolution must be positive and finite")

    centered = y_sorted - float(np.mean(y_sorted))
    total_ss = float(np.dot(centered, centered))
    if total_ss <= np.finfo(float).eps * max(
        1.0,
        float(np.dot(y_sorted, y_sorted)),
    ):
        q_statistic(y_sorted, np.ones_like(y_sorted, dtype=int))

    scales = (coarse_scale, *buffers)
    steps: list[MSDScaleResult] = []
    selected_codes: tuple[int, ...] | None = None
    previous_scale: int | None = None

    for scale_index, scale in enumerate(scales):
        codes = _grid_codes(
            x_sorted,
            origin=resolved_origin,
            base_resolution=resolved_resolution,
            scale=scale,
        )
        position_by_code, value_by_code = _candidate_positions(x_sorted, codes)
        all_codes = tuple(sorted(position_by_code))
        candidate_groups: tuple[tuple[int, ...], ...] | None = None

        if scale_index == 0 or selected_codes is None or previous_scale is None:
            candidate_codes = all_codes
            source = "all coarse-scale boundaries"
            candidate_positions = tuple(
                position_by_code[code] for code in candidate_codes
            )
            raw_combinations = _raw_combination_count(
                len(candidate_codes),
                classes,
            )
            solution = _best_partition(
                y_sorted,
                candidate_positions,
                n_strata=classes,
                min_stratum_size=min_stratum_size,
                objective_tolerance=q_tolerance * max(total_ss, 1.0),
            )
        else:
            groups: list[tuple[int, ...]] = []
            for code in selected_codes:
                low = int(
                    np.ceil(previous_scale * (code - neighbourhood) / scale)
                )
                high = int(
                    np.floor(previous_scale * (code + neighbourhood) / scale)
                )
                groups.append(
                    tuple(
                        candidate
                        for candidate in all_codes
                        if low <= candidate <= high
                    )
                )
            candidate_groups = tuple(groups)
            candidate_codes = tuple(
                sorted({code for group in candidate_groups for code in group})
            )
            source = "one cut selected from each mapped epsilon neighbourhood"
            position_groups = tuple(
                tuple(position_by_code[code] for code in group)
                for group in candidate_groups
            )
            raw_combinations = (
                prod(len(group) for group in candidate_groups)
                if all(candidate_groups)
                else 0
            )
            solution = _best_grouped_partition(
                y_sorted,
                position_groups,
                min_stratum_size=min_stratum_size,
                objective_tolerance=q_tolerance * max(total_ss, 1.0),
            )

        if solution is None:
            reason = (
                f"no valid {classes}-stratum partition at scale {scale} under "
                f"min_stratum_size={min_stratum_size}"
            )
            steps.append(
                MSDScaleResult(
                    scale=scale,
                    candidate_codes=candidate_codes,
                    candidate_cut_points=tuple(
                        value_by_code[code] for code in candidate_codes
                    ),
                    selected_codes=(),
                    selected_cut_points=(),
                    q=None,
                    within_ss=None,
                    raw_combinations=raw_combinations,
                    accepted=False,
                    rejection_reason=reason,
                    metadata={
                        "candidate_source": source,
                        "candidate_groups": candidate_groups,
                    },
                )
            )
            raise InvalidDataError(reason)

        cut_positions, within_ss = solution
        code_by_position = {
            position: code for code, position in position_by_code.items()
        }
        selected_codes = tuple(
            code_by_position[position] for position in cut_positions
        )
        selected_cut_points = tuple(
            float(x_sorted[position]) for position in cut_positions
        )
        q_value = min(max(1.0 - within_ss / total_ss, 0.0), 1.0)
        steps.append(
            MSDScaleResult(
                scale=scale,
                candidate_codes=candidate_codes,
                candidate_cut_points=tuple(
                    value_by_code[code] for code in candidate_codes
                ),
                selected_codes=selected_codes,
                selected_cut_points=selected_cut_points,
                q=q_value,
                within_ss=within_ss,
                raw_combinations=raw_combinations,
                accepted=True,
                rejection_reason=None,
                metadata={
                    "candidate_source": source,
                    "candidate_groups": candidate_groups,
                },
            )
        )
        previous_scale = scale

    if selected_codes is None or not steps:
        raise InvalidDataError("MSD did not produce a valid stratification")

    final_cut_points = steps[-1].selected_cut_points
    clean_labels = _labels_from_cuts(x_clean, final_cut_points)
    q_result = q_statistic(
        y_clean,
        clean_labels,
        missing="raise",
        min_stratum_size=min_stratum_size,
    )

    clean_label_iterator = iter(int(value) for value in clean_labels)
    expanded_labels = tuple(
        next(clean_label_iterator) if keep else None for keep in keep_mask
    )
    counts_series = pd.Series(clean_labels, dtype=int).value_counts(sort=False)
    counts = {int(label): int(count) for label, count in counts_series.items()}
    stratification = StratificationResult(
        method="multiscale_discretization",
        labels=expanded_labels,
        cut_points=final_cut_points,
        requested_strata=classes,
        actual_strata=len(counts),
        counts=counts,
        n_observations=int(len(y_clean)),
        dropped_count=dropped_count,
        duplicate_cut_points=0,
        collapsed_strata=max(classes - len(counts), 0),
        min_stratum_size=min_stratum_size,
        rejected=False,
        rejection_reason=None,
        supervised=True,
        metadata={
            "upscale": coarse_scale,
            "buffer_scales": buffers,
            "epsilon": neighbourhood,
            "origin": resolved_origin,
            "base_resolution": resolved_resolution,
            "cut_point_membership": "latter_class",
        },
    )
    return MSDResult(
        stratification=stratification,
        q_result=q_result,
        steps=tuple(steps),
        n_strata=classes,
        upscale=coarse_scale,
        buffer_scales=buffers,
        epsilon=neighbourhood,
        origin=resolved_origin,
        base_resolution=resolved_resolution,
        tie_rule=MSD_TIE_RULE,
        q_tolerance=float(q_tolerance),
    )


class MSD:
    """Estimator-style wrapper for :func:`multiscale_discretize`."""

    def __init__(
        self,
        *,
        n_strata: int,
        upscale: int = 1,
        buffer_scales: Sequence[int] | None = None,
        epsilon: int = 1,
        base_resolution: float | None = None,
        origin: float | None = None,
        missing: MissingPolicy = "drop",
        min_stratum_size: int = 2,
        q_tolerance: float = 1e-12,
    ) -> None:
        self.n_strata = n_strata
        self.upscale = upscale
        self.buffer_scales = buffer_scales
        self.epsilon = epsilon
        self.base_resolution = base_resolution
        self.origin = origin
        self.missing = missing
        self.min_stratum_size = min_stratum_size
        self.q_tolerance = q_tolerance

    def fit(self, y: Any, x: Any) -> MSDResult:
        """Fit MSD to one response and one continuous explanatory variable."""

        return multiscale_discretize(
            y,
            x,
            n_strata=self.n_strata,
            upscale=self.upscale,
            buffer_scales=self.buffer_scales,
            epsilon=self.epsilon,
            base_resolution=self.base_resolution,
            origin=self.origin,
            missing=self.missing,
            min_stratum_size=self.min_stratum_size,
            q_tolerance=self.q_tolerance,
        )
