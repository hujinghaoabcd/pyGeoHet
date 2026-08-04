"""q-guided evaluation and optimal univariate stratification."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import replace
from typing import Any

import numpy as np
import pandas as pd

from pygeohet.core.qstat import q_statistic
from pygeohet.exceptions import InvalidDataError, MissingDataError
from pygeohet.stratification.methods import canonical_method, stratify
from pygeohet.stratification.results import (
    OptimalStratificationResult,
    StratificationEvaluationResult,
    StratificationResult,
)
from pygeohet.validation import MissingPolicy

TIE_RULE = (
    "maximum q; q values within q_tolerance are tied; then prefer fewer actual "
    "strata, fewer requested strata, earlier method order, and earlier candidate"
)


def evaluate_stratification(
    y: Any,
    stratification: StratificationResult | Any,
    *,
    missing: MissingPolicy = "drop",
    min_stratum_size: int = 2,
    require_requested_strata: bool = False,
    candidate_index: int = 0,
    method_rank: int = 0,
) -> StratificationEvaluationResult:
    """Evaluate one stratification with q while preserving rejection evidence."""

    if isinstance(stratification, StratificationResult):
        result = stratification
    else:
        labels = tuple(
            None if pd.isna(value) else int(value) for value in stratification
        )
        observed = [label for label in labels if label is not None]
        counts_series = pd.Series(observed, dtype=int).value_counts(sort=False)
        counts = {
            int(label): int(count) for label, count in counts_series.items()
        }
        result = StratificationResult(
            method="supplied_labels",
            labels=labels,
            cut_points=(),
            requested_strata=None,
            actual_strata=len(counts),
            counts=counts,
            n_observations=len(observed),
            dropped_count=len(labels) - len(observed),
            duplicate_cut_points=0,
            collapsed_strata=0,
            min_stratum_size=min_stratum_size,
            rejected=False,
            rejection_reason=None,
            supervised=False,
            metadata={"source": "supplied labels"},
        )

    reason = result.rejection_reason if result.rejected else None
    if (
        reason is None
        and require_requested_strata
        and result.requested_strata is not None
        and result.actual_strata != result.requested_strata
    ):
        reason = (
            f"requested {result.requested_strata} strata but produced "
            f"{result.actual_strata}"
        )

    if reason is not None:
        return StratificationEvaluationResult(
            candidate_index=candidate_index,
            method_rank=method_rank,
            stratification=result,
            q_result=None,
            accepted=False,
            rejection_reason=reason,
        )

    try:
        q_result = q_statistic(
            y,
            result.labels,
            missing=missing,
            min_stratum_size=min_stratum_size,
        )
    except (InvalidDataError, ValueError) as exc:
        return StratificationEvaluationResult(
            candidate_index=candidate_index,
            method_rank=method_rank,
            stratification=result,
            q_result=None,
            accepted=False,
            rejection_reason=str(exc),
        )

    return StratificationEvaluationResult(
        candidate_index=candidate_index,
        method_rank=method_rank,
        stratification=result,
        q_result=q_result,
        accepted=True,
        rejection_reason=None,
    )


def _prepare_joint_numeric(
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

    keep = (~missing_mask).to_numpy(dtype=bool)
    y_clean = y_numeric.loc[~missing_mask].to_numpy(dtype=float, copy=True)
    x_clean = x_numeric.loc[~missing_mask].to_numpy(dtype=float, copy=True)
    if y_clean.size == 0:
        raise InvalidDataError("no complete observations remain")
    if not bool(np.isfinite(y_clean).all() and np.isfinite(x_clean).all()):
        raise InvalidDataError("y and x must contain only finite values")
    return y_clean, x_clean, keep, int(missing_mask.sum())


def _expand_result(
    result: StratificationResult,
    keep_mask: np.ndarray,
    dropped_count: int,
) -> StratificationResult:
    clean_labels = iter(result.labels)
    expanded = tuple(next(clean_labels) if keep else None for keep in keep_mask)
    return replace(
        result,
        labels=expanded,
        dropped_count=dropped_count,
        n_observations=int(keep_mask.sum()),
    )


def _validated_counts(n_strata: Iterable[int]) -> tuple[int, ...]:
    counts: list[int] = []
    for value in n_strata:
        if isinstance(value, bool) or not isinstance(value, (int, np.integer)):
            raise ValueError("all n_strata candidates must be integers")
        integer = int(value)
        if integer < 2:
            raise ValueError("all n_strata candidates must be at least 2")
        if integer not in counts:
            counts.append(integer)
    if not counts:
        raise ValueError("n_strata must contain at least one candidate")
    return tuple(counts)


def optimize_stratification(
    y: Any,
    x: Any,
    *,
    methods: Sequence[str] = (
        "standard_deviation",
        "equal_interval",
        "geometric_interval",
        "quantile",
        "natural_breaks",
    ),
    n_strata: Iterable[int] = range(3, 9),
    missing: MissingPolicy = "drop",
    min_stratum_size: int = 2,
    require_requested_strata: bool = True,
    q_tolerance: float = 1e-12,
    head_tail_threshold: float = 0.4,
) -> OptimalStratificationResult:
    """Search method-by-class candidates and retain the complete audit table."""

    if q_tolerance < 0.0:
        raise ValueError("q_tolerance must be nonnegative")
    if not methods:
        raise ValueError("methods must contain at least one method")

    canonical_methods: list[str] = []
    for method in methods:
        canonical = canonical_method(method)
        if canonical not in canonical_methods:
            canonical_methods.append(canonical)
    requested_counts = _validated_counts(n_strata)

    y_clean, x_clean, keep_mask, dropped_count = _prepare_joint_numeric(
        y, x, missing=missing
    )

    candidates: list[StratificationEvaluationResult] = []
    candidate_index = 0
    for method_rank, method in enumerate(canonical_methods):
        method_counts: tuple[int | None, ...]
        if method == "head_tail_breaks":
            method_counts = (None,)
        else:
            method_counts = requested_counts

        for requested in method_counts:
            stratification = stratify(
                x_clean,
                method=method,
                n_strata=requested,
                missing="raise",
                min_stratum_size=min_stratum_size,
                head_tail_threshold=head_tail_threshold,
            )
            evaluation = evaluate_stratification(
                y_clean,
                stratification,
                missing="raise",
                min_stratum_size=min_stratum_size,
                require_requested_strata=require_requested_strata,
                candidate_index=candidate_index,
                method_rank=method_rank,
            )
            expanded = _expand_result(
                evaluation.stratification, keep_mask, dropped_count
            )
            candidates.append(replace(evaluation, stratification=expanded))
            candidate_index += 1

    accepted = [
        item for item in candidates if item.accepted and item.q_result is not None
    ]
    best = None
    if accepted:
        maximum_q = max(
            item.q_result.q
            for item in accepted
            if item.q_result is not None
        )
        tied = [
            item
            for item in accepted
            if item.q_result is not None
            and maximum_q - item.q_result.q <= q_tolerance
        ]
        best = min(
            tied,
            key=lambda item: (
                item.stratification.actual_strata,
                item.stratification.requested_strata
                if item.stratification.requested_strata is not None
                else item.stratification.actual_strata,
                item.method_rank,
                item.candidate_index,
            ),
        )

    return OptimalStratificationResult(
        candidates=tuple(candidates),
        best=best,
        tie_rule=TIE_RULE,
        q_tolerance=float(q_tolerance),
    )
