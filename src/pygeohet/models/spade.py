"""Spatial association detector (SPADE) workflows."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any

import numpy as np
import pandas as pd

from pygeohet.exceptions import InvalidDataError, SmallStratumError
from pygeohet.models.spade_core import (
    compensated_spatial_determinant,
    cpsd_clean,
    power_spatial_determinant,
    prepare_cpsd_sample,
    validate_minimum,
    validate_permutations,
)
from pygeohet.models.spade_results import (
    CompensatedSpatialDeterminantResult,
    MultilevelSpatialCandidate,
    MultilevelSpatialDeterminantResult,
    SPADEResult,
)
from pygeohet.spatial.variance import _coerce_weight_matrix
from pygeohet.stratification import StratificationResult, canonical_method, stratify
from pygeohet.validation import MissingPolicy, coerce_factor_frame


def _parse_levels(levels: Iterable[int]) -> tuple[int, ...]:
    parsed: list[int] = []
    for value in levels:
        if isinstance(value, bool) or not isinstance(value, (int, np.integer)):
            raise ValueError("n_strata must contain integers")
        integer = int(value)
        if integer < 2:
            raise ValueError("all n_strata values must be at least 2")
        parsed.append(integer)
    result = tuple(dict.fromkeys(parsed))
    if not result:
        raise ValueError("n_strata must contain at least one level")
    return result


def _permutation_summary(
    observed: float,
    null_values: np.ndarray,
) -> tuple[float, float, float]:
    tolerance = 64.0 * np.finfo(float).eps * max(1.0, abs(observed))
    p_value = float(
        (1 + np.count_nonzero(null_values >= observed - tolerance))
        / (len(null_values) + 1)
    )
    null_mean = float(np.mean(null_values))
    null_sd = float(np.std(null_values, ddof=1)) if len(null_values) > 1 else 0.0
    return p_value, null_mean, null_sd


def multilevel_spatial_determinant(
    y: Any,
    x: Any,
    weights: Any,
    *,
    n_strata: Iterable[int] = range(3, 9),
    method: str = "quantile",
    missing: MissingPolicy = "drop",
    min_stratum_size: int = 2,
    allow_islands: bool = False,
    denominator_tolerance: float = 1e-12,
    invalid: str = "omit",
    permutations: int = 0,
    random_state: int | None = None,
) -> MultilevelSpatialDeterminantResult:
    """Calculate PSMD as the mean CPSD over explicit discretization levels."""

    if invalid not in {"omit", "raise"}:
        raise ValueError("invalid must be either 'omit' or 'raise'")
    minimum = validate_minimum(min_stratum_size)
    levels = _parse_levels(n_strata)
    canonical = canonical_method(method)
    if canonical == "head_tail_breaks":
        raise ValueError(
            "head_tail_breaks has an automatic class count and cannot define PSMD levels"
        )
    if denominator_tolerance < 0.0:
        raise ValueError("denominator_tolerance must be nonnegative")
    permutation_count = validate_permutations(permutations)

    y_length = len(pd.Series(y, copy=False))
    placeholder = np.zeros(y_length, dtype=int)
    y_clean, x_clean, _, matrix, used, dropped = prepare_cpsd_sample(
        y,
        x,
        placeholder,
        weights,
        missing=missing,
    )

    candidates: list[MultilevelSpatialCandidate] = []
    accepted_labels: list[np.ndarray] = []
    accepted_values: list[float] = []
    accepted_levels: list[int] = []
    for level in levels:
        stratification: StratificationResult | None = None
        try:
            stratification = stratify(
                x_clean,
                method=canonical,
                n_strata=level,
                missing="raise",
                min_stratum_size=minimum,
            )
            if stratification.rejected:
                raise InvalidDataError(
                    stratification.rejection_reason or "stratification was rejected"
                )
            labels = np.asarray(stratification.labels, dtype=object)
            value, response, information = cpsd_clean(
                y_clean,
                x_clean,
                labels,
                matrix,
                min_stratum_size=minimum,
                allow_islands=allow_islands,
                denominator_tolerance=denominator_tolerance,
            )
            result = CompensatedSpatialDeterminantResult(
                value=value,
                response_psd=response,
                information_psd=information,
                n_observations=len(y_clean),
                dropped_count=dropped,
                used_indices=tuple(int(index) for index in used),
                denominator_tolerance=float(denominator_tolerance),
            )
        except (InvalidDataError, SmallStratumError, ValueError) as exc:
            candidates.append(
                MultilevelSpatialCandidate(
                    requested_strata=level,
                    stratification=stratification,
                    result=None,
                    accepted=False,
                    rejection_reason=str(exc),
                )
            )
            if invalid == "raise":
                raise InvalidDataError(f"PSMD level {level} failed: {exc}") from exc
        else:
            candidates.append(
                MultilevelSpatialCandidate(
                    requested_strata=level,
                    stratification=stratification,
                    result=result,
                    accepted=True,
                    rejection_reason=None,
                )
            )
            accepted_labels.append(labels)
            accepted_values.append(value)
            accepted_levels.append(level)

    if len(accepted_values) < 2:
        raise InvalidDataError("PSMD requires at least two accepted discretization levels")
    observed = float(np.mean(accepted_values))

    p_value: float | None = None
    null_mean: float | None = None
    null_sd: float | None = None
    if permutation_count:
        rng = np.random.default_rng(random_state)
        null_values = np.empty(permutation_count, dtype=float)
        for permutation_index in range(permutation_count):
            permuted = rng.permutation(y_clean)
            values = [
                cpsd_clean(
                    permuted,
                    x_clean,
                    labels,
                    matrix,
                    min_stratum_size=minimum,
                    allow_islands=allow_islands,
                    denominator_tolerance=denominator_tolerance,
                )[0]
                for labels in accepted_labels
            ]
            null_values[permutation_index] = float(np.mean(values))
        p_value, null_mean, null_sd = _permutation_summary(observed, null_values)

    return MultilevelSpatialDeterminantResult(
        value=observed,
        candidates=tuple(candidates),
        method=canonical,
        requested_levels=levels,
        accepted_levels=tuple(accepted_levels),
        n_observations=len(y_clean),
        dropped_count=dropped,
        used_indices=tuple(int(index) for index in used),
        p_value=p_value,
        permutations=permutation_count,
        null_mean=null_mean,
        null_standard_deviation=null_sd,
        random_state=random_state,
    )


class SPADE:
    """Run PSD for categorical factors and PSMD for continuous factors."""

    def __init__(
        self,
        *,
        n_strata: Iterable[int] = range(3, 9),
        method: str = "quantile",
        missing: MissingPolicy = "drop",
        min_stratum_size: int = 2,
        allow_islands: bool = False,
        denominator_tolerance: float = 1e-12,
        invalid: str = "omit",
        permutations: int = 0,
        random_state: int | None = None,
    ) -> None:
        self.n_strata = tuple(n_strata)
        self.method = method
        self.missing = missing
        self.min_stratum_size = min_stratum_size
        self.allow_islands = allow_islands
        self.denominator_tolerance = denominator_tolerance
        self.invalid = invalid
        self.permutations = permutations
        self.random_state = random_state

    def fit(
        self,
        y: Any,
        factors: Any,
        weights: Any,
        *,
        continuous_factors: Sequence[str] | None = None,
    ) -> SPADEResult:
        """Fit SPADE to explicit continuous and categorical factor columns.

        When ``continuous_factors`` is omitted, every factor is treated as
        continuous, matching the default workflow in current reference software.
        """

        frame = coerce_factor_frame(factors)
        if frame.empty or frame.shape[1] == 0:
            raise InvalidDataError("factors must contain at least one column")
        matrix = _coerce_weight_matrix(weights, len(frame))

        if continuous_factors is None:
            continuous = tuple(frame.columns)
        else:
            continuous = tuple(str(name) for name in continuous_factors)
            unknown = sorted(set(continuous) - set(frame.columns))
            if unknown:
                raise InvalidDataError(
                    "continuous_factors contains unknown columns: "
                    + ", ".join(unknown)
                )
        if len(set(continuous)) != len(continuous):
            raise InvalidDataError("continuous_factors must not contain duplicates")
        continuous_set = set(continuous)
        categorical = tuple(name for name in frame.columns if name not in continuous_set)

        if self.permutations:
            seed_sequence = np.random.SeedSequence(self.random_state)
            child_seeds: list[int | None] = [
                int(sequence.generate_state(1)[0])
                for sequence in seed_sequence.spawn(len(frame.columns))
            ]
        else:
            child_seeds = [None] * len(frame.columns)

        results: dict[str, Any] = {}
        for index, name in enumerate(frame.columns):
            if name in continuous_set:
                results[name] = multilevel_spatial_determinant(
                    y,
                    frame[name],
                    matrix,
                    n_strata=self.n_strata,
                    method=self.method,
                    missing=self.missing,
                    min_stratum_size=self.min_stratum_size,
                    allow_islands=self.allow_islands,
                    denominator_tolerance=self.denominator_tolerance,
                    invalid=self.invalid,
                    permutations=self.permutations,
                    random_state=child_seeds[index],
                )
            else:
                results[name] = power_spatial_determinant(
                    y,
                    frame[name],
                    matrix,
                    missing=self.missing,
                    min_stratum_size=self.min_stratum_size,
                    allow_islands=self.allow_islands,
                    permutations=self.permutations,
                    random_state=child_seeds[index],
                )

        return SPADEResult(
            factors=results,
            continuous_factors=continuous,
            categorical_factors=categorical,
            weight_shape=(int(matrix.shape[0]), int(matrix.shape[1])),
        )


def spade(
    y: Any,
    factors: Any,
    weights: Any,
    *,
    continuous_factors: Sequence[str] | None = None,
    n_strata: Iterable[int] = range(3, 9),
    method: str = "quantile",
    missing: MissingPolicy = "drop",
    min_stratum_size: int = 2,
    allow_islands: bool = False,
    denominator_tolerance: float = 1e-12,
    invalid: str = "omit",
    permutations: int = 0,
    random_state: int | None = None,
) -> SPADEResult:
    """Functional interface to :class:`SPADE`."""

    return SPADE(
        n_strata=n_strata,
        method=method,
        missing=missing,
        min_stratum_size=min_stratum_size,
        allow_islands=allow_islands,
        denominator_tolerance=denominator_tolerance,
        invalid=invalid,
        permutations=permutations,
        random_state=random_state,
    ).fit(
        y,
        factors,
        weights,
        continuous_factors=continuous_factors,
    )


__all__ = [
    "SPADE",
    "SPADEResult",
    "compensated_spatial_determinant",
    "multilevel_spatial_determinant",
    "power_spatial_determinant",
    "spade",
]
