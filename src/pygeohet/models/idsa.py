"""Interactive detector for spatial associations (IDSA)."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from itertools import combinations
from typing import Any, Literal, cast

import numpy as np
import pandas as pd

from pygeohet.exceptions import InvalidDataError, MissingDataError, SmallStratumError
from pygeohet.models.idsa_results import (
    FuzzyOperation,
    FuzzyOverlayResult,
    FuzzyRiskLevel,
    FuzzyTiePolicy,
    IDSACombinationResult,
    IDSAResult,
    InteractiveSpatialDeterminantResult,
    SpatialDiscretizationCandidate,
    SpatialDiscretizationOptimizationResult,
)
from pygeohet.models.spade_core import (
    cpsd_clean,
    psd_clean,
    validate_minimum,
    validate_permutations,
)
from pygeohet.models.spade_results import CompensatedSpatialDeterminantResult
from pygeohet.spatial.variance import _coerce_weight_matrix
from pygeohet.stratification import canonical_method, stratify
from pygeohet.validation import MissingPolicy, coerce_factor_frame

IDSASearch = Literal["greedy", "exhaustive"]
SPATIAL_DISCRETIZATION_TIE_RULE = (
    "maximum CPSD; values within cpsd_tolerance are tied; then choose fewer "
    "actual strata, fewer requested strata, earlier method order and earlier candidate"
)
IDSA_COMBINATION_TIE_RULE = (
    "maximum PID; values within pid_tolerance are tied; then choose fewer factors "
    "and earlier explanatory-factor order"
)


def _object_array(values: Sequence[Any]) -> np.ndarray:
    result = np.empty(len(values), dtype=object)
    result[:] = list(values)
    return result


def _prepare_joint_spatial(
    y: Any,
    factors: Any,
    weights: Any,
    *,
    missing: MissingPolicy,
) -> tuple[np.ndarray, pd.DataFrame, np.ndarray, np.ndarray, int, int]:
    if missing not in {"drop", "raise"}:
        raise ValueError("missing must be either 'drop' or 'raise'")
    frame = coerce_factor_frame(factors)
    if frame.empty or frame.shape[1] == 0:
        raise InvalidDataError("factors must contain at least one column")
    y_series = pd.Series(y, copy=False, name="y").reset_index(drop=True)
    if y_series.ndim != 1:
        raise InvalidDataError("y must be one-dimensional")
    if len(y_series) != len(frame):
        raise InvalidDataError("y and factors must have equal length")
    if len(y_series) == 0:
        raise InvalidDataError("y and factors must not be empty")

    matrix = _coerce_weight_matrix(weights, len(frame))
    y_numeric = pd.to_numeric(y_series, errors="raise").astype(float)
    missing_mask = y_numeric.isna() | frame.isna().any(axis=1)
    if missing == "raise" and bool(missing_mask.any()):
        raise MissingDataError("missing values are present in y or factors")
    used = np.flatnonzero(~missing_mask.to_numpy(dtype=bool))
    y_clean = y_numeric.iloc[used].to_numpy(dtype=float, copy=True)
    frame_clean = frame.iloc[used].reset_index(drop=True)
    if y_clean.size < 2:
        raise InvalidDataError("at least two complete observations are required")
    if not bool(np.isfinite(y_clean).all()):
        raise InvalidDataError("y must contain only finite values")
    return (
        y_clean,
        frame_clean,
        matrix[np.ix_(used, used)].copy(),
        used,
        int(missing_mask.sum()),
        len(frame),
    )


def _validate_fuzzy_options(
    operation: str,
    tie_policy: str,
    membership_tolerance: float,
) -> tuple[FuzzyOperation, FuzzyTiePolicy]:
    if operation not in {"and", "or"}:
        raise ValueError("operation must be either 'and' or 'or'")
    if tie_policy not in {"first", "last"}:
        raise ValueError("tie_policy must be either 'first' or 'last'")
    if membership_tolerance < 0.0:
        raise ValueError("membership_tolerance must be nonnegative")
    return cast(FuzzyOperation, operation), cast(FuzzyTiePolicy, tie_policy)


def _risk_levels_and_memberships(
    y: np.ndarray,
    factors: pd.DataFrame,
    *,
    risk_tolerance: float,
) -> tuple[
    tuple[FuzzyRiskLevel, ...],
    dict[str, np.ndarray],
    float,
    float,
]:
    risk_records: list[tuple[str, Any, int, float]] = []
    means_by_factor: dict[str, dict[Any, float]] = {}
    for factor in factors.columns:
        labels = factors[factor].to_numpy(copy=False)
        means: dict[Any, float] = {}
        for label in pd.unique(pd.Series(labels, dtype=object)):
            try:
                hash(label)
            except TypeError as exc:
                raise InvalidDataError(
                    f"factor {factor!r} contains an unhashable stratum label"
                ) from exc
            indices = np.flatnonzero(labels == label)
            mean_response = float(np.mean(y[indices]))
            means[label] = mean_response
            risk_records.append((factor, label, len(indices), mean_response))
        means_by_factor[factor] = means

    risks = np.asarray([record[3] for record in risk_records], dtype=float)
    minimum = float(np.min(risks))
    maximum = float(np.max(risks))
    spread = maximum - minimum
    scale = max(1.0, abs(minimum), abs(maximum))
    if spread <= risk_tolerance * scale:
        raise InvalidDataError(
            "all factor-stratum mean responses are equal; fuzzy memberships are undefined"
        )

    membership_by_zone: dict[tuple[str, Any], float] = {}
    levels: list[FuzzyRiskLevel] = []
    for factor, label, count, mean_response in risk_records:
        membership = float((mean_response - minimum) / spread)
        membership_by_zone[(factor, label)] = membership
        levels.append(
            FuzzyRiskLevel(
                factor=factor,
                stratum=label,
                count=count,
                mean_response=mean_response,
                membership=membership,
            )
        )

    memberships: dict[str, np.ndarray] = {}
    for factor in factors.columns:
        labels = factors[factor].to_numpy(copy=False)
        memberships[factor] = np.asarray(
            [membership_by_zone[(factor, label)] for label in labels],
            dtype=float,
        )
    return tuple(levels), memberships, minimum, maximum


def _fuzzy_overlay_clean(
    y: np.ndarray,
    factors: pd.DataFrame,
    *,
    operation: FuzzyOperation,
    tie_policy: FuzzyTiePolicy,
    membership_tolerance: float,
    risk_tolerance: float,
) -> FuzzyOverlayResult:
    if factors.shape[1] < 2:
        raise InvalidDataError("fuzzy overlay requires at least two factors")
    levels, memberships, risk_minimum, risk_maximum = _risk_levels_and_memberships(
        y,
        factors,
        risk_tolerance=risk_tolerance,
    )
    names = tuple(factors.columns)
    matrix = np.column_stack([memberships[name] for name in names])
    selected_labels: list[tuple[str, Any]] = []
    tied_rows = 0
    for row_index, row in enumerate(matrix):
        target = float(np.min(row) if operation == "and" else np.max(row))
        tied = np.flatnonzero(np.abs(row - target) <= membership_tolerance)
        if tied.size > 1:
            tied_rows += 1
        selected_index = int(tied[0] if tie_policy == "first" else tied[-1])
        factor = names[selected_index]
        label = factors.iloc[row_index, selected_index]
        selected_labels.append((factor, label))

    return FuzzyOverlayResult(
        labels=tuple(selected_labels),
        memberships={
            name: tuple(float(value) for value in memberships[name]) for name in names
        },
        risk_levels=levels,
        factors=names,
        operation=operation,
        tie_policy=tie_policy,
        membership_tolerance=float(membership_tolerance),
        tied_row_count=tied_rows,
        n_observations=len(y),
        dropped_count=0,
        used_indices=tuple(range(len(y))),
        risk_minimum=risk_minimum,
        risk_maximum=risk_maximum,
    )


def _expand_overlay(
    overlay: FuzzyOverlayResult,
    *,
    used_indices: np.ndarray,
    total_length: int,
    dropped_count: int,
) -> FuzzyOverlayResult:
    labels: list[tuple[str, Any] | None] = [None] * total_length
    memberships: dict[str, list[float | None]] = {
        name: [None] * total_length for name in overlay.factors
    }
    for clean_index, original_index in enumerate(used_indices):
        labels[int(original_index)] = overlay.labels[clean_index]
        for name in overlay.factors:
            memberships[name][int(original_index)] = overlay.memberships[name][
                clean_index
            ]
    return FuzzyOverlayResult(
        labels=tuple(labels),
        memberships={name: tuple(values) for name, values in memberships.items()},
        risk_levels=overlay.risk_levels,
        factors=overlay.factors,
        operation=overlay.operation,
        tie_policy=overlay.tie_policy,
        membership_tolerance=overlay.membership_tolerance,
        tied_row_count=overlay.tied_row_count,
        n_observations=overlay.n_observations,
        dropped_count=dropped_count,
        used_indices=tuple(int(index) for index in used_indices),
        risk_minimum=overlay.risk_minimum,
        risk_maximum=overlay.risk_maximum,
    )


def fuzzy_overlay(
    y: Any,
    factors: Any,
    *,
    operation: FuzzyOperation = "and",
    tie_policy: FuzzyTiePolicy = "first",
    missing: MissingPolicy = "drop",
    membership_tolerance: float = 1e-12,
    risk_tolerance: float = 1e-12,
) -> FuzzyOverlayResult:
    """Construct collision-safe fuzzy interaction zones from response risk.

    Membership values are min-max normalized over all factor-stratum response
    means. Fuzzy AND selects the minimum membership and fuzzy OR the maximum.
    """

    operation, tie_policy = _validate_fuzzy_options(
        operation,
        tie_policy,
        membership_tolerance,
    )
    if risk_tolerance < 0.0:
        raise ValueError("risk_tolerance must be nonnegative")
    frame = coerce_factor_frame(factors)
    y_series = pd.Series(y, copy=False, name="y").reset_index(drop=True)
    if len(y_series) != len(frame):
        raise InvalidDataError("y and factors must have equal length")
    y_numeric = pd.to_numeric(y_series, errors="raise").astype(float)
    missing_mask = y_numeric.isna() | frame.isna().any(axis=1)
    if missing == "raise" and bool(missing_mask.any()):
        raise MissingDataError("missing values are present in y or factors")
    used = np.flatnonzero(~missing_mask.to_numpy(dtype=bool))
    y_clean = y_numeric.iloc[used].to_numpy(dtype=float, copy=True)
    frame_clean = frame.iloc[used].reset_index(drop=True)
    if y_clean.size < 2:
        raise InvalidDataError("at least two complete observations are required")
    if not bool(np.isfinite(y_clean).all()):
        raise InvalidDataError("y must contain only finite values")
    overlay = _fuzzy_overlay_clean(
        y_clean,
        frame_clean,
        operation=operation,
        tie_policy=tie_policy,
        membership_tolerance=membership_tolerance,
        risk_tolerance=risk_tolerance,
    )
    return _expand_overlay(
        overlay,
        used_indices=used,
        total_length=len(frame),
        dropped_count=int(missing_mask.sum()),
    )


def _canonical_ordinal_codes(
    factors: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, dict[float, int]]]:
    encoded: dict[str, np.ndarray] = {}
    mappings: dict[str, dict[float, int]] = {}
    for name in factors.columns:
        numeric = pd.to_numeric(factors[name], errors="raise").to_numpy(dtype=float)
        if not bool(np.isfinite(numeric).all()):
            raise InvalidDataError(
                f"discrete factor {name!r} must contain finite ordinal values"
            )
        unique = np.unique(numeric)
        if unique.size < 2:
            raise InvalidDataError(
                f"discrete factor {name!r} must contain at least two strata"
            )
        codes = np.searchsorted(unique, numeric, side="left") + 1
        encoded[name] = codes.astype(int)
        mappings[name] = {float(value): index + 1 for index, value in enumerate(unique)}
    return pd.DataFrame(encoded), mappings


def _pid_clean(
    y: np.ndarray,
    discrete_factors: pd.DataFrame,
    weights: np.ndarray,
    *,
    operation: FuzzyOperation,
    tie_policy: FuzzyTiePolicy,
    membership_tolerance: float,
    risk_tolerance: float,
    min_zone_size: int,
    allow_islands: bool,
    denominator_tolerance: float,
    used_indices: tuple[int, ...],
    dropped_count: int,
) -> InteractiveSpatialDeterminantResult:
    encoded, mappings = _canonical_ordinal_codes(discrete_factors)
    overlay = _fuzzy_overlay_clean(
        y,
        encoded,
        operation=operation,
        tie_policy=tie_policy,
        membership_tolerance=membership_tolerance,
        risk_tolerance=risk_tolerance,
    )
    zones = _object_array(overlay.labels)
    theta = psd_clean(
        y,
        zones,
        weights,
        min_stratum_size=min_zone_size,
        allow_islands=allow_islands,
        used_indices=used_indices,
        dropped_count=dropped_count,
    )

    components: dict[str, Any] = {}
    within_total = 0.0
    global_total = 0.0
    for name in encoded.columns:
        values = encoded[name].to_numpy(dtype=float)
        component = psd_clean(
            values,
            zones,
            weights,
            min_stratum_size=min_zone_size,
            allow_islands=allow_islands,
            used_indices=used_indices,
            dropped_count=dropped_count,
        )
        components[name] = component
        within_total += component.within_weighted_variance
        global_total += component.total_weighted_variance
    if global_total <= denominator_tolerance:
        raise InvalidDataError("IDSA information denominator is zero")
    phi = float(1.0 - within_total / global_total)
    if abs(phi) <= denominator_tolerance:
        raise InvalidDataError("IDSA information-retention power phi is zero")
    pid = float(theta.value / phi)

    counts = pd.Series(list(overlay.labels), dtype=object).value_counts(sort=False)
    finely_divided = int(np.count_nonzero(counts.to_numpy() == 1))
    return InteractiveSpatialDeterminantResult(
        value=pid,
        theta=theta,
        phi=phi,
        information_components=components,
        overlay=overlay,
        encoded_factors={
            name: tuple(int(value) for value in encoded[name].to_numpy())
            for name in encoded.columns
        },
        n_observations=len(y),
        dropped_count=dropped_count,
        used_indices=used_indices,
        denominator_tolerance=float(denominator_tolerance),
        finely_divided_zone_count=finely_divided,
        metadata={
            "formula": "PID = theta / phi",
            "theta": "PSD(response, fuzzy_zone, W)",
            "phi": "1 - sum_i within_i / sum_i total_i",
            "ordinal_encoding": mappings,
            "overlay_recomputed_under_permutation": True,
        },
    )


def _with_permutation_inference(
    observed: InteractiveSpatialDeterminantResult,
    y: np.ndarray,
    factors: pd.DataFrame,
    weights: np.ndarray,
    *,
    operation: FuzzyOperation,
    tie_policy: FuzzyTiePolicy,
    membership_tolerance: float,
    risk_tolerance: float,
    min_zone_size: int,
    allow_islands: bool,
    denominator_tolerance: float,
    used_indices: tuple[int, ...],
    dropped_count: int,
    permutations: int,
    random_state: int | None,
) -> InteractiveSpatialDeterminantResult:
    if not permutations:
        return observed
    rng = np.random.default_rng(random_state)
    null_values: list[float] = []
    failed = 0
    for _ in range(permutations):
        try:
            candidate = _pid_clean(
                rng.permutation(y),
                factors,
                weights,
                operation=operation,
                tie_policy=tie_policy,
                membership_tolerance=membership_tolerance,
                risk_tolerance=risk_tolerance,
                min_zone_size=min_zone_size,
                allow_islands=allow_islands,
                denominator_tolerance=denominator_tolerance,
                used_indices=used_indices,
                dropped_count=dropped_count,
            )
        except (InvalidDataError, SmallStratumError):
            failed += 1
        else:
            null_values.append(candidate.value)
    if not null_values:
        raise InvalidDataError("all IDSA permutations produced invalid fuzzy zones")
    null = np.asarray(null_values, dtype=float)
    tolerance = 64.0 * np.finfo(float).eps * max(1.0, abs(observed.value))
    p_value = float(
        (1 + np.count_nonzero(null >= observed.value - tolerance)) / (len(null) + 1)
    )
    null_mean = float(np.mean(null))
    null_sd = float(np.std(null, ddof=1)) if len(null) > 1 else 0.0
    return InteractiveSpatialDeterminantResult(
        value=observed.value,
        theta=observed.theta,
        phi=observed.phi,
        information_components=observed.information_components,
        overlay=observed.overlay,
        encoded_factors=observed.encoded_factors,
        n_observations=observed.n_observations,
        dropped_count=observed.dropped_count,
        used_indices=observed.used_indices,
        denominator_tolerance=observed.denominator_tolerance,
        finely_divided_zone_count=observed.finely_divided_zone_count,
        p_value=p_value,
        permutations=permutations,
        valid_permutations=len(null),
        failed_permutations=failed,
        null_mean=null_mean,
        null_standard_deviation=null_sd,
        random_state=random_state,
        metadata=observed.metadata,
    )


def power_interactive_determinant(
    y: Any,
    discrete_factors: Any,
    weights: Any,
    *,
    operation: FuzzyOperation = "and",
    tie_policy: FuzzyTiePolicy = "first",
    missing: MissingPolicy = "drop",
    membership_tolerance: float = 1e-12,
    risk_tolerance: float = 1e-12,
    min_zone_size: int = 2,
    allow_islands: bool = False,
    denominator_tolerance: float = 1e-12,
    permutations: int = 0,
    random_state: int | None = None,
) -> InteractiveSpatialDeterminantResult:
    """Calculate fixed-strata IDSA power ``PID = theta / phi``."""

    operation, tie_policy = _validate_fuzzy_options(
        operation,
        tie_policy,
        membership_tolerance,
    )
    if risk_tolerance < 0.0 or denominator_tolerance < 0.0:
        raise ValueError("risk_tolerance and denominator_tolerance must be nonnegative")
    minimum = validate_minimum(min_zone_size)
    permutation_count = validate_permutations(permutations)
    y_clean, frame, matrix, used, dropped, total_length = _prepare_joint_spatial(
        y,
        discrete_factors,
        weights,
        missing=missing,
    )
    if frame.shape[1] < 2:
        raise InvalidDataError("IDSA requires at least two explanatory factors")
    used_tuple = tuple(int(index) for index in used)
    result = _pid_clean(
        y_clean,
        frame,
        matrix,
        operation=operation,
        tie_policy=tie_policy,
        membership_tolerance=membership_tolerance,
        risk_tolerance=risk_tolerance,
        min_zone_size=minimum,
        allow_islands=allow_islands,
        denominator_tolerance=denominator_tolerance,
        used_indices=used_tuple,
        dropped_count=dropped,
    )
    result = _with_permutation_inference(
        result,
        y_clean,
        frame,
        matrix,
        operation=operation,
        tie_policy=tie_policy,
        membership_tolerance=membership_tolerance,
        risk_tolerance=risk_tolerance,
        min_zone_size=minimum,
        allow_islands=allow_islands,
        denominator_tolerance=denominator_tolerance,
        used_indices=used_tuple,
        dropped_count=dropped,
        permutations=permutation_count,
        random_state=random_state,
    )
    expanded_overlay = _expand_overlay(
        result.overlay,
        used_indices=used,
        total_length=total_length,
        dropped_count=dropped,
    )
    encoded_full: dict[str, tuple[int | None, ...]] = {}
    for name, values in result.encoded_factors.items():
        full: list[int | None] = [None] * total_length
        for clean_index, original_index in enumerate(used):
            full[int(original_index)] = values[clean_index]
        encoded_full[name] = tuple(full)
    return InteractiveSpatialDeterminantResult(
        value=result.value,
        theta=result.theta,
        phi=result.phi,
        information_components=result.information_components,
        overlay=expanded_overlay,
        encoded_factors=encoded_full,
        n_observations=result.n_observations,
        dropped_count=result.dropped_count,
        used_indices=result.used_indices,
        denominator_tolerance=result.denominator_tolerance,
        finely_divided_zone_count=result.finely_divided_zone_count,
        p_value=result.p_value,
        permutations=result.permutations,
        valid_permutations=result.valid_permutations,
        failed_permutations=result.failed_permutations,
        null_mean=result.null_mean,
        null_standard_deviation=result.null_standard_deviation,
        random_state=result.random_state,
        metadata=result.metadata,
    )


def _parse_spatial_discretization_grid(
    methods: Sequence[str],
    n_strata: Iterable[int],
) -> tuple[tuple[str, ...], tuple[int, ...]]:
    canonical_methods = tuple(
        dict.fromkeys(canonical_method(method) for method in methods)
    )
    if not canonical_methods:
        raise ValueError("methods must contain at least one method")
    if "head_tail_breaks" in canonical_methods:
        raise ValueError(
            "head_tail_breaks has an automatic class count and is not supported in IDSA search"
        )
    levels: list[int] = []
    for value in n_strata:
        if isinstance(value, bool) or not isinstance(value, (int, np.integer)):
            raise ValueError("n_strata must contain integers")
        integer = int(value)
        if integer < 2:
            raise ValueError("all n_strata values must be at least 2")
        levels.append(integer)
    parsed_levels = tuple(dict.fromkeys(levels))
    if not parsed_levels:
        raise ValueError("n_strata must contain at least one level")
    return canonical_methods, parsed_levels


def _optimize_spatial_discretization_clean(
    y: np.ndarray,
    x: np.ndarray,
    weights: np.ndarray,
    *,
    methods: tuple[str, ...],
    n_strata: tuple[int, ...],
    min_stratum_size: int,
    allow_islands: bool,
    denominator_tolerance: float,
    cpsd_tolerance: float,
) -> SpatialDiscretizationOptimizationResult:
    candidates: list[SpatialDiscretizationCandidate] = []
    candidate_index = 0
    for method_rank, method in enumerate(methods):
        for classes in n_strata:
            stratification = None
            try:
                stratification = stratify(
                    x,
                    method=method,
                    n_strata=classes,
                    missing="raise",
                    min_stratum_size=min_stratum_size,
                )
                if stratification.rejected:
                    raise InvalidDataError(
                        stratification.rejection_reason or "stratification was rejected"
                    )
                labels = np.asarray(stratification.labels, dtype=object)
                value, response, information = cpsd_clean(
                    y,
                    x,
                    labels,
                    weights,
                    min_stratum_size=min_stratum_size,
                    allow_islands=allow_islands,
                    denominator_tolerance=denominator_tolerance,
                )
                cpsd = CompensatedSpatialDeterminantResult(
                    value=value,
                    response_psd=response,
                    information_psd=information,
                    n_observations=len(y),
                    dropped_count=0,
                    used_indices=tuple(range(len(y))),
                    denominator_tolerance=denominator_tolerance,
                )
            except (InvalidDataError, SmallStratumError, ValueError) as exc:
                candidates.append(
                    SpatialDiscretizationCandidate(
                        candidate_index=candidate_index,
                        method_rank=method_rank,
                        method=method,
                        requested_strata=classes,
                        stratification=stratification,
                        result=None,
                        accepted=False,
                        rejection_reason=str(exc),
                    )
                )
            else:
                candidates.append(
                    SpatialDiscretizationCandidate(
                        candidate_index=candidate_index,
                        method_rank=method_rank,
                        method=method,
                        requested_strata=classes,
                        stratification=stratification,
                        result=cpsd,
                        accepted=True,
                        rejection_reason=None,
                    )
                )
            candidate_index += 1

    accepted = [candidate for candidate in candidates if candidate.result is not None]
    if not accepted:
        reasons = sorted(
            {
                candidate.rejection_reason
                for candidate in candidates
                if candidate.rejection_reason is not None
            }
        )
        raise InvalidDataError(
            "no spatial discretization candidate was accepted: " + "; ".join(reasons)
        )
    best_value = max(
        candidate.result.value for candidate in accepted if candidate.result
    )
    tied = [
        candidate
        for candidate in accepted
        if candidate.result is not None
        and candidate.result.value >= best_value - cpsd_tolerance
    ]
    best = min(
        tied,
        key=lambda candidate: (
            (
                candidate.stratification.actual_strata
                if candidate.stratification is not None
                else candidate.requested_strata
            ),
            candidate.requested_strata,
            candidate.method_rank,
            candidate.candidate_index,
        ),
    )
    return SpatialDiscretizationOptimizationResult(
        candidates=tuple(candidates),
        best=best,
        tie_rule=SPATIAL_DISCRETIZATION_TIE_RULE,
        cpsd_tolerance=float(cpsd_tolerance),
    )


def optimize_spatial_discretization(
    y: Any,
    x: Any,
    weights: Any,
    *,
    methods: Sequence[str] = (
        "quantile",
        "natural_breaks",
        "equal_interval",
        "geometric_interval",
        "standard_deviation",
    ),
    n_strata: Iterable[int] = range(3, 9),
    missing: MissingPolicy = "drop",
    min_stratum_size: int = 2,
    allow_islands: bool = False,
    denominator_tolerance: float = 1e-12,
    cpsd_tolerance: float = 1e-12,
) -> SpatialDiscretizationOptimizationResult:
    """Select one continuous-factor discretization by maximum CPSD."""

    if denominator_tolerance < 0.0 or cpsd_tolerance < 0.0:
        raise ValueError("denominator_tolerance and cpsd_tolerance must be nonnegative")
    minimum = validate_minimum(min_stratum_size)
    parsed_methods, parsed_levels = _parse_spatial_discretization_grid(
        methods,
        n_strata,
    )
    y_clean, frame, matrix, _, _, _ = _prepare_joint_spatial(
        y,
        {"x": x},
        weights,
        missing=missing,
    )
    x_clean = pd.to_numeric(frame["x"], errors="raise").to_numpy(dtype=float)
    if not bool(np.isfinite(x_clean).all()):
        raise InvalidDataError("x must contain only finite values")
    return _optimize_spatial_discretization_clean(
        y_clean,
        x_clean,
        matrix,
        methods=parsed_methods,
        n_strata=parsed_levels,
        min_stratum_size=minimum,
        allow_islands=allow_islands,
        denominator_tolerance=denominator_tolerance,
        cpsd_tolerance=cpsd_tolerance,
    )


def _evaluate_combination(
    y: np.ndarray,
    discrete: pd.DataFrame,
    weights: np.ndarray,
    factors: tuple[str, ...],
    *,
    operation: FuzzyOperation,
    tie_policy: FuzzyTiePolicy,
    membership_tolerance: float,
    risk_tolerance: float,
    min_zone_size: int,
    allow_islands: bool,
    denominator_tolerance: float,
    used_indices: tuple[int, ...],
    dropped_count: int,
    search_step: int,
    added_factor: str | None,
) -> IDSACombinationResult:
    try:
        result = _pid_clean(
            y,
            discrete.loc[:, list(factors)],
            weights,
            operation=operation,
            tie_policy=tie_policy,
            membership_tolerance=membership_tolerance,
            risk_tolerance=risk_tolerance,
            min_zone_size=min_zone_size,
            allow_islands=allow_islands,
            denominator_tolerance=denominator_tolerance,
            used_indices=used_indices,
            dropped_count=dropped_count,
        )
    except (InvalidDataError, SmallStratumError, ValueError) as exc:
        return IDSACombinationResult(
            factors=factors,
            result=None,
            accepted=False,
            rejection_reason=str(exc),
            search_step=search_step,
            added_factor=added_factor,
        )
    return IDSACombinationResult(
        factors=factors,
        result=result,
        accepted=True,
        rejection_reason=None,
        search_step=search_step,
        added_factor=added_factor,
    )


def _select_best_combination(
    candidates: Sequence[IDSACombinationResult],
    factor_rank: dict[str, int],
    pid_tolerance: float,
) -> IDSACombinationResult:
    accepted = [item for item in candidates if item.result is not None]
    if not accepted:
        raise InvalidDataError("no IDSA factor combination was accepted")
    best_value = max(item.result.value for item in accepted if item.result is not None)
    tied = [
        item
        for item in accepted
        if item.result is not None and item.result.value >= best_value - pid_tolerance
    ]
    return min(
        tied,
        key=lambda item: (
            len(item.factors),
            tuple(factor_rank[name] for name in item.factors),
        ),
    )


class IDSA:
    """Optimize continuous factors and identify their spatial fuzzy interaction."""

    def __init__(
        self,
        *,
        methods: Sequence[str] = (
            "quantile",
            "natural_breaks",
            "equal_interval",
            "geometric_interval",
            "standard_deviation",
        ),
        n_strata: Iterable[int] = range(3, 9),
        search: IDSASearch = "greedy",
        operation: FuzzyOperation = "and",
        tie_policy: FuzzyTiePolicy = "first",
        missing: MissingPolicy = "drop",
        min_stratum_size: int = 2,
        min_zone_size: int = 2,
        allow_islands: bool = False,
        membership_tolerance: float = 1e-12,
        risk_tolerance: float = 1e-12,
        denominator_tolerance: float = 1e-12,
        cpsd_tolerance: float = 1e-12,
        pid_tolerance: float = 1e-12,
        max_combinations: int = 4096,
        permutations: int = 0,
        random_state: int | None = None,
    ) -> None:
        if search not in {"greedy", "exhaustive"}:
            raise ValueError("search must be either 'greedy' or 'exhaustive'")
        if isinstance(max_combinations, bool) or max_combinations < 1:
            raise ValueError("max_combinations must be a positive integer")
        if cpsd_tolerance < 0.0 or pid_tolerance < 0.0:
            raise ValueError("cpsd_tolerance and pid_tolerance must be nonnegative")
        self.methods = tuple(methods)
        self.n_strata = tuple(n_strata)
        self.search = search
        self.operation = operation
        self.tie_policy = tie_policy
        self.missing = missing
        self.min_stratum_size = min_stratum_size
        self.min_zone_size = min_zone_size
        self.allow_islands = allow_islands
        self.membership_tolerance = membership_tolerance
        self.risk_tolerance = risk_tolerance
        self.denominator_tolerance = denominator_tolerance
        self.cpsd_tolerance = cpsd_tolerance
        self.pid_tolerance = pid_tolerance
        self.max_combinations = int(max_combinations)
        self.permutations = permutations
        self.random_state = random_state

    def fit(self, y: Any, continuous_factors: Any, weights: Any) -> IDSAResult:
        """Fit spatial discretizations and search fuzzy factor interactions."""

        operation, tie_policy = _validate_fuzzy_options(
            self.operation,
            self.tie_policy,
            self.membership_tolerance,
        )
        if self.risk_tolerance < 0.0 or self.denominator_tolerance < 0.0:
            raise ValueError(
                "risk_tolerance and denominator_tolerance must be nonnegative"
            )
        minimum = validate_minimum(self.min_stratum_size)
        minimum_zone = validate_minimum(self.min_zone_size)
        permutation_count = validate_permutations(self.permutations)
        methods, levels = _parse_spatial_discretization_grid(
            self.methods,
            self.n_strata,
        )
        y_clean, raw, matrix, used, dropped, total_length = _prepare_joint_spatial(
            y,
            continuous_factors,
            weights,
            missing=self.missing,
        )
        if raw.shape[1] < 2:
            raise InvalidDataError("IDSA requires at least two explanatory factors")
        numeric = raw.apply(pd.to_numeric, errors="raise").astype(float)
        if not bool(np.isfinite(numeric.to_numpy(dtype=float)).all()):
            raise InvalidDataError("continuous factors must contain only finite values")

        optimizations: dict[str, SpatialDiscretizationOptimizationResult] = {}
        discrete_clean: dict[str, np.ndarray] = {}
        individual_power: dict[str, float] = {}
        for name in numeric.columns:
            optimization = _optimize_spatial_discretization_clean(
                y_clean,
                numeric[name].to_numpy(dtype=float),
                matrix,
                methods=methods,
                n_strata=levels,
                min_stratum_size=minimum,
                allow_islands=self.allow_islands,
                denominator_tolerance=self.denominator_tolerance,
                cpsd_tolerance=self.cpsd_tolerance,
            )
            assert optimization.best.stratification is not None
            assert optimization.best.result is not None
            optimizations[name] = optimization
            discrete_clean[name] = np.asarray(
                optimization.best.stratification.labels,
                dtype=int,
            )
            individual_power[name] = optimization.best.result.value
        discrete = pd.DataFrame(discrete_clean)

        factor_order: tuple[str, ...] = tuple(str(name) for name in numeric.columns)
        factor_rank = {name: index for index, name in enumerate(factor_order)}
        used_tuple = tuple(int(index) for index in used)
        attempts: list[IDSACombinationResult] = []

        if self.search == "exhaustive":
            requested = sum(
                1
                for size in range(2, len(factor_order) + 1)
                for _ in combinations(factor_order, size)
            )
            if requested > self.max_combinations:
                raise InvalidDataError(
                    f"exhaustive IDSA requires {requested} combinations, exceeding "
                    f"max_combinations={self.max_combinations}"
                )
            step = 1
            for size in range(2, len(factor_order) + 1):
                for subset in combinations(factor_order, size):
                    attempts.append(
                        _evaluate_combination(
                            y_clean,
                            discrete,
                            matrix,
                            tuple(subset),
                            operation=operation,
                            tie_policy=tie_policy,
                            membership_tolerance=self.membership_tolerance,
                            risk_tolerance=self.risk_tolerance,
                            min_zone_size=minimum_zone,
                            allow_islands=self.allow_islands,
                            denominator_tolerance=self.denominator_tolerance,
                            used_indices=used_tuple,
                            dropped_count=dropped,
                            search_step=step,
                            added_factor=None,
                        )
                    )
                    step += 1
            best = _select_best_combination(attempts, factor_rank, self.pid_tolerance)
        else:
            ranked = sorted(
                factor_order,
                key=lambda name: (-individual_power[name], factor_rank[name]),
            )
            current: tuple[str, ...] = (ranked[0],)
            remaining = [name for name in factor_order if name not in current]
            step = 1
            pair_attempts: list[IDSACombinationResult] = []
            for name in remaining:
                subset = tuple(sorted((*current, name), key=factor_rank.__getitem__))
                candidate = _evaluate_combination(
                    y_clean,
                    discrete,
                    matrix,
                    subset,
                    operation=operation,
                    tie_policy=tie_policy,
                    membership_tolerance=self.membership_tolerance,
                    risk_tolerance=self.risk_tolerance,
                    min_zone_size=minimum_zone,
                    allow_islands=self.allow_islands,
                    denominator_tolerance=self.denominator_tolerance,
                    used_indices=used_tuple,
                    dropped_count=dropped,
                    search_step=step,
                    added_factor=name,
                )
                attempts.append(candidate)
                pair_attempts.append(candidate)
            best = _select_best_combination(
                pair_attempts,
                factor_rank,
                self.pid_tolerance,
            )
            assert best.result is not None
            current = best.factors
            current_value = best.result.value
            remaining = [name for name in factor_order if name not in current]
            while remaining:
                step += 1
                stage_attempts: list[IDSACombinationResult] = []
                for name in remaining:
                    subset = tuple(
                        sorted((*current, name), key=factor_rank.__getitem__)
                    )
                    candidate = _evaluate_combination(
                        y_clean,
                        discrete,
                        matrix,
                        subset,
                        operation=operation,
                        tie_policy=tie_policy,
                        membership_tolerance=self.membership_tolerance,
                        risk_tolerance=self.risk_tolerance,
                        min_zone_size=minimum_zone,
                        allow_islands=self.allow_islands,
                        denominator_tolerance=self.denominator_tolerance,
                        used_indices=used_tuple,
                        dropped_count=dropped,
                        search_step=step,
                        added_factor=name,
                    )
                    attempts.append(candidate)
                    stage_attempts.append(candidate)
                accepted_stage = [
                    item for item in stage_attempts if item.result is not None
                ]
                if not accepted_stage:
                    break
                stage_best = _select_best_combination(
                    accepted_stage,
                    factor_rank,
                    self.pid_tolerance,
                )
                assert stage_best.result is not None
                if stage_best.result.value <= current_value + self.pid_tolerance:
                    break
                best = stage_best
                current = stage_best.factors
                current_value = stage_best.result.value
                remaining = [name for name in factor_order if name not in current]

        assert best.result is not None
        if permutation_count:
            best_with_inference = _with_permutation_inference(
                best.result,
                y_clean,
                discrete.loc[:, list(best.factors)],
                matrix,
                operation=operation,
                tie_policy=tie_policy,
                membership_tolerance=self.membership_tolerance,
                risk_tolerance=self.risk_tolerance,
                min_zone_size=minimum_zone,
                allow_islands=self.allow_islands,
                denominator_tolerance=self.denominator_tolerance,
                used_indices=used_tuple,
                dropped_count=dropped,
                permutations=permutation_count,
                random_state=self.random_state,
            )
            replacement = IDSACombinationResult(
                factors=best.factors,
                result=best_with_inference,
                accepted=True,
                rejection_reason=None,
                search_step=best.search_step,
                added_factor=best.added_factor,
            )
            attempts = [replacement if item is best else item for item in attempts]
            best = replacement

        discrete_full: dict[str, tuple[int | None, ...]] = {}
        for name in factor_order:
            full: list[int | None] = [None] * total_length
            for clean_index, original_index in enumerate(used):
                full[int(original_index)] = int(discrete.iloc[clean_index][name])
            discrete_full[name] = tuple(full)

        if best.result is not None:
            expanded_overlay = _expand_overlay(
                best.result.overlay,
                used_indices=used,
                total_length=total_length,
                dropped_count=dropped,
            )
            final_result = InteractiveSpatialDeterminantResult(
                value=best.result.value,
                theta=best.result.theta,
                phi=best.result.phi,
                information_components=best.result.information_components,
                overlay=expanded_overlay,
                encoded_factors={name: discrete_full[name] for name in best.factors},
                n_observations=best.result.n_observations,
                dropped_count=best.result.dropped_count,
                used_indices=best.result.used_indices,
                denominator_tolerance=best.result.denominator_tolerance,
                finely_divided_zone_count=best.result.finely_divided_zone_count,
                p_value=best.result.p_value,
                permutations=best.result.permutations,
                valid_permutations=best.result.valid_permutations,
                failed_permutations=best.result.failed_permutations,
                null_mean=best.result.null_mean,
                null_standard_deviation=best.result.null_standard_deviation,
                random_state=best.result.random_state,
                metadata=best.result.metadata,
            )
            final_best = IDSACombinationResult(
                factors=best.factors,
                result=final_result,
                accepted=True,
                rejection_reason=None,
                search_step=best.search_step,
                added_factor=best.added_factor,
            )
            attempts = [final_best if item is best else item for item in attempts]
            best = final_best

        return IDSAResult(
            discretizations=optimizations,
            discrete_labels=discrete_full,
            combinations=tuple(attempts),
            best=best,
            search=self.search,
            operation=operation,
            tie_rule=IDSA_COMBINATION_TIE_RULE,
        )


def idsa(
    y: Any,
    continuous_factors: Any,
    weights: Any,
    **kwargs: Any,
) -> IDSAResult:
    """Functional interface to :class:`IDSA`."""

    return IDSA(**kwargs).fit(y, continuous_factors, weights)


__all__ = [
    "IDSA",
    "IDSAResult",
    "fuzzy_overlay",
    "idsa",
    "optimize_spatial_discretization",
    "power_interactive_determinant",
]
