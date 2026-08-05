"""Information-consistency measures for spatially stratified heterogeneity."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Any, Literal

import numpy as np
import pandas as pd

from pygeohet.exceptions import InvalidDataError, MissingDataError, SmallStratumError
from pygeohet.models.information_results import (
    ContinuousInformationConsistencyResult,
    ContinuousStratumContribution,
    InformationConsistencyFactorResult,
    InformationTargetKind,
    NominalInformationConsistencyResult,
    NominalJointCount,
)
from pygeohet.validation import MissingPolicy, coerce_factor_frame

HistogramMethod = Literal[
    "sturges",
    "square_root",
    "rice",
    "scott",
    "freedman_diaconis",
]
BinSpecification = HistogramMethod | int | Sequence[float]


@dataclass(frozen=True)
class _PreparedInformationData:
    target: np.ndarray
    factors: pd.DataFrame
    used_indices: np.ndarray
    dropped_count: int
    total_length: int


def _validate_permutations(permutations: int) -> int:
    if isinstance(permutations, bool) or not isinstance(
        permutations, (int, np.integer)
    ):
        raise ValueError("permutations must be a nonnegative integer")
    count = int(permutations)
    if count < 0:
        raise ValueError("permutations must be a nonnegative integer")
    return count


def _validate_minimum(min_stratum_size: int) -> int:
    if isinstance(min_stratum_size, bool) or not isinstance(
        min_stratum_size, (int, np.integer)
    ):
        raise ValueError("min_stratum_size must be a positive integer")
    minimum = int(min_stratum_size)
    if minimum < 1:
        raise ValueError("min_stratum_size must be a positive integer")
    return minimum


def _validate_hashable(values: np.ndarray, *, role: str) -> None:
    for value in values:
        try:
            hash(value)
        except TypeError as exc:
            raise InvalidDataError(f"{role} labels must be hashable") from exc


def _prepare_information_data(
    target: Any,
    factors: Any,
    *,
    target_kind: InformationTargetKind,
    missing: MissingPolicy,
) -> _PreparedInformationData:
    if target_kind not in {"nominal", "continuous"}:
        raise ValueError("target_kind must be either 'nominal' or 'continuous'")
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

    missing_mask = target_series.isna() | frame.isna().any(axis=1)
    if missing == "raise" and bool(missing_mask.any()):
        raise MissingDataError("missing values are present in target or factors")

    used = np.flatnonzero(~missing_mask.to_numpy(dtype=bool))
    if used.size < 2:
        raise InvalidDataError("at least two complete observations are required")

    target_clean = target_series.iloc[used].reset_index(drop=True)
    factors_clean = frame.iloc[used].reset_index(drop=True)

    for name in factors_clean.columns:
        values = factors_clean[name].to_numpy(dtype=object, copy=False)
        _validate_hashable(values, role=f"factor {name!r}")

    if target_kind == "continuous":
        try:
            numeric = pd.to_numeric(target_clean, errors="raise").to_numpy(dtype=float)
        except (TypeError, ValueError) as exc:
            raise InvalidDataError("continuous target must be numeric") from exc
        if not bool(np.isfinite(numeric).all()):
            raise InvalidDataError("continuous target must contain only finite values")
        if np.unique(numeric).size < 2:
            raise InvalidDataError("continuous target must contain at least two values")
        target_values = numeric
    else:
        target_values = target_clean.to_numpy(dtype=object, copy=True)
        _validate_hashable(target_values, role="target")
        if pd.Series(target_values, dtype=object).nunique(dropna=False) < 2:
            raise InvalidDataError(
                "nominal target entropy is zero because the target is constant"
            )

    return _PreparedInformationData(
        target=target_values,
        factors=factors_clean,
        used_indices=used,
        dropped_count=int(missing_mask.sum()),
        total_length=len(frame),
    )


def _validate_strata(strata: np.ndarray, min_stratum_size: int) -> None:
    counts = Counter(strata.tolist())
    if not counts:
        raise InvalidDataError("strata must not be empty")
    too_small = {
        label: count for label, count in counts.items() if count < min_stratum_size
    }
    if too_small:
        details = ", ".join(f"{label!r}: {count}" for label, count in too_small.items())
        raise SmallStratumError(
            f"strata smaller than min_stratum_size={min_stratum_size}: {details}"
        )


def _entropy(probabilities: Iterable[float]) -> float:
    values = np.asarray(tuple(probabilities), dtype=float)
    positive = values > 0.0
    if not bool(np.any(positive)):
        return 0.0
    return float(-np.sum(values[positive] * np.log(values[positive])))


def _nominal_components(
    target: np.ndarray,
    strata: np.ndarray,
    *,
    entropy_tolerance: float,
) -> tuple[
    float,
    float,
    float,
    float,
    dict[Any, float],
    dict[Any, float],
    tuple[NominalJointCount, ...],
]:
    n_observations = len(target)
    target_order = tuple(pd.unique(pd.Series(target, dtype=object)))
    stratum_order = tuple(pd.unique(pd.Series(strata, dtype=object)))

    target_counts = Counter(target.tolist())
    stratum_counts = Counter(strata.tolist())
    joint_counts = Counter(zip(strata.tolist(), target.tolist(), strict=True))

    target_probabilities = {
        label: target_counts[label] / n_observations for label in target_order
    }
    stratum_probabilities = {
        label: stratum_counts[label] / n_observations for label in stratum_order
    }
    target_entropy = _entropy(target_probabilities.values())
    if target_entropy <= entropy_tolerance:
        raise InvalidDataError(
            "nominal target entropy is zero; information consistency is undefined"
        )

    conditional_entropy = 0.0
    cells: list[NominalJointCount] = []
    for stratum in stratum_order:
        stratum_count = stratum_counts[stratum]
        conditional_values: list[float] = []
        for target_label in target_order:
            count = joint_counts[(stratum, target_label)]
            if count == 0:
                continue
            joint_probability = count / n_observations
            conditional_probability = count / stratum_count
            conditional_values.append(conditional_probability)
            cells.append(
                NominalJointCount(
                    stratum=stratum,
                    target=target_label,
                    count=count,
                    joint_probability=joint_probability,
                    conditional_probability=conditional_probability,
                )
            )
        conditional_entropy += stratum_probabilities[stratum] * _entropy(
            conditional_values
        )

    mutual_information = target_entropy - conditional_entropy
    tolerance = 64.0 * np.finfo(float).eps * max(1.0, target_entropy)
    if mutual_information < 0.0 and abs(mutual_information) <= tolerance:
        mutual_information = 0.0
    if mutual_information > target_entropy and (
        mutual_information - target_entropy <= tolerance
    ):
        mutual_information = target_entropy
    value = mutual_information / target_entropy
    value = float(np.clip(value, 0.0, 1.0))
    return (
        value,
        target_entropy,
        conditional_entropy,
        mutual_information,
        target_probabilities,
        stratum_probabilities,
        tuple(cells),
    )


def _permutation_summary(
    observed: float,
    null_values: np.ndarray,
) -> tuple[float, float, float]:
    tolerance = 64.0 * np.finfo(float).eps * max(1.0, abs(observed))
    exceedances = int(np.count_nonzero(null_values >= observed - tolerance))
    p_value = float((1 + exceedances) / (len(null_values) + 1))
    null_mean = float(np.mean(null_values))
    null_sd = float(np.std(null_values, ddof=1)) if len(null_values) > 1 else 0.0
    return p_value, null_mean, null_sd


def _nominal_result(
    target: np.ndarray,
    strata: np.ndarray,
    *,
    min_stratum_size: int,
    entropy_tolerance: float,
    permutations: int,
    random_state: int | None,
    total_length: int,
    dropped_count: int,
    used_indices: np.ndarray,
) -> NominalInformationConsistencyResult:
    _validate_strata(strata, min_stratum_size)
    (
        value,
        target_entropy,
        conditional_entropy,
        mutual_information,
        target_probabilities,
        stratum_probabilities,
        cells,
    ) = _nominal_components(
        target,
        strata,
        entropy_tolerance=entropy_tolerance,
    )

    p_value = None
    null_mean = None
    null_sd = None
    if permutations:
        rng = np.random.default_rng(random_state)
        null_values = np.empty(permutations, dtype=float)
        for index in range(permutations):
            null_values[index] = _nominal_components(
                rng.permutation(target),
                strata,
                entropy_tolerance=entropy_tolerance,
            )[0]
        p_value, null_mean, null_sd = _permutation_summary(value, null_values)

    return NominalInformationConsistencyResult(
        value=value,
        target_entropy=target_entropy,
        conditional_entropy=conditional_entropy,
        mutual_information=mutual_information,
        target_probabilities=target_probabilities,
        stratum_probabilities=stratum_probabilities,
        joint_counts=cells,
        n_observations=len(target),
        total_length=total_length,
        dropped_count=dropped_count,
        used_indices=tuple(int(index) for index in used_indices),
        p_value=p_value,
        permutations=permutations,
        null_mean=null_mean,
        null_standard_deviation=null_sd,
        random_state=random_state,
        metadata={
            "formula": "IN = I(target; strata) / H(target)",
            "equivalent_formula": "IN = 1 - H(target | strata) / H(target)",
            "logarithm": "natural logarithm used consistently",
            "permutation": "target labels shuffled relative to fixed strata",
            "p_value": "(1 + exceedances) / (B + 1)",
            "min_stratum_size": min_stratum_size,
        },
    )


def nominal_information_consistency(
    target: Any,
    strata: Any,
    *,
    missing: MissingPolicy = "drop",
    min_stratum_size: int = 2,
    entropy_tolerance: float = 1e-12,
    permutations: int = 0,
    random_state: int | None = 42,
) -> NominalInformationConsistencyResult:
    """Measure nominal SSH with normalized mutual information.

    The statistic is ``I(target; strata) / H(target)`` and therefore lies in
    ``[0, 1]``. The logarithm base cancels in the ratio; pyGeoHet uses natural
    logarithms consistently for all entropy components.
    """

    if entropy_tolerance < 0.0:
        raise ValueError("entropy_tolerance must be nonnegative")
    minimum = _validate_minimum(min_stratum_size)
    permutation_count = _validate_permutations(permutations)
    prepared = _prepare_information_data(
        target,
        {"strata": strata},
        target_kind="nominal",
        missing=missing,
    )
    strata_values = prepared.factors["strata"].to_numpy(dtype=object, copy=True)
    return _nominal_result(
        prepared.target,
        strata_values,
        min_stratum_size=minimum,
        entropy_tolerance=entropy_tolerance,
        permutations=permutation_count,
        random_state=random_state,
        total_length=prepared.total_length,
        dropped_count=prepared.dropped_count,
        used_indices=prepared.used_indices,
    )


def _canonical_histogram_method(method: str) -> HistogramMethod:
    normalized = method.strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "sturges": "sturges",
        "square_root": "square_root",
        "squareroot": "square_root",
        "sqrt": "square_root",
        "rice": "rice",
        "scott": "scott",
        "freedman_diaconis": "freedman_diaconis",
        "freedmandiaconis": "freedman_diaconis",
        "fd": "freedman_diaconis",
    }
    try:
        return aliases[normalized]  # type: ignore[return-value]
    except KeyError as exc:
        raise ValueError(f"unknown histogram method: {method!r}") from exc


def _automatic_bin_count(target: np.ndarray, method: HistogramMethod) -> int:
    n_observations = len(target)
    data_range = float(np.max(target) - np.min(target))
    if data_range <= 0.0:
        raise InvalidDataError("continuous target range must be positive")

    if method == "sturges":
        count = int(np.ceil(np.log2(n_observations) + 1.0))
    elif method == "square_root":
        count = int(np.ceil(np.sqrt(n_observations)))
    elif method == "rice":
        count = int(np.ceil(2.0 * np.cbrt(n_observations)))
    elif method == "scott":
        standard_deviation = float(np.std(target, ddof=0))
        width = 3.49 * standard_deviation / np.cbrt(n_observations)
        count = int(np.ceil(data_range / width)) if width > 0.0 else 0
    else:
        q1, q3 = np.quantile(target, [0.25, 0.75])
        width = 2.0 * float(q3 - q1) / np.cbrt(n_observations)
        count = int(np.ceil(data_range / width)) if width > 0.0 else 0

    if count < 2:
        count = int(np.ceil(np.log2(n_observations) + 1.0))
    return max(2, count)


def _resolve_bin_edges(
    target: np.ndarray,
    bins: BinSpecification,
) -> tuple[np.ndarray, str]:
    minimum = float(np.min(target))
    maximum = float(np.max(target))
    if minimum == maximum:
        raise InvalidDataError("continuous target range must be positive")

    if isinstance(bins, str):
        method = _canonical_histogram_method(bins)
        bin_count = _automatic_bin_count(target, method)
        edges = np.linspace(minimum, maximum, bin_count + 1, dtype=float)
        label = method
    elif isinstance(bins, bool):
        raise ValueError("bins must be a method name, integer or edge sequence")
    elif isinstance(bins, (int, np.integer)):
        bin_count = int(bins)
        if bin_count < 2:
            raise ValueError("integer bins must be at least 2")
        edges = np.linspace(minimum, maximum, bin_count + 1, dtype=float)
        label = f"explicit_count:{bin_count}"
    else:
        try:
            edges = np.asarray(tuple(bins), dtype=float)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "bins must be a method name, integer or edge sequence"
            ) from exc
        if edges.ndim != 1 or edges.size < 3:
            raise ValueError("explicit bin edges must contain at least three values")
        if not bool(np.isfinite(edges).all()):
            raise ValueError("explicit bin edges must be finite")
        if not bool(np.all(np.diff(edges) > 0.0)):
            raise ValueError("explicit bin edges must be strictly increasing")
        if edges[0] > minimum or edges[-1] < maximum:
            raise ValueError("explicit bin edges must cover the complete target range")
        edges = edges.copy()
        label = "explicit_edges"

    if not bool(np.all(np.diff(edges) > 0.0)):
        raise InvalidDataError("histogram bin edges are not strictly increasing")
    return edges, label


def _continuous_components(
    target: np.ndarray,
    strata: np.ndarray,
    edges: np.ndarray,
) -> tuple[
    float,
    tuple[float, ...],
    tuple[ContinuousStratumContribution, ...],
]:
    n_observations = len(target)
    global_counts, _ = np.histogram(target, bins=edges)
    if int(np.sum(global_counts)) != n_observations:
        raise InvalidDataError("histogram edges do not cover the complete target")
    global_probabilities = global_counts.astype(float) / n_observations

    contributions: list[ContinuousStratumContribution] = []
    value = 0.0
    stratum_order = tuple(pd.unique(pd.Series(strata, dtype=object)))
    for stratum in stratum_order:
        mask = strata == stratum
        stratum_target = target[mask]
        count = len(stratum_target)
        probability = count / n_observations
        counts, _ = np.histogram(stratum_target, bins=edges)
        probabilities = counts.astype(float) / count
        positive = probabilities > 0.0
        if bool(np.any(global_probabilities[positive] <= 0.0)):
            raise InvalidDataError(
                "global histogram has zero mass where a stratum has positive mass"
            )
        kl_divergence = float(
            np.sum(
                probabilities[positive]
                * np.log(probabilities[positive] / global_probabilities[positive])
            )
        )
        if kl_divergence < 0.0 and abs(kl_divergence) <= 1e-14:
            kl_divergence = 0.0
        transformed = float(np.arctan(kl_divergence) / (np.pi / 2.0))
        weighted = probability * transformed
        value += weighted
        contributions.append(
            ContinuousStratumContribution(
                stratum=stratum,
                count=count,
                probability=probability,
                kl_divergence=kl_divergence,
                transformed_divergence=transformed,
                weighted_contribution=weighted,
                histogram_probabilities=tuple(float(item) for item in probabilities),
            )
        )

    return (
        float(np.clip(value, 0.0, 1.0)),
        tuple(float(item) for item in global_probabilities),
        tuple(contributions),
    )


def _continuous_result(
    target: np.ndarray,
    strata: np.ndarray,
    *,
    edges: np.ndarray,
    bin_method: str,
    min_stratum_size: int,
    permutations: int,
    random_state: int | None,
    total_length: int,
    dropped_count: int,
    used_indices: np.ndarray,
) -> ContinuousInformationConsistencyResult:
    _validate_strata(strata, min_stratum_size)
    value, global_probabilities, contributions = _continuous_components(
        target,
        strata,
        edges,
    )

    p_value = None
    null_mean = None
    null_sd = None
    if permutations:
        rng = np.random.default_rng(random_state)
        null_values = np.empty(permutations, dtype=float)
        for index in range(permutations):
            null_values[index] = _continuous_components(
                rng.permutation(target),
                strata,
                edges,
            )[0]
        p_value, null_mean, null_sd = _permutation_summary(value, null_values)

    return ContinuousInformationConsistencyResult(
        value=value,
        bin_edges=tuple(float(edge) for edge in edges),
        bin_method=bin_method,
        global_histogram_probabilities=global_probabilities,
        contributions=contributions,
        n_observations=len(target),
        total_length=total_length,
        dropped_count=dropped_count,
        used_indices=tuple(int(index) for index in used_indices),
        p_value=p_value,
        permutations=permutations,
        null_mean=null_mean,
        null_standard_deviation=null_sd,
        random_state=random_state,
        metadata={
            "formula": "IC = sum_h p_h * atan(KL(P_h || P)) / (pi / 2)",
            "density_estimator": "shared-support histogram probabilities",
            "bin_edges": "one common edge sequence from the complete target",
            "zero_handling": "terms with P_h=0 are omitted; P>0 wherever P_h>0",
            "permutation": "target values shuffled relative to fixed strata and edges",
            "p_value": "(1 + exceedances) / (B + 1)",
            "min_stratum_size": min_stratum_size,
        },
    )


def continuous_information_consistency(
    target: Any,
    strata: Any,
    *,
    bins: BinSpecification = "sturges",
    missing: MissingPolicy = "drop",
    min_stratum_size: int = 2,
    permutations: int = 0,
    random_state: int | None = 42,
) -> ContinuousInformationConsistencyResult:
    """Measure continuous SSH with weighted transformed KL divergence.

    All stratum and global histograms use one common support and one shared edge
    sequence, making every relative-entropy contribution directly comparable.
    """

    minimum = _validate_minimum(min_stratum_size)
    permutation_count = _validate_permutations(permutations)
    prepared = _prepare_information_data(
        target,
        {"strata": strata},
        target_kind="continuous",
        missing=missing,
    )
    strata_values = prepared.factors["strata"].to_numpy(dtype=object, copy=True)
    edges, method = _resolve_bin_edges(prepared.target.astype(float), bins)
    return _continuous_result(
        prepared.target.astype(float),
        strata_values,
        edges=edges,
        bin_method=method,
        min_stratum_size=minimum,
        permutations=permutation_count,
        random_state=random_state,
        total_length=prepared.total_length,
        dropped_count=prepared.dropped_count,
        used_indices=prepared.used_indices,
    )


class InformationConsistency:
    """Evaluate multiple stratifications on one common information sample."""

    def __init__(
        self,
        *,
        target_kind: InformationTargetKind,
        bins: BinSpecification = "sturges",
        missing: MissingPolicy = "drop",
        min_stratum_size: int = 2,
        entropy_tolerance: float = 1e-12,
        permutations: int = 0,
        random_state: int | None = 42,
    ) -> None:
        if target_kind not in {"nominal", "continuous"}:
            raise ValueError("target_kind must be either 'nominal' or 'continuous'")
        if entropy_tolerance < 0.0:
            raise ValueError("entropy_tolerance must be nonnegative")
        self.target_kind = target_kind
        self.bins = bins
        self.missing = missing
        self.min_stratum_size = min_stratum_size
        self.entropy_tolerance = entropy_tolerance
        self.permutations = permutations
        self.random_state = random_state

    def fit(self, target: Any, factors: Any) -> InformationConsistencyFactorResult:
        """Evaluate every factor using one joint complete-case sample."""

        minimum = _validate_minimum(self.min_stratum_size)
        permutation_count = _validate_permutations(self.permutations)
        prepared = _prepare_information_data(
            target,
            factors,
            target_kind=self.target_kind,
            missing=self.missing,
        )

        results: dict[
            str,
            NominalInformationConsistencyResult
            | ContinuousInformationConsistencyResult,
        ] = {}
        if self.target_kind == "continuous":
            continuous_target = prepared.target.astype(float)
            edges, method = _resolve_bin_edges(continuous_target, self.bins)
            for name in prepared.factors.columns:
                strata = prepared.factors[name].to_numpy(dtype=object, copy=True)
                results[name] = _continuous_result(
                    continuous_target,
                    strata,
                    edges=edges,
                    bin_method=method,
                    min_stratum_size=minimum,
                    permutations=permutation_count,
                    random_state=self.random_state,
                    total_length=prepared.total_length,
                    dropped_count=prepared.dropped_count,
                    used_indices=prepared.used_indices,
                )
        else:
            for name in prepared.factors.columns:
                strata = prepared.factors[name].to_numpy(dtype=object, copy=True)
                results[name] = _nominal_result(
                    prepared.target,
                    strata,
                    min_stratum_size=minimum,
                    entropy_tolerance=self.entropy_tolerance,
                    permutations=permutation_count,
                    random_state=self.random_state,
                    total_length=prepared.total_length,
                    dropped_count=prepared.dropped_count,
                    used_indices=prepared.used_indices,
                )

        return InformationConsistencyFactorResult(
            target_kind=self.target_kind,
            factors=results,
            n_observations=len(prepared.target),
            total_length=prepared.total_length,
            dropped_count=prepared.dropped_count,
            used_indices=tuple(int(index) for index in prepared.used_indices),
        )


def information_consistency(
    target: Any,
    factors: Any,
    *,
    target_kind: InformationTargetKind,
    **kwargs: Any,
) -> InformationConsistencyFactorResult:
    """Functional interface to :class:`InformationConsistency`."""

    return InformationConsistency(target_kind=target_kind, **kwargs).fit(
        target,
        factors,
    )


__all__ = [
    "InformationConsistency",
    "InformationConsistencyFactorResult",
    "continuous_information_consistency",
    "information_consistency",
    "nominal_information_consistency",
]
