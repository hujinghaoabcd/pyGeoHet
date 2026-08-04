from itertools import combinations

import numpy as np
import pandas as pd
import pytest

from pygeohet.core.qstat import q_statistic
from pygeohet.exceptions import InvalidDataError, MissingDataError
from pygeohet.models.robust import (
    RGD,
    RID,
    optimize_robust_discretization,
    robust_discretize,
)


def _brute_force(
    y: np.ndarray,
    x: np.ndarray,
    n_strata: int,
    min_size: int = 2,
) -> tuple[float, tuple[int, ...]]:
    order = np.argsort(x, kind="mergesort")
    x_sorted = x[order]
    y_sorted = y[order]
    positions = [
        index
        for index in range(1, len(x_sorted))
        if x_sorted[index - 1] < x_sorted[index]
    ]
    best: tuple[float, tuple[int, ...]] | None = None
    for cuts in combinations(positions, n_strata - 1):
        boundaries = (0, *cuts, len(x_sorted))
        if any(
            stop - start < min_size
            for start, stop in zip(boundaries[:-1], boundaries[1:])
        ):
            continue
        within_ss = 0.0
        for start, stop in zip(boundaries[:-1], boundaries[1:]):
            values = y_sorted[start:stop]
            within_ss += float(np.sum((values - np.mean(values)) ** 2))
        if (
            best is None
            or within_ss < best[0] - 1e-12
            or (abs(within_ss - best[0]) <= 1e-12 and cuts < best[1])
        ):
            best = (within_ss, cuts)
    assert best is not None
    return best


def test_robust_discretization_matches_brute_force() -> None:
    x = np.arange(12, dtype=float)
    y = np.asarray([0, 0, 0, 1, 1, 1, 8, 8, 8, 9, 9, 9], dtype=float)
    _, cuts = _brute_force(y, x, 4)

    result = robust_discretize(y, x, n_strata=4)

    assert result.break_positions == cuts
    assert result.cut_points == tuple(x[index] for index in cuts)
    assert result.b_value == pytest.approx(q_statistic(y, result.labels).q)


def test_duplicate_explanatory_values_are_never_split() -> None:
    x = np.repeat(np.arange(6, dtype=float), 2)
    y = np.repeat([0.0, 0.0, 5.0, 5.0, 10.0, 10.0], 2)

    result = robust_discretize(y, x, n_strata=3, min_stratum_size=2)
    frame = pd.DataFrame({"x": x, "label": result.labels})

    assert frame.groupby("x")["label"].nunique().max() == 1
    assert result.duplicate_x_count == 6


def test_rank_equivalent_extreme_x_keeps_labels_and_b_value() -> None:
    x = np.arange(18, dtype=float)
    y = np.repeat([0.0, 5.0, 10.0], 6)
    transformed = np.exp(x / 3.0)
    transformed[-1] = 1e100

    first = robust_discretize(y, x, n_strata=3)
    second = robust_discretize(y, transformed, n_strata=3)

    assert first.labels == second.labels
    assert first.b_value == pytest.approx(second.b_value)


def test_optimization_retains_candidates_and_selection_rules() -> None:
    x = np.arange(30, dtype=float)
    y = np.repeat([0.0, 5.0, 10.0], 10)

    maximum = optimize_robust_discretization(
        y,
        x,
        n_strata=(2, 3, 4),
        selection="max_b",
    )
    marginal = optimize_robust_discretization(
        y,
        x,
        n_strata=(2, 3, 4),
        selection="marginal_gain",
        increase_rate=0.01,
    )

    assert list(maximum.candidates_frame()["n_strata"]) == [2, 3, 4]
    assert maximum.best.result is not None
    assert maximum.best.result.b_value == pytest.approx(1.0)
    assert maximum.best.n_strata == 3
    assert marginal.best.n_strata == 4


def test_rgd_and_rid_integrate_with_classical_detectors() -> None:
    x1 = np.arange(24, dtype=float)
    x2 = np.tile(np.arange(6, dtype=float), 4)
    y = np.repeat([0.0, 4.0, 9.0, 13.0], 6) + 0.2 * x2
    factors = pd.DataFrame({"trend": x1, "cycle": x2})

    rgd_result = RGD(n_strata=(2, 3, 4), selection="max_b").fit(y, factors)
    rid_result = RID(n_strata=(2, 3), selection="max_b").fit(y, factors)

    assert set(rgd_result.optimizations) == {"trend", "cycle"}
    for name, optimization in rgd_result.optimizations.items():
        assert optimization.best.result is not None
        assert rgd_result.detector.factor[name].q == pytest.approx(
            optimization.best.result.b_value
        )
    assert len(rid_result.interaction.comparisons) == 1


def test_missing_and_invalid_contracts_are_explicit() -> None:
    x = [0.0, 1.0, np.nan, 3.0, 4.0, 5.0]
    y = [0.0, 0.0, 99.0, 1.0, 1.0, 2.0]

    result = robust_discretize(y, x, n_strata=2)
    assert result.labels[2] is None
    assert result.dropped_count == 1

    with pytest.raises(MissingDataError):
        robust_discretize(y, x, n_strata=2, missing="raise")
    with pytest.raises(InvalidDataError, match="distinct break"):
        robust_discretize(np.arange(8), np.ones(8), n_strata=2)
    with pytest.raises(InvalidDataError, match="at least two"):
        RID(n_strata=(2,)).fit(np.arange(8), {"x": np.arange(8)})
