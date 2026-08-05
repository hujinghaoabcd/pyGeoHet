"""Spatial rough set-based geographical detectors for nominal targets."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from itertools import combinations
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

from pygeohet.exceptions import InvalidDataError, MissingDataError
from pygeohet.models.srsgd_results import (
    SRSEcologicalComparisonResult,
    SRSEcologicalDetectorResult,
    SRSFactorDetectorResult,
    SRSGeoDetectorResult,
    SRSInteractionComparisonResult,
    SRSInteractionDetectorResult,
    SpatialHeterogeneityChange,
    SpatialRoughSetResult,
)
from pygeohet.validation import MissingPolicy, coerce_factor_frame


@dataclass(frozen=True)
class _PreparedSRSData:
    target: np.ndarray
    factors: pd.DataFrame
    adjacency: np.ndarray
    used_indices: np.ndarray
    dropped_count: int
    total_length: int
    island_indices: np.ndarray
    adjacency_symmetric: bool


def _coerce_adjacency(adjacency: Any, n_observations: int) -> np.ndarray:
    try:
        matrix = np.asarray(adjacency, dtype=float)
    except (TypeError, ValueError) as exc:
        raise InvalidDataError("adjacency must be a numeric square matrix") from exc
    if matrix.ndim != 2 or matrix.shape != (n_observations, n_observations):
        raise InvalidDataError(
            "adjacency must have shape "
            f"({n_observations}, {n_observations})"
        )
    if not bool(np.isfinite(matrix).all()):
        raise InvalidDataError("adjacency must contain only finite values")
    if bool(np.any((matrix != 0.0) & (matrix != 1.0))):
        raise InvalidDataError("adjacency must be binary with values 0 or 1")
    binary = matrix.astype(bool, copy=True)
    np.fill_diagonal(binary, False)
    return binary


def _validate_discrete_series(series: pd.Series, *, role: str) -> None:
    values = series.to_numpy(copy=False)
    for value in values:
        try:
            hash(value)
        except TypeError as exc:
            raise InvalidDataError(f"{role} labels must be hashable") from exc

    if pd.api.types.is_numeric_dtype(series.dtype):
        numeric = pd.to_numeric(series, errors="raise").to_numpy(dtype=float)
        if not bool(np.isfinite(numeric).all()):
            raise InvalidDataError(f"{role} must contain only finite labels")
        if not bool(np.equal(numeric, np.floor(numeric)).all()):
            raise InvalidDataError(
                f"{role} must be nominal or deliberately discretized; "
                "noninteger floating values are not accepted"
            )

    unique_count = int(series.nunique(dropna=False))
    if unique_count < 2:
        raise InvalidDataError(f"{role} must contain at least two categories")
    if unique_count == len(series) and len(series) > 1:
        raise InvalidDataError(
            f"{role} contains one unique label per observation; "
            "discretize it or confirm that identifiers were not supplied"
        )


def _prepare_srs_data(
    target: Any,
    factors: Any,
    adjacency: Any,
    *,
    missing: MissingPolicy,
    allow_islands: bool,
    require_symmetric: bool,
) -> _PreparedSRSData:
    if missing not in {"drop", "raise"}:
        raise ValueError("missing must be either 'drop' or 'raise'")

    frame = coerce_factor_frame(factors)
    if frame.empty or frame.shape[1] == 0:
        raise InvalidDataError("factors must contain at least one column")

    target_series = pd.Series(target, copy=False, name="target").reset_index(drop=True)
    if target_series.ndim != 1:
        raise InvalidDataError("target must be one-dimensional")
    if len(target_series) != len(frame):
        raise InvalidDataError("target and factors must have equal length")
    if len(target_series) == 0:
        raise InvalidDataError("target and factors must not be empty")

    matrix = _coerce_adjacency(adjacency, len(frame))
    missing_mask = target_series.isna() | frame.isna().any(axis=1)
    if missing == "raise" and bool(missing_mask.any()):
        raise MissingDataError("missing values are present in target or factors")

    used = np.flatnonzero(~missing_mask.to_numpy(dtype=bool))
    if used.size < 2:
        raise InvalidDataError("at least two complete observations are required")
    target_clean = target_series.iloc[used].reset_index(drop=True)
    factors_clean = frame.iloc[used].reset_index(drop=True)
    matrix_clean = matrix[np.ix_(used, used)].copy()

    _validate_discrete_series(target_clean, role="target")
    for name in factors_clean.columns:
        _validate_discrete_series(factors_clean[name], role=f"factor {name!r}")

    symmetric = bool(np.array_equal(matrix_clean, matrix_clean.T))
    if require_symmetric and not symmetric:
        raise InvalidDataError(
            "adjacency must be symmetric for the primary SRS-GD estimand"
        )

    islands_clean = np.flatnonzero(matrix_clean.sum(axis=1) == 0)
    islands_original = used[islands_clean]
    if islands_clean.size and not allow_islands:
        listed = ", ".join(str(int(index)) for index in islands_original[:10])
        suffix = "" if islands_original.size <= 10 else ", ..."
        raise InvalidDataError(
            "SRS-GD found observations without neighbours after missing-value "
            f"handling: {listed}{suffix}; pass allow_islands=True only when "
            "self-only local regions are scientifically intended"
        )

    return _PreparedSRSData(
        target=target_clean.to_numpy(dtype=object, copy=True),
        factors=factors_clean,
        adjacency=matrix_clean,
        used_indices=used,
        dropped_count=int(missing_mask.sum()),
        total_length=len(frame),
        island_indices=islands_original,
        adjacency_symmetric=symmetric,
    )


def _test_sample(
    n_observations: int,
    sample_size: int | None,
    random_state: int | None,
) -> np.ndarray:
    if sample_size is None:
        return np.arange(n_observations, dtype=int)
    if isinstance(sample_size, bool) or not isinstance(sample_size, (int, np.integer)):
        raise ValueError("sample_size must be an integer or None")
    size = int(sample_size)
    if size < 2:
        raise ValueError("sample_size must be at least 2")
    if size > n_observations:
        raise ValueError("sample_size cannot exceed the complete observation count")
    rng = np.random.default_rng(random_state)
    return np.sort(rng.choice(n_observations, size=size, replace=False))


def _one_sample_test(values: np.ndarray, *, alternative: str) -> tuple[float, float]:
    if values.size < 2:
        raise InvalidDataError("at least two local values are required for inference")
    if bool(np.allclose(values, 0.0, rtol=0.0, atol=1e-15)):
        return 0.0, 1.0
    if bool(np.allclose(values, values[0], rtol=0.0, atol=1e-15)):
        if alternative == "greater":
            return (float("inf"), 0.0) if values[0] > 0.0 else (float("-inf"), 1.0)
        return (float("inf") if values[0] > 0.0 else float("-inf"), 0.0)
    result = stats.ttest_1samp(values, popmean=0.0, alternative=alternative)
    return float(result.statistic), float(result.pvalue)


def _local_rough_set_values(
    target: np.ndarray,
    factor_frame: pd.DataFrame,
    adjacency: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    n_observations = len(target)
    quality = np.empty(n_observations, dtype=float)
    region_sizes = np.empty(n_observations, dtype=int)
    positive_sizes = np.empty(n_observations, dtype=int)
    factor_values = factor_frame.to_numpy(dtype=object, copy=False)

    for focal in range(n_observations):
        neighbours = np.flatnonzero(adjacency[focal])
        region = np.concatenate((np.asarray([focal], dtype=int), neighbours))
        region_sizes[focal] = len(region)

        classes: dict[tuple[Any, ...], list[int]] = defaultdict(list)
        for index in region:
            classes[tuple(factor_values[index])].append(int(index))

        positive_count = 0
        for indices in classes.values():
            decisions = {target[index] for index in indices}
            if len(decisions) == 1:
                positive_count += len(indices)
        positive_sizes[focal] = positive_count
        quality[focal] = positive_count / len(region)

    return quality, region_sizes, positive_sizes


def _expand_numeric(
    values: np.ndarray,
    used_indices: np.ndarray,
    total_length: int,
) -> tuple[float | None, ...]:
    expanded: list[float | None] = [None] * total_length
    for clean_index, original_index in enumerate(used_indices):
        expanded[int(original_index)] = float(values[clean_index])
    return tuple(expanded)


def _expand_integer(
    values: np.ndarray,
    used_indices: np.ndarray,
    total_length: int,
) -> tuple[int | None, ...]:
    expanded: list[int | None] = [None] * total_length
    for clean_index, original_index in enumerate(used_indices):
        expanded[int(original_index)] = int(values[clean_index])
    return tuple(expanded)


def _measure_prepared(
    prepared: _PreparedSRSData,
    feature_names: Sequence[str],
    *,
    sample_size: int | None,
    random_state: int | None,
) -> SpatialRoughSetResult:
    names = tuple(str(name) for name in feature_names)
    if not names:
        raise InvalidDataError("at least one feature is required")
    unknown = [name for name in names if name not in prepared.factors]
    if unknown:
        raise KeyError(unknown[0])
    if len(set(names)) != len(names):
        raise InvalidDataError("feature_names must not contain duplicates")

    local, region_sizes, positive_sizes = _local_rough_set_values(
        prepared.target,
        prepared.factors.loc[:, list(names)],
        prepared.adjacency,
    )
    average = float(np.mean(local))
    local_sum = float(np.sum(local))
    if local_sum <= 0.0:
        entropy = None
        normalized_entropy = None
    else:
        probabilities = local / local_sum
        positive = probabilities > 0.0
        entropy = float(-np.sum(probabilities[positive] * np.log2(probabilities[positive])))
        maximum = float(np.log2(len(local)))
        normalized_entropy = entropy / maximum if maximum > 0.0 else None

    sampled_clean = _test_sample(len(local), sample_size, random_state)
    t_statistic, p_value = _one_sample_test(
        local[sampled_clean],
        alternative="greater",
    )
    sampled_original = prepared.used_indices[sampled_clean]

    return SpatialRoughSetResult(
        feature_names=names,
        average_local_power=average,
        spatial_entropy=entropy,
        normalized_spatial_entropy=normalized_entropy,
        local_quality=_expand_numeric(
            local,
            prepared.used_indices,
            prepared.total_length,
        ),
        region_size=_expand_integer(
            region_sizes,
            prepared.used_indices,
            prepared.total_length,
        ),
        positive_region_size=_expand_integer(
            positive_sizes,
            prepared.used_indices,
            prepared.total_length,
        ),
        n_observations=len(local),
        total_length=prepared.total_length,
        dropped_count=prepared.dropped_count,
        used_indices=tuple(int(index) for index in prepared.used_indices),
        island_indices=tuple(int(index) for index in prepared.island_indices),
        adjacency_symmetric=prepared.adjacency_symmetric,
        t_statistic=t_statistic,
        p_value=p_value,
        test_sample_indices=tuple(int(index) for index in sampled_original),
        random_state=random_state,
        metadata={
            "local_region": "focal object union binary neighbours",
            "indiscernibility": "exact feature tuple within each local region",
            "positive_region": "local equivalence classes with one target category",
            "formula_D": "mean(local approximation quality)",
            "formula_SE": "Shannon entropy of normalized local quality",
            "inference": "one-sample Student test against zero",
            "sample_size": len(sampled_clean),
        },
    )


def spatial_rough_set_measure(
    target: Any,
    features: Any,
    adjacency: Any,
    *,
    missing: MissingPolicy = "drop",
    allow_islands: bool = False,
    require_symmetric: bool = True,
    sample_size: int | None = None,
    random_state: int | None = 42,
) -> SpatialRoughSetResult:
    """Calculate paper-aligned local quality, average power and spatial entropy.

    The target and features must already be nominal or deliberately discretized.
    The supplied binary adjacency matrix does not need self links because the focal
    object is added to every local region according to the paper definition.
    """

    frame = coerce_factor_frame(features)
    prepared = _prepare_srs_data(
        target,
        frame,
        adjacency,
        missing=missing,
        allow_islands=allow_islands,
        require_symmetric=require_symmetric,
    )
    return _measure_prepared(
        prepared,
        tuple(frame.columns),
        sample_size=sample_size,
        random_state=random_state,
    )


def srs_factor_detector(
    target: Any,
    factors: Any,
    adjacency: Any,
    *,
    missing: MissingPolicy = "drop",
    allow_islands: bool = False,
    require_symmetric: bool = True,
    sample_size: int | None = None,
    random_state: int | None = 42,
) -> SRSFactorDetectorResult:
    """Evaluate every supplied feature with SRSF on one common sample."""

    frame = coerce_factor_frame(factors)
    prepared = _prepare_srs_data(
        target,
        frame,
        adjacency,
        missing=missing,
        allow_islands=allow_islands,
        require_symmetric=require_symmetric,
    )
    results = {
        name: _measure_prepared(
            prepared,
            (name,),
            sample_size=sample_size,
            random_state=random_state,
        )
        for name in frame.columns
    }
    return SRSFactorDetectorResult(results)


def _result_local_values(result: SpatialRoughSetResult) -> np.ndarray:
    return np.asarray(
        [result.local_quality[index] for index in result.used_indices],
        dtype=float,
    )


def _paired_comparison(
    first: np.ndarray,
    second: np.ndarray,
    sample: np.ndarray,
    *,
    alternative: str,
) -> tuple[float, float]:
    if first.shape != second.shape:
        raise InvalidDataError("paired local-quality vectors must have equal shape")
    return _one_sample_test(first[sample] - second[sample], alternative=alternative)


def srs_ecological_detector(
    target: Any,
    factors: Any,
    adjacency: Any,
    *,
    alpha: float = 0.05,
    missing: MissingPolicy = "drop",
    allow_islands: bool = False,
    require_symmetric: bool = True,
    sample_size: int | None = None,
    random_state: int | None = 42,
) -> SRSEcologicalDetectorResult:
    """Compare average local explanatory power with paired Student tests."""

    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie strictly between 0 and 1")
    frame = coerce_factor_frame(factors)
    if frame.shape[1] < 2:
        raise InvalidDataError("ecological detection requires at least two factors")
    prepared = _prepare_srs_data(
        target,
        frame,
        adjacency,
        missing=missing,
        allow_islands=allow_islands,
        require_symmetric=require_symmetric,
    )
    measures = {
        name: _measure_prepared(
            prepared,
            (name,),
            sample_size=sample_size,
            random_state=random_state,
        )
        for name in frame.columns
    }
    sampled_clean = _test_sample(len(prepared.target), sample_size, random_state)
    sampled_original = tuple(
        int(index) for index in prepared.used_indices[sampled_clean]
    )

    comparisons_out: list[SRSEcologicalComparisonResult] = []
    for name_1, name_2 in combinations(frame.columns, 2):
        result_1 = measures[name_1]
        result_2 = measures[name_2]
        local_1 = _result_local_values(result_1)
        local_2 = _result_local_values(result_2)
        t_statistic, p_value = _paired_comparison(
            local_1,
            local_2,
            sampled_clean,
            alternative="two-sided",
        )
        difference = result_1.D - result_2.D
        significant = p_value < alpha
        if not significant or abs(difference) <= 1e-15:
            more_explanatory = None
        else:
            more_explanatory = (name_1,) if difference > 0.0 else (name_2,)
        comparisons_out.append(
            SRSEcologicalComparisonResult(
                feature_1=(name_1,),
                feature_2=(name_2,),
                result_1=result_1,
                result_2=result_2,
                difference=difference,
                t_statistic=t_statistic,
                p_value=p_value,
                significant=significant,
                more_explanatory=more_explanatory,
                sample_indices=sampled_original,
            )
        )
    return SRSEcologicalDetectorResult(tuple(comparisons_out))


def _entropy_change(
    baseline: float | None,
    joint: float | None,
    tolerance: float,
) -> tuple[float | None, SpatialHeterogeneityChange | None]:
    if baseline is None or joint is None:
        return None, None
    change = joint - baseline
    if abs(change) <= tolerance:
        state: SpatialHeterogeneityChange = "unchanged"
    elif change > 0.0:
        state = "decreased"
    else:
        state = "increased"
    return change, state


def srs_interaction_detector(
    target: Any,
    factors: Any,
    adjacency: Any,
    *,
    baseline: str | None = None,
    alpha: float = 0.05,
    tolerance: float = 1e-12,
    missing: MissingPolicy = "drop",
    allow_islands: bool = False,
    require_symmetric: bool = True,
    sample_size: int | None = None,
    random_state: int | None = 42,
) -> SRSInteractionDetectorResult:
    """Measure nonnegative explanatory-power gains from exact feature unions."""

    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie strictly between 0 and 1")
    if tolerance < 0.0:
        raise ValueError("tolerance must be nonnegative")
    frame = coerce_factor_frame(factors)
    if frame.shape[1] < 2:
        raise InvalidDataError("interaction detection requires at least two factors")
    if baseline is not None and baseline not in frame:
        raise KeyError(baseline)

    prepared = _prepare_srs_data(
        target,
        frame,
        adjacency,
        missing=missing,
        allow_islands=allow_islands,
        require_symmetric=require_symmetric,
    )
    sampled_clean = _test_sample(len(prepared.target), sample_size, random_state)
    sampled_original = tuple(
        int(index) for index in prepared.used_indices[sampled_clean]
    )

    if baseline is None:
        pairs = list(combinations(frame.columns, 2))
    else:
        pairs = [(baseline, name) for name in frame.columns if name != baseline]

    comparisons_out: list[SRSInteractionComparisonResult] = []
    for base_name, added_name in pairs:
        base_result = _measure_prepared(
            prepared,
            (base_name,),
            sample_size=sample_size,
            random_state=random_state,
        )
        joint_result = _measure_prepared(
            prepared,
            (base_name, added_name),
            sample_size=sample_size,
            random_state=random_state,
        )
        base_local = _result_local_values(base_result)
        joint_local = _result_local_values(joint_result)
        differences = joint_local - base_local
        minimum_gain = float(np.min(differences))
        if minimum_gain < -tolerance:
            raise InvalidDataError(
                "exact feature refinement violated SRS monotonicity by "
                f"{minimum_gain:.6g}"
            )
        t_statistic, p_value = _one_sample_test(
            differences[sampled_clean],
            alternative="greater",
        )
        power_gain = joint_result.D - base_result.D
        if power_gain < -tolerance:
            raise InvalidDataError("average SRS interaction gain is negative")
        entropy_delta, heterogeneity_state = _entropy_change(
            base_result.SE,
            joint_result.SE,
            tolerance,
        )
        comparisons_out.append(
            SRSInteractionComparisonResult(
                baseline_features=(base_name,),
                added_features=(added_name,),
                joint_features=(base_name, added_name),
                baseline_result=base_result,
                joint_result=joint_result,
                power_gain=max(0.0, power_gain),
                entropy_change=entropy_delta,
                heterogeneity_change=heterogeneity_state,
                t_statistic=t_statistic,
                p_value=p_value,
                significant_gain=p_value < alpha,
                sample_indices=sampled_original,
            )
        )
    return SRSInteractionDetectorResult(tuple(comparisons_out))


class SRSGeoDetector:
    """Integrated factor, ecological and interaction SRS-GD workflow."""

    def __init__(
        self,
        *,
        baseline: str | None = None,
        alpha: float = 0.05,
        tolerance: float = 1e-12,
        missing: MissingPolicy = "drop",
        allow_islands: bool = False,
        require_symmetric: bool = True,
        sample_size: int | None = None,
        random_state: int | None = 42,
    ) -> None:
        self.baseline = baseline
        self.alpha = alpha
        self.tolerance = tolerance
        self.missing = missing
        self.allow_islands = allow_islands
        self.require_symmetric = require_symmetric
        self.sample_size = sample_size
        self.random_state = random_state

    def fit(self, target: Any, factors: Any, adjacency: Any) -> SRSGeoDetectorResult:
        """Run all three SRS-GD detector families on the supplied inputs."""

        common: dict[str, Any] = {
            "missing": self.missing,
            "allow_islands": self.allow_islands,
            "require_symmetric": self.require_symmetric,
            "sample_size": self.sample_size,
            "random_state": self.random_state,
        }
        factor = srs_factor_detector(target, factors, adjacency, **common)
        ecological = srs_ecological_detector(
            target,
            factors,
            adjacency,
            alpha=self.alpha,
            **common,
        )
        interaction = srs_interaction_detector(
            target,
            factors,
            adjacency,
            baseline=self.baseline,
            alpha=self.alpha,
            tolerance=self.tolerance,
            **common,
        )
        return SRSGeoDetectorResult(
            factor=factor,
            ecological=ecological,
            interaction=interaction,
        )


def srsgd(
    target: Any,
    factors: Any,
    adjacency: Any,
    **kwargs: Any,
) -> SRSGeoDetectorResult:
    """Functional interface to :class:`SRSGeoDetector`."""

    return SRSGeoDetector(**kwargs).fit(target, factors, adjacency)


__all__ = [
    "SRSGeoDetector",
    "SRSGeoDetectorResult",
    "SpatialRoughSetResult",
    "spatial_rough_set_measure",
    "srs_ecological_detector",
    "srs_factor_detector",
    "srs_interaction_detector",
    "srsgd",
]
