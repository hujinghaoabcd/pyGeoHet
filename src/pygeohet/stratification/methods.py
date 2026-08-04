"""Deterministic univariate stratification methods."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np
import pandas as pd

from pygeohet.exceptions import InvalidDataError, MissingDataError
from pygeohet.stratification.results import StratificationResult
from pygeohet.validation import MissingPolicy

_METHOD_ALIASES: Mapping[str, str] = {
    "equal": "equal_interval",
    "equal_interval": "equal_interval",
    "quantile": "quantile",
    "natural": "natural_breaks",
    "natural_breaks": "natural_breaks",
    "jenks": "natural_breaks",
    "geometric": "geometric_interval",
    "geometric_interval": "geometric_interval",
    "sd": "standard_deviation",
    "standard_deviation": "standard_deviation",
    "headtails": "head_tail_breaks",
    "head_tail": "head_tail_breaks",
    "head_tail_breaks": "head_tail_breaks",
}


def canonical_method(method: str) -> str:
    """Return the canonical public name for a stratification method."""

    key = str(method).strip().lower().replace("-", "_").replace("/", "_")
    try:
        return _METHOD_ALIASES[key]
    except KeyError as exc:
        supported = ", ".join(sorted(set(_METHOD_ALIASES.values())))
        raise ValueError(
            f"unsupported stratification method {method!r}; {supported}"
        ) from exc


def _prepare_values(
    values: Any,
    *,
    missing: MissingPolicy,
) -> tuple[np.ndarray, np.ndarray, int, int]:
    if missing not in {"drop", "raise"}:
        raise ValueError("missing must be either 'drop' or 'raise'")

    series = pd.Series(values, copy=False, name="value").reset_index(drop=True)
    if series.ndim != 1:
        raise InvalidDataError("values must be one-dimensional")
    if len(series) == 0:
        raise InvalidDataError("values must not be empty")

    numeric = pd.to_numeric(series, errors="raise").astype(float)
    missing_mask = numeric.isna()
    if missing == "raise" and bool(missing_mask.any()):
        raise MissingDataError("missing values are present in values")

    clean = numeric.loc[~missing_mask].to_numpy(dtype=float, copy=True)
    if clean.size == 0:
        raise InvalidDataError("no complete observations remain")
    if not bool(np.isfinite(clean).all()):
        raise InvalidDataError("values must contain only finite values")

    return (
        clean,
        (~missing_mask).to_numpy(dtype=bool),
        len(series),
        int(missing_mask.sum()),
    )


def _validate_n_strata(n_strata: int | None, method: str) -> int | None:
    if method == "head_tail_breaks" and n_strata is None:
        return None
    if n_strata is None:
        raise ValueError(f"n_strata is required for method {method!r}")
    if isinstance(n_strata, bool) or not isinstance(n_strata, (int, np.integer)):
        raise ValueError("n_strata must be an integer")
    if int(n_strata) < 2:
        raise ValueError("n_strata must be at least 2")
    return int(n_strata)


def _weighted_sse(
    prefix_count: np.ndarray,
    prefix_sum: np.ndarray,
    prefix_square: np.ndarray,
    start: int,
    stop: int,
) -> float:
    count = prefix_count[stop] - prefix_count[start]
    total = prefix_sum[stop] - prefix_sum[start]
    square = prefix_square[stop] - prefix_square[start]
    return float(max(square - total * total / count, 0.0))


def _jenks_cut_points(values: np.ndarray, n_strata: int) -> tuple[float, ...]:
    unique, weights = np.unique(values, return_counts=True)
    k = min(n_strata, int(unique.size))
    if k < 2:
        return ()

    weighted = unique * weights
    prefix_count = np.concatenate(([0.0], np.cumsum(weights, dtype=float)))
    prefix_sum = np.concatenate(([0.0], np.cumsum(weighted, dtype=float)))
    prefix_square = np.concatenate(
        ([0.0], np.cumsum(unique * unique * weights, dtype=float))
    )

    m = int(unique.size)
    costs = np.full((k + 1, m + 1), np.inf, dtype=float)
    previous = np.full((k + 1, m + 1), -1, dtype=int)
    costs[0, 0] = 0.0

    for classes in range(1, k + 1):
        for stop in range(classes, m + 1):
            best_cost = np.inf
            best_start = -1
            for start in range(classes - 1, stop):
                candidate = costs[classes - 1, start] + _weighted_sse(
                    prefix_count,
                    prefix_sum,
                    prefix_square,
                    start,
                    stop,
                )
                tolerance = (
                    64.0
                    * np.finfo(float).eps
                    * max(
                        1.0,
                        abs(candidate),
                        abs(best_cost) if np.isfinite(best_cost) else 1.0,
                    )
                )
                if candidate < best_cost - tolerance:
                    best_cost = candidate
                    best_start = start
                elif abs(candidate - best_cost) <= tolerance and (
                    best_start < 0 or start < best_start
                ):
                    best_start = start
            costs[classes, stop] = best_cost
            previous[classes, stop] = best_start

    starts: list[int] = []
    stop = m
    for classes in range(k, 1, -1):
        start = int(previous[classes, stop])
        if start <= 0:
            break
        starts.append(start)
        stop = start
    starts.reverse()

    return tuple(float((unique[index - 1] + unique[index]) / 2.0) for index in starts)


def _head_tail_cut_points(values: np.ndarray, threshold: float) -> tuple[float, ...]:
    if not 0.0 < threshold < 1.0:
        raise ValueError("head_tail_threshold must lie strictly between 0 and 1")

    head = values.copy()
    cuts: list[float] = []
    for _ in range(100):
        mean = float(np.mean(head))
        cuts.append(mean)
        next_head = head[head > mean]
        proportion = float(next_head.size / head.size)
        if next_head.size <= 1 or proportion > threshold:
            break
        head = next_head
    return tuple(cuts)


def _make_rejected_result(
    *,
    method: str,
    keep_mask: np.ndarray,
    requested_strata: int | None,
    dropped_count: int,
    min_stratum_size: int,
    reason: str,
    metadata: Mapping[str, Any],
) -> StratificationResult:
    labels = tuple(1 if keep else None for keep in keep_mask)
    count = int(keep_mask.sum())
    return StratificationResult(
        method=method,
        labels=labels,
        cut_points=(),
        requested_strata=requested_strata,
        actual_strata=1 if count else 0,
        counts={1: count} if count else {},
        n_observations=count,
        dropped_count=dropped_count,
        duplicate_cut_points=0,
        collapsed_strata=max((requested_strata or 1) - 1, 0),
        min_stratum_size=min_stratum_size,
        rejected=True,
        rejection_reason=reason,
        supervised=False,
        metadata=metadata,
    )


def _build_result(
    *,
    method: str,
    clean: np.ndarray,
    keep_mask: np.ndarray,
    dropped_count: int,
    raw_cut_points: tuple[float, ...],
    requested_strata: int | None,
    min_stratum_size: int,
    boundary_side: str,
    metadata: Mapping[str, Any],
) -> StratificationResult:
    raw = np.asarray(raw_cut_points, dtype=float)
    raw = raw[np.isfinite(raw)]
    unique_cuts = np.unique(raw)
    duplicate_cut_points = int(raw.size - unique_cuts.size)

    clean_labels = np.searchsorted(unique_cuts, clean, side=boundary_side) + 1
    observed = np.unique(clean_labels)
    remap = {int(label): index + 1 for index, label in enumerate(observed)}
    clean_labels = np.asarray([remap[int(label)] for label in clean_labels], dtype=int)

    labels_list: list[int | None] = [None] * int(keep_mask.size)
    clean_index = 0
    for index, keep in enumerate(keep_mask):
        if keep:
            labels_list[index] = int(clean_labels[clean_index])
            clean_index += 1

    label_values, label_counts = np.unique(clean_labels, return_counts=True)
    counts = {
        int(label): int(count)
        for label, count in zip(label_values, label_counts, strict=True)
    }
    actual = int(len(counts))
    collapsed = max((requested_strata or actual) - actual, 0)
    minimum_count = min(counts.values(), default=0)

    reason = None
    if actual < 2:
        reason = "stratification produced fewer than two nonempty strata"
    elif minimum_count < min_stratum_size:
        reason = (
            f"minimum stratum count {minimum_count} is below "
            f"min_stratum_size={min_stratum_size}"
        )

    return StratificationResult(
        method=method,
        labels=tuple(labels_list),
        cut_points=tuple(float(value) for value in unique_cuts),
        requested_strata=requested_strata,
        actual_strata=actual,
        counts=counts,
        n_observations=int(clean.size),
        dropped_count=dropped_count,
        duplicate_cut_points=duplicate_cut_points,
        collapsed_strata=collapsed,
        min_stratum_size=min_stratum_size,
        rejected=reason is not None,
        rejection_reason=reason,
        supervised=False,
        metadata=metadata,
    )


def stratify(
    values: Any,
    *,
    method: str = "natural_breaks",
    n_strata: int | None = 5,
    missing: MissingPolicy = "drop",
    min_stratum_size: int = 1,
    head_tail_threshold: float = 0.4,
) -> StratificationResult:
    """Stratify one continuous variable with a deterministic audited method.

    Duplicate cut points are collapsed rather than splitting equal values across
    strata. The returned object records the requested and achieved stratum counts.
    """

    canonical = canonical_method(method)
    requested = _validate_n_strata(n_strata, canonical)
    if isinstance(min_stratum_size, bool) or min_stratum_size < 1:
        raise ValueError("min_stratum_size must be a positive integer")

    clean, keep_mask, _, dropped_count = _prepare_values(values, missing=missing)
    metadata: dict[str, Any] = {"boundary_convention": "documented per method"}

    if np.unique(clean).size < 2:
        return _make_rejected_result(
            method=canonical,
            keep_mask=keep_mask,
            requested_strata=requested,
            dropped_count=dropped_count,
            min_stratum_size=min_stratum_size,
            reason="values must contain at least two distinct observations",
            metadata=metadata,
        )

    minimum = float(np.min(clean))
    maximum = float(np.max(clean))
    boundary_side = "left"

    if canonical == "equal_interval":
        assert requested is not None
        width = (maximum - minimum) / requested
        raw_cuts = tuple(minimum + width * index for index in range(1, requested))
        metadata["boundary_convention"] = "exact cut point remains in the lower stratum"
    elif canonical == "quantile":
        assert requested is not None
        probabilities = np.arange(1, requested, dtype=float) / requested
        raw_cuts = tuple(
            float(value) for value in np.quantile(clean, probabilities, method="lower")
        )
        metadata["quantile_method"] = "lower"
        metadata["boundary_convention"] = (
            "equal values are never split; exact cut stays lower"
        )
    elif canonical == "natural_breaks":
        assert requested is not None
        raw_cuts = _jenks_cut_points(clean, requested)
        metadata["algorithm"] = "weighted Fisher-Jenks dynamic programming"
        metadata["boundary_convention"] = "midpoints between adjacent distinct values"
    elif canonical == "geometric_interval":
        assert requested is not None
        if minimum <= 0.0:
            return _make_rejected_result(
                method=canonical,
                keep_mask=keep_mask,
                requested_strata=requested,
                dropped_count=dropped_count,
                min_stratum_size=min_stratum_size,
                reason="geometric intervals require strictly positive values",
                metadata=metadata,
            )
        ratio = (maximum / minimum) ** (1.0 / requested)
        raw_cuts = tuple(minimum * ratio**index for index in range(1, requested))
        boundary_side = "right"
        metadata["ratio"] = ratio
        metadata["boundary_convention"] = "exact cut point enters the upper stratum"
    elif canonical == "standard_deviation":
        assert requested is not None
        standard_deviation = float(np.std(clean, ddof=1))
        mean = float(np.mean(clean))
        raw_cuts = tuple(
            mean + (index - requested / 2.0) * standard_deviation
            for index in range(1, requested)
        )
        metadata["mean"] = mean
        metadata["sample_standard_deviation"] = standard_deviation
        metadata["boundary_convention"] = "exact cut point remains in the lower stratum"
    else:
        raw_cuts = _head_tail_cut_points(clean, head_tail_threshold)
        boundary_side = "right"
        requested = None
        metadata["threshold"] = head_tail_threshold
        metadata["boundary_convention"] = (
            "exact recursive mean enters the upper stratum"
        )

    return _build_result(
        method=canonical,
        clean=clean,
        keep_mask=keep_mask,
        dropped_count=dropped_count,
        raw_cut_points=raw_cuts,
        requested_strata=requested,
        min_stratum_size=int(min_stratum_size),
        boundary_side=boundary_side,
        metadata=metadata,
    )
