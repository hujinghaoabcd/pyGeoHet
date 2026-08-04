import numpy as np
import pandas as pd
import pytest

from pygeohet import (
    InteractionDetector,
    InteractionType,
    categorical_overlay,
    classify_interaction,
)


def test_tuple_overlay_prevents_string_collisions() -> None:
    x1 = np.array(["a_b", "a"], dtype=object)
    x2 = np.array(["c", "b_c"], dtype=object)
    overlay = categorical_overlay(x1, x2)
    assert overlay.tolist() == [("a_b", "c"), ("a", "b_c")]
    assert overlay[0] != overlay[1]


@pytest.mark.parametrize(
    ("q1", "q2", "q12", "expected"),
    [
        (0.4, 0.5, 0.3, InteractionType.WEAKEN_NONLINEAR),
        (0.4, 0.5, 0.45, InteractionType.WEAKEN_UNIVARIATE),
        (0.4, 0.5, 0.7, InteractionType.ENHANCE_BIVARIATE),
        (0.4, 0.5, 0.9, InteractionType.INDEPENDENT),
        (0.4, 0.5, 0.95, InteractionType.ENHANCE_NONLINEAR),
    ],
)
def test_classify_interaction_covers_five_types(
    q1: float,
    q2: float,
    q12: float,
    expected: InteractionType,
) -> None:
    assert classify_interaction(q1, q2, q12) is expected


def test_classify_interaction_uses_float_tolerance() -> None:
    assert (
        classify_interaction(0.2, 0.3, 0.50000000001, atol=1e-8)
        is InteractionType.INDEPENDENT
    )


def test_interaction_uses_one_joint_complete_case_sample() -> None:
    data = pd.DataFrame(
        {
            "x1": ["a", "a", "b", "b", "a", "a", "b", "b", "a"],
            "x2": ["u", "u", "u", "u", "v", "v", "v", "v", None],
        }
    )
    y = np.array([1.0, 1.2, 2.0, 2.2, 4.0, 4.2, 5.0, 5.2, 6.0])
    result = InteractionDetector().fit(y, data)
    comparison = result.comparisons[0]

    assert comparison.dropped_count == 1
    assert comparison.factor_1_result.n_observations == 8
    assert comparison.factor_2_result.n_observations == 8
    assert comparison.overlay_result.n_observations == 8
    assert comparison.to_series()["overlay_strata"] == 4


def test_interaction_frame_is_auditable() -> None:
    y = [1.0, 1.1, 2.0, 2.1, 4.0, 4.1, 5.0, 5.1]
    factors = {
        "x1": ["a", "a", "b", "b", "a", "a", "b", "b"],
        "x2": ["u", "u", "u", "u", "v", "v", "v", "v"],
    }
    frame = InteractionDetector().fit(y, factors).to_frame()
    assert frame.loc[0, "factor_1"] == "x1"
    assert frame.loc[0, "factor_2"] == "x2"
    assert 0.0 <= frame.loc[0, "q_overlay"] <= 1.0
    assert frame.loc[0, "interaction"] in {item.value for item in InteractionType}


def test_singleton_overlay_cells_are_retained_by_explicit_default() -> None:
    y = [1.0, 1.1, 2.0, 2.1, 4.0, 4.1, 5.0]
    factors = {
        "x1": ["a", "a", "b", "b", "a", "a", "b"],
        "x2": ["u", "u", "u", "u", "v", "v", "v"],
    }
    comparison = InteractionDetector().fit(y, factors).comparisons[0]
    assert comparison.overlay_result.stratum_counts[("b", "v")] == 1
