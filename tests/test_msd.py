from itertools import combinations

import numpy as np
import pandas as pd
import pytest

from pygeohet import MSD, multiscale_discretize
from pygeohet.core.qstat import q_statistic
from pygeohet.exceptions import InvalidDataError, MissingDataError


def _exhaustive_best(
    y: np.ndarray,
    x: np.ndarray,
    n_strata: int,
) -> tuple[tuple[float, ...], float]:
    unique = np.unique(x)
    best_cuts: tuple[float, ...] | None = None
    best_q = -np.inf
    for cuts in combinations(unique[1:], n_strata - 1):
        labels = np.searchsorted(np.asarray(cuts), x, side="right") + 1
        counts = pd.Series(labels).value_counts()
        if int(counts.min()) < 2:
            continue
        q_value = q_statistic(y, labels).q
        if q_value > best_q + 1e-12 or (
            abs(q_value - best_q) <= 1e-12 and (best_cuts is None or cuts < best_cuts)
        ):
            best_cuts = tuple(float(value) for value in cuts)
            best_q = q_value
    assert best_cuts is not None
    return best_cuts, float(best_q)


def test_exact_scale_matches_exhaustive_global_optimum() -> None:
    x = np.arange(12, dtype=float)
    y = np.asarray([0, 0, 0, 1, 1, 1, 5, 5, 5, 9, 9, 9], dtype=float)
    expected_cuts, expected_q = _exhaustive_best(y, x, 4)

    result = multiscale_discretize(y, x, n_strata=4, upscale=1)

    assert result.stratification.cut_points == expected_cuts
    assert result.q_result.q == pytest.approx(expected_q)
    assert result.steps[-1].raw_combinations == 165


def test_paper_style_upscale_downscale_recovers_known_boundaries() -> None:
    x = np.arange(100, dtype=float)
    y = np.select(
        [x < 18, x < 41, x < 64, x < 85],
        [0.0, 10.0, 20.0, 30.0],
        default=40.0,
    )

    result = MSD(
        n_strata=5,
        upscale=6,
        buffer_scales=(3, 1),
        epsilon=1,
        base_resolution=1.0,
        min_stratum_size=2,
    ).fit(y, x)

    assert result.stratification.cut_points == (18.0, 41.0, 64.0, 85.0)
    assert result.q_result.q == pytest.approx(1.0)
    assert tuple(step.scale for step in result.steps) == (6, 3, 1)
    assert all(step.accepted for step in result.steps)
    assert result.steps[1].raw_combinations == 625


def test_cut_point_value_belongs_to_latter_class() -> None:
    x = np.arange(8, dtype=float)
    y = np.asarray([0, 0, 0, 0, 10, 10, 10, 10], dtype=float)

    result = multiscale_discretize(y, x, n_strata=2, upscale=1)

    assert result.stratification.cut_points == (4.0,)
    assert result.stratification.labels[3] == 1
    assert result.stratification.labels[4] == 2


def test_joint_missing_sample_is_expanded_and_audited() -> None:
    x = [0.0, 1.0, np.nan, 3.0, 4.0, 5.0, 6.0]
    y = [0.0, 0.0, 99.0, 1.0, 1.0, 2.0, 2.0]

    result = multiscale_discretize(
        y,
        x,
        n_strata=3,
        upscale=1,
        min_stratum_size=2,
    )

    assert result.stratification.dropped_count == 1
    assert result.stratification.labels[2] is None
    assert result.q_result.n_observations == 6

    with pytest.raises(MissingDataError):
        multiscale_discretize(
            y,
            x,
            n_strata=3,
            upscale=1,
            missing="raise",
            min_stratum_size=2,
        )


def test_ties_choose_lexicographically_smallest_cut_tuple() -> None:
    x = np.arange(8, dtype=float)
    y = np.zeros(8, dtype=float)
    y[::2] = 1.0

    result = multiscale_discretize(
        y,
        x,
        n_strata=2,
        upscale=1,
        min_stratum_size=2,
    )

    exhaustive_cuts, _ = _exhaustive_best(y, x, 2)
    assert result.stratification.cut_points == exhaustive_cuts


def test_invalid_scale_and_class_contracts_are_explicit() -> None:
    x = np.arange(12, dtype=float)
    y = np.repeat([0.0, 1.0, 2.0], 4)

    with pytest.raises(ValueError, match="buffer_scales are required"):
        multiscale_discretize(y, x, n_strata=3, upscale=4)
    with pytest.raises(ValueError, match="strictly decreasing"):
        multiscale_discretize(
            y,
            x,
            n_strata=3,
            upscale=4,
            buffer_scales=(4, 1),
        )
    with pytest.raises(ValueError, match="practical limit"):
        multiscale_discretize(y, x, n_strata=11)
    with pytest.raises(InvalidDataError, match="at least n_strata distinct"):
        multiscale_discretize(y, np.ones_like(x), n_strata=3)


def test_step_frames_retain_search_evidence() -> None:
    x = np.arange(30, dtype=float)
    y = np.repeat([0.0, 5.0, 10.0], 10)

    result = multiscale_discretize(
        y,
        x,
        n_strata=3,
        upscale=4,
        buffer_scales=(2, 1),
        epsilon=1,
        base_resolution=1.0,
    )
    frame = result.steps_frame()

    assert list(frame["scale"]) == [4, 2, 1]
    assert {
        "candidate_count",
        "raw_combinations",
        "selected_cut_points",
        "q",
    }.issubset(frame.columns)
    assert "q=" in result.summary()
